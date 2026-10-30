import ast
from textwrap import dedent

import pytest

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        pytest.param("pass", "", id="pass"),
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
                (
                    "op add __p2m_tmp0 left right",
                    "op mul result __p2m_tmp0 factor",
                )
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
            "\n".join(
                (
                    "set uadd_var var",
                    "set uadd_num 1.23",
                    "op sub usub_var 0 var",
                    "set usub_num -1.23",
                    "set double_usub_num 1.23",
                    "op not invert_var var",
                    "set invert_int -124",
                )
            ),
            id="unary-ops",
        ),
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
                a = abs(a)
                b = ord('a')
            """).strip(),
            "\n".join(
                (
                    "op abs a a",
                    'read b "a" 0',
                )
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
            "\n".join(
                (
                    "select a equal condition true b d",
                    'select a equal b c 1 "str"',
                    "select a lessThan b c null -1.23",
                )
            ),
            id="ifexp-to-select",
        ),
        pytest.param(
            "a = abs(b) + c + d if e >= f else g * h - i * j",
            "\n".join(
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
                )
            ),
            id="ifexp-to-branches",
        ),
        pytest.param(
            dedent("""
                def get_value():
                    return 42

                result = get_value()
            """).strip(),
            "\n".join(
                (
                    "op add __p2m_func_scope_get_value.__p2m_func_ret_addr @counter 2",
                    "jump __p2m_label0 always",
                    "set result __p2m_func_scope_get_value.__p2m_func_ret_val",
                    "end",
                    "__p2m_label0:",
                    "set __p2m_func_scope_get_value.__p2m_func_ret_val 42",
                    "set @counter __p2m_func_scope_get_value.__p2m_func_ret_addr",
                )
            ),
            id="function-without-parameters",
        ),
        pytest.param(
            dedent("""
                def add(left, right):
                    return left + right

                result = add(2, 3)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-positional-parameters",
        ),
        pytest.param(
            dedent("""
                def add(left, right):
                    return left + right

                result = add(left=2, right=3)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-call-with-keyword-arguments",
        ),
        pytest.param(
            dedent("""
                def double(value):
                    return value * 2

                result = double(left + right)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-call-with-binary-expression-argument",
        ),
        pytest.param(
            dedent("""
                def add(left, right=3):
                    return left + right

                result = add(2)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-default-argument",
        ),
        pytest.param(
            dedent("""
                def add(left, /, right):
                    return left + right

                result = add(2, right=3)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-positional-only-parameter",
        ),
        pytest.param(
            dedent("""
                def add(left, *, right):
                    return left + right

                result = add(2, right=3)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-keyword-only-parameter",
        ),
        pytest.param(
            dedent("""
                a = 1

                def assign():
                    a = 2

                assign()
            """),
            "\n".join(
                (
                    "set a 1",
                    "op add __p2m_func_scope_assign.__p2m_func_ret_addr @counter 2",
                    "jump __p2m_label0 always",
                    "end",
                    "__p2m_label0:",
                    "set __p2m_func_scope_assign.a 2",
                    "set __p2m_func_scope_assign.__p2m_func_ret_val null",
                    "set @counter __p2m_func_scope_assign.__p2m_func_ret_addr",
                )
            ),
            id="function-with-scoped-assign",
        ),
        pytest.param(
            dedent("""
                def choose(condition):
                    if condition:
                        return 1
                    return 2

                result = choose(condition)
            """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-branched-return",
        ),
        # added this in case the special case for ast.Name
        # when compiling ifexp unscoped the identifiers
        pytest.param(
            dedent("""
                def choose(condition):
                    a = 1
                    return a if condition else 2

                result = choose(condition)
                    """).strip(),
            "\n".join(
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
                )
            ),
            id="function-with-ifexp-return",
        ),
        pytest.param(
            dedent("""
                def return_nothing():
                    return

                result = return_nothing()
            """).strip(),
            "\n".join(
                (
                    "op add __p2m_func_scope_return_nothing.__p2m_func_ret_addr @counter 2",
                    "jump __p2m_label0 always",
                    "set result __p2m_func_scope_return_nothing.__p2m_func_ret_val",
                    "end",
                    "__p2m_label0:",
                    "set __p2m_func_scope_return_nothing.__p2m_func_ret_val null",
                    "set @counter __p2m_func_scope_return_nothing.__p2m_func_ret_addr",
                )
            ),
            id="function-with-empty-return",
        ),
        pytest.param(
            dedent("""
                def return_early():
                    return
                    result = 123
                    return result

                result = return_early()
            """).strip(),
            "\n".join(
                (
                    "op add __p2m_func_scope_return_early.__p2m_func_ret_addr @counter 2",
                    "jump __p2m_label0 always",
                    "set result __p2m_func_scope_return_early.__p2m_func_ret_val",
                    "end",
                    "__p2m_label0:",
                    "set __p2m_func_scope_return_early.__p2m_func_ret_val null",
                    "set @counter __p2m_func_scope_return_early.__p2m_func_ret_addr",
                )
            ),
            id="function-with-early-return",
        ),
        pytest.param(
            dedent("""
                def implicit_return():
                    pass

                result = implicit_return()
            """).strip(),
            "\n".join(
                (
                    "op add __p2m_func_scope_implicit_return.__p2m_func_ret_addr @counter 2",
                    "jump __p2m_label0 always",
                    "set result __p2m_func_scope_implicit_return.__p2m_func_ret_val",
                    "end",
                    "__p2m_label0:",
                    "set __p2m_func_scope_implicit_return.__p2m_func_ret_val null",
                    "set @counter __p2m_func_scope_implicit_return.__p2m_func_ret_addr",
                )
            ),
            id="function-with-implicit-none-return",
        ),
        # closures not yet supported
        pytest.param(
            dedent("""
                def outer():
                    def inner():
                        return 123

                    return inner()

                result = outer()
            """).strip(),
            "\n".join(
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
                )
            ),
            id="nested-function-definition",
        ),
        pytest.param(
            dedent("""
                def outer(value):
                    return value * 2
                def inner(value):
                    return value + 1

                result = outer(inner(input_value))
            """).strip(),
            "\n".join(
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
                )
            ),
            id="nested-function-call",
        ),
        pytest.param(
            "a = b if condition1 else (c if condition2 else d)",
            "\n".join(
                (
                    "jump __p2m_label0 equal condition1 false",
                    "set a b",
                    "jump __p2m_label1 always",
                    "__p2m_label0:",
                    "select a equal condition2 true c d",
                    "__p2m_label1:",
                )
            ),
            id="nested-ifexp",
        ),
        pytest.param(
            dedent("""
                a = Env.copper
                b = Env.water
            """).strip(),
            "\n".join(
                (
                    "set a @copper",
                    "set b @water",
                )
            ),
            id="env-attr-resources",
        ),
    ],
)
def test_snippet(src: str, expected: str):
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    assert generate_mlog(emitter.instructions) == expected
