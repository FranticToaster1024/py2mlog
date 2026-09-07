"""
Enums for selectable parameters. e.g.
In `radar player ally any distance turret1 1 result`,
`player`, `ally`, and `any` are selectable parameters.
In `ulocate building core true @copper outx outy found building`,
`building` and `core` are selectable parameters.
"""

from enum import Enum

from .instruction_types import InstructionType


class SelectableParam:
    pass


# TODO: add selectable param enums
class RadarSelectableParam(SelectableParam, Enum):
    pass


# TODO: complete selectable param map
selectable_param_map = {
    InstructionType.OPERATION: RadarSelectableParam,
    "placeholdercuzblackhatesme": None,
}
