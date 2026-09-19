import ast

from collections.abc import Callable

from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.suboperations import OperationSuboperation
from py2mlog.mlog.mlog_expressions import (
    MlogExpr,
    MlogNumberLiteral,
    MlogVar,
    MlogBoolLiteral,
)

UNARY_OP_MAP: dict[
    type[ast.unaryop], Callable[[MlogVar, MlogExpr], Instruction | None]
] = {
    ast.UAdd: lambda *_: None,
    ast.USub: lambda in_expr, out_expr: Instruction(
        InstructionType.OPERATION,
        OperationSuboperation.SUB,
        (),
        (out_expr, MlogNumberLiteral(0), in_expr),
    ),
    ast.Not: lambda in_expr, out_expr: Instruction(
        InstructionType.OPERATION,
        OperationSuboperation.NOT_EQUAL,
        (),
        (out_expr, in_expr, MlogBoolLiteral(True)),
    ),
    ast.Invert: lambda in_expr, out_expr: Instruction(
        InstructionType.OPERATION,
        OperationSuboperation.BITWISE_NOT,
        (),
        (out_expr, in_expr),
    ),
}

BIN_OP_MAP: dict[type[ast.operator], OperationSuboperation] = {
    ast.Add: OperationSuboperation.ADD,
    ast.Sub: OperationSuboperation.SUB,
    ast.Mult: OperationSuboperation.MUL,
    ast.Div: OperationSuboperation.DIV,
    ast.FloorDiv: OperationSuboperation.INTEGER_DIV,
    ast.Mod: OperationSuboperation.TRUE_MOD,
    ast.Pow: OperationSuboperation.POW,
    ast.BitAnd: OperationSuboperation.BITWISE_AND,
    ast.BitOr: OperationSuboperation.BITWISE_OR,
    ast.BitXor: OperationSuboperation.BITWISE_XOR,
    ast.LShift: OperationSuboperation.BITSHIFT_LEFT,
    ast.RShift: OperationSuboperation.BITSHIFT_RIGHT,
}
