import ast
import pytest

from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.error import CompilerError, CompilerErrorType

from py2mlog.mlog.codegen import generate_mlog


@pytest.mark.parametrize(
    ("src", "error_type"),
    [
        pytest.param("break", CompilerErrorType.SYNTAX, id="break-outside-loop"),
        pytest.param("continue", CompilerErrorType.SYNTAX, id="continue-outside-loop"),
    ],
)
def test_error(src: str, error_type: CompilerErrorType):
    emitter = Emitter()

    with pytest.raises(CompilerError) as exc_info:
        Compiler(src, ast.parse(src), emitter).compile()
        generate_mlog(emitter.instructions)

    assert exc_info.value.error == error_type
