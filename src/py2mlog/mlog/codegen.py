from collections.abc import Iterator

from .instruction import Instruction
from .param_map import PARAM_MAP, ParamType


def _get_param_order(instr: Instruction) -> tuple[ParamType, ...] | None:
    instr_entry = PARAM_MAP.get(instr.type, None)

    if instr_entry is None:
        return None

    if not isinstance(instr_entry, dict):
        return instr_entry

    param_order = instr_entry.get(instr.suboperation, None)

    if param_order is not None:
        return param_order

    for key, val in instr_entry.items():
        if instr.suboperation in key:
            return val

    return None


def _build_arg_list(
    instr: Instruction, param_order: tuple[ParamType, ...]
) -> Iterator[str]:
    selectables = iter(instr.selectable_args)
    args = iter(instr.args)

    for param_type in param_order:
        match param_type:
            case ParamType.SUBOPERATION:
                yield instr.suboperation.value
            case ParamType.SELECTABLE:
                yield next(selectables).value
            case ParamType.VAR:
                yield str(next(args))


def generate_mlog(instructions: list[Instruction]) -> str:
    mlog: list[str] = []

    for instr in instructions:
        param_order = _get_param_order(instr)

        if param_order is not None:
            mlog.append(" ".join(_build_arg_list(instr, param_order)))

        else:
            s = " ".join(
                instr.suboperation.value,
                *(a.value for a in instr.selectable_args),
                *map(str, instr.args),
            )
            mlog.append(s)

    return "\n".join(mlog)
