from collections.abc import Mapping

from py2mlog.compiler.config import ALIAS
from py2mlog.compiler.mimex_utils import (
    MIMEX_DATA_DIR,
    camel_to_snake,
    kebab_to_snake,
    select_col,
)
from py2mlog.mlog.mlog_expressions import MlogBuiltin, MlogExpr, MlogNullLiteral

# unsure if this belongs in compiler/ or mlog/

# ----------------------------------------
# Env namespace (Env.*)
# ----------------------------------------
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
    camel_to_snake(s): MlogBuiltin(s)
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

MISC_ENV_ATTR_MAP = {
    "null": MlogNullLiteral(),
}

ENV_ATTR_MAP: Mapping[str, MlogExpr] = (
    CONTENT_MAP | SPECIAL_BUILTIN_MAP | MISC_ENV_ATTR_MAP
)


# ----------------------------------------
# UnitType namespace (UnitType.*)
# ----------------------------------------
UNIT_TYPE_MAP = {
    kebab_to_snake(s): MlogBuiltin(s)
    for s in select_col(
        (MIMEX_DATA_DIR / "mimex-units.txt").read_text(encoding="utf-8"), "name"
    )
}
# ----------------------------------------
# Align namespace (Align.*)
# ----------------------------------------
# for draw print alignments (e.g. '@topLeft')
ALIGN_MAP = {
    s: MlogBuiltin(raw_str)
    for raw_str in select_col(
        (MIMEX_DATA_DIR / "mimex-alignments.txt").read_text(encoding="utf-8"),
        "name",
    )
    # accept 'topLeft', 'top_left', 'topleft'
    for s in (raw_str, camel_to_snake(raw_str), raw_str.lower())
}


# ----------------------------------------
# allowed namespaces or whatever
# ----------------------------------------
ALIAS_NAMESPACES = {
    "Link": ALIAS.LINK,
}


# TODO: extract from builtin_funcs.py
EXTRA_BUILTIN_FUNCS = {
    "sleep",
    "wait",
}

MLOG_BUILTIN_NAMESPACES = (
    {
        "Env",
        "Links",
        "Color",
        "Screen",
        "UnitType",
        "Unit",
        "Align",  # for draw print alignments (see mimex-alignments.txt)
        "Mem",
    }
    | EXTRA_BUILTIN_FUNCS
    | {k for k, v in ALIAS_NAMESPACES.items() if v}
)
