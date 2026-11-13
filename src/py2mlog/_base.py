# ruff: noqa: B024

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

# tf am i doing with all these as runtime values


# there is an actual Color 'builtin' to be generated later
class _Color(float):
    """
    Represents an Mlog color literal, e.g. %ffffff.
    Subclass of 'float', so arithmetic is supported.
    """


class Content:
    pass


class Item(Content):
    pass


class Liquid(Content):
    pass


class Block(Content):
    """
    Includes terrain blocks, not just building types.
    """


class Senseable(ABC):
    # TODO: attributes or something
    pass


class Controllable(ABC):
    # TODO: attributes or something
    pass


class _Unit(Senseable): ...


class Building(Senseable, Controllable): ...
