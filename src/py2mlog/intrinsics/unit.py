import logging

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.compiler.mlog_builtins import UNIT_TYPE_MAP
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBuiltin,
    MlogExpr,
    MlogNullLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import UnitControlSuboperation

logger = logging.getLogger(__name__)


# ----------------------------------------
# Unit namespace (Unit.*)
# ----------------------------------------
def _unit_bind(
    call_ctx: IntrinsicCallCtx, type_: MlogExpr, /
) -> MlogNullLiteral:
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
        if not isinstance(type_, MlogVar):
            logger.warning(
                "Called 'unit bind' with literal of type '%s'.",
                type(type_).__name__,
            )

        call_ctx.emitter.emit_instruction(
            Instruction(InstructionType.UNIT_BIND, None, (), (type_,))
        )

    return MlogNullLiteral()


# TODO: radar & locate


# all the ucontrol stuff
def _unit_move(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
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


FUNC_MAP: IntrinsicFuncMap = {
    "bind": _unit_bind,
    "move": _unit_move,
}

_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map
