# coding=utf-8
# Author: @hsiaoxychen
import argparse
import collections
import typing

from minesqlite.minesqlite import MineSQLite


CommandInfo = collections.namedtuple(
    "CommandInfo",
    ['command', 'name', 'handler', 'description', 'help_',
     'argparser_factory'],
)

_registry: typing.Dict[str, CommandInfo] = {}
ArgparserFactoryType = typing.Callable[
    [MineSQLite, argparse.ArgumentParser], argparse.ArgumentParser,
]


def register(command: str, name: str, description: str,
             argparser_factory: ArgparserFactoryType):
    def decorator(func):
        global _registry
        help_ = func.__doc__
        command_info = CommandInfo(
            command, name, func, description, help_, argparser_factory)
        _registry[command] = command_info
        return func

    return decorator


def get_command_info(command: str) -> CommandInfo:
    return _registry[command]


def get_all_commands() -> typing.Dict[str, CommandInfo]:
    return _registry
