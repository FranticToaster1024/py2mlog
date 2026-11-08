from dataclasses import dataclass

from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import MlogArg
from py2mlog.mlog.selectable_params import SelectableParam
from py2mlog.mlog.suboperations import Suboperation


@dataclass(frozen=True)
class Instruction:
    """
    Represent a single mlog instruction (including arguments).
    """

    type: InstructionType
    suboperation: Suboperation | None
    selectable_args: tuple[SelectableParam, ...]
    args: tuple[MlogArg, ...]


@dataclass(frozen=True)
class Label:
    name: str


type MlogItem = Instruction | Label
