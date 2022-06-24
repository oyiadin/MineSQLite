# coding=utf-8
# Author: @hsiaoxychen
import datetime
import inspect
from unittest import mock
import pytest

from minesqlite import commands, exceptions
from minesqlite.common import utils


@pytest.mark.parametrize(['arguments', 'expect'], [
    ([
         ('id', '12345'),
         ('name', 'Chen Xiaoyuan'),
         ('in_date', '2022-06-05'),
         ('department', 'aCMP'),
         ('position', 'Software Development Engineer'),
     ],
     True),
])
def test_command_add(instance, arguments, expect):
    mock_ret = mock.Mock()
    mock_converted = mock.Mock()
    mock_convert_types = mock.MagicMock()
    mock_convert_types.return_value = mock_converted
    instance.schema.convert_types = mock_convert_types

    def mock_create_one(*args):
        assert args[0] == mock_converted.pop(instance.schema.primary_key)
        assert args[1] == mock_convert_types()
        return mock_ret

    instance.data.driver.create_one = mock_create_one

    if inspect.isclass(expect) and issubclass(expect, Exception):
        with pytest.raises(exceptions.DataEntryInvalid):
            commands.command_add(instance, arguments.copy())
    else:
        got = commands.command_add(instance, arguments.copy())
        assert got == [mock_ret]
        mock_convert_types.assert_called()


@pytest.mark.parametrize(['arguments'], [
    (['12345'],),
])
def test_command_del(instance, arguments):
    mock_ret = mock.Mock()
    mock_delete_one = mock.Mock()
    mock_delete_one.return_value = mock_ret
    instance.data.driver.delete_one = mock_delete_one
    got = commands.command_del(instance, arguments)
    assert got == [mock_ret]


@pytest.mark.parametrize(['arguments'], [
    (['12345'],),
])
def test_command_get(instance, arguments):
    mock_ret = mock.Mock()
    mock_read_one = mock.Mock()
    mock_read_one.return_value = mock_ret
    instance.data.driver.read_one = mock_read_one
    got = commands.command_get(instance, arguments)
    assert got == [mock_ret]


@pytest.mark.parametrize(['data', 'arguments', 'expect'], [
    ([...], [], [...]),
    ([{'k': 'v'}], [('k', 'v')], [{'k': 'v'}]),
    ([{'k': 'v1'}], [('k', 'v')], []),
    ([], [('k', 'v')], []),
    ([], [('k', 'v1'), ('k', 'v2')], exceptions.CommandArgumentConflict),
    ([{'k': 2}, {'k': 1}], [('$sort_asc', 'k')], [{'k': 1}, {'k': 2}]),
    ([{'k': 1}, {'k': 2}], [('$sort_desc', 'k')], [{'k': 2}, {'k': 1}]),
    ([{'k1': 2, 'k2': 1}, {'k1': 1, 'k2': 3}, {'k1': 2, 'k2': 2},
      {'k1': 2, 'k2': 1}],
     [('$sort_desc', 'k1'), ('$sort_asc', 'k2')],
     [{'k1': 2, 'k2': 1}, {'k1': 2, 'k2': 1}, {'k1': 2, 'k2': 2},
      {'k1': 1, 'k2': 3}]),
    ([..., ...], [('$illegal', 'v')], exceptions.InternalError),
])
def test_command_list(instance, data, arguments, expect):
    def mock_convert_types(*args, **kwargs):
        return utils.convert_argument_groups_into_dict(
            [group for group in arguments if not group[0].startswith('$')])

    def mock_build_cursor(*args, **kwargs):
        return len(data)

    def mock_next_row(cursor, *args, **kwargs):
        return cursor - 1, data[cursor - 1]

    @mock.patch.object(instance.schema, 'validate_keys', mock.Mock())
    @mock.patch.object(instance.schema, 'convert_types', mock_convert_types)
    @mock.patch.object(instance.data.driver, 'build_cursor', mock_build_cursor)
    @mock.patch.object(instance.data.driver, 'next_row', mock_next_row)
    def do_test():
        if inspect.isclass(expect) and issubclass(expect, Exception):
            with pytest.raises(expect):
                commands.command_list(instance, arguments)
        else:
            got = commands.command_list(instance, arguments)
            assert got == expect

    do_test()


@pytest.mark.parametrize(['arguments', 'expect'], [
    ([('id', '12345'), ('name', 'test')], True),
    ([('id', '12345'), ('id', '54321')], exceptions.CommandInvalidKeyArgument),
])
def test_command_mod(instance, arguments, expect):
    mock_ret = mock.Mock()

    mock_update_one = mock.Mock()
    mock_update_one.return_value = mock_ret

    instance.schema.primary_key = 'id'

    @mock.patch.object(instance.data.driver, 'update_one', mock_update_one)
    def do_test():
        if inspect.isclass(expect) and issubclass(expect, Exception):
            with pytest.raises(expect):
                commands.command_mod(instance, arguments)
        else:
            got = commands.command_mod(instance, arguments)
            assert got == [mock_ret]

    do_test()


def test_command_mod_invalid_key(instance):
    instance.schema.primary_key = 'another_key'
    with pytest.raises(exceptions.CommandInvalidKeyArgument):
        commands.command_mod(instance, arguments=[('id', '12345')])


def test_command_help_of_all(instance):
    mock_ret = {'test': mock.Mock()}
    mock_get_all_commands = mock.Mock()
    mock_get_all_commands.return_value = mock_ret

    @mock.patch('minesqlite.commands.get_all_commands', mock_get_all_commands)
    def do_test():
        commands.command_help(instance, [])

    do_test()


def test_command_help_of_specific(instance):
    mock_ret = mock.Mock()
    mock_cmd = mock.Mock()
    mock_get_command_info = mock.Mock()
    mock_get_command_info.return_value = mock_ret

    @mock.patch('minesqlite.commands.get_command_info', mock_get_command_info)
    def do_test():
        commands.command_help(instance, [mock_cmd])
        mock_get_command_info.assert_called_once_with(mock_cmd)

    do_test()