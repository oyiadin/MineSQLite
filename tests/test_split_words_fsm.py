# coding=utf-8
# Author: @hsiaoxychen
import pytest

import minesqlite.common.split_words_fsm


@pytest.mark.parametrize(['line', 'expect'], [
    ('', []),
    (' ', []),
    ('  ', []),
    ('k', ['k']),
    (' k  ', ['k']),
    ('"k"', ['k']),
    (' " k " ', [' k ']),
    ('  ab  c  ""  " "  k', ['ab', 'c', '', ' ', 'k']),
])
def test_split_words(line, expect):
    got = minesqlite.common.split_words_fsm.split_words(line)
    assert got == expect
