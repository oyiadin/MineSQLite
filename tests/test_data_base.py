# coding=utf-8
# Author: @hsiaoxychen
import pytest

from minesqlite import exceptions
from minesqlite.data.drivers import memory_dict
from minesqlite.data.base import DataManager


def test_data_manager_memory_dict(instance):
    instance.sysconf['data.driver'] = 'memory_dict'
    manager = DataManager(instance)
    assert isinstance(manager.driver, memory_dict.MemoryDictDataManager)


def test_data_manager_illegal_driver(instance):
    instance.sysconf['data.driver'] = 'something_illegal'
    with pytest.raises(exceptions.InternalError):
        DataManager(instance)
