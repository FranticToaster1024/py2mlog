from collections.abc import Iterator

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.mlog_expressions import (
    LabelRef,
    MlogArg,
    MlogBoolLiteral,
    MlogBuiltin,
    MlogColorLiteral,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.param_map import PARAM_MAP, ParamType


def _get_param_order(instr: Instruction) -> tuple[ParamType, ...] | None:
    instr_entry = PARAM_MAP.get(instr.type, None)

    if instr_entry is None:
        return None

    if not isinstance(instr_entry, dict):
        return instr_entry

    if instr.suboperation is None:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err="Invalid param_map/invalid instruction",
        )

    param_order = instr_entry.get(instr.suboperation)

    if param_order is not None:
        return param_order

    for key, val in instr_entry.items():
        if isinstance(key, tuple) and instr.suboperation in key:
            return val

    return None


def _arg_to_str(arg: MlogArg) -> str:
    match arg:
        case LabelRef(name):
            return name
        case MlogBuiltin(name):
            return "@" + name
        case MlogStringLiteral(value):
            return f'"{value}"'
        case MlogNumberLiteral(value):
            return str(value)
        case MlogBoolLiteral(value):
            return "true" if value else "false"
        case MlogNullLiteral():
            return "null"
        case MlogColorLiteral(value):
            return "%" + value
        case MlogVar(name):
            return name
        case _:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Unknown arg type {type(arg).__name__} of {arg!r}",
            )


# list of all args including suboperation & selectable params
def _build_arg_list(
    instr: Instruction, param_order: tuple[ParamType, ...]
) -> Iterator[str]:
    yield instr.type.value

    selectables = iter(instr.selectable_args)
    args = iter(instr.args)

    for param_type in param_order:
        try:
            match param_type:
                case ParamType.SUBOPERATION:
                    yield (
                        instr.suboperation.value
                        if instr.suboperation is not None
                        else ""
                    )
                case ParamType.SELECTABLE:
                    yield next(selectables).value
                case ParamType.VAR:
                    yield _arg_to_str(next(args))
                case ParamType.FILLER:
                    yield "_"

        except StopIteration:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Instruction '{instr!r}' did not match PARAM_MAP: missing '{param_type}'",
            ) from None


def _generate_mlog_from_instruction(instr: Instruction) -> str:
    param_order = _get_param_order(instr)

    if param_order is not None:
        return " ".join(_build_arg_list(instr, param_order))

    arg_list = [
        instr.type.value,
        *(a.value for a in instr.selectable_args),
        *map(_arg_to_str, instr.args),
    ]

    if instr.suboperation is not None:
        arg_list.insert(1, instr.suboperation.value)

    return " ".join(arg_list)


def generate_mlog(mlog_items: list[MlogItem]) -> str:
    mlog: list[str] = []

    for item in mlog_items:
        match item:
            case Instruction():
                mlog.append(_generate_mlog_from_instruction(item))
            case Label(name=name):
                mlog.append(name + ":")

    return "\n".join(mlog)
