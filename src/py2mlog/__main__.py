import argparse
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
from typing import NoReturn

from py2mlog.api import compile_src_to_mlog
from py2mlog.compiler.error import CompilerError

try:
    _version = version("py2mlog")
except PackageNotFoundError:
    _version = "unknown"
VERSION = _version


logger = logging.getLogger(__name__)


CLIPBOARD_DEPENDENCY_NAME = "pyperclip"


def _try_import_clipboard():
    try:
        import pyperclip  # pyright: ignore[reportMissingModuleSource] # noqa: PLC0415
    except ImportError:
        return None
    else:
        return pyperclip


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
    copy: bool


type COMPILE_PATH_CALLABLE = Callable[[Py2mlogCLIArgs, Path, Path], None]


def _log_err_and_exit(msg: str, exit_code: int = 1) -> NoReturn:
    logger.error(msg)
    sys.exit(exit_code)


def log_compile(
    func: COMPILE_PATH_CALLABLE,
) -> COMPILE_PATH_CALLABLE:
    @wraps(func)
    def wrapper(
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

        result = func(args, target, output)

        logger.info("Done in %ss.", round(perf_counter() - time_st, 2))

        return result

    return wrapper


def _compile_path(
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
) -> None:
    if target.is_file():
        _compile_file(args, target, output)

    elif target.is_dir():
        _compile_dir(args, target, output)

    elif not target.exists():
        _log_err_and_exit(f"Target '{target.resolve()}' does not exist.")

    else:
        _log_err_and_exit("Something went wrong.")


@log_compile
def _compile_dir(
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
) -> None:
    if not output.exists():
        output.mkdir(parents=True)

    if not output.is_dir():
        _log_err_and_exit(
            f"Target '{target.resolve()}' is a directory "
            f"but output '{output.resolve()}' is not a directory."
        )

    for path in target.rglob("*"):
        if path.is_file() and path.suffix == ".py":
            with indent_log():
                _compile_file(
                    args,
                    path,
                    (output / path.relative_to(target)).with_suffix(".mlog"),
                )


@log_compile
def _compile_file(
    args: Py2mlogCLIArgs,
    target: Path,
    output: Path,
) -> None:
    if not target.exists():
        _log_err_and_exit(f"Target '{target.resolve()}' does not exist.")
    if not target.is_file():
        _log_err_and_exit(f"Target '{target.resolve()}' is not a file.")
    if target.suffix != ".py":
        logger.warning(
            "Target '%s' does not have a .py extension.", output.resolve()
        )

    if output.exists() and not output.is_file():
        _log_err_and_exit(f"Output '{output.resolve()}' is not a file.")
    if output.suffix != ".mlog":
        logger.warning(
            "Output '%s' does not have a .mlog extension.", output.resolve()
        )

    try:
        src = target.read_text(encoding="utf-8")
    except OSError as e:
        _log_err_and_exit(f"Failed to read from '{target.resolve()}': {e!s}")

    try:
        mlog = compile_src_to_mlog(src)

    except SyntaxError as e:
        logger.error(  # noqa: TRY400
            "A syntax error occurred while compiling %s:\n\n", target.name
        )
        print_exception(e, limit=0)
        sys.exit(1)

    except CompilerError as e:
        _log_err_and_exit(
            f"A compiler error occurred while compiling {target.name}:\n\n"
            f"{type(e).__name__}: {e!s}",
        )

    if args.stdout:
        sys.stdout.write(f"\n{indent(mlog, '\t' * (indent_level + 1))}\n\n")

    pyperclip = _try_import_clipboard()
    if args.copy and pyperclip is not None:
        try:
            pyperclip.copy(mlog)
        except pyperclip.PyperclipException:
            logger.exception(
                "An error occurred while copying output to clipboard: %s"
            )
            sys.exit(1)

    if args.file:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(mlog, encoding="utf-8")
        except OSError as e:
            _log_err_and_exit(f"Failed to write to '{output.resolve()}': {e!s}")


# thx pyndustric <3
def _create_parser() -> argparse.ArgumentParser:
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
        help="The output file/folder(s) (defaults to path/to/src/<target>.mlog).",
        dest="outputs",
    )
    parser.add_argument(
        "-s",
        "--stdout",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Print result to standard output (defaults to False).",
    )
    parser.add_argument(
        "--file",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Create output file/folder(s) (defaults to True).",
    )
    parser.add_argument(
        "-c",
        "--copy",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Copy output to clipboard. "
        f"Requires optional dependency '{CLIPBOARD_DEPENDENCY_NAME}'. "
        "Can only be used with singular files. Defaults to False.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(IndentFormatter("%(levelname)s %(message)s"))
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    parser = _create_parser()
    args = parser.parse_args(argv, namespace=Py2mlogCLIArgs())

    if args.outputs is None:
        args.outputs = []
    elif not args.file:
        parser.error(
            "'-o' or '--output' specify the output files."
            "They cannot be used with '--no-file'."
        )

    if not args.stdout and not args.file and not args.copy:
        parser.error(
            "No output provided; cannot disable stdout, "
            "file and clipboard outputs together."
        )

    if args.copy and _try_import_clipboard() is None:
        _log_err_and_exit(
            f"Missing dependency '{CLIPBOARD_DEPENDENCY_NAME}' "
            "for '-c' or '--clip'.",
        )

    time_st = perf_counter()
    for i, target in enumerate(args.targets):
        if i < len(args.outputs):
            output = args.outputs[i]
        else:
            output = target.with_suffix(".mlog") if target.is_file() else target

        _compile_path(args, target, output)

    logger.info("All done in %ss!", round(perf_counter() - time_st, 2))
