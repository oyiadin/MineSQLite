# coding=utf-8
# Author: @hsiaoxychen
from minesqlite.repl.loop import loop as repl_loop
from minesqlite.sysconf.manager import SysConfManager

if __name__ == '__main__':
    sysconf = SysConfManager()
    repl_loop(sysconf)
