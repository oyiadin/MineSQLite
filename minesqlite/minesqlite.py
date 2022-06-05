# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
from minesqlite.data.base import DataManager
from minesqlite.schema.manager import SchemaManager
from minesqlite.sysconf.manager import SysConfManager


class MineSQLite(object):
    def __init__(self, /, sysconf_kwargs=None):
        if sysconf_kwargs is None:
            sysconf_kwargs = {}
        self.sysconf = SysConfManager(**sysconf_kwargs)

        self.schema = SchemaManager(self.sysconf)
        self.data = DataManager(self.sysconf)
