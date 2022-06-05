# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
from minesqlite.minesqlite import MineSQLite
from minesqlite.repl.read import read
from minesqlite.repl.split import split
from minesqlite.repl.eval import eval_


def loop(instance: MineSQLite):
    while True:
        for line in read(instance):
            try:
                splitted = split(line)
                results = eval_(instance, splitted)
            except Exception as exc:
                print("{}: {}".format(exc.__class__.__name__, str(exc)))
