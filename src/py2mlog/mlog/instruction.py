from dataclasses import dataclass
from typing import TypeAlias

from .instruction_types import InstructionType
from .mlog_expressions import MlogExpr
from .suboperations import Suboperation
from .selectable_params import SelectableParam


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
