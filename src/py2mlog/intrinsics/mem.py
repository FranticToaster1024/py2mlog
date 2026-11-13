from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    generate_aliases,
    validate_arg_type_factory,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogVar,
)

NAMESPACE = "Mem"


def _mem_read(
    call_ctx: IntrinsicCallCtx, cell: MlogExpr, index: MlogExpr
) -> MlogExpr:
    _validate_arg_type(MlogVar, _mem_read, cell)
    _validate_arg_type(MlogNumberLiteral, _mem_read, index)
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.READ,
            None,
            (),
            (call_ctx.output_expr[0], cell, index),
        )
    )
    return call_ctx.output_expr[0]


def _mem_write(
    call_ctx: IntrinsicCallCtx, value: MlogExpr, cell: MlogExpr, index: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogVar, _mem_write, cell)
    _validate_arg_type(MlogNumberLiteral, _mem_write, index)
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.WRITE, None, (), (value, cell, index))
    )
    return MlogNullLiteral()


_func_map: IntrinsicFuncMap = {
    "read": _mem_read,
    "write": _mem_write,
}

FUNC_MAP = generate_aliases(_func_map)

_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


_validate_arg_type = validate_arg_type_factory(NAMESPACE, _REV_MAP)
