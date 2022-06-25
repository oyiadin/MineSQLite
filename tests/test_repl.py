# coding=utf-8
# Author: @hsiaoxychen
import inspect
import os

import pytest
from pytest_mock import MockerFixture

from minesqlite import repl
from minesqlite import exceptions
from tests.utils import *


@pytest.mark.parametrize(
    ['data', 'expect'],
    [
        # test for non-ascii characters, blank lines and spaces stripping
        (
            os.linesep.join(['a', 'a b', '测试', '', '', ' x', ' abc  ']),
            ['a', 'a b', '测试', 'x', 'abc'],
        ),
        # test for only blank lines
        (
            os.linesep * 3,
            [],
        ),
    ]
)
def test_read_lines(mocker: MockerFixture, instance, data, expect):
    mock_open = mocker.mock_open(read_data=data)
    instance.sysconf['repl.read.infile'] = mock_open()
    got = list(repl.read_lines(instance))
    assert got == expect


def test_read_interrupted(instance):
    class FakeFile(object):
        def __init__(self):
            self.index = 0
            self.data = ['a', 'b', None, 'c']

        def __iter__(self):
            return self

        def __next__(self):
            ret = self.data[self.index]
            if ret is None:
                raise KeyboardInterrupt
            self.index += 1
            return ret

    instance.sysconf['repl.read.infile'] = FakeFile()

    got = list(repl.read_lines(instance))
    assert got == ['a', 'b']


@pytest.mark.parametrize(
    ['data', 'success'],
    [
        ('t', True),
        ('T', True),
        ('TEST_test__0123_', True),
        ('__1', True),
        ('test-123', False),
        ('0123', False),
        ('test_测试', False),
        ('test_$', False),
        ('$test', False),
        ('$sort_asc', True),
        ('$sort_desc', True),  # TODO: constant
    ]
)
def test_validate_key(data, success):
    expect_exc = no_raise() if success \
        else raises(exceptions.CommandInvalidKeyArgument)
    with expect_exc:
        repl.validate_key(data)


@pytest.mark.parametrize(
    ['args_format', 'min_args', 'max_args', 'arguments', 'expect', 'expect_exc'],
    [
        # TEST CASES OF KEY-VALUE TYPE
        # normal test case with exactly one argument allowed
        (
            'key-value',
            1,
            1,
            ['k', 'v'],
            [('k', 'v')],
            no_raise(),
        ),
        # no companion value for the passed key
        (
            'key-value',
            1,
            1,
            ['k'],
            None,
            raises(exceptions.CommandKeyValueUnmatched),
        ),
        # too few arguments
        (
            'key-value',
            1,
            1,
            [],
            None,
            raises(exceptions.CommandTooFewArguments),
        ),
        # too many arguments
        (
            'key-value',
            1,
            1,
            ['k1', 'v1', 'k2', 'v2'],
            None,
            raises(exceptions.CommandTooManyArguments),
        ),
        # no argument while no parameter is required
        (
            'key-value',
            0,
            0,
            [],
            [],
            no_raise(),
        ),
        # no argument while min_args=0 was set
        (
            'key-value',
            0,
            1,
            [],
            [],
            no_raise(),
        ),
        # pass only one argument group while max_args=1 was set
        (
            'key-value',
            0,
            1,
            ['k', 'v'],
            [('k', 'v')],
            no_raise(),
        ),
        # try to do with an invalid key
        (
            'key-value',
            0,
            1,
            ['0-illegal-key', 'v'],
            None,
            raises(exceptions.CommandInvalidKeyArgument),
        ),

        # TEST CASES OF KEY TYPE
        (
            'key',
            1,
            1,
            ['k'],
            ['k'],
            no_raise(),
        ),
        (
            'key',
            1,
            1,
            [],
            None,
            raises(exceptions.CommandTooFewArguments),
        ),
        (
            'key',
            1,
            1,
            ['k1', 'k2'],
            None,
            raises(exceptions.CommandTooManyArguments),
        ),
        (
            'key',
            0,
            1,
            [],
            [],
            no_raise(),
        ),
        (
            'key',
            1,
            1,
            ['0-illegal-key'],
            None,
            raises(exceptions.CommandInvalidKeyArgument),
        ),

        # TEST CASES OF VALUE TYPE
        (
            'value',
            1,
            1,
            ['v'],
            ['v'],
            no_raise(),
        ),
        (
            'illegal-value',
            0,
            0,
            ['v'],
            None,
            raises(exceptions.InternalError),
        ),
    ]
)
def test_analyse_arguments(mocker: MockerFixture,
                           args_format, min_args, max_args, arguments,
                           expect, expect_exc):
    cmd_info = mocker.MagicMock()
    cmd_info.args_format = args_format
    cmd_info.min_args = min_args
    cmd_info.max_args = max_args

    with expect_exc:
        got = repl.analyse_arguments(cmd_info, arguments)
        assert got == expect


@pytest.mark.parametrize(['raise_exc'], [(False,), (True,)])
def test_repl_loop(mocker: MockerFixture, instance, raise_exc):
    mock_lines = [mocker.Mock]
    mock_read_lines = mocker.Mock()
    mock_read_lines.return_value = mock_lines

    mock_words = [mocker.Mock(), mocker.Mock()]
    mock_split_words = mocker.Mock()
    mock_split_words.return_value = mock_words

    mock_cmd_info = mocker.Mock()
    mock_get_command_info = mocker.Mock()
    mock_get_command_info.return_value = mock_cmd_info

    mock_grouped = mocker.Mock()
    mock_analyse_arguments = mocker.Mock()
    mock_analyse_arguments.return_value = mock_grouped

    mock_rows = mocker.Mock()
    mock_execute_command = mocker.Mock()
    mock_execute_command.return_value = mock_rows

    mock_print_results = mocker.Mock()

    mocker.patch('minesqlite.repl.read_lines', mock_read_lines)
    mocker.patch('minesqlite.repl.split_words', mock_split_words)
    mocker.patch('minesqlite.repl.get_command_info', mock_get_command_info)
    mocker.patch('minesqlite.repl.analyse_arguments', mock_analyse_arguments)
    mocker.patch('minesqlite.repl.execute_command', mock_execute_command)

    if not raise_exc:
        mocker.patch('minesqlite.repl.print_results', mock_print_results)

    repl.repl_loop(instance)
    mock_read_lines.assert_called_once()
    mock_split_words.assert_called_once_with(mock_lines[0])
    mock_get_command_info.assert_called_once_with(mock_words[0])
    mock_analyse_arguments.assert_called_once_with(mock_cmd_info, mock_words[1:])
    mock_execute_command.assert_called_once()

    if not raise_exc:
        mock_print_results.assert_called_once_with(instance, mock_rows)
