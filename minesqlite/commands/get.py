# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('get', 'Get', 'Gets the info of an employee.',
          args_format=['kv'])
def get(instance: MineSQLite, groups) -> typing.List[dict]:
    """Gets the information of an employee.

    Example:
        get id 12345
        get name "Chen Xiaoyuan"
    """
    key, value = groups[0][0]
    if key not in ['id', 'name']:
        # TODO: read from schema configs
        raise ValueError("you can specify only id or name")

    driver = instance.data.driver
    if key == 'id':
        return [driver.read_one(value)]
    else:  # name
        rows = []
        cursor = driver.build_cursor()
        while cursor:
            cursor, row = instance.data.driver.next_row(cursor)
            if row['name'] == value:
                rows.append(row)
        return rows

    return []
