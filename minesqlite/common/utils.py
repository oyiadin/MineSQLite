# coding=utf-8
# Author: @hsiaoxychen 2022/06/15

import typing

from minesqlite import exceptions

KT = typing.TypeVar('KT')
VT = typing.TypeVar('VT')


def convert_argument_groups_into_dict(
        argument_groups: list[tuple[KT, VT]]) -> dict[KT, VT]:
    result = {}
    for key, value in argument_groups:
        if key in result:
            raise exceptions.CommandArgumentConflict(key=key)
        result[key] = value
    return result
