import ast

from .emitter import Emitter
from .operation_map import UNARY_OP_MAP, BIN_OP_MAP
from .error import CompilerError, CompilerErrorType, SourceLocation

from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogExpr,
    MlogBoolLiteral,
    MlogBuiltin,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)


class Compiler:
    def __init__(self, src: str, ast_: ast.Module, emitter: Emitter) -> None:
        self._src = src
        self._ast = ast_

        self.emitter = emitter

        self._src_lines = src.splitlines()

    def compile_const(self, const: ast.Constant) -> MlogExpr:
        match const.value:
            case None:
                return MlogNullLiteral()

            case bool(val):
                return MlogBoolLiteral(val)

            case int() | float() as val:
                return MlogNumberLiteral(val)

            case str(val):
                return MlogStringLiteral(val)

            case _:
                raise self._unsupported_expr_error(const)

    def compile_expr(self, expr: ast.expr) -> MlogExpr:
        match expr:
            case ast.Constant():
                return self.compile_const(expr)

            case ast.Name(id=name):
                return MlogVar(name)

            case ast.BinOp(op=op):
                opSubop = BIN_OP_MAP.get(type(op), None)

                if opSubop is None:
                    raise self._unsupported_expr_error(expr)

                output_expr = self.emitter.new_tmp()
                instr = Instruction(
                    InstructionType.OPERATION,
                    opSubop,
                    (),
                    (
                        output_expr,
                        self.compile_expr(expr.left),
                        self.compile_expr(expr.right),
                    ),
                )

                if not self.emitter.emit_instruction(instr):
                    raise self._invalid_mlog_instr_internal_error(instr)

                return output_expr

            case _:
                raise self._unsupported_expr_error(expr)

    def _unsupported_expr_error(self, expr: ast.expr) -> CompilerError:
        return CompilerError(
            CompilerErrorType.UNSUPPORTED,
            SourceLocation.from_ast_node(expr, self._src_lines),
            feature=f'Ast expression "{type(expr).__name__}"',
        )

    def _invalid_mlog_instr_internal_error(self, instr: Instruction) -> CompilerError:
        return CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err=f"Attempted to create invalid mlog instruction:\n{instr!r}",
        )
