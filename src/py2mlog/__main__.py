import argparse
import ast
from pathlib import Path

from py2mlog.compiler.compiler import Compiler
from py2mlog.compiler.emitter import Emitter
from py2mlog.mlog.codegen import generate_mlog


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
        parser.error(f"Could not read '{target.resolve()}'.")
    except FileNotFoundError:
        parser.error(f"Could not find '{target.resolve()}'.")
    except OSError as e:
        parser.error(
            f"An OS error occurred while reading '{target.resolve()}': {e}"
        )

    emitter = Emitter()
    Compiler(src, ast.parse(src), emitter).compile()
    mlog = generate_mlog(emitter.instructions)

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


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="py2mlog",
        description="A python to mindustry logic (mlog) compiler.",
    )

    parser.add_argument("target", type=Path, help="The target file to compile.")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        type=Path,
        help="The output file (defaults to <target>.mlog).",
    )

    args = parser.parse_args()

    if args.output is None:
        args.output = args.target.with_suffix(".mlog")

    _compile_file(parser, args.target, args.output)
