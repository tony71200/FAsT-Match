"""ctypes wrapper for the FAsT-Match C API shared library."""

from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Iterable


class FastMatchDllError(RuntimeError):
    """Raised when shared-library based matching fails."""


def _default_library_candidates() -> Iterable[Path]:
    root = Path(__file__).resolve().parents[1]
    return (
        root / "build" / "libfast_match_capi.so",
        root / "build" / "Release" / "fast_match_capi.dll",
        root / "build" / "Debug" / "fast_match_capi.dll",
        root / "build" / "libfast_match_capi.dylib",
    )


def _load_library(library_path: str | Path | None):
    if library_path is None:
        for cand in _default_library_candidates():
            if cand.exists():
                library_path = cand
                break

    if library_path is None:
        raise FastMatchDllError(
            "Cannot find fast_match_capi shared library. Build it first with CMake."
        )

    lib = ctypes.CDLL(str(library_path))
    func = lib.fast_match_template_paths
    func.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_int,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
    ]
    func.restype = ctypes.c_int
    return func


def match_template_paths_via_dll(
    image_path: str | Path,
    template_path: str | Path,
    *,
    library_path: str | Path | None = None,
    epsilon: float = 0.15,
    delta: float = 0.25,
    photometric_invariance: bool = False,
    min_scale: float = 0.5,
    max_scale: float = 2.0,
) -> list[list[float]]:
    """Run FAsT-Match via shared library and return 4 transformed corners."""
    func = _load_library(library_path)

    out = (ctypes.c_float * 8)()
    err = ctypes.create_string_buffer(1024)
    ret = func(
        str(image_path).encode("utf-8"),
        str(template_path).encode("utf-8"),
        ctypes.c_float(epsilon),
        ctypes.c_float(delta),
        ctypes.c_int(1 if photometric_invariance else 0),
        ctypes.c_float(min_scale),
        ctypes.c_float(max_scale),
        out,
        8,
        err,
        len(err),
    )

    if ret != 0:
        message = err.value.decode("utf-8", errors="replace") or "Unknown error"
        raise FastMatchDllError(message)

    return [[float(out[i]), float(out[i + 1])] for i in range(0, 8, 2)]
