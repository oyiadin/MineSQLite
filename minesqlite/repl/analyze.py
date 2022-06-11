# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import enum
import re
import typing

from minesqlite.command_registry import get_command_info, CommandInfo


class RepeatMode(enum.Enum):
    SINGLE = 'single'
    ANY = 'any'  # *
    AT_LEAST_ONE = 'at_least_one'  # +
    AT_MOST_ONE = 'at_most_one'  # ?


char_to_repeat_mode = {
    '*': RepeatMode.ANY,
    '+': RepeatMode.AT_LEAST_ONE,
    '?': RepeatMode.AT_MOST_ONE,
}


def validate_key(data: str):
    result = re.match(r'^\$?[a-zA-Z_]\w*$', data)
    if result is None:
        raise ValueError("invalid key: {}".format(data))


def validate_value(data: str):
    return


def analyze(cmd: str, words: list[str]) \
        -> tuple[typing.Callable, list[typing.Union[list, dict]]]:
    """Analyze the arguments according to the given rules."""
    command_info: CommandInfo = get_command_info(cmd)
    index = 0
    words_iter = iter(words)

    groups = []
    for group in command_info.args_format:
        # extract how many times we should repeat
        repeat_mode = RepeatMode.SINGLE
        if group[-1] in ['*', '+', '?']:
            repeat_mode = char_to_repeat_mode[group[-1]]
            group = group[:-1]

        current_group = {} if group == 'kv' else []
        times = 0
        while True:
            try:
                if group == 'k':
                    # make key as lowercase
                    arg = next(words_iter).lower()
                    validate_key(arg)
                    current_group.append(arg)
                elif group == 'v':
                    arg = next(words_iter)
                    validate_value(arg)
                    current_group.append(arg)
                elif group == 'kv':
                    # make key as lowercase
                    arg1 = next(words_iter).lower()
                    try:
                        arg2 = next(words_iter)
                    except StopIteration:
                        raise ValueError("%s should come with a value" % arg1)
                    validate_key(arg1)
                    validate_value(arg2)
                    current_group[arg1] = arg2
                else:
                    raise ValueError("unknown arg_format: %s" % group)

            except StopIteration:
                if repeat_mode == RepeatMode.ANY:
                    break
                elif repeat_mode == RepeatMode.AT_LEAST_ONE:
                    if times > 0:
                        break
                    else:
                        raise ValueError("too few arguments")
                elif repeat_mode == RepeatMode.SINGLE:
                    if times == 0:
                        raise ValueError("too few arguments")
                    else:
                        break
                elif repeat_mode == RepeatMode.AT_MOST_ONE:
                    break
                else:
                    raise Exception("unexpected error!")

            times += 1
            if repeat_mode in [RepeatMode.SINGLE, RepeatMode.AT_MOST_ONE]:
                break

        groups.append(current_group)

    if index < len(words):
        # TODO: more specific exceptions
        raise ValueError("too many arguments!")

    return command_info.handler, groups
