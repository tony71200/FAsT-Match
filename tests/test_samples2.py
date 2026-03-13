#!/usr/bin/env python3
"""Smoke test for ctypes(shared library) flow using bundled images."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = [
    (ROOT / "image.png", ROOT / "template.png"),
    (ROOT / "image2.png", ROOT / "template2.png"),
]


def _validate(corners: list[list[float]]) -> None:
    if len(corners) != 4:
        raise AssertionError(f"Expected 4 corners, got {len(corners)}")
    for p in corners:
        if len(p) != 2:
            raise AssertionError(f"Invalid point: {p}")
        if not all(isinstance(v, (int, float)) for v in p):
            raise AssertionError(f"Point must be numeric: {p}")


def main() -> int:
    try:
        from fast_match.dll_api import FastMatchDllError, match_template_paths_via_dll
    except Exception as exc:
        print(f"[ERROR] Cannot import dll_api: {exc}")
        return 1

    library_candidates = [
        ROOT / "build" / "libfast_match_capi.so",
        ROOT / "build" / "libfast_match_capi.dylib",
        ROOT / "build" / "Release" / "fast_match_capi.dll",
        ROOT / "build" / "Debug" / "fast_match_capi.dll",
    ]
    library_path = next((p for p in library_candidates if p.exists()), None)

    if library_path is None:
        print("[ERROR] Shared library not found.")
        print("Build first, e.g.: cmake -S . -B build && cmake --build build")
        return 1

    ok = True
    for image_path, template_path in SAMPLES:
        try:
            corners = match_template_paths_via_dll(
                image_path,
                template_path,
                library_path=library_path,
            )
            _validate(corners)
            print(f"[OK] {image_path.name} + {template_path.name} -> {corners}")
        except FastMatchDllError as exc:
            ok = False
            print(f"[FAIL] DLL matching failed for {image_path.name}: {exc}")
        except Exception as exc:
            ok = False
            print(f"[FAIL] Unexpected error for {image_path.name}: {exc}")

    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
