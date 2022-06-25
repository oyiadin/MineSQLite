# coding=utf-8
# Author: @hsiaoxychen 2022/06/05
import collections
import datetime
import typing
from dataclasses import dataclass

import yaml

from minesqlite import exceptions

if typing.TYPE_CHECKING:
    from minesqlite.sysconf import SysConfManager


@dataclass
class FieldType(object):
    converter: typing.Callable = None


field_types: dict[str, FieldType] = collections.defaultdict(FieldType)


def register_field_helper(type_name: str):
    def decorator(func):
        setattr(field_types[type_name], 'converter', func)
        return func
    return decorator


class SchemaManager(object):
    def __init__(self, sysconf: 'SysConfManager'):
        infile = sysconf['schema.read.infile']
        data = yaml.safe_load(infile)
        self._inner_data = data
        self._primary_key = None

        if 'columns' not in data or not data['columns']:
            raise exceptions.InternalError(
                "`columns` is required to be a non-empty list")

        # validate `type` field
        for col in data['columns']:
            if 'type' not in col:
                raise exceptions.InternalError(
                    "`type` required in schema definition")
            if col['type'] not in field_types.keys():
                raise exceptions.InternalError(
                    "invalid value of `type` within schema definition: %s"
                    % col['type'])

        for col in data['columns']:
            attrs = col.get('attribute', '').split(',')
            if 'primary_key' in attrs:
                if self._primary_key is not None:
                    raise exceptions.InternalError(
                        "multiple primary key is not allowed")
                self._primary_key = col

        if self._primary_key is None:
            raise exceptions.InternalError(
                "no primary_key found within schema definition")

    @property
    def fields(self):
        return [col['name'] for col in self._inner_data['columns']]

    @property
    def primary_key(self):
        return self._primary_key['name']

    def validate_keys(self, entry: dict, no_missing=True, no_extra=True):
        """To ensure that no extra keys or missing keys in the entry."""
        got_keys = set(entry.keys())
        expect_keys = set(self.fields)
        if got_keys != expect_keys:
            missing_keys = expect_keys - got_keys
            extra_keys = got_keys - expect_keys
            if missing_keys and no_missing:
                raise exceptions.DataEntryInvalid(
                    reason="missing keys: %s" % ', '.join(missing_keys))
            if extra_keys and no_extra:
                raise exceptions.DataEntryInvalid(
                    reason="unexpected extra keys: %s" % ', '.join(extra_keys))

    def convert_types(self, entry: dict) -> dict:
        """Convert the entry inplace."""
        for col in self._inner_data['columns']:
            if col['name'] not in entry:
                continue
            converter = field_types[col['type']].converter
            converted = converter(entry[col['name']])
            entry[col['name']] = converted
        return entry

    def convert_primary_key_type(self, pk_value: str) -> typing.Any:
        field_type = self._primary_key['type']
        return field_types[field_type].converter(pk_value)

    @staticmethod
    @register_field_helper("integer")
    def _convert_integer_type(value: str) -> int:
        try:
            return int(value)
        except Exception as e:
            raise exceptions.DataEntryInvalid(
                reason="invalid integer: %s" % value) from e

    @staticmethod
    @register_field_helper("string")
    def _convert_string_type(value: str) -> str:
        return value

    @staticmethod
    @register_field_helper("date")
    def _convert_date_type(value: str):
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError as e:
            raise exceptions.DataEntryInvalid(
                reason="incorrect date format, should be YYYY-MM-DD: %s"
                       % value) from e
