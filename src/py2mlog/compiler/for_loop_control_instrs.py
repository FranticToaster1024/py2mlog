from dataclasses import dataclass

from py2mlog.compiler.directives import UnrollDirective
from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    LabelRef,
    MlogBuiltin,
    MlogExpr,
    MlogNumberLiteral,
)
from py2mlog.mlog.suboperations import (
    ConditionOpSuboperation,
    OperationSuboperation,
)

# slightly cursed but i really don't want this sitting in compiler


@dataclass(frozen=True)
class LoopLabelRefs:
    loop_label_ref: LabelRef
    else_label_ref: LabelRef


@dataclass(frozen=True)
class ForLoopControlInstrs:
    loop_start: tuple[Instruction, ...]
    body_start: tuple[Instruction, ...]
    body_end: tuple[Instruction, ...]
    loop_end: tuple[Instruction, ...]


def for_range_loop_control_instrs(
    label_refs: LoopLabelRefs,
    compiled_target: MlogExpr,
    tmp: MlogExpr,
    start: MlogExpr,
    stop: MlogExpr,
    step: MlogExpr,
) -> ForLoopControlInstrs:

    # loop entry
    # op sub tmp start stop
    # op idiv tmp2 tmp step
    # jump skip greaterThanEq tmp2 0
    # op mul tmp3 tmp2 step
    # op sub end start tmp3

    # reuse tmp because i can
    start_minus_stop = negative_len = negative_offset_from_start = (
        target_end_val
    ) = tmp

    loop_start = (
        # subtract start from stop to save an instruction, explained below
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.SUB,
            (),
            (start_minus_stop, start, stop),
        ),
        # idiv in mindustry rounds to negative infinity
        # https://github.com/Anuken/Mindustry/blob/19a0f40d44514f4802a8b79770456e7e32e34da0/core/src/mindustry/logic/LogicOp.java#L12
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
            (label_refs.else_label_ref, negative_len, MlogNumberLiteral(0)),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.MUL,
            (),
            (negative_offset_from_start, negative_len, step),
        ),
        # subtract because the offset is negative
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.SUB,
            (),
            (target_end_val, start, negative_offset_from_start),
        ),
    )

    body_start = ()

    body_end = (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ADD,
            (),
            (compiled_target, compiled_target, step),
        ),
    )

    loop_end = (
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.NOT_EQUAL,
            (),
            (label_refs.loop_label_ref, compiled_target, target_end_val),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end, loop_end)


def unrolled_for_range_loop_control_instrs(
    label_refs: LoopLabelRefs,
    remainder_loop_else_ref: LabelRef,
    compiled_target: MlogExpr,
    tgt_end_val_tmp: MlogExpr,
    start: MlogExpr,
    stop: MlogExpr,
    step: MlogExpr,
    unroll: UnrollDirective,
    unroll_tmp: MlogExpr,
) -> ForLoopControlInstrs:
    if not isinstance(unroll.factor, int):
        raise CompilerError(
            CompilerErrorType.INTERNAL,
            None,
            err="Invalid call to 'unrolled_for_range_loop_control_instrs()'",
        )

    # 'len' refers to trip count here
    start_minus_stop = negative_offset_from_start = target_end_val = (
        tgt_end_val_tmp
    )

    # reuse tmp for negative_len because i can
    negative_len = remainder_negative_len = remainder_negative_offset = (
        unrolled_tgt_end_val
    ) = unroll_tmp

    # loop entry
    # op sub start_minus_stop start stop
    # op idiv negative_len start_minus_stop step

    # # check for empty range
    # jump skip_both greaterThanEq negative_len 0

    # # compute end first so its present in remainder loop
    # # even when unrolled loop is skipped

    # op mul negative_offset_from_start negative_len step
    # op sub end start negative_offset_from_start

    # # let remainder loop handle empty range
    # jump skip greaterThan negative_len negative_unroll_factor

    # op mod remainder_negative_len negative_len unroll_factor
    # op mul remainder_negative_offset remainder_negative_len step
    # op add unrolled_tgt_end_val end remainder_negative_offset

    # # slightly misleading variable names:
    # # remainder_negative_len, remainder_negative_offset
    # # since remainder loop actually uses the total values, not these

    loop_start = (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.SUB,
            (),
            (start_minus_stop, start, stop),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.INTEGER_DIV,
            (),
            (negative_len, start_minus_stop, step),
        ),
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.GREATER_THAN_OR_EQ,
            (),
            (remainder_loop_else_ref, negative_len, MlogNumberLiteral(0)),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.MUL,
            (),
            (negative_offset_from_start, negative_len, step),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.SUB,
            (),
            (target_end_val, start, negative_offset_from_start),
        ),
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.GREATER_THAN,
            (),
            (
                label_refs.else_label_ref,
                negative_len,
                MlogNumberLiteral(-unroll.factor),
            ),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.MOD,
            (),
            (
                remainder_negative_len,
                negative_len,
                MlogNumberLiteral(unroll.factor),
            ),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.MUL,
            (),
            (remainder_negative_offset, remainder_negative_len, step),
        ),
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ADD,
            (),
            (unrolled_tgt_end_val, target_end_val, remainder_negative_offset),
        ),
    )

    body_start = ()

    body_end = (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ADD,
            (),
            (compiled_target, compiled_target, step),
        ),
    )

    loop_end = (
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.NOT_EQUAL,
            (),
            (label_refs.loop_label_ref, compiled_target, unrolled_tgt_end_val),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end, loop_end)


def for_range_remainder_loop_control_instrs(
    label_refs: LoopLabelRefs,
    compiled_target: MlogExpr,
    target_end_val: MlogExpr,
    step: MlogExpr,
) -> ForLoopControlInstrs:
    loop_start = (
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.EQUAL,
            (),
            (label_refs.else_label_ref, compiled_target, target_end_val),
        ),
    )

    body_start = ()

    body_end = (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ADD,
            (),
            (compiled_target, compiled_target, step),
        ),
    )

    loop_end = (
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.NOT_EQUAL,
            (),
            (label_refs.loop_label_ref, compiled_target, target_end_val),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end, loop_end)


def for_env_links_loop_control_instrs(
    label_refs: LoopLabelRefs, compiled_target: MlogExpr, loop_iter: MlogExpr
) -> ForLoopControlInstrs:
    loop_start = (
        Instruction(
            InstructionType.SET, None, (), (loop_iter, MlogNumberLiteral(0))
        ),
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.EQUAL,
            (),
            (
                label_refs.else_label_ref,
                MlogBuiltin("links"),
                MlogNumberLiteral(0),
            ),
        ),
    )

    body_start = (
        Instruction(
            InstructionType.GET_LINK, None, (), (compiled_target, loop_iter)
        ),
    )

    body_end = (
        Instruction(
            InstructionType.OPERATION,
            OperationSuboperation.ADD,
            (),
            (loop_iter, loop_iter, MlogNumberLiteral(1)),
        ),
    )

    loop_end = (
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.LESS_THAN,
            (),
            (label_refs.loop_label_ref, loop_iter, MlogBuiltin("links")),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end, loop_end)
