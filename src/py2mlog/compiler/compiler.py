import ast
import logging
from collections import deque
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from inspect import signature

from py2mlog import intrinsics
from py2mlog.compiler import config
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
    InlineFuncDef,
    ResolvedKwargs,
    ResolvedPosArgs,
    resolve_args,
    resolve_args_from_signature,
)
from py2mlog.compiler.mimex_utils import snake_to_kebab
from py2mlog.compiler.mlog_builtins import (
    ALIGN_MAP,
    ENV_ATTR_MAP,
    MLOG_BUILTIN_NAMESPACES,
    UNIT_TYPE_MAP,
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
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicCallCtx,
    IntrinsicFunc,
)
from py2mlog.mlog.instruction import Instruction, Label
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    LabelRef,
    MlogBoolLiteral,
    MlogBuiltin,
    MlogExpr,
    MlogFillerExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.suboperations import (
    ConditionOpSuboperation,
    OperationSuboperation,
    UnitControlSuboperation,
)
from py2mlog.optimizer.optimizer import _remove_useless_end  # pyright: ignore[reportPrivateUsage]

logger = logging.getLogger(__name__)


class Compiler:
    def __init__(self, src: str, ast_: ast.Module, emitter: Emitter) -> None:
        self._src = src
        self._ast = ast_

        self.emitter = emitter

        self._src_lines = src.splitlines()

        self._in_loop: bool = False
        # (sometimes) generated on-demand by break/continue statements
        self._current_loop_break: Label | None = None
        self._current_loop_break_ref: LabelRef | None = None
        self._current_loop_continue: Label | None = None
        self._current_loop_continue_ref: LabelRef | None = None

        self._scope = deque([GLOBAL_SCOPE])
        # misleading name ¯\_(ツ)_/¯
        self._func_table: dict[str, CompiledFunc] = {}
        self._arg_table: dict[str, MlogExpr] = {}
        self._inline_func_ret_target: MlogExpr | None = None
        self._inline_func_table: dict[str, InlineFuncDef] = {}
        self._filling_inline_arg_table: bool = False

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

        # its actually kinda a correctness issue
        # because labels on last line aren't properly processed
        # and also im just too lazy to add 'end' to every testcase
        self.emitter.instructions = list(
            _remove_useless_end(tuple(self.emitter.instructions))
        )

    def compile_expr(
        self,
        expr: ast.expr,
        output_expr: MlogExpr | None = None,
        *,
        suppress_ctx_check: bool = False,
    ) -> MlogExpr:
        """
        Compiles an expression and returns the result's location.
        If `output_expr` is provided, the result is stored there.
        """
        if not suppress_ctx_check and isinstance(
            getattr(expr, "ctx", None), ast.Store
        ):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                self._get_src_loc_from_node(expr),
                err=" attempted to call '_compile_expr' with 'ast.Store()' context",
            )

        result = self._compile_expr(expr, output_expr)

        return self._set_expr_output(result, output_expr)

    def _set_expr_output(
        self, expr: MlogExpr, output_expr: MlogExpr | None
    ) -> MlogExpr:
        if output_expr is not None and expr != output_expr:
            self.emitter.emit_instruction(
                Instruction(InstructionType.SET, None, (), (output_expr, expr))
            )
            return output_expr

        return expr

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
                    name,
                    MlogVar(name)
                    if self._filling_inline_arg_table
                    else MlogVar(self._get_scope_str(name)),
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
                return self.compile_func_call(
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

            case ast.Attribute(value=value, attr=attr):
                if isinstance(value, ast.Name):
                    match value.id:
                        case "Env":
                            builtin = ENV_ATTR_MAP.get(attr)
                            if builtin is None:
                                builtin = MlogBuiltin(snake_to_kebab(attr))
                                logger.warning(
                                    "Unknown Env attribute '%s'. "
                                    "Using '@%s' as fallback.",
                                    attr,
                                    builtin.name,
                                )

                            return builtin

                        case "Align":
                            builtin = ALIGN_MAP.get(attr)
                            if builtin is None:
                                raise CompilerError(
                                    CompilerErrorType.UNSUPPORTED,
                                    self._get_src_loc_from_node(expr),
                                    feature=f"Unknown Align attribute '{attr}'",
                                )

                            return builtin

                        # this is literally almost identical to the other cases ;-;
                        case "UnitType":
                            unit_type = UNIT_TYPE_MAP.get(attr)
                            if unit_type is None:
                                raise CompilerError(
                                    CompilerErrorType.UNSUPPORTED,
                                    self._get_src_loc_from_node(expr),
                                    feature=f"Unknown UnitType attribute '{attr}'",
                                )

                            return unit_type

                        # TODO: predefined colors from mimex

                        case _:
                            pass

                raise self._unsupported_expr_error(
                    expr, " on non-special values"
                )

            case ast.Subscript(value=value, slice=slice):
                output_expr = self._get_output_expr(output_expr)

                if (val := self._get_mem_expr(expr)) is not None:
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.READ,
                            None,
                            (),
                            (
                                output_expr,
                                MlogVar(val.attr),
                                self.compile_expr(slice),
                            ),
                        )
                    )
                    return output_expr

                if not isinstance(value, ast.Name):
                    raise CompilerError(
                        CompilerErrorType.UNSUPPORTED,
                        self._get_src_loc_from_node(expr),
                        feature="Complex subscript target",
                    )

                match value.id:
                    # slightly silly snippet
                    case "Link" | "Links" as name if (
                        name == "Links" or config.ALIAS.LINK
                    ):
                        index = self.compile_expr(slice)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.GET_LINK,
                                None,
                                (),
                                (output_expr, index),
                            )
                        )

                    case _:
                        raise CompilerError(
                            CompilerErrorType.UNSUPPORTED,
                            self._get_src_loc_from_node(expr),
                            feature="Unknown subscript target",
                        )

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
                # a little repetitive
                if config.STRING_LITERAL_AS_COLOR and val and val[0] == "%":
                    return intrinsics.builtins.builtin_color(
                        IntrinsicCallCtx(
                            (MlogFillerExpr(),),
                            self._get_src_loc_from_node(const),
                            self.emitter,
                        ),
                        MlogStringLiteral(val),
                    )

                return MlogStringLiteral(val)

            case _:
                raise self._unsupported_expr_error(const)

    def compile_func_call(
        self, func_call: ast.Call, output_expr: MlogExpr
    ) -> MlogExpr:
        output = self._compile_func_call(func_call, (output_expr,))

        if isinstance(output, tuple):
            # this raises even when just calling it with no output
            # but like why would you do that anyway
            raise CompilerError(
                CompilerErrorType.UNSUPPORTED,
                self._get_src_loc_from_node(func_call),
                # don't wanna deal with passing func name everywhere
                # location should be enough info anyway
                feature="Called builtin which returns tuple "
                "without immediate iterable unpacking",
            )

        return output

    def _compile_func_call(
        self, func_call: ast.Call, output_expr: tuple[MlogExpr, ...]
    ) -> MlogExpr | tuple[MlogExpr, ...]:
        """
        Only call this directly for tuple return.
        """
        src_loc = self._get_src_loc_from_node(func_call)

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

        if isinstance(func_call.func, ast.Attribute):
            return self._compile_builtin_func_call(
                func_call,
                output_expr,
                func_kwargs,
                self._get_attr_call_func(func_call),
            )

        if not isinstance(func_call.func, ast.Name):
            # idk what desc to put in the error sooo
            # misleading error message again
            raise self._unsupported_expr_error(
                func_call, "with non-identifier/attribute"
            )
        func_name = func_call.func.id

        # basic recursion check
        if f"{PREFIX_FUNC_SCOPE}{func_name}" in self._scope:
            raise self._unsupported_expr_error(func_call, " with recursion")

        # TODO: LEGB, passing function references
        # TODO: check outer scopes

        scope_str = self._get_scope_str(func_name)

        compiled_func = self._func_table.get(scope_str)
        if compiled_func is not None:
            return self._compile_non_inline_func_call(func_call, compiled_func)

        inline_func_def = self._inline_func_table.get(scope_str)
        if inline_func_def is not None:
            if len(output_expr) != 1:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    src_loc,
                    err="Called inline function with multiple output expressions "
                    "(possibly due to attempted iterable unpacking on its result)",
                )

            return self._compile_inline_func_call(
                func_call, inline_func_def, output_expr[0]
            )

        # TODO: non-inline builtins
        inline_builtin = intrinsics.builtins.FUNC_MAP.get(func_name, ...)
        if inline_builtin is None:
            raise self._unsupported_expr_error(
                func_call, f" with builtin {func_name}"
            )
        if inline_builtin is ...:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err=f"unknown/undefined function {func_name}",
            )

        return self._compile_builtin_func_call(
            func_call, output_expr, func_kwargs, inline_builtin
        )

    def _compile_builtin_func_call(
        self,
        func_call: ast.Call,
        output_expr: tuple[MlogExpr, ...],
        func_kwargs: dict[str, ast.expr],
        func_ref: IntrinsicFunc,
    ) -> MlogExpr | tuple[MlogExpr, ...]:
        src_loc = self._get_src_loc_from_node(func_call)

        pos_args, kwargs, _ = resolve_args_from_signature(
            [FillerAstExpr(), *func_call.args],
            func_kwargs,
            src_loc,
            signature(func_ref),
        )
        compiled_pos_args, compiled_kwargs = self._compile_args(
            pos_args, kwargs
        )

        return func_ref(
            IntrinsicCallCtx(output_expr, src_loc, self.emitter),
            *compiled_pos_args,
            **compiled_kwargs,
        )

    def _get_attr_call_func(self, func_call: ast.Call) -> IntrinsicFunc:
        if not isinstance(func_call.func, ast.Attribute):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err="called '_get_attr_call_func' with non-attr call",
            )

        if not isinstance(func_call.func.value, ast.Name):
            raise self._unsupported_expr_error(
                func_call, " with non-identifier as target of attribute access"
            )
        namespace = func_call.func.value.id
        func_name = func_call.func.attr

        namespaced_builtin_func = None
        match namespace:
            # TODO: DRY or something
            case intrinsics.unit.NAMESPACE:
                namespaced_builtin_func = intrinsics.unit.FUNC_MAP.get(
                    func_name
                )

            case intrinsics.screen.NAMESPACE:
                namespaced_builtin_func = intrinsics.screen.FUNC_MAP.get(
                    func_name
                )

            case intrinsics.mem.NAMESPACE:
                namespaced_builtin_func = intrinsics.mem.FUNC_MAP.get(func_name)

            case _:
                raise self._unsupported_expr_error(
                    func_call, " with custom namespaces"
                )

        if namespaced_builtin_func is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                self._get_src_loc_from_node(func_call),
                err=f"unknown/unsupported namespaced function {namespace}.{func_name}",
            )

        return namespaced_builtin_func

    def _compile_args(
        self, pos_args: ResolvedPosArgs, kwargs: ResolvedKwargs
    ) -> tuple[tuple[MlogExpr, ...], Mapping[str, MlogExpr]]:
        # misleading error message ¯\_(ツ)_/¯
        # TODO: add special case for *args or something
        # also relying on this helper
        # to filter out the FillerAstExpr is questionable

        compiled_pos_args: list[MlogExpr] = []
        for expr in pos_args:
            if isinstance(expr, FillerAstExpr):
                continue
            if isinstance(expr, MlogExpr):
                compiled_pos_args.append(expr)
                continue

            compiled_pos_args.append(self.compile_expr(expr))

        compiled_kwargs: Mapping[str, MlogExpr] = {}
        for name, expr in kwargs.items():
            if isinstance(expr, FillerAstExpr):
                # if this happens something probably went wrong but ¯\_(ツ)_/¯
                continue
            if isinstance(expr, MlogExpr):
                compiled_kwargs[name] = expr
                continue

            compiled_kwargs[name] = self.compile_expr(expr)

        return (tuple(compiled_pos_args), compiled_kwargs)

    def _compile_inline_func_call(
        self,
        func_call: ast.Call,
        inline_func_def: InlineFuncDef,
        output_expr: MlogExpr,
    ) -> MlogExpr:
        func_def = inline_func_def.func_def

        with self._inline_func_context(func_call, func_def, output_expr):
            for stmt in func_def.body:
                self.compile_stmt(stmt)

        return output_expr

    def _compile_non_inline_func_call(
        self, func_call: ast.Call, compiled_func: CompiledFunc
    ) -> MlogExpr:
        *_, arg_map = resolve_args(
            func_call.args,
            func_call.keywords,
            self._get_src_loc_from_node(func_call),
            compiled_func.params,
        )

        for name, arg in arg_map.items():
            if isinstance(arg, MlogExpr):
                continue
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
                is_func_call_jump=True,
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

    def compile_target(
        self, expr: ast.expr, input_expr: MlogExpr | None = None
    ) -> MlogExpr:
        """Resolves an expression in store context and returns its location."""

        if not isinstance(getattr(expr, "ctx", None), ast.Store):
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                self._get_src_loc_from_node(expr),
                err="Called compile_target() on an expression with store context",
            )

        match expr:
            case ast.Name(id=name):
                # indirect way of checking if we are compiling an inline func
                if self._inline_func_ret_target is not None:
                    # I really didn't want to do this but i tried ok
                    raise CompilerError(
                        CompilerErrorType.UNSUPPORTED,
                        self._get_src_loc_from_node(expr),
                        feature="Parameter with store context in inline function",
                    )
                #    # fragile and repetitive
                #    self._arg_table[name] = MlogVar(
                #        self._get_scope_str(PREFIX_FUNC_ARG) + name
                #    )

                return self._arg_table.get(
                    name, MlogVar(self._get_scope_str(name))
                )

            case ast.Subscript(slice=slice):
                if input_expr is None:
                    raise CompilerError(
                        CompilerErrorType.INTERNAL_COMP_TGT_NEED_INPUT_EXPR,
                        self._get_src_loc_from_node(expr),
                    )

                if (val := self._get_mem_expr(expr)) is not None:
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.WRITE,
                            None,
                            (),
                            (
                                input_expr,
                                MlogVar(val.attr),
                                self.compile_expr(slice),
                            ),
                        )
                    )
                    return input_expr

                raise CompilerError(
                    CompilerErrorType.UNSUPPORTED,
                    self._get_src_loc_from_node(expr),
                    feature="Complex subscript target",
                )

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
        src_loc = self._get_src_loc_from_node(stmt)
        match stmt:
            case ast.Expr(value=value):
                self.compile_expr(value)

            case ast.Assign(targets=targets, value=value):
                # pyndustric compatibility
                if (
                    len(targets) == 1
                    and isinstance(targets[0], ast.Attribute)
                    and isinstance(targets[0].value, ast.Name)
                    and targets[0].value.id == intrinsics.unit.NAMESPACE
                    and targets[0].attr == "flag"
                ):
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.UNIT_CONTROL,
                            UnitControlSuboperation.FLAG,
                            (),
                            (self.compile_expr(value),),
                        )
                    )
                    # don't wanna use return in case i add stuff to bottom of compile_stmt later

                elif any(isinstance(t, ast.Tuple) for t in targets):
                    if len(targets) > 1:
                        raise CompilerError(
                            CompilerErrorType.UNSUPPORTED,
                            src_loc,
                            feature="Multiple assignment targets with iterable unpacking",
                        )

                    if not isinstance(value, ast.Call):
                        raise CompilerError(
                            CompilerErrorType.BAD_ASSIGN,
                            src_loc,
                            feature="Non-call value with iterable unpacking assignment",
                        )

                    if not isinstance(targets[0], ast.Tuple):
                        raise CompilerError(
                            CompilerErrorType.INTERNAL,
                            src_loc,
                            err="this shouldn't be possible and is just to please the type checker",
                        )

                    output = self._compile_func_call(
                        value,
                        tuple(self.compile_target(t) for t in targets[0].elts),
                    )

                    expected_len = (
                        len(output) if isinstance(output, tuple) else 1
                    )
                    actual_len = len(targets[0].elts)
                    if actual_len != expected_len:
                        raise CompilerError(
                            CompilerErrorType.BAD_ASSIGN,
                            src_loc,
                            err="Mismatch in number of values to unpack: "
                            f"Expected {expected_len} but got {actual_len}",
                        )

                else:
                    try:
                        value_expr = self.compile_expr(
                            value, self.compile_target(targets[0])
                        )
                    except CompilerError as e:
                        if (
                            e.error
                            != CompilerErrorType.INTERNAL_COMP_TGT_NEED_INPUT_EXPR
                        ):
                            raise e from None

                        value_expr = self.compile_expr(value)
                        self.compile_target(targets[0], value_expr)

                    for target in targets[1:]:
                        t = self.compile_target(target, value_expr)
                        if self._get_mem_expr(target) is not None:
                            continue

                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SET, None, (), (t, value_expr)
                            )
                        )

            case ast.AugAssign(target=target, op=op, value=value):
                op_subop = BIN_OP_MAP.get(type(op))

                if op_subop is None:
                    raise self._unsupported_stmt_error(
                        stmt, f" with operation {op_subop}"
                    )

                def _emit_op(t: MlogExpr) -> None:
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.OPERATION,
                            op_subop,
                            (),
                            (
                                t,
                                self.compile_expr(
                                    target, suppress_ctx_check=True
                                ),
                                self.compile_expr(value),
                            ),
                        )
                    )

                try:
                    t = self.compile_target(target)
                    _emit_op(t)
                except CompilerError as e:
                    if (
                        e.error
                        != CompilerErrorType.INTERNAL_COMP_TGT_NEED_INPUT_EXPR
                    ):
                        raise e from None

                    t = self.emitter.new_tmp()
                    _emit_op(t)
                    self.compile_target(target, input_expr=t)

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

            case ast.While(test=test, body=body, orelse=orelse):
                loop_label, loop_label_ref = self.emitter.new_label()
                else_label, else_label_ref = self.emitter.new_label()
                break_label = None if orelse else else_label
                break_label_ref = None if orelse else else_label_ref

                # initial check to make it a proper while instead of do-while

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
                self.emitter.emit_label(loop_label)

                with self._loop_context(break_label, break_label_ref):
                    for stmt_ in body:
                        self.compile_stmt(stmt_)

                    # this solution is really confusing imo but oh well
                    this_loop_break = self._current_loop_break

                    if self._current_loop_continue:
                        self.emitter.emit_label(self._current_loop_continue)

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

                self.emitter.emit_label(else_label)

                for stmt_ in orelse:
                    self.compile_stmt(stmt_)

                # to prevent duplicate emission because of my shitty code
                if orelse and this_loop_break is not None:
                    self.emitter.emit_label(this_loop_break)

            case ast.Break():
                if not self._in_loop:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(stmt),
                        err="'break' outside loop",
                    )

                if self._current_loop_break_ref is None:
                    self._current_loop_break, self._current_loop_break_ref = (
                        self.emitter.new_label()
                    )

                elif (
                    self._current_loop_break is None
                    or self._current_loop_break.name
                    != self._current_loop_break_ref.name
                ):
                    raise CompilerError(
                        CompilerErrorType.INTERNAL, None, err=r"¯\_(ツ)_/¯"
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.ALWAYS,
                        (),
                        (self._current_loop_break_ref,),
                    )
                )

            case ast.Continue():
                if not self._in_loop:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(stmt),
                        err="'continue' outside loop",
                    )

                if self._current_loop_continue_ref is None:
                    (
                        self._current_loop_continue,
                        self._current_loop_continue_ref,
                    ) = self.emitter.new_label()

                elif (
                    self._current_loop_continue is None
                    or self._current_loop_continue.name
                    != self._current_loop_continue_ref.name
                ):
                    raise CompilerError(
                        CompilerErrorType.INTERNAL, None, err=r"¯\_(ツ)_/¯"
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.JUMP,
                        ConditionOpSuboperation.ALWAYS,
                        (),
                        (self._current_loop_continue_ref,),
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

            case ast.For(target=target, iter=iter_, body=body, orelse=orelse):
                if not isinstance(target, ast.Name):
                    raise self._unsupported_stmt_error(
                        stmt, " complex loop target"
                    )

                compiled_target = self.compile_target(target)
                if (
                    isinstance(iter_, ast.Call)
                    and isinstance(iter_.func, ast.Name)
                    and iter_.func.id == "range"
                ):
                    if len(iter_.args) == 1:
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SET,
                                None,
                                (),
                                (compiled_target, MlogNumberLiteral(0)),
                            )
                        )
                        start = compiled_target  # i think this is fine?
                        stop = self.compile_expr(iter_.args[0])
                        step = MlogNumberLiteral(1)
                    elif len(iter_.args) <= 3:  # noqa: PLR2004
                        start = self.compile_expr(
                            iter_.args[0], compiled_target
                        )
                        stop = self.compile_expr(iter_.args[1])
                        step = (
                            MlogNumberLiteral(1)
                            if len(iter_.args) == 2  # noqa:PLR2004
                            else self.compile_expr(iter_.args[2])
                        )
                    else:
                        raise CompilerError(
                            CompilerErrorType.BAD_CALL,
                            self._get_src_loc_from_node(target),
                            err="Too many arguments for range()",
                        )

                    loop_label, loop_label_ref = self.emitter.new_label()
                    else_label, else_label_ref = self.emitter.new_label()
                    break_label = None if orelse else else_label
                    break_label_ref = None if orelse else else_label_ref

                    # loop entry
                    # op sub tmp start stop
                    # op idiv tmp2 tmp step
                    # jump skip greaterThanEq tmp2 0
                    # op mul tmp3 tmp2 step
                    # op sub end start tmp3

                    # reuse tmp because i can
                    # notice how in the above commented code,
                    # tmp is only used to find tmp2
                    # tmp2 is not used after finding tmp3
                    # tmp3 is only used to find end
                    start_minus_stop = negative_len = (
                        negative_offset_from_start
                    ) = target_end_val = self.emitter.new_tmp()

                    self.emitter.emit_items(
                        (
                            # subtract start from stop to save an instruction, explained below
                            Instruction(
                                InstructionType.OPERATION,
                                OperationSuboperation.SUB,
                                (),
                                (start_minus_stop, start, stop),
                            ),
                            # negative len to save an instruction
                            # because with positive len
                            # i'd need to do ceil and div (2 instructions)
                            # which is combined into idiv with negative len
                            Instruction(
                                InstructionType.OPERATION,
                                OperationSuboperation.INTEGER_DIV,
                                (),
                                (negative_len, start_minus_stop, step),
                            ),
                            # `-len >= 0` equivalent to `len <= 0`
                            Instruction(
                                InstructionType.JUMP,
                                ConditionOpSuboperation.GREATER_THAN_OR_EQ,
                                (),
                                (
                                    else_label_ref,
                                    negative_len,
                                    MlogNumberLiteral(0),
                                ),
                            ),
                            Instruction(
                                InstructionType.OPERATION,
                                OperationSuboperation.MUL,
                                (),
                                (
                                    negative_offset_from_start,
                                    negative_len,
                                    step,
                                ),
                            ),
                            # subtract because well the offset is negative
                            Instruction(
                                InstructionType.OPERATION,
                                OperationSuboperation.SUB,
                                (),
                                (
                                    target_end_val,
                                    start,
                                    negative_offset_from_start,
                                ),
                            ),
                            loop_label,
                        )
                    )

                    with self._loop_context(break_label, break_label_ref):
                        for stmt_ in body:
                            self.compile_stmt(stmt_)

                        this_loop_break = self._current_loop_break

                        # rmb continue label must be before increment
                        if self._current_loop_continue:
                            self.emitter.emit_label(self._current_loop_continue)

                    self.emitter.emit_items(
                        (
                            Instruction(
                                InstructionType.OPERATION,
                                OperationSuboperation.ADD,
                                (),
                                (compiled_target, compiled_target, step),
                            ),
                            Instruction(
                                InstructionType.JUMP,
                                ConditionOpSuboperation.NOT_EQUAL,
                                (),
                                (
                                    loop_label_ref,
                                    compiled_target,
                                    target_end_val,
                                ),
                            ),
                            else_label,
                        )
                    )

                    for stmt_ in orelse:
                        self.compile_stmt(stmt_)

                    if orelse and this_loop_break is not None:
                        self.emitter.emit_label(this_loop_break)

                else:
                    raise self._unsupported_stmt_error(
                        stmt, " with non-range() iterable"
                    )

            case ast.ImportFrom(module=module, names=names, level=level):
                if module != "py2mlog_api" or level != 0:
                    raise self._unsupported_stmt_error(
                        stmt, " with non 'py2mlog' import"
                    )

                if any(n.asname is not None for n in names):
                    raise self._unsupported_stmt_error(
                        stmt, " with aliases (from ... import ... as ...)"
                    )

                if any(
                    n.name != "*"  # star import
                    and n.name not in MLOG_BUILTIN_NAMESPACES
                    for n in names
                ):
                    raise CompilerError(
                        CompilerErrorType.BAD_IMPORT,
                        self._get_src_loc_from_node(stmt),
                        err="unrecognised namespace import",
                    )

            case _:
                raise self._unsupported_stmt_error(stmt)

    def _get_mem_expr(self, expr: ast.expr) -> ast.Attribute | None:
        """
        Returns the ast.Attribute if criteria is met.
        """
        if (
            isinstance(expr, ast.Subscript)
            and isinstance(expr.value, ast.Attribute)
            and isinstance(expr.value.value, ast.Name)
            and expr.value.value.id == "Mem"
        ):
            return expr.value

        return None

    def _compile_func_def(self, func_def: ast.FunctionDef) -> None:
        # TODO: non-special decorators
        inline = False
        for decor in func_def.decorator_list:
            if not isinstance(decor, ast.Name):
                raise self._unsupported_stmt_error(
                    func_def, " complex decorator"
                )

            if decor.id == "inline":
                if inline:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(func_def),
                        err=" duplicate '@inline' decorator",
                    )
                inline = True
            else:
                raise self._unsupported_stmt_error(
                    func_def, ": non-speical function decorators"
                )

        scope_str = self._get_scope_str(func_def.name)
        if inline:
            self._inline_func_table[scope_str] = InlineFuncDef(func_def)
            self._func_table.pop(scope_str, None)
            return

        with self._func_context(func_def):
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
            self._inline_func_table.pop(scope_str, None)

    def _compile_return(self, value: ast.expr | None) -> None:
        if value is None:
            value = ast.Constant(None)

        if self._inline_func_ret_target is not None:
            self.compile_expr(value, self._inline_func_ret_target)
            return

        self.compile_expr(
            value, MlogVar(self._get_scope_str(NAME_FUNC_RET_VAL))
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

    # this whole loop context thing is so stupid
    # i wonder which fool thought it was a good idea
    @contextmanager
    def _loop_context(
        self,
        break_label: Label | None,
        break_label_ref: LabelRef | None,
        *,
        in_loop: bool = True,
    ) -> Generator[None, None, None]:
        prev_in_loop = self._in_loop
        prev_break = self._current_loop_break
        prev_break_ref = self._current_loop_break_ref
        prev_continue = self._current_loop_continue
        prev_continue_ref = self._current_loop_continue_ref

        self._in_loop = in_loop
        self._current_loop_break = break_label
        self._current_loop_break_ref = break_label_ref
        self._current_loop_continue = None
        self._current_loop_continue_ref = None

        yield

        self._in_loop = prev_in_loop
        self._current_loop_break = prev_break
        self._current_loop_break_ref = prev_break_ref
        self._current_loop_continue = prev_continue
        self._current_loop_continue_ref = prev_continue_ref

    @contextmanager
    def _func_context(
        self,
        func_def: ast.FunctionDef,
        *,
        inline: bool = False,
    ) -> Generator[None, None, None]:
        """
        Manages the current scope, emitter, and arg table.
        Yields the current full scope string.
        """
        clear_emitter = not inline

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

        if not inline:
            all_args = (
                func_args.posonlyargs
                + func_args.args
                + func_args.kwonlyargs
                + ([func_args.vararg] if func_args.vararg is not None else [])
                + ([func_args.kwarg] if func_args.kwarg is not None else [])
            )

            for arg in all_args:
                self._arg_table[arg.arg] = MlogVar(
                    self._get_scope_str(PREFIX_FUNC_ARG + arg.arg)
                )

        # i don't like this but whatever
        old_instructions = self.emitter.instructions
        if clear_emitter:
            self.emitter.instructions = []

        # only reason in_loop as arg exists,
        # and hijacking the loop context is probably a bad idea
        with self._loop_context(None, None, in_loop=False):
            yield

        self._scope.pop()
        self._arg_table = {}
        if clear_emitter:
            self.emitter.instructions = old_instructions

    @contextmanager
    def _inline_func_context(
        self,
        func_call: ast.Call,
        func_def: ast.FunctionDef,
        output_expr: MlogExpr,
    ):
        *_, arg_map = resolve_args(
            func_call.args,
            func_call.keywords,
            self._get_src_loc_from_node(func_call),
            func_def.args,
        )

        old_inline_func_ret_target = self._inline_func_ret_target
        with self._func_context(func_def, inline=True):
            self._filling_inline_arg_table = True

            for name, arg in arg_map.items():
                if isinstance(arg, MlogExpr):
                    continue
                self._arg_table[name] = self.compile_expr(arg)

            self._filling_inline_arg_table = False
            self._inline_func_ret_target = output_expr

            yield

        self._inline_func_ret_target = old_inline_func_ret_target

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
            f'(under context "{type(ctx).__name__}") '
            if ctx is not None
            else ""
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
