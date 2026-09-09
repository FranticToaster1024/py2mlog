from dataclasses import dataclass

from .instruction_types import InstructionType
from .mlog_identifiers import MlogIdentifier
from .suboperations import Suboperation
from .selectable_params import SelectableParam


@dataclass(frozen=True)
class Instruction:
    """
    Represent a single mlog instruction (including arguments).
    """

    type: InstructionType
    suboperation: Suboperation
    selectable_args: tuple[SelectableParam, ...]
    args: tuple[MlogIdentifier, ...]
