# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

# TODO: 12 factor app
import collections.abc
import configparser
import sys
import typing


KT = str
VT = typing.Any


class SysConfManager(collections.abc.MutableMapping):
    """A defaultdict with some hooks to read and write values."""

    def __init__(self, conf_file: typing.TextIO):
        self._inner_data = collections.defaultdict(str)

        # load config file
        section = 'DEFAULT'
        config = configparser.SafeConfigParser()
        config.read_file(conf_file)
        for k, v in config.items(section=section):
            self[k] = v.strip('"')

    def _get_hook(self, action: str, key: str):
        """"""
        attr = getattr(
            self, '_hook_{}_{}'.format(action, key.replace('.', '_')), None)
        return attr if callable(attr) else None

    def __setitem__(self, k: KT, v: VT) -> None:
        """Call hook (if any) and replace the value before setting it."""
        handler: typing.Callable[[KT, VT], VT] = self._get_hook("set", k)
        newv = handler(k, v) if handler is not None else v
        return self._inner_data.__setitem__(k, newv)

    def __delitem__(self, k: KT) -> None:
        return self._inner_data.__delitem__(k)

    def __getitem__(self, k: KT) -> VT:
        return self._inner_data.__getitem__(k)

    def __len__(self) -> int:
        return len(self._inner_data)

    def __iter__(self) -> typing.Iterator[KT]:
        return iter(self._inner_data)

    @staticmethod
    def _set_filename_helper(k: KT, v: VT) -> VT:
        """Replace the filename string with file object."""
        if v == 'stdin':
            return sys.stdin
        return open(v)

    @staticmethod
    def _set_boolean_helper(k: KT, v: VT) -> VT:
        if v in ['true', 'True', 'yes', '1']:
            return True
        elif v in ['false', 'False', 'no', '0']:
            return False
        raise ValueError("invalid boolean value in config %s: %s" % (k, v))

    @staticmethod
    def _hook_set_repl_read_infile(k: KT, v: VT) -> VT:
        return SysConfManager._set_filename_helper(k, v)

    @staticmethod
    def _hook_set_schema_read_infile(k: KT, v: VT) -> VT:
        return SysConfManager._set_filename_helper(k, v)

    @staticmethod
    def _hook_set_general_debug(k: KT, v: VT) -> VT:
        return SysConfManager._set_boolean_helper(k, v)
