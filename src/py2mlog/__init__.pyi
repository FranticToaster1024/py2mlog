"""
Internal modules: compiler, mlog, mimex_data, intrinsics.
Avoid importing them for regular use.
"""

from typing import Self

from py2mlog._gen import *  # noqa: F403

# i dunno maybe we can even generate these from the maps too instead
# ima just manually write these for now
# otherwise i get red squiggly lines every time i write something

def sleep(seconds: float) -> None: ...

wait = sleep

# is this how you do it?
class Color(float):
    """
    Represents an Mlog color literal, e.g. %ffffff.
    Subclass of 'float', so arithmetic is supported.
    """
    def __new__(cls, x: str | int) -> Self: ...

# TODO: generate stuff like Env.* from mimex because i am NOT writing that manually
# because im feeling lazy maybe also generate Screen.* and similar stuff from the maps
