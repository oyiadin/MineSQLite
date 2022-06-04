# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import enum
import re
import typing

from minesqlite.command_registry import get_command_info


class RepeatMode(enum.Enum):
    SINGLE = 'single'
    ANY = 'any'
    AT_LEAST_ONE = 'at_least_one'


def validate_key(data: str):
    result = re.match(r'^[a-zA-Z_]\w?$', data)
    if result is None:
        raise ValueError("invalid key: {}".format(data))


def validate_value(data: str):
    return


def eval_(components: typing.List[str]):
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
        repeat_mode = RepeatMode.SINGLE
        if arg_part[-1] in ['*', '+']:
            repeat_mode = {
                '*': RepeatMode.ANY,
                '+': RepeatMode.AT_LEAST_ONE,
            }[arg_part[-1]]
            arg_part = arg_part[:-1]

        current_group = []
        times = 0
        while True:
            try:
                if arg_part == 'k':
                    arg = next_arg()
                    validate_key(arg)
                    current_group.append(arg)
                elif arg_part == 'v':
                    arg = next_arg()
                    validate_value(arg)
                    current_group.append(arg)
                elif arg_part == 'kv':
                    arg1 = next_arg()
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
                if repeat_mode == RepeatMode.ANY:
                    break
                elif repeat_mode == RepeatMode.AT_LEAST_ONE:
                    if times > 0:
                        break
                    else:
                        raise ValueError("too few arguments")
                else:
                    raise Exception("unexpected error!")

            times += 1
            if repeat_mode == RepeatMode.SINGLE:
                break

        parsed_args.append(current_group)

    return command_info.handler(parsed_args)
