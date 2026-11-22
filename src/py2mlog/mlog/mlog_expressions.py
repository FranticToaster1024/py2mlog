from dataclasses import dataclass
from types import NoneType
from typing import Any

from py2mlog._types import ColorType, Content


@dataclass(frozen=True)
class LabelRef:
    name: str


@dataclass(frozen=True)
class MlogFillerExpr:
    """Use sparingly."""


@dataclass(frozen=True)
class MlogBuiltin:
    name: str


@dataclass(frozen=True)
class MlogStringLiteral:
    value: str


@dataclass(frozen=True)
class MlogNumberLiteral:
    value: int | float


@dataclass(frozen=True)
class MlogBoolLiteral:
    value: bool


@dataclass(frozen=True)
class MlogColorLiteral:
    value: str


class MlogNullLiteral:
    pass


@dataclass(frozen=True)
class MlogVar:
    name: str


MlogLiteral = (
    MlogStringLiteral
    | MlogNumberLiteral
    | MlogBoolLiteral
    | MlogColorLiteral
    | MlogNullLiteral
)
MlogExpr = MlogFillerExpr | MlogBuiltin | MlogLiteral | MlogVar
type MlogArg = MlogExpr | LabelRef


def get_mlog_expr_as_py_val_str(expr: MlogExpr) -> str:
    match expr:
        case MlogNullLiteral():
            return str(None)
        case MlogColorLiteral(value=value):
            return f'Color("%{value}")'
        case MlogStringLiteral(value=value):
            return repr(value)
        case MlogBoolLiteral() | MlogNumberLiteral():
            return str(expr.value)
        case _:
            return "..."


MLOG_EXPR_TYPE_MAP = {
    MlogExpr: Any,
    MlogBuiltin: Content,
    MlogStringLiteral: str,
    MlogNumberLiteral: float,  # linter yells if i use int | float
    MlogBoolLiteral: bool,
    MlogColorLiteral: ColorType,
    MlogNullLiteral: NoneType,
    MlogVar: Any,
}
