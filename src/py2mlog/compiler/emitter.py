from py2mlog.mlog.instruction import MlogItem, Instruction, Label
from py2mlog.mlog.mlog_expressions import MlogVar, LabelRef

from .error import CompilerError, CompilerErrorType


class Emitter:
    def __init__(self) -> None:
        self.instructions: list[MlogItem] = []

        self._tmp_counter = 0
        self._label_counter = 0

    def new_tmp(self) -> MlogVar:
        tmp = MlogVar(f"__p2m_tmp{self._tmp_counter}")
        self._tmp_counter += 1
        return tmp

    def new_label(self) -> tuple[Label, LabelRef]:
        label = Label(f"__p2m_label{self._label_counter}")
        label_ref = LabelRef(label.name)

        self._label_counter += 1

        return (label, label_ref)

    def emit_instruction(self, instr: Instruction) -> None:
        """Raises an error if given instruction is invalid. (WIP)"""
        if self._check_instruction_validity(instr):
            self.instructions.append(instr)
        else:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Attempted to create invalid mlog instruction:\n{instr!r}",
            )

    def _check_instruction_validity(self, instr: Instruction) -> bool:
        # TODO: instruction validation
        return True

    def emit_label(self, label: Label) -> None:
        """Raises an error if given label is invalid."""
        if self._check_label_validity(label):
            self.instructions.append(label)
        else:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Attempted to emit invalid label: {label!r}",
            )

    def _check_label_validity(self, label: Label) -> bool:
        # TODO: align validity checking with mindustry/arc parseDouble validity
        try:
            float(label.name)
            return False
        except ValueError:
            return True
