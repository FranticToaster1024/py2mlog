import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Concatenate, Protocol

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    SourceLocation,
)
from py2mlog.mlog.instruction import Instruction, InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogExpr,
    MlogVar,
)
from py2mlog.mlog.suboperations import (
    Suboperation,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntrinsicCallCtx:
    output_expr: MlogExpr
    src_loc: SourceLocation
    emitter: Emitter


type IntrinsicFunc = Callable[Concatenate[IntrinsicCallCtx, ...], MlogExpr]
type IntrinsicFuncMap = dict[str, IntrinsicFunc | None]
type IntrinsicFuncRevMap = dict[IntrinsicFunc | None, list[str]]


def get_func_names(
    namespace: str, rev_map: IntrinsicFuncRevMap, func: IntrinsicFunc
) -> str:
    func_names = "/".join(rev_map.get(func, ("[func not in _rev_map]",)))

    return f"{namespace}.{func_names}"


class _EmitSubopFunc(Protocol):
    def __call__(
        self, call_ctx: IntrinsicCallCtx, subop: Suboperation, *args: MlogExpr
    ) -> None: ...


def emit_subop_func_factory(instr_type: InstructionType) -> _EmitSubopFunc:
    def _emit_subop_func(
        call_ctx: IntrinsicCallCtx, subop: Suboperation, *args: MlogExpr
    ) -> None:
        call_ctx.emitter.emit_instruction(
            Instruction(instr_type, subop, (), args)
        )

    return _emit_subop_func


class _ValidateArgTypeFunc(Protocol):
    def __call__(
        self, type_: type[MlogExpr], func: IntrinsicFunc, *args: MlogExpr
    ) -> None: ...


def validate_arg_type_factory(
    namespace: str, rev_map: IntrinsicFuncRevMap
) -> _ValidateArgTypeFunc:
    # this might like mess up the logger location but ¯\_(ツ)_/¯
    def _validate_arg_type(
        type_: type[MlogExpr], func: IntrinsicFunc, *args: MlogExpr
    ) -> None:
        """Accepts MlogVar along with given type."""
        for arg in args:
            if not isinstance(arg, (type_, MlogVar)):
                logger.warning(
                    "Called '%s' with arg '%s'. Expected type: '%s'%s.",
                    get_func_names(namespace, rev_map, func),
                    arg,
                    type(type_).__name__,
                    " or 'MlogVar'" if type_ is not MlogVar else "",
                )

    return _validate_arg_type
