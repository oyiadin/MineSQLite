# coding=utf-8
# Author: @hsiaoxychen
import datetime
import os

import pytest
from pytest_mock import MockerFixture

from minesqlite import schema, exceptions
from tests.utils import *


@pytest.mark.parametrize(
    ['data', 'expect', 'expect_exc'],
    [
        # no any columns
        (
            'columns:',
            None,
            raises(exceptions.InternalError),
        ),
        # two normal columns
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: string',
                '    attribute: primary_key',
                '  - name: id2',
                '    type: string',
            ]),
            ['id1', 'id2'],
            no_raise(),
        ),
        # some columns are without type field
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: string',
                '    attribute: primary_key',
                '  - name: id2',
            ]),
            ['id1', 'id2'],
            raises(exceptions.InternalError),
        ),
        # wrong type value
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: something illegal',
            ]),
            None,
            raises(exceptions.InternalError),
        )
    ]
)
def test_fields(mocker: MockerFixture, sysconf, data, expect, expect_exc):
    mock_open = mocker.mock_open(read_data=data)
    sysconf['schema.read.infile'] = mock_open()
    with expect_exc:
        manager = schema.SchemaManager(sysconf)
        assert manager.fields == expect


@pytest.mark.parametrize(
    ['data', 'expect', 'expect_exc'],
    [
        # no primary key
        (
            'columns:',
            None,
            raises(exceptions.InternalError),
        ),
        # two columns but without any primary keys
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: string',
                '  - name: id2',
                '    type: string',
            ]),
            None,
            raises(exceptions.InternalError),
        ),
        # three columns with a primary key
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: string',
                '  - name: id2',
                '    type: string',
                '    attribute: primary_key',
                '  - name: id3',
                '    type: string',
            ]),
            'id2',
            no_raise(),
        ),
        # two columns with multiple primary keys
        (
            os.linesep.join([
                'columns:',
                '  - name: id1',
                '    type: string',
                '    attribute: primary_key',
                '  - name: id2',
                '    type: string',
                '    attribute: primary_key',
            ]),
            None,
            raises(exceptions.InternalError),
        ),
    ]
)
def test_primary_key(mocker: MockerFixture, sysconf, data, expect, expect_exc):
    mock_open = mocker.mock_open(read_data=data)
    sysconf['schema.read.infile'] = mock_open()
    with expect_exc:
        manager = schema.SchemaManager(sysconf)
        assert manager.primary_key == expect


@pytest.mark.parametrize(
    'data',
    [
        os.linesep.join([
            'columns:',
            '  - name: id1',
            '    type: string',
            '  - name: id2',
            '    type: string',
            '    attribute: primary_key',
        ]),
    ]
)
@pytest.mark.parametrize(
    ['entry', 'expect_exc'],
    [
        # normal test case
        (
            {
                'id1': 'v1',
                'id2': 'v2',
            },
            no_raise(),
        ),
        # missing primary key
        (
            {
                'id1': 'v1',
            },
            raises(exceptions.DataEntryInvalid),
        ),
        # missing non-primary key
        (
            {
                'id2': 'v2',
            },
            raises(exceptions.DataEntryInvalid),
        ),
        # with extra key
        (
            {
                'id1': 'v1',
                'id2': 'v2',
                'id3': 'v3',
            },
            raises(exceptions.DataEntryInvalid),
        ),
        # missing & extra key
        (
            {
                'id2': 'v2',
                'id3': 'v3',
            },
            raises(exceptions.DataEntryInvalid),
        ),
    ]
)
def test_validate_keys(mocker: MockerFixture, sysconf, data, entry, expect_exc):
    mock_open = mocker.mock_open(read_data=data)
    sysconf['schema.read.infile'] = mock_open()
    with expect_exc:
        manager = schema.SchemaManager(sysconf)
        manager.validate_keys(entry)


@pytest.mark.parametrize(
    'data',
    [
        os.linesep.join([
            'columns:',
            '  - name: key',
            '    type: integer',
            '    attribute: primary_key',
        ]),
    ]
)
@pytest.mark.parametrize(
    ['value', 'expect', 'expect_exc'],
    [
        # normal test cases
        (0, 0, no_raise()),
        (123, 123, no_raise()),
        ('123', 123, no_raise()),
        # invalid test cases
        ('a123', None, raises(exceptions.DataEntryInvalid)),
        ('1.2', None, raises(exceptions.DataEntryInvalid)),
    ]
)
def test_convert_types_integer(mocker: MockerFixture, sysconf,
                               data, value, expect, expect_exc):
    mock_open = mocker.mock_open(read_data=data)
    sysconf['schema.read.infile'] = mock_open()
    with expect_exc:
        manager = schema.SchemaManager(sysconf)
        got = manager.convert_types({'key': value})
        assert got == {'key': expect}


@pytest.mark.parametrize(
    'data',
    [
        os.linesep.join([
            'columns:',
            '  - name: key',
            '    type: date',
            '    attribute: primary_key',
        ]),
    ]
)
@pytest.mark.parametrize(
    ['value', 'expect', 'expect_exc'],
    [
        # normal test case
        (
            '2022-06-25',
            datetime.datetime.strptime('2022-06-25', '%Y-%m-%d'),
            no_raise(),
        ),
        # invalid test cases
        (
            '2022-06-251',
            None,
            raises(exceptions.DataEntryInvalid),
        ),
    ]
)
def test_convert_types_date(mocker: MockerFixture, sysconf,
                            data, value, expect, expect_exc):
    mock_open = mocker.mock_open(read_data=data)
    sysconf['schema.read.infile'] = mock_open()
    with expect_exc:
        manager = schema.SchemaManager(sysconf)
        got = manager.convert_types({'key': value})
        assert got == {'key': expect}
