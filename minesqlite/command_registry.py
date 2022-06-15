# coding=utf-8
# Author: @hsiaoxychen
import collections
import typing

from minesqlite import exceptions


CommandInfo = collections.namedtuple(
    "CommandInfo",
    ['name', 'handler', 'description', 'help_',
     'args_format', 'min_args', 'max_args'],
)

_registry: typing.Dict[str, CommandInfo] = {}


def register(command: str, name: str, description: str,
             args_format: typing.Literal["key-value", "key", "value"],
             min_args: int = None, max_args: int = None):
    def decorator(func):
        global _registry
        help_ = func.__doc__
        command_info = CommandInfo(name, func, description, help_,
                                   args_format, min_args, max_args)
        _registry[command] = command_info
        return func

    return decorator


def get_command_info(command: str) -> CommandInfo:
    if command not in _registry:
        raise exceptions.CommandNotFound(command=command)
    return _registry[command]


def get_all_commands() -> typing.Dict[str, CommandInfo]:
    return _registry
