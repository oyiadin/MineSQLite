# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import argparse
import typing

from minesqlite.command_registry import get_all_commands
from minesqlite.minesqlite import MineSQLite


class NoExitArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        raise argparse.ArgumentError(message)


def analyze(parser: argparse.ArgumentParser, words: list[str]) \
        -> tuple[typing.Callable, argparse.Namespace]:
    """Analyze the arguments according to the given rules."""
    args = parser.parse_args(words)
    return args.handler, args


def get_argparsers(instance: MineSQLite) -> argparse.ArgumentParser:
    root_parser = NoExitArgumentParser(exit_on_error=False)
    subparsers = root_parser.add_subparsers()
    for cmd, cmd_info in get_all_commands().items():
        parser = subparsers.add_parser(cmd_info.command,
                                       help=cmd_info.help_,
                                       usage=cmd_info.handler.__doc__)
        parser.set_defaults(handler=cmd_info.handler)
        cmd_info.argparser_factory(instance, parser)
    return root_parser
