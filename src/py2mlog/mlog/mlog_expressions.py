from dataclasses import dataclass


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
