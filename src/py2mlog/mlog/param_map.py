from enum import Enum, auto

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.suboperations import (
    ConditionOpSuboperation,
    EffectSuboperation,
    FetchSuboperation,
    FlushMessageSuboperation,
    PlaySoundSuboperation,
    SetRuleSuboperation,
    Suboperation,
    UnitLocateSuboperation,
)


class ParamType(Enum):
    VAR = auto()
    SELECTABLE = auto()
    SUBOPERATION = auto()
    LABEL_REF = auto()
    FILLER = auto()


type _ArgOrder = tuple[ParamType, ...]
# default arg order:
# [*suboperation], [*selectable], *var
PARAM_MAP: dict[
    InstructionType,
    _ArgOrder | dict[Suboperation | tuple[Suboperation, ...], _ArgOrder],
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
            ParamType.LABEL_REF,
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
            ParamType.LABEL_REF,
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
        # i suspect this is cuz uradar just ripped code from regular radar
        ParamType.FILLER,
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


def get_param_order(
    instr_type: InstructionType, subop: Suboperation | None
) -> tuple[ParamType, ...] | None:
    instr_entry = PARAM_MAP.get(instr_type)

    if instr_entry is None:
        return None

    if not isinstance(instr_entry, dict):
        return instr_entry

    if subop is None:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err="Invalid param_map/instruction",
        )

    param_order = instr_entry.get(subop)

    if param_order is not None:
        return param_order

    for key, val in instr_entry.items():
        if isinstance(key, tuple) and subop in key:
            return val

    return None
