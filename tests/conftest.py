# coding=utf-8
# Author: @hsiaoxychen
import collections
import os
import sys
import typing
from unittest import mock
import pytest

from minesqlite.data.base import CursorABC, DataManagerABC

sys.path.append(os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def sysconf():
    return collections.defaultdict(str)


@pytest.fixture(scope='session')
def schema():
    return mock.MagicMock()


@pytest.fixture(scope='session')
def instance(sysconf, schema):
    m = mock.MagicMock()
    m.sysconf = sysconf
    m.schema = schema
    return m
