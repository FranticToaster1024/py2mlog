import ast
from textwrap import dedent

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
    [],
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
                "abs(x=1)",
                "abs(1, 2, 3)",
                "ord()",
                "ord(1, 2)",
                "min()",
                # does Color() belong here? might need separate testcase
                "Color(True)",
                "Color(16777215.0)",
                "Color(1 + 2)",
            ),
            CompilerErrorType.BAD_CALL,
            id="bad-builtin-calls",
        ),
        pytest.param(
            (
                '"%abcde"',
                "Color(0xabcdefabc)",
                'Color("%abcde")',
                'Color("abcde")',
            ),
            CompilerErrorType.SYNTAX,
            id="bad-color-literals",
        ),
        pytest.param(
            ("break", "continue"),
            CompilerErrorType.SYNTAX,
            id="break-and-continue-outside-loop",
        ),
        pytest.param(
            (
                """
                while True:
                    def x():
                        break
                """,
                """
                while True:
                    def x():
                        continue
                """,
            ),
            CompilerErrorType.SYNTAX,
            id="break-and-continue-in-func-def-in-loop",
        ),
        pytest.param(
            (
                """
                while True:
                    @inline
                    def x():
                        break

                    x()  # inline func defers compilation to call site
                """,
                """
                while True:
                    @inline
                    def x():
                        continue

                    x()  # inline func defers compilation to call site
                """,
            ),
            CompilerErrorType.SYNTAX,
            id="break-and-continue-in-inline-func-def-in-loop",
        ),
    ],
)
def test_error_list(src: tuple[str, ...], error_type: CompilerErrorType):
    src = tuple(dedent(s).strip() for s in src)

    for testcase in src:
        _test_error(testcase, error_type)
