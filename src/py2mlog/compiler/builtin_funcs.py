import logging
from collections.abc import Callable
from dataclasses import dataclass
from string import hexdigits
from typing import Concatenate

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.compiler.mlog_builtins import ALIGN_MAP, UNIT_TYPE_MAP
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBuiltin,
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import (
    DrawSuboperation,
    OperationSuboperation,
    UnitControlSuboperation,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuiltinCallCtx:
    output_expr: MlogExpr
    src_loc: SourceLocation
    emitter: Emitter


type _BuiltinFunc = Callable[Concatenate[BuiltinCallCtx, ...], MlogExpr]
type _BuiltinFuncMap = dict[str, _BuiltinFunc | None]
type _BuiltinFuncRevMap = dict[_BuiltinFunc | None, list[str]]


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


INLINE_BUILTIN_FUNC_MAP: _BuiltinFuncMap = {
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


UNIT_NAMESPACE_BUILTIN_FUNC_MAP: _BuiltinFuncMap = {
    "bind": _unit_bind,
    "move": _unit_move,
}


# ----------------------------------------
# Screen namespace (Screen.*)
# ----------------------------------------
def _get_func_names(
    namespace: str, rev_map: _BuiltinFuncRevMap, func: _BuiltinFunc
) -> str:
    func_names = "/".join(rev_map.get(func, ("[func not in _rev_map]",)))

    return f"{namespace}.{func_names}"


# maybe make a factory for these later if necessary
def _emit_draw_subop(
    call_ctx: BuiltinCallCtx, subop: DrawSuboperation, *args: MlogExpr
) -> None:
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.DRAW, subop, (), args)
    )


# this might like mess up the logger location but ¯\_(ツ)_/¯
def _validate_screen_arg_type(
    type_: type[MlogExpr], func: _BuiltinFunc, *args: MlogExpr
) -> None:
    for arg in args:
        if not isinstance(arg, (type_, MlogVar)):
            # quite cursed and probably overkill

            logger.warning(
                "Called '%s' with '%s'. Expected '%s'%s.",
                _get_func_names("Screen", SCREEN_NAMESPACE_REV_MAP, func),
                arg,
                type(type_).__name__,
                " or 'MlogVar'" if type_ is not MlogVar else "",
            )


def _screen_clear(
    call_ctx: BuiltinCallCtx, r: MlogExpr, g: MlogExpr, b: MlogExpr
) -> MlogNullLiteral:
    for arg in (r, g, b):
        if not isinstance(arg, (MlogNumberLiteral, MlogVar)):
            logger.warning(
                "Called '%s' with non-number literal: '%s'.",
                _get_func_names(
                    "Screen", SCREEN_NAMESPACE_REV_MAP, _screen_clear
                ),
                arg,
            )

        elif isinstance(arg, MlogNumberLiteral) and not 0 <= arg.value <= 255:  # noqa:PLR2004
            logger.warning(
                "Called '%s' with number literal arg '%s' "
                "with value outside bounds.",
                _get_func_names(
                    "Screen", SCREEN_NAMESPACE_REV_MAP, _screen_clear
                ),
                arg,
            )

    _emit_draw_subop(call_ctx, DrawSuboperation.CLEAR, r, g, b)
    return MlogNullLiteral()


_MlogNumberLiteral255 = MlogNumberLiteral(255)


def _screen_color(
    call_ctx: BuiltinCallCtx,
    r: MlogExpr,
    g: MlogExpr,
    b: MlogExpr,
    a: MlogExpr = _MlogNumberLiteral255,
) -> MlogNullLiteral:
    for arg in (r, g, b, a):
        if not isinstance(arg, (MlogNumberLiteral, MlogVar)):
            logger.warning(
                "Called '%s' with non-number literal: '%s'.",
                _get_func_names(
                    "Screen", SCREEN_NAMESPACE_REV_MAP, _screen_color
                ),
                arg,
            )

        elif isinstance(arg, MlogNumberLiteral) and not 0 <= arg.value <= 255:  # noqa:PLR2004
            logger.warning(
                "Called '%s' with number literal arg '%s' "
                "with value outside bounds.",
                _get_func_names(
                    "Screen", SCREEN_NAMESPACE_REV_MAP, _screen_color
                ),
                arg,
            )

    _emit_draw_subop(call_ctx, DrawSuboperation.COLOR, r, g, b, a)
    return MlogNullLiteral()


def _screen_col(
    call_ctx: BuiltinCallCtx, color: MlogExpr, /
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogColorLiteral, _screen_col, color)
    _emit_draw_subop(call_ctx, DrawSuboperation.COL, color)
    return MlogNullLiteral()


def _screen_stroke(
    call_ctx: BuiltinCallCtx, width: MlogExpr
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_stroke, width)
    _emit_draw_subop(call_ctx, DrawSuboperation.STROKE, width)
    return MlogNullLiteral()


def _screen_line(
    call_ctx: BuiltinCallCtx,
    x1: MlogExpr,
    y1: MlogExpr,
    x2: MlogExpr,
    y2: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_line, x1, y1, x2, y2)
    _emit_draw_subop(call_ctx, DrawSuboperation.LINE, x1, y1, x2, y2)
    return MlogNullLiteral()


def _screen_rect(
    call_ctx: BuiltinCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    width: MlogExpr,
    height: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_rect, x, y, width, height
    )
    _emit_draw_subop(call_ctx, DrawSuboperation.RECT, x, y, width, height)
    return MlogNullLiteral()


def _screen_line_rect(
    call_ctx: BuiltinCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    width: MlogExpr,
    height: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_line_rect, x, y, width, height
    )
    _emit_draw_subop(call_ctx, DrawSuboperation.LINE_RECT, x, y, width, height)
    return MlogNullLiteral()


def _screen_poly(
    call_ctx: BuiltinCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    sides: MlogExpr,
    radius: MlogExpr,
    rotation: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_poly, x, y, sides, radius, rotation
    )
    if isinstance(sides, MlogNumberLiteral) and not isinstance(
        sides.value, int
    ):
        logger.warning(
            "Called '%s' with float literal for arg 'sides': '%s'.",
            _get_func_names("Screen", SCREEN_NAMESPACE_REV_MAP, _screen_poly),
            sides,
        )

    _emit_draw_subop(
        call_ctx, DrawSuboperation.POLY, x, y, sides, radius, rotation
    )
    return MlogNullLiteral()


def _screen_line_poly(
    call_ctx: BuiltinCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    sides: MlogExpr,
    radius: MlogExpr,
    rotation: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_poly, x, y, sides, radius, rotation
    )
    if isinstance(sides, MlogNumberLiteral) and not isinstance(
        sides.value, int
    ):
        logger.warning(
            "Called '%s' with float literal for arg 'sides': '%s'.",
            _get_func_names(
                "Screen", SCREEN_NAMESPACE_REV_MAP, _screen_line_poly
            ),
            sides,
        )

    _emit_draw_subop(
        call_ctx, DrawSuboperation.LINE_POLY, x, y, sides, radius, rotation
    )
    return MlogNullLiteral()


def _screen_triangle(
    call_ctx: BuiltinCallCtx,
    x1: MlogExpr,
    y1: MlogExpr,
    x2: MlogExpr,
    y2: MlogExpr,
    x3: MlogExpr,
    y3: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_triangle, x1, y1, x2, y2, x3, y3
    )
    _emit_draw_subop(
        call_ctx, DrawSuboperation.TRIANGLE, x1, y1, x2, y2, x3, y3
    )
    return MlogNullLiteral()


def _screen_image(
    call_ctx: BuiltinCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    image: MlogExpr,
    size: MlogExpr,
    rotation: MlogExpr,
) -> MlogNullLiteral:
    _validate_screen_arg_type(
        MlogNumberLiteral, _screen_image, x, y, size, rotation
    )
    _validate_screen_arg_type(MlogBuiltin, _screen_image, image)
    _emit_draw_subop(
        call_ctx, DrawSuboperation.IMAGE, x, y, image, size, rotation
    )
    return MlogNullLiteral()


def _screen_print(
    call_ctx: BuiltinCallCtx, x: MlogExpr, y: MlogExpr, alignment: MlogExpr
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_print, x, y)
    if isinstance(alignment, MlogStringLiteral):
        _alignment = ALIGN_MAP.get(alignment.value)
        if _alignment is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Unknown alignment '{alignment}'",
            )

        alignment = _alignment

    elif not isinstance(alignment, (MlogBuiltin, MlogVar)):
        logger.warning(
            "Called '%s' with literal of type '%s'.",
            _get_func_names("Screen", SCREEN_NAMESPACE_REV_MAP, _screen_print),
            type(alignment).__name__,
        )

    _emit_draw_subop(call_ctx, DrawSuboperation.PRINT, x, y, alignment)
    return MlogNullLiteral()


def _screen_translate(
    call_ctx: BuiltinCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_translate, x, y)
    _emit_draw_subop(call_ctx, DrawSuboperation.TRANSLATE, x, y)
    return MlogNullLiteral()


def _screen_scale(
    call_ctx: BuiltinCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_scale, x, y)
    _emit_draw_subop(call_ctx, DrawSuboperation.SCALE, x, y)
    return MlogNullLiteral()


def _screen_rotate(
    call_ctx: BuiltinCallCtx, degrees: MlogExpr
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogNumberLiteral, _screen_rotate, degrees)
    _emit_draw_subop(call_ctx, DrawSuboperation.ROTATE, degrees)
    return MlogNullLiteral()


def _screen_reset(call_ctx: BuiltinCallCtx) -> MlogNullLiteral:
    _emit_draw_subop(call_ctx, DrawSuboperation.RESET)
    return MlogNullLiteral()


_MlogVar_display1 = MlogVar("display1")


def _screen_flush(
    call_ctx: BuiltinCallCtx, target: MlogExpr = _MlogVar_display1
) -> MlogNullLiteral:
    _validate_screen_arg_type(MlogVar, _screen_flush, target)
    call_ctx.emitter.emit_instruction(
        Instruction(InstructionType.DRAW_FLUSH, None, (), (target,))
    )
    return MlogNullLiteral()


SCREEN_NAMESPACE_BUILTIN_FUNC_MAP: _BuiltinFuncMap = {
    "clear": _screen_clear,
    "fill": _screen_clear,  # alias
    "color": _screen_color,
    "col": _screen_col,
    "stroke": _screen_stroke,
    "line": _screen_line,
    "rect": _screen_rect,
    "fillrect": _screen_rect,  # alias
    "fill_rect": _screen_rect,  # alias
    "line_rect": _screen_line_rect,
    "linerect": _screen_line_rect,  # alias
    "hollow_rect": _screen_line_rect,  # alias
    "poly": _screen_poly,
    "fillpoly": _screen_poly,  # alias
    "fill_poly": _screen_poly,  # alias
    "line_poly": _screen_line_poly,
    "linepoly": _screen_line_poly,  # alias
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


_screen_namespace_rev_map: _BuiltinFuncRevMap = {}
for k, v in SCREEN_NAMESPACE_BUILTIN_FUNC_MAP.items():
    _screen_namespace_rev_map.setdefault(v, []).append(k)

SCREEN_NAMESPACE_REV_MAP = _screen_namespace_rev_map
