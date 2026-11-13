import subprocess
import sys
from pathlib import Path

import py2mlog
from py2mlog.compiler.mlog_builtins import ALIGN_MAP, ENV_ATTR_MAP

gen = f"""
class Content:
    pass


class Env:
{"\n".join(f"\t{s}: Content" for s in ENV_ATTR_MAP)}


class Alignment:
    pass

class Align:
{"\n".join(f"\t{s}: Alignment" for s in ALIGN_MAP)}
"""

# py2mlog.__file__ points to the __init__.py not directory apparently
gen_path = (Path(py2mlog.__file__).parent / "_gen.pyi").resolve()
gen_path.write_text(gen, encoding="utf-8")


subprocess.run(
    [sys.executable, "-m", "ruff", "check", "--fix", gen_path], check=True
)
subprocess.run([sys.executable, "-m", "ruff", "format", gen_path], check=True)
subprocess.run([sys.executable, "-m", "pyright", gen_path], check=True)
