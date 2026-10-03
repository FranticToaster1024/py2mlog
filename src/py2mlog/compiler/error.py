import ast

from dataclasses import dataclass
from typing import Any, Sequence
from enum import Enum, auto


class CompilerErrorType(Enum):
    UNSUPPORTED = auto()
    SYNTAX = auto()
    BAD_BUILTIN_CALL = auto()
    INTERNAL = auto()


_ERR_DESCRIPTIONS = {
    CompilerErrorType.UNSUPPORTED: "Unsupported feature: {feature}.",
    CompilerErrorType.SYNTAX: "A syntax error occurred: {err}.",
    CompilerErrorType.BAD_BUILTIN_CALL: "Invalid builtin call.",
    CompilerErrorType.INTERNAL: "An internal error occurred: {err}.",
}

assert len(CompilerErrorType) == len(
    _ERR_DESCRIPTIONS
), "Missing CompilerErrorType description."


@dataclass(frozen=True)
class SourceLocation:
    line_no: int
    end_line_no: int | None
    start_col: int | None = None
    end_col: int | None = None
    line: str | None = None

    @classmethod
    def from_ast_node(
        cls, node: ast.expr | ast.stmt, src_lines: Sequence[str]
    ) -> "SourceLocation":
        return cls(
            node.lineno,
            node.end_lineno,
            node.col_offset,
            node.end_col_offset,
            (
                "\n".join(src_lines[node.lineno - 1 : node.end_lineno])
                if node.end_lineno is not None
                else src_lines[node.lineno - 1]
            ),
        )


class CompilerError(Exception):

    def __init__(
        self,
        error: CompilerErrorType,
        location: SourceLocation | None,
        **format_args: Any,
    ) -> None:
        """Contains error type and location metadata of an error. Description format args passed as kwargs."""
        self.error = error
        self.location = location
        self.format_args = format_args

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        description = _ERR_DESCRIPTIONS.get(
            self.error, f"MISSING ERROR DESCRIPTION FOR ERROR TYPE {self.error}"
        ).format(**self.format_args)

        message = f"{description}\n"

        if self.location is None:
            return message

        single_line = (
            self.location.end_line_no is None
            or self.location.line_no == self.location.end_line_no
        )

        if single_line:
            message += f"At line {self.location.line_no}"
        else:
            message += (
                f"At lines {self.location.line_no} to {self.location.end_line_no}"
            )

        if self.location.line is not None:
            message += f":\n{self.location.line}"

            if self.location.start_col is not None and single_line:
                end_col = (
                    self.location.end_col
                    if self.location.end_col is not None
                    else len(self.location.line) - 1
                )

                message += (
                    "\n"
                    + " " * self.location.start_col
                    + "^" * (end_col - self.location.start_col)
                )

        return message
