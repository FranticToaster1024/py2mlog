"""
Enums for selectable parameters. e.g.
In `radar player ally any distance turret1 1 result`,
`player`, `ally`, `any` and `distance` are selectable parameters.
In `lookup item result 0`,
`item` is a selectable parameter.
"""

from enum import Enum


class SelectableParam:
    pass


# class names are either based on instruction name or name in mimex repo


class RadarTargetSelectableParam(SelectableParam, Enum):
    ANY = "any"
    ENEMY = "enemy"
    ALLY = "ally"
    PLAYER = "player"
    ATTACKER = "attacker"
    FLYING = "flying"
    BOSS = "boss"
    GROUND = "ground"


class RadarSortSelectableParam(SelectableParam, Enum):
    DISTANCE = "distance"
    HEALTH = "health"
    SHIELD = "shield"
    ARMOR = "armor"
    MAX_HEALTH = "maxHealth"


class LookupSelectableParam(SelectableParam, Enum):
    BLOCK = "block"
    UNIT = "unit"
    ITEM = "item"
    LIQUID = "liquid"
    TEAM = "team"


class UnitLocateBuildingSelectableParam(SelectableParam, Enum):
    CORE = "core"
    STORAGE = "storage"
    GENERATOR = "generator"
    TURRET = "turret"
    FACTORY = "factory"
    REPAIR = "repair"
    BATTERY = "battery"
    REACTOR = "reactor"
    DRILL = "drill"
    SHIELD = "shield"


class QuerySelectableParam(SelectableParam, Enum):
    UNIT = "unit"
    BUILDING = "building"


class TileLayerSelectableParam(SelectableParam, Enum):
    FLOOR = "floor"
    ORE = "ore"
    BLOCK = "block"
    BUILDING = "building"


# it is treated as a regular arg in-game
# avoid hardcoding to support data-patches (?)
# class ApplyStatusSelectableParam(SelectableParam, Enum):
#    pass


class MakeMarkerSelectableParam(SelectableParam, Enum):
    SHAPE_TEXT = "shapeText"
    POINT = "point"
    SHAPE = "shape"
    TEXT = "text"
    LINE = "line"
    TEXTURE = "texture"
    QUAD = "quad"
