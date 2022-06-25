# coding=utf-8
# Author: @hsiaoxychen
"""Integration tests."""
import os
import datetime
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from minesqlite import MineSQLite, exceptions
from minesqlite import commands


def test_integration(mocker: MockerFixture, tmp_path: Path):
    config = os.linesep.join([
        '[DEFAULT]',
        'general.debug = true',
        'repl.banner = banner',
        'repl.read.infile = stdin',
        'repl.read.prompt = ">>> "',
        'schema.read.infile = {schema_filepath}',
        'data.driver = memory_dict',
    ])
    schema = os.linesep.join([
        'columns:',
        '  - name: id',
        '    type: integer',
        '    attribute: primary_key',
        '  - name: name',
        '    type: string',
        '  - name: date',
        '    type: date',
    ])
    test_datas = [
        [('id', '100'), ('name', 'A-original'), ('date', '2022-06-25')],
        [('id', '104'), ('name', 'D'), ('date', '2022-06-23')],
        [('id', '103'), ('name', 'C'), ('date', '2022-06-24')],
        [('id', '101'), ('name', 'B'), ('date', '2022-06-25')],
        [('id', '99'), ('name', 'A'), ('date', '2022-06-25')],
    ]
    expect_datas = [
        {'id': 100, 'name': 'A',
         'date': datetime.datetime.strptime('2022-06-25', '%Y-%m-%d')},
        {'id': 104, 'name': 'D',
         'date': datetime.datetime.strptime('2022-06-23', '%Y-%m-%d')},
        {'id': 103, 'name': 'C',
         'date': datetime.datetime.strptime('2022-06-24', '%Y-%m-%d')},
        {'id': 101, 'name': 'B',
         'date': datetime.datetime.strptime('2022-06-25', '%Y-%m-%d')},
        {'id': 99, 'name': 'A',
         'date': datetime.datetime.strptime('2022-06-25', '%Y-%m-%d')},
    ]

    schema_filepath = tmp_path / "schema.txt"
    schema_filepath.write_text(schema)
    config = config.format(schema_filepath=schema_filepath)
    mock_open = mocker.mock_open(read_data=config)
    instance = MineSQLite(
        sysconf_kwargs={'conf_file': mock_open()})

    # assert that no any data right now
    assert commands.command_list(instance, []) == []

    # normally add then get, and get a not found entry
    expect_data = {
        'id': 100, 'name': 'A-original',
        'date': datetime.datetime.strptime('2022-06-25', '%Y-%m-%d')}
    assert commands.command_add(instance, test_datas[0]) == [expect_data]
    assert commands.command_get(instance, [expect_datas[0]['id']]) \
           == [expect_data]
    with pytest.raises(exceptions.DataEntryNotFound):
        commands.command_get(instance, ['114514'])

    # modify an existed entry
    assert commands.command_mod(instance,
                                [('id', '100'), ('name', 'A')]) \
           == [expect_datas[0]]

    # modify a non-existed entry
    with pytest.raises(exceptions.DataEntryNotFound):
        commands.command_mod(instance,
                             [('id', '114514'), ('name', 'hey!')])

    # add an entry with duplicate id
    with pytest.raises(exceptions.DataDuplicateEntry):
        commands.command_add(instance, test_datas[0])

    # add an entry then delete
    commands.command_add(
        instance, [('id', '1234'), ('name', 'A'), ('date', '2022-06-25')])
    assert len(commands.command_list(instance, [])) == 2
    commands.command_del(instance, ['1234'])
    assert len(commands.command_list(instance, [])) == 1

    # delete a non-existed entry
    with pytest.raises(exceptions.DataEntryNotFound):
        commands.command_del(instance, ['1234'])

    # add some other test data and then test list
    for n, test_data in enumerate(test_datas[1:]):
        assert commands.command_add(instance, test_data) == [expect_datas[n+1]]
    assert commands.command_list(instance, []) == expect_datas
    assert len(commands.command_list(instance, [('name', 'A')])) == 2
    assert commands.command_list(instance,
                                 [('$sort_asc', 'date'),
                                  ('$sort_desc', 'name'),
                                  ('$sort_asc', 'id')]) \
           == [{'id': 104, 'name': 'D',
                'date': datetime.datetime(2022, 6, 23, 0, 0)},
               {'id': 103, 'name': 'C',
                'date': datetime.datetime(2022, 6, 24, 0, 0)},
               {'id': 101, 'name': 'B',
                'date': datetime.datetime(2022, 6, 25, 0, 0)},
               {'id': 99, 'name': 'A',
                'date': datetime.datetime(2022, 6, 25, 0, 0)},
               {'id': 100, 'name': 'A',
                'date': datetime.datetime(2022, 6, 25, 0, 0)}]
