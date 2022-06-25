# coding=utf-8
# Author: @hsiaoxychen
import inspect

import pytest
from pytest_mock import MockerFixture

from conftest import TEST_PK
from minesqlite import exceptions
from minesqlite.data.drivers.memory_dict import MemoryDictDataManager
from tests.utils import *


@pytest.fixture
def manager(instance):
    return MemoryDictDataManager(instance)


@pytest.mark.parametrize(
    ['initial_data', 'pk', 'kvs', 'expect_ret', 'expect_exc', 'expect_data'],
    [
        # insert duplicated entry
        (
            {'pk': ...},
            'pk',
            ...,
            None,
            raises(exceptions.DataDuplicateEntry),
            {'pk': ...},
        ),
        (
            {'pk1': ...},
            'pk2',
            {'k': 'v'},
            {TEST_PK: 'pk2', 'k': 'v'},
            no_raise(),
            {'pk1': ..., 'pk2': {'k': 'v'}},
        ),
    ]
)
def test_create_one(mocker: MockerFixture, instance, manager,
                    initial_data, pk, kvs, expect_ret, expect_exc, expect_data):
    mocker.patch.object(instance.schema, 'primary_key', TEST_PK)

    manager._inner_data = initial_data

    with expect_exc:
        got = manager.create_one(pk, kvs)
        assert got == expect_ret

    assert manager._inner_data == expect_data


@pytest.mark.parametrize(
    ['initial_data', 'pk', 'expect_ret', 'expect_exc'],
    [
        # read existed entry
        (
            {'pk': {'k': 'v'}},
            'pk',
            {TEST_PK: 'pk', 'k': 'v'},
            no_raise(),
        ),
        # read non-exist entry
        (
            {'pk': {'k': 'v'}},
            'pk2',
            None,
            raises(exceptions.DataEntryNotFound),
        ),
    ]
)
def test_read_one(mocker: MockerFixture, instance, manager,
                  initial_data, pk, expect_ret, expect_exc):
    mocker.patch.object(instance.schema, 'primary_key', TEST_PK)

    manager._inner_data = initial_data

    with expect_exc:
        got = manager.read_one(pk)
        assert got == expect_ret

    assert manager._inner_data == initial_data


@pytest.mark.parametrize(
    ['initial_data', 'expect_ret'],
    [
        (
            {'pk1': {'k1': 'v1'}},
            {'id': 'pk1', 'k1': 'v1'},
        ),
    ]
)
def test_traverse_one_row(mocker: MockerFixture, instance, manager,
                          initial_data, expect_ret):
    mocker.patch.object(instance.schema, 'primary_key', 'id')

    manager._inner_data = initial_data
    cursor = manager.build_cursor()
    assert cursor

    cursor, row = manager.next_row(cursor)
    assert not cursor
    assert row == expect_ret


def test_traverse_no_row(instance, manager):
    manager._inner_data = {}
    cursor = manager.build_cursor()
    assert not cursor


@pytest.mark.parametrize(
    ['initial_data', 'pk', 'kvs', 'expect_ret', 'expect_exc', 'expect_data'],
    [
        # check the data before and after a modification
        (
            {'pk1': {'k1': 'v1', 'k2': 'v2'}},
            'pk1',
            {'k1': 'v11', 'k3': 'v3'},
            {TEST_PK: 'pk1', 'k1': 'v11', 'k2': 'v2', 'k3': 'v3'},
            no_raise(),
            {'pk1': {'k1': 'v11', 'k2': 'v2', 'k3': 'v3'}},
        ),
        # modify non-exist entry
        (
            {},
            'pk1',
            {'k': 'v'},
            None,
            raises(exceptions.DataEntryNotFound),
            {},
        ),
    ]
)
def test_update_one(mocker: MockerFixture, instance, manager,
                    initial_data, pk, kvs, expect_ret, expect_exc, expect_data):
    mocker.patch.object(instance.schema, 'primary_key', TEST_PK)

    manager._inner_data = initial_data

    with expect_exc:
        got = manager.update_one(pk, kvs)
        assert got == expect_ret

    assert manager._inner_data == initial_data


@pytest.mark.parametrize(
    ['initial_data', 'pk', 'expect_ret', 'expect_exc', 'expect_data'], 
    [
        # assert that the matched entry be deleted
        (
            {'pk1': {'k1': 'v1'}},
            'pk1',
            {TEST_PK: 'pk1', 'k1': 'v1'},
            no_raise(),
            {},
        ),
        # delete a non-exist entry
        (
            {}, 
            'pk1', 
            None,
            raises(exceptions.DataEntryNotFound), 
            {},
        ),
    ]
)
def test_delete_one(mocker: MockerFixture, instance, manager,
                    initial_data, pk, expect_ret, expect_exc, expect_data):
    mocker.patch.object(instance.schema, 'primary_key', TEST_PK)

    manager._inner_data = initial_data

    with expect_exc:
        got = manager.delete_one(pk)
        assert got == expect_ret

    assert manager._inner_data == initial_data
