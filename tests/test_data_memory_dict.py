# coding=utf-8
# Author: @hsiaoxychen
import inspect
from unittest import mock

import pytest

from minesqlite import exceptions
from minesqlite.data.drivers.memory_dict import MemoryDictDataManager


@pytest.fixture
def manager(instance):
    return MemoryDictDataManager(instance)


@pytest.mark.parametrize(['initial_data', 'pk', 'kvs', 'expect_ret', 'expect_data'], [
    ({'pk': {}}, 'pk', {}, exceptions.DataDuplicateEntry, {'pk': {}}),
    ({'pk1': {}}, 'pk2', {'k': 'v'}, {'id': 'pk2', 'k': 'v'}, {'pk1': {}, 'pk2': {'k': 'v'}}),
])
def test_create_one(instance, manager, initial_data, pk, kvs, expect_ret, expect_data):
    @mock.patch.object(instance.schema, 'primary_key', 'id')
    def do_test():
        manager._inner_data = initial_data

        if inspect.isclass(expect_ret) and issubclass(expect_ret, Exception):
            with pytest.raises(expect_ret):
                manager.create_one(pk, kvs)
        else:
            got = manager.create_one(pk, kvs)
            assert got == expect_ret

        assert manager._inner_data == expect_data

    do_test()


@pytest.mark.parametrize(['initial_data', 'pk', 'expect_ret'], [
    ({'pk': {'k': 'v'}}, 'pk', {'id': 'pk', 'k': 'v'}),
    ({'pk': {'k': 'v'}}, 'pk2', exceptions.DataEntryNotFound),
])
def test_read_one(instance, manager, initial_data, pk, expect_ret):
    @mock.patch.object(instance.schema, 'primary_key', 'id')
    def do_test():
        manager._inner_data = initial_data

        if inspect.isclass(expect_ret) and issubclass(expect_ret, Exception):
            with pytest.raises(expect_ret):
                manager.read_one(pk)
        else:
            got = manager.read_one(pk)
            assert got == expect_ret

        assert manager._inner_data == initial_data

    do_test()


@pytest.mark.parametrize(['initial_data', 'expect_ret'], [
    ({'pk1': {'k1': 'v1'}}, {'id': 'pk1', 'k1': 'v1'}),
])
def test_traverse_one_row(instance, manager, initial_data, expect_ret):
    @mock.patch.object(instance.schema, 'primary_key', 'id')
    def do_test():
        manager._inner_data = initial_data
        cursor = manager.build_cursor()
        assert cursor

        cursor, row = manager.next_row(cursor)
        assert not cursor
        assert row == expect_ret

    do_test()


def test_traverse_no_row(instance, manager):
    manager._inner_data = {}
    cursor = manager.build_cursor()
    assert not cursor


@pytest.mark.parametrize(['initial_data', 'pk', 'kvs', 'expect_ret', 'expect_data'], [
    ({}, 'pk1', {'k': 'v'}, exceptions.DataEntryNotFound, {}),
    ({'pk1': {'k1': 'v1', 'k2': 'v2'}}, 'pk1', {'k1': 'v11', 'k3': 'v3'},
     {'id': 'pk1', 'k1': 'v11', 'k2': 'v2', 'k3': 'v3'},
     {'pk1': {'k1': 'v11', 'k2': 'v2', 'k3': 'v3'}}),
])
def test_update_one(instance, manager, initial_data, pk, kvs, expect_ret, expect_data):
    @mock.patch.object(instance.schema, 'primary_key', 'id')
    def do_test():
        manager._inner_data = initial_data

        if inspect.isclass(expect_ret) and issubclass(expect_ret, Exception):
            with pytest.raises(expect_ret):
                manager.update_one(pk, kvs)
        else:
            got = manager.update_one(pk, kvs)
            assert got == expect_ret

        assert manager._inner_data == initial_data

    do_test()


@pytest.mark.parametrize(['initial_data', 'pk', 'expect_ret', 'expect_data'], [
    ({}, 'pk1', exceptions.DataEntryNotFound, {}),
    ({'pk1': {'k1': 'v1'}}, 'pk1', {'id': 'pk1', 'k1': 'v1'}, {}),
])
def test_delete_one(instance, manager, initial_data, pk, expect_ret, expect_data):
    @mock.patch.object(instance.schema, 'primary_key', 'id')
    def do_test():
        manager._inner_data = initial_data

        if inspect.isclass(expect_ret) and issubclass(expect_ret, Exception):
            with pytest.raises(expect_ret):
                manager.delete_one(pk)
        else:
            got = manager.delete_one(pk)
            assert got == expect_ret

        assert manager._inner_data == initial_data

    do_test()
