# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import enum
import re
import typing

from minesqlite.minesqlite import MineSQLite


def read_(instance: MineSQLite) -> typing.Iterator[str]:
    """Prints prompts, reads the input, then yields each lines of them."""
    infile: typing.IO = instance.sysconf['repl.read.infile']
    prompt: str = instance.sysconf['repl.read.prompt']
    print(prompt, end='')
    try:
        for line in infile:
            line = line.strip()
            if not line:
                print(prompt, end='')
                continue
            yield line
            print(prompt, end='')
    except KeyboardInterrupt:
        print('Goodbye!')


class _RepeatMode(enum.Enum):
    SINGLE = 'single'
    ANY = 'any'  # *
    AT_LEAST_ONE = 'at_least_one'  # +
    AT_MOST_ONE = 'at_most_one'  # ?


def eval_(instance: MineSQLite, components: typing.List[str]):
    command = components[0]
    args = components[1:]
    arg_index = 0

    def next_arg():
        nonlocal arg_index
        result = args[arg_index]
        arg_index += 1
        return result

    parsed_args = []
    command_info = get_command_info(command)
    for arg_part in command_info.args_format:
        repeat_mode = _RepeatMode.SINGLE
        if arg_part[-1] in ['*', '+', '?']:
            repeat_mode = {
                '*': _RepeatMode.ANY,
                '+': _RepeatMode.AT_LEAST_ONE,
                '?': _RepeatMode.AT_MOST_ONE,
            }[arg_part[-1]]
            arg_part = arg_part[:-1]

        current_group = []
        times = 0
        while True:
            try:
                if arg_part == 'k':
                    # make key as lowercase
                    arg = next_arg().lower()
                    validate_key(arg)
                    current_group.append(arg)
                elif arg_part == 'v':
                    arg = next_arg()
                    validate_value(arg)
                    current_group.append(arg)
                elif arg_part == 'kv':
                    # make key as lowercase
                    arg1 = next_arg().lower()
                    try:
                        arg2 = next_arg()
                    except IndexError:
                        raise ValueError(
                            "the key {} must come with a value!".format(arg1))
                    validate_key(arg1)
                    validate_value(arg2)
                    current_group.append((arg1, arg2))
                else:
                    raise ValueError("invalid arg_format: {}".format(arg_part))

            except IndexError:
                if repeat_mode == _RepeatMode.ANY:
                    break
                elif repeat_mode == _RepeatMode.AT_LEAST_ONE:
                    if times > 0:
                        break
                    else:
                        raise ValueError("too few arguments")
                elif repeat_mode == _RepeatMode.SINGLE:
                    if times == 0:
                        raise ValueError("too few arguments")
                    else:
                        break
                elif repeat_mode == _RepeatMode.AT_MOST_ONE:
                    break
                else:
                    raise Exception("unexpected error!")

            times += 1
            if repeat_mode in [_RepeatMode.SINGLE, _RepeatMode.AT_MOST_ONE]:
                break

        parsed_args.append(current_group)

    if arg_index < len(args):
        # TODO: more specific exceptions
        raise ValueError("too many arguments!")

    return command_info.handler(instance, parsed_args)
