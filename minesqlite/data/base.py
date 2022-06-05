# coding=utf-8
# Author: @hsiaoxychen
import abc
import typing

if typing.TYPE_CHECKING:
    from minesqlite.minesqlite import MineSQLite


_KeyType = str
_RowType = dict


class CursorABC(abc.ABC):
    @abc.abstractmethod
    def __bool__(self):
        pass


class DataManagerABC(abc.ABC):
    def __init__(self, instance: 'MineSQLite'):
        self.instance = instance

    @abc.abstractmethod
    def create_one(self, pk: _KeyType, kvs: _RowType) -> _RowType:
        pass

    @abc.abstractmethod
    def read_one(self, pk: _KeyType) -> _RowType:
        pass

    @abc.abstractmethod
    def build_cursor(self) -> CursorABC:
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
    def __init__(self, instance: 'MineSQLite'):
        self.instance = instance
        self.driver: typing.Optional[DataManagerABC] = None

        driver_kwargs = {'instance': instance}
        data_driver = instance.sysconf['data.driver']
        if data_driver == 'memory_dict':
            from minesqlite.data.memory_dict import manager as driver
            self.driver = driver.MemoryDictDataManager(**driver_kwargs)
        elif data_driver == 'memory_bytes':
            from minesqlite.data.memory_bytes import manager as driver
            self.driver = driver.MemoryBytesDataManager(**driver_kwargs)
        else:
            raise ValueError("unknown data.driver: {}".format(data_driver))
