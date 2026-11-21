__all__ = ["compile_src_to_mlog"]

import ast

from py2mlog.compiler import config
from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.optimizer.optimizer import optimize


def compile_src_to_mlog(
    src: str,
    /,
    *,
    optimizer_iterations: int = config.DEFAULT_OPTIMIZER_ITERATIONS,
) -> str:
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()
    emitter.resolve_absolute_jumps()

    instrs = emitter.instructions

    instrs = optimize(instrs, iterations=optimizer_iterations)

    return generate_mlog(instrs)
