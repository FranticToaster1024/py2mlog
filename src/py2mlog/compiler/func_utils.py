import ast
import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from inspect import Parameter

from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import MlogItem
from py2mlog.mlog.mlog_expressions import LabelRef, MlogVar


class FillerAstExpr(ast.expr):
    pass


@dataclass(frozen=True)
class CompiledFunc:
    location: LabelRef
    params: ast.arguments
    body: list[MlogItem]
    scoped_ret_addr: MlogVar
    scoped_ret_val: MlogVar
    scoped_arg_prefix: str


# more confusing mixing of 'arg' and 'param'
def resolve_args(
    call_args: list[ast.expr],
    call_kwargs: list[ast.keyword],
    src_loc: SourceLocation,
    args: ast.arguments,
) -> Mapping[str, ast.expr]:
    """L docstrings"""

    params: list[Parameter] = []

    positional = args.posonlyargs + args.args
    defaults = [Parameter.empty] * (
        len(positional) - len(args.defaults)
    ) + args.defaults

    for i, (arg, default) in enumerate(zip(positional, defaults, strict=True)):
        kind = (
            Parameter.POSITIONAL_ONLY
            if i < len(args.posonlyargs)
            else Parameter.POSITIONAL_OR_KEYWORD
        )

        params.append(Parameter(arg.arg, kind, default=default))

    if args.vararg:
        raise CompilerError(
            CompilerErrorType.UNSUPPORTED, src_loc, feature="var args (*args)"
        )
        # params.append(Parameter(args.vararg.arg, Parameter.VAR_POSITIONAL))

    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        params.append(
            Parameter(
                arg.arg,
                Parameter.KEYWORD_ONLY,
                default=Parameter.empty if default is None else default,
            )
        )

    if args.kwarg:
        raise CompilerError(
            CompilerErrorType.UNSUPPORTED,
            src_loc,
            feature="var kwargs (**kwargs)",
        )
        # params.append(Parameter(args.kwarg.arg, Parameter.VAR_KEYWORD))

    signature = inspect.Signature(params)
    return resolve_args_from_signature(
        call_args,
        {kw.arg: kw.value for kw in call_kwargs if kw.arg},
        src_loc,
        signature,
    )


def resolve_args_from_signature(
    call_args: list[ast.expr],
    call_kwargs: dict[str, ast.expr],
    src_loc: SourceLocation,
    signature: inspect.Signature,
) -> Mapping[str, ast.expr]:
    try:
        bound_args = signature.bind(*call_args, **call_kwargs)
    except TypeError as e:
        raise CompilerError(
            CompilerErrorType.BAD_CALL, src_loc, err=e
        ) from None
    bound_args.apply_defaults()

    return bound_args.arguments
