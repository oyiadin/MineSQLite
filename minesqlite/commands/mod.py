# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('mod', 'Modify', 'Modify an employee.',
          args_format=['kv', 'kv+'])
def mod(instance: MineSQLite, groups) -> typing.List[dict]:
    """Modify an employee.

    Example:
        mod id 12345 name hsiaoxychen
    """
    kv1 = groups[0][0]
    kvs2 = groups[1]
    assert kv1[0] in ['id'], "you can only modify by id"
    kvs_dict = {}
    for key, value in kvs2:
        if key == 'id':
            raise ValueError("not allowed to change id!")
        if key in kvs_dict:
            raise ValueError("duplicated key!")
        kvs_dict[key] = value

    return [instance.data.driver.update_one(kv1[1], kvs_dict)]
