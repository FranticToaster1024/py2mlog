from dataclasses import dataclass
from types import NoneType
from typing import Any

from py2mlog._types import Content, _Color  # pyright: ignore[reportPrivateUsage]


@dataclass(frozen=True)
class LabelRef:
    name: str


class MlogExpr:
    pass


@dataclass(frozen=True)
class MlogFillerExpr(MlogExpr):
    """Use sparingly."""


@dataclass(frozen=True)
class MlogBuiltin(MlogExpr):
    name: str


@dataclass(frozen=True)
class MlogStringLiteral(MlogExpr):
    value: str


@dataclass(frozen=True)
class MlogNumberLiteral(MlogExpr):
    value: int | float


@dataclass(frozen=True)
class MlogBoolLiteral(MlogExpr):
    value: bool


@dataclass(frozen=True)
class MlogColorLiteral(MlogExpr):
    value: str


class MlogNullLiteral(MlogExpr):
    pass


@dataclass(frozen=True)
class MlogVar(MlogExpr):
    name: str


type MlogArg = MlogExpr | LabelRef


def get_val_str(expr: MlogExpr) -> str:
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
    MlogColorLiteral: _Color,
    MlogNullLiteral: NoneType,
    MlogVar: Any,
}
