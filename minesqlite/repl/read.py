# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing

from minesqlite.minesqlite import MineSQLite


def read(instance: MineSQLite) -> typing.Iterator[str]:
    """Prints prompts, reads the input, then yields each lines of them."""
    infile: typing.IO = instance.sysconf['repl.read.infile']
    prompt: str = instance.sysconf['repl.read.prompt']
    print(prompt, end='', flush=True)
    try:
        for line in infile:
            line = line.strip()
            if not line:
                print(prompt, end='', flush=True)
                continue
            yield line
            print(prompt, end='', flush=True)
    except KeyboardInterrupt:
        pass

    print('Goodbye!')
