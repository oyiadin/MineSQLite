# coding=utf-8
# Author: @hsiaoxychen 2022/06/04

from minesqlite.minesqlite import MineSQLite
from minesqlite.repl.print_ import print_
from minesqlite.repl.read import read
from minesqlite.repl.split_words import split_words
from minesqlite.repl.analyze import analyze, get_argparsers


def loop(instance: MineSQLite):
    """Implements the REPL steps.

    * READ the input (and prints prompts)
    * SPLIT the input into words with careful handling of quotes
    * ANALYZE the statements according to the registered format
    * EVAL the command and collects the results
    * PRINT the command results
    """
    argparser = get_argparsers(instance)

    for line in read(instance):
        try:
            words = split_words(line)
            handler, arguments = analyze(argparser, words)
            rows = handler(instance, arguments)
            print_(rows)
        except Exception as exc:
            print("{}: {}".format(exc.__class__.__name__, str(exc)))
        print()
