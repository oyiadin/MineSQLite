# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import yaml

from minesqlite.sysconf.manager import SysConfManager


class SchemaManager(object):
    def __init__(self, sysconf: SysConfManager):
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
        return self._primary_key

    def validate_fields(self, kvs: dict):
        got_keys = set(kvs.keys())
        expect_keys = set(self.fields)
        if got_keys != expect_keys:
            missing_keys = expect_keys - got_keys
            extra_keys = got_keys - expect_keys
            if missing_keys:
                raise ValueError(
                    "missing keys: {}".format(', '.join(missing_keys)))
            if extra_keys:
                raise ValueError(
                    "unexpected extra keys: {}".format(', '.join(extra_keys)))
