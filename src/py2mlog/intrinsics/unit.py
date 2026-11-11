import logging

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.compiler.mimex_utils import camel_to_snake
from py2mlog.compiler.mlog_builtins import UNIT_TYPE_MAP
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    emit_subop_func_factory,
    get_func_names,
    validate_arg_type_factory,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBoolLiteral,
    MlogBuiltin,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.selectable_params import (
    RadarSortSelectableParam,
    RadarTargetSelectableParam,
)
from py2mlog.mlog.suboperations import UnitControlSuboperation

logger = logging.getLogger(__name__)


# ----------------------------------------
# Unit namespace (Unit.*)
# ----------------------------------------
_NAMESPACE = "Unit"


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
                "Called '%s' with literal of type '%s'.",
                get_func_names(_NAMESPACE, _REV_MAP, _unit_bind),
                type(type_).__name__,
            )

        call_ctx.emitter.emit_instruction(
            Instruction(InstructionType.UNIT_BIND, None, (), (type_,))
        )

    return MlogNullLiteral()


_RADAR_TARGET_NAME_MAP = {t.value: t for t in RadarTargetSelectableParam}
_RADAR_SORT_NAME_MAP = {
    name: sel_param
    for sel_param in RadarSortSelectableParam
    for name in (
        sel_param.value,
        camel_to_snake(sel_param.value),
        sel_param.value.lower(),
    )
}
_RADAR_ORDER_NAMES = {
    # im not sure if 'min' and 'max' are fully accurate
    # but pyndustric compatibility so
    "min": MlogNumberLiteral(1),
    "True": MlogNumberLiteral(1),
    "1": MlogNumberLiteral(1),
    "max": MlogNumberLiteral(0),
    "False": MlogNumberLiteral(0),
    "0": MlogNumberLiteral(0),
}
_RadarTargetSelParam_Any = MlogStringLiteral("any")
_RadarSortSelParam_Distance = MlogStringLiteral("distance")
_MlogBoolLiteral_True = MlogBoolLiteral(True)


def _unit_radar(
    call_ctx: IntrinsicCallCtx,
    filter1: MlogExpr = _RadarTargetSelParam_Any,
    filter2: MlogExpr = _RadarTargetSelParam_Any,
    filter3: MlogExpr = _RadarTargetSelParam_Any,
    /,
    *,
    order: MlogExpr = _MlogBoolLiteral_True,
    key: MlogExpr = _RadarSortSelParam_Distance,
) -> MlogExpr:
    this_func_name = get_func_names(_NAMESPACE, _REV_MAP, _unit_radar)

    filter_sel_params: list[RadarTargetSelectableParam] = []
    for arg in (filter1, filter2, filter3):
        if not isinstance(arg, (MlogStringLiteral, MlogVar)):
            # raise an error instead of the usual warning
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Called '{this_func_name}' "
                f"with arg '{arg}'. Expected type: '{MlogStringLiteral.__name__}' "
                f"or '{MlogVar.__name__}'",
            )

        arg_str = arg.value if isinstance(arg, MlogStringLiteral) else arg.name
        filter_sel_param = _RADAR_TARGET_NAME_MAP.get(arg_str)
        if filter_sel_param is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Called '{this_func_name}' with unknown filter type '{arg_str}'. "
                f"Allowed types: '{', '.join(_RADAR_TARGET_NAME_MAP)}'",
            )

        filter_sel_params.append(filter_sel_param)

    if not isinstance(key, (MlogStringLiteral, MlogVar)):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_ctx.src_loc,
            err=f"Called '{this_func_name}' with arg '{arg}'. "
            f"Expected type: '{MlogStringLiteral.__name__}' "
            f"or '{MlogVar.__name__}'",
        )
    key_str = key.value if isinstance(key, MlogStringLiteral) else key.name
    key_sel_param = _RADAR_SORT_NAME_MAP.get(key_str)
    if key_sel_param is None:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_ctx.src_loc,
            err=f"Called '{this_func_name}' with unknown key type '{arg_str}'. "
            f"Allowed types: '{', '.join(_RADAR_TARGET_NAME_MAP)}'",
        )

    if not isinstance(
        order, (MlogVar, MlogNumberLiteral, MlogBoolLiteral, MlogStringLiteral)
    ):
        logger.warning(
            "Called '%s' with literal of type '%s' for 'order' kwarg.",
            this_func_name,
            type(order).__name__,
        )

    if isinstance(order, MlogStringLiteral):
        order_ = _RADAR_ORDER_NAMES.get(order.value)
        if order_ is None:
            logger.warning(
                "Called '%s' with unrecognised string literal '%s'. Defaulting to '%s'.",
                this_func_name,
                order.value,
                _MlogBoolLiteral_True.value,
            )
            order_ = _MlogBoolLiteral_True

        order = order_

    elif isinstance(order, MlogVar):
        order_ = _RADAR_ORDER_NAMES.get(order.name)
        if order_ is not None:
            order = order_

    # idk if mlog accepts bool so just play safe here
    elif isinstance(order, MlogBoolLiteral):
        order = MlogNumberLiteral(int(order.value))

    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.UNIT_RADAR,
            None,
            (*filter_sel_params, key_sel_param),
            (order, call_ctx.output_expr),
        )
    )
    return call_ctx.output_expr


# TODO: locate


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
    "radar": _unit_radar,
    # ucontrol
    "move": _unit_move,
}

_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


_emit_subop = emit_subop_func_factory(InstructionType.DRAW)
_validate_arg_type = validate_arg_type_factory(_NAMESPACE, _REV_MAP)
