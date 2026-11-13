__all__ = ["FUNC_MAP"]


import logging
from typing import cast

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.compiler.mlog_builtins import ALIGN_MAP
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    emit_subop_func_factory,
    generate_aliases,
    get_func_names,
    validate_arg_type_factory,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBuiltin,
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import DrawSuboperation

logger = logging.getLogger(__name__)


# ----------------------------------------
# Screen namespace (Screen.*)
# ----------------------------------------
NAMESPACE = "Screen"

# param types are not enforced, hence the casts


def _screen_clear(
    call_ctx: IntrinsicCallCtx,
    r: MlogNumberLiteral | MlogVar,
    g: MlogNumberLiteral | MlogVar,
    b: MlogNumberLiteral | MlogVar,
) -> MlogNullLiteral:
    for arg in (r, g, b):
        arg = cast("MlogExpr", arg)  # see comment below 'NAMESPACE = ...'

        if not isinstance(arg, (MlogNumberLiteral, MlogVar)):
            logger.warning(
                "Called '%s' with non-number literal: '%s'.",
                get_func_names(NAMESPACE, _REV_MAP, _screen_clear),
                arg,
            )

        elif isinstance(arg, MlogNumberLiteral) and not 0 <= arg.value <= 255:  # noqa:PLR2004
            logger.warning(
                "Called '%s' with number literal arg '%s' "
                "with value outside bounds.",
                get_func_names(NAMESPACE, _REV_MAP, _screen_clear),
                arg,
            )

    _emit_draw_subop(call_ctx, DrawSuboperation.CLEAR, r, g, b)
    return MlogNullLiteral()


_MlogNumberLiteral255 = MlogNumberLiteral(255)


def _screen_color(
    call_ctx: IntrinsicCallCtx,
    r: MlogNumberLiteral | MlogVar,
    g: MlogNumberLiteral | MlogVar,
    b: MlogNumberLiteral | MlogVar,
    a: MlogNumberLiteral | MlogVar = _MlogNumberLiteral255,
) -> MlogNullLiteral:
    for arg in (r, g, b, a):
        arg = cast("MlogExpr", arg)

        if not isinstance(arg, (MlogNumberLiteral, MlogVar)):
            logger.warning(
                "Called '%s' with non-number literal: '%s'.",
                get_func_names(NAMESPACE, _REV_MAP, _screen_color),
                arg,
            )

        elif isinstance(arg, MlogNumberLiteral) and not 0 <= arg.value <= 255:  # noqa:PLR2004
            logger.warning(
                "Called '%s' with number literal arg '%s' "
                "with value outside bounds.",
                get_func_names(NAMESPACE, _REV_MAP, _screen_color),
                arg,
            )

    _emit_draw_subop(call_ctx, DrawSuboperation.COLOR, r, g, b, a)
    return MlogNullLiteral()


def _screen_col(
    call_ctx: IntrinsicCallCtx, color: MlogColorLiteral, /
) -> MlogNullLiteral:
    _validate_arg_type(MlogColorLiteral, _screen_col, color)
    _emit_draw_subop(call_ctx, DrawSuboperation.COL, color)
    return MlogNullLiteral()


def _screen_stroke(
    call_ctx: IntrinsicCallCtx, width: MlogNumberLiteral
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_stroke, width)
    _emit_draw_subop(call_ctx, DrawSuboperation.STROKE, width)
    return MlogNullLiteral()


def _screen_line(
    call_ctx: IntrinsicCallCtx,
    x1: MlogNumberLiteral,
    y1: MlogNumberLiteral,
    x2: MlogNumberLiteral,
    y2: MlogNumberLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_line, x1, y1, x2, y2)
    _emit_draw_subop(call_ctx, DrawSuboperation.LINE, x1, y1, x2, y2)
    return MlogNullLiteral()


def _screen_rect(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    width: MlogNumberLiteral,
    height: MlogNumberLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_rect, x, y, width, height)
    _emit_draw_subop(call_ctx, DrawSuboperation.RECT, x, y, width, height)
    return MlogNullLiteral()


def _screen_line_rect(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    width: MlogNumberLiteral,
    height: MlogNumberLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(
        MlogNumberLiteral, _screen_line_rect, x, y, width, height
    )
    _emit_draw_subop(call_ctx, DrawSuboperation.LINE_RECT, x, y, width, height)
    return MlogNullLiteral()


def _screen_poly(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    sides: MlogNumberLiteral,
    radius: MlogNumberLiteral,
    rotation: MlogNumberLiteral,
) -> MlogNullLiteral:
    sides_ = cast("MlogExpr", sides)

    _validate_arg_type(
        MlogNumberLiteral, _screen_poly, x, y, sides_, radius, rotation
    )
    if isinstance(sides_, MlogNumberLiteral) and not isinstance(
        sides_.value, int
    ):
        logger.warning(
            "Called '%s' with float literal for arg 'sides': '%s'.",
            get_func_names(NAMESPACE, _REV_MAP, _screen_poly),
            sides_,
        )

    _emit_draw_subop(
        call_ctx, DrawSuboperation.POLY, x, y, sides_, radius, rotation
    )
    return MlogNullLiteral()


def _screen_line_poly(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    sides: MlogNumberLiteral,
    radius: MlogNumberLiteral,
    rotation: MlogNumberLiteral,
) -> MlogNullLiteral:
    sides_ = cast("MlogExpr", sides)

    _validate_arg_type(
        MlogNumberLiteral, _screen_poly, x, y, sides_, radius, rotation
    )
    if isinstance(sides_, MlogNumberLiteral) and not isinstance(
        sides_.value, int
    ):
        logger.warning(
            "Called '%s' with float literal for arg 'sides': '%s'.",
            get_func_names(NAMESPACE, _REV_MAP, _screen_line_poly),
            sides_,
        )

    _emit_draw_subop(
        call_ctx, DrawSuboperation.LINE_POLY, x, y, sides_, radius, rotation
    )
    return MlogNullLiteral()


def _screen_triangle(
    call_ctx: IntrinsicCallCtx,
    x1: MlogNumberLiteral,
    y1: MlogNumberLiteral,
    x2: MlogNumberLiteral,
    y2: MlogNumberLiteral,
    x3: MlogNumberLiteral,
    y3: MlogNumberLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(
        MlogNumberLiteral, _screen_triangle, x1, y1, x2, y2, x3, y3
    )
    _emit_draw_subop(
        call_ctx, DrawSuboperation.TRIANGLE, x1, y1, x2, y2, x3, y3
    )
    return MlogNullLiteral()


def _screen_image(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    image: MlogBuiltin,
    size: MlogNumberLiteral,
    rotation: MlogNumberLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_image, x, y, size, rotation)
    _validate_arg_type(MlogBuiltin, _screen_image, image)
    _emit_draw_subop(
        call_ctx, DrawSuboperation.IMAGE, x, y, image, size, rotation
    )
    return MlogNullLiteral()


def _screen_print(
    call_ctx: IntrinsicCallCtx,
    x: MlogNumberLiteral,
    y: MlogNumberLiteral,
    alignment: MlogBuiltin,
) -> MlogNullLiteral:
    alignment_ = cast("MlogExpr", alignment)

    _validate_arg_type(MlogNumberLiteral, _screen_print, x, y)
    if isinstance(alignment_, MlogStringLiteral):
        _alignment = ALIGN_MAP.get(alignment_.value)
        if _alignment is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Unknown alignment '{alignment_}'",
            )

        alignment_ = _alignment

    elif not isinstance(alignment_, (MlogBuiltin, MlogVar)):
        logger.warning(
            "Called '%s' with literal of type '%s'.",
            get_func_names(NAMESPACE, _REV_MAP, _screen_print),
            type(alignment_).__name__,
        )

    _emit_draw_subop(call_ctx, DrawSuboperation.PRINT, x, y, alignment_)
    return MlogNullLiteral()


def _screen_translate(
    call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, y: MlogNumberLiteral
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_translate, x, y)
    _emit_draw_subop(call_ctx, DrawSuboperation.TRANSLATE, x, y)
    return MlogNullLiteral()


def _screen_scale(
    call_ctx: IntrinsicCallCtx, x: MlogNumberLiteral, y: MlogNumberLiteral
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_scale, x, y)
    _emit_draw_subop(call_ctx, DrawSuboperation.SCALE, x, y)
    return MlogNullLiteral()


def _screen_rotate(
    call_ctx: IntrinsicCallCtx, degrees: MlogNumberLiteral
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _screen_rotate, degrees)
    _emit_draw_subop(call_ctx, DrawSuboperation.ROTATE, degrees)
    return MlogNullLiteral()


def _screen_reset(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
    _emit_draw_subop(call_ctx, DrawSuboperation.RESET)
    return MlogNullLiteral()


_MlogVar_display1 = MlogVar("display1")


def _screen_flush(
    call_ctx: IntrinsicCallCtx, target: MlogExpr = _MlogVar_display1
) -> MlogNullLiteral:
    _validate_arg_type(MlogVar, _screen_flush, target)
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.DRAW_FLUSH, None, (), (target,))
    )
    return MlogNullLiteral()


_func_map: IntrinsicFuncMap = {
    "clear": _screen_clear,
    "fill": _screen_clear,  # alias
    "color": _screen_color,
    "col": _screen_col,
    "stroke": _screen_stroke,
    "line": _screen_line,
    "rect": _screen_rect,
    "fill_rect": _screen_rect,  # alias
    "line_rect": _screen_line_rect,
    "hollow_rect": _screen_line_rect,  # alias
    "poly": _screen_poly,
    "fill_poly": _screen_poly,  # alias
    "line_poly": _screen_line_poly,
    "hollow_poly": _screen_line_poly,  # alias
    "triangle": _screen_triangle,
    "image": _screen_image,
    "print": _screen_print,
    "translate": _screen_translate,
    "scale": _screen_scale,
    "rotate": _screen_rotate,
    "reset": _screen_reset,
    "flush": _screen_flush,
}
FUNC_MAP = generate_aliases(_func_map)


_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


_emit_draw_subop = emit_subop_func_factory(InstructionType.DRAW)
_validate_arg_type = validate_arg_type_factory(NAMESPACE, _REV_MAP)
