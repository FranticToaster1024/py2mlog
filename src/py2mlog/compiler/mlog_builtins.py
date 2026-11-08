from collections.abc import Mapping

from py2mlog.compiler.config import ALIAS
from py2mlog.compiler.mimex_utils import (
    MIMEX_DATA_DIR,
    kebab_to_snake,
    select_col,
)
from py2mlog.mlog.mlog_expressions import MlogBuiltin, MlogExpr

CONTENT_MAP: Mapping[str, MlogBuiltin] = {
    kebab_to_snake(s): MlogBuiltin(s)
    for file_name in (
        "mimex-items.txt",
        "mimex-liquids.txt",
        "mimex-blocks.txt",
    )
    for s in select_col(
        (MIMEX_DATA_DIR / file_name).read_text(encoding="utf-8"), "name"
    )
}

SPECIAL_BUILTIN_MAP: Mapping[str, MlogBuiltin] = {
    kebab_to_snake(s): MlogBuiltin(s)
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
