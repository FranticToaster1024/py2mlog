"""
Internals: compiler, mlog, mimex_data, intrinsics, optimizer,
scripts, api, __main__, _gen, _types.
Avoid importing them for regular use.
"""

from collections.abc import Callable
from typing import LiteralString

from py2mlog._gen import *  # noqa: F403

def inline[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    """
    Can only be used as decorator.
    """

def mlog_raw(src: LiteralString, /) -> None:
    """
    Emit raw mlog. Use a raw string so that escape sequences work properly.
    """
