# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

import minesqlite.commands
from minesqlite.data import base as data_base
from minesqlite import schema
from minesqlite import sysconf

__version__ = '0.0.1'


class MineSQLite(object):
    def __init__(self, sysconf_kwargs: dict):
        self.sysconf = sysconf.SysConfManager(**sysconf_kwargs)
        self.schema = schema.SchemaManager(self.sysconf)
        self.data = data_base.DataManager(self)
