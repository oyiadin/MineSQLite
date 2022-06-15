# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing


class MineSQLiteException(Exception):
    errcode: str = None
    message_format: str = None

    def __init__(self, message_format=None, **kwargs):
        if not message_format:
            message_format = self.message_format
        message = message_format % kwargs
        super().__init__(message)


class InternalError(MineSQLiteException):
    errcode = '0x100000'
    message_format = 'internal error: %(msg)s'


class CommandNotFound(MineSQLiteException):
    errcode = '0x101000'
    message_format = 'command not found: %(command)s'


class CommandKeyValueUnmatched(MineSQLiteException):
    errcode = '0x101001'
    message_format = 'you should provide a value for the key `%(key)s`'


class CommandInvalidKeyArgument(MineSQLiteException):
    errcode = '0x101002'
    message_format = 'invalid key-argument: `%(key)s`'


class CommandInvalidValueArgument(MineSQLiteException):
    errcode = '0x101003'
    message_format = 'invalid value-argument: `%(value)s`'


class CommandTooFewArguments(MineSQLiteException):
    errcode = '0x101004'
    message_format = "too few arguments! expect %(expect)d argument(-groups) " \
                     "while only %(real)d supplied."


class CommandTooManyArguments(MineSQLiteException):
    errcode = '0x101005'
    message_format = "too many arguments! expect %(expect)d argument(-groups)" \
                     " while %(real)d supplied."


class CommandArgumentConflict(MineSQLiteException):
    errcode = '0x101006'
    message_format = "conflict argument: %(key)s"


class DataDuplicateEntry(MineSQLiteException):
    errcode = '0x102001'
    message_format = 'duplicate entry: there is already an entry ' \
                     'whose `%(field)s` equals to `%(value)s`'


class DataEntryNotFound(MineSQLiteException):
    errcode = '0x102002'
    message_format = 'no any entries matching %(field)s=%(value)s were found.'


class DataEntryInvalid(MineSQLiteException):
    errcode = '0x102003'
    message_format = 'invalid entry: %(reason)s'
