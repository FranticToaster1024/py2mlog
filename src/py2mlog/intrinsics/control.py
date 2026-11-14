"""
Also used for method calls on objects.
"""

__all__ = ["FUNC_MAP"]

import logging

from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFunc,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    emit_subop_func_factory,
    generate_aliases,
    get_func_names,
)
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBoolLiteral,
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import ControlSuboperation

logger = logging.getLogger(__name__)

NAMESPACE_NAME = "Control"


def _control_enabled(
    call_ctx: IntrinsicCallCtx, building: MlogExpr, enabled: MlogExpr
) -> MlogNullLiteral:
    _validate_control_or_method_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _control_enabled, enabled
    )
    _emit_control_subop(
        call_ctx, ControlSuboperation.ENABLED, building, enabled
    )
    return MlogNullLiteral()


def _control_enable(
    call_ctx: IntrinsicCallCtx, building: MlogExpr
) -> MlogNullLiteral:
    _emit_control_subop(
        call_ctx, ControlSuboperation.ENABLED, building, MlogBoolLiteral(True)
    )
    return MlogNullLiteral()


def _control_disable(
    call_ctx: IntrinsicCallCtx, building: MlogExpr
) -> MlogNullLiteral:
    _emit_control_subop(
        call_ctx, ControlSuboperation.ENABLED, building, MlogBoolLiteral(False)
    )
    return MlogNullLiteral()


_MlogBoolLiteral_True = MlogBoolLiteral(True)


def _control_shoot(
    call_ctx: IntrinsicCallCtx,
    building: MlogExpr,
    x: MlogExpr,
    y: MlogExpr,
    shoot: MlogExpr = _MlogBoolLiteral_True,
) -> MlogNullLiteral:
    _validate_control_or_method_arg_type(
        MlogNumberLiteral, _control_shoot, x, y
    )
    _validate_control_or_method_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _control_shoot, shoot
    )
    _emit_control_subop(
        call_ctx, ControlSuboperation.SHOOT, building, x, y, shoot
    )
    return MlogNullLiteral()


def _control_ceasefire(
    call_ctx: IntrinsicCallCtx, building: MlogExpr
) -> MlogNullLiteral:
    _emit_control_subop(
        call_ctx,
        ControlSuboperation.SHOOT,
        building,
        MlogNumberLiteral(0),
        MlogNumberLiteral(0),
        MlogBoolLiteral(False),
    )
    return MlogNullLiteral()


def _control_shootp(
    call_ctx: IntrinsicCallCtx,
    building: MlogExpr,
    unit: MlogExpr,
    shoot: MlogExpr = _MlogBoolLiteral_True,
) -> MlogNullLiteral:
    _validate_control_or_method_arg_type(
        (MlogNumberLiteral, MlogBoolLiteral), _control_shootp, shoot
    )
    _emit_control_subop(
        call_ctx, ControlSuboperation.SHOOTP, building, unit, shoot
    )
    return MlogNullLiteral()


def _control_color(
    call_ctx: IntrinsicCallCtx, building: MlogExpr, color: MlogExpr
) -> MlogNullLiteral:
    _validate_control_or_method_arg_type(
        MlogColorLiteral, _control_color, color
    )
    _emit_control_subop(call_ctx, ControlSuboperation.COLOR, building, color)
    return MlogNullLiteral()


def _control_config(
    call_ctx: IntrinsicCallCtx, building: MlogExpr, config: MlogExpr
) -> MlogNullLiteral:
    _emit_control_subop(call_ctx, ControlSuboperation.CONFIG, building, config)
    return MlogNullLiteral()


_func_map: IntrinsicFuncMap = {
    "enabled": _control_enabled,
    "enable": _control_enable,
    "disable": _control_disable,
    "shoot": _control_shoot,
    "ceasefire": _control_ceasefire,
    "shootp": _control_shootp,
    "color": _control_color,
    "config": _control_config,
}

FUNC_MAP = generate_aliases(_func_map)

_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


def _validate_control_or_method_arg_type(
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
            names = get_func_names(NAMESPACE_NAME, _REV_MAP, func)
            logger.warning(
                "Called '%s' or their method equivalents "
                "with arg '%s'. Expected type(s): %s%s.",
                names,
                arg,
                ", ".join(type(t).__name__ for t in types),
                ", 'MlogVar'" if MlogVar in types else "",
            )


_emit_control_subop = emit_subop_func_factory(InstructionType.CONTROL)
