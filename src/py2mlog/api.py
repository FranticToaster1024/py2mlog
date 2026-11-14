__all__ = ["compile_src_to_mlog"]

import ast

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.optimizer.optimizer import optimize


def compile_src_to_mlog(
    src: str, /, *, optimization_iterations: int | None = None
) -> str:
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    if optimization_iterations is not None:
        instrs = optimize(
            emitter.instructions, iterations=optimization_iterations
        )
    else:
        instrs = optimize(emitter.instructions)

    return generate_mlog(instrs)
