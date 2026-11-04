import logging
from collections.abc import Mapping
from importlib import resources

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


MLOG_BUILTIN_MAP: Mapping[str, MlogBuiltin] = {
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

ENV_ATTR_MAP: Mapping[str, MlogExpr] = MLOG_BUILTIN_MAP
