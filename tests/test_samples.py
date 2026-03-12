#!/usr/bin/env python3
"""Smoke test for fast_match package using bundled sample images."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = [
    (ROOT / "image.png", ROOT / "template.png"),
    (ROOT / "image2.png", ROOT / "template2.png"),
]


def _validate_corners(corners: list[list[float]], image_path: Path) -> None:
    if not isinstance(corners, list):
        raise AssertionError("Result must be a list")

    if len(corners) != 4:
        raise AssertionError(f"Expected 4 corners, got {len(corners)}")

    for idx, point in enumerate(corners):
        if not isinstance(point, list) or len(point) != 2:
            raise AssertionError(f"Corner #{idx} must be [x, y], got: {point}")

        x, y = point
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise AssertionError(f"Corner #{idx} must contain numeric values, got: {point}")

    # Optional extra sanity check with OpenCV dimensions if cv2 is installed.
    try:
        import cv2  # type: ignore
    except ImportError:
        return

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise AssertionError(f"Cannot read sample image: {image_path}")

    height, width = image.shape[:2]
    min_x = min(p[0] for p in corners)
    max_x = max(p[0] for p in corners)
    min_y = min(p[1] for p in corners)
    max_y = max(p[1] for p in corners)

    if max_x < -20 or min_x > width + 20 or max_y < -20 or min_y > height + 20:
        raise AssertionError(
            f"All corners appear outside image bounds for {image_path.name}: {corners}"
        )


def main() -> int:
    try:
        from fast_match import match_template_paths
    except Exception as exc:  # pragma: no cover
        print("[ERROR] Cannot import fast_match package.")
        print("Install/build it first, for example: python -m pip install .")
        print(f"Details: {exc}")
        return 1

    all_ok = True
    for image_path, template_path in SAMPLES:
        if not image_path.exists() or not template_path.exists():
            print(f"[ERROR] Missing sample files: {image_path} / {template_path}")
            return 1

        try:
            corners = match_template_paths(str(image_path), str(template_path))
            _validate_corners(corners, image_path)
            print(f"[OK] {image_path.name} + {template_path.name} -> {corners}")
        except Exception as exc:
            all_ok = False
            print(f"[FAIL] {image_path.name} + {template_path.name}: {exc}")

    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())
