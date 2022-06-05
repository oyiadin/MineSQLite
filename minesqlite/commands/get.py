# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('get', 'Get', 'Gets the info of an employee.',
          args_format=['kv'])
def get(instance: MineSQLite, groups) -> typing.List[dict]:
    key, value = groups[0][0]
    if key not in ['id', 'name']:
        # TODO: read from schema configs
        raise ValueError("you can specify only id or name")

    if key == 'id':
        return [instance.data.driver.read_one(value)]
    else:
        raise NotImplementedError
