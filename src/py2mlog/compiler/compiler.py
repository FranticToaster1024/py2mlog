import ast
import logging
from collections import deque
from collections.abc import Generator
from contextlib import contextmanager
from inspect import signature

from py2mlog.compiler.builtin_funcs import BUILTIN_FUNC_MAP
from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    HasPosition,
    SourceLocation,
)
from py2mlog.compiler.func_utils import (
    CompiledFunc,
    FillerAstExpr,
    resolve_args,
    resolve_args_from_signature,
)
from py2mlog.compiler.names import (
    GLOBAL_SCOPE,
    NAME_FUNC_RET_ADDR,
    NAME_FUNC_RET_VAL,
    PREFIX_FUNC_ARG,
    PREFIX_FUNC_SCOPE,
    PREFIX_LABEL,
    VAR_ERR_MSG,
)
from py2mlog.compiler.operation_maps import (
    BIN_OP_MAP,
    CMP_OP_MAP,
    NEGATED_CMP_OPS_MAP,
    UNARY_OP_MAP,
)
from py2mlog.mlog.instruction import Instruction, Label
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    LabelRef,
    MlogBoolLiteral,
    MlogBuiltin,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import (
    ConditionOpSuboperation,
    OperationSuboperation,
)

logger = logging.getLogger(__name__)


class Compiler:
    def __init__(self, src: str, ast_: ast.Module, emitter: Emitter) -> None:
        self._src = src
        self._ast = ast_

        self.emitter = emitter

        self._src_lines = src.splitlines()

        self._current_loop_break: LabelRef | None = None
        self._current_loop_continue: LabelRef | None = None

        self._scope = deque([GLOBAL_SCOPE])
        self._func_table: dict[str, CompiledFunc] = {}
        self._arg_table: dict[str, MlogVar] = {}

        self._has_assert = False
        self._assert_error_label = Label(f"{PREFIX_LABEL}_err_assert")
        self._assert_error_label_ref = LabelRef(self._assert_error_label.name)

    def compile(self):
        for node in self._ast.body:
            self.compile_stmt(node)

        self.emitter.emit_instruction(
            Instruction(InstructionType.END, None, (), ())
        )

        if self._has_assert:
            self._emit_assert_err()

        self._emit_funcs()

        # kinda dumb but it works
        while self.emitter.instructions:
            last_instr = self.emitter.instructions[-1]

            if (
                isinstance(last_instr, Instruction)
                and last_instr.type == InstructionType.END
            ):
                self.emitter.instructions.pop()

            else:
                break

    def compile_expr(self, expr: ast.expr, output_expr: MlogExpr | None = None):
        """
        Compiles an expression and returns the result's location.
        If `output_expr` is provided, the result is stored there.
        """
        result = self._compile_expr(expr, output_expr)

        if output_expr is not None and result != output_expr:
            self.emitter.emit_instruction(
                Instruction(
                    InstructionType.SET, None, (), (output_expr, result)
                )
            )

        return result

    def _compile_expr(
        self, expr: ast.expr, output_expr: MlogExpr | None
    ) -> MlogExpr:
        """
        Compiles an expression and returns the result's location.
        If `output_expr` is not `None`, it may be used as the result's location.
        """

        match expr:
            case ast.Constant():
                return self._compile_const(expr)

            case ast.Name(id=name):
                return self._arg_table.get(
                    name, MlogVar(self._get_scope_str(name))
                )

            case ast.BinOp(op=op, left=left, right=right):
                output_expr = self._get_output_expr(output_expr)

                op_subop = BIN_OP_MAP.get(type(op))

                if op_subop is None:
                    raise self._unsupported_expr_error(expr)

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        op_subop,
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
                compiled_operand = self.compile_expr(operand)

                # special cases handled separately to keep the map clean
                if isinstance(op, ast.UAdd):
                    return compiled_operand

                if isinstance(op, ast.USub) and isinstance(
                    compiled_operand, MlogNumberLiteral
                ):
                    return MlogNumberLiteral(-compiled_operand.value)

                if (
                    isinstance(op, ast.Invert)
                    and isinstance(compiled_operand, MlogNumberLiteral)
                    and isinstance(compiled_operand.value, int)
                ):
                    return MlogNumberLiteral(~compiled_operand.value)

                output_expr = self._get_output_expr(output_expr)

                factory = UNARY_OP_MAP.get(type(op))
                if factory is None:
                    raise self._unsupported_expr_error(expr)

                instr = factory(compiled_operand, output_expr)

                self.emitter.emit_instruction(instr)

                return output_expr

            case ast.BoolOp(op=op, values=values):
                output_expr = self._get_output_expr(output_expr)

                # python BoolOp returns operand value based on short-circuiting
                if isinstance(op, ast.And):
                    prev = self.compile_expr(values[0])

                    for raw_val in values[1:]:
                        val = self.compile_expr(raw_val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (
                                    output_expr,
                                    prev,
                                    MlogBoolLiteral(True),
                                    val,
                                    prev,
                                ),
                            )
                        )
                        prev = output_expr

                elif isinstance(op, ast.Or):
                    prev = self.compile_expr(values[0])

                    for raw_val in values[1:]:
                        val = self.compile_expr(raw_val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (
                                    output_expr,
                                    val,
                                    MlogBoolLiteral(True),
                                    val,
                                    prev,
                                ),
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
                    subops = CMP_OP_MAP.get(type(ops[i]))

                    if subops is None:
                        raise self._unsupported_expr_error(expr)

                    return subops

                output_expr = self._get_output_expr(output_expr)

                op_subop = get_subops(0)[0]

                prev = self.compile_expr(comparators[0])

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        op_subop,
                        (),
                        (
                            output_expr,
                            self.compile_expr(left),
                            prev,
                        ),
                    )
                )

                for i, raw_comparator in enumerate(comparators[1:], 1):
                    cond_op_subop = get_subops(i)[1]

                    comparator = self.compile_expr(raw_comparator)
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            cond_op_subop,
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

            case ast.Call():
                return self._compile_func_call(
                    expr, self._get_output_expr(output_expr)
                )

            case ast.IfExp(test=test, body=body, orelse=orelse):
                output_expr = self._get_output_expr(output_expr)

                if Compiler._is_non_emitting(
                    body
                ) and Compiler._is_non_emitting(orelse):
                    cond_op_subop, left, right = self.compile_condition(
                        test, reverse=False
                    )
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            cond_op_subop,
                            (),
                            (
                                output_expr,
                                left,
                                right,
                                self.compile_expr(body, None),
                                self.compile_expr(orelse, None),
                            ),
                        )
                    )

                    return output_expr

                else_label, else_label_ref = self.emitter.new_label()

                # reverse for else branch
                cond_op_subop, left, right = self.compile_condition(
                    test, reverse=True
                )
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        cond_op_subop,
                        (),
                        (else_label_ref, left, right),
                    )
                )

                self.compile_expr(body, output_expr)

                skip_else_label, skip_else_label_ref = self.emitter.new_label()

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.ALWAYS,
                        (),
                        (skip_else_label_ref,),
                    )
                )

                self.emitter.emit_label(else_label)

                self.compile_expr(orelse, output_expr)

                self.emitter.emit_label(skip_else_label)

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

    def _compile_func_call(
        self, func_call: ast.Call, output_expr: MlogExpr
    ) -> MlogExpr:
        """Returns the function call's output expression."""

        if not isinstance(func_call.func, ast.Name):
            raise self._unsupported_expr_error(func_call)
        func_name = func_call.func.id

        # can probably be bypassed easily
        if f"{PREFIX_FUNC_SCOPE}{func_name}" in self._scope:
            raise self._unsupported_expr_error(func_call, " with recursion")

        func_kwargs: dict[str, ast.expr] = {}
        for kwarg in func_call.keywords:
            if kwarg.arg in func_kwargs:
                raise CompilerError(
                    CompilerErrorType.SYNTAX,
                    self._get_src_loc_from_node(kwarg),
                    err="Duplicate keyword arguments",
                )

            if kwarg.arg is None:
                raise self._unsupported_expr_error(kwarg.value)

            func_kwargs[kwarg.arg] = kwarg.value

        src_location = self._get_src_loc_from_node(func_call)

        # TODO: LEGB, passing function references
        # TODO: check outer scopes
        # TODO: delayed resolution

        scope_str = self._get_scope_str(func_name)
        compiled_func = self._func_table.get(scope_str)

        if compiled_func is not None:
            return self._compile_non_inline_func_call(func_call, compiled_func)

        # TODO: non-inline builtins
        # TODO: rename BUILTIN_FUNC_MAP to show inline-only

        compile_inline_builtin = BUILTIN_FUNC_MAP.get(func_name, ...)

        if compile_inline_builtin is None:
            raise self._unsupported_expr_error(
                func_call, f": builtin {func_name}"
            )

        if compile_inline_builtin is ...:
            raise self._unsupported_expr_error(
                func_call, f": unknown function {func_name}"
            )

        arg_map = resolve_args_from_signature(
            # filler to account for first arg being output_expr
            [FillerAstExpr(), *func_call.args],
            func_kwargs,
            src_location,
            signature(compile_inline_builtin),
        )
        arg_list = list(arg_map.values())[1:]  # skip the filler
        # misleading error message ¯\_(ツ)_/¯
        compiled_arg_list = [self.compile_expr(e) for e in arg_list]

        output = compile_inline_builtin(output_expr, *compiled_arg_list)

        self.emitter.emit_items(output)

        return output_expr

    def _compile_non_inline_func_call(
        self, func_call: ast.Call, compiled_func: CompiledFunc
    ) -> MlogExpr:
        arg_list = resolve_args(
            func_call.args,
            func_call.keywords,
            self._get_src_loc_from_node(func_call),
            compiled_func.params,
        )

        for name, arg in arg_list.items():
            self.compile_expr(
                arg, MlogVar(compiled_func.scoped_arg_prefix + name)
            )

        self.emitter.emit_instruction(
            Instruction(
                InstructionType.OPERATION,
                OperationSuboperation.ADD,
                (),
                (
                    compiled_func.scoped_ret_addr,
                    MlogBuiltin("counter"),
                    MlogNumberLiteral(2),
                ),
            )
        )
        self.emitter.emit_instruction(
            Instruction(
                InstructionType.JUMP,
                ConditionOpSuboperation.ALWAYS,
                (),
                (compiled_func.location,),
            )
        )

        return compiled_func.scoped_ret_val

    def _get_output_expr(self, output_expr: MlogExpr | None) -> MlogExpr:
        return (
            output_expr if output_expr is not None else self.emitter.new_tmp()
        )

    @staticmethod
    def _is_non_emitting(expr: ast.expr) -> bool:
        if isinstance(expr, (ast.Name, ast.Constant)):
            return True
        return bool(
            isinstance(expr, ast.UnaryOp)
            and isinstance(expr.op, ast.USub)
            and isinstance(expr.operand, ast.Constant)
            and isinstance(expr.operand.value, (int, float))
        )

    def compile_target(self, expr: ast.expr) -> MlogExpr:
        """Resolves an expression in store context and returns its location."""

        if not isinstance(getattr(expr, "ctx", None), ast.Store):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                self._get_src_loc_from_node(expr),
                err="Called compile_target() on an expression with store context",
            )

        match expr:
            case ast.Name():
                # shouldn't do this because compile_expr is for non-store ctx
                # but also it compiles the same for ast.Name anyway
                # and i don't want to repeat scoping code twice
                return self.compile_expr(expr)

            case _:
                raise self._unsupported_expr_error(expr)

    def compile_condition(
        self,
        expr: ast.expr,
        *,
        reverse: bool,
        output_expr: MlogExpr | None = None,
    ) -> tuple[ConditionOpSuboperation, MlogExpr, MlogExpr]:
        """
        Compiles a condition for ConditionOpSuboperation.
        If given expression is Compare, it is not fully compiled.
        Instead, suboperation and operands are returned.
        If `reverse` is `True`, the logical negation of the condition is returned.
        """
        if not isinstance(expr, ast.Compare) or len(expr.ops) > 1:
            return (
                ConditionOpSuboperation.EQUAL,
                self.compile_expr(expr, output_expr),
                MlogBoolLiteral(not reverse),
            )

        op = type(expr.ops[0])

        if reverse:
            reverse_op = NEGATED_CMP_OPS_MAP.get(op)
            if reverse_op is None or reverse_op not in CMP_OP_MAP:
                logger.warning(
                    "Absent logical negation of %s in NEGATED_CMP_OPS_MAP, "
                    "or its logical negation %s was absent from CMP_OP_MAP.",
                    str(op),
                    str(reverse_op),
                )
                logger.warning("Check operation_maps.py!")
                return (
                    ConditionOpSuboperation.NOT_EQUAL,
                    self.compile_expr(expr, output_expr),
                    MlogBoolLiteral(not reverse),
                )

            op = reverse_op

        subops = CMP_OP_MAP.get(op)
        if subops is None:
            raise self._unsupported_expr_error(expr)

        cond_op_subop = subops[1]

        return (
            cond_op_subop,
            self.compile_expr(expr.left),
            self.compile_expr(expr.comparators[0]),
        )

    def compile_stmt(self, stmt: ast.stmt) -> None:
        match stmt:
            case ast.Expr(value=value):
                self.compile_expr(value)

            case ast.Assign(targets=targets, value=value):
                value_expr = self.compile_expr(
                    value, self.compile_target(targets[0])
                )

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
                op_subop = BIN_OP_MAP.get(type(op))

                if op_subop is None:
                    raise self._unsupported_stmt_error(
                        stmt, f" with operation {op_subop}"
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        op_subop,
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

                # reverse since this jump is for `else` branch
                cond_op_subop, left, right = self.compile_condition(
                    test, reverse=True
                )
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        cond_op_subop,
                        (),
                        (else_label_ref, left, right),
                    )
                )

                for stmt_ in body:
                    self.compile_stmt(stmt_)

                if orelse:
                    skip_else_label, skip_else_label_ref = (
                        self.emitter.new_label()
                    )

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
                break_label, break_label_ref = self.emitter.new_label()

                # initial check to make it a proper while instead of do-while

                cond_op_subop, left, right = self.compile_condition(
                    test, reverse=True
                )
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        cond_op_subop,
                        (),
                        (break_label_ref, left, right),
                    )
                )

                self.emitter.emit_label(loop_label)

                with self._loop_context(break_label_ref, loop_label_ref) as _:
                    for stmt_ in body:
                        self.compile_stmt(stmt_)

                # actual loop jump

                cond_op_subop, left, right = self.compile_condition(
                    test, reverse=False
                )
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        cond_op_subop,
                        (),
                        (loop_label_ref, left, right),
                    )
                )

                self.emitter.emit_label(break_label)

            case ast.Break():
                if self._current_loop_break is None:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(stmt),
                        err="'break' outside loop",
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.ALWAYS,
                        (),
                        (self._current_loop_break,),
                    )
                )

            case ast.Continue():
                if self._current_loop_continue is None:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(stmt),
                        err="'continue' outside loop",
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.ALWAYS,
                        (),
                        (self._current_loop_continue,),
                    )
                )

            case ast.Assert(test=test, msg=msg):
                self._has_assert = True

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.SET,
                        None,
                        (),
                        (
                            VAR_ERR_MSG,
                            (
                                MlogStringLiteral("")
                                if msg is None
                                else self.compile_expr(msg)
                            ),
                        ),
                    )
                )

                cond_op_subop, left, right = self.compile_condition(
                    test, reverse=True
                )
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        cond_op_subop,
                        (),
                        (self._assert_error_label_ref, left, right),
                    )
                )

            case ast.FunctionDef():
                self._compile_func_def(stmt)

            case ast.Return(value=value):
                self._compile_return(value)

            case ast.Pass():
                pass  # haha funny

            case _:
                raise self._unsupported_stmt_error(stmt)

    def _compile_func_def(self, func_def: ast.FunctionDef) -> None:
        # TODO: decorators
        if func_def.decorator_list:
            raise self._unsupported_stmt_error(
                func_def, ": function decorators"
            )

        with self._func_context(func_def) as scope_str:
            # TODO: function inlining
            # TODO: LEGB, global & nonlocal keywords
            # TODO: use line numbers over labels so they can be passed around
            call_label, call_label_ref = self.emitter.new_label()
            self.emitter.emit_label(call_label)

            for stmt in func_def.body:
                self.compile_stmt(stmt)
                if isinstance(stmt, ast.Return):
                    break

            else:
                self._compile_return(None)

            self._func_table[scope_str] = CompiledFunc(
                call_label_ref,
                func_def.args,
                self.emitter.instructions,
                MlogVar(self._get_scope_str(NAME_FUNC_RET_ADDR)),
                MlogVar(self._get_scope_str(NAME_FUNC_RET_VAL)),
                self._get_scope_str(PREFIX_FUNC_ARG),
            )

    def _compile_return(self, value: ast.expr | None) -> None:
        self.compile_expr(
            value if value is not None else ast.Constant(None),
            MlogVar(self._get_scope_str(NAME_FUNC_RET_VAL)),
        )

        self.emitter.emit_instruction(
            Instruction(
                InstructionType.SET,
                None,
                (),
                (
                    MlogBuiltin("counter"),
                    MlogVar(self._get_scope_str(NAME_FUNC_RET_ADDR)),
                ),
            )
        )

    def _emit_funcs(self):
        for func in self._func_table.values():
            self.emitter.emit_items(func.body)

        self.emitter.emit_instruction(
            Instruction(InstructionType.END, None, (), ())
        )

    def _emit_assert_err(self) -> None:
        self.emitter.emit_label(self._assert_error_label)
        self.emitter.emit_instruction(
            Instruction(
                InstructionType.PRINT,
                None,
                (),
                (MlogStringLiteral("[red]AssertionError: {0}.[]"),),
            )
        )
        self.emitter.emit_instruction(
            Instruction(InstructionType.FORMAT, None, (), (VAR_ERR_MSG,))
        )
        self.emitter.emit_instruction(
            Instruction(InstructionType.STOP, None, (), ())
        )

    @contextmanager
    def _loop_context(
        self, break_ref: LabelRef | None, continue_ref: LabelRef | None
    ) -> Generator[None, None, None]:
        prev_break = self._current_loop_break
        prev_continue = self._current_loop_continue

        self._current_loop_break = break_ref
        self._current_loop_continue = continue_ref

        yield

        self._current_loop_break = prev_break
        self._current_loop_continue = prev_continue

    @contextmanager
    def _func_context(
        self, func_def: ast.FunctionDef
    ) -> Generator[str, None, None]:
        """
        Manages the current scope, emitter, and arg table.
        Yields the current full scope string.
        """
        outside_scope = self._get_scope_str(func_def.name)
        self._scope.append(f"{PREFIX_FUNC_SCOPE}{func_def.name}")

        func_args = func_def.args
        if func_args.vararg is not None:
            raise CompilerError(
                CompilerErrorType.UNSUPPORTED,
                self._get_src_loc_from_node(func_args.vararg),
                feature="arbitrary arguments (*args)",
            )

        if func_args.kwarg is not None:
            raise CompilerError(
                CompilerErrorType.UNSUPPORTED,
                self._get_src_loc_from_node(func_args.kwarg),
                feature="arbitrary keyword arguments (**kwargs)",
            )

        all_args = (
            func_args.posonlyargs
            + func_args.args
            + func_args.kwonlyargs
            + ([func_args.vararg] if func_args.vararg is not None else [])
            + ([func_args.kwarg] if func_args.kwarg is not None else [])
        )
        for arg in all_args:
            arg_name = self._get_scope_str(PREFIX_FUNC_ARG + arg.arg)
            self._arg_table[arg.arg] = MlogVar(arg_name)

        # i don't like swapping emitter but whatever
        old_instructions = self.emitter.instructions
        self.emitter.instructions = []

        with self._loop_context(None, None):
            yield outside_scope

        self._scope.pop()
        self._arg_table = {}
        self.emitter.instructions = old_instructions

    def _get_scope_str(self, scope_name: str = "") -> str:
        _, *local_ = self._scope
        return ".".join(  # maybe use '::'?
            [*(self._scope if self._scope[0] else local_), scope_name]
        )

    def _unsupported_expr_error(
        self, expr: ast.expr, info: str = ""
    ) -> CompilerError:
        ctx = getattr(expr, "ctx", None)
        ctx_str = (
            '(under context "{type(ctx).__name__}")' if ctx is not None else ""
        )

        return CompilerError(
            CompilerErrorType.UNSUPPORTED,
            self._get_src_loc_from_node(expr),
            feature=f'Ast expression {ctx_str}"{type(expr).__name__}"{info}',
        )

    def _unsupported_stmt_error(
        self, stmt: ast.stmt, info: str = ""
    ) -> CompilerError:
        return CompilerError(
            CompilerErrorType.UNSUPPORTED,
            self._get_src_loc_from_node(stmt),
            feature=f'Ast statement "{type(stmt).__name__}"{info}',
        )

    def _get_src_loc_from_node(self, node: HasPosition):
        return SourceLocation.from_ast_node(node, self._src_lines)
