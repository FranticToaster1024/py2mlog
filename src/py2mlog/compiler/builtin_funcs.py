import logging
from collections.abc import Callable
from dataclasses import dataclass
from string import hexdigits
from typing import Concatenate, TypeAlias

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.compiler.mlog_builtins import UNIT_TYPE_MAP
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBuiltin,
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
)
from py2mlog.mlog.suboperations import (
    OperationSuboperation,
    UnitControlSuboperation,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuiltinCallCtx:
    output_expr: MlogExpr
    src_loc: SourceLocation
    emitter: Emitter


# ----------------------------------------
# inline builtins
# ----------------------------------------
def _inline_abs(call_ctx: BuiltinCallCtx, x: MlogExpr, /) -> MlogExpr:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ABS,
            (),
            (call_ctx.output_expr, x),
        ),
    )
    return call_ctx.output_expr


def _inline_ord(call_ctx: BuiltinCallCtx, character: MlogExpr, /) -> MlogExpr:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.READ,
            None,
            (),
            (call_ctx.output_expr, character, MlogNumberLiteral(0)),
        ),
    )
    return call_ctx.output_expr


def _inline_min(
    call_ctx: BuiltinCallCtx,
    arg1: MlogExpr,
    arg2: MlogExpr,
    # *args: MlogExpr,
    # default: MlogExpr,
    # key: MlogExpr ,
) -> MlogExpr:

    # TODO: support *args or something

    # args_rev = tuple(reversed(args))

    instructions: list[Instruction] = []
    curr = arg2  # kinda hacky but whatever x2
    # if args_rev:
    #     curr = args_rev[0]  # kinda hacky but whatever
    #     for val in (*args_rev[1:], arg2):
    #         prev = curr
    #         curr = call_ctx.emitter.new_tmp()
    #         instructions.append(
    #             Instruction(
    #                 InstructionType.OPERATION,
    #                 OperationSuboperation.MIN,
    #                 (),
    #                 (curr, prev, val),
    #             )
    #         )

    call_ctx.emitter.emit_items(
        (
            *instructions,
            Instruction(
                InstructionType.OPERATION,
                OperationSuboperation.MIN,
                (),
                (call_ctx.output_expr, curr, arg1),
            ),
        )
    )

    return call_ctx.output_expr


def _inline_Color(  # noqa: N802
    call_ctx: BuiltinCallCtx, x: MlogExpr, /
) -> MlogColorLiteral:
    if not isinstance(
        x, (MlogNumberLiteral, MlogStringLiteral, MlogColorLiteral)
    ):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_ctx.src_loc,
            err=f"Called 'Color()' with unsupported MlogExpr type '{type(x).__name__}'",
        )

    # to handle Color("%ffffff")
    if isinstance(x, MlogColorLiteral):
        return x

    if isinstance(x, MlogStringLiteral):
        val = x.value[1:] if x.value[0] == "%" else x.value

        if all(s in hexdigits for s in val):
            # why doesn't ruff flag these as magic values?
            # 'RGB' and 'RGBA'
            if len(val) in (3, 4):
                # TODO: support shorthand hex color literals, possibly with a config
                pass
            # 'RRGGBB' and 'RRGGBBAA'
            elif len(val) in (6, 8):
                return MlogColorLiteral(val)

        raise CompilerError(
            CompilerErrorType.SYNTAX,
            call_ctx.src_loc,
            err="Invalid color literal",
        )

    # i keep forgetting bool is subclass of int
    if isinstance(x.value, int):
        if 0x000 <= x.value <= 0xFFFF:  # noqa: PLR2004
            # TODO: support shorthand hex color literals, possibly with a config
            pass
        elif 0x000000 <= x.value <= 0xFFFFFFFF:  # noqa: PLR2004
            return MlogColorLiteral(f"{x.value:x}")

        raise CompilerError(
            CompilerErrorType.SYNTAX,
            call_ctx.src_loc,
            err="Invalid color literal",
        )

    raise CompilerError(
        CompilerErrorType.BAD_CALL,
        call_ctx.src_loc,
        err="Called 'Color()' with float",
    )


def _inline_sleep(call_ctx: BuiltinCallCtx, t: MlogExpr, /) -> MlogNullLiteral:
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.WAIT, None, (), (t,))
    )
    return MlogNullLiteral()


_InlineBuiltinFunc: TypeAlias = Callable[
    Concatenate[BuiltinCallCtx, ...], MlogExpr
]

INLINE_BUILTIN_FUNC_MAP: dict[str, _InlineBuiltinFunc | None] = {
    "abs": _inline_abs,
    "ord": _inline_ord,
    "min": _inline_min,
    "Color": _inline_Color,
    "sleep": _inline_sleep,
    "wait": _inline_sleep,
    "exec": None,
    "eval": None,
}


# ¯\_(ツ)_/¯
builtin_color = _inline_Color


# ----------------------------------------
# Unit namespace (Unit.*)
# ----------------------------------------
def _unit_bind(call_ctx: BuiltinCallCtx, type_: MlogExpr, /) -> MlogNullLiteral:
    if isinstance(type_, (MlogStringLiteral, MlogBuiltin)):
        type_str = (
            type_.value.removeprefix("@")
            if isinstance(type_, MlogStringLiteral)
            else type_.name
        )

        mlog_builtin = UNIT_TYPE_MAP.get(type_str)
        if mlog_builtin is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Unknown unit type '{type_str}'",
            )

        call_ctx.emitter.emit_instruction(
            Instruction(InstructionType.UNIT_BIND, None, (), (mlog_builtin,))
        )

    else:
        # i mean if the user really wants to
        # unit bind to a color literal
        # im not gonna stop them
        call_ctx.emitter.emit_instruction(
            Instruction(InstructionType.UNIT_BIND, None, (), (type_,))
        )

    return MlogNullLiteral()


# TODO: radar & locate


# all the ucontrol stuff
def _unit_move(
    call_ctx: BuiltinCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.UNIT_CONTROL,
            UnitControlSuboperation.MOVE,
            (),
            (x, y),
        )
    )
    return MlogNullLiteral()


# TODO: all the ucontrol stuff


UNIT_NAMESPACE_BUILTIN_FUNC_MAP: dict[
    str, Callable[Concatenate[BuiltinCallCtx, ...], MlogExpr] | None
] = {
    "bind": _unit_bind,
    "move": _unit_move,
}
