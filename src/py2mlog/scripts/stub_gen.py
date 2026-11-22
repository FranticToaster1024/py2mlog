import logging
import subprocess
import sys
import typing
from functools import reduce
from inspect import Parameter, getdoc, signature
from pathlib import Path
from textwrap import indent
from types import NoneType
from typing import Any

import py2mlog
from py2mlog import intrinsics
from py2mlog.compiler import config
from py2mlog.compiler.mlog_builtins import (
    ALIGN_MAP,
    BLOCK_MAP,
    COLOR_MAP,
    ITEM_MAP,
    LACCESS_SENSOR,
    LIQUID_MAP,
    PAYLOADS,
    UNIT_MAP,
)
from py2mlog.intrinsics.intrinsic_func_utils import (
    IntrinsicFuncMap,
    generate_alias,
)
from py2mlog.mlog.mlog_expressions import (
    MLOG_EXPR_TYPE_MAP,
    get_mlog_expr_as_py_val_str,
)

logger = logging.getLogger(__name__)


INDENT = " " * 4


# 'helpers' for relative names
# e.g. 'Content' instead of py2mlog._base.Content
def _relative_name(annotation: Any) -> str:
    types = typing.get_args(annotation)
    if not types:
        return (
            "None"
            if annotation is NoneType
            else getattr(annotation, "__name__", str(annotation))
        )

    return " | ".join(map(_relative_name, types))


# sig calls repr of non-types when formatting a signature as str
# with just str it gives 'abc' with the quotes
class _Name(str):
    __slots__ = ()
    __repr__ = str.__str__


def _get_relative_name(annotation: Any) -> _Name:
    return _Name(_relative_name(annotation))


def _map_intrinsic_func_annotation(annotation: Any) -> Any:
    mapped = MLOG_EXPR_TYPE_MAP.get(annotation, ...)
    if mapped is not ...:
        return mapped

    types = typing.get_args(annotation)
    if not types:
        logger.warning(
            "Unmapped non-union type '%s' when generating stubs. "
            "Defaulting to 'Any'.",
            annotation,
        )
        return Any

    return reduce(
        lambda a, b: a | b,
        (m for t in types if (m := MLOG_EXPR_TYPE_MAP.get(t, ...)) is not ...),
    )


def _stubs_from_func_map(
    func_map: IntrinsicFuncMap,
    *,
    exclude: tuple[str, ...] = (),
    is_method: bool = True,
) -> str:
    exclude_aliases = {a for e in exclude for a in generate_alias(e)}

    s: list[str] = []
    for k, f in func_map.items():
        if k in exclude_aliases:
            continue
        if f is None:
            continue

        sig = signature(f)

        new_params = [
            p.replace(
                annotation=_get_relative_name(
                    _map_intrinsic_func_annotation(p.annotation)
                ),
                default=(
                    Parameter.empty
                    if p.default is Parameter.empty
                    else _Name(get_mlog_expr_as_py_val_str(p.default))
                ),
            )
            for p in list(sig.parameters.values())[1:]
        ]
        new_return = _get_relative_name(
            _map_intrinsic_func_annotation(sig.return_annotation)
        )

        new_sig = sig.replace(
            parameters=new_params, return_annotation=new_return
        )

        if is_method:
            s.append(f"{INDENT}@staticmethod")

        base_indent = INDENT if is_method else ""
        s.append(f"{base_indent}def {k}{new_sig!s}:")

        docstring = getdoc(f)
        if docstring is None:
            s.append(f"{base_indent}{INDENT}...")
        else:
            s.append(f'{base_indent}{INDENT}"""')
            s.append(f"{base_indent}{indent(docstring, INDENT)}")
            s.append(f'{base_indent}{INDENT}"""')

    return "\n".join(s)


# if the class has a dunder method that needs an instance
# remember to 'create' the instance
gen = f"""
from abc import ABC
from collections.abc import Iterator
from typing import Any, Literal, LiteralString, overload

from py2mlog._types import ColorType, Content

class Item(Content): ...
class Liquid(Content): ...

class Block(Content):
    \"""
    Includes terrain blocks, not just building types.
    \"""

class UnitType(Content): ...

class Senseable(ABC):
    def __getitem__(self, i: Item | Liquid | str | Any) -> Any: ...
{"\n".join(f"{INDENT}{s}: int" for s in ITEM_MAP | LIQUID_MAP | PAYLOADS)}
    # TODO: manually type these attributes or something
{"\n".join(f"{INDENT}{s}: Any" for s in sorted(LACCESS_SENSOR))}


class Controllable(ABC):
    def enabled(self, enabled: bool | int) -> None: ...
    def enable(self) -> None: ...
    def disable(self) -> None: ...
    def shoot(self, x: float, y: float, shoot: bool | int = True) -> None: ...
    def ceasefire(self) -> None: ...
    def shootp(self, unit: UnitObj, shoot: bool | int = True) -> None: ...
    def color(self, color: ColorType) -> None: ...
    def config(self, config: Any) -> None: ...


class Building(Senseable, Controllable): ...
class UnitObj(Senseable): ...





class Env:
    # Processor
    this: Building
    thisx: float
    thisy: float
    ipt: float

    # General
    pi: float
    e: float
    deg_to_rad: float
    rad_to_deg: float

    # Map
    time: float
    tick: float
    second: float
    minute: float
    wave_number: int
    wave_time: float
    mapw: float
    maph: float

    # Network/clientside (wproc only)
    # TODO: properly type these
    server: Any
    client: Any
    client_locale: Any
    client_unit: Any
    client_name: Any
    client_team: Any
    client_mobile: Any
    client_music_playing: Any
    client_current_music: Any

    # Lookup
    block_count: int
    unit_count: int
    item_count: int
    liquid_count: int

    # Misc
    counter: int
    unit: UnitObj

    # Special (manually defined)
    x: float
    y: float
    link_count: int
    null: None

{"\n".join(f"{INDENT}{s}: Item" for s in ITEM_MAP)}
{"\n".join(f"{INDENT}{s}: Liquid" for s in LIQUID_MAP)}
{"\n".join(f"{INDENT}{s}: Block" for s in BLOCK_MAP)}

    @staticmethod
    def links() -> Iterator[Building]:
        \"""
        Only available as iterable target in for loops.
        \"""


class Alignment: ...

class Align:
{"\n".join(f"{INDENT}{s}: Alignment" for s in ALIGN_MAP)}


class Units:
{"\n".join(f"{INDENT}{s}: UnitObj" for s in UNIT_MAP)}


class Colors:
{"\n".join(f"{INDENT}{s}: ColorType" for s in COLOR_MAP)}





def print(
    *args: Any,
    sep: str = " ",
    end: str = r"\\n",
    flush: Building | Literal[False] = ...,
) -> None:
    \"""
    Param 'flush' defaults to 'message1'. Set 'flush' to False to omit 'printflush'.
    \"""

def mlog_raw(src: LiteralString, /) -> None:
    \"""
    Emit raw mlog. Use a raw string so that escape sequences work properly.
    \"""

def radar(
    building: Building,
    filter1: str | Any = "any",
    filter2: str | Any = "any",
    filter3: str | Any = "any",
    /,
    *,
    order: bool | float | str = True,
    key: str = "distance",
) -> UnitObj | None: ...

{
    _stubs_from_func_map(
        intrinsics.builtins.FUNC_MAP, is_method=False, exclude=("radar",)
    )
}





class Unit:
    @staticmethod
    def bind(type: str | UnitType | UnitObj, /) -> None: ...


    @staticmethod
    def radar(
        filter1: str | Any = "any",
        filter2: str | Any = "any",
        filter3: str | Any = "any",
        /,
        *,
        order: bool | float | str = True,
        key: str = "distance",
    ) -> UnitObj | None: ...


    @overload
    @staticmethod
    # Any here for var name as subop name (e.g. subop=ore instead of subop="ore")
    def locate(
        subop: Literal["ore"] | Any, /, *, ore_type: Item
    ) -> tuple[float, float, bool]: ...

    @overload
    @staticmethod
    def locate(
        subop: Literal["building"] | Any,
        /,
        *,
        block_flag: str | Any,
        is_enemy_building: bool | int | str,
    ) -> tuple[float, float, bool, Building | None]: ...

    @overload
    @staticmethod
    def locate(
        subop: Literal["spawn", "damaged"] | Any, /
    ) -> tuple[float, float, bool, Building | None]: ...


    @overload
    @staticmethod
    def shoot() -> None: ...

    @overload
    @staticmethod
    def shoot(x: float, y: float) -> None: ...

    @staticmethod
    def targetp(unit: Unit, shoot: bool | int) -> None: ...

{
    "\n".join(
        f"{INDENT}{func_name} = targetp"
        for func_name in generate_alias("target_unit")
    )
}


{
    "\n".join(
        f"{INDENT}@staticmethod\n"
        f"{INDENT}def {func_name}(to: Building, amount: float) -> None: ..."
        for func_name in generate_alias("item_drop")
    )
}

    store = item_drop


{
    "\n".join(
        f"{INDENT}@staticmethod\n"
        f"{INDENT}def {func_name}(from_: Building, item: Item, amount: float) -> None: ..."
        for func_name in generate_alias("item_take")
    )
}

    fetch = item_take


    @staticmethod
    def build(
        x: float,
        y: float,
        block: Block,
        rotation: float = 0,
        config: Any = None,
    ) -> None: ...
{
    _stubs_from_func_map(
        intrinsics.unit.FUNC_MAP,
        exclude=(
            "locate",
            "radar",
            "bind",
            "shoot",
            "targetp",
            "target_unit",
            "item_drop",
            "store",
            "item_take",
            "fetch",
            "build",
        ),
    )
}



class Screen:
    @staticmethod
    def flush(target: Building) -> None: ...
    @staticmethod
    def print(x: float, y: float, alignment: Alignment) -> None: ...
{_stubs_from_func_map(intrinsics.screen.FUNC_MAP, exclude=("flush", "print"))}



class Control:
    # something something DRY
    @staticmethod
    def enabled(building: Building, enabled: bool | int) -> None: ...
    @staticmethod
    def enable(building: Building) -> None: ...
    @staticmethod
    def disable(building: Building) -> None: ...
    @staticmethod
    def shoot(
        building: Building, x: float, y: float, shoot: bool | int = True
    ) -> None: ...
    @staticmethod
    def ceasefire(building: Building) -> None: ...
    @staticmethod
    def shootp(
        building: Building, unit: UnitObj, shoot: bool | int = True
    ) -> None: ...
    @staticmethod
    def color(building: Building, color: ColorType) -> None: ...
    @staticmethod
    def config(building: Building, config: Any) -> None: ...





class _Links:
    def __getitem__(self, index: int) -> Building: ...

Links: _Links
{"Link: _Links" if config.ALIAS.LINK else ""}





class MemBuilding(Building):
    # in compiler.py, Mem.foo[etc] gets its own branch
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: int,
    ) -> Any: ...
    def __setitem__(self, index: int, value: Any) -> None: ...

class _Mem:
    def __getattr__(self, name: str) -> MemBuilding: ...

    # can't really generate MemBuilding
    @staticmethod
    def read(cell: MemBuilding | str, index: int) -> Any: ...
    @staticmethod
    def write(value: int, cell: MemBuilding, index: int) -> Any: ...
{_stubs_from_func_map(intrinsics.mem.FUNC_MAP, exclude=("read", "write"))}

# so that the __getattr__ actually works
# you can still access staticmethods from an instance
Mem: _Mem

"""

# py2mlog.__file__ points to the __init__.py(i) not directory apparently
gen_path = (Path(py2mlog.__file__).parent / "_gen.pyi").resolve()
gen_path.write_text(gen, encoding="utf-8")


# linting errors might be important
subprocess.run([sys.executable, "-m", "ruff", "check", gen_path], check=True)
subprocess.run([sys.executable, "-m", "ruff", "format", gen_path], check=True)
subprocess.run([sys.executable, "-m", "pyright", gen_path], check=True)


sys.stdout.write("Successfully generated stub :D\n")
