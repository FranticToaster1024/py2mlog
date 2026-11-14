"""
Internals: compiler, mlog, mimex_data, intrinsics, optimizer,
scripts, api, __main__, _base, _gen.
Avoid importing them for regular use.
"""

from collections.abc import Callable

from py2mlog._base import *  # noqa: F403
from py2mlog._gen import *  # noqa: F403

def inline[**P, R](f: Callable[P, R]) -> Callable[P, R]: ...
