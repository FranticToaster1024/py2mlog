import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Concatenate, Protocol

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import SourceLocation
from py2mlog.compiler.mimex_utils import snake_to_camel
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import MlogExpr, MlogVar
from py2mlog.mlog.selectable_params import SelectableParam
from py2mlog.mlog.suboperations import Suboperation

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntrinsicCallCtx:
    output_expr: tuple[MlogExpr, ...]
    src_loc: SourceLocation
    emitter: Emitter


type IntrinsicFunc = Callable[
    Concatenate[IntrinsicCallCtx, ...], MlogExpr | tuple[MlogExpr, ...]
]
type IntrinsicFuncMap = dict[str, IntrinsicFunc | None]
type IntrinsicFuncRevMap = dict[IntrinsicFunc | None, list[str]]


def get_func_names(
    namespace_name: str, rev_map: IntrinsicFuncRevMap, func: IntrinsicFunc
) -> str:
    func_names = "/".join(rev_map.get(func, ("[func not in _rev_map]",)))

    return f"{namespace_name}.{func_names}"


class _EmitSubopFunc(Protocol):
    def __call__(
        self,
        call_ctx: IntrinsicCallCtx,
        subop: Suboperation,
        *args: MlogExpr,
        sel_args: tuple[SelectableParam, ...] = (),
    ) -> None: ...


def emit_subop_func_factory(instr_type: InstructionType) -> _EmitSubopFunc:
    def _emit_subop_func(
        call_ctx: IntrinsicCallCtx,
        subop: Suboperation,
        *args: MlogExpr,
        sel_args: tuple[SelectableParam, ...] = (),
    ) -> None:
        call_ctx.emitter.emit_instruction(
            Instruction(instr_type, subop, sel_args, args)
        )

    return _emit_subop_func


class _ValidateArgTypeFunc(Protocol):
    def __call__(
        self,
        type_: type[MlogExpr] | tuple[type[MlogExpr], ...],
        func: IntrinsicFunc,
        *args: MlogExpr,
    ) -> None: ...


# the param types in intrinsic func defs aren't actually enforced
# they are just used for stub generation
# so this is needed for runtime
def validate_arg_type_factory(
    namespace_name: str, rev_map: IntrinsicFuncRevMap, _logger: logging.Logger
) -> _ValidateArgTypeFunc:
    # this might like mess up the logger location but ¯\_(ツ)_/¯
    def _validate_arg_type(
        type_: type[MlogExpr] | tuple[type[MlogExpr], ...],
        func: IntrinsicFunc,
        *args: MlogExpr,
    ) -> None:
        """Accepts MlogVar along with given type(s)."""
        if not type_:
            _logger.warning(
                "(Internal) Called _validate_arg_type with empty tuple as type."
            )
        types = type_ if isinstance(type_, tuple) else (type_,)

        for arg in args:
            if not isinstance(arg, (*types, MlogVar)):
                _logger.warning(
                    "Called '%s' with arg '%s'. Expected type(s): %s%s.",
                    get_func_names(namespace_name, rev_map, func),
                    arg,
                    ", ".join(type(t).__name__ for t in types),
                    ", 'MlogVar'" if MlogVar not in types else "",
                )

    return _validate_arg_type


def generate_alias(s: str) -> set[str]:
    return {s, snake_to_camel(s), s.replace("_", "").lower()}


def generate_aliases(m: IntrinsicFuncMap) -> IntrinsicFuncMap:
    return {
        alias: func
        for name, func in m.items()
        for alias in generate_alias(name)
    }


def pad_output_expr(output_expr: tuple[MlogExpr, ...], n: int):
    return (output_expr + (MlogVar("_"),) * n)[:n]
