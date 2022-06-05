# coding=utf-8
# Author: @hsiaoxychen 2022/06/04
import typing
from pprint import pprint


def print_(rows: typing.Iterable[dict]):
    for row in rows:
        pprint(row)
