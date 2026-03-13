"""Python package for FAsT-Match."""

import os
from pathlib import Path

from .dll_api import FastMatchDllError, match_template_paths_via_dll


def _register_opencv_dll_dirs() -> None:
    """On Windows, add OpenCV runtime directories to DLL search path."""
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    opencv_dir = os.environ.get("OpenCV_DIR")
    if not opencv_dir:
        return

    base = Path(opencv_dir)
    candidates = [
        base / "x64" / "vc17" / "bin",
        base / "x64" / "vc16" / "bin",
        base / "bin",
    ]
    for d in candidates:
        if d.is_dir():
            os.add_dll_directory(str(d))


_register_opencv_dll_dirs()

_EXTENSION_IMPORT_ERROR = None

try:
    from ._fast_match import FastMatch, match_template_paths
except Exception as exc:  # pragma: no cover
    _EXTENSION_IMPORT_ERROR = exc

    class FastMatch:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "Cannot import fast_match._fast_match extension module. "
                f"Original error: {_EXTENSION_IMPORT_ERROR}"
            )

    def match_template_paths(*args, **kwargs):  # type: ignore
        raise ImportError(
            "Cannot import fast_match._fast_match extension module. "
            f"Original error: {_EXTENSION_IMPORT_ERROR}"
        )


__all__ = [
    "FastMatch",
    "match_template_paths",
    "FastMatchDllError",
    "match_template_paths_via_dll",
]
