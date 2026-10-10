from collections.abc import Callable

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import LabelRef, MlogExpr
from py2mlog.mlog.suboperations import OperationSuboperation


def builtin_abs(
    emitter: Emitter,
    output_expr: MlogExpr,
    func_args: list[MlogExpr],
    func_kwargs: dict[str, MlogExpr],
    src_loc: SourceLocation,
) -> MlogExpr:
    if len(func_args) != 1 or func_kwargs:
        raise CompilerError(CompilerErrorType.BAD_BUILTIN_CALL, src_loc)

    emitter.emit_instruction(
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ABS,
            (),
            (output_expr, func_args[0]),
        )
    )
    return output_expr


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
    "abs": builtin_abs,
    "exec": None,
    "eval": None,
}
