# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing

from minesqlite.minesqlite import MineSQLite


def read(instance: MineSQLite) -> typing.Iterator[str]:
    sysconf = instance.sysconf
    infile: typing.IO = sysconf['repl.read.infile']
    prompt: str = sysconf['repl.read.prompt']
    while True:
        print(prompt, end='')
        line = infile.readline().strip()
        if not line:
            continue
        yield line
