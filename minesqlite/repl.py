# coding=utf-8
# Author: @hsiaoxychen 2022/06/15
import re
import typing

from tabulate import tabulate

from minesqlite import exceptions
from minesqlite.command_registry import get_command_info, CommandInfo
from minesqlite.common.split_words_fsm import split_words
from minesqlite import MineSQLite


def read_lines(instance: MineSQLite) -> typing.Iterator[str]:
    """Prints prompts, reads the input, then yields each lines of them."""
    infile: typing.IO = instance.sysconf['repl.read.infile']
    prompt: str = instance.sysconf['repl.read.prompt']
    print(prompt, end='', flush=True)
    try:
        for line in infile:
            line = line.strip()
            if not line:
                print(prompt, end='', flush=True)
                continue
            yield line
            print(prompt, end='', flush=True)
    except KeyboardInterrupt:
        pass

    print('Goodbye!')


def validate_key(key: str):
    magic_params = ['$sort_asc', '$sort_desc']
    if key in magic_params:
        return
    if re.match(r'^[a-zA-Z_]\w*$', key, flags=re.ASCII) is None:
        raise exceptions.CommandInvalidKeyArgument(key=key)


def validate_value(value: str):
    pass


def analyse_arguments(cmd_info: CommandInfo, arguments: list[str]) \
        -> list[typing.Union[tuple[str, str], str]]:
    arguments = arguments.copy()
    results = []
    while arguments:
        arg1 = arguments.pop(0)
        if cmd_info.args_format == 'key-value':
            if len(arguments) < 1:
                raise exceptions.CommandKeyValueUnmatched(key=arg1)
            arg2 = arguments.pop(0)
            validate_key(arg1)
            validate_value(arg2)
            results.append((arg1, arg2))
        elif cmd_info.args_format == 'key':
            validate_key(arg1)
            results.append(arg1)
        elif cmd_info.args_format == 'value':
            validate_value(arg1)
            results.append(arg1)
        else:
            raise exceptions.InternalError(
                msg="invalid `args_format`: %s" % cmd_info.args_format)

    if cmd_info.min_args is not None and len(results) < cmd_info.min_args:
        raise exceptions.CommandTooFewArguments(
            expect=cmd_info.min_args, real=len(results))
    if cmd_info.max_args is not None and len(results) > cmd_info.max_args:
        raise exceptions.CommandTooManyArguments(
            expect=cmd_info.max_args, real=len(results))

    return results


def execute_command(instance: 'MineSQLite',
                    command_info: CommandInfo,
                    arguments: list[typing.Union[tuple[str, str], str]]):
    """Execute the command with the very arguments."""
    return command_info.handler(instance, arguments)


def print_results(instance: MineSQLite, rows: typing.Iterable[dict]):
    """Print the results of a command."""
    if not rows:
        return

    headers = [field.upper() for field in instance.schema.fields]
    table = []
    for row_dict in rows:
        row_list = []
        for field in instance.schema.fields:
            row_list.append(row_dict[field])
        table.append(row_list)
    print(tabulate(table, headers=headers, tablefmt='orgtbl'))


def repl_loop(instance: MineSQLite):
    """Implements the REPL steps.

    1) READ the input (and prints prompts)
    1.1) SPLIT the input into words with careful handling of quotes
    1.2) ANALYSE the arguments (cut into groups and validate them)
    2) EVAL the command and collects the results
    3) PRINT the command results
    4) LOOP again...
    """
    for line in read_lines(instance):
        try:
            words = split_words(line)
            command, arguments = words[0], words[1:]
            command_info = get_command_info(command)
            grouped_arguments = analyse_arguments(command_info, arguments)
            rows = execute_command(instance, command_info, grouped_arguments)
            print_results(instance, rows)
        except Exception as exc:
            # if not in debug mode, just prints a brief message
            if not instance.sysconf['general.debug']:
                errcode = getattr(exc, 'errcode', None)
                if errcode is not None:
                    print("[%s] %s: %s" % (
                        errcode, exc.__class__.__name__, str(exc)))
                else:
                    print("%s: %s" % (exc.__class__.__name__, str(exc)))
            else:
                raise
        print()
