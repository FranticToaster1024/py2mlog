import ast
import inspect
from collections.abc import Callable
from string import hexdigits
from textwrap import indent
from typing import TypeAlias, get_type_hints

from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogColorLiteral,
    MlogExpr,
    MlogFillerExpr,
    MlogNumberLiteral,
)
from py2mlog.mlog.suboperations import OperationSuboperation


# ----------------------------------------
# python builtins
# ----------------------------------------
# these take compiled arglist
# these might need src loc later idk
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


INLINE_BUILTIN_FUNC_MAP: dict[
    str,
    Callable[..., tuple[Instruction, ...]] | None,
] = {
    "abs": _builtin_abs,
    "ord": _builtin_ord,
    "exec": None,
    "eval": None,
}


def _verify_builtin_func(func: Callable[..., tuple[Instruction, ...]]) -> bool:
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


for f in INLINE_BUILTIN_FUNC_MAP.values():
    if f is not None and not _verify_builtin_func(f):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Bad inline builtin func def: {f.__name__}",
        )


# ----------------------------------------
# special builtins
# ----------------------------------------
# these directly take ast expressions as arguments
def _special_Color(  # noqa: N802
    _: MlogExpr, src_loc: SourceLocation, x: ast.expr, /
) -> tuple[tuple[Instruction, ...], MlogColorLiteral]:
    if not isinstance(x, ast.Constant):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            src_loc,
            err="Called 'Color()' with non-literal",
        )

    if isinstance(x.value, str):
        val = x.value[1:] if x.value[0] == "%" else x.value

        if all(s in hexdigits for s in val):
            # why doesn't ruff flag these as magic values?
            # 'RGB' and 'RGBA'
            if len(val) in (3, 4):
                # TODO: support shorthand hex color literals, possibly with a config
                pass
            # 'RRGGBB' and 'RRGGBBAA'
            elif len(val) in (6, 8):
                return ((), MlogColorLiteral(val))

        raise CompilerError(
            CompilerErrorType.SYNTAX, src_loc, err="Invalid color literal"
        )

    if isinstance(x.value, int):
        if 0x000 <= x.value <= 0xFFFF:  # noqa: PLR2004
            # TODO: support shorthand hex color literals, possibly with a config
            pass
        elif 0x000000 <= x.value <= 0xFFFFFFFF:  # noqa: PLR2004
            return ((), MlogColorLiteral(f"{x.value:x}"))

    raise CompilerError(
        CompilerErrorType.BAD_CALL,
        src_loc,
        err=f"Called 'Color()' with unsupported literal type '{type(x.value).__name__}'",
    )


_SpecialBuiltinFunc: TypeAlias = Callable[
    ..., tuple[tuple[Instruction, ...], MlogExpr]
]

SPECIAL_BUILTIN_FUNC_MAP: dict[str, _SpecialBuiltinFunc] = {
    "Color": _special_Color,
}


def _verify_special_builtin_func(
    func: _SpecialBuiltinFunc,
) -> bool:
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if len(params) < 2:  # noqa: PLR2004
        return False

    # is it really necessary to check param names? type should be enough right?
    # i'll leave it here for now though
    first_param = params[0]
    if first_param.name not in ("_", "output_expr"):
        return False
    second_param = params[1]
    if second_param.name not in ("_", "src_loc"):
        return False

    type_hints = get_type_hints(func)

    first_param_type = type_hints.get(first_param.name, inspect.Parameter.empty)
    if first_param_type != MlogExpr:
        return False

    second_param_type = type_hints.get(
        second_param.name, inspect.Parameter.empty
    )
    return second_param_type == SourceLocation


for f in SPECIAL_BUILTIN_FUNC_MAP.values():
    if f is not None and not _verify_special_builtin_func(f):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Bad special builtin func def: {f.__name__}",
        )


# ----------------------------------------
# miscellaneous
# ----------------------------------------
# this is probably a bad idea but DRY or something ¯\_(ツ)_/¯
def ast_const_to_mlog_col_literal(
    src_loc: SourceLocation, x: ast.Constant
) -> MlogColorLiteral:
    """Internal use only."""
    try:
        return _special_Color(MlogFillerExpr(), src_loc, x)[1]
    except CompilerError as e:
        raise CompilerError(
            CompilerErrorType.INTERNAL, None, err=f"\n{indent(str(e), '    ')}"
        ) from None
