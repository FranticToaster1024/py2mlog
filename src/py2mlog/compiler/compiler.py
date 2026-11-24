import ast
import logging
from collections import deque
from collections.abc import Callable, Generator, Mapping
from contextlib import contextmanager
from inspect import signature

from py2mlog import intrinsics
from py2mlog.compiler import config
from py2mlog.compiler.directives import Directives, UnrollDirective
from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    HasPosition,
    SourceLocation,
)
from py2mlog.compiler.for_loop_control_instrs import (
    ForLoopControlInstrs,
    LoopLabelRefs,
    for_env_links_loop_control_instrs,
    for_env_links_remainder_loop_control_instrs,
    for_range_loop_control_instrs,
    for_range_remainder_loop_control_instrs,
    unrolled_for_env_links_loop_control_instrs,
    unrolled_for_range_loop_control_instrs,
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
    COLOR_MAP,
    ENV_ATTR_MAP,
    SENSOR_PROPERTIES,
    UNIT_MAP,
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
from py2mlog.mlog.parser import parse_mlog
from py2mlog.mlog.suboperations import (
    ConditionOpSuboperation,
    OperationSuboperation,
    UnitControlSuboperation,
)
from py2mlog.optimizer.peephole import _remove_useless_end_and_wrap_labels  # pyright: ignore[reportPrivateUsage]
from py2mlog.optimizer.utils import mlog_expr_as_print_str

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

        self._SPECIAL_BUILTINS: dict[
            str,
            Callable[
                [ast.Call, tuple[MlogExpr, ...]],
                MlogExpr | tuple[MlogExpr, ...],
            ],
        ] = {
            "print": self._compile_print_call,
            "mlog_raw": self._compile_mlog_raw_call,
            "create_links": lambda _, out_expr: (
                (MlogFillerExpr(),) * len(out_expr)
            ),
        }

        self._unroll: UnrollDirective | None = None

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
            _remove_useless_end_and_wrap_labels(
                tuple(self.emitter.instructions)
            )
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
                    tmp = None
                    prev = self.compile_expr(values[0])

                    for raw_val in values[1:-1]:
                        if tmp is None:
                            tmp = self.emitter.new_tmp()

                        val = self.compile_expr(raw_val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (tmp, prev, MlogBoolLiteral(True), val, prev),
                            )
                        )
                        prev = tmp

                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            ConditionOpSuboperation.EQUAL,
                            (),
                            (
                                output_expr,
                                prev,
                                MlogBoolLiteral(True),
                                self.compile_expr(values[-1]),
                                prev,
                            ),
                        )
                    )

                elif isinstance(op, ast.Or):
                    tmp = None
                    prev = self.compile_expr(values[0])

                    for raw_val in values[1:-1]:
                        if tmp is None:
                            tmp = self.emitter.new_tmp()

                        val = self.compile_expr(raw_val)
                        self.emitter.emit_instruction(
                            Instruction(
                                InstructionType.SELECT,
                                ConditionOpSuboperation.EQUAL,
                                (),
                                (tmp, prev, MlogBoolLiteral(True), prev, val),
                            )
                        )
                        prev = tmp

                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            ConditionOpSuboperation.EQUAL,
                            (),
                            (
                                output_expr,
                                prev,
                                MlogBoolLiteral(True),
                                prev,
                                self.compile_expr(values[-1]),
                            ),
                        )
                    )

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
                compiled_left = self.compile_expr(left)

                tmp = self.emitter.new_tmp()
                prev = self.compile_expr(comparators[0])

                if len(comparators) == 1:
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.OPERATION,
                            op_subop,
                            (),
                            (output_expr, compiled_left, prev),
                        )
                    )
                    return output_expr

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.OPERATION,
                        op_subop,
                        (),
                        (tmp, compiled_left, prev),
                    )
                )

                for i, raw_comparator in enumerate(comparators[1:-1], 1):
                    cond_op_subop = get_subops(i)[1]

                    comparator = self.compile_expr(raw_comparator)
                    self.emitter.emit_instruction(
                        Instruction(
                            InstructionType.SELECT,
                            cond_op_subop,
                            (),
                            (
                                tmp,
                                prev,
                                comparator,
                                tmp,
                                MlogBoolLiteral(False),
                            ),
                        )
                    )
                    prev = comparator

                cond_op_subop = get_subops(len(comparators) - 1)[1]
                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.SELECT,
                        cond_op_subop,
                        (),
                        (
                            output_expr,
                            prev,
                            self.compile_expr(comparators[-1]),
                            tmp,
                            MlogBoolLiteral(False),
                        ),
                    )
                )

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
                    builtin_var = self._get_builtin_attr_var(
                        value.id,
                        attr,
                        src_loc=self._get_src_loc_from_node(expr),
                    )

                    if builtin_var is not None:
                        return builtin_var

                output_expr = self._get_output_expr(output_expr)
                compiled_value = self.compile_expr(value)

                sensor_property = SENSOR_PROPERTIES.get(attr)
                if sensor_property is None:
                    raise CompilerError(
                        CompilerErrorType.UNKNOWN_ATTRIBUTE,
                        self._get_src_loc_from_node(expr),
                        attr=f"sensor property '{attr}'. ",
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.SENSOR,
                        None,
                        (),
                        (
                            output_expr,
                            compiled_value,
                            sensor_property,
                        ),
                    )
                )

                return output_expr

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

                if isinstance(value, ast.Name) and (
                    value.id == "Links"
                    or (config.ALIAS.LINK and value.id == "Link")
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
                    return output_expr

                # building[res_as_expr]
                # building['res_name']
                compiled_value = self.compile_expr(value)
                compiled_slice = self.compile_expr(slice)

                if isinstance(compiled_slice, MlogStringLiteral):
                    if compiled_slice.value not in SENSOR_PROPERTIES:
                        logger.warning(
                            "Unknown sensor property '%s'. "
                            "Using '@%s' as fallback.",
                            compiled_slice.value,
                            compiled_slice.value,
                        )

                    compiled_slice = MlogBuiltin(
                        snake_to_kebab(compiled_slice.value)
                    )

                self.emitter.emit_instruction(
                    Instruction(
                        InstructionType.SENSOR,
                        None,
                        (),
                        (output_expr, compiled_value, compiled_slice),
                    )
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

                s: list[str] = []
                for c in val:
                    # https://github.com/Anuken/Mindustry/blob/1a22b880576d2f8f97550280f76bfdd0d0069543/core/src/mindustry/logic/LAssembler.java#L81
                    if c == "\n":
                        s.append(r"\n")
                    elif c == "\\":
                        s.append(r"\\")
                    elif c == '"':
                        s.append(r"\"")
                    elif c.isprintable():
                        s.append(c)
                    else:
                        s.append(f"\\u{ord(c):04x}")

                return MlogStringLiteral("".join(s))

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
            raise self._unsupported_expr_error(
                func_call, " with non-identifier/attribute"
            )
        func_name = func_call.func.id

        # check if it's a compiler directive
        try:
            Directives(func_name)
        except ValueError:
            pass
        else:
            raise CompilerError(
                CompilerErrorType.BAD_DIRECTIVE,
                src_loc,
                err=f"Called compiler directive '{func_name}' "
                "in disallowed context",
            )

        # basic recursion check
        if f"{PREFIX_FUNC_SCOPE}{func_name}" in self._scope:
            raise self._unsupported_expr_error(func_call, " with recursion")

        # TODO: LEGB, passing function references

        compiled_func = self._get_compiled_func(func_name)
        if compiled_func is not None:
            return self._compile_non_inline_func_call(func_call, compiled_func)

        inline_func_def = self._get_inline_func_def(func_name)
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

        _compile_special_builtin = self._SPECIAL_BUILTINS.get(func_name)
        if _compile_special_builtin is not None:
            return _compile_special_builtin(func_call, output_expr)

        # TODO: non-inline builtins
        inline_builtin = intrinsics.builtins.FUNC_MAP.get(func_name)
        if inline_builtin is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err=f"unknown/undefined function {func_name}",
            )

        return self._compile_builtin_func_call(
            func_call, output_expr, func_kwargs, inline_builtin
        )

    def _get_compiled_func(self, func_name: str) -> CompiledFunc | None:
        curr_scope = self._scope.copy()

        compiled_func = None
        # this'll also pop the global scope but that won't break anything
        while self._scope:
            scope_str = self._get_scope_str(func_name)

            compiled_func = self._func_table.get(scope_str)
            if compiled_func is not None:
                break

            self._scope.pop()

        self._scope = curr_scope
        return compiled_func

    def _get_inline_func_def(self, func_name: str) -> InlineFuncDef | None:
        curr_scope = self._scope.copy()

        compiled_func = None
        # this'll also pop the global scope but that won't break anything
        while self._scope:
            scope_str = self._get_scope_str(func_name)

            compiled_func = self._inline_func_table.get(scope_str)
            if compiled_func is not None:
                break

            self._scope.pop()

        self._scope = curr_scope
        return compiled_func

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
        attr_target_name = func_call.func.value.id
        func_name = func_call.func.attr

        intrinsic_namespace_func_map = (
            intrinsics.NAMESPACES_NAME_TO_FUNC_MAP_MAP.get(attr_target_name)
        )
        if intrinsic_namespace_func_map is not None:
            func = intrinsic_namespace_func_map.get(func_name)
            if func is None:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    self._get_src_loc_from_node(func_call),
                    err=f"unknown namespaced builtin '{attr_target_name}.{func_name}'",
                )

            return func

        method = intrinsics.INSTANCE_METHOD_FUNC_MAP.get(func_name)
        if method is None:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                self._get_src_loc_from_node(func_call),
                err=f"unknown method '.{func_name}'",
            )

        def _func(
            call_ctx: IntrinsicCallCtx, *args: MlogExpr, **kwargs: MlogExpr
        ) -> MlogExpr | tuple[MlogExpr, ...]:
            try:
                return method(
                    call_ctx, MlogVar(attr_target_name), *args, **kwargs
                )

            except TypeError as e:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    self._get_src_loc_from_node(func_call),
                    err=e,
                ) from None

        return _func

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
            self.compile_func_def_body(func_def.body)

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

    def _compile_print_call(
        self, func_call: ast.Call, _: tuple[MlogExpr, ...]
    ) -> MlogNullLiteral:
        src_loc = self._get_src_loc_from_node(func_call)

        # TODO: so many things

        sep = MlogStringLiteral(" ")
        end = MlogStringLiteral(r"\n")
        flush = MlogVar("message1")
        for kw in func_call.keywords:
            if kw.arg == "sep":
                if (
                    not isinstance(kw.value, ast.Constant)
                    and len(func_call.args) > 3  # noqa: PLR2004
                ):
                    logger.warning(
                        "Calling 'print()' with non-string-literal for param 'sep'. "
                        "This may incur high performance costs",
                    )

                sep = self.compile_expr(kw.value)

            elif kw.arg == "end":
                end = self.compile_expr(kw.value)

            elif kw.arg == "flush":
                flush = self.compile_expr(kw.value)

            else:
                raise CompilerError(
                    CompilerErrorType.BAD_CALL,
                    src_loc,
                    err=f"Unexpected kwarg '{kw.arg}' for 'print()'",
                )

        # idk i heard repeated string concat was slow
        s: list[str] = []
        instrs: list[Instruction] = []

        def _format_mlog_expr(e: MlogExpr) -> None:
            print_str = mlog_expr_as_print_str(e)
            if print_str is None:
                s.append("{0}")
                instrs.append(
                    Instruction(InstructionType.FORMAT, None, (), (e,))
                )

            else:
                s.append(print_str)

        for i, arg in enumerate(func_call.args):
            # handling general case first which is a little silly
            # but the other case is a big block of code
            if not isinstance(arg, ast.JoinedStr):
                compiled_arg = self.compile_expr(arg)
                _format_mlog_expr(compiled_arg)

            else:
                for value in arg.values:
                    if isinstance(value, ast.Constant):
                        _format_mlog_expr(self._compile_const(value))
                    elif isinstance(value, ast.FormattedValue):
                        if value.conversion != -1:
                            raise CompilerError(
                                CompilerErrorType.UNSUPPORTED,
                                src_loc,
                                feature='conversion in fstring (e.g. f"{x!s}", f"{x!r}")',
                            )

                        if value.format_spec is not None:
                            raise CompilerError(
                                CompilerErrorType.UNSUPPORTED,
                                src_loc,
                                feature="format spec in fstring"
                                '(e.g. f"{x:2f}", f"{x:05}")',
                            )

                        _format_mlog_expr(self.compile_expr(value.value))
                    else:
                        raise CompilerError(
                            CompilerErrorType.SYNTAX,
                            src_loc,
                            err="Somehow generated node of type "
                            f"'{type(value).__name__}' inside fstring.",
                        )

            if i < len(func_call.args) - 1:
                _format_mlog_expr(sep)

        _format_mlog_expr(end)

        self.emitter.emit_items(
            (
                Instruction(
                    InstructionType.PRINT,
                    None,
                    (),
                    (MlogStringLiteral("".join(s)),),
                ),
                *instrs,
            )
        )
        if not isinstance(flush, MlogBoolLiteral) or flush.value:
            self.emitter.emit_instruction(
                Instruction(InstructionType.PRINT_FLUSH, None, (), (flush,))
            )
        return MlogNullLiteral()

    def _compile_mlog_raw_call(
        self, func_call: ast.Call, _: tuple[MlogExpr, ...]
    ) -> MlogNullLiteral:
        # intercept at ast level instead of as builtin
        # because compiling string literals messes up newlines and such
        src_loc = self._get_src_loc_from_node(func_call)
        if func_call.keywords:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err="'mlog_raw' takes 0 kwargs",
            )

        if len(func_call.args) != 1:
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err="Pos arg count mismatch for 'mlog_raw': "
                f"Expected 1, got {len(func_call.args)}",
            )

        if not isinstance(func_call.args[0], ast.Constant) or not isinstance(
            func_call.args[0].value, str
        ):
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err="Called 'mlog_raw' with non string-literal.",
            )

        try:
            parsed_mlog = parse_mlog(func_call.args[0].value, src_loc)
        except CompilerError as e:
            if e.error is not CompilerErrorType.SYNTAX:
                raise e from None
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                None,
                err=f"While compiling 'mlog_raw' call:\n{e!s}",
            ) from None

        # something something DRY
        try:
            self.emitter.emit_items(parsed_mlog)
        except CompilerError as e:
            if e.error is not CompilerErrorType.INTERNAL:
                raise e from None
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                None,
                err=f"While compiling 'mlog_raw' call:\n{e!s}",
            ) from None

        return MlogNullLiteral()

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
                if (
                    self._inline_func_ret_target is not None
                    and name in self._arg_table
                ):
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

            case ast.Attribute(value=value, attr=attr):
                if isinstance(value, ast.Name):
                    builtin_var = self._get_builtin_attr_var(
                        value.id,
                        attr,
                        src_loc=self._get_src_loc_from_node(expr),
                    )
                    if builtin_var is not None:
                        return builtin_var

                raise CompilerError(
                    CompilerErrorType.UNSUPPORTED,
                    self._get_src_loc_from_node(expr),
                    err="Non-builtin attribute expression in store context",
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

    def _get_builtin_attr_var(
        self, value_name: str, attr: str, *, src_loc: SourceLocation
    ) -> MlogExpr | None:
        builtin_namespace = True
        builtin = None

        match value_name:
            case "Env":
                builtin = ENV_ATTR_MAP.get(attr)
                if builtin is None:
                    # don't use snake_to_kebab helper
                    # because it forces lowercase
                    builtin = MlogBuiltin(attr.replace("_", "-"))
                    logger.warning(
                        "Unknown Env attribute '%s'. Using '@%s' as fallback.",
                        attr,
                        builtin.name,
                    )

                return builtin

            case "Align":
                builtin = ALIGN_MAP.get(attr)

            case "Units":
                builtin = UNIT_MAP.get(attr)

            case "Colors":
                builtin = COLOR_MAP.get(attr)

            # TODO: predefined colors from mimex

            case _:
                builtin_namespace = False

        if builtin_namespace:
            if builtin is None:
                raise CompilerError(
                    CompilerErrorType.UNKNOWN_ATTRIBUTE,
                    src_loc,
                    attr=f"Unknown attribute '{value_name}.{attr}'",
                )
            return builtin

        return None

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
        if (
            isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Call)
            and isinstance(stmt.value.func, ast.Name)
            and stmt.value.func.id == "unroll"
        ):
            src_loc = self._get_src_loc_from_node(stmt)
            call = stmt.value

            if call.keywords:
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="'unroll()' takes 0 kwargs",
                )

            if len(call.args) != 1:
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="Pos arg count mismatch for 'unroll()': "
                    f"Expected 1, got {len(call.args)}",
                )

            if not isinstance(call.args[0], ast.Constant):
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="Called 'unroll()' with non-literal",
                )

            factor = call.args[0].value
            if not isinstance(factor, (int, str)):
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="Called 'unroll()' with unsupported literal type. "
                    'Expected int or str literal "full"',
                )

            if isinstance(factor, str) and factor != "full":
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="Called 'unroll()' with unsupported string literal. "
                    f"Expected \"full\", got '{factor}'",
                )

            if isinstance(factor, int) and factor <= 0:
                raise CompilerError(
                    CompilerErrorType.BAD_DIRECTIVE,
                    src_loc,
                    err="Called 'unroll()' with non-positive integer: "
                    f"'{factor}'",
                )

            self._unroll = UnrollDirective(factor, src_loc)

            return

        compiled = self._compile_stmt(stmt)

        self._check_directives_clear()

        return compiled

    def _compile_stmt(self, stmt: ast.stmt) -> None:
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
                    and targets[0].value.id == intrinsics.unit.NAMESPACE_NAME
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

                self.compile_stmt_list(body)

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

                self.compile_stmt_list(orelse)

                if skip_else_label is not None:
                    self.emitter.emit_label(skip_else_label)

            case ast.While(test=test, body=body, orelse=orelse):
                unroll = self._unroll
                self._unroll = None

                if unroll is not None:
                    raise CompilerError(
                        CompilerErrorType.UNSUPPORTED,
                        src_loc,
                        feature="unrolling while loops",
                    )

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
                    self.compile_stmt_list(body)

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

                self.compile_stmt_list(orelse)

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
                unroll = self._unroll
                self._unroll = None

                if not isinstance(target, ast.Name):
                    raise self._unsupported_stmt_error(
                        stmt, " complex loop target"
                    )

                compiled_target = self.compile_target(target)

                loop_label, loop_label_ref = self.emitter.new_label()
                else_label, else_label_ref = self.emitter.new_label()
                break_label = None if orelse else else_label
                break_label_ref = None if orelse else else_label_ref

                if (
                    isinstance(iter_, ast.Call)
                    and isinstance(iter_.func, ast.Name)
                    and iter_.func.id == "range"
                ):
                    start, stop, step = self._process_range_call(
                        iter_, compiled_target, src_loc
                    )

                    if unroll is not None:
                        if unroll.factor == "full":
                            if (
                                not isinstance(start, MlogNumberLiteral)
                                or not isinstance(stop, MlogNumberLiteral)
                                or not isinstance(step, MlogNumberLiteral)
                            ):
                                raise CompilerError(
                                    CompilerErrorType.BAD_DIRECTIVE,
                                    self._get_src_loc_from_node(iter_),
                                    err="Cannot fully unroll 'range()' with non int-literal",
                                )

                            if (
                                not isinstance(start.value, int)
                                or not isinstance(stop.value, int)
                                or not isinstance(step.value, int)
                            ):
                                raise CompilerError(
                                    CompilerErrorType.BAD_DIRECTIVE,
                                    self._get_src_loc_from_node(iter_),
                                    err="Cannot fully unroll 'range()' with float literal",
                                )

                            this_loop_break = None
                            is_start = True
                            for i in range(start.value, stop.value, step.value):
                                # index already set for first iter; avoid duplicating
                                if not is_start:
                                    # ideally this would belong in for_loop_control_instrs.py
                                    self.emitter.emit_instruction(
                                        Instruction(
                                            InstructionType.SET,
                                            None,
                                            (),
                                            (
                                                compiled_target,
                                                MlogNumberLiteral(i),
                                            ),
                                        )
                                    )
                                is_start = False

                                # recompile body every time
                                # should prevent tmps from carrying over
                                # and prevent continue label clashes
                                this_loop_break, this_loop_break_ref = (
                                    self._compile_loop_body(
                                        body, break_label, break_label_ref
                                    )
                                )

                                if (
                                    break_label is None
                                    or break_label_ref is None
                                ):
                                    break_label = this_loop_break
                                    break_label_ref = this_loop_break_ref

                            self.compile_stmt_list(orelse)

                            if orelse and this_loop_break is not None:
                                self.emitter.emit_label(this_loop_break)

                            return

                        # partial unrolling

                        remainder_loop_label, remainder_loop_label_ref = (
                            self.emitter.new_label()
                        )
                        remainder_else_label, remainder_else_label_ref = (
                            self.emitter.new_label()
                        )
                        # use existing break label

                        target_end_val_tmp = self.emitter.new_tmp()
                        unrolled_loop_control_instrs = (
                            unrolled_for_range_loop_control_instrs(
                                LoopLabelRefs(loop_label_ref, else_label_ref),
                                remainder_else_label_ref,
                                compiled_target,
                                target_end_val_tmp,
                                start,
                                stop,
                                step,
                                unroll,
                                self.emitter.new_tmp(),
                            )
                        )

                        break_label, break_label_ref = (
                            self._emit_partially_unrolled_loop(
                                unroll.factor,
                                unrolled_loop_control_instrs,
                                body=body,
                                loop_label=loop_label,
                                else_label=else_label,
                                break_label=break_label,
                                break_label_ref=break_label_ref,
                            )
                        )

                        # remainder loop

                        del (
                            loop_label,
                            loop_label_ref,
                            else_label,
                            else_label_ref,
                        )

                        loop_label, loop_label_ref = (
                            remainder_loop_label,
                            remainder_loop_label_ref,
                        )
                        else_label, else_label_ref = (
                            remainder_else_label,
                            remainder_else_label_ref,
                        )
                        # break label and break label ref already generated and used

                        loop_control_instrs = (
                            for_range_remainder_loop_control_instrs(
                                LoopLabelRefs(loop_label_ref, else_label_ref),
                                compiled_target,
                                target_end_val_tmp,
                                step,
                            )
                        )

                    else:
                        loop_control_instrs = for_range_loop_control_instrs(
                            LoopLabelRefs(loop_label_ref, else_label_ref),
                            compiled_target,
                            self.emitter.new_tmp(),
                            start,
                            stop,
                            step,
                        )

                elif (
                    isinstance(iter_, ast.Call)
                    and isinstance(iter_.func, ast.Attribute)
                    and isinstance(iter_.func.value, ast.Name)
                    and iter_.func.value.id == "Env"
                    and iter_.func.attr == "links"
                ):
                    if len(iter_.args) > 0 or len(iter_.keywords) > 0:
                        raise CompilerError(
                            CompilerErrorType.BAD_CALL,
                            self._get_src_loc_from_node(iter_),
                            err="Env.links() does not take any arguments.",
                        )

                    loop_iter = self.emitter.new_loop_iter()

                    if unroll is not None:
                        if unroll.factor == "full":
                            raise CompilerError(
                                CompilerErrorType.BAD_DIRECTIVE,
                                self._get_src_loc_from_node(iter_),
                                err="Cannot fully unroll 'Env.links()'",
                            )

                        unrolled_loop_control_instrs = (
                            unrolled_for_env_links_loop_control_instrs(
                                LoopLabelRefs(loop_label_ref, else_label_ref),
                                compiled_target,
                                loop_iter,
                                unroll.factor,
                                self.emitter.new_tmp(),
                            )
                        )

                        break_label, break_label_ref = (
                            self._emit_partially_unrolled_loop(
                                unroll.factor,
                                unrolled_loop_control_instrs,
                                body=body,
                                loop_label=loop_label,
                                else_label=else_label,
                                break_label=break_label,
                                break_label_ref=break_label_ref,
                            )
                        )

                        del (
                            loop_label,
                            loop_label_ref,
                            else_label,
                            else_label_ref,
                        )

                        loop_label, loop_label_ref = self.emitter.new_label()
                        else_label, else_label_ref = self.emitter.new_label()

                        loop_control_instrs = (
                            for_env_links_remainder_loop_control_instrs(
                                LoopLabelRefs(loop_label_ref, else_label_ref),
                                compiled_target,
                                loop_iter,
                            )
                        )

                    else:
                        loop_control_instrs = for_env_links_loop_control_instrs(
                            LoopLabelRefs(loop_label_ref, else_label_ref),
                            compiled_target,
                            loop_iter,
                        )

                else:
                    raise self._unsupported_stmt_error(
                        stmt, " with non-range()/Env.links() iterable"
                    )

                self.emitter.emit_items(loop_control_instrs.loop_start)
                self.emitter.emit_label(loop_label)

                self.emitter.emit_items(loop_control_instrs.body_start)

                this_loop_break, _ = self._compile_loop_body(
                    body, break_label, break_label_ref
                )

                self.emitter.emit_items(loop_control_instrs.body_end)
                self.emitter.emit_items(loop_control_instrs.loop_end)

                self.emitter.emit_label(else_label)
                self.compile_stmt_list(orelse)

                if orelse and this_loop_break is not None:
                    self.emitter.emit_label(this_loop_break)

            case ast.ImportFrom(module=module, level=level):
                if module != "py2mlog" or level != 0:
                    raise CompilerError(
                        CompilerErrorType.BAD_IMPORT,
                        self._get_src_loc_from_node(stmt),
                        err="non 'py2mlog' import",
                    )

            case _:
                raise self._unsupported_stmt_error(stmt)

    def compile_stmt_list(self, stmts: list[ast.stmt]) -> None:
        for stmt in stmts:
            self.compile_stmt(stmt)

        self._check_directives_clear()

    def compile_func_def_body(self, body: list[ast.stmt]) -> None:
        for stmt in body:
            self.compile_stmt(stmt)
            if isinstance(stmt, ast.Return):
                break

        else:
            self._compile_return(None)

        self._check_directives_clear()

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

    def _emit_partially_unrolled_loop(
        self,
        unroll_factor: int,
        unrolled_loop_control_instrs: ForLoopControlInstrs,
        *,
        body: list[ast.stmt],
        loop_label: Label,
        else_label: Label,
        break_label: Label | None,
        break_label_ref: LabelRef | None,
    ) -> tuple[Label | None, LabelRef | None]:
        self.emitter.emit_items(unrolled_loop_control_instrs.loop_start)
        self.emitter.emit_label(loop_label)

        for _ in range(unroll_factor):
            self.emitter.emit_items(unrolled_loop_control_instrs.body_start)

            this_loop_break, this_loop_break_ref = self._compile_loop_body(
                body, break_label, break_label_ref
            )

            self.emitter.emit_items(unrolled_loop_control_instrs.body_end)

            if break_label is None or break_label_ref is None:
                break_label = this_loop_break
                break_label_ref = this_loop_break_ref

        self.emitter.emit_items(unrolled_loop_control_instrs.loop_end)

        self.emitter.emit_label(else_label)

        # don't generate orelse & break label in partially unrolled loop

        return (break_label, break_label_ref)

    def _process_range_call(
        self,
        iter_: ast.Call,
        compiled_for_loop_target: MlogExpr,
        src_loc: SourceLocation,
    ) -> tuple[
        MlogNumberLiteral | MlogVar,
        MlogNumberLiteral | MlogVar,
        MlogNumberLiteral | MlogVar,
    ]:
        if len(iter_.args) == 1:
            start = MlogNumberLiteral(0)
            self._set_expr_output(start, compiled_for_loop_target)

            stop = self.compile_expr(iter_.args[0])
            step = MlogNumberLiteral(1)

        elif 2 <= len(iter_.args) <= 3:  # noqa: PLR2004
            if isinstance(iter_.args[0], ast.Constant):
                start = self._compile_const(iter_.args[0])
                self._set_expr_output(start, compiled_for_loop_target)

            else:
                start = self.compile_expr(
                    iter_.args[0], compiled_for_loop_target
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
                self._get_src_loc_from_node(iter_),
                err="Pos arg count mismatch for 'range()': "
                f"Expected 1 to 3, got {len(iter_.args)}",
            )

        if (
            not isinstance(start, (MlogNumberLiteral, MlogVar))
            or not isinstance(stop, (MlogNumberLiteral, MlogVar))
            or not isinstance(step, (MlogNumberLiteral, MlogVar))
        ):
            raise CompilerError(
                CompilerErrorType.BAD_CALL,
                src_loc,
                err="'range()' arguments must be number literal or variable",
            )

        if any(
            isinstance(arg.value, float)
            for arg in (start, stop, step)
            if isinstance(arg, MlogNumberLiteral)
        ):
            logger.warning("Called 'range()' with float literal.")

        return (start, stop, step)

    def _compile_func_def(self, func_def: ast.FunctionDef) -> None:
        # TODO: non-special decorators
        inline = False
        for decor in func_def.decorator_list:
            if not isinstance(decor, ast.Name):
                raise self._unsupported_stmt_error(
                    func_def, " complex decorator"
                )

            if decor.id == Directives.INLINE.value:
                if inline:
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        self._get_src_loc_from_node(func_def),
                        err=f"duplicate '@{Directives.INLINE.value}' decorator",
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

            self.compile_func_def_body(func_def.body)

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

    def _compile_loop_body(
        self,
        body: list[ast.stmt],
        break_label: Label | None,
        break_label_ref: LabelRef | None,
    ) -> tuple[Label | None, LabelRef | None]:
        with self._loop_context(break_label, break_label_ref):
            self.compile_stmt_list(body)

            this_loop_break = self._current_loop_break
            this_loop_break_ref = self._current_loop_break_ref

            if self._current_loop_continue:
                self.emitter.emit_label(self._current_loop_continue)

        return (this_loop_break, this_loop_break_ref)

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
    ) -> Generator[None, None, None]:
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

    def _check_directives_clear(self) -> None:
        if self._unroll is not None:
            raise CompilerError(
                CompilerErrorType.BAD_DIRECTIVE,
                self._unroll.src_loc,
                err="Unused unroll directive",
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
