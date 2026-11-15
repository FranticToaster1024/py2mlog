from py2mlog import intrinsics
from py2mlog.compiler import config

# ----------------------------------------
# allowed namespaces or whatever
# ----------------------------------------
ALIAS_NAMESPACE_NAMES = {
    "Link": config.ALIAS.LINK,
}


BUILTIN_FUNC_NAMES = set(intrinsics.builtins.FUNC_MAP.keys())


INTRINSIC_NAMESPACE_NAMES = set(
    intrinsics.NAMESPACES_NAME_TO_FUNC_MAP_MAP.keys()
)


ALL_NAMESPACE_NAMES = (
    {
        "Env",
        "Links",
        "UnitType",
        "Align",  # for draw print alignments (see mimex-alignments.txt)
    }
    | BUILTIN_FUNC_NAMES
    | INTRINSIC_NAMESPACE_NAMES
    | {k for k, v in ALIAS_NAMESPACE_NAMES.items() if v}
)
