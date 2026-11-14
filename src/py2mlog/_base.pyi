__all__ = [
    "Block",
    "Building",
    "Content",
    "Controllable",
    "Item",
    "Liquid",
    "Senseable",
    "_Color",
    "_Unit",
]

from abc import ABC
from typing import Any

from py2mlog._types import Content, _Color  # pyright: ignore[reportPrivateUsage]

# there is an actual Color 'builtin' to be generated later

class Item(Content): ...
class Liquid(Content): ...

class Block(Content):
    """
    Includes terrain blocks, not just building types.
    """

class Senseable(ABC):
    # TODO: attributes or something
    ...

class _Unit(Senseable): ...

class Controllable(ABC):
    def enabled(self, enabled: bool | int) -> None: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...
    def shoot(self, x: float, y: float, shoot: bool | int = True) -> None: ...
    def ceasefire(self) -> None: ...
    def shootp(self, unit: _Unit, shoot: bool | int = True) -> None: ...
    def color(self, color: _Color) -> None: ...
    def config(self, config: Any) -> None: ...

class Building(Senseable, Controllable): ...
