from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog import codegen
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    LabelRef,
    MlogArg,
    MlogBoolLiteral,
    MlogBuiltin,
    MlogColorLiteral,
    MlogStringLiteral,
    MlogVar,
)


def mlog_expr_as_print_str(e: MlogArg) -> str | None:
    if isinstance(e, LabelRef):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Called 'mlog_expr_as_print_str' with 'LabelRef': '{e}'",
        )

    # TODO: do something about the color literals
    if isinstance(e, (MlogVar, MlogColorLiteral)):
        return None
    if isinstance(e, MlogBoolLiteral):
        return str(int(e.value))
    if isinstance(e, MlogBuiltin):
        return e.name
    # generate str instead of 'str'
    if isinstance(e, MlogStringLiteral):
        return e.value
    return codegen.arg_to_str(e)


def get_jump_target_name(instr: Instruction) -> str:
    if instr.type != InstructionType.JUMP:
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err="Called '_get_jump_target_name' with non-jump instruction.",
        )

    if not isinstance(instr.args[0], LabelRef):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Unlabelled jump '{instr}'. "
            f"First arg not instance of '{LabelRef.__name__}'",
        )

    return instr.args[0].name
