import ast

from .emitter import Emitter
from .operation_maps import UNARY_OP_MAP, BIN_OP_MAP, CMP_OP_MAP
from .error import CompilerError, CompilerErrorType, SourceLocation

from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.suboperations import OperationSuboperation, ConditionOpSuboperation
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

    def compile(self):
        for node in self._ast.body:
            self.compile_stmt(node)

    def compile_expr(self, expr: ast.expr, output_expr: MlogExpr | None = None):
        """
        Compiles an expression and returns the result's location.
        If `output_expr` is provided, the result is stored there.
        """
        result = self._compile_expr(expr, output_expr)

        if output_expr is not None and result != output_expr:
            self.emitter.emit_instruction(
                Instruction(InstructionType.SET, None, (), (output_expr, result))
            )

        return result

    def _compile_expr(self, expr: ast.expr, output_expr: MlogExpr | None) -> MlogExpr:
        """
        Compiles an expression and returns the result's location.
        If `output_expr` is not `None`, it may be used as the result's location.
        """

        def get_output_expr() -> MlogExpr:
            return output_expr if output_expr is not None else self.emitter.new_tmp()

        match expr:
            case ast.Constant():
                return self._compile_const(expr)

            case ast.Name(id=name):
                return MlogVar(name)

            case ast.BinOp(op=op, left=left, right=right):
                output_expr = get_output_expr()

                opSubop = BIN_OP_MAP.get(type(op), None)

                if opSubop is None:
                    raise self._unsupported_expr_error(expr)

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        opSubop,
                        (),
                        (
                            output_expr,
                            self.compile_expr(left),
                            self.compile_expr(right),
                        ),
                    )
                )

                return output_expr

            case ast.UnaryOp(op=op, operand=operand):
                output_expr = get_output_expr()

                factory = UNARY_OP_MAP.get(type(op), None)

                if factory is None:
                    raise self._unsupported_expr_error(expr)

                compiled_operand = self.compile_expr(operand)
                instr = factory(compiled_operand, output_expr)

                if instr is None:
                    return compiled_operand

                self.emitter.emit_instruction(instr)

                return output_expr

            case ast.BoolOp(op=op, values=values):
                output_expr = get_output_expr()

                # python BoolOp returns operand value based on short-circuiting
                if isinstance(op, ast.And):
                    prev = self.compile_expr(values[0])

                    for val in values[1:]:
                        val = self.compile_expr(val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (output_expr, prev, MlogBoolLiteral(True), val, prev),
                            )
                        )
                        prev = output_expr

                elif isinstance(op, ast.Or):
                    prev = self.compile_expr(values[0])

                    for val in values[1:]:
                        val = self.compile_expr(val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (output_expr, val, MlogBoolLiteral(True), val, prev),
                            )
                        )
                        prev = output_expr

                else:
                    raise self._unsupported_expr_error(expr)

                return output_expr

            case ast.Compare(ops=ops, left=left, comparators=comparators):

                def get_subops(
                    i: int,
                ) -> tuple[OperationSuboperation, ConditionOpSuboperation]:
                    Subops = CMP_OP_MAP.get(type(ops[i]), None)

                    if Subops is None:
                        raise self._unsupported_expr_error(expr)

                    return Subops

                output_expr = get_output_expr()

                opSubop = get_subops(0)[0]

                prev = self.compile_expr(comparators[0])

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        opSubop,
                        (),
                        (
                            output_expr,
                            self.compile_expr(left),
                            prev,
                        ),
                    )
                )

                for i, comparator in enumerate(comparators[1:], 1):
                    condOpSubop = get_subops(i)[1]

                    comparator = self.compile_expr(comparator)
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            condOpSubop,
                            (),
                            (
                                output_expr,
                                prev,
                                comparator,
                                output_expr,
                                MlogBoolLiteral(False),
                            ),
                        )
                    )
                    prev = comparator

                return output_expr

            case _:
                raise self._unsupported_expr_error(expr)

    def _compile_const(self, const: ast.Constant) -> MlogExpr:
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

    def compile_target(self, expr: ast.expr) -> MlogExpr:
        """Resolves an expression in store context and returns its location."""

        if not isinstance(getattr(expr, "ctx", None), ast.Store):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                SourceLocation.from_ast_node(expr, self._src_lines),
                err="Called compile_target() on an expression with store context",
            )

        match expr:
            case ast.Name(id=name):
                return MlogVar(name)

            case _:
                raise self._unsupported_expr_error(expr)

    def compile_stmt(self, stmt: ast.stmt) -> None:
        match stmt:
            case ast.Expr(value=value):
                self.compile_expr(value)

            case ast.Assign(targets=targets, value=value):
                value_expr = self.compile_expr(value, self.compile_target(targets[0]))

                for target in targets[1:]:
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SET,
                            None,
                            (),
                            (self.compile_target(target), value_expr),
                        )
                    )
            case ast.AugAssign(target=target, op=op, value=value):
                opSubop = BIN_OP_MAP.get(type(op), None)

                if opSubop is None:
                    raise self._unsupported_stmt_error(
                        stmt, f" with operation {opSubop}"
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        opSubop,
                        (),
                        (
                            self.compile_target(target),
                            self.compile_expr(target),
                            self.compile_expr(value),
                        ),
                    )
                )

            case ast.If(test=test, body=body, orelse=orelse):
                else_label, else_label_ref = self.emitter.new_label()

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.EQUAL,
                        (),
                        (
                            else_label_ref,
                            self.compile_expr(test),
                            MlogBoolLiteral(False),
                        ),
                    )
                )

                for stmt_ in body:
                    self.compile_stmt(stmt_)

                if orelse:
                    skip_else_label, skip_else_label_ref = self.emitter.new_label()

                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.JUMP,
                            ConditionOpSuboperation.ALWAYS,
                            (),
                            (skip_else_label_ref,),
                        )
                    )
                else:
                    skip_else_label = None

                self.emitter.emit_label(else_label)

                for stmt_ in orelse:
                    self.compile_stmt(stmt_)

                if skip_else_label is not None:
                    self.emitter.emit_label(skip_else_label)

            # TODO: implement while/else
            case ast.While(test=test, body=body, orelse=orelse):
                loop_label, loop_label_ref = self.emitter.new_label()

                self.emitter.emit_label(loop_label)

                for stmt_ in body:
                    self.compile_stmt(stmt_)

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.EQUAL,
                        (),
                        (
                            loop_label_ref,
                            self.compile_expr(test),
                            MlogBoolLiteral(True),
                        ),
                    )
                )

            # TODO: implement break statements

            case _:
                raise self._unsupported_stmt_error(stmt)

    def _unsupported_expr_error(self, expr: ast.expr) -> CompilerError:
        ctx = getattr(expr, "ctx", None)
        ctx_str = '(under context "{type(ctx).__name__}")' if ctx is not None else ""

        return CompilerError(
            CompilerErrorType.UNSUPPORTED,
            SourceLocation.from_ast_node(expr, self._src_lines),
            feature=f'Ast expression {ctx_str}"{type(expr).__name__}"',
        )

    def _unsupported_stmt_error(self, stmt: ast.stmt, info: str = "") -> CompilerError:
        return CompilerError(
            CompilerErrorType.UNSUPPORTED,
            SourceLocation.from_ast_node(stmt, self._src_lines),
            feature=f'Ast statement "{type(stmt).__name__}{info}"',
        )
