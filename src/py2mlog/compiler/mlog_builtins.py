import logging
from collections.abc import Mapping
from importlib import resources

from py2mlog.compiler.config import ALIAS
from py2mlog.mlog.mlog_expressions import MlogBuiltin, MlogExpr

logger = logging.getLogger(__name__)

mimex_data_dir = resources.files("py2mlog") / "mimex_data/data/be/"


def _kebab_to_camel(s: str) -> str:
    s_ = s.strip("-")
    if s != s_:
        logger.warning(
            "Removed starting or trailing hyphen in string '%s' "
            "when converting kebab-case to camelCase",
            s,
        )
        s = s_

    words = s.split("-")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def _select_col(data: str, col_name: str) -> list[str]:
    col_no: int | None = None
    col: list[str] = []

    for row in data.split("\n"):
        if not row or row.startswith(("//", "#")):
            continue

        if col_no is None:
            col_no = row.split(";").index(col_name)
            continue

        # IndexError? too bad
        col.append(row.split(";")[col_no])

    return col


CONTENT_MAP: Mapping[str, MlogBuiltin] = {
    _kebab_to_camel(s): MlogBuiltin(s)
    for file_name in (
        "mimex-items.txt",
        "mimex-liquids.txt",
        "mimex-blocks.txt",
    )
    for s in _select_col(
        (mimex_data_dir / file_name).read_text(encoding="utf-8"), "name"
    )
}

SPECIAL_BUILTIN_MAP: Mapping[str, MlogBuiltin] = {
    _kebab_to_camel(s): MlogBuiltin(s)
    for s in (
        # Processor
        "this",
        "thisx",
        "thisy",
        "links",
        "ipt",
        # General
        "pi",
        "e",
        "degToRad",
        "radToDeg",
        # Map
        "time",
        "tick",
        "second",
        "minute",
        "waveNumber",
        "waveTime",
        "mapw",
        "maph"
        # Network/clientside (wproc only)
        "server",
        "client",
        "clientLocale",
        "clientUnit",
        "clientName",
        "clientTeam",
        "clientMobile",
        "clientMusicPlaying",
        "clientCurrentMusic",
        # Lookup
        "blockCount",
        "unitCount",
        "itemCount",
        "liquidCount",
        # Misc
        "counter",
    )
}

ENV_ATTR_MAP: Mapping[str, MlogExpr] = CONTENT_MAP | SPECIAL_BUILTIN_MAP


ALIAS_NAMESPACES = {
    "Link": ALIAS.LINK,
}

MLOG_BUILTIN_NAMESPACES = {
    "Env",
    "Links",
    "Color",
} | {k for k, v in ALIAS_NAMESPACES.items() if v}
