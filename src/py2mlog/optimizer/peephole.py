import logging
from collections import deque

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.suboperations import (
    NEGATED_COND_OP_SUBOP_MAP,
    ConditionOpSuboperation,
)
from py2mlog.optimizer.utils import get_jump_target_name

logger = logging.getLogger(__name__)

type JumpLabelMap = dict[str, list[Instruction]]


def peephole(instrs: tuple[MlogItem, ...], /) -> tuple[MlogItem, ...]:
    jump_label_map = _generate_jump_label_map(instrs)

    instrs = _remove_useless_end_and_wrap_labels(instrs)
    return _simplify_adjacent_jumps(instrs, jump_label_map=jump_label_map)


def _remove_useless_end_and_wrap_labels(
    instrs: tuple[MlogItem, ...],
) -> tuple[MlogItem, ...]:
    new_instrs = deque(instrs)

    while new_instrs:
        last_instr = new_instrs[-1]

        if (
            isinstance(last_instr, Instruction)
            and last_instr.type == InstructionType.END
        ):
            new_instrs.pop()

        elif isinstance(last_instr, Label):
            # label on last line doesn't wrap properly;
            # see https://github.com/Anuken/Mindustry-Suggestions/issues/6629
            new_instrs.appendleft(new_instrs.pop())

        else:
            break

    return tuple(new_instrs)


def _simplify_adjacent_jumps(
    instrs: tuple[MlogItem, ...], /, jump_label_map: JumpLabelMap
) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem] = []

    # build new_instrs
    i = 0
    while i < len(instrs):
        instr = instrs[i]

        # skip useless label
        if isinstance(instr, Label) and not jump_label_map[instr.name]:
            i += 1
            continue

        if (
            isinstance(instr, Instruction)
            and instr.type is InstructionType.JUMP
        ):
            # mostly to please the type checker
            if not isinstance(instr.suboperation, ConditionOpSuboperation):
                raise CompilerError(
                    CompilerErrorType.INTERNAL,
                    None,
                    err=f"Jump instruction with non-{ConditionOpSuboperation.__name__} "
                    f"suboperation: {instr!r}",
                )

            label_name = get_jump_target_name(instr)

            next_i = i + 1
            if next_i < len(instrs):
                next_instr = instrs[next_i]

                # check for
                # jump label ...  # <-- skip
                # label:  # <-- keep in case other jumps point here
                if (
                    isinstance(next_instr, Label)
                    and next_instr.name == label_name
                ):
                    i = next_i
                    continue

                # check for
                # jump l1 ...  # <-- negate this condition and jump to l2 instead
                # jump l2 always  # <-- skip
                # l1:  # <-- keep
                negated_cond_op_subop = NEGATED_COND_OP_SUBOP_MAP.get(
                    instr.suboperation
                )
                if (
                    negated_cond_op_subop is not None
                    and isinstance(next_instr, Instruction)
                    and next_instr.type is InstructionType.JUMP
                    and next_instr.suboperation
                    == ConditionOpSuboperation.ALWAYS
                ):
                    # wow nice naming convention
                    next_next_i = next_i + 1
                    if next_next_i < len(instrs):
                        next_next_instr = instrs[next_next_i]
                        if (
                            isinstance(next_next_instr, Label)
                            and next_next_instr.name == label_name
                        ):
                            new_instrs.append(
                                Instruction(
                                    InstructionType.JUMP,
                                    negated_cond_op_subop,
                                    (),
                                    (next_instr.args[0], *instr.args[1:]),
                                )
                            )
                            i = next_next_i
                            continue

        new_instrs.append(instr)
        i += 1

    return tuple(new_instrs)


def _generate_jump_label_map(
    instrs: tuple[MlogItem, ...],
) -> JumpLabelMap:
    jump_label_map: JumpLabelMap = {}

    # fill labels
    for instr in instrs:
        if isinstance(instr, Label):
            if instr.name in jump_label_map:
                raise CompilerError(
                    CompilerErrorType.INTERNAL,
                    None,
                    err=f"Duplicate labels in generated mlog with name '{instr.name}'.",
                )

            jump_label_map[instr.name] = []

    # fill jumps
    for instr in instrs:
        if (
            isinstance(instr, Instruction)
            and instr.type == InstructionType.JUMP
        ):
            label_name = get_jump_target_name(instr)

            jump_label_map_entry = jump_label_map.get(label_name)
            if jump_label_map_entry is None:
                logger.warning(
                    "Jump to '%s' with no matching label.", label_name
                )
            else:
                jump_label_map_entry.append(instr)

    return jump_label_map
