import ast

import pytest

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import CompilerError, CompilerErrorType


def _test_error(src: str, error_type: CompilerErrorType):
    emitter = Emitter()

    with pytest.raises(CompilerError) as exc_info:
        Compiler(src, ast.parse(src), emitter).compile()

    assert exc_info.value.error == error_type


@pytest.mark.parametrize(
    ("src", "error_type"),
    [
        pytest.param(
            "break", CompilerErrorType.SYNTAX, id="break-outside-loop"
        ),
        pytest.param(
            "continue", CompilerErrorType.SYNTAX, id="continue-outside-loop"
        ),
    ],
)
def test_error(src: str, error_type: CompilerErrorType):
    _test_error(src, error_type)


@pytest.mark.parametrize(
    ("src", "error_type"),
    [
        pytest.param(
            (
                'exec("x = 123")',
                'eval("1 + 2")',
            ),
            CompilerErrorType.UNSUPPORTED,
            id="unsupported-builtin-functions",
        ),
        pytest.param(
            (
                "abs()",
                "abs(1, 2, 3)",
            ),
            CompilerErrorType.BAD_BUILTIN_CALL,
            id="bad-builtin-call",
        ),
    ],
)
def test_error_list(src: tuple[str], error_type: CompilerErrorType):
    for testcase in src:
        _test_error(testcase, error_type)
