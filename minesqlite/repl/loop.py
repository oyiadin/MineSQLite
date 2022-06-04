# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

from minesqlite.repl.read import read
from minesqlite.repl.split import split
from minesqlite.repl.eval import eval_
from minesqlite.sysconf.manager import SysConfManager


def loop(sysconf: SysConfManager):
    while True:
        for line in read(sysconf):
            splitted = split(line)
            results = eval_(splitted)
