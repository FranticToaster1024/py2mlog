from dataclasses import dataclass
from enum import Enum
from typing import Literal

from py2mlog.compiler.error import SourceLocation

# eventually this should handle more stuff


class Directives(Enum):
    INLINE = "inline"
    UNROLL = "unroll"


@dataclass(frozen=True)
class UnrollDirective:
    factor: int | Literal["full"]

    src_loc: SourceLocation
