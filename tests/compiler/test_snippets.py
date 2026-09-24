import ast

import pytest

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        pytest.param(
            "\n".join(
                (
                    "integer = 123",
                    "float_ = 12.3",
                    'string = "str"',
                    "boolean = True",
                    "none = None",
                    "copy = value",
                )
            ),
            "\n".join(
                (
                    "set integer 123",
                    "set float_ 12.3",
                    'set string "str"',
                    "set boolean true",
                    "set none null",
                    "set copy value",
                )
            ),
            id="basic-assignment",
        ),
        pytest.param(
            "first = second = value",
            "\n".join(("set first value", "set second value")),
            id="multiple-assignment-targets",
        ),
        pytest.param(
            "result = (left + right) * factor",
            "\n".join(
                ("op add __p2m_tmp0 left right", "op mul result __p2m_tmp0 factor")
            ),
            id="nested-binary-operation",
        ),
        *[
            pytest.param(
                f"result = left {operator} right",
                f"op {mlog_operator} result left right",
                id=f"operator-{mlog_operator}",
            )
            for operator, mlog_operator in (
                ("+", "add"),
                ("-", "sub"),
                ("*", "mul"),
                ("/", "div"),
                ("//", "idiv"),
                ("%", "emod"),
                ("**", "pow"),
                ("&", "and"),
                ("|", "or"),
                ("^", "xor"),
                ("<<", "shl"),
                (">>", "shr"),
            )
        ],
        *[
            pytest.param(
                f"result = {operator}value",
                expected,
                id=f"unary-{name}",
            )
            for operator, expected, name in (
                ("+", "set result value", "plus"),
                ("-", "op sub result 0 value", "minus"),
                ("not ", "op notEqual result value true", "not"),
                ("~", "op not result value", "invert"),
            )
        ],
        pytest.param(
            "left + right",
            "op add __p2m_tmp0 left right",
            id="expression-statement",
        ),
    ],
)
def test_snippet(src: str, expected: str):
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    assert generate_mlog(emitter.instructions) == expected
