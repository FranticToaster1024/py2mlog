__all__ = ["FUNC_MAP", "builtin_color"]


import logging
from inspect import cleandoc
from string import hexdigits
from typing import cast

from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
)
from py2mlog.compiler.mimex_utils import camel_to_snake
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFunc,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    emit_subop_func_factory,
    generate_aliases,
    get_func_names,
    pad_output_expr,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import OperationSuboperation

logger = logging.getLogger(__name__)


def _single_arg_op_builtin_factory(
    subop: OperationSuboperation,
) -> IntrinsicFunc:
    """
    Param and return type hints are MlogNumberLiteral.
    """

    def _single_arg_op_builtin(
        call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, /
    ) -> MlogNumberLiteral:
        _validate_arg_type(MlogNumberLiteral, _single_arg_op_builtin, x)
        _emit_operation_subop(call_ctx, subop, call_ctx.output_expr[0], x)
        # type hints are lies (for the sake of stub generation) and unenforced anyway
        return cast("MlogNumberLiteral", call_ctx.output_expr[0])

    return _single_arg_op_builtin


# something something DRY
def _double_arg_op_builtin_factory(
    subop: OperationSuboperation, docstring: str | None = None
) -> IntrinsicFunc:
    """
    Param and return type hints are MlogNumberLiteral.
    """

    def _double_arg_op_builtin(
        call_ctx: IntrinsicCallCtx,
        a: MlogNumberLiteral,
        b: MlogNumberLiteral,
        /,
    ) -> MlogNumberLiteral:
        _validate_arg_type(MlogNumberLiteral, _double_arg_op_builtin, a, b)
        _emit_operation_subop(call_ctx, subop, call_ctx.output_expr[0], a, b)
        return cast("MlogNumberLiteral", call_ctx.output_expr[0])

    if docstring is not None:
        _double_arg_op_builtin.__doc__ = cleandoc(docstring)
    return _double_arg_op_builtin


# ----------------------------------------
# inline python builtins
# ----------------------------------------
def _ord(
    call_ctx: IntrinsicCallCtx, character: MlogStringLiteral, /
) -> MlogNumberLiteral:
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.READ,
            None,
            (),
            (call_ctx.output_expr[0], character, MlogNumberLiteral(0)),
        ),
    )
    return cast("MlogNumberLiteral", call_ctx.output_expr[0])


def _min(
    call_ctx: IntrinsicCallCtx,
    arg1: MlogNumberLiteral,
    arg2: MlogNumberLiteral,
    # *args: MlogExpr,
    # default: MlogExpr,
    # key: MlogExpr ,
) -> MlogNumberLiteral:

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

    return cast("MlogNumberLiteral", call_ctx.output_expr[0])


# ----------------------------------------
# inline non-python builtins
# ----------------------------------------
def _Color(  # noqa: N802
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


def _sleep(
    call_ctx: IntrinsicCallCtx, t: MlogNumberLiteral, /
) -> MlogNullLiteral:
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.WAIT, None, (), (t,))
    )
    return MlogNullLiteral()


def _print_flush(
    call_ctx: IntrinsicCallCtx, tgt: MlogVar, /
) -> MlogNullLiteral:
    _validate_arg_type(MlogVar, _print_flush, tgt)
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.PRINT_FLUSH, None, (), (tgt,))
    )
    return MlogNullLiteral()


def _end(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
    """
    Jump to the top of the program.
    Does NOT terminate the program; use 'stop()' instead.
    """
    # end gets emitted first
    # so if user tries to assign to result
    # it never gets reached
    # but it's not really incorrect or misleading behaviour is it?
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.END, None, (), ())
    )
    return MlogNullLiteral()


def _stop(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
    """Terminates the program."""
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.STOP, None, (), ())
    )
    return MlogNullLiteral()


def _pack_color(
    call_ctx: IntrinsicCallCtx,
    r: MlogNumberLiteral,
    g: MlogNumberLiteral,
    b: MlogNumberLiteral,
    a: MlogNumberLiteral,
) -> MlogNumberLiteral:
    """Arguments should be between 0 and 1 inclusive."""
    _validate_arg_type(MlogNumberLiteral, _pack_color, r, g, b, a)
    for arg in (r, g, b, a):
        arg = cast("MlogExpr", arg)
        if isinstance(arg, MlogNumberLiteral) and not 0 <= arg.value <= 1:
            logger.warning(
                "Called '%s' with number literal arg '%s' "
                "with value outside bounds of [0, 1].",
                get_func_names("", _REV_MAP, _pack_color),
                arg,
            )

    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.PACK_COLOR,
            None,
            (),
            (call_ctx.output_expr[0], r, g, b, a),
        )
    )
    return cast("MlogNumberLiteral", call_ctx.output_expr[0])


def _unpack_color(
    call_ctx: IntrinsicCallCtx, color: MlogColorLiteral, /
) -> tuple[MlogNumberLiteral, ...]:
    output_expr = pad_output_expr(call_ctx.output_expr, 4)
    _validate_arg_type(MlogColorLiteral, _unpack_color, color)
    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.UNPACK_COLOR, None, (), (*output_expr, color)
        )
    )
    return cast("tuple[MlogNumberLiteral, ...]", output_expr)


# ----------------------------------------
# op funcs
# ----------------------------------------
def _op_vec_angle(
    call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, y: MlogNumberLiteral, /
) -> MlogNumberLiteral:
    """
    Similar to atan2.
    Note that this function takes (x, y) and not (y, x).
    Returns 0 to 360 **degrees**.
    """
    # https://github.com/Anuken/Arc/blob/7445105cd2683daf5b9ac7033ebb07265d3e814d/arc-core/src/arc/math/Angles.java#L58
    _validate_arg_type(MlogNumberLiteral, _op_vec_angle, x, y)
    _emit_operation_subop(
        call_ctx, OperationSuboperation.ANGLE, call_ctx.output_expr[0], x, y
    )
    return cast("MlogNumberLiteral", call_ctx.output_expr[0])


def _op_logn(
    call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, base: MlogNumberLiteral
) -> MlogNumberLiteral:
    _validate_arg_type(MlogNumberLiteral, _op_logn, x, base)
    _emit_operation_subop(
        call_ctx, OperationSuboperation.LOGN, call_ctx.output_expr[0], x, base
    )
    return cast("MlogNumberLiteral", call_ctx.output_expr[0])


# ----------------------------------------
# op func maps
# ----------------------------------------
_SINGLE_ARG_OP_BUILTIN_MAP = {
    "flip": _single_arg_op_builtin_factory(OperationSuboperation.BITWISE_NOT),
    **{
        camel_to_snake(subop.value): _single_arg_op_builtin_factory(subop)
        for subop in (
            OperationSuboperation.ABS,
            OperationSuboperation.SIGN,
            OperationSuboperation.LOG,
            OperationSuboperation.LOG10,
            OperationSuboperation.FLOOR,
            OperationSuboperation.CEIL,
            OperationSuboperation.ROUND,
            OperationSuboperation.SQRT,
            OperationSuboperation.RAND,
            OperationSuboperation.SIN,
            OperationSuboperation.COS,
            OperationSuboperation.TAN,
            OperationSuboperation.ASIN,
            OperationSuboperation.ACOS,
            OperationSuboperation.ATAN,
        )
    },
}


_DOUBLE_ARG_OP_BUILTIN_MAP = {
    "vec_angle": _op_vec_angle,
    "vec_len": _double_arg_op_builtin_factory(OperationSuboperation.LEN),
    "logn": _op_logn,
    **{
        camel_to_snake(subop.value): _double_arg_op_builtin_factory(subop)
        for subop in (
            # python uses true modulo
            # x = a % b
            # compiles to
            # op emod x a b
            #    ^
            OperationSuboperation.MOD,
            OperationSuboperation.UNSIGNED_BITSHIFT_RIGHT,
            OperationSuboperation.ANGLE_DIFF,
            # docstring would be useful here but im lazy
            OperationSuboperation.NOISE,
        )
    },
}


# ----------------------------------------
# func map
# ----------------------------------------
_func_map: IntrinsicFuncMap = (
    {
        # inline python builtins
        "ord": _ord,
        "min": _min,
        # inline non-python builtins
        "Color": _Color,
        "sleep": _sleep,
        "wait": _sleep,
        "print_flush": _print_flush,
        "end": _end,
        "top": _end,
        "stop": _stop,
        "pack_color": _pack_color,
        "unpack_color": _unpack_color,
    }
    | _SINGLE_ARG_OP_BUILTIN_MAP
    | _DOUBLE_ARG_OP_BUILTIN_MAP
)


FUNC_MAP = generate_aliases(_func_map)


_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


# ¯\_(ツ)_/¯
builtin_color = _Color


# TODO: DRY
def _validate_arg_type(
    type_: type[MlogExpr] | tuple[type[MlogExpr], ...],
    func: IntrinsicFunc,
    *args: MlogExpr,
) -> None:
    """Accepts MlogVar along with given type(s)."""
    if not type_:
        logger.warning(
            "(Internal) Called _validate_control_or_method_arg_type "
            "with empty tuple as type."
        )
    types = type_ if isinstance(type_, tuple) else (type_,)

    for arg in args:
        if not isinstance(arg, (*types, MlogVar)):
            logger.warning(
                "Called '%s' with arg '%s'. Expected type(s): %s%s.",
                get_func_names("", _REV_MAP, func).replace(".", ""),
                arg,
                ", ".join(type(t).__name__ for t in types),
                ", 'MlogVar'" if MlogVar not in types else "",
            )


_emit_operation_subop = emit_subop_func_factory(InstructionType.OPERATION)
