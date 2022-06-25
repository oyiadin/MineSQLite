# coding=utf-8
# Author: @hsiaoxychen
import collections
import os
import sys

import pytest
from pytest_mock import MockerFixture


sys.path.append(os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..')))

TEST_PK = '__test_pk'


@pytest.fixture
def sysconf():
    return collections.defaultdict(str)


@pytest.fixture
def schema(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def instance(mocker: MockerFixture, sysconf, schema):
    m = mocker.MagicMock()
    m.sysconf = sysconf
    m.schema = schema
    return m


@pytest.fixture
def mock_pk(mocker: MockerFixture, instance):
    mocker.patch(instance.schema, 'primary_key', TEST_PK)
