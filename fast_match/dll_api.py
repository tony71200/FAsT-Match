"""ctypes wrapper for the FAsT-Match C API shared library."""

from __future__ import annotations

import ctypes
import os
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


def _windows_dependency_dirs(library_path: Path) -> list[Path]:
    dirs: list[Path] = []

    # Ensure directory of fast_match_capi.dll is searched first.
    dirs.append(library_path.parent)

    # Common OpenCV runtime location from OpenCV_DIR env, e.g. C:/opencv/build/x64/vc17/bin
    opencv_dir = os.environ.get("OpenCV_DIR")
    if opencv_dir:
        base = Path(opencv_dir)
        dirs.extend(
            [
                base / "x64" / "vc17" / "bin",
                base / "x64" / "vc16" / "bin",
                base / "bin",
            ]
        )

    # Respect any user-provided extra DLL directories.
    extra = os.environ.get("FAST_MATCH_DLL_DIRS")
    if extra:
        for part in extra.split(os.pathsep):
            if part.strip():
                dirs.append(Path(part.strip()))

    # Keep existing order but remove duplicates.
    seen: set[str] = set()
    result: list[Path] = []
    for item in dirs:
        key = str(item.resolve()) if item.exists() else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _register_windows_dll_dirs(library_path: Path) -> None:
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    for dll_dir in _windows_dependency_dirs(library_path):
        if dll_dir.exists():
            os.add_dll_directory(str(dll_dir))


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

    lib_path = Path(library_path)
    _register_windows_dll_dirs(lib_path)

    try:
        lib = ctypes.CDLL(str(lib_path))
    except OSError as exc:
        raise FastMatchDllError(
            "Cannot load fast_match_capi shared library. "
            "On Windows this often means missing dependent DLLs (e.g. OpenCV runtime). "
            "Set OpenCV_DIR correctly or add runtime folders via FAST_MATCH_DLL_DIRS. "
            f"Library: {lib_path}. Original error: {exc}"
        ) from exc

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
