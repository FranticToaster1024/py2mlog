from py2mlog.compiler.error import CompilerError, CompilerErrorType

from . import builtins, control, mem, screen, unit
from .intrinsic_func_utils import IntrinsicFuncMap

__all__ = [
    "NAMESPACES_NAME_TO_FUNC_MAP_MAP",
    "builtins",
    "control",
    "mem",
    "screen",
    "unit",
]


def _get_namespaces_name_to_func_map_map() -> dict[str, IntrinsicFuncMap]:
    namespaces_name_to_func_map_map: dict[str, IntrinsicFuncMap] = {}

    for intrinsic_namespace in (control, mem, screen, unit):
        namespace_name: str | None = getattr(
            intrinsic_namespace, "NAMESPACE_NAME", None
        )
        if namespace_name is None:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Intrinsic namespace '{intrinsic_namespace!r}' "
                "missing attribute 'NAMESPACE_NAME'",
            )

        func_map: IntrinsicFuncMap | None = getattr(
            intrinsic_namespace, "FUNC_MAP", None
        )
        if func_map is None:
            raise CompilerError(
                CompilerErrorType.INTERNAL,
                None,
                err=f"Intrinsic namespace '{intrinsic_namespace!r}' "
                "missing attribute 'FUNC_MAP'",
            )

        namespaces_name_to_func_map_map[namespace_name] = func_map

    return namespaces_name_to_func_map_map


NAMESPACES_NAME_TO_FUNC_MAP_MAP = _get_namespaces_name_to_func_map_map()
