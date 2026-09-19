from py2mlog.mlog.instruction import MlogItem, Instruction, Label
from py2mlog.mlog.mlog_expressions import MlogVar


class Emitter:
    def __init__(self) -> None:
        self.instructions: list[MlogItem] = []

        self._tmp_counter = 0
        self._label_counter = 0

    def new_tmp(self) -> MlogVar:
        tmp = MlogVar(f"__p2m_tmp{self._tmp_counter}")
        self._tmp_counter += 1
        return tmp

    def new_label(self) -> Label:
        label = Label(f"__p2m_label{self._label_counter}")
        self._label_counter += 1
        return label

    def emit_instruction(self, instr: Instruction) -> bool:
        """Returns whether given instruction is valid. (WIP)"""
        self.instructions.append(instr)
        # TODO: instruction validation
        return True

    def emit_label(self, label: Label) -> bool:
        """Returns whether given label is valid."""
        is_valid = True
        try:
            # TODO: align validity checking with mindustry/arc parseDouble validity
            float(label.name)
            is_valid = False
        except ValueError:
            pass

        if is_valid:
            self.instructions.append(label)

        return is_valid
