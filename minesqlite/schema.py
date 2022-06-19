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
    validator: typing.Callable = None
    converter: typing.Callable = None


field_types: dict[str, FieldType] = collections.defaultdict(FieldType)


def register_field_helper(helper_type: typing.Literal["validator", "converter"],
                          type_name: str):
    def decorator(func):
        setattr(field_types[type_name], helper_type, func)
        return func
    return decorator


class SchemaManager(object):
    def __init__(self, sysconf: 'SysConfManager'):
        infile = sysconf['schema.read.infile']
        data = yaml.safe_load(infile)
        self._inner_data = data
        self._primary_key = None

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
                self._primary_key = col
                break

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

    def validate_types(self, entry: dict):
        """Validate the types of each column within the entry."""
        for col in self._inner_data['columns']:
            if col['name'] not in entry:
                continue
            validator = field_types[col['type']].validator
            validator(entry[col['name']])

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
    @register_field_helper("validator", "integer")
    def _validate_integer_type(value: str):
        if not value.isdigit():
            raise exceptions.DataEntryInvalid(
                reason="invalid integer: %s" % value)

    @staticmethod
    @register_field_helper("converter", "integer")
    def _convert_integer_type(value: str) -> int:
        return int(value)

    @staticmethod
    @register_field_helper("validator", "string")
    def _validate_string_type(value: str):
        return True

    @staticmethod
    @register_field_helper("converter", "string")
    def _convert_string_type(value: str) -> str:
        return value

    @staticmethod
    @register_field_helper("validator", "date")
    def _validate_date_type(value: str):
        try:
            datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise exceptions.DataEntryInvalid(
                reason="incorrect date format, should be YYYY-MM-DD: %s"
                       % value)

    @staticmethod
    @register_field_helper("converter", "date")
    def _validate_date_type(value: str):
        return datetime.datetime.strptime(value, '%Y-%m-%d')
