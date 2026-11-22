import logging
from textwrap import dedent

import pytest

from py2mlog.compiler import config
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
    pytest.param(
        """
        jump l1 equal x true
        set a 1
        jump l2 always
        set b 1
        l1:
        set c 1
        l2:
        set d 1
        """,
        """
        jump l1 equal x true
        set a 1
        jump l2 always
        l1:
        set c 1
        l2:
        set d 1
        """,
        id="unreachable-code-after-end",
    ),
    pytest.param(
        """
        jump l1 equal x true
        set a 1
        end
        set b 1
        l1:
        set c 1
        """,
        """
        jump l1 equal x true
        set a 1
        end
        l1:
        set c 1
        """,
        id="unreachable-code-after-end",
    ),
    pytest.param(
        """
        jump l1 equal x true
        set a 1
        stop
        set b 1
        l1:
        set c 1
        """,
        """
        jump l1 equal x true
        set a 1
        stop
        l1:
        set c 1
        """,
        id="unreachable-code-after-stop",
    ),
    pytest.param(
        """
        print "foo"
        print "bar"
        noop
        print "foo"
        print "bar"
        print "baz"
        print "idk"
        """,
        """
        print "foobar"
        noop
        print "foobarbazidk"
        """,
        id="print-merge",
    ),
    pytest.param(
        """
        print "foo"
        print a
        print 123
        print "bar"
        print b
        print "baz"
        """,
        """
        print "foo{0}123bar{0}baz"
        format a
        format b
        """,
        id="print-merge-with-vars",
    ),
    pytest.param(
        """
        print "foo{0}{1}{0}foo"
        format a
        format b
        format c
        """,
        """
        print "foo{0}{0}{0}foo"
        format a
        format c
        format b
        """,
        id="print-merge-with-format",
    ),
    pytest.param(
        """
        print "foo{1}foo{0}foo"
        format a
        format b
        print "foo{0}{1}{0}foo"
        format c
        format d
        format e
        """,
        """
        print "foo{0}foo{0}foofoo{0}{0}{0}foo"
        format b
        format a
        format c
        format e
        format d
        """,
        id="print-merge-with-formats",
    ),
    pytest.param("print a", "print a", id="print-var-no-pessimization"),
    pytest.param(
        'print "literal"',
        'print "literal"',
        id="print-str-pessimization",
    ),
    pytest.param(
        'print "literal"\nnoop',
        'print "literal"\nnoop',
        id="multiple-print-str-pessimization",
    ),
    pytest.param(
        "print a\nprint b\nprint c",
        "print a\nprint b\nprint c",
        id="multiple-print-var-no-pessimization",
    ),
    pytest.param(
        'print "foo"\nprint a',
        'print "foo{0}"\nformat a',
        id="mixed-print-no-pessimization",
    ),
    pytest.param(
        'print "{0}"\nformat a', "print a", id="merge-print-format-to-print-var"
    ),
    pytest.param(
        """
        print "{0}"
        noop
        print "{1}"
        noop
        format a
        """,
        """
        print "{0}"
        noop
        noop
        print a
        """,
        id="merge-print-format-to-print-var-with-gap",
    ),
    pytest.param(
        'print "{0}foo"\nformat 123',
        'print "123foo"',
        id="merge-print-format-with-literal",
    ),
    pytest.param(
        """
        print "foo{0}bar{9}"
        noop
        format "baz"
        noop
        format 1.23
        noop
        format "unused"
        """,
        """
        noop
        noop
        print "foobazbar1.23"
        noop
        format "unused"
        """,
        id="merge-print-format-with-literals-with-gap",
    ),
    pytest.param(
        """
        set 1 2
        set x x
        set @counter @counter
        set x 1
        set x y
        op add 0 1 1
        op abs "abc" -5
        op add x 0 x
        op add x x 0
        op sub x x 0
        op mul x x 1
        op mul x 1 x
        op div x x 1
        op idiv x x 1
        op add x y 1
        op sub x 0 x
        op mul x y 2
        op div x 1 y
        """,
        """
        set x 1
        set x y
        op add x y 1
        op sub x 0 x
        op mul x y 2
        op div x 1 y
        """,
        id="remove-useless-instrs",
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

    assert (
        generate_mlog(
            optimize(parsed_src, iterations=config.DEFAULT_OPTIMIZER_ITERATIONS)
        )
        == expected_str
    )
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
