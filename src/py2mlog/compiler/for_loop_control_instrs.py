from dataclasses import dataclass

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


def range_for_loop_control_instrs(
    label_refs: LoopLabelRefs,
    compiled_target: MlogExpr,
    tmp: MlogExpr,
    _start: MlogExpr,
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
            # compiled target equal to start before loop start
            (start_minus_stop, compiled_target, stop),
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
            # compiled target equal to start before loop start
            (target_end_val, compiled_target, negative_offset_from_start),
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
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.NOT_EQUAL,
            (),
            (label_refs.loop_label_ref, compiled_target, target_end_val),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end)


def env_links_for_loop_control_instrs(
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
        Instruction(
            InstructionType.JUMP,
            ConditionOpSuboperation.LESS_THAN,
            (),
            (label_refs.loop_label_ref, loop_iter, MlogBuiltin("links")),
        ),
    )

    return ForLoopControlInstrs(loop_start, body_start, body_end)
