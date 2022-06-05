# coding=utf-8
# Author: @hsiaoxychen
from minesqlite.minesqlite import MineSQLite
from minesqlite.repl.loop import loop as repl_loop

if __name__ == '__main__':
    instance = MineSQLite()
    repl_loop(instance)
