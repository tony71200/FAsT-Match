"""Python package for FAsT-Match."""

from .dll_api import FastMatchDllError, match_template_paths_via_dll

try:
    from ._fast_match import FastMatch, match_template_paths
except Exception:  # pragma: no cover - allows dll_api usage without extension installed
    FastMatch = None  # type: ignore
    match_template_paths = None  # type: ignore

__all__ = [
    "FastMatch",
    "match_template_paths",
    "FastMatchDllError",
    "match_template_paths_via_dll",
]
