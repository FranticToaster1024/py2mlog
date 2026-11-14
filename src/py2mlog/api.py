__all__ = ["compile_src_to_mlog"]

import ast

from py2mlog.compiler import config
from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog
from py2mlog.optimizer.optimizer import optimize


def compile_src_to_mlog(
    src: str, /, *, optimizer_iterations: int | None = None
) -> str:
    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()

    instrs = emitter.instructions

    if config.OPTIMIZER:
        if optimizer_iterations is not None:
            instrs = optimize(instrs, iterations=optimizer_iterations)
        else:
            instrs = optimize(instrs)

    return generate_mlog(instrs)
