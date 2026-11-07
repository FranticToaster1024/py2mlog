import argparse
import ast
import logging
import sys
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from textwrap import indent
from time import perf_counter
from traceback import print_exception
from typing import TypeAlias

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.compiler.error import CompilerError
from py2mlog.mlog.codegen import generate_mlog

try:
    _version = version("py2mlog")
except PackageNotFoundError:
    _version = "unknown"
VERSION = _version


logger = logging.getLogger(__name__)


indent_level = 0


class IndentFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return indent(super().format(record), indent_level * 4 * " ")


@contextmanager
def indent_log() -> Generator[None, None, None]:
    global indent_level  # noqa:PLW0603
    indent_level += 1
    yield
    indent_level -= 1


COMPILE_PATH_CALLABLE: TypeAlias = Callable[
    [argparse.ArgumentParser, Path, Path], None
]


def log_compile(
    func: COMPILE_PATH_CALLABLE,
) -> COMPILE_PATH_CALLABLE:
    @wraps(func)
    def wrapper(
        parser: argparse.ArgumentParser, target: Path, output: Path
    ) -> None:
        time_st = perf_counter()
        logger.info("Compiling '%s' to '%s'...", target.name, output.name)

        result = func(parser, target, output)

        logger.info("Done in %ss.", round(perf_counter() - time_st, 2))

        return result

    return wrapper


def _compile_path(
    parser: argparse.ArgumentParser, target: Path, output: Path
) -> None:
    if target.is_file():
        _compile_file(parser, target, output)

    elif target.is_dir():
        _compile_dir(parser, target, output)


@log_compile
def _compile_dir(
    parser: argparse.ArgumentParser, target: Path, output: Path
) -> None:
    if not output.exists():
        output.mkdir(parents=True)

    if not output.is_dir():
        parser.error(
            f"Target '{target.resolve()}' is a directory "
            f"but output '{output.resolve()}' is not a directory."
        )

    for path in target.rglob("*"):
        if path.is_file() and path.suffix == ".py":
            with indent_log():
                _compile_file(
                    parser,
                    path,
                    (output / path.relative_to(target)).with_suffix(".mlog"),
                )


@log_compile
def _compile_file(
    parser: argparse.ArgumentParser, target: Path, output: Path
) -> None:
    if not target.is_file():
        parser.error(f"Target '{target.resolve()}' is not a file.")
    if target.suffix != ".py":
        parser.error(
            f"Target '{target.resolve()}' does not have a .py extension."
        )

    if output.exists() and not output.is_file():
        parser.error(f"Output '{output.resolve()}' is not a file.")
    if output.suffix != ".mlog":
        parser.error(
            f"Output '{output.resolve()}' does not have a .mlog extension."
        )

    try:
        src = target.read_text(encoding="utf-8")
    except PermissionError:
        parser.error(f"Could not read from '{target.resolve()}'.")
    except FileNotFoundError:
        parser.error(f"Could not find '{target.resolve()}'.")
    except OSError as e:
        parser.error(
            f"An OS error occurred while reading from '{target.resolve()}': {e}"
        )

    emitter = Emitter()
    try:
        Compiler(src, ast.parse(src), emitter).compile()
        mlog = generate_mlog(emitter.instructions)

    except SyntaxError as e:
        logger.exception(  # noqa: LOG007
            "A syntax error occurred while compiling %s:\n\n",
            target.name,
            exc_info=False,
        )
        print_exception(e, limit=0)
        sys.exit(1)

    except CompilerError as e:
        logger.exception(  # noqa:LOG007
            "A compiler error occurred while compiling %s:\n\n%s: %s",
            target.name,
            type(e).__name__,
            e,  # noqa: TRY401
            exc_info=False,
        )
        sys.exit(1)

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(mlog, encoding="utf-8")
    except PermissionError:
        parser.error(f"Could not write to '{output.resolve()}'.")
    except FileNotFoundError:
        parser.error(f"Could not find '{output.resolve()}'.")
    except OSError as e:
        parser.error(
            f"An OS error occurred while writing to '{output.resolve()}': {e}"
        )


class Py2mlogCLIArgs(argparse.Namespace):
    targets: list[Path]
    outputs: list[Path] | None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="py2mlog",
        description="A python to mindustry logic (mlog) compiler.",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, version {VERSION}"
    )

    parser.add_argument(
        "targets",
        nargs="+",
        type=Path,
        help="The target file/folder(s) to compile.",
        metavar="target",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="+",
        default=None,
        type=Path,
        help="The output file/folder(s) (defaults to path/to/python/src/<target>.mlog).",
        dest="outputs",
    )

    args = parser.parse_args(argv, namespace=Py2mlogCLIArgs())

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(IndentFormatter("%(levelname)s: %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    if args.outputs is None:
        args.outputs = []

    time_st = perf_counter()
    for i, target in enumerate(args.targets):
        if i < len(args.outputs):
            output = args.outputs[i]
        else:
            output = target.with_suffix(".mlog") if target.is_file() else target

        _compile_path(parser, target, output)

    logger.info("All done in %ss!", round(perf_counter() - time_st, 2))
