"""
Internal modules: compiler, mlog, mimex_data, intrinsics.
Avoid importing them for regular use.
"""

from abc import ABC
from typing import Any, Self

from py2mlog._gen import *  # noqa: F403

# move this to generated stub
class Senseable(ABC):
    # TODO: attributes or something
    ...

# move this to generated stub
class Controllable(ABC):
    # TODO: attributes or something
    ...

class Building(Senseable, Controllable): ...

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

# because im feeling lazy maybe also generate Screen.* and similar stuff from the maps

class MemBuilding(Building):
    def __getitem__(self, index: int) -> Any: ...
    def __setitem__(self, index: int, value: Any) -> None: ...

class Mem:
    def __getattr__(self, name: str) -> MemBuilding: ...
    # TODO: methods
