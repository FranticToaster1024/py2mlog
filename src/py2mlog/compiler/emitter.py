from collections.abc import Iterable

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.compiler.names import PREFIX_LABEL, PREFIX_TMP
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.mlog_expressions import LabelRef, MlogVar


class Emitter:
    def __init__(self) -> None:
        self.instructions: list[MlogItem] = []

        self._tmp_counter = 0
        self._label_counter = 0

    def new_tmp(self) -> MlogVar:
        tmp = MlogVar(f"{PREFIX_TMP}{self._tmp_counter}")
        self._tmp_counter += 1
        return tmp

    def new_label(self) -> tuple[Label, LabelRef]:
        label = Label(f"{PREFIX_LABEL}{self._label_counter}")
        label_ref = LabelRef(label.name)

        self._label_counter += 1

        return (label, label_ref)

    def emit_items(self, items: Iterable[MlogItem]) -> None:
        for item in items:
            match item:
                case Instruction():
                    self.emit_instruction(item)
                case Label():
                    self.emit_label(item)

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

    def _check_instruction_validity(self, instr: Instruction) -> bool:  # noqa: ARG002
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
        except ValueError:
            return True
        else:
            return False
