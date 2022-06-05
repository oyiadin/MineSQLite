# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('del', 'Delete', 'Delete an employee.',
          args_format=['kv'])
def del_(instance: MineSQLite, groups) -> typing.List[dict]:
    """Delete an employee.

    Example:
        del id 12345
    """
    key, value = groups[0][0]
    assert key in ['id'], "you can only delete by id"

    return [instance.data.driver.delete_one(value)]
