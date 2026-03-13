"""Python package for FAsT-Match."""

from .dll_api import FastMatchDllError, match_template_paths_via_dll

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
