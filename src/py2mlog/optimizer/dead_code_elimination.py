from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.suboperations import ConditionOpSuboperation
from py2mlog.optimizer.utils import get_jump_target_name


def dead_code_elimination(
    instrs: tuple[MlogItem, ...], /
) -> tuple[MlogItem, ...]:
    instrs = _unreachable_code_elimination(instrs)
    return _remove_unreachable_code_after_jump_always(instrs)


def _unreachable_code_elimination(
    instrs: tuple[MlogItem, ...], /
) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem] = []

    i = 0
    while i < len(instrs):
        instr = instrs[i]
        if isinstance(instr, Instruction) and instr.type in (
            InstructionType.END,
            InstructionType.STOP,
        ):
            new_instrs.append(instr)
            i += 1
            while i < len(instrs) and not isinstance(instrs[i], Label):
                i += 1
            continue

        new_instrs.append(instr)
        i += 1

    return tuple(new_instrs)


def _remove_unreachable_code_after_jump_always(
    instrs: tuple[MlogItem, ...],
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
            label_name = get_jump_target_name(instr)

            if (
                label_name not in curr_labels
                and instr.suboperation == ConditionOpSuboperation.ALWAYS
                and earliest_open_jump_always_lineno is None
                and not instr.is_func_call_jump
            ):
                earliest_open_jump_always_lineno = i

    return tuple(e for e in new_instrs if e is not None)
