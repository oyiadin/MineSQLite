# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import functools
import typing

from minesqlite.command_registry import register, get_all_commands, get_command_info
from minesqlite.minesqlite import MineSQLite


print_no_sep = functools.partial(print, sep='')


@register('help', 'Help', 'Show this help message.',
          args_format=['v?'])
def mod(instance: MineSQLite, groups) -> typing.List[dict]:
    what = groups[0][0] if groups[0] else None
    print('Help:\n')

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
