from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from itertools import chain
from typing import Any, cast

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import LabelRef, MlogExpr, MlogNumberLiteral
from py2mlog.mlog.suboperations import OperationSuboperation


@dataclass(frozen=True)
class _BuiltinCallArgs:
    emitter: Emitter
    output_expr: MlogExpr
    func_args: list[MlogExpr]
    func_kwargs: dict[str, MlogExpr]
    src_loc: SourceLocation


def _builtin_wrapper(
    func: Callable[[_BuiltinCallArgs], None],
) -> Callable[
    [
        Emitter,
        MlogExpr,
        list[MlogExpr],
        dict[str, MlogExpr],
        SourceLocation,
    ],
    MlogExpr,
]:
    @wraps(func)
    def wrapper(
        emitter: Emitter,
        output_expr: MlogExpr,
        func_args: list[MlogExpr],
        func_kwargs: dict[str, MlogExpr],
        src_loc: SourceLocation,
    ) -> MlogExpr:
        func(
            _BuiltinCallArgs(
                emitter, output_expr, func_args, func_kwargs, src_loc
            )
        )
        return output_expr

    return wrapper


# TODO: REWRITE (stub parsing maybe?)
def _resolve_args(
    call_args: _BuiltinCallArgs,
    *,
    param_str: str,
    param_defaults: dict[str, MlogExpr],
) -> list[MlogExpr]:
    """
    Takes param shape as a string similar to
    python function signatures without brackets.
    e.g.

    ```
    x, y, /, z, *, a, b
    ```

    The actual value of default parameters is supplied through
    `param_defaults`, in the form dict[param_name, default_mlog_expression].
    e.g.

    ```
    {"b": MlogNullLiteral()}
    ```
    """

    params = [s.strip() for s in param_str.split(",")]

    _params_set = set(params)

    for name in param_defaults:
        if name not in _params_set:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Unexpected default keyword argument {name}",
            )

    if len(params) != len(_params_set):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Duplicate paramter or symbol in param shape {param_str}",
        )

    if (
        "/" in params
        and "*" in params
        and params.index("*") < params.index("/")
    ):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"'*' before '/' in param shape {param_str}",
        )

    default_start_idx = len(params)
    for i, param in enumerate(params):
        if default_start_idx == len(params):
            if param in param_defaults:
                default_start_idx = i

        elif param not in param_defaults:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Required parameter after optional parameter in param shape {param_str}",
            )

    combined_param_count = len(params)

    # req for required, opt for optional
    req_pos_only_params = []
    opt_pos_only_params = []
    if "/" in params:
        slash_index = params.index("/")
        req_pos_only_params = params[: min(slash_index, default_start_idx + 1)]
        opt_pos_only_params = params[
            min(slash_index + 1, default_start_idx) : slash_index
        ]

        combined_param_count -= 1

    pos_arg_count = len(call_args.func_args)
    if pos_arg_count < len(req_pos_only_params):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_args.src_loc,
            err=f"Missing required positional arg(s) {', '.join(req_pos_only_params[pos_arg_count:])}",
        )

    req_kw_only_params = []
    opt_kw_only_params = []
    if "*" in params:
        asterisk_index = params.index("*")
        req_kw_only_params = params[asterisk_index + 1 : default_start_idx]
        opt_kw_only_params = params[
            max(asterisk_index + 1, default_start_idx) :
        ]

        combined_param_count -= 1

    kw_arg_count = len(call_args.func_kwargs)
    if kw_arg_count < len(req_kw_only_params):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_args.src_loc,
            err=f"Missing required keyword arg(s) {', '.join(e[0] for e in req_kw_only_params[kw_arg_count:])}",
        )

    supplied_arg_count = len(call_args.func_args) + len(call_args.func_kwargs)
    if combined_param_count < supplied_arg_count:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_args.src_loc,
            err=(
                "Excess arg(s): expected "
                f"{combined_param_count - len([e for e in params if e in param_defaults])} "
                f"to {combined_param_count} but got {supplied_arg_count}"
            ),
        )

    aft_slash_index = params.index("/") + 1 if "/" in params else None
    asterisk_index = params.index("*") if "*" in params else len(params)

    # these *must* be usable as both pos and kw
    # not a combination of pos_only and kw_only
    req_pos_or_kw_params = params[
        aft_slash_index : min(asterisk_index, default_start_idx)
    ]
    opt_pos_or_kw_params = params[
        min(asterisk_index + 1, default_start_idx) : asterisk_index
    ]

    def _find_arg_segment(
        index: int, segments: tuple[list[Any], ...]
    ) -> tuple[int, int] | None:
        """Returns `None` if index >= total length of all segments.
        Otherwise, returns (index_of_segment, index_in_segment)"""
        for i, segment in enumerate(segments):
            if index < len(segment):
                return i, index
            index -= len(segment)
        return None

    arg_list: list[MlogExpr | None] = [None] * combined_param_count

    for i, arg in enumerate(call_args.func_args):
        arg_list[i] = arg

    current_index = len(call_args.func_args) - 1

    pos_param_segments = (
        req_pos_only_params,
        opt_pos_only_params,
        req_pos_or_kw_params,
        opt_pos_or_kw_params,
    )
    segment = _find_arg_segment(
        current_index,
        pos_param_segments,
    )

    if segment is None:
        expected_min = len(req_pos_only_params)
        expected_max = (
            expected_min
            + len(opt_pos_only_params)
            + len(req_pos_or_kw_params)
            + len(opt_pos_or_kw_params)
        )
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            call_args.src_loc,
            err=(
                f"Excess positional arg(s): "
                f"expected {expected_min} to {expected_max} "
                f"but got {current_index + 1}"
            ),
        )

    index_of_segment, index_in_segment = segment

    # missing pos args already handled earlier

    # opt_pos_only_params
    if index_of_segment == 1:
        for arg in opt_pos_only_params[index_in_segment + 1 :]:
            current_index += 1
            arg_list[current_index] = param_defaults[arg]

    param_name_arg_list_index_map: dict[str, int] = {}
    for i, name in enumerate(
        chain(
            req_pos_only_params,
            opt_pos_only_params,
            req_pos_or_kw_params,
            opt_pos_or_kw_params,
            req_kw_only_params,
            opt_kw_only_params,
        )
    ):
        if name in "/.":
            continue
        param_name_arg_list_index_map[name] = i

    for name, val in call_args.func_kwargs.items():
        if name not in param_name_arg_list_index_map:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_args.src_loc,
                err=f"Unexpected keyword arg '{name}'",
            )

        i = param_name_arg_list_index_map[name]
        if arg_list[i] is not None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_args.src_loc,
                err=f"Got multiple values for argument '{name}'",
            )

        arg_list[i] = val

    for name, val in param_defaults.items():
        i = param_name_arg_list_index_map[name]
        if arg_list[i] is None:
            arg_list[i] = val

    req_pos_or_kw_param_start_idx = (
        len(req_pos_only_params) + len(opt_pos_only_params) + 1
    )

    for i, arg in enumerate(req_pos_or_kw_params):
        arg_list_index = req_pos_or_kw_param_start_idx + i
        if arg_list[arg_list_index] is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                call_args.src_loc,
                err=f"Missing required positional or keyword argument '{arg}'",
            )

    if None in arg_list:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"'None' in resolved arg list '{arg_list!r}'",
        )

    return cast("list[MlogExpr]", arg_list)


@_builtin_wrapper
def _builtin_abs(call_args: _BuiltinCallArgs) -> None:
    arg_list = _resolve_args(call_args, param_str="x, /", param_defaults={})
    call_args.emitter.emit_instruction(
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ABS,
            (),
            (call_args.output_expr, arg_list[0]),
        )
    )
    # output expr returned automatically through wrapper


@_builtin_wrapper
def _builtin_ord(call_args: _BuiltinCallArgs) -> None:
    arg_list = _resolve_args(
        call_args, param_str="character, /", param_defaults={}
    )
    call_args.emitter.emit_instruction(
        Instruction(
            InstructionType.READ,
            None,
            (),
            (call_args.output_expr, arg_list[0], MlogNumberLiteral(0)),
        )
    )


BUILTIN_FUNC_MAP: dict[
    str,
    Callable[
        [
            Emitter,
            MlogExpr,
            list[MlogExpr],
            dict[str, MlogExpr],
            SourceLocation,
        ],
        MlogExpr | LabelRef,
    ]
    | None,
] = {
    "abs": _builtin_abs,
    "ord": _builtin_ord,
    "exec": None,
    "eval": None,
}
