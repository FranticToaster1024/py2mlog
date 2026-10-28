import argparse
import ast
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
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


def _compile_file(
    parser: argparse.ArgumentParser, target: Path, output: Path
) -> None:
    if target.is_dir():
        parser.error(f"Target '{target.resolve()}' is a directory.")
    if target.suffix != ".py":
        parser.error(
            f"Target '{target.resolve()}' does not have a .py extension."
        )

    if output.is_dir():
        parser.error(f"Output '{output.resolve()}' is a directory.")
    if output.suffix != ".mlog":
        parser.error(
            f"Output '{output.resolve()}' does not have a .mlog extension."
        )

    src = ""
    try:
        with open(target, encoding="utf-8") as f:
            src = f.read()
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
        sys.stderr.write(
            f"A syntax error occurred while compiling {target.name}:\n\n"
        )
        print_exception(e, limit=0)
        sys.exit(1)
    except CompilerError as e:
        sys.stderr.write(
            f"A compiler error occurred while compiling {target.name}:\n\n"
        )
        sys.stderr.write(f"{type(e).__name__}: {e}")
        sys.exit(1)

    try:
        with open(output, "w", encoding="utf-8") as f:
            f.write(mlog)
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
        help="The target file(s) to compile.",
        metavar="target",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="+",
        default=None,
        type=Path,
        help="The output file(s) (defaults to <target>.mlog).",
        dest="outputs",
    )

    args = parser.parse_args(argv, namespace=Py2mlogCLIArgs())

    if args.outputs is None:
        args.outputs = []

    time_st_all = perf_counter()
    for i, target in enumerate(args.targets):
        time_st_iter = perf_counter()

        if i < len(args.outputs):
            output = args.outputs[i]
        else:
            output = target.with_suffix(".mlog")

        print(f"Compiling {target.name} to {output.name}...")

        _compile_file(parser, target, output)

        print(f"Done in {perf_counter() - time_st_iter:.2f}s.\n")

    print(f"All done in {perf_counter() - time_st_all:.2f}s!")
