# coding=utf-8
# Author: @hsiaoxychen
from minesqlite.minesqlite import MineSQLite
from minesqlite.repl import repl_loop

if __name__ == '__main__':
    instance = MineSQLite(
        sysconf_kwargs={'conf_file': open('etc/config.ini')})
    repl_loop(instance)
