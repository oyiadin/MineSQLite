# coding=utf-8
# Author: @hsiaoxychen
import functools
import typing

from minesqlite.command_registry import register
from minesqlite.minesqlite import MineSQLite


@register('list', 'List', 'List all employees.',
          args_format=['kv*'])
def list_(instance: MineSQLite, groups: list[tuple[str, str]]) -> typing.List[dict]:
    """List all employees.

    Example:
        list
        list name "Chen Xiaoyuan" $sort_asc id $sort_desc name
    """
    magic_params = []
    filter_params = {}
    kvs_list = groups[0]
    for key, value in kvs_list:
        if key in filter_params:
            raise ValueError("field repeated: {}".format(key))
        if key.startswith('$'):
            magic_params.append((key, value))
        else:
            filter_params[key] = value

    data_driver = instance.data.driver
    cursor = data_driver.build_cursor()
    rows = []
    while cursor:
        cursor, row = instance.data.driver.next_row(cursor)
        for filter_key, filter_value in filter_params.items():
            if row[filter_key] != filter_value:
                break
        else:
            rows.append(row)

    def compare(row1: dict, row2: dict) -> int:
        for magic_key, magic_value in magic_params:
            if magic_key == '$sort_asc':
                reverse = False
            elif magic_key == '$sort_desc':
                reverse = True
            else:
                continue  # TODO 这里直接忽略没啥问题，后续可以优化下

            field_name = magic_value
            value1, value2 = row1[field_name], row2[field_name]
            if value1 == value2:
                continue
            result = 1 if value1 > value2 else -1
            if reverse:
                result = -result
            return result
        return 0

    if magic_params:
        rows.sort(key=functools.cmp_to_key(compare))
    return rows
