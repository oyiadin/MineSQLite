# coding=utf-8
# Author: @hsiaoxychen
import pytest
from pytest_mock import MockerFixture

from minesqlite import commands, exceptions
from minesqlite.common import utils
from minesqlite.command_registry import get_command_info
from tests.conftest import TEST_PK
from tests.utils import *


@pytest.mark.parametrize('arguments', [
    [('id', '12345'), ('name', 'Chen Xiaoyuan')],
])
def test_command_add(mocker: MockerFixture, instance, arguments):
    """Test the basic procedures of add command."""
    assert get_command_info('add') is not None

    mock_ret = mocker.Mock()
    mock_converted = mocker.Mock()
    mock_convert_types = mocker.MagicMock()
    mock_convert_types.return_value = mock_converted

    def mock_create_one(*args):
        assert args[0] == mock_converted.pop(instance.schema.primary_key)
        assert args[1] == mock_convert_types()
        return mock_ret

    mocker.patch.object(instance.schema, 'validate_keys')
    mocker.patch.object(instance.schema, 'convert_types', mock_convert_types)
    mocker.patch.object(instance.data.driver, 'create_one', mock_create_one)

    got = commands.command_add(instance, arguments.copy())
    assert got == [mock_ret]
    mock_convert_types.assert_called()


@pytest.mark.parametrize('arguments', [
    ['12345'],
])
def test_command_del(mocker: MockerFixture, instance, arguments):
    assert get_command_info('del') is not None

    mock_ret = mocker.Mock()
    mock_delete_one = mocker.Mock()
    mock_delete_one.return_value = mock_ret

    mocker.patch.object(instance.schema, 'convert_primary_key_type')
    mocker.patch.object(instance.data.driver, 'delete_one', mock_delete_one)

    got = commands.command_del(instance, arguments)
    assert got == [mock_ret]


@pytest.mark.parametrize('arguments', [
    ['12345'],
])
def test_command_get(mocker: MockerFixture, instance, arguments):
    assert get_command_info('get') is not None

    mock_ret = mocker.Mock()
    mock_read_one = mocker.Mock()
    mock_read_one.return_value = mock_ret

    mocker.patch.object(instance.schema, 'convert_primary_key_type')
    mocker.patch.object(instance.data.driver, 'read_one', mock_read_one)

    got = commands.command_get(instance, arguments)
    assert got == [mock_ret]


@pytest.mark.parametrize(
    ['data', 'arguments', 'expect', 'expect_exc'],
    [
        # empty query to empty data
        (
            [],
            [],
            [],
            no_raise(),
        ),
        # empty query to non-empty data
        (
            [...],
            [],
            [...],  # returns the whole original data
            no_raise(),
        ),
        # filter successfully
        (
            [{'pk': 'pkv1', 'k': 'v1'}, {'pk': 'pkv2', 'k': 'v2'}],
            [('k', 'v2')],
            [{'pk': 'pkv2', 'k': 'v2'}],
            no_raise(),
        ),
        # no entries matched after filtering
        (
            [{'k': 'v'}],
            [('k', 'v123')],
            [],
            no_raise(),
        ),
        # do filter in the empty data
        (
            [],
            [('k', 'v')],
            [],
            no_raise(),
        ),
        # do filter with conflict keys
        (
            [],
            [('k', 'v1'), ('k', 'v2')],
            None,
            raises(exceptions.CommandArgumentConflict),
        ),
        # sort in ascending order
        (
            [{'k': 2}, {'k': 1}],
            [('$sort_asc', 'k')],
            [{'k': 1}, {'k': 2}],
            no_raise(),
        ),
        # sort in descending order
        (
            [{'k': 1}, {'k': 2}],
            [('$sort_desc', 'k')],
            [{'k': 2}, {'k': 1}],
            no_raise(),
        ),
        # sort with multiple orders
        (
            [
                {'k1': 2, 'k2': 1},
                {'k1': 1, 'k2': 3},
                {'k1': 2, 'k2': 2},
                {'k1': 2, 'k2': 1},
            ],
            [('$sort_desc', 'k1'), ('$sort_asc', 'k2')],
            [
                {'k1': 2, 'k2': 1},
                {'k1': 2, 'k2': 1},
                {'k1': 2, 'k2': 2},
                {'k1': 1, 'k2': 3},
            ],
            no_raise(),
        ),
        # sort with illegal magic key
        (
            [..., ...],
            [('$illegal', 'v')],
            None,
            raises(exceptions.InternalError),
        ),
    ]
)
def test_command_list(mocker: MockerFixture, instance,
                      data, arguments, expect, expect_exc):
    assert get_command_info('list') is not None

    def mock_convert_types(*args, **kwargs):
        return utils.convert_argument_groups_into_dict(
            [group for group in arguments if not group[0].startswith('$')])

    def mock_build_cursor(*args, **kwargs):
        return len(data)

    def mock_next_row(cursor, *args, **kwargs):
        return cursor - 1, data[cursor - 1]

    mocker.patch.object(instance.schema, 'validate_keys')
    mocker.patch.object(instance.schema, 'convert_types', mock_convert_types)
    mocker.patch.object(instance.data.driver, 'build_cursor', mock_build_cursor)
    mocker.patch.object(instance.data.driver, 'next_row', mock_next_row)

    with expect_exc:
        got = commands.command_list(instance, arguments)
        assert got == expect


@pytest.mark.parametrize(
    ['arguments', 'expect_exc'],
    [
        # normal test case
        (
            [(TEST_PK, '12345'), ('name', 'test')],
            no_raise(),
        ),
        # try to modify primary key
        (
            [(TEST_PK, '12345'), (TEST_PK, '54321')],
            raises(exceptions.CommandInvalidKeyArgument),
        ),
        # try to match with non-primary key
        (
            [('something-not-pk', '12345'), ('name', 'test')],
            raises(exceptions.CommandInvalidKeyArgument),
        ),
    ]
)
def test_command_mod(mocker: MockerFixture, instance, arguments, expect_exc):
    assert get_command_info('mod') is not None

    mocker.patch.object(instance.schema, 'primary_key', TEST_PK)

    mock_ret = mocker.Mock()
    mock_update_one = mocker.Mock()
    mock_update_one.return_value = mock_ret
    mocker.patch.object(instance.data.driver, 'update_one', mock_update_one)

    with expect_exc:
        got = commands.command_mod(instance, arguments)
        assert got == [mock_ret]


def test_command_help_of_all(mocker: MockerFixture, instance):
    assert get_command_info('help') is not None

    mock_ret = {'test': mocker.Mock()}
    mock_get_all_commands = mocker.Mock()
    mock_get_all_commands.return_value = mock_ret
    mocker.patch('minesqlite.commands.get_all_commands', mock_get_all_commands)
    commands.command_help(instance, [])


def test_command_help_of_specific(mocker: MockerFixture, instance):
    mock_ret = mocker.Mock()
    mock_cmd = mocker.Mock()
    mock_get_command_info = mocker.Mock()
    mock_get_command_info.return_value = mock_ret

    mocker.patch('minesqlite.commands.get_command_info', mock_get_command_info)

    commands.command_help(instance, [mock_cmd])
    mock_get_command_info.assert_called_once_with(mock_cmd)
