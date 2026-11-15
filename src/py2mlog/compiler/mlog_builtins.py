from collections.abc import Mapping

from py2mlog.compiler.mimex_utils import (
    MIMEX_DATA_DIR,
    camel_to_snake,
    kebab_to_snake,
    select_col,
)
from py2mlog.mlog.mlog_expressions import MlogBuiltin, MlogExpr, MlogNullLiteral

# unsure if this belongs in compiler/ or mlog/


def _build_builtin_map(file_name: str) -> dict[str, MlogBuiltin]:
    return {
        kebab_to_snake(s): MlogBuiltin(s)
        for s in select_col(
            (MIMEX_DATA_DIR / file_name).read_text(encoding="utf-8"), "name"
        )
    }


# ----------------------------------------
# Units namespace (Units.*)
# ----------------------------------------
UNIT_MAP = _build_builtin_map("mimex-units.txt")


# ----------------------------------------
# Content (not in a specific namespace)
# ----------------------------------------
ITEM_MAP = _build_builtin_map("mimex-items.txt")
LIQUID_MAP = _build_builtin_map("mimex-liquids.txt")
BLOCK_MAP = _build_builtin_map("mimex-blocks.txt")

# TODO: cleanup
_block_data = (MIMEX_DATA_DIR / "mimex-blocks.txt").read_text(encoding="utf-8")
BUILDING_TYPES = {
    kebab_to_snake(s)
    for s, c in zip(
        select_col(_block_data, "name"),
        select_col(_block_data, "visibility"),
        strict=True,
    )
    if c == "shown"  # close enough ig
}
PAYLOADS = BUILDING_TYPES | set(UNIT_MAP)

_laccess_data = (MIMEX_DATA_DIR / "mimex-laccess.txt").read_text(
    encoding="utf-8"
)
LACCESS_SENSOR = {
    kebab_to_snake(s)
    for s, c in zip(
        select_col(_laccess_data, "name"),
        select_col(_laccess_data, "sensor"),
        strict=True,
    )
    if c == "true"
}

SENSOR_PROPERTIES = set(ITEM_MAP | LIQUID_MAP) | PAYLOADS | LACCESS_SENSOR

# ----------------------------------------
# Env namespace (Env.*)
# ----------------------------------------


CONTENT_MAP: Mapping[str, MlogBuiltin] = ITEM_MAP | LIQUID_MAP | BLOCK_MAP

SPECIAL_BUILTIN_MAP: Mapping[str, MlogBuiltin] = {
    camel_to_snake(s): MlogBuiltin(s)
    for s in (
        # Processor
        "this",
        "thisx",
        "thisy",
        # clashes with Env.links()
        # "links",
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
        "unit",
    )
}

MISC_ENV_ATTR_MAP = {
    "x": MlogBuiltin("thisx"),
    "y": MlogBuiltin("thisy"),
    "link_count": MlogBuiltin("links"),
    "null": MlogNullLiteral(),
}

ENV_ATTR_MAP: Mapping[str, MlogExpr] = (
    CONTENT_MAP | SPECIAL_BUILTIN_MAP | MISC_ENV_ATTR_MAP
)


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
