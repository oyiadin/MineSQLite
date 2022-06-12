# coding=utf-8
# Author: @hsiaoxychen
import argparse
import functools
import typing

from minesqlite.command_registry import register
from minesqlite.common.constant import SortOrder
from minesqlite.minesqlite import MineSQLite


def argparser_factory_add(
        instance: MineSQLite,
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    for field in instance.schema.fields:
        parser.add_argument('--%s' % field, required=True)
    return parser


@register(command='add', name='Add',
          description='Adds an employee.',
          argparser_factory=argparser_factory_add)
def command_add(instance: MineSQLite, args: argparse.Namespace) -> list[dict]:
    """Adds an employee.

    Example:
        add --id 12345 --name "Chen Xiaoyuan" --in_date 2022-06-05 \
--department aCMP --position "Software Development Engineer"
    """
    kvs = args.__dict__.copy()
    pk = kvs.pop(instance.schema.primary_key)
    return [instance.data.driver.create_one(pk, kvs)]


def argparser_factory_delete(
        instance: MineSQLite,
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument('--%s' % instance.schema.primary_key, required=True)
    return parser


@register(command='del', name='Delete',
          description='Delete an employee.',
          argparser_factory=argparser_factory_delete)
def command_delete(instance: MineSQLite, args: argparse.Namespace) \
        -> list[dict]:
    """Delete an employee.

    Example:
        del --id 12345
    """
    pk = args[instance.schema.primary_key]
    return [instance.data.driver.delete_one(pk)]


def argparser_factory_get(
        instance: MineSQLite,
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument('--%s' % instance.schema.primary_key, required=True)
    return parser


@register(command='get', name='Get',
          description='Gets the info of an employee.',
          argparser_factory=argparser_factory_get)
def command_get(instance: MineSQLite, args: argparse.Namespace) -> list[dict]:
    """Gets the information of an employee.

    Example:
        get --id 12345
    """
    pk = args[instance.schema.primary_key]
    return [instance.data.driver.read_one(pk)]


def argparser_factory_list(
        instance: MineSQLite,
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    for field in instance.schema.fields:
        parser.add_argument('--%s' % field, required=False)
    parser.add_argument('--sort', nargs='+', required=False)
    return parser


@register(command='list', name='List', description='List all employees.',
          argparser_factory=argparser_factory_list)
def command_list(instance: MineSQLite, args: argparse.Namespace) -> list[dict]:
    """List all employees (after filtering) and sort them.

    Example:
        # list all employees
        list
        # list all employees within aCMP and sort them, id asc, name desc
        list --department aCMP --sort >id <name
    """
    filter_params = args.__dict__.copy()
    sort_params = []
    # extract the sorting rules
    if 'sort' in filter_params:
        filter_params.pop('sort')
        for field in args.sort:
            order = SortOrder.DESC if field.startswith('<') else SortOrder.ASC
            field = field.lstrip('><')
            sort_params.append((field, order))

    # iterate over the whole database and do the filter (if any)
    cursor = instance.data.driver.build_cursor()
    rows = []
    while cursor:
        cursor, row = instance.data.driver.next_row(cursor)
        for filter_key, filter_value in filter_params.items():
            if row[filter_key] != filter_value:
                break
        else:
            rows.append(row)

    def compare(row1: dict, row2: dict) -> int:
        for field, order in sort_params:
            value1, value2 = row1[field], row2[field]
            if value1 == value2:
                continue
            if order == SortOrder.ASC:
                return 1 if value1 > value2 else -1
            else:
                return 1 if value1 < value2 else -1
        return 0  # all equal

    if sort_params:
        rows.sort(key=functools.cmp_to_key(compare))

    return rows


def argparser_factory_mod(
        instance: MineSQLite,
        parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    for field in instance.schema.fields:
        required = field == instance.schema.primary_key
        parser.add_argument('--%s' % field, required=required)
    return parser


@register('mod', 'Modify', 'Modify an employee.',
          argparser_factory=argparser_factory_mod)
def mod(instance: MineSQLite, args: argparse.Namespace) -> list[dict]:
    """Modify an employee.

    Example:
        mod --id 12345 --name hsiaoxychen
    """
    kvs = args.__dict__.copy()
    pk = kvs[instance.schema.primary_key]
    kvs.pop(instance.schema.primary_key)
    return [instance.data.driver.update_one(pk, kvs)]

#
#
# @register('help', 'Help', 'Show this help message.',
#           args_format=['v?'])
# def command_help(instance: MineSQLite, groups) -> typing.List[dict]:
#     what = groups[0][0] if groups[0] else None
#     print('Help:\n')
#     print_no_sep = functools.partial(print, sep='')
#
#     # help of all commands
#     if what is None:
#         prefix = ' ' * 4
#         command_infos = get_all_commands()
#         max_width = max(len(command) for command in command_infos.keys())
#         for command, info in command_infos.items():
#             print_no_sep(prefix,
#                          f'{command:{max_width}} \t',
#                          info.description)
#
#     # help of a specific command
#     else:
#         info = get_command_info(what)
#         prefix = ' ' * 4
#         print_no_sep(prefix, what, ': ', info.name)
#         if info.help_ is not None:
#             print_no_sep(prefix, info.help_)
#
#     return []
