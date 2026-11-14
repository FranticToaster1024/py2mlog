__all__ = ["FUNC_MAP", "builtin_color"]


import logging
from string import hexdigits
from typing import cast

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
)
from py2mlog.mlog.suboperations import OperationSuboperation

logger = logging.getLogger(__name__)


# ----------------------------------------
# inline builtins
# ----------------------------------------
def _inline_abs(
    call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, /
) -> MlogExpr:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ABS,
            (),
            (call_ctx.output_expr[0], x),
        ),
    )
    return call_ctx.output_expr[0]


def _inline_ord(
    call_ctx: IntrinsicCallCtx, character: MlogStringLiteral, /
) -> MlogExpr:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.READ,
            None,
            (),
            (call_ctx.output_expr[0], character, MlogNumberLiteral(0)),
        ),
    )
    return call_ctx.output_expr[0]


def _inline_min(
    call_ctx: IntrinsicCallCtx,
    arg1: MlogNumberLiteral,
    arg2: MlogNumberLiteral,
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
                (call_ctx.output_expr[0], curr, arg1),
            ),
        )
    )

    return call_ctx.output_expr[0]


def _inline_Color(  # noqa: N802
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral | MlogColorLiteral | MlogStringLiteral,
    /,
) -> MlogColorLiteral:
    if not isinstance(
        cast("MlogExpr", x),
        (MlogNumberLiteral, MlogStringLiteral, MlogColorLiteral),
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


def _inline_sleep(
    call_ctx: IntrinsicCallCtx, t: MlogNumberLiteral, /
) -> MlogNullLiteral:
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.WAIT, None, (), (t,))
    )
    return MlogNullLiteral()


FUNC_MAP: IntrinsicFuncMap = {
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
