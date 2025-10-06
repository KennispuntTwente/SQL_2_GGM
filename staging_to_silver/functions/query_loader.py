"""
Query loader: scan a package for modules that expose
__query_exports__ = {"DEST_TABLE": callable}

Usage:
    from staging_to_silver.functions.query_loader import load_queries
    queries = load_queries()  # or load_queries(normalize="upper")
"""

from importlib import import_module
import pkgutil
import inspect
from functools import lru_cache
from typing import Callable, Dict, Optional, Sequence

def _load_exports(mod) -> Dict[str, Callable]:
    exports = getattr(mod, "__query_exports__", None)
    if not isinstance(exports, dict):
        return {}

    out: Dict[str, Callable] = {}
    for k, v in exports.items():
        if not callable(v):
            continue
        # Light, non-fatal validation: first parameter named 'engine'
        try:
            sig = inspect.signature(v)
            params = list(sig.parameters.values())
            if not params or params[0].name != "engine":
                pass
        except (ValueError, TypeError):
            pass
        out[k] = v
    return out

def _normalize_key(name: str, mode: Optional[str]) -> str:
    if not mode:
        return name
    mode = mode.lower()
    if mode == "upper":
        return name.upper()
    if mode == "lower":
        return name.lower()
    return name  # unknown mode -> no-op

@lru_cache(maxsize=None)
def load_queries(
    package: str = "staging_to_silver.queries",
    normalize: Optional[str] = None,
    extra_modules: Sequence[str] = (),
) -> Dict[str, Callable]:
    """
    Scan `package` for modules and merge their __query_exports__ dicts.
    - `normalize`: "upper" | "lower" | None — coerces destination keys.
    - `extra_modules`: optional list of fully-qualified module names to merge.
    """
    queries: Dict[str, Callable] = {}

    # Import the package and list its modules
    pkg = import_module(package)
    module_names = sorted(
        (m for _, m, ispkg in pkgutil.iter_modules(pkg.__path__) if not ispkg and not m.startswith("_")),
        key=str.lower,
    )

    # Merge exports from each module in the package
    for mod_name in module_names:
        module = import_module(f"{package}.{mod_name}")
        for dest, fn in _load_exports(module).items():
            key = _normalize_key(dest, normalize)
            if key in queries:
                prev = queries[key].__module__
                raise ValueError(
                    f"Duplicate query for destination '{key}': "
                    f"{module.__name__} conflicts with {prev}"
                )
            queries[key] = fn

    # Optionally merge exports from explicitly named modules
    for mod_path in extra_modules or ():
        try:
            module = import_module(mod_path)
        except ModuleNotFoundError:
            continue
        for dest, fn in _load_exports(module).items():
            key = _normalize_key(dest, normalize)
            if key in queries:
                prev = queries[key].__module__
                raise ValueError(
                    f"Duplicate query for destination '{key}': "
                    f"{module.__name__} conflicts with {prev}"
                )
            queries[key] = fn

    if not queries:
        raise RuntimeError(
            f"No queries discovered. Ensure {package} exists, has an __init__.py, "
            "and its modules define __query_exports__ = {'DEST_TABLE': builder}."
        )
    return queries
