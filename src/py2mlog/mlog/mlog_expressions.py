from dataclasses import dataclass
from typing import TypeAlias


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
class MlogVar:
    name: str


MlogExpr: TypeAlias = MlogBuiltin | MlogStringLiteral | MlogNumberLiteral | MlogVar
