# coding=utf-8
# Author: @hsiaoxychen
import inspect
import os
from unittest import mock

import pytest

from minesqlite import repl
from minesqlite import exceptions


@pytest.mark.parametrize(['data', 'expect'], [
    # test for non-ascii characters, blank lines and spaces stripping
    (os.linesep.join(['a', 'a b', '测试', '', '', ' x', ' abc  ']),
     ['a', 'a b', '测试', 'x', 'abc']),
    # test for only blank lines
    (os.linesep * 3,
     []),
])
def test_read_lines(instance, data, expect):
    mock_open = mock.mock_open(read_data=data)
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


@pytest.mark.parametrize(['data', 'expect'], [
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
])
def test_validate_key(data, expect):
    if expect:
        repl.validate_key(data)
    else:
        with pytest.raises(exceptions.CommandInvalidKeyArgument):
            repl.validate_key(data)


def test_validate_value():
    repl.validate_value(mock.Mock())


@pytest.mark.parametrize(
    ['args_format', 'min_args', 'max_args', 'arguments', 'expect'],
    [
        ('key-value', 1, 1, ['k', 'v'], [('k', 'v')]),
        ('key-value', 1, 1, ['k'], exceptions.CommandKeyValueUnmatched),
        ('key-value', 1, 1, [], exceptions.CommandTooFewArguments),
        ('key-value', 1, 1, ['k1', 'v1', 'k2', 'v2'],
         exceptions.CommandTooManyArguments),
        ('key-value', 0, 0, [], []),
        ('key-value', 0, 0, ['k', 'v'], exceptions.CommandTooManyArguments),
        ('key-value', 0, 1, [], []),
        ('key-value', 0, 1, ['k', 'v'], [('k', 'v')]),
        ('key-value', 0, 1, ['0-illegal-key', 'v'],
         exceptions.CommandInvalidKeyArgument),

        ('key', 1, 1, ['k'], ['k']),
        ('key', 1, 1, [], exceptions.CommandTooFewArguments),
        ('key', 1, 1, ['k1', 'k2'], exceptions.CommandTooManyArguments),
        ('key', 0, 1, [], []),
        ('key', 1, 1, ['0-illegal-key'], exceptions.CommandInvalidKeyArgument),

        ('value', 1, 1, ['v'], ['v']),
        ('illegal-value', 0, 0, ['v'], exceptions.InternalError),
    ]
)
def test_analyse_arguments(args_format, min_args, max_args, arguments, expect):
    cmd_info = mock.MagicMock()
    cmd_info.args_format = args_format
    cmd_info.min_args = min_args
    cmd_info.max_args = max_args

    if inspect.isclass(expect) and issubclass(expect, Exception):
        with pytest.raises(expect):
            repl.analyse_arguments(cmd_info, arguments)
    else:
        got = repl.analyse_arguments(cmd_info, arguments)
        assert got == expect


@pytest.mark.parametrize(['raise_exc'], [(False,), (True,)])
def test_repl_loop(instance, raise_exc):
    mock_lines = [mock.Mock]
    mock_read_lines = mock.Mock()
    mock_read_lines.return_value = mock_lines

    mock_words = [mock.Mock(), mock.Mock()]
    mock_split_words = mock.Mock()
    mock_split_words.return_value = mock_words

    mock_cmd_info = mock.Mock()
    mock_get_command_info = mock.Mock()
    mock_get_command_info.return_value = mock_cmd_info

    mock_grouped = mock.Mock()
    mock_analyse_arguments = mock.Mock()
    mock_analyse_arguments.return_value = mock_grouped

    mock_rows = mock.Mock()
    mock_execute_command = mock.Mock()
    mock_execute_command.return_value = mock_rows

    mock_print_results = mock.Mock()

    @mock.patch('minesqlite.repl.read_lines', mock_read_lines)
    @mock.patch('minesqlite.repl.split_words', mock_split_words)
    @mock.patch('minesqlite.repl.get_command_info', mock_get_command_info)
    @mock.patch('minesqlite.repl.analyse_arguments', mock_analyse_arguments)
    @mock.patch('minesqlite.repl.execute_command', mock_execute_command)
    def do_test():
        repl.repl_loop(instance)
        mock_read_lines.assert_called_once()
        mock_split_words.assert_called_once_with(mock_lines[0])
        mock_get_command_info.assert_called_once_with(mock_words[0])
        mock_analyse_arguments.assert_called_once_with(mock_cmd_info, mock_words[1:])
        mock_execute_command.assert_called_once()

    if not raise_exc:
        with mock.patch('minesqlite.repl.print_results', mock_print_results):
            do_test()
            mock_print_results.assert_called_once_with(instance, mock_rows)
    else:
        do_test()
