# coding=utf-8
# Author: @hsiaoxychen
import functools
import typing

from minesqlite.command_registry import register, get_all_commands, \
    get_command_info
from minesqlite.minesqlite import MineSQLite


@register('add', 'Add', 'Adds an employee.',
          args_format=['kv+'])
def command_add(instance: MineSQLite,
                args_groups: list[dict]) -> list[dict]:
    """Adds an employee.

    Example:
        add id 12345 name "Chen Xiaoyuan" in_date 2022-06-05 department aCMP position "Software Development Engineer"
    """
    kvs = args_groups[0]
    instance.schema.validate_fields(kvs)
    pk = kvs.pop(instance.schema.primary_key)
    return [instance.data.driver.create_one(pk, kvs)]


@register('del', 'Delete', 'Delete an employee.',
          args_format=['kv'])
def command_del(instance: MineSQLite,
                args_groups: list[list]) -> list[dict]:
    """Delete an employee.

    Example:
        del id 12345
    """
    key, value = args_groups[0]
    assert key in ['id'], "you can only delete by id"
    return [instance.data.driver.delete_one(value)]


@register('get', 'Get', 'Gets the info of an employee.',
          args_format=['kv'])
def command_get(instance: MineSQLite,
                args_groups: list[list]) -> list[dict]:
    """Gets the information of an employee.

    Example:
        get id 12345
    """
    key, value = args_groups[0]
    assert key in ['id'], "you can only delete by id"
    return [instance.data.driver.read_one(value)]


@register('list', 'List', 'List all employees.',
          args_format=['kv*'])
def command_list(instance: MineSQLite,
                 args_groups: list[dict]) -> list[dict]:
    """List all employees (after filtering) and sort them.

    Example:
        list
        list name "Chen Xiaoyuan" $sort_asc id $sort_desc name
    """
    magic_params = []
    filter_params = {}
    for key, value in args_groups[0].items():
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


@register('help', 'Help', 'Show this help message.',
          args_format=['v?'])
def command_help(instance: MineSQLite, groups) -> typing.List[dict]:
    what = groups[0][0] if groups[0] else None
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
