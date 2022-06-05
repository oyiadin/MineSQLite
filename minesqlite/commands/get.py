# coding=utf-8
# Author: @hsiaoxychen
from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('get', 'Get', 'Gets the info of an employee.',
          args_format=['kv'])
def get(instance: MineSQLite, groups):
    key, value = groups[0][0]
    if key not in ['id', 'name']:
        # TODO: read from schema configs
        raise ValueError("you can specify only id or name")
