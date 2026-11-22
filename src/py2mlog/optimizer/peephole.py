import logging
from collections import deque
from collections.abc import Callable
from itertools import accumulate

from py2mlog.compiler.error import CompilerError, CompilerErrorType
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
)
from py2mlog.mlog.suboperations import (
    NEGATED_COND_OP_SUBOP_MAP,
    ConditionOpSuboperation,
    OperationSuboperation,
)
from py2mlog.optimizer.utils import get_jump_target_name, mlog_expr_as_print_str

logger = logging.getLogger(__name__)


type _OptFunc = Callable[[tuple[MlogItem, ...]], tuple[MlogItem, ...]]

# thanks minpiler <3
_opts: list[_OptFunc] = []


def _add_opt_func(f: _OptFunc) -> _OptFunc:
    _opts.append(f)
    return f


type JumpLabelMap = dict[str, list[Instruction]]


def peephole(instrs: tuple[MlogItem, ...], /) -> tuple[MlogItem, ...]:
    for opt in _opts:
        instrs = opt(instrs)

    return instrs


@_add_opt_func
def _merge_print_format(instrs: tuple[MlogItem, ...]) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem | None] = list(instrs)

    last_print_instr_idx: int | None = None

    for i, instr in enumerate(instrs):
        if isinstance(instr, Instruction):
            if instr.type is InstructionType.PRINT:
                last_print_instr_idx = i
                continue

            if instr.type is InstructionType.FORMAT:
                if last_print_instr_idx is None:
                    continue

                last_print_instr = new_instrs[last_print_instr_idx]

                if not isinstance(
                    last_print_instr, Instruction
                ) or not isinstance(
                    last_print_instr.args[0], MlogStringLiteral
                ):
                    continue

                print_str = last_print_instr.args[0].value
                format_str = mlog_expr_as_print_str(instr.args[0])

                if format_str is None:
                    # regex would be cleaner
                    if (
                        len(print_str) == 3  # noqa: PLR2004
                        and print_str[0] == "{"
                        and print_str[1].isdigit()
                        and print_str[2] == "}"
                    ):
                        # print "{0}"
                        # format foo
                        # ->
                        # print foo
                        new_instrs[last_print_instr_idx] = None
                        new_instrs[i] = Instruction(
                            InstructionType.PRINT, None, (), (instr.args[0],)
                        )
                        last_print_instr_idx = i

                    else:
                        last_print_instr_idx = None

                    continue

                indexes, fill_order = (
                    _get_placeholder_str_indexes_and_fill_order(print_str)
                )

                if 0 not in fill_order:
                    continue

                str_index = indexes[fill_order.index(0)]
                print_str_list = list(print_str)

                print_str_list[str_index - 1 : str_index + 2] = [format_str]

                new_instrs[last_print_instr_idx] = None
                new_instrs[i] = Instruction(
                    InstructionType.PRINT,
                    None,
                    (),
                    (MlogStringLiteral("".join(print_str_list)),),
                )
                last_print_instr_idx = i

        last_print_instr_idx = None

    return tuple(e for e in new_instrs if e is not None)


# probably shitty time complexity
@_add_opt_func
def _merge_prints(instrs: tuple[MlogItem, ...]) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem] = []

    # we can't process the string
    # until we have all the format instrs
    # (processed, unprocessed)
    curr_print_strs: tuple[str | None, str | None] = (None, None)
    # temporary buffer
    curr_format_instrs: list[Instruction] = []
    ordered_format_instrs: list[Instruction] = []

    def _flush_instrs():
        nonlocal curr_print_strs, curr_format_instrs, ordered_format_instrs

        if curr_print_strs != (None, None):
            processed_str = (
                "" if curr_print_strs[0] is None else curr_print_strs[0]
            )

            if curr_print_strs[1] is not None:
                unprocessed_str = curr_print_strs[1]
                new_str, format_instrs = (
                    _rewrite_placeholders_and_reorder_format_instrs(
                        unprocessed_str, curr_format_instrs
                    )
                )
            else:
                new_str = ""
                format_instrs = curr_format_instrs

            ordered_format_instrs.extend(format_instrs)
            curr_format_instrs = []

            new_instrs.append(
                Instruction(
                    InstructionType.PRINT,
                    None,
                    (),
                    (MlogStringLiteral(processed_str + new_str),),
                )
            )
            new_instrs.extend(ordered_format_instrs)

        elif ordered_format_instrs:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=r"shouldn't happen ¯\_(ツ)_/¯",
            )

        curr_print_strs = (None, None)
        ordered_format_instrs = []
        curr_format_instrs = []

    i = 0
    while i < len(instrs):
        instr = instrs[i]
        if isinstance(instr, Instruction):
            if instr.type is InstructionType.PRINT:
                print_str = mlog_expr_as_print_str(instr.args[0])

                if curr_print_strs[0] is None and curr_print_strs[1] is None:
                    # we ignore those that are
                    # - at the start of the chain
                    # - cannot be statically converted to a string
                    if print_str is not None:
                        if curr_format_instrs or ordered_format_instrs:
                            raise CompilerError(
                                CompilerErrorType.INTERNAL,
                                None,
                                err=r"shouldn't happen ¯\_(ツ)_/¯",
                            )

                        curr_print_strs = (curr_print_strs[0], print_str)

                        i += 1
                        continue

                else:
                    if curr_print_strs[1] is not None:
                        processed_str = (
                            ""
                            if curr_print_strs[0] is None
                            else curr_print_strs[0]
                        )

                        new_str, format_instrs = (
                            _rewrite_placeholders_and_reorder_format_instrs(
                                curr_print_strs[1], curr_format_instrs
                            )
                        )
                        curr_print_strs = (processed_str + new_str, None)

                        ordered_format_instrs.extend(format_instrs)
                        curr_format_instrs = []

                    if print_str is None:
                        curr_print_strs = (
                            curr_print_strs[0] + "{0}",
                            curr_print_strs[1],
                        )
                        ordered_format_instrs.append(
                            Instruction(
                                InstructionType.FORMAT,
                                None,
                                (),
                                (instr.args[0],),
                            )
                        )

                        i += 1
                        continue

                    curr_print_strs = (curr_print_strs[0], print_str)

                    i += 1
                    continue

            elif (
                instr.type is InstructionType.FORMAT
                and curr_print_strs[1] is not None
            ):
                curr_format_instrs.append(instr)
                i += 1
                continue

        _flush_instrs()

        new_instrs.append(instr)
        i += 1

    _flush_instrs()

    return tuple(new_instrs)


# mindustry only fills one placeholder at once,
# so we can rewrite every placeholder as {0}
# if we re-order the format instructions accordingly
# https://github.com/Anuken/Mindustry/blob/19a0f40d44514f4802a8b79770456e7e32e34da0/core/src/mindustry/logic/LExecutor.java#L1127
def _rewrite_placeholders_and_reorder_format_instrs(
    tgt_str: str, format_instrs: list[Instruction]
) -> tuple[str, list[Instruction]]:
    """
    Replaces all placeholders with {0} and reorders format instructions accordingly.
    Mutates format_instrs.
    Returns (new_str, format_instrs).
    """
    output = list(tgt_str)

    placeholder_str_indexes, placeholder_fill_order = (
        _get_placeholder_str_indexes_and_fill_order(tgt_str)
    )

    for i, (str_idx, fill_idx) in enumerate(
        zip(placeholder_str_indexes, placeholder_fill_order, strict=True)
    ):
        if i >= len(format_instrs) or fill_idx >= len(format_instrs):
            continue

        # the number inside the placeholder
        # {0}, {1}, etc
        #  ^    ^
        num = int(tgt_str[str_idx])

        if num == 0:
            continue

        output[str_idx] = "0"
        format_instrs[fill_idx], format_instrs[i] = (
            format_instrs[i],
            format_instrs[fill_idx],
        )

    return ("".join(output), format_instrs)


def _get_placeholder_str_indexes_and_fill_order(
    tgt_str: str,
) -> tuple[list[int], list[int]]:
    placeholder_str_indexes: list[int] = []
    placeholder_num_counts = [0] * 10

    i = 0
    while i < len(tgt_str):
        char = tgt_str[i]
        if (
            char == "{"
            and i + 2 < len(tgt_str)
            and tgt_str[i + 1].isdigit()
            and tgt_str[i + 2] == "}"
        ):
            num = int(tgt_str[i + 1])
            placeholder_str_indexes.append(i + 1)
            placeholder_num_counts[num] += 1

        i += 1

    placeholder_num_cum_counts = list(accumulate(placeholder_num_counts))
    # ¯\_(ツ)_/¯
    curr_placeholder_num_counts = [0] * 10

    placeholder_fill_order: list[int] = []
    for i in placeholder_str_indexes:
        num = int(tgt_str[i])

        if num == 0:
            placeholder_fill_order.append(curr_placeholder_num_counts[0])
        else:
            placeholder_fill_order.append(
                curr_placeholder_num_counts[num]
                + placeholder_num_cum_counts[num - 1]
            )

        curr_placeholder_num_counts[num] += 1

    return (placeholder_str_indexes, placeholder_fill_order)


@_add_opt_func
def _remove_useless_end_and_wrap_labels(
    instrs: tuple[MlogItem, ...],
) -> tuple[MlogItem, ...]:
    new_instrs = deque(instrs)

    while new_instrs:
        last_instr = new_instrs[-1]

        if (
            isinstance(last_instr, Instruction)
            and last_instr.type == InstructionType.END
        ):
            new_instrs.pop()

        elif isinstance(last_instr, Label):
            # label on last line doesn't wrap properly;
            # see https://github.com/Anuken/Mindustry-Suggestions/issues/6629
            new_instrs.appendleft(new_instrs.pop())

        else:
            break

    return tuple(new_instrs)


@_add_opt_func
def _simplify_adjacent_jumps(
    instrs: tuple[MlogItem, ...], /
) -> tuple[MlogItem, ...]:
    jump_label_map = _generate_jump_label_map(instrs)

    new_instrs: list[MlogItem] = []

    # build new_instrs
    i = 0
    while i < len(instrs):
        instr = instrs[i]

        # skip useless label
        if isinstance(instr, Label) and not jump_label_map[instr.name]:
            i += 1
            continue

        if (
            isinstance(instr, Instruction)
            and instr.type is InstructionType.JUMP
        ):
            # mostly to please the type checker
            if not isinstance(instr.suboperation, ConditionOpSuboperation):
                raise CompilerError(
                    CompilerErrorType.INTERNAL,
                    None,
                    err=f"Jump instruction with non-{ConditionOpSuboperation.__name__} "
                    f"suboperation: {instr!r}",
                )

            label_name = get_jump_target_name(instr)

            next_i = i + 1
            if next_i < len(instrs):
                next_instr = instrs[next_i]

                # check for
                # jump label ...  # <-- skip
                # label:  # <-- keep in case other jumps point here
                if (
                    isinstance(next_instr, Label)
                    and next_instr.name == label_name
                ):
                    i = next_i
                    continue

                # check for
                # jump l1 ...  # <-- negate this condition and jump to l2 instead
                # jump l2 always  # <-- skip
                # l1:  # <-- keep
                negated_cond_op_subop = NEGATED_COND_OP_SUBOP_MAP.get(
                    instr.suboperation
                )
                if (
                    negated_cond_op_subop is not None
                    and isinstance(next_instr, Instruction)
                    and next_instr.type is InstructionType.JUMP
                    and next_instr.suboperation
                    == ConditionOpSuboperation.ALWAYS
                ):
                    # wow nice naming convention
                    next_next_i = next_i + 1
                    if next_next_i < len(instrs):
                        next_next_instr = instrs[next_next_i]
                        if (
                            isinstance(next_next_instr, Label)
                            and next_next_instr.name == label_name
                        ):
                            new_instrs.append(
                                Instruction(
                                    InstructionType.JUMP,
                                    negated_cond_op_subop,
                                    (),
                                    (next_instr.args[0], *instr.args[1:]),
                                )
                            )
                            i = next_next_i
                            continue

        new_instrs.append(instr)
        i += 1

    return tuple(new_instrs)


def _generate_jump_label_map(
    instrs: tuple[MlogItem, ...],
) -> JumpLabelMap:
    jump_label_map: JumpLabelMap = {}

    # fill labels
    for instr in instrs:
        if isinstance(instr, Label):
            if instr.name in jump_label_map:
                raise CompilerError(
                    CompilerErrorType.INTERNAL,
                    None,
                    err=f"Duplicate labels in generated mlog with name '{instr.name}'.",
                )

            jump_label_map[instr.name] = []

    # fill jumps
    for instr in instrs:
        if (
            isinstance(instr, Instruction)
            and instr.type == InstructionType.JUMP
        ):
            label_name = get_jump_target_name(instr)

            jump_label_map_entry = jump_label_map.get(label_name)
            if jump_label_map_entry is None:
                logger.warning(
                    "Jump to '%s' with no matching label.", label_name
                )
            else:
                jump_label_map_entry.append(instr)

    return jump_label_map


@_add_opt_func
def _remove_no_op_instrs(
    instrs: tuple[MlogItem, ...],
) -> tuple[MlogItem, ...]:
    """
    Does not remove literal 'noop' instructions for testing purposes.
    """
    new_instrs: list[MlogItem] = []

    for instr in instrs:
        if isinstance(instr, Instruction):
            if instr.type is InstructionType.SET:
                # e.g.
                # set 0 foo
                # set "abc" foo
                if isinstance(instr.args[0], MlogLiteral):
                    continue

                # e.g.
                # set x x
                # set @counter @counter
                if instr.args[0] == instr.args[1]:
                    continue

            # e.g.
            # op add 0 foo bar
            # op abs "abc" foo
            elif instr.type is InstructionType.OPERATION and isinstance(
                instr.args[0], MlogLiteral
            ):
                continue

        new_instrs.append(instr)

    return tuple(new_instrs)


@_add_opt_func
def _simplify_ops(instrs: tuple[MlogItem, ...]) -> tuple[MlogItem, ...]:
    new_instrs: list[MlogItem] = []

    for instr in instrs:
        if (
            isinstance(instr, Instruction)
            and instr.type is InstructionType.OPERATION
        ):
            # op add foo bar 0
            # op add foo 0 bar
            if instr.suboperation is OperationSuboperation.ADD:
                val = None
                if instr.args[1] == MlogNumberLiteral(0):
                    val = instr.args[2]

                elif instr.args[2] == MlogNumberLiteral(0):
                    val = instr.args[1]

                if val is not None:
                    new_instrs.append(
                        Instruction(
                            InstructionType.SET, None, (), (instr.args[0], val)
                        )
                    )
                    continue

            # op sub foo bar 0
            if instr.suboperation is OperationSuboperation.SUB and instr.args[
                2
            ] == MlogNumberLiteral(0):
                new_instrs.append(
                    Instruction(
                        InstructionType.SET,
                        None,
                        (),
                        (instr.args[0], instr.args[1]),
                    )
                )
                continue

            # op mul foo bar 1
            # op mul foo 1 bar
            if instr.suboperation is OperationSuboperation.MUL:
                val = None
                if instr.args[1] == MlogNumberLiteral(1):
                    val = instr.args[2]

                elif instr.args[2] == MlogNumberLiteral(1):
                    val = instr.args[1]

                if val is not None:
                    new_instrs.append(
                        Instruction(
                            InstructionType.SET, None, (), (instr.args[0], val)
                        )
                    )
                    continue

            # op div foo bar 1
            # op idiv foo bar 1
            if instr.suboperation in (
                OperationSuboperation.DIV,
                OperationSuboperation.INTEGER_DIV,
            ) and instr.args[2] == MlogNumberLiteral(1):
                new_instrs.append(
                    Instruction(
                        InstructionType.SET,
                        None,
                        (),
                        (instr.args[0], instr.args[1]),
                    )
                )
                continue

        new_instrs.append(instr)

    return tuple(new_instrs)
