from dataclasses import dataclass

from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import MlogArg
from py2mlog.mlog.selectable_params import SelectableParam
from py2mlog.mlog.suboperations import Suboperation


@dataclass(frozen=True, slots=True)
class Instruction:
    """
    Represent a single mlog instruction (including arguments).
    """

    type: InstructionType
    suboperation: Suboperation | None
    selectable_args: tuple[SelectableParam, ...]
    args: tuple[MlogArg, ...]

    # metadata
    is_func_call_jump: bool = False


@dataclass(frozen=True, eq=False)
class Label:
    name: str


type MlogItem = Instruction | Label
