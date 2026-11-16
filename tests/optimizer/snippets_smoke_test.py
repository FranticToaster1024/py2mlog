import logging
from textwrap import dedent

import pytest

from py2mlog.api import compile_src_to_mlog
from tests.compiler.test_snippets import COMPILER_SNIPPET_TESTCASES


@pytest.mark.parametrize(
    "src",
    [
        pytest.param(t.values[0], marks=t.marks, id=t.id)
        for t in COMPILER_SNIPPET_TESTCASES
    ],
)
def test_snippets(src: str, caplog: pytest.LogCaptureFixture) -> None:
    src = dedent(src).strip()
    compile_src_to_mlog(src)

    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
