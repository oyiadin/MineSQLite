# coding=utf-8
# Author: @hsiaoxychen
from minesqlite.command_registry import register


@register('add', 'Add', 'Adds an employee.',
          args_format=['kv+'])
def add(groups):
    kvs = groups[0]
    for key, value in kvs:
        pass
