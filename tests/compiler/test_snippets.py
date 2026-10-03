import ast
from textwrap import dedent

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
                f"result {operator}= value",
                f"op {mlog_operator} result result value",
                id=f"augmented-assignment-{mlog_operator}",
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
        *[
            pytest.param(
                f"result = left {operator} right",
                f"op {mlog_operator} result left right",
                id=f"comparison-{mlog_operator}",
            )
            for operator, mlog_operator in (
                ("==", "equal"),
                ("!=", "notEqual"),
                ("<", "lessThan"),
                ("<=", "lessThanEq"),
                (">", "greaterThan"),
                (">=", "greaterThanEq"),
            )
        ],
        pytest.param(
            "result = first and second",
            "select result equal first true second first",
            id="boolean-and",
        ),
        pytest.param(
            "result = first or second",
            "select result equal second true second first",
            id="boolean-or",
        ),
        pytest.param(
            "result = first and second and third",
            "\n".join(
                (
                    "select result equal first true second first",
                    "select result equal result true third result",
                )
            ),
            id="chained-boolean-and",
        ),
        pytest.param(
            "result = first or second or third",
            "\n".join(
                (
                    "select result equal second true second first",
                    "select result equal third true third result",
                )
            ),
            id="chained-boolean-or",
        ),
        pytest.param(
            "result = left < middle <= right",
            "\n".join(
                (
                    "op lessThan result left middle",
                    "select result lessThanEq middle right result false",
                )
            ),
            id="chained-comparison-with-different-operators",
        ),
        pytest.param(
            "left + right",
            "op add __p2m_tmp0 left right",
            id="expression-statement",
        ),
        pytest.param(
            dedent("""
                if condition:
                    result = first
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label0 equal condition false",
                    "set result first",
                    "__p2m_label0:",
                )
            ),
            id="if-with-name-condition",
        ),
        pytest.param(
            dedent("""
                if x < 5:
                    x = x + 1
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label0 greaterThanEq x 5",
                    "op add x x 1",
                    "__p2m_label0:",
                )
            ),
            id="if-with-comparison-condition",
        ),
        pytest.param(
            dedent("""
                if condition:
                    result = first
                else:
                    result = second
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label0 equal condition false",
                    "set result first",
                    "jump __p2m_label1 always",
                    "__p2m_label0:",
                    "set result second",
                    "__p2m_label1:",
                )
            ),
            id="if-else",
        ),
        pytest.param(
            dedent("""
                if first_condition:
                    result = first
                elif second_condition:
                    result = second
                else:
                    result = fallback
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label0 equal first_condition false",
                    "set result first",
                    "jump __p2m_label1 always",
                    "__p2m_label0:",
                    "jump __p2m_label2 equal second_condition false",
                    "set result second",
                    "jump __p2m_label3 always",
                    "__p2m_label2:",
                    "set result fallback",
                    "__p2m_label3:",
                    "__p2m_label1:",
                )
            ),
            id="if-elif-else",
        ),
        pytest.param(
            dedent("""
                if first_condition:
                    result = first
                elif second_condition:
                    result = second
                elif third_condition:
                    result = third
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label0 equal first_condition false",
                    "set result first",
                    "jump __p2m_label1 always",
                    "__p2m_label0:",
                    "jump __p2m_label2 equal second_condition false",
                    "set result second",
                    "jump __p2m_label3 always",
                    "__p2m_label2:",
                    "jump __p2m_label4 equal third_condition false",
                    "set result third",
                    "__p2m_label4:",
                    "__p2m_label3:",
                    "__p2m_label1:",
                )
            ),
            id="if-multiple-elif-without-else",
        ),
        pytest.param(
            dedent("""
                while condition:
                    result = value
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 equal condition false",
                    "__p2m_label0:",
                    "set result value",
                    "jump __p2m_label0 equal condition true",
                    "__p2m_label1:",
                )
            ),
            id="while-with-name-condition",
        ),
        pytest.param(
            dedent("""
                while count < limit:
                    count = count + 1
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 greaterThanEq count limit",
                    "__p2m_label0:",
                    "op add count count 1",
                    "jump __p2m_label0 lessThan count limit",
                    "__p2m_label1:",
                )
            ),
            id="while-with-comparison-condition",
        ),
        pytest.param(
            dedent("""
                while outer_condition:
                    while inner_condition:
                        result = value
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 equal outer_condition false",
                    "__p2m_label0:",
                    "jump __p2m_label3 equal inner_condition false",
                    "__p2m_label2:",
                    "set result value",
                    "jump __p2m_label2 equal inner_condition true",
                    "__p2m_label3:",
                    "jump __p2m_label0 equal outer_condition true",
                    "__p2m_label1:",
                )
            ),
            id="nested-while-loops",
        ),
        pytest.param(
            dedent("""
                while condition:
                    break
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 equal condition false",
                    "__p2m_label0:",
                    "jump __p2m_label1 always",
                    "jump __p2m_label0 equal condition true",
                    "__p2m_label1:",
                )
            ),
            id="while-break",
        ),
        pytest.param(
            dedent("""
                while condition:
                    continue
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 equal condition false",
                    "__p2m_label0:",
                    "jump __p2m_label0 always",
                    "jump __p2m_label0 equal condition true",
                    "__p2m_label1:",
                )
            ),
            id="while-continue",
        ),
        pytest.param(
            dedent("""
                while outer_condition:
                    while inner_condition:
                        break
                    continue
            """).strip(),
            "\n".join(
                (
                    "jump __p2m_label1 equal outer_condition false",
                    "__p2m_label0:",
                    "jump __p2m_label3 equal inner_condition false",
                    "__p2m_label2:",
                    "jump __p2m_label3 always",
                    "jump __p2m_label2 equal inner_condition true",
                    "__p2m_label3:",
                    "jump __p2m_label0 always",
                    "jump __p2m_label0 equal outer_condition true",
                    "__p2m_label1:",
                )
            ),
            id="nested-while-break-continue",
        ),
        pytest.param(
            dedent("""
                assert False, "abc"
                x = 123
            """).strip(),
            "\n".join(
                (
                    'set __p2m_msg_err "abc"',
                    "jump __p2m_label_err_assert equal false false",
                    "set x 123",
                    "end",
                    "__p2m_label_err_assert:",
                    'print "[red]AssertionError: {0}.[]"',
                    "format __p2m_msg_err",
                    "stop",
                )
            ),
            id="assert-false-with-messsage",
        ),
        pytest.param(
            dedent("""
                assert x > y
                x += y
            """).strip(),
            "\n".join(
                (
                    'set __p2m_msg_err ""',
                    "jump __p2m_label_err_assert lessThanEq x y",
                    "op add x x y",
                    "end",
                    "__p2m_label_err_assert:",
                    'print "[red]AssertionError: {0}.[]"',
                    "format __p2m_msg_err",
                    "stop",
                )
            ),
            id="assert-comparison-without-messsage",
        ),
        pytest.param(
            dedent("""
                x = abs(x)
            """).strip(),
            "\n".join(("op abs x x",)),
            id="supported-builtin-functions",
        ),
    ],
)
def test_snippet(src: str, expected: str):
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    assert generate_mlog(emitter.instructions) == expected
