# coding=utf-8
# Author: @hsiaoxychen
import abc
import typing

from minesqlite import exceptions

if typing.TYPE_CHECKING:
    from minesqlite import MineSQLite


_KeyType = str
_RowType = dict


class CursorABC(abc.ABC):
    @abc.abstractmethod
    def __bool__(self):
        pass


class DataManagerABC(abc.ABC):
    def __init__(self, instance: 'MineSQLite'):
        self.instance = instance

    @property
    def pk(self):
        """Primary key name."""
        return self.instance.schema.primary_key

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
            from minesqlite.data.drivers import memory_dict as driver
            self.driver = driver.MemoryDictDataManager(**driver_kwargs)
        else:
            raise exceptions.InternalError(
                "unknown data.driver: %s" % data_driver)
