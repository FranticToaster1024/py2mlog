__all__ = ["parse_mlog"]

from typing import TYPE_CHECKING

from py2mlog.compiler.emitter import INSTRUCTION_ARG_SHAPES
from py2mlog.compiler.error import (
    CompilerError,
    CompilerErrorType,
    SourceLocation,
)
from py2mlog.mlog.instruction import Instruction, Label, MlogItem
from py2mlog.mlog.instruction_types import InstructionType
from py2mlog.mlog.mlog_expressions import (
    MlogBoolLiteral,
    MlogBuiltin,
    MlogColorLiteral,
    MlogExpr,
    MlogNullLiteral,
    MlogNumberLiteral,
    MlogStringLiteral,
    MlogVar,
)
from py2mlog.mlog.param_map import ParamType, get_param_order

if TYPE_CHECKING:
    from py2mlog.mlog.selectable_params import SelectableParam


def str_to_arg(s: str) -> MlogExpr:
    if s.startswith('"') and s.endswith('"'):
        return MlogStringLiteral(s.removeprefix('"').removesuffix('"'))
    if s.startswith("@"):
        return MlogBuiltin(s.removeprefix("@"))
    if s.startswith("%"):
        return MlogColorLiteral(s.removeprefix("%"))
    if s == "null":
        return MlogNullLiteral()
    if s in ("true", "false"):
        return MlogBoolLiteral(s == "true")

    try:
        return MlogNumberLiteral(int(s))
    except ValueError:
        try:
            return MlogNumberLiteral(float(s))
        except ValueError:
            return MlogVar(s)


def _tokenize_mlog(
    src: str, src_loc: SourceLocation
) -> list[tuple[list[str], SourceLocation]]:
    _lineno = src_loc.line_no
    _start_col_offset = src_loc.start_col
    del src_loc
    _this_line_start_idx = 0

    def _get_src_loc() -> SourceLocation:
        _curr_line: list[str] = []

        i = _this_line_start_idx
        while i < len(src) and src[i] != "\n":
            _curr_line.append(src[i])
            i += 1

        return SourceLocation(
            _lineno,
            _lineno,
            _start_col_offset,
            (
                _start_col_offset + len(_curr_line)
                if _start_col_offset is not None
                else _start_col_offset
            ),
            "".join(_curr_line),
        )

    _curr_src_loc = _get_src_loc()

    lines: list[tuple[list[str], SourceLocation]] = []
    curr_tokens: list[str] = []
    expect_new_tok = False

    def _newline(i: int) -> None:
        nonlocal \
            curr_tokens, \
            expect_new_tok, \
            _curr_src_loc, \
            _lineno, \
            _this_line_start_idx, \
            _start_col_offset
        if curr_tokens:
            _curr_src_loc = _get_src_loc()
            lines.append((curr_tokens, _curr_src_loc))
        curr_tokens = []
        expect_new_tok = False

        _lineno += 1
        _this_line_start_idx = i
        _start_col_offset = 0  # only applies to first line

    i = 0
    while i < len(src):
        char = src[i]

        if char in ("\n", ";"):
            i += 1
            _newline(i)
            continue

        if expect_new_tok and not char.isspace():
            raise CompilerError(
                CompilerErrorType.SYNTAX,
                _curr_src_loc,
                err="Expected space after string",
            )

        expect_new_tok = False

        if char == "#":
            while i < len(src) and char != "\n":
                char = src[i]
                i += 1
            _newline(i)
            continue

        if char == '"':
            s: list[str] = [char]
            i += 1  # otherwise it sees itself as both opening and closing quote
            while i < len(src):
                char = src[i]
                s.append(char)
                if char == "\n":
                    raise CompilerError(
                        CompilerErrorType.SYNTAX,
                        _curr_src_loc,
                        err="Newline with open quote",
                    )
                if char == '"':
                    expect_new_tok = True
                    i += 1
                    break
                i += 1
            else:
                raise CompilerError(
                    CompilerErrorType.SYNTAX,
                    _curr_src_loc,
                    err="Open quote on last line",
                )

            curr_tokens.append("".join(s))
            continue

        if char.isspace():
            i += 1
            continue

        s: list[str] = []
        while i < len(src):
            char = src[i]
            if char.isspace() or char in ("\n", ";"):
                break
            s.append(char)
            i += 1
        curr_tokens.append("".join(s))

    _newline(-1)
    return lines


def parse_mlog(src: str, _src_loc: SourceLocation) -> list[MlogItem]:
    mlog_items: list[MlogItem] = []

    for (firstword, *tokens), src_loc in _tokenize_mlog(src, _src_loc):
        if not firstword:
            continue

        if not tokens and firstword.endswith(":"):
            try:
                mlog_items.append(Label(firstword.removesuffix(":")))
                continue
            except CompilerError as e:
                if e.error is not CompilerErrorType.INTERNAL:
                    raise e from None
                raise CompilerError(
                    CompilerErrorType.SYNTAX, src_loc, err=str(e)
                ) from None

        try:
            instr_type = InstructionType(firstword)
        except ValueError:
            raise CompilerError(
                CompilerErrorType.SYNTAX,
                src_loc,
                err=f"Unknown instruction type '{firstword}'",
            ) from None

        expected_arg_shape = INSTRUCTION_ARG_SHAPES[firstword]
        subop_type = expected_arg_shape.subop

        if subop_type is None:
            param_order = get_param_order(instr_type, subop_type)
            subop = None
        else:
            # we need the param map to find the subop
            # but the param map key is the subop
            # so we try every subop and take the first valid one
            for _subop in subop_type:
                param_order = get_param_order(instr_type, _subop)
                if param_order is None:
                    try:
                        if _subop == subop_type(tokens[0]):
                            subop = _subop
                            break
                    except (ValueError, IndexError):
                        continue

                else:
                    subop_index = param_order.index(ParamType.SUBOPERATION)
                    if subop_index >= len(tokens):
                        continue

                    try:
                        if _subop == subop_type(tokens[subop_index]):
                            subop = _subop
                            break
                    except (ValueError, IndexError):
                        continue
            else:
                raise CompilerError(
                    CompilerErrorType.SYNTAX,
                    src_loc,
                    err=f"Instruction '{' '.join(firstword, *tokens)}' "
                    "did not match any suboperation.",
                )

        sel_params: list[SelectableParam] = []
        args: list[MlogExpr] = []

        if param_order is None:
            subop_offset = 1 if subop is not None else 0
            sel_param_end = False

            for i, token in enumerate(tokens):
                if i == 0 and subop is not None:
                    continue

                if not sel_param_end and i < subop_offset + len(
                    expected_arg_shape.sel_params
                ):
                    sel_param_type = expected_arg_shape.sel_params[
                        i - subop_offset
                    ]
                    try:
                        sel_params.append(sel_param_type(token))
                        continue
                    except ValueError:
                        sel_param_end = True

                args.append(str_to_arg(token))

        else:
            if len(tokens) != len(param_order):
                raise CompilerError(
                    CompilerErrorType.SYNTAX,
                    src_loc,
                    err=f"Arg count mismatch: "
                    f"Expected {len(param_order) + 1}, "
                    f"Got {len(tokens) + 1}",
                )

            sel_param_idx = 0
            for token, param_type in zip(tokens, param_order, strict=True):
                if param_type == ParamType.FILLER:
                    pass

                elif param_type == ParamType.SELECTABLE:
                    sel_param_type = expected_arg_shape.sel_params[
                        sel_param_idx
                    ]
                    try:
                        sel_params.append(sel_param_type(token))
                    except ValueError:
                        raise CompilerError(
                            CompilerErrorType.SYNTAX,
                            src_loc,
                            err=f"Invalid selectable param '{token}' "
                            f"for type '{sel_param_type.__name__}'",
                        ) from None

                    sel_param_idx += 1

                elif param_type == ParamType.VAR:
                    args.append(str_to_arg(token))

        mlog_items.append(
            Instruction(instr_type, subop, tuple(sel_params), tuple(args))
        )

    return mlog_items
