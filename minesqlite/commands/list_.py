# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('list', 'List', 'List all employees.',
          args_format=[])
def list_(instance: MineSQLite, groups) -> typing.List[dict]:
    data_driver = instance.data.driver
    cursor = data_driver.build_cursor()
    rows = []
    while cursor:
        cursor, row = instance.data.driver.next_row(cursor)
        rows.append(row)
    return rows
