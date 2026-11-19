import logging
from time import perf_counter

from py2mlog.mlog.instruction import MlogItem
from py2mlog.optimizer.dead_code_elimination import dead_code_elimination
from py2mlog.optimizer.peephole import peephole

logger = logging.getLogger(__name__)


_MAX_ITERATIONS = 5


# TODO: maybe special classes to avoid recomputing metadata?
# optimize the optimizer, heh
def optimize(
    _instructions: list[MlogItem], /, *, iterations: int = _MAX_ITERATIONS
) -> list[MlogItem]:
    st_time = perf_counter()

    instrs = tuple(_instructions)

    start_len = len(instrs)
    last_len = start_len
    for i in range(iterations):
        instrs = peephole(instrs)
        instrs = dead_code_elimination(instrs)

        if len(instrs) == last_len:
            logger.debug(
                "Ended optimizer after %s iterations "
                "(no instructions removed in last iteration).",
                i + 1,
            )

        last_len = len(instrs)

    logger.debug(
        "Optimizer finished in %ss. Removed %s instructions.",
        round(perf_counter() - st_time, 2),
        start_len - last_len,
    )
    return list(instrs)


# TODO: constant folding
