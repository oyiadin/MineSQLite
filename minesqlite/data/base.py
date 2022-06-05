# coding=utf-8
# Author: @hsiaoxychen
import abc
import typing

from minesqlite.sysconf.manager import SysConfManager

_KeyType = str
_RowType = dict


class CursorABC(abc.ABC):
    pass


class DataManagerABC(abc.ABC):
    def __init__(self, sysconf: SysConfManager):
        self.sysconf = sysconf

    @abc.abstractmethod
    def create_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        pass

    @abc.abstractmethod
    def read_one(self, pk: _KeyType) -> _RowType:
        pass

    @abc.abstractmethod
    def next_row(self, cursor: typing.Optional[CursorABC] = None) \
            -> typing.Tuple[CursorABC, _RowType]:
        pass

    @abc.abstractmethod
    def update_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        pass

    @abc.abstractmethod
    def delete_one(self, pk: _KeyType) -> _RowType:
        pass


class DataManager(abc.ABC):
    def __init__(self, sysconf: SysConfManager):
        self.sysconf = sysconf
        self.driver: typing.Optional[DataManagerABC] = None

        driver_kwargs = {'sysconf': sysconf}
        if sysconf['data.driver'] == 'memory_dict':
            from minesqlite.data.memory_dict import manager as driver
            self.driver = driver.MemoryDictDataManager(**driver_kwargs)
        elif sysconf['data.driver'] == 'memory_bytes':
            from minesqlite.data.memory_bytes import manager as driver
            self.driver = driver.MemoryBytesDataManager(**driver_kwargs)
        else:
            raise ValueError(
                "unknown data.driver: {}".format(sysconf['data.driver']))
