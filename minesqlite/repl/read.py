# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing

from minesqlite.minesqlite import MineSQLite


def read(instance: MineSQLite) -> typing.Iterator[str]:
    sysconf = instance.sysconf
    infile: typing.IO = sysconf['repl.read.infile']
    prompt: str = sysconf['repl.read.prompt']
    print(prompt, end='')
    for line in infile:
        line = line.strip()
        if not line:
            print(prompt, end='')
            continue
        yield line
        print(prompt, end='')

    # TODO
    raise StopIteration
