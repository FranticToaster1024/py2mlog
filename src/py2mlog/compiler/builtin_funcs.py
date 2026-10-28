import inspect
from collections.abc import Callable
from typing import get_type_hints

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogExpr,
    MlogNumberLiteral,
)
from py2mlog.mlog.suboperations import OperationSuboperation


def _builtin_abs(
    output_expr: MlogExpr, x: MlogExpr, /
) -> tuple[Instruction, ...]:
    return (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ABS,
            (),
            (output_expr, x),
        ),
    )


def _builtin_ord(
    output_expr: MlogExpr, character: MlogExpr, /
) -> tuple[Instruction, ...]:
    return (
        Instruction(
            InstructionType.READ,
            None,
            (),
            (output_expr, character, MlogNumberLiteral(0)),
        ),
    )


BUILTIN_FUNC_MAP: dict[
    str,
    Callable[..., tuple[Instruction, ...]] | None,
] = {
    "abs": _builtin_abs,
    "ord": _builtin_ord,
    "exec": None,
    "eval": None,
}


def _verify_func(func: Callable[..., tuple[Instruction, ...]]) -> bool:
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if not params:
        return False

    first_param = params[0]
    if first_param.name != "output_expr":
        return False

    type_hints = get_type_hints(func)
    first_param_type = type_hints.get(first_param.name, inspect.Parameter.empty)

    return first_param_type == MlogExpr


for f in BUILTIN_FUNC_MAP.values():
    if f is not None and not _verify_func(f):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Bad builtin func def: {f.__name__}",
        )
