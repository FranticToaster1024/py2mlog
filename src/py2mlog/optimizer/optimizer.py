import logging
from collections import deque
from time import perf_counter

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import LabelRef
from py2mlog.mlog.suboperations import (
    NEGATED_COND_OP_SUBOP_MAP,
    ConditionOpSuboperation,
)

logger = logging.getLogger(__name__)


_DEFAULT_ITERATIONS = 5


type JumpLabelMap = dict[str, list[Instruction]]


# TODO: maybe special classes to avoid recomputing metadata?
# optimize the optimizer, heh
def optimize(
    _instructions: list[MlogItem], /, *, iterations: int = _DEFAULT_ITERATIONS
) -> list[MlogItem]:
    st_time = perf_counter()

    instrs = tuple(_instructions)

    start_len = len(instrs)
    last_len = start_len
    for i in range(iterations):
        jump_label_map = _generate_jump_label_map(instrs)

        instrs = _optimize_jumps(instrs, jump_label_map=jump_label_map)
        instrs = _dead_code_elimination(instrs)
        instrs = _remove_useless_end(instrs)

        if len(instrs) == last_len:
            logger.debug(
                "Ended optimizer after %s iterations "
                "(no instructions removed in last iteration).",
                i + 1,
            )

        last_len = len(instrs)

    logger.debug(
        "Optimizer finished in %ss. Removed %s instructions.",
        round(perf_counter() - st_time, 2),
        start_len - last_len,
    )
    return list(instrs)


def _optimize_jumps(
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

            label_name = _get_jump_target_name(instr)

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


def _dead_code_elimination(
    instrs: tuple[MlogItem, ...], /
) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem | None] = list(instrs)

    curr_labels: set[str] = set()
    # jump label always
    # deadcode
    # deadcode
    # otherlabel:
    # not deadcode
    # label:
    earliest_open_jump_always_lineno: int | None = None

    for i, instr in enumerate(instrs):
        if isinstance(instr, Label):
            curr_labels.add(instr.name)

            if earliest_open_jump_always_lineno is not None:
                for j in range(earliest_open_jump_always_lineno + 1, i):
                    new_instrs[j] = None

                earliest_open_jump_always_lineno = None

        elif instr.type == InstructionType.JUMP:
            label_name = _get_jump_target_name(instr)

            if (
                label_name not in curr_labels
                and instr.suboperation == ConditionOpSuboperation.ALWAYS
                and earliest_open_jump_always_lineno is None
                and not instr.is_func_call_jump
            ):
                earliest_open_jump_always_lineno = i

    return tuple(e for e in new_instrs if e is not None)


def _remove_useless_end(instrs: tuple[MlogItem, ...]) -> tuple[MlogItem, ...]:
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


# TODO: constant folding


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
            label_name = _get_jump_target_name(instr)

            jump_label_map_entry = jump_label_map.get(label_name)
            if jump_label_map_entry is None:
                logger.warning(
                    "Jump to '%s' with no matching label.", label_name
                )
            else:
                jump_label_map_entry.append(instr)

    return jump_label_map


def _get_jump_target_name(instr: Instruction) -> str:
    if instr.type != InstructionType.JUMP:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err="Called '_get_jump_target_name' with non-jump instruction.",
        )

    if not isinstance(instr.args[0], LabelRef):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Unlabelled jump '{instr}'. "
            f"First arg not instance of '{LabelRef.__name__}'",
        )

    return instr.args[0].name
