from enum import Enum, auto
from typing import TypeAlias

from .instruction_types import InstructionType
from .suboperations import *


class ParamType(Enum):
    VAR = auto()
    SELECTABLE = auto()
    SUBOPERATION = auto()
    FILLER = auto()


_arg_order: TypeAlias = tuple[ParamType, ...]
# default arg order:
# [*suboperation], [*selectable], *var
PARAM_MAP: dict[
    InstructionType,
    _arg_order | dict[Suboperation | tuple[Suboperation, ...], _arg_order],
] = {
    InstructionType.SELECT: {
        ConditionOpSuboperation.ALWAYS: (
            ParamType.VAR,
            ParamType.SUBOPERATION,
            ParamType.FILLER,
            ParamType.FILLER,
            ParamType.VAR,
        ),
        (
            ConditionOpSuboperation.EQUAL,
            ConditionOpSuboperation.NOT_EQUAL,
            ConditionOpSuboperation.LESS_THAN,
            ConditionOpSuboperation.LESS_THAN_OR_EQ,
            ConditionOpSuboperation.GREATER_THAN,
            ConditionOpSuboperation.GREATER_THAN_OR_EQ,
            ConditionOpSuboperation.STRICT_EQUAL,
        ): (
            ParamType.VAR,
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
        ),
    },
    InstructionType.JUMP: {
        ConditionOpSuboperation.ALWAYS: (
            ParamType.VAR,
            ParamType.SUBOPERATION,
        ),
        (
            ConditionOpSuboperation.EQUAL,
            ConditionOpSuboperation.NOT_EQUAL,
            ConditionOpSuboperation.LESS_THAN,
            ConditionOpSuboperation.LESS_THAN_OR_EQ,
            ConditionOpSuboperation.GREATER_THAN,
            ConditionOpSuboperation.GREATER_THAN_OR_EQ,
            ConditionOpSuboperation.STRICT_EQUAL,
        ): (
            ParamType.VAR,
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
        ),
    },
    InstructionType.UNIT_RADAR: (
        ParamType.SELECTABLE,
        ParamType.SELECTABLE,
        ParamType.SELECTABLE,
        ParamType.SELECTABLE,
        ParamType.FILLER,  # ?????
        ParamType.VAR,
        ParamType.VAR,
    ),
    InstructionType.UNIT_LOCATE: {
        UnitLocateSuboperation.BUILDING: (
            ParamType.SUBOPERATION,
            ParamType.SELECTABLE,
            ParamType.VAR,
            ParamType.FILLER,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
        ),
        UnitLocateSuboperation.ORE: (
            ParamType.SUBOPERATION,
            ParamType.FILLER,
            ParamType.FILLER,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
        ),
        (UnitLocateSuboperation.SPAWN, UnitLocateSuboperation.DAMAGED): (
            ParamType.SUBOPERATION,
            ParamType.FILLER,
            ParamType.FILLER,
            ParamType.FILLER,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            # NOTE: building attribute, ulocate spawn has this in-game for some reason
            # i suspect it is a bug, but i'll keep it as-is for now to mirror the game's syntax
            ParamType.VAR,
        ),
    },
    InstructionType.SET_RULE: {
        SetRuleSuboperation.MAP_AREA: (
            ParamType.SUBOPERATION,
            ParamType.FILLER,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
        ),
    },
    InstructionType.FLUSH_MESSAGE: {
        (FlushMessageSuboperation.NOTIFY, FlushMessageSuboperation.MISSION): (
            ParamType.SUBOPERATION,
            ParamType.FILLER,
            ParamType.VAR,
        ),
    },
    InstructionType.EFFECT: {
        (
            EffectSuboperation.BLOCK_FALL,
            EffectSuboperation.SMOKE_CLOUD,
            EffectSuboperation.VAPOR,
            EffectSuboperation.HIT,
            EffectSuboperation.HIT_SQUARE,
            EffectSuboperation.SPARK,
            EffectSuboperation.SPARK_BIG,
            EffectSuboperation.SPARK_SHOOT,
            EffectSuboperation.DRILL,
            EffectSuboperation.DRILL_BIG,
        ): (
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.FILLER,
            ParamType.VAR,
        ),
    },
    InstructionType.FETCH: {
        (FetchSuboperation.UNIT_COUNT, FetchSuboperation.BUILD_COUNT): (
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.FILLER,
            ParamType.VAR,
        ),
    },
    InstructionType.PLAY_SOUND: {
        PlaySoundSuboperation.GLOBAL: (
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.FILLER,
            ParamType.FILLER,
            ParamType.VAR,
        ),
        PlaySoundSuboperation.POSITIONAL: (
            ParamType.SUBOPERATION,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.FILLER,
            ParamType.VAR,
            ParamType.VAR,
            ParamType.VAR,
        ),
    },
}
