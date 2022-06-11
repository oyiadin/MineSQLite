# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing

if typing.TYPE_CHECKING:
    from minesqlite.minesqlite import MineSQLite


def eval_(instance: 'MineSQLite',
          handler: typing.Callable,
          args_groups: list[typing.Union[list, dict]]):
    return handler(instance, args_groups)
