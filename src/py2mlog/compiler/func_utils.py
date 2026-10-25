import ast
from dataclasses import dataclass
from itertools import chain
from typing import cast

from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import MlogItem
from py2mlog.mlog.mlog_expressions import LabelRef, MlogVar


@dataclass(frozen=True)
class CompiledFunc:
    location: LabelRef
    params: ast.arguments
    body: list[MlogItem]
    scoped_ret_addr: MlogVar
    scoped_ret_val: MlogVar
    scoped_arg_prefix: str


# there are probably a bunch of bugs that will surface later ¯\_(ツ)_/¯
# also confusing naming mixing 'arg' and 'param'
def resolve_args(
    call_args: list[ast.expr],
    call_kwargs: list[ast.keyword],
    src_loc: SourceLocation,
    params: ast.arguments,
) -> dict[str, ast.expr]:
    """L docstrings"""

    all_params = (
        params.posonlyargs
        + params.args
        + params.kwonlyargs
        + ([params.vararg] if params.vararg is not None else [])
        + ([params.kwarg] if params.kwarg is not None else [])
    )
    total_param_count = len(all_params)

    pos_arg_count = len(call_args)
    req_pos_only_arg_count = len(params.posonlyargs) - len(params.defaults)
    if pos_arg_count < req_pos_only_arg_count:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            src_loc,
            err=(
                "Missing required positional arg(s): "
                + ", ".join(
                    str(e)
                    for e in params.posonlyargs[
                        pos_arg_count:req_pos_only_arg_count
                    ]
                )
            ),
        )

    kw_arg_count = len(call_kwargs)
    req_kw_only_arg_count = len(params.kwonlyargs) - len(params.kw_defaults)
    if kw_arg_count < req_kw_only_arg_count:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            src_loc,
            err=(
                "Missing required keyword arg(s): "
                + ", ".join(
                    str(e)
                    for e in params.kwonlyargs[
                        kw_arg_count:req_kw_only_arg_count
                    ]
                )
            ),
        )

    supplied_arg_count = len(call_args) + len(call_kwargs)
    if supplied_arg_count > total_param_count:
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            src_loc,
            err=(
                "Excess arg(s): expected "
                f"{total_param_count - len(params.defaults) - len(params.kw_defaults)} "
                f"to {total_param_count} but got {supplied_arg_count}"
            ),
        )

    max_pos_arg_count = len(params.posonlyargs) + len(params.args)
    if len(call_args) > len(params.posonlyargs) + len(params.args):
        raise CompilerError(
            CompilerErrorType.BAD_CALL,
            src_loc,
            err=(
                f"Excess positional arg(s): "
                f"expected {req_pos_only_arg_count} to {max_pos_arg_count} "
                f"but got {len(call_args)}"
            ),
        )

    arg_list: list[ast.expr | None] = [None] * total_param_count

    for i, arg in enumerate(call_args):
        if arg_list[i] is not None:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                src_loc,
                err=(
                    "Something went VERY wrong: non-None value in arg_list"
                    f"when filling positional args. Arg_list was:\n{arg_list!r}"
                ),
            )

        arg_list[i] = arg

    param_name_to_arg_list_index_map: dict[str, int] = {
        param.arg: i
        for i, param in enumerate(
            chain(params.posonlyargs, params.args, params.kwonlyargs)
        )
    }
    for kw in call_kwargs:
        name = kw.arg
        if name not in param_name_to_arg_list_index_map:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err=f"Unexpected keyword arg '{name}'",
            )

        i = param_name_to_arg_list_index_map[name]
        if arg_list[i] is not None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err=f"Got multiple values for argument '{name}'",
            )

        arg_list[i] = kw.value

    for i, val in enumerate(
        params.defaults,
        start=len(params.posonlyargs) + len(params.args) - len(params.defaults),
    ):
        if arg_list[i] is None:
            arg_list[i] = val
    for i, val in enumerate(
        params.kw_defaults,
        start=len(params.posonlyargs)
        + len(params.args)
        + (1 if params.vararg is not None else 0),
    ):
        if val is not None and arg_list[i] is None:
            arg_list[i] = val

    req_params = params.args[
        : len(params.posonlyargs) + len(params.args) - len(params.defaults)
    ]
    for i, param in enumerate(req_params, start=len(params.posonlyargs)):
        if arg_list[i] is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err=f"Missing required argument '{param.arg}'",
            )

    if None in arg_list:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"'None' in resolved arg list '{arg_list!r}'",
        )

    casted_arg_list = cast("list[ast.expr]", arg_list)
    return {
        param.arg: val
        for param, val in zip(all_params, casted_arg_list, strict=True)
    }
