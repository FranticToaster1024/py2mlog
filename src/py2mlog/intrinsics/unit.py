import logging
from collections.abc import Callable

from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
)
from py2mlog.compiler.mimex_utils import camel_to_snake
from py2mlog.compiler.mlog_builtins import UNIT_TYPE_MAP
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFuncMap,
    IntrinsicFuncRevMap,
    emit_subop_func_factory,
    generate_aliases,
    get_func_names,
    pad_output_expr,
    validate_arg_type_factory,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBoolLiteral,
    MlogBuiltin,
    MlogExpr,
    MlogFillerExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.selectable_params import (
    RadarSortSelectableParam,
    RadarTargetSelectableParam,
    UnitLocateBuildingSelectableParam,
)
from py2mlog.mlog.suboperations import (
    UnitControlSuboperation,
    UnitLocateSuboperation,
)

logger = logging.getLogger(__name__)


# ----------------------------------------
# Unit namespace (Unit.*)
# ----------------------------------------
NAMESPACE = "Unit"


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
                get_func_names(NAMESPACE, _REV_MAP, _unit_bind),
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
    "min": MlogBoolLiteral(True),
    "True": MlogBoolLiteral(True),
    "1": MlogBoolLiteral(True),
    "max": MlogBoolLiteral(False),
    "False": MlogBoolLiteral(False),
    "0": MlogBoolLiteral(False),
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
    this_func_name = get_func_names(NAMESPACE, _REV_MAP, _unit_radar)

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
            err=f"Called '{this_func_name}' with arg '{arg}' for param 'key'. "
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

    call_ctx.emitter.emit_instruction(
        Instruction(
            InstructionType.UNIT_RADAR,
            None,
            (*filter_sel_params, key_sel_param),
            (order, call_ctx.output_expr[0]),
        )
    )
    return call_ctx.output_expr[0]


_ULOCATE_BUILDING_SEL_PARAM = {
    name: sel_param
    for sel_param in UnitLocateBuildingSelectableParam
    for name in (
        sel_param.value,
        camel_to_snake(sel_param.value),
        sel_param.value.lower(),
    )
}
_IS_ENEMY_STR_MAP = {
    "False": MlogBoolLiteral(False),
    "ally": MlogBoolLiteral(False),
    "True": MlogBoolLiteral(True),
    "enemy": MlogBoolLiteral(True),
}
_MlogFillerExpr = MlogFillerExpr()


def _unit_locate(
    call_ctx: IntrinsicCallCtx,
    subop: MlogExpr,
    /,
    *,
    block_flag: MlogExpr = _MlogFillerExpr,
    is_enemy_building: MlogExpr = _MlogFillerExpr,
    ore_type: MlogExpr = _MlogFillerExpr,
) -> tuple[MlogExpr, ...]:
    this_func_name = get_func_names(NAMESPACE, _REV_MAP, _unit_locate)

    if not isinstance(subop, (MlogStringLiteral, MlogVar)):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_ctx.src_loc,
            err=f"Called '{this_func_name}' with arg '{subop}' for param 'subop'. "
            f"Allowed types: '{MlogStringLiteral.__name__}' or '{MlogVar.__name__}'",
        )
    subop_str = (
        subop.value if isinstance(subop, MlogStringLiteral) else subop.name
    )

    output_expr = pad_output_expr(call_ctx.output_expr, 4)

    # using kwargs here is a little cursed
    # and the func name is also kinda misleading
    # but its just a tiny helper cut me some slack ok
    def _validate_arg_presence(
        expect_present: bool,  # noqa: FBT001
        **kwargs: MlogExpr,
    ) -> None:
        for param_name, arg in kwargs.items():
            is_present = not isinstance(arg, MlogFillerExpr)
            if is_present != expect_present:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    call_ctx.src_loc,
                    err=f"{'Missing' if expect_present else 'Unexpected'} "
                    f"arg for param '{param_name}'",
                )

    _emit_ulocate_subop = emit_subop_func_factory(InstructionType.UNIT_LOCATE)
    match subop_str:
        case "ore":
            _validate_arg_presence(
                False,
                block_flag=block_flag,
                is_enemy_building=is_enemy_building,
            )
            _validate_arg_presence(True, ore_type=ore_type)
            _validate_arg_type(MlogBuiltin, _unit_locate, ore_type)

            # ulocate ore only returns 3 values
            # also :3
            output_expr = output_expr[:3]
            _emit_ulocate_subop(
                call_ctx, UnitLocateSuboperation.ORE, ore_type, *output_expr
            )

        case "building":
            _validate_arg_presence(False, ore_type=ore_type)
            _validate_arg_presence(
                True, block_flag=block_flag, is_enemy_building=is_enemy_building
            )

            # block flag is a sel param, hence this mess
            if not isinstance(block_flag, (MlogStringLiteral, MlogVar)):
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    call_ctx.src_loc,
                    err=f"Called '{this_func_name}' with arg '{block_flag}' for param 'subop'. "
                    f"Allowed types: '{MlogStringLiteral.__name__}' or '{MlogVar.__name__}'",
                )
            block_flag_str = (
                block_flag.value
                if isinstance(block_flag, MlogStringLiteral)
                else block_flag.name
            )
            block_flag_sel_param = _ULOCATE_BUILDING_SEL_PARAM.get(
                block_flag_str
            )
            if block_flag_sel_param is None:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    call_ctx.src_loc,
                    err=f"Unknown value for param 'block_flag' for '{this_func_name}': {subop_str}",
                )

            _validate_arg_type(
                (MlogBoolLiteral, MlogNumberLiteral, MlogStringLiteral),
                _unit_locate,
                is_enemy_building,
            )
            if isinstance(is_enemy_building, MlogStringLiteral):
                mapped = _IS_ENEMY_STR_MAP.get(is_enemy_building.value)
                if mapped is None:
                    logger.warning(
                        "Called '%s' with %s with value other than %s "
                        "for param 'is_enemy_building': '%s'. ",
                        get_func_names(NAMESPACE, _REV_MAP, _unit_item_drop),
                        MlogStringLiteral.__name__,
                        "/".join(_IS_ENEMY_STR_MAP),
                        is_enemy_building,
                    )
                else:
                    is_enemy_building = mapped

            _emit_ulocate_subop(
                call_ctx,
                UnitLocateSuboperation.BUILDING,
                is_enemy_building,
                *output_expr,
                sel_args=(block_flag_sel_param,),
            )

        case "spawn":
            _validate_arg_presence(
                False,
                ore_type=ore_type,
                block_flag=block_flag,
                is_enemy_building=is_enemy_building,
            )
            _emit_ulocate_subop(
                call_ctx, UnitLocateSuboperation.SPAWN, *output_expr
            )

        case "damaged":
            _validate_arg_presence(
                False,
                ore_type=ore_type,
                block_flag=block_flag,
                is_enemy_building=is_enemy_building,
            )
            _emit_ulocate_subop(
                call_ctx, UnitLocateSuboperation.DAMAGED, *output_expr
            )

        case _:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_ctx.src_loc,
                err=f"Unknown pos arg ('subop') for '{this_func_name}': {subop_str}",
            )

    return output_expr


# all the ucontrol stuff
def _argless_ucontrol_func_factory(
    subop: UnitControlSuboperation,
) -> Callable[[IntrinsicCallCtx], MlogNullLiteral]:

    def _argless_ucontrol_func(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
        _emit_ucontrol_subop(call_ctx, subop)
        return MlogNullLiteral()

    return _argless_ucontrol_func


def _unit_move(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_move, x, y)
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.MOVE, x, y)
    return MlogNullLiteral()


def _unit_approach(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr, radius: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_approach, x, y, radius)
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.APPROACH, x, y, radius
    )
    return MlogNullLiteral()


def _unit_pathfind(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_pathfind, x, y)
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.PATHFIND, x, y)
    return MlogNullLiteral()


def _unit_boost(
    call_ctx: IntrinsicCallCtx, enabled: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _unit_boost, enabled
    )
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.BOOST, enabled)
    return MlogNullLiteral()


def _unit_shoot(
    call_ctx: IntrinsicCallCtx,
    x: MlogExpr = _MlogFillerExpr,
    y: MlogExpr = _MlogFillerExpr,
) -> MlogNullLiteral:
    if isinstance(x, MlogFillerExpr) and isinstance(y, MlogFillerExpr):
        _emit_ucontrol_subop(
            call_ctx,
            UnitControlSuboperation.TARGETP,
            MlogBuiltin("unit"),
            MlogBoolLiteral(True),
        )
    elif not isinstance(x, MlogFillerExpr) and not isinstance(
        y, MlogFillerExpr
    ):
        _emit_ucontrol_subop(
            call_ctx,
            UnitControlSuboperation.TARGET,
            x,
            y,
            MlogBoolLiteral(True),
        )
    else:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_ctx.src_loc,
            err=f"Called {get_func_names(NAMESPACE, _REV_MAP, _unit_shoot)} "
            "with one arg. Expected exactly zero or two.",
        )

    return MlogNullLiteral()


def _unit_target(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr, shoot: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_target, x, y)
    _validate_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _unit_target, shoot
    )
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.TARGET, x, y, shoot)
    return MlogNullLiteral()


def _unit_targetp(
    call_ctx: IntrinsicCallCtx, unit: MlogExpr, shoot: MlogExpr
) -> MlogNullLiteral:
    # @unit, @this, probably others
    # so im not gonna bother validating the builtin's actual value
    _validate_arg_type((MlogVar, MlogBuiltin), _unit_targetp, unit)
    _validate_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _unit_targetp, shoot
    )
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.TARGETP, unit, shoot)
    return MlogNullLiteral()


def _unit_ceasefire(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
    _emit_ucontrol_subop(
        call_ctx,
        UnitControlSuboperation.TARGET,
        MlogNumberLiteral(0),
        MlogNumberLiteral(0),
        MlogBoolLiteral(False),
    )
    return MlogNullLiteral()


# pyndustric uses 1 as default amount but this makes much more sense imo
_MlogNumberLiteral_999 = MlogNumberLiteral(9999)


def _unit_item_drop(
    call_ctx: IntrinsicCallCtx,
    to: MlogExpr,
    amount: MlogExpr = _MlogNumberLiteral_999,
) -> MlogNullLiteral:
    # '@air' is valid and of type MlogBuiltin
    _validate_arg_type((MlogVar, MlogBuiltin), _unit_item_drop, to)
    if isinstance(to, MlogBuiltin) and to.name != "air":
        # error message kinda sucks
        logger.warning(
            "Called '%s' with non-'air' %s for param 'to': '%s'. ",
            get_func_names(NAMESPACE, _REV_MAP, _unit_item_drop),
            MlogBuiltin.__name__,
            to,
        )
    _validate_arg_type(MlogNumberLiteral, _unit_item_drop, amount)
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.ITEM_DROP, to, amount
    )
    return MlogNullLiteral()


def _unit_item_take(
    call_ctx: IntrinsicCallCtx,
    from_: MlogExpr,
    item: MlogExpr,
    amount: MlogExpr = _MlogNumberLiteral_999,
) -> MlogNullLiteral:
    _validate_arg_type(MlogVar, _unit_item_take, from_)
    _validate_arg_type(MlogBuiltin, _unit_item_take, item)
    _validate_arg_type(MlogNumberLiteral, _unit_item_take, amount)
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.ITEM_TAKE, from_, item, amount
    )
    return MlogNullLiteral()


_unit_pay_drop = _argless_ucontrol_func_factory(
    UnitControlSuboperation.PAY_DROP
)


def _unit_pay_take(
    call_ctx: IntrinsicCallCtx, take_units: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(
        (MlogBoolLiteral, MlogNumberLiteral), _unit_pay_take, take_units
    )
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.PAY_TAKE, take_units)
    return MlogNullLiteral()


def _unit_pay_take_unit(call_ctx: IntrinsicCallCtx) -> MlogNullLiteral:
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.PAY_TAKE, MlogBoolLiteral(True)
    )
    return MlogNullLiteral()


def _unit_mine(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_mine, x, y)
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.MINE, x, y)
    return MlogNullLiteral()


def _unit_flag(
    call_ctx: IntrinsicCallCtx, value: MlogExpr, /
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_flag, value)
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.FLAG, value)
    return MlogNullLiteral()


_MlogNumberLiteral_0 = MlogNumberLiteral(0)
_MlogNullLiteral = MlogNullLiteral()


def _unit_build(
    call_ctx: IntrinsicCallCtx,
    x: MlogExpr,
    y: MlogExpr,
    block: MlogExpr,
    rotation: MlogExpr = _MlogNumberLiteral_0,
    config: MlogExpr = _MlogNullLiteral,
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_build, x, y, rotation)
    _validate_arg_type(MlogBuiltin, _unit_build, block)
    # idk what types are valid for 'config'
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.BUILD, x, y, block, rotation, config
    )
    return MlogNullLiteral()


def _unit_deconstruct(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
) -> MlogNullLiteral:
    _validate_arg_type(MlogNumberLiteral, _unit_deconstruct, x, y)
    _emit_ucontrol_subop(call_ctx, UnitControlSuboperation.DECONSTRUCT, x, y)
    return MlogNullLiteral()


def _unit_get_block(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr
) -> tuple[MlogExpr, ...]:
    output_expr = pad_output_expr(call_ctx.output_expr, 3)

    _validate_arg_type(MlogNumberLiteral, _unit_get_block, x, y)
    _emit_ucontrol_subop(
        call_ctx, UnitControlSuboperation.GET_BLOCK, x, y, *output_expr
    )

    # length of this is used to validate the unpacking
    return output_expr


def _unit_within(
    call_ctx: IntrinsicCallCtx, x: MlogExpr, y: MlogExpr, radius: MlogExpr
) -> MlogExpr:
    _validate_arg_type(MlogNumberLiteral, _unit_within, x, y, radius)
    _emit_ucontrol_subop(
        call_ctx,
        UnitControlSuboperation.WITHIN,
        x,
        y,
        radius,
        call_ctx.output_expr[0],
    )
    return call_ctx.output_expr[0]


# use snake case here; aliases are generated based on it
_func_map: IntrinsicFuncMap = {
    "bind": _unit_bind,
    "radar": _unit_radar,
    "locate": _unit_locate,
    # ucontrol
    "idle": _argless_ucontrol_func_factory(UnitControlSuboperation.IDLE),
    "stop": _argless_ucontrol_func_factory(UnitControlSuboperation.STOP),
    "move": _unit_move,
    "approach": _unit_approach,
    "pathfind": _unit_pathfind,
    "auto_pathfind": _argless_ucontrol_func_factory(
        UnitControlSuboperation.AUTO_PATHFIND
    ),
    "boost": _unit_boost,
    "shoot": _unit_shoot,
    "target": _unit_target,
    "targetp": _unit_targetp,
    "target_unit": _unit_targetp,  # alias
    "ceasefire": _unit_ceasefire,
    "item_drop": _unit_item_drop,
    "store": _unit_item_drop,  # alias
    "item_take": _unit_item_take,
    "fetch": _unit_item_take,  # alias
    "pay_drop": _unit_pay_drop,
    "drop": _unit_pay_drop,  # alias
    "pay_take": _unit_pay_take,
    "lift": _unit_pay_take_unit,
    "carry": _unit_pay_take_unit,  # alias
    "pay_enter": _argless_ucontrol_func_factory(
        UnitControlSuboperation.PAY_ENTER
    ),
    "mine": _unit_mine,
    "flag": _unit_flag,
    "build": _unit_build,
    "deconstruct": _unit_deconstruct,
    "get_block": _unit_get_block,
    "within": _unit_within,
    "unbind": _argless_ucontrol_func_factory(UnitControlSuboperation.UNBIND),
}

FUNC_MAP = generate_aliases(_func_map)

_rev_map: IntrinsicFuncRevMap = {}
for k, v in FUNC_MAP.items():
    _rev_map.setdefault(v, []).append(k)

_REV_MAP = _rev_map


_emit_ucontrol_subop = emit_subop_func_factory(InstructionType.UNIT_CONTROL)
_validate_arg_type = validate_arg_type_factory(NAMESPACE, _REV_MAP)
