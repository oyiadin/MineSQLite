# coding=utf-8
# Author: @hsiaoxychen
from contextlib import nullcontext

import pytest

__all__ = ['raises', 'no_raise']

raises = pytest.raises
no_raise = nullcontext
