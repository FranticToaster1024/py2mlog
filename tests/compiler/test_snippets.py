from textwrap import dedent

import pytest

from py2mlog.api import compile_src_to_mlog

_test_snippet_testcases = [
    pytest.param("pass", ("",), id="pass"),
    pytest.param(
        "\n".join(
            (
                "integer = 123",
                "float_ = 12.3",
                'string = "str"',
                "boolean = True",
                "none = None",
                "copy = value",
                'col_lit_from_str = "%ffffff"',
                'col_lit_from_builtin = Color("%ffffff")',
                'col_lit_from_builtin = Color("ffffff")',
                'col_lit_from_builtin = Color("ffffffff")',
                "col_lit_from_builtin = Color(0xffffff)",
                "col_lit_from_builtin = Color(0xffffffff)",
            )
        ),
        (
            "set integer 123",
            "set float_ 12.3",
            'set string "str"',
            "set boolean true",
            "set none null",
            "set copy value",
            "set col_lit_from_str %ffffff",
            "set col_lit_from_builtin %ffffff",
            "set col_lit_from_builtin %ffffff",
            "set col_lit_from_builtin %ffffffff",
            "set col_lit_from_builtin %ffffff",
            "set col_lit_from_builtin %ffffffff",
        ),
        id="basic-assignment-and-types",
    ),
    pytest.param(
        "first = second = third = value",
        (
            "set first value",
            "set second first",
            "set third first",
        ),
        id="multiple-assignment-targets",
    ),
    pytest.param(
        "result = (left + right) * factor",
        (
            "op add __p2m_tmp0 left right",
            "op mul result __p2m_tmp0 factor",
        ),
        id="nested-binary-operation",
    ),
    *[
        pytest.param(
            f"result = left {operator} right",
            (f"op {mlog_operator} result left right",),
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
            (f"op {mlog_operator} result result value",),
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
    pytest.param(
        "\n".join(
            (
                "uadd_var = +var",
                "uadd_num = +1.23",
                "usub_var = -var",
                "usub_num = -1.23",
                "double_usub_num = -(-1.23)",
                "invert_var = ~var",
                "invert_int = ~123",
            )
        ),
        (
            "set uadd_var var",
            "set uadd_num 1.23",
            "op sub usub_var 0 var",
            "set usub_num -1.23",
            "set double_usub_num 1.23",
            "op not invert_var var",
            "set invert_int -124",
        ),
        id="unary-ops",
    ),
    *[
        pytest.param(
            f"result = left {operator} right",
            (f"op {mlog_operator} result left right",),
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
        ("select result equal first true second first",),
        id="boolean-and",
    ),
    pytest.param(
        "result = first or second",
        ("select result equal second true second first",),
        id="boolean-or",
    ),
    pytest.param(
        "result = first and second and third",
        (
            "select result equal first true second first",
            "select result equal result true third result",
        ),
        id="chained-boolean-and",
    ),
    pytest.param(
        "result = first or second or third",
        (
            "select result equal second true second first",
            "select result equal third true third result",
        ),
        id="chained-boolean-or",
    ),
    pytest.param(
        "result = left < middle <= right",
        (
            "op lessThan result left middle",
            "select result lessThanEq middle right result false",
        ),
        id="chained-comparison-with-different-operators",
    ),
    pytest.param(
        "left + right",
        ("op add __p2m_tmp0 left right",),
        id="expression-statement",
    ),
    pytest.param(
        """
        if condition:
            result = first
        """,
        (
            "__p2m_label0:",
            "jump __p2m_label0 equal condition false",
            "set result first",
        ),
        id="if-with-name-condition",
    ),
    pytest.param(
        """
        if x < 5:
            x = x + 1
        """,
        (
            "__p2m_label0:",
            "jump __p2m_label0 greaterThanEq x 5",
            "op add x x 1",
        ),
        id="if-with-comparison-condition",
    ),
    pytest.param(
        """
        if condition:
            result = first
        else:
            result = second
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label0 equal condition false",
            "set result first",
            "jump __p2m_label1 always",
            "__p2m_label0:",
            "set result second",
        ),
        id="if-else",
    ),
    pytest.param(
        """
        if first_condition:
            result = first
        elif second_condition:
            result = second
        else:
            result = fallback
        """,
        (
            "__p2m_label3:",
            "__p2m_label1:",
            "jump __p2m_label0 equal first_condition false",
            "set result first",
            "jump __p2m_label1 always",
            "__p2m_label0:",
            "jump __p2m_label2 equal second_condition false",
            "set result second",
            "jump __p2m_label3 always",
            "__p2m_label2:",
            "set result fallback",
        ),
        id="if-elif-else",
    ),
    pytest.param(
        """
        if first_condition:
            result = first
        elif second_condition:
            result = second
        elif third_condition:
            result = third
        """,
        (
            "__p2m_label4:",
            "__p2m_label3:",
            "__p2m_label1:",
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
        ),
        id="if-multiple-elif-without-else",
    ),
    pytest.param(
        """
        while condition:
            result = value
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal condition false",
            "__p2m_label0:",
            "set result value",
            "jump __p2m_label0 equal condition true",
        ),
        id="while-with-name-condition",
    ),
    pytest.param(
        """
        while count < limit:
            count = count + 1
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 greaterThanEq count limit",
            "__p2m_label0:",
            "op add count count 1",
            "jump __p2m_label0 lessThan count limit",
        ),
        id="while-with-comparison-condition",
    ),
    pytest.param(
        """
        while outer_condition:
            while inner_condition:
                result = value
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal outer_condition false",
            "__p2m_label0:",
            "jump __p2m_label3 equal inner_condition false",
            "__p2m_label2:",
            "set result value",
            "jump __p2m_label2 equal inner_condition true",
            "__p2m_label3:",
            "jump __p2m_label0 equal outer_condition true",
        ),
        id="nested-while-loops",
    ),
    pytest.param(
        """
        while condition:
            break
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal condition false",
            "__p2m_label0:",
            "jump __p2m_label1 always",
            "jump __p2m_label0 equal condition true",
        ),
        id="while-break",
    ),
    pytest.param(
        """
        while condition1:
            if condition2:
                break

            x += 10
            break
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal condition1 false",
            "__p2m_label0:",
            # could use optimization here as well
            "jump __p2m_label2 equal condition2 false",
            "jump __p2m_label1 always",
            "__p2m_label2:",
            "op add x x 10",
            "jump __p2m_label1 always",
            "jump __p2m_label0 equal condition1 true",
        ),
        id="while-multiple-break",
    ),
    pytest.param(
        """
        while condition:
            continue
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal condition false",
            "__p2m_label0:",
            "jump __p2m_label2 always",
            "__p2m_label2:",
            "jump __p2m_label0 equal condition true",
        ),
        id="while-continue",
    ),
    pytest.param(
        """
        while condition:
            result = False
        else:
            result = True
        """,
        (
            "jump __p2m_label1 equal condition false",
            "__p2m_label0:",
            "set result false",
            "jump __p2m_label0 equal condition true",
            "__p2m_label1:",
            "set result true",
        ),
        id="while-else-without-break",
    ),
    pytest.param(
        """
        while condition:
            result = False
            break
        else:
            result = True
        """,
        (
            "__p2m_label2:",
            "jump __p2m_label1 equal condition false",
            "__p2m_label0:",
            "set result false",
            "jump __p2m_label2 always",
            "jump __p2m_label0 equal condition true",
            "__p2m_label1:",
            "set result true",
        ),
        id="while-else-with-break",
    ),
    pytest.param(
        """
        while outer_condition:
            while inner_condition:
                break
            continue
        """,
        (
            "__p2m_label1:",
            "jump __p2m_label1 equal outer_condition false",
            "__p2m_label0:",
            "jump __p2m_label3 equal inner_condition false",
            "__p2m_label2:",
            "jump __p2m_label3 always",
            "jump __p2m_label2 equal inner_condition true",
            "__p2m_label3:",
            "jump __p2m_label4 always",
            "__p2m_label4:",
            "jump __p2m_label0 equal outer_condition true",
        ),
        id="nested-while-break-continue",
    ),
    pytest.param(
        """
        for index in range(5):
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 0",
            "op sub __p2m_tmp0 index 5",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-one-literal",
    ),
    pytest.param(
        """
        for index in range(2, 8):
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 2",
            "op sub __p2m_tmp0 index 8",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-start-stop-literals",
    ),
    pytest.param(
        """
        for index in range(1, 10, 2):
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 1",
            "op sub __p2m_tmp0 index 10",
            "op idiv __p2m_tmp0 __p2m_tmp0 2",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 2",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index 2",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-start-stop-step-literals",
    ),
    pytest.param(
        """
        for index in range(stop):
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 0",
            "op sub __p2m_tmp0 index stop",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-identifier",
    ),
    pytest.param(
        """
        for index in range(start, stop, step):
            result = index
        """,
        (
            "__p2m_label1:",
            "set index start",
            "op sub __p2m_tmp0 index stop",
            "op idiv __p2m_tmp0 __p2m_tmp0 step",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 step",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index step",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-identifiers",
    ),
    pytest.param(
        """
        for index in range(start + offset, limit * 2, step + 1):
            result = index
        """,
        (
            "__p2m_label1:",
            "op add index start offset",
            "op mul __p2m_tmp0 limit 2",
            "op add __p2m_tmp1 step 1",
            "op sub __p2m_tmp2 index __p2m_tmp0",
            "op idiv __p2m_tmp2 __p2m_tmp2 __p2m_tmp1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp2 0",
            "op mul __p2m_tmp2 __p2m_tmp2 __p2m_tmp1",
            "op sub __p2m_tmp2 index __p2m_tmp2",
            "__p2m_label0:",
            "set result index",
            "op add index index __p2m_tmp1",
            "jump __p2m_label0 notEqual index __p2m_tmp2",
        ),
        id="for-range-binary-expressions",
    ),
    pytest.param(
        """
        for outer in range(3):
            for inner in range(outer):
                result = outer + inner
        """,
        (
            "__p2m_label1:",
            "set outer 0",
            "op sub __p2m_tmp0 outer 3",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 outer __p2m_tmp0",
            "__p2m_label0:",
            "set inner 0",
            "op sub __p2m_tmp1 inner outer",
            "op idiv __p2m_tmp1 __p2m_tmp1 1",
            "jump __p2m_label3 greaterThanEq __p2m_tmp1 0",
            "op mul __p2m_tmp1 __p2m_tmp1 1",
            "op sub __p2m_tmp1 inner __p2m_tmp1",
            "__p2m_label2:",
            "op add result outer inner",
            "op add inner inner 1",
            "jump __p2m_label2 notEqual inner __p2m_tmp1",
            "__p2m_label3:",
            "op add outer outer 1",
            "jump __p2m_label0 notEqual outer __p2m_tmp0",
        ),
        id="nested-for-range",
    ),
    pytest.param(
        """
        for index in range(10):
            if should_stop:
                break
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 0",
            "op sub __p2m_tmp0 index 10",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            # optimization available again
            "jump __p2m_label2 equal should_stop false",
            "jump __p2m_label1 always",
            "__p2m_label2:",
            "set result index",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-break",
    ),
    pytest.param(
        """
        for index in range(10):
            if should_skip:
                continue
            result = index
        """,
        (
            "__p2m_label1:",
            "set index 0",
            "op sub __p2m_tmp0 index 10",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            # ¯\_(ツ)_/¯
            "jump __p2m_label2 equal should_skip false",
            "jump __p2m_label3 always",
            "__p2m_label2:",
            "set result index",
            "__p2m_label3:",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
        ),
        id="for-range-continue",
    ),
    pytest.param(
        """
        for index in range(5):
            result = index
        else:
            completed = True
        """,
        (
            "set index 0",
            "op sub __p2m_tmp0 index 5",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "set result index",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
            "__p2m_label1:",
            "set completed true",
        ),
        id="for-range-else-without-break",
    ),
    pytest.param(
        """
        for index in range(5):
            if should_stop:
                break
        else:
            completed = True
        """,
        (
            "__p2m_label3:",
            "set index 0",
            "op sub __p2m_tmp0 index 5",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 index __p2m_tmp0",
            "__p2m_label0:",
            "jump __p2m_label2 equal should_stop false",
            "jump __p2m_label3 always",
            "__p2m_label2:",
            "op add index index 1",
            "jump __p2m_label0 notEqual index __p2m_tmp0",
            "__p2m_label1:",
            "set completed true",
        ),
        id="for-range-else-with-break",
    ),
    pytest.param(
        """
        for outer in range(3):
            for inner in range(4):
                if should_stop:
                    break
                if should_skip:
                    continue
                result = outer + inner
        """,
        (
            "__p2m_label1:",
            "set outer 0",
            "op sub __p2m_tmp0 outer 3",
            "op idiv __p2m_tmp0 __p2m_tmp0 1",
            "jump __p2m_label1 greaterThanEq __p2m_tmp0 0",
            "op mul __p2m_tmp0 __p2m_tmp0 1",
            "op sub __p2m_tmp0 outer __p2m_tmp0",
            "__p2m_label0:",
            "set inner 0",
            "op sub __p2m_tmp1 inner 4",
            "op idiv __p2m_tmp1 __p2m_tmp1 1",
            "jump __p2m_label3 greaterThanEq __p2m_tmp1 0",
            "op mul __p2m_tmp1 __p2m_tmp1 1",
            "op sub __p2m_tmp1 inner __p2m_tmp1",
            "__p2m_label2:",
            "jump __p2m_label4 equal should_stop false",
            "jump __p2m_label3 always",
            "__p2m_label4:",
            "jump __p2m_label5 equal should_skip false",
            "jump __p2m_label6 always",
            "__p2m_label5:",
            "op add result outer inner",
            "__p2m_label6:",
            "op add inner inner 1",
            "jump __p2m_label2 notEqual inner __p2m_tmp1",
            "__p2m_label3:",
            "op add outer outer 1",
            "jump __p2m_label0 notEqual outer __p2m_tmp0",
        ),
        id="nested-for-range-break-continue",
    ),
    pytest.param(
        """
        assert False, "abc"
        x = 123
        """,
        (
            'set __p2m_msg_err "abc"',
            "jump __p2m_label_err_assert equal false false",
            "set x 123",
            "end",
            "__p2m_label_err_assert:",
            'print "[red]AssertionError: {0}.[]"',
            "format __p2m_msg_err",
            "stop",
        ),
        id="assert-false-with-messsage",
    ),
    pytest.param(
        """
        assert x > y
        x += y
        """,
        (
            'set __p2m_msg_err ""',
            "jump __p2m_label_err_assert lessThanEq x y",
            "op add x x y",
            "end",
            "__p2m_label_err_assert:",
            'print "[red]AssertionError: {0}.[]"',
            "format __p2m_msg_err",
            "stop",
        ),
        id="assert-comparison-without-messsage",
    ),
    pytest.param(
        """
        x = ord('a')
        x = min(a, 2)
        # x = min(1, 2, a, b)
        sleep(10)
        x = wait(a)  # why would you do this though

        # generated from subop
        x = flip(a)
        x = abs(a)
        x = sign(a)
        x = log(a)
        x = log10(a)
        x = floor(a)
        x = ceil(a)
        x = round(a)
        x = sqrt(a)
        x = rand(a)
        x = sin(a)
        x = cos(a)
        x = tan(a)
        x = asin(a)
        x = acos(a)
        x = atan(a)
        """,
        (
            'read x "a" 0',
            "op min x 2 a",
            # "op min __p2m_tmp0 b a",
            # "op min __p2m_tmp1 __p2m_tmp0 2",
            # "op min x __p2m_tmp1 1",
            "wait 10",
            "wait a",
            "set x null",
            # generated from subop
            "op not x a",
            "op abs x a",
            "op sign x a",
            "op log x a",
            "op log10 x a",
            "op floor x a",
            "op ceil x a",
            "op round x a",
            "op sqrt x a",
            "op rand x a",
            "op sin x a",
            "op cos x a",
            "op tan x a",
            "op asin x a",
            "op acos x a",
            "op atan x a",
        ),
        id="supported-inline-builtin-functions",
    ),
    pytest.param(
        "\n".join(
            (
                "a = b if condition else d",
                'a = 1 if b == c else "str"',
                "a = None if b < c else -1.23",
            )
        ),
        (
            "select a equal condition true b d",
            'select a equal b c 1 "str"',
            "select a lessThan b c null -1.23",
        ),
        id="ifexp-to-select",
    ),
    pytest.param(
        "a = abs(b) + c + d if e >= f else g * h - i * j",
        (
            "__p2m_label1:",
            "jump __p2m_label0 lessThan e f",
            "op abs __p2m_tmp1 b",
            "op add __p2m_tmp0 __p2m_tmp1 c",
            "op add a __p2m_tmp0 d",
            "jump __p2m_label1 always",
            "__p2m_label0:",
            "op mul __p2m_tmp2 g h",
            "op mul __p2m_tmp3 i j",
            "op sub a __p2m_tmp2 __p2m_tmp3",
        ),
        id="ifexp-to-branches",
    ),
    pytest.param(
        """
        def get_value():
            return 42

        result = get_value()
        """,
        (
            "op add __p2m_func_scope_get_value.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_get_value.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_get_value.__p2m_func_ret_val 42",
            "set @counter __p2m_func_scope_get_value.__p2m_func_ret_addr",
        ),
        id="function-without-parameters",
    ),
    pytest.param(
        """
        def add(left, right):
            return left + right

        result = add(2, 3)
        """,
        (
            "set __p2m_func_scope_add.__p2m_func_arg_left 2",
            "set __p2m_func_scope_add.__p2m_func_arg_right 3",
            "op add __p2m_func_scope_add.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_add.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            # reasonable-length function names mhm
            "op add __p2m_func_scope_add.__p2m_func_ret_val "
            "__p2m_func_scope_add.__p2m_func_arg_left "
            "__p2m_func_scope_add.__p2m_func_arg_right",
            "set @counter __p2m_func_scope_add.__p2m_func_ret_addr",
        ),
        id="function-with-positional-parameters",
    ),
    pytest.param(
        """
        def add(left, right):
            return left + right

        result = add(left=2, right=3)
        """,
        (
            "set __p2m_func_scope_add.__p2m_func_arg_left 2",
            "set __p2m_func_scope_add.__p2m_func_arg_right 3",
            "op add __p2m_func_scope_add.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_add.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op add __p2m_func_scope_add.__p2m_func_ret_val "
            "__p2m_func_scope_add.__p2m_func_arg_left "
            "__p2m_func_scope_add.__p2m_func_arg_right",
            "set @counter __p2m_func_scope_add.__p2m_func_ret_addr",
        ),
        id="function-call-with-keyword-arguments",
    ),
    pytest.param(
        """
        def double(value):
            return value * 2

        result = double(left + right)
        """,
        (
            "op add __p2m_func_scope_double.__p2m_func_arg_value left right",
            "op add __p2m_func_scope_double.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_double.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op mul __p2m_func_scope_double.__p2m_func_ret_val "
            "__p2m_func_scope_double.__p2m_func_arg_value 2",
            "set @counter __p2m_func_scope_double.__p2m_func_ret_addr",
        ),
        id="function-call-with-binary-expression-argument",
    ),
    pytest.param(
        """
        def add(left, right=3):
            return left + right

        result = add(2)
        """,
        (
            "set __p2m_func_scope_add.__p2m_func_arg_left 2",
            "set __p2m_func_scope_add.__p2m_func_arg_right 3",
            "op add __p2m_func_scope_add.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_add.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op add __p2m_func_scope_add.__p2m_func_ret_val "
            "__p2m_func_scope_add.__p2m_func_arg_left "
            "__p2m_func_scope_add.__p2m_func_arg_right",
            "set @counter __p2m_func_scope_add.__p2m_func_ret_addr",
        ),
        id="function-with-default-argument",
    ),
    pytest.param(
        """
        def add(left, /, right):
            return left + right

        result = add(2, right=3)
        """,
        (
            "set __p2m_func_scope_add.__p2m_func_arg_left 2",
            "set __p2m_func_scope_add.__p2m_func_arg_right 3",
            "op add __p2m_func_scope_add.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_add.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op add __p2m_func_scope_add.__p2m_func_ret_val "
            "__p2m_func_scope_add.__p2m_func_arg_left "
            "__p2m_func_scope_add.__p2m_func_arg_right",
            "set @counter __p2m_func_scope_add.__p2m_func_ret_addr",
        ),
        id="function-with-positional-only-parameter",
    ),
    pytest.param(
        """
        def add(left, *, right):
            return left + right

        result = add(2, right=3)
        """,
        (
            "set __p2m_func_scope_add.__p2m_func_arg_left 2",
            "set __p2m_func_scope_add.__p2m_func_arg_right 3",
            "op add __p2m_func_scope_add.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_add.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op add __p2m_func_scope_add.__p2m_func_ret_val "
            "__p2m_func_scope_add.__p2m_func_arg_left "
            "__p2m_func_scope_add.__p2m_func_arg_right",
            "set @counter __p2m_func_scope_add.__p2m_func_ret_addr",
        ),
        id="function-with-keyword-only-parameter",
    ),
    pytest.param(
        """
        a = 1

        def assign():
            a = 2

        assign()
        """,
        (
            "set a 1",
            "op add __p2m_func_scope_assign.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_assign.a 2",
            "set __p2m_func_scope_assign.__p2m_func_ret_val null",
            "set @counter __p2m_func_scope_assign.__p2m_func_ret_addr",
        ),
        id="function-with-scoped-assign",
    ),
    pytest.param(
        """
        def choose(condition):
            if condition:
                return 1
            return 2

        result = choose(condition)
        """,
        (
            "set __p2m_func_scope_choose.__p2m_func_arg_condition condition",
            "op add __p2m_func_scope_choose.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_choose.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "jump __p2m_label1 equal __p2m_func_scope_choose.__p2m_func_arg_condition false",
            "set __p2m_func_scope_choose.__p2m_func_ret_val 1",
            "set @counter __p2m_func_scope_choose.__p2m_func_ret_addr",
            "__p2m_label1:",
            "set __p2m_func_scope_choose.__p2m_func_ret_val 2",
            "set @counter __p2m_func_scope_choose.__p2m_func_ret_addr",
        ),
        id="function-with-branched-return",
    ),
    # added this in case the special case for ast.Name
    # when compiling ifexp unscoped the identifiers
    pytest.param(
        """
        def choose(condition):
            a = 1
            return a if condition else 2

        result = choose(condition)
        """,
        (
            "set __p2m_func_scope_choose.__p2m_func_arg_condition condition",
            "op add __p2m_func_scope_choose.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_choose.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_choose.a 1",
            "select __p2m_func_scope_choose.__p2m_func_ret_val "
            "equal __p2m_func_scope_choose.__p2m_func_arg_condition true "
            "__p2m_func_scope_choose.a 2",
            "set @counter __p2m_func_scope_choose.__p2m_func_ret_addr",
        ),
        id="function-with-ifexp-return",
    ),
    pytest.param(
        """
        def return_nothing():
            return

        result = return_nothing()
        """,
        (
            "op add __p2m_func_scope_return_nothing.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_return_nothing.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_return_nothing.__p2m_func_ret_val null",
            "set @counter __p2m_func_scope_return_nothing.__p2m_func_ret_addr",
        ),
        id="function-with-empty-return",
    ),
    pytest.param(
        """
        def return_early():
            return
            result = 123
            return result

        result = return_early()
        """,
        (
            "op add __p2m_func_scope_return_early.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_return_early.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_return_early.__p2m_func_ret_val null",
            "set @counter __p2m_func_scope_return_early.__p2m_func_ret_addr",
        ),
        id="function-with-early-return",
    ),
    pytest.param(
        """
        def implicit_return():
            pass

        result = implicit_return()
        """,
        (
            "op add __p2m_func_scope_implicit_return.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_implicit_return.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "set __p2m_func_scope_implicit_return.__p2m_func_ret_val null",
            "set @counter __p2m_func_scope_implicit_return.__p2m_func_ret_addr",
        ),
        id="function-with-implicit-none-return",
    ),
    # closures not yet supported
    pytest.param(
        """
        def outer():
            def inner():
                return 123

            return inner()

        result = outer()
        """,
        (
            "op add __p2m_func_scope_outer.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_outer.__p2m_func_ret_val",
            "end",
            "__p2m_label1:",
            "set __p2m_func_scope_outer.__p2m_func_scope_inner.__p2m_func_ret_val 123",
            "set @counter __p2m_func_scope_outer.__p2m_func_scope_inner.__p2m_func_ret_addr",
            "__p2m_label0:",
            "op add __p2m_func_scope_outer.__p2m_func_scope_inner.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label1 always",
            "set __p2m_func_scope_outer.__p2m_func_ret_val "
            "__p2m_func_scope_outer.__p2m_func_scope_inner.__p2m_func_ret_val",
            "set @counter __p2m_func_scope_outer.__p2m_func_ret_addr",
        ),
        id="nested-function-definition",
    ),
    pytest.param(
        """
        def outer(value):
            return value * 2
        def inner(value):
            return value + 1

        result = outer(inner(input_value))
        """,
        (
            "set __p2m_func_scope_inner.__p2m_func_arg_value input_value",
            "op add __p2m_func_scope_inner.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label1 always",
            "set __p2m_func_scope_outer.__p2m_func_arg_value "
            "__p2m_func_scope_inner.__p2m_func_ret_val",
            "op add __p2m_func_scope_outer.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_outer.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op mul __p2m_func_scope_outer.__p2m_func_ret_val "
            "__p2m_func_scope_outer.__p2m_func_arg_value 2",
            "set @counter __p2m_func_scope_outer.__p2m_func_ret_addr",
            "__p2m_label1:",
            "op add __p2m_func_scope_inner.__p2m_func_ret_val "
            "__p2m_func_scope_inner.__p2m_func_arg_value 1",
            "set @counter __p2m_func_scope_inner.__p2m_func_ret_addr",
        ),
        id="nested-function-call",
    ),
    pytest.param(
        """
        @inline
        def inline_func():
            return 42

        x = inline_func()
        """,
        ("set x 42",),
        id="inline-func",
    ),
    pytest.param(
        """
        @inline
        def inline_func(x, /, *, y):
            return abs(x) + y - 1

        x = 10
        z = inline_func(x, y=21 * 2)
        """,
        (
            "set x 10",
            "op mul __p2m_tmp0 21 2",
            "op abs __p2m_tmp2 x",
            "op add __p2m_tmp1 __p2m_tmp2 __p2m_tmp0",
            "op sub z __p2m_tmp1 1",
        ),
        id="inline-func-with-args",
    ),
    pytest.param(
        """
        @inline
        def outer(value):
            @inline
            def inner():
                return value + 1

            return inner()

        result = outer(input_value)
        """,
        ("op add result input_value 1",),
        id="inline-func-with-nested-inline-func",
    ),
    pytest.param(
        """
        def outer(value):
            @inline
            def inner():
                return value + 1

            return inner()

        result = outer(input_value)
        """,
        (
            "set __p2m_func_scope_outer.__p2m_func_arg_value input_value",
            "op add __p2m_func_scope_outer.__p2m_func_ret_addr @counter 2",
            "jump __p2m_label0 always",
            "set result __p2m_func_scope_outer.__p2m_func_ret_val",
            "end",
            "__p2m_label0:",
            "op add __p2m_func_scope_outer.__p2m_func_ret_val __p2m_func_scope_outer.__p2m_func_arg_value 1",
            "set @counter __p2m_func_scope_outer.__p2m_func_ret_addr",
        ),
        id="non-inline-func-with-nested-inline-func",
    ),
    pytest.param(
        """
        @inline
        def inline_func(x):
            return x * 2

        a = inline_func(2)
        b = inline_func(4)
        """,
        ("op mul a 2 2", "op mul b 4 2"),
        id="multiple-inline-func-calls",
    ),
    pytest.param(
        "a = b if condition1 else (c if condition2 else d)",
        (
            "__p2m_label1:",
            "jump __p2m_label0 equal condition1 false",
            "set a b",
            "jump __p2m_label1 always",
            "__p2m_label0:",
            "select a equal condition2 true c d",
        ),
        id="nested-ifexp",
    ),
    pytest.param(
        """
        a = Env.copper
        a = Env.water
        a = Env.red_stone
        a = Env.naval_factory
        a = Env.counter
        a = Env.time
        a = Env.null  # ;-;
        """,
        (
            "set a @copper",
            "set a @water",
            "set a @red-stone",
            "set a @naval-factory",
            "set a @counter",
            "set a @time",
            "set a null",
        ),
        id="env-attr",
    ),
    pytest.param(
        """
        a = UnitType.flare
        b = UnitType.quell_missile

        Unit.bind(a)
        Unit.bind(UnitType.flare)
        Unit.bind("flare")
        Unit.bind("@flare")

        a = Unit.radar("ally", order=max, key=maxHealth)
        b = Unit.radar("flying", enemy, order="max", key=max_health)
        c = Unit.radar("ground", boss, attacker, order=False, key=maxhealth)

        a, b, c = Unit.locate("ore", ore_type=Env.copper)
        a, b, c, d = Unit.locate("building", block_flag="core", is_enemy_building=False)
        a, b, c, d = Unit.locate("building", block_flag="turret", is_enemy_building="ally")
        a, b, c, d = Unit.locate("spawn")
        a, b, c, d = Unit.locate("damaged")

        Unit.flag = 123

        Unit.idle()
        Unit.stop()
        Unit.move(100, abc)
        Unit.move(x=100, y=abc)
        Unit.approach(100, 200, radius=10)
        Unit.pathfind(150, 150)
        Unit.auto_pathfind()
        Unit.boost(True)
        Unit.shoot()
        Unit.shoot(100, 100)
        Unit.target(100, 100, False)
        Unit.targetp(router1, False)
        Unit.target_unit(some_unit, True)
        Unit.ceasefire()
        Unit.item_drop(vault1)
        Unit.itemdrop(vault1, 123)
        Unit.store(container1, 123)
        Unit.itemTake(nucleus1, Env.copper, 123)
        Unit.fetch(vault1, Env.copper)
        Unit.pay_drop()
        Unit.drop()
        Unit.pay_take(False)
        Unit.lift()
        Unit.carry()
        Unit.pay_enter()
        Unit.mine(x, y)
        Unit.flag(123)
        Unit.build(150, 150, Env.copper_wall)
        Unit.deconstruct(150, 150)
        t, b, f = Unit.get_block(150, 150)
        w = Unit.within(150, 150, 10)
        Unit.unbind()
        """,
        (
            "set a @flare",
            "set b @quell-missile",
            # unit bind
            "ubind a",
            "ubind @flare",
            "ubind @flare",
            "ubind @flare",
            # unit radar
            "uradar ally any any maxHealth _ false a",
            "uradar flying enemy any maxHealth _ false b",
            "uradar ground boss attacker maxHealth _ false c",
            # unit locate
            "ulocate ore _ _ @copper a b c",
            "ulocate building core false _ a b c d",
            "ulocate building turret false _ a b c d",
            "ulocate spawn _ _ _ a b c d",
            "ulocate damaged _ _ _ a b c d",
            # setting Unit.flag property instead of using Unit.flag() for some reason
            "ucontrol flag 123",
            # unit control
            "ucontrol idle",
            "ucontrol stop",
            "ucontrol move 100 abc",
            "ucontrol move 100 abc",
            "ucontrol approach 100 200 10",
            "ucontrol pathfind 150 150",
            "ucontrol autoPathfind",
            "ucontrol boost true",
            "ucontrol targetp @unit true",
            "ucontrol target 100 100 true",
            "ucontrol target 100 100 false",
            "ucontrol targetp router1 false",
            "ucontrol targetp some_unit true",
            "ucontrol target 0 0 false",
            # 9999 is arbitrary so this test is pretty brittle ¯\_(ツ)_/¯
            "ucontrol itemDrop vault1 9999",
            "ucontrol itemDrop vault1 123",
            "ucontrol itemDrop container1 123",
            "ucontrol itemTake nucleus1 @copper 123",
            "ucontrol itemTake vault1 @copper 9999",
            "ucontrol payDrop",
            "ucontrol payDrop",
            "ucontrol payTake false",
            "ucontrol payTake true",
            "ucontrol payTake true",
            "ucontrol payEnter",
            "ucontrol mine x y",
            "ucontrol flag 123",
            "ucontrol build 150 150 @copper-wall 0 null",
            "ucontrol deconstruct 150 150",
            "ucontrol getBlock 150 150 t b f",
            "ucontrol within 150 150 10 w",
            "ucontrol unbind",
        ),
        id="unit-operations",
    ),
    pytest.param(
        """
        Screen.clear(0, 127, 255)
        Screen.fill(a, b, c)
        Screen.color(a, b, c)
        Screen.color(a, b, c, d)
        Screen.col(Color("%ffffff"))
        Screen.stroke(3)
        Screen.line(0, 0, x2=80, y2=160)
        Screen.rect(0, 0, 80, height=160)
        Screen.fill_rect(a, y=b, width=c, height=d)
        Screen.fillRect(a, y=b, width=c, height=d)
        Screen.linerect(0, 0, 80, 160)
        Screen.poly(80, 80, 6, 40 ,0)
        Screen.line_poly(80, 80, 6, 40, 0)
        Screen.triangle(50, 50, 100, 50, 50, 100)
        Screen.image(80, 80, Env.router, 40, 0)
        Screen.print(80, 80, Align.top_left)
        Screen.print(80, 80, "topleft")
        Screen.translate(80, 80)
        Screen.scale(2, 2)
        Screen.rotate(180)
        Screen.reset()
        Screen.flush()
        Screen.flush(display2)
        """,
        (
            "draw clear 0 127 255",
            "draw clear a b c",
            "draw color a b c 255",
            "draw color a b c d",
            "draw col %ffffff",
            "draw stroke 3",
            "draw line 0 0 80 160",
            "draw rect 0 0 80 160",
            "draw rect a b c d",
            "draw rect a b c d",
            "draw lineRect 0 0 80 160",
            "draw poly 80 80 6 40 0",
            "draw linePoly 80 80 6 40 0",
            "draw triangle 50 50 100 50 50 100",
            "draw image 80 80 @router 40 0",
            "draw print 80 80 @topLeft",
            "draw print 80 80 @topLeft",
            "draw translate 80 80",
            "draw scale 2 2",
            "draw rotate 180",
            "draw reset",
            "drawflush display1",
            "drawflush display2",
        ),
        id="screen-operations",
    ),
    pytest.param(
        """
        Control.enabled(turret1, True)
        Control.enable(turret1)
        Control.disable(turret1)
        Control.shoot(foo, 100, 100, True)
        Control.shoot(foo, 100, 100)
        Control.ceasefire(foo)
        Control.shootp(foo, Env.this, True)
        Control.shootp(foo, Env.this)
        Control.color(foo, Color("008080"))
        Control.config(sorter1, Env.copper)

        turret1.enabled(True)
        turret1.enable()
        turret1.disable()
        foo.shoot(100, 100, True)
        foo.shoot(100, 100)
        foo.ceasefire()
        foo.shootp(Env.this, True)
        foo.shootp(Env.this)
        foo.color(Color("008080"))
        sorter1.config(Env.copper)
        """,
        (
            # Control.*
            "control enabled turret1 true",
            "control enabled turret1 true",
            "control enabled turret1 false",
            "control shoot foo 100 100 true",
            "control shoot foo 100 100 true",
            "control shoot foo 0 0 false",
            "control shootp foo @this true",
            "control shootp foo @this true",
            "control color foo %008080",
            "control config sorter1 @copper",
            # methods
            "control enabled turret1 true",
            "control enabled turret1 true",
            "control enabled turret1 false",
            "control shoot foo 100 100 true",
            "control shoot foo 100 100 true",
            "control shoot foo 0 0 false",
            "control shootp foo @this true",
            "control shootp foo @this true",
            "control color foo %008080",
            "control config sorter1 @copper",
        ),
        id="control-operations-and-methods",
    ),
    pytest.param(
        """
        a = Links[0]
        b = Links[1 + 2 * 3]
        c = Links[i]
        d = Links[abs(-1)]

        e = Link[0]
        """,
        (
            "getlink a 0",
            "op mul __p2m_tmp1 2 3",
            "op add __p2m_tmp0 1 __p2m_tmp1",
            "getlink b __p2m_tmp0",
            "getlink c i",
            "op abs __p2m_tmp2 -1",
            "getlink d __p2m_tmp2",
            "getlink e 0",
        ),
        id="links-subscript-access",
    ),
    pytest.param(
        """
        x = abs(Mem.cell1[1])
        Mem.cell2[10] = x * 2
        Mem.cell1[1] = Mem.cell2[10]
        y = Mem.read(cell1, 1)
        Mem.write(y, cell2, 10)
        x = y = Mem.cell1[1]
        Mem.cell2[10] = x = 123
        x = Mem.cell2[10] = 123
        Mem.cell1[1] += 1
        """,
        (
            "read __p2m_tmp0 cell1 1",
            "op abs x __p2m_tmp0",
            "op mul __p2m_tmp1 x 2",
            "write __p2m_tmp1 cell2 10",
            "read __p2m_tmp2 cell2 10",
            "write __p2m_tmp2 cell1 1",
            "read y cell1 1",
            # this write call wastes a tmp
            # func call generates tmp even when unneeded
            "write y cell2 10",
            "read x cell1 1",
            "set y x",
            "write 123 cell2 10",
            "set x 123",
            "set x 123",
            "write x cell2 10",
            "read __p2m_tmp5 cell1 1",
            # the tmp for the op is generated first
            "op add __p2m_tmp4 __p2m_tmp5 1",
            "write __p2m_tmp4 cell1 1",
        ),
        id="mem-operations-and-subscript-access",
    ),
    pytest.param(
        """
        from py2mlog_api import Env, Links
        from py2mlog_api import *
        """,
        (),
        id="py2mlog-api-namespace-imports",
    ),
]


@pytest.mark.parametrize(("src", "expected"), _test_snippet_testcases)
def test_snippet(src: str, expected: tuple[str]):
    src = dedent(src).strip()
    expected_str = "\n".join(expected)

    assert compile_src_to_mlog(src, optimizer_iterations=0) == expected_str
