from collections.abc import Iterable
from dataclasses import dataclass

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.compiler.mimex_utils import MIMEX_DATA_DIR, select_col
from py2mlog.compiler.names import PREFIX_LABEL, PREFIX_LOOP_ITER, PREFIX_TMP
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mimex_arg_types import (
    MIMEX_SELECTABLE_PARAM_ARG_TYPE_MAP,
    MIMEX_SUBOP_ARG_TYPE_MAP,
    MIMEX_VAR_ARG_NAMES,
)
from py2mlog.mlog.mlog_expressions import LabelRef, MlogNumberLiteral, MlogVar
from py2mlog.mlog.selectable_params import (
    GetblockSelectableParam,
    SelectableParam,
)
from py2mlog.mlog.suboperations import (
    SUBOPERATION_MAP,
    EffectSuboperation,
    SetBlockSuboperation,
    Suboperation,
)


@dataclass(frozen=True)
class InstrArgShape:
    subop: type[Suboperation] | None
    sel_params: tuple[type[SelectableParam], ...]
    var_arg_count: int


_INSTRUCTION_DATA = (MIMEX_DATA_DIR / "mimex-logic-statements.txt").read_text(
    encoding="utf-8"
)


def _get_instr_arg_shapes() -> dict[str, InstrArgShape]:
    instr_arg_shapes: dict[str, InstrArgShape] = {}
    for opcode, arg_types in zip(
        select_col(_INSTRUCTION_DATA, "opcode"),
        select_col(_INSTRUCTION_DATA, "argumentTypes"),
        strict=True,
    ):
        subop = None
        sel_params: list[type[SelectableParam]] = []
        var_arg_count = 0
        for arg_type in arg_types.split():
            if arg_type in MIMEX_VAR_ARG_NAMES:
                var_arg_count += 1
                continue

            sel_param = MIMEX_SELECTABLE_PARAM_ARG_TYPE_MAP.get(arg_type)
            curr_subop = MIMEX_SUBOP_ARG_TYPE_MAP.get(arg_type)

            # more special cases
            if arg_type == "TileLayer":
                if opcode == InstructionType.GET_BLOCK.value:
                    sel_param = GetblockSelectableParam
                elif opcode == InstructionType.SET_BLOCK.value:
                    curr_subop = SetBlockSuboperation

            if sel_param is not None:
                sel_params.append(sel_param)
                continue

            if curr_subop is not None:
                if subop is None:
                    expected_subop = SUBOPERATION_MAP[InstructionType(opcode)]
                    if (
                        expected_subop is not curr_subop
                        and expected_subop not in curr_subop
                    ):
                        raise CompilerError(
                            CompilerErrorType.INTERNAL,
                            None,
                            err="Mismatch between SUBOPERATION_MAP and mimex "
                            f"'{expected_subop}' and '{curr_subop}'",
                        )

                    subop = expected_subop

                    continue

                raise CompilerError(
                    CompilerErrorType.INTERNAL,
                    None,
                    err=f"Multiple suboperations when parsing mimex argumentTypes '{arg_types}'",
                )

            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Unknown arg type '{arg_type}' when parsing mimex argumentTypes",
            )

        instr_arg_shapes[opcode] = InstrArgShape(
            subop, tuple(sel_params), var_arg_count
        )

    # manually fixing it ig ¯\_(ツ)_/¯
    effect_instr_arg_shape = instr_arg_shapes[InstructionType.EFFECT.value]
    instr_arg_shapes[InstructionType.EFFECT.value] = InstrArgShape(
        EffectSuboperation,
        effect_instr_arg_shape.sel_params,
        effect_instr_arg_shape.var_arg_count - 1,
    )

    return instr_arg_shapes


INSTRUCTION_ARG_SHAPES = _get_instr_arg_shapes()


class Emitter:
    def __init__(self) -> None:
        self.instructions: list[MlogItem] = []

        self._tmp_counter = 0
        self._label_counter = 0
        self._loop_iter_counter = 0

    def new_tmp(self) -> MlogVar:
        tmp = MlogVar(f"{PREFIX_TMP}{self._tmp_counter}")
        self._tmp_counter += 1
        return tmp

    def new_label(self) -> tuple[Label, LabelRef]:
        label = Label(f"{PREFIX_LABEL}{self._label_counter}")
        label_ref = LabelRef(label.name)

        self._label_counter += 1

        return (label, label_ref)

    def new_loop_iter(self) -> MlogVar:
        loop_iter = MlogVar(f"{PREFIX_LOOP_ITER}{self._loop_iter_counter}")
        self._loop_iter_counter += 1
        return loop_iter

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
                err=f"Attempted to create invalid mlog instruction:\n'{instr!r}'\n"
                "False positives may happen; if you think this is one, "
                "you can file a bug report at "
                "https://github.com/FranticToaster1024/py2mlog/issues",
            )

    def _check_instruction_validity(self, instr: Instruction) -> bool:
        # this isn't fully rigourous but should catch most things
        # may have a few false positives here and there though

        if (
            instr.type is InstructionType.JUMP
            and instr.args
            and isinstance(instr.args[0], MlogNumberLiteral)
            and isinstance(instr.args[0].value, float)
        ):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err="Attempted to emit jump instruction with float lineno: "
                f"'{instr!r}'",
            )

        # TODO: add early return for false positives

        expected_arg_shape = INSTRUCTION_ARG_SHAPES.get(instr.type.value)
        if expected_arg_shape is None:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Instruction of type '{instr.type.name}' not found in mimex data",
            )

        if expected_arg_shape.subop is None:
            if instr.suboperation is not None:
                return False
        elif not isinstance(instr.suboperation, expected_arg_shape.subop):
            return False

        if instr.suboperation is None:
            if len(instr.selectable_args) != len(expected_arg_shape.sel_params):
                return False
            if not all(
                isinstance(sel_param, expected_sel_param)
                for sel_param, expected_sel_param in zip(
                    instr.selectable_args,
                    expected_arg_shape.sel_params,
                    strict=True,
                )
            ):
                return False
        elif len(instr.selectable_args) > len(expected_arg_shape.sel_params):
            return False

        var_arg_count = len(instr.args)

        # TODO: maybe move this to another function or use some kinda mapping?
        # for now its just uradar though
        if instr.type == InstructionType.UNIT_RADAR:
            var_arg_count += 1

        if instr.suboperation is None:
            return var_arg_count == expected_arg_shape.var_arg_count

        return var_arg_count <= expected_arg_shape.var_arg_count

    def emit_label(self, label: Label) -> None:
        """Raises an error if given label is invalid."""
        if self._check_label_validity(label):
            self.instructions.append(label)
        else:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Attempted to emit invalid label: '{label!r}'",
            )

    def _check_label_validity(self, label: Label) -> bool:
        # TODO: align validity checking with mindustry/arc parseDouble validity
        try:
            float(label.name)
        except ValueError:
            return True
        else:
            return False

    def resolve_absolute_jumps(self) -> None:
        label_insert_indexes: dict[int, tuple[Label, LabelRef]] = {}

        for i, instr in enumerate(self.instructions):
            if (
                not isinstance(instr, Instruction)
                or instr.type is not InstructionType.JUMP
                or not isinstance(instr.args[0], MlogNumberLiteral)
            ):
                continue

            tgt_lineno = int(instr.args[0].value)
            tgt_label = label_insert_indexes.get(tgt_lineno)
            if tgt_label is None:
                tgt_label = self.new_label()
                label_insert_indexes[tgt_lineno] = tgt_label

            self.instructions[i] = Instruction(
                InstructionType.JUMP,
                instr.suboperation,
                instr.selectable_args,
                (tgt_label[1], *instr.args[1:]),
            )

        new_instructions: list[MlogItem] = []
        for i, instr in enumerate(self.instructions):
            label_to_insert = label_insert_indexes.get(i)
            if label_to_insert is not None:
                new_instructions.append(label_to_insert[0])

            new_instructions.append(instr)

        self.instructions = new_instructions
