# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
from minesqlite.minesqlite import MineSQLite
from minesqlite.repl.print_ import print_
from minesqlite.repl.read import read
from minesqlite.repl.split import split
from minesqlite.repl.eval import eval_


def loop(instance: MineSQLite):
    for line in read(instance):
        try:
            splitted = split(line)
            rows = eval_(instance, splitted)
            print_(rows)
        except Exception as exc:
            print("{}: {}".format(exc.__class__.__name__, str(exc)))
        print()
