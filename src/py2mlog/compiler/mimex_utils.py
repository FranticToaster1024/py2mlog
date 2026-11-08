import logging
from importlib import resources

logger = logging.getLogger(__name__)


MIMEX_DATA_DIR = resources.files("py2mlog") / "mimex_data/data/be/"


def kebab_to_snake(s: str) -> str:
    s_ = s.strip("-")
    if s != s_:
        logger.warning(
            "Removed starting or trailing hyphen in string '%s' "
            "when converting kebab-case to snake_case",
            s,
        )
        s = s_

    return s.lower().replace("-", "_")


def kebab_to_camel(s: str) -> str:
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


def select_col(data: str, col_name: str) -> list[str]:
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
