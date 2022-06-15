# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
from minesqlite.data.base import DataManager
from minesqlite.schema import SchemaManager
from minesqlite.sysconf import SysConfManager


class MineSQLite(object):
    def __init__(self, sysconf_kwargs: dict):
        self.sysconf: SysConfManager = SysConfManager(**sysconf_kwargs)

        self.schema: SchemaManager = SchemaManager(self.sysconf)
        self.data: DataManager = DataManager(self)
