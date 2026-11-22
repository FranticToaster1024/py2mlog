"""
Internals: compiler, mlog, mimex_data, intrinsics, optimizer,
scripts, api, __main__, _gen, _types.
Avoid importing them for regular use.
"""

from collections.abc import Callable
from typing import Literal

from py2mlog._gen import *  # noqa: F403

def inline[**P, R](f: Callable[P, R]) -> Callable[P, R]:
    """
    (Compiler Directive)
    Can only be used as decorator.
    """

def unroll(factor: int | Literal["all"], /) -> None:
    """
    (Compiler Directive)
    Unroll the loop directly below if present, raises otherwise.
    'factor' must be a literal, not variable.
    Can only be called as standalone function call.
    """
