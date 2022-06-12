# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import typing

import yaml

if typing.TYPE_CHECKING:
    from minesqlite.sysconf import SysConfManager


class SchemaManager(object):
    def __init__(self, sysconf: 'SysConfManager'):
        infile = sysconf['schema.read.infile']
        data = yaml.safe_load(infile)
        self._inner_data = data
        self._primary_key = None

        for col in data['columns']:
            attrs = col.get('attribute', '').split(',')
            if 'primary_key' in attrs:
                self._primary_key = col
                break

    @property
    def fields(self):
        return [col['name'] for col in self._inner_data['columns']]

    @property
    def primary_key(self):
        return self._primary_key['name']
