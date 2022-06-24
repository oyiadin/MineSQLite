# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

import minesqlite.commands
from minesqlite.data.base import DataManager
from minesqlite.schema import SchemaManager
from minesqlite.sysconf import SysConfManager

__version__ = '0.0.1'


class MineSQLite(object):
    def __init__(self, sysconf_kwargs: dict):
        self.sysconf: SysConfManager = SysConfManager(**sysconf_kwargs)
        self.schema: SchemaManager = SchemaManager(self.sysconf)
        self.data: DataManager = DataManager(self)
