import logging
from textwrap import dedent

import pytest

from py2mlog.compiler.error import SourceLocation
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.mlog.parser import parse_mlog
from py2mlog.optimizer.optimizer import optimize

OPTIMIZER_SNIPPET_TESTCASES = [
    pytest.param(
        """
        jump l1 always
        l1:
        jump l2 equal x true
        l2:
        # no-op so that label doesn't wrap to top
        noop
        """,
        """
        noop
        """,
        id="jump-to-next-line",
    ),
    pytest.param(
        """
        jump l1 equal x true
        jump l2 always
        l1:
        noop
        l2:
        noop
        """,
        """
        jump l2 notEqual x true
        noop
        l2:
        noop
        """,
        id="wrapped-jump-always",
    ),
]


@pytest.mark.parametrize(("src", "expected"), OPTIMIZER_SNIPPET_TESTCASES)
def test_snippet(
    src: str, expected: str, caplog: pytest.LogCaptureFixture
) -> None:
    src = dedent(src).strip()
    expected_str = "\n".join(
        s for e in dedent(expected).split("\n") if (s := e.strip())
    )
    parsed_src = parse_mlog(src, SourceLocation(-1, None))

    assert generate_mlog(optimize(parsed_src)) == expected_str
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
