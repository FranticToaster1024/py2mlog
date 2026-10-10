from dataclasses import dataclass
from typing import TypeAlias

from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import MlogExpr
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
    args: tuple[MlogExpr, ...]


@dataclass(frozen=True)
class Label:
    name: str


MlogItem: TypeAlias = Instruction | Label
