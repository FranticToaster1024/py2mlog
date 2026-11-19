from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import LabelRef


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
