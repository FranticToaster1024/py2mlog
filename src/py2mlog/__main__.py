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


# this might need cleanup at some point
# probably also needs tests to check whether it errors properly
# and like better tests in general
# but i can't be bothered

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


class Py2mlogCLIArgs(argparse.Namespace):
    targets: list[Path]
    outputs: list[Path] | None
    stdout: bool
    file: bool


type COMPILE_PATH_CALLABLE = Callable[
    [argparse.ArgumentParser, Py2mlogCLIArgs, Path, Path], None
]


def log_compile(
    func: COMPILE_PATH_CALLABLE,
) -> COMPILE_PATH_CALLABLE:
    @wraps(func)
    def wrapper(
        parser: argparse.ArgumentParser,
        args: Py2mlogCLIArgs,
        target: Path,
        output: Path,
    ) -> None:
        time_st = perf_counter()
        logger.info(
            "Compiling '%s'%s...",
            target.name,
            f" to '{output.name}'" if args.file else "",
        )

        result = func(parser, args, target, output)

        logger.info("Done in %ss.", round(perf_counter() - time_st, 2))

        return result

    return wrapper


def _compile_path(
    parser: argparse.ArgumentParser,
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
) -> None:
    if target.is_file():
        _compile_file(parser, args, target, output)

    elif target.is_dir():
        _compile_dir(parser, args, target, output)

    elif not target.exists():
        parser.error(f"Target '{target.resolve()}' does not exist.")

    else:
        parser.error("Something went wrong.")


@log_compile
def _compile_dir(
    parser: argparse.ArgumentParser,
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
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
                    args,
                    path,
                    (output / path.relative_to(target)).with_suffix(".mlog"),
                )


@log_compile
def _compile_file(
    parser: argparse.ArgumentParser,
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
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
        logger.error(  # noqa: TRY400
            "A syntax error occurred while compiling %s:\n\n", target.name
        )
        print_exception(e, limit=0)
        sys.exit(1)

    except CompilerError as e:
        logger.error(  # noqa: TRY400
            "A compiler error occurred while compiling %s:\n\n%s: %s",
            target.name,
            type(e).__name__,
            e,
        )
        sys.exit(1)

    if args.stdout:
        sys.stdout.write(f"\n{indent(mlog, '\t' * (indent_level + 1))}\n\n")

    if args.file:
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
    parser.add_argument(
        "-s",
        "--stdout",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether to print result to standard output (defaults to False).",
    )
    parser.add_argument(
        "-f",
        "--file",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to create output file/folder(s). "
        "Overrides '--output' when False. Defaults to True.",
    )

    args = parser.parse_args(argv, namespace=Py2mlogCLIArgs())

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(IndentFormatter("%(levelname)s: %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    if args.outputs is None:
        args.outputs = []

    if not args.stdout and not args.file:
        parser.error(
            "No output provided; cannot disable stdout and file outputs together."
        )

    time_st = perf_counter()
    for i, target in enumerate(args.targets):
        if i < len(args.outputs):
            output = args.outputs[i]
        else:
            output = target.with_suffix(".mlog") if target.is_file() else target

        _compile_path(parser, args, target, output)

    logger.info("All done in %ss!", round(perf_counter() - time_st, 2))
