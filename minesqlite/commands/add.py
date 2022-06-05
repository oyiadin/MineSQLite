# coding=utf-8
# Author: @hsiaoxychen
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('add', 'Add', 'Adds an employee.',
          args_format=['kv+'])
def add(instance: MineSQLite, groups) -> typing.List[dict]:
    kvs = groups[0]
    kvs_dict = {}
    for key, value in kvs:
        if key in kvs_dict:
            raise ValueError("field repeated: {}".format(key))
        kvs_dict[key] = value

    instance.schema.validate_fields(kvs_dict)
    pk = kvs_dict.pop(instance.schema.primary_key)
    return [instance.data.driver.create_one(pk, kvs_dict)]
