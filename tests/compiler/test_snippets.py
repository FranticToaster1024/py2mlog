import ast
from textwrap import dedent

import pytest

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog


@pytest.mark.parametrize(
    ("src", "expected"),
    [
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
                )
            ),
            (
                "set integer 123",
                "set float_ 12.3",
                'set string "str"',
                "set boolean true",
                "set none null",
                "set copy value",
            ),
            id="basic-assignment",
        ),
        pytest.param(
            "first = second = value",
            (
                "set first value",
                # 'first' instead of 'value'
                # does it matter? ¯\_(ツ)_/¯
                "set second first",
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
                "jump __p2m_label0 equal condition false",
                "set result first",
                "__p2m_label0:",
            ),
            id="if-with-name-condition",
        ),
        pytest.param(
            """
            if x < 5:
                x = x + 1
            """,
            (
                "jump __p2m_label0 greaterThanEq x 5",
                "op add x x 1",
                "__p2m_label0:",
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
                "jump __p2m_label0 equal condition false",
                "set result first",
                "jump __p2m_label1 always",
                "__p2m_label0:",
                "set result second",
                "__p2m_label1:",
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
            ),
            id="if-multiple-elif-without-else",
        ),
        pytest.param(
            """
            while condition:
                result = value
            """,
            (
                "jump __p2m_label1 equal condition false",
                "__p2m_label0:",
                "set result value",
                "jump __p2m_label0 equal condition true",
                "__p2m_label1:",
            ),
            id="while-with-name-condition",
        ),
        pytest.param(
            """
            while count < limit:
                count = count + 1
            """,
            (
                "jump __p2m_label1 greaterThanEq count limit",
                "__p2m_label0:",
                "op add count count 1",
                "jump __p2m_label0 lessThan count limit",
                "__p2m_label1:",
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
                "jump __p2m_label1 equal outer_condition false",
                "__p2m_label0:",
                "jump __p2m_label3 equal inner_condition false",
                "__p2m_label2:",
                "set result value",
                "jump __p2m_label2 equal inner_condition true",
                "__p2m_label3:",
                "jump __p2m_label0 equal outer_condition true",
                "__p2m_label1:",
            ),
            id="nested-while-loops",
        ),
        pytest.param(
            """
            while condition:
                break
            """,
            (
                "jump __p2m_label1 equal condition false",
                "__p2m_label0:",
                "jump __p2m_label1 always",
                "jump __p2m_label0 equal condition true",
                "__p2m_label1:",
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
                "jump __p2m_label1 equal condition1 false",
                "__p2m_label0:",
                # could use optimization here as well
                "jump __p2m_label2 equal condition2 false",
                "jump __p2m_label1 always",
                "__p2m_label2:",
                "op add x x 10",
                "jump __p2m_label1 always",
                "jump __p2m_label0 equal condition1 true",
                "__p2m_label1:",
            ),
            id="while-multiple-break",
        ),
        pytest.param(
            """
            while condition:
                continue
            """,
            (
                "jump __p2m_label1 equal condition false",
                "__p2m_label0:",
                # could use some optimization when condition jump is 1 instruction like here
                "jump __p2m_label2 always",
                "__p2m_label2:",
                "jump __p2m_label0 equal condition true",
                "__p2m_label1:",
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
                "jump __p2m_label1 equal condition false",
                "__p2m_label0:",
                "set result false",
                "jump __p2m_label2 always",
                "jump __p2m_label0 equal condition true",
                "__p2m_label1:",
                "set result true",
                "__p2m_label2:",
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
                "__p2m_label1:",
            ),
            id="nested-while-break-continue",
        ),
        pytest.param(
            """
            for index in range(5):
                result = index
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
            ),
            id="for-range-one-literal",
        ),
        pytest.param(
            """
            for index in range(2, 8):
                result = index
            """,
            (
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
                "__p2m_label1:",
            ),
            id="for-range-start-stop-literals",
        ),
        pytest.param(
            """
            for index in range(1, 10, 2):
                result = index
            """,
            (
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
                "__p2m_label1:",
            ),
            id="for-range-start-stop-step-literals",
        ),
        pytest.param(
            """
            for index in range(stop):
                result = index
            """,
            (
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
                "__p2m_label1:",
            ),
            id="for-range-identifier",
        ),
        pytest.param(
            """
            for index in range(start, stop, step):
                result = index
            """,
            (
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
                "__p2m_label1:",
            ),
            id="for-range-identifiers",
        ),
        pytest.param(
            """
            for index in range(start + offset, limit * 2, step + 1):
                result = index
            """,
            (
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
                "__p2m_label1:",
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
                "__p2m_label1:",
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
                "__p2m_label1:",
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
                "__p2m_label1:",
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
                "__p2m_label3:",
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
                "__p2m_label1:",
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
            a = abs(a)
            b = ord('a')
            """,
            (
                "op abs a a",
                'read b "a" 0',
            ),
            id="supported-builtin-functions",
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
                "jump __p2m_label0 lessThan e f",
                "op abs __p2m_tmp1 b",
                "op add __p2m_tmp0 __p2m_tmp1 c",
                "op add a __p2m_tmp0 d",
                "jump __p2m_label1 always",
                "__p2m_label0:",
                "op mul __p2m_tmp2 g h",
                "op mul __p2m_tmp3 i j",
                "op sub a __p2m_tmp2 __p2m_tmp3",
                "__p2m_label1:",
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
            "a = b if condition1 else (c if condition2 else d)",
            (
                "jump __p2m_label0 equal condition1 false",
                "set a b",
                "jump __p2m_label1 always",
                "__p2m_label0:",
                "select a equal condition2 true c d",
                "__p2m_label1:",
            ),
            id="nested-ifexp",
        ),
        pytest.param(
            """
            a = Env.copper
            b = Env.water
            """,
            (
                "set a @copper",
                "set b @water",
            ),
            id="env-attr-resources",
        ),
    ],
)
def test_snippet(src: str, expected: tuple[str]):
    src = dedent(src).strip()
    expected_str = "\n".join(expected)

    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    assert generate_mlog(emitter.instructions) == expected_str
