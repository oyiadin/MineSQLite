# coding=utf-8
# Author: @hsiaoxychen
import functools
import typing

from minesqlite import exceptions
from minesqlite.command_registry import (
    register,
    get_all_commands,
    get_command_info,
)
from minesqlite.common import utils

if typing.TYPE_CHECKING:
    from minesqlite import MineSQLite


@register(command='add', name='Add', description='Adds an employee.',
          args_format='key-value', min_args=1)
def command_add(instance: 'MineSQLite',
                arguments: list[tuple[str, str]]) -> list[dict]:
    """Adds an employee.

    Example:
        add id 12345 name "Chen Xiaoyuan" in_date 2022-06-05 department aCMP position "Software Development Engineer"
    """
    kvs = utils.convert_argument_groups_into_dict(arguments)
    instance.schema.validate_keys(kvs)
    instance.schema.validate_types(kvs)

    kvs = instance.schema.convert_types(kvs)
    pk = kvs.pop(instance.schema.primary_key)
    return [instance.data.driver.create_one(pk, kvs)]


@register('del', 'Delete', 'Delete an employee.',
          args_format='value', min_args=1, max_args=1)
def command_del(instance: 'MineSQLite', arguments: list[str]) -> list[dict]:
    """Delete an employee.

    Example:
        del 12345
    """
    pk_value = instance.schema.convert_primary_key_type(arguments[0])
    return [instance.data.driver.delete_one(pk_value)]


@register('get', 'Get', 'Gets the info of an employee.',
          args_format='value', min_args=1, max_args=1)
def command_get(instance: 'MineSQLite',
                arguments: list[str]) -> list[dict]:
    """Gets the information of an employee.

    Example:
        get 12345
    """
    pk_value = instance.schema.convert_primary_key_type(arguments[0])
    return [instance.data.driver.read_one(pk_value)]


@register('list', 'List', 'List all employees.',
          args_format='key-value')
def command_list(instance: 'MineSQLite',
                 arguments: list[tuple[str, str]]) -> list[dict]:
    """List all employees (after filtering) and sort them.

    Example:
        list
        list name "Chen Xiaoyuan" $sort_asc id $sort_desc name
    """
    magic_params = []
    filter_params = {}
    for key, value in arguments:
        if key in filter_params:
            raise exceptions.CommandArgumentConflict(key=key)
        if key.startswith('$'):
            magic_params.append((key, value))
        else:
            filter_params[key] = value

    instance.schema.validate_keys(
        filter_params, no_missing=False, no_extra=True)
    instance.schema.validate_types(filter_params)
    filter_params = instance.schema.convert_types(filter_params)

    def do_filter(_row: dict) -> bool:
        for filter_key, filter_value in filter_params.items():
            if _row[filter_key] != filter_value:
                return False
        return True

    cursor = instance.data.driver.build_cursor()
    rows = []
    while cursor:
        cursor, row = instance.data.driver.next_row(cursor)
        if do_filter(row):
            rows.append(row)

    def compare(row1: dict, row2: dict) -> int:
        for magic_key, field_name in magic_params:
            if magic_key == '$sort_asc':
                reverse = False
            elif magic_key == '$sort_desc':
                reverse = True
            else:
                raise exceptions.InternalError(
                    "invalid magic_key: %s" % magic_key)

            value1, value2 = row1[field_name], row2[field_name]
            if value1 == value2:
                continue
            if not reverse:
                return 1 if value1 > value2 else -1
            else:
                return 1 if value1 < value2 else -1
        return 0

    if magic_params:
        rows.sort(key=functools.cmp_to_key(compare))
    return rows


@register('mod', 'Modify', 'Modify an employee.',
          args_format='key-value', min_args=2)
def command_mod(instance: 'MineSQLite',
                arguments: list[tuple[str, str]]) -> list[dict]:
    """Modify an employee.

    Example:
        mod id 12345 name hsiaoxychen
    """
    query_key, query_value = arguments.pop(0)
    if query_key != instance.schema.primary_key:
        raise exceptions.CommandInvalidKeyArgument(
            "you can only modify by matching `id`, "
            "rather than by `%s`" % query_key)
    pk_value = instance.schema.convert_primary_key_type(query_value)

    kvs = utils.convert_argument_groups_into_dict(arguments)
    if instance.schema.primary_key in kvs:
        raise exceptions.CommandInvalidKeyArgument(
            "cannot modify primary key `%s`" % instance.schema.primary_key)

    instance.schema.validate_keys(kvs, no_missing=False, no_extra=True)
    instance.schema.validate_types(kvs)
    kvs = instance.schema.convert_types(kvs)
    return [instance.data.driver.update_one(pk_value, kvs)]


@register('help', 'Help', 'Show this help message.',
          args_format='value', max_args=1)
def command_help(instance: 'MineSQLite', arguments: list[str]) \
        -> typing.List[dict]:
    what = arguments[0] if arguments else None
    print('Help:\n')
    print_no_sep = functools.partial(print, sep='')

    # help of all commands
    if what is None:
        prefix = ' ' * 4
        command_infos = get_all_commands()
        max_width = max(len(command) for command in command_infos.keys())
        for command, info in command_infos.items():
            print_no_sep(prefix,
                         f'{command:{max_width}} \t',
                         info.description)

    # help of a specific command
    else:
        info = get_command_info(what)
        prefix = ' ' * 4
        print_no_sep(prefix, what, ': ', info.name)
        if info.help_ is not None:
            print_no_sep(prefix, info.help_)

    return []
