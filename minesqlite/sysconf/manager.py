# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

# TODO: 12 factor app
import configparser
import sys
import typing

from minesqlite.common.nested_dict import NestedDefaultDict

_KT = str
_VT = typing.Any


class SysConfManager(NestedDefaultDict):
    _DEFAULTS = {
        'repl.read.infile': 'stdin',
        'repl.read.prompt': '>>> ',
    }

    def __init__(self, conf_file: typing.TextIO):
        super().__init__(default_factory=lambda: None)

        # load defaults
        for k, v in self._DEFAULTS.items():
            self[k] = v

        # load config file
        if conf_file is not None:
            section = 'DEFAULT'
            config = configparser.ConfigParser()
            config.read_file(conf_file)
            for k, v in config.items(section=section):
                self[k] = v

    def _get_action_handler(self,
                            action: typing.Literal["set", "get", "del"],
                            key: str):
        attr = getattr(
            self, '_{}_{}'.format(action, key.replace('.', '_')), None)
        return attr if callable(attr) else None

    def __setitem__(self, k: _KT, v: _VT) -> None:
        handler: typing.Callable[[_KT, _VT], _VT] = \
            self._get_action_handler("set", k)
        newv = handler(k, v) if handler is not None else v
        super().__setitem__(k, newv)

    def __delitem__(self, k: _KT) -> None:
        handler: typing.Callable[[_KT], None] = \
            self._get_action_handler("del", k)
        if handler is not None:
            handler(k)
        super().__delitem__(k)

    def __getitem__(self, k: _KT) -> _VT:
        handler: typing.Callable[[_KT], _VT] = \
            self._get_action_handler("get", k)
        value = super().__getitem__(k)
        return handler(k) if handler is not None else value

    @staticmethod
    def _set_repl_read_infile(k: _KT, v: _VT) -> _VT:
        if v == 'stdin':
            return sys.stdin
        return open(v)
