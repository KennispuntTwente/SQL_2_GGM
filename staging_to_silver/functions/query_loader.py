"""
Query loader: scan a package for modules that expose
__query_exports__ = {"DEST_TABLE": callable}

Usage:
    from staging_to_silver.functions.query_loader import load_queries
    # Default behavior (no normalization):
    queries = load_queries()
    # Normalize destination table names to UPPER and column labels to LOWER:
    queries = load_queries(table_name_case="upper", column_name_case="lower")
"""

from importlib import import_module
import importlib.util
import os
import hashlib
import pkgutil
import inspect
from functools import lru_cache
from typing import Callable, Dict, Optional, Sequence

from sqlalchemy.sql.elements import ColumnElement  # type: ignore


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


def _wrap_builder_for_column_case(
    fn: Callable, column_name_case: Optional[str]
) -> Callable:
    """
    Wrap a query builder function so that the returned SELECT statement has
    its projected column labels coerced to the requested case (upper/lower).

    The wrapper is a no-op when `column_name_case` is falsy.
    """
    if not column_name_case:
        return fn

    def _wrapped(engine, *args, **kwargs):  # keep first param 'engine'
        stmt = fn(engine, *args, **kwargs)
        # We only attempt to transform SQLAlchemy Select-like objects
        # that expose `selected_columns` and `with_only_columns`.
        if hasattr(stmt, "selected_columns") and hasattr(stmt, "with_only_columns"):
            cols = []
            for col in stmt.selected_columns:  # type: ignore[attr-defined]
                # ColumnElement has `.name` for label/column key
                label_name = getattr(col, "name", None)
                if not isinstance(col, ColumnElement) or label_name is None:
                    cols.append(col)
                    continue
                new_name = _normalize_key(label_name, column_name_case)
                # Relabel only when necessary to avoid redundant nesting
                if new_name != label_name:
                    cols.append(col.label(new_name))
                else:
                    cols.append(col)
            # SQLAlchemy 2.0 expects varargs for with_only_columns; older versions accepted a list
            try:
                return stmt.with_only_columns(*cols, maintain_column_froms=True)
            except TypeError:
                try:
                    return stmt.with_only_columns(*cols)
                except TypeError:
                    try:
                        return stmt.with_only_columns(cols, maintain_column_froms=True)
                    except TypeError:
                        return stmt.with_only_columns(cols)
        return stmt

    # Preserve metadata for debuggability
    _wrapped.__name__ = getattr(fn, "__name__", "wrapped_query_builder")
    _wrapped.__doc__ = getattr(fn, "__doc__", None)
    _wrapped.__module__ = getattr(fn, "__module__", __name__)
    return _wrapped


@lru_cache(maxsize=None)
def _load_queries_cached(
    package: str,
    normalize: Optional[str],
    table_name_case: Optional[str],
    column_name_case: Optional[str],
    extra_modules_tuple: tuple[str, ...],
    extra_paths_tuple: tuple[str, ...],
    scan_package: bool,
) -> Dict[str, Callable]:
    """Hashable-args version of load_queries for safe caching.

    Do not call directly; use load_queries which normalizes arguments.
    """
    queries: Dict[str, Callable] = {}

    # Back-compat shim
    if table_name_case is None:
        table_name_case = normalize

    if scan_package:
        # Import the package and list its modules
        pkg = import_module(package)
        module_names = sorted(
            (
                m
                for _, m, ispkg in pkgutil.iter_modules(pkg.__path__)
                if not ispkg and not m.startswith("_")
            ),
            key=str.lower,
        )

        # Merge exports from each module in the package
        for mod_name in module_names:
            module = import_module(f"{package}.{mod_name}")
            for dest, fn in _load_exports(module).items():
                key = _normalize_key(dest, table_name_case)
                if key in queries:
                    prev = queries[key].__module__
                    raise ValueError(
                        f"Duplicate query for destination '{key}': "
                        f"{module.__name__} conflicts with {prev}"
                    )
                queries[key] = _wrap_builder_for_column_case(fn, column_name_case)

    # Optionally merge exports from explicitly named modules
    for mod_path in extra_modules_tuple or ():
        try:
            module = import_module(mod_path)
        except ModuleNotFoundError:
            continue
        for dest, fn in _load_exports(module).items():
            key = _normalize_key(dest, table_name_case)
            if key in queries:
                prev = queries[key].__module__
                raise ValueError(
                    f"Duplicate query for destination '{key}': "
                    f"{module.__name__} conflicts with {prev}"
                )
            queries[key] = _wrap_builder_for_column_case(fn, column_name_case)

    # Optionally merge exports from filesystem paths (directories or individual files)
    for path in extra_paths_tuple or ():
        if not path:
            continue
        # Resolve environment variables and user tilde, then absolute
        resolved = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
        if not os.path.exists(resolved):
            continue

        py_files: list[str] = []
        if os.path.isdir(resolved):
            # Collect .py files recursively under the directory, skip dunder and private modules
            for root, _, files in os.walk(resolved):
                for fname in files:
                    if not fname.endswith(".py"):
                        continue
                    if fname == "__init__.py" or fname.startswith("_"):
                        continue
                    py_files.append(os.path.join(root, fname))
        elif resolved.endswith(".py"):
            py_files.append(resolved)
        else:
            # Non-.py file, skip
            continue

        for file_path in sorted(set(py_files), key=str.lower):
            # Create a stable, unique module name based on file path
            digest = hashlib.md5(file_path.encode("utf-8")).hexdigest()  # nosec - used for namespacing only
            mod_name = f"staging_to_silver.dynamic.m_{digest}"

            try:
                spec = importlib.util.spec_from_file_location(mod_name, file_path)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                # type: ignore[attr-defined]
                spec.loader.exec_module(module)  # Executes the module code
            except Exception:
                # Skip files that cannot be imported
                continue

            for dest, fn in _load_exports(module).items():
                key = _normalize_key(dest, table_name_case)
                if key in queries:
                    prev = queries[key].__module__
                    raise ValueError(
                        f"Duplicate query for destination '{key}': "
                        f"{module.__name__} conflicts with {prev}"
                    )
                queries[key] = _wrap_builder_for_column_case(fn, column_name_case)

    if not queries:
        raise RuntimeError(
            f"No queries discovered. Ensure {package} exists, has an __init__.py, "
            "and its modules define __query_exports__ = {'DEST_TABLE': builder}."
        )
    return queries


def load_queries(
    package: str = "staging_to_silver.queries",
    normalize: Optional[str] = None,  # deprecated alias for table_name_case
    table_name_case: Optional[str] = None,
    column_name_case: Optional[str] = None,
    extra_modules: Sequence[str] = (),
    extra_files_or_dirs: Sequence[str] = (),
    scan_package: bool = True,
) -> Dict[str, Callable]:
    """
    Public entry that normalizes arguments and delegates to cached implementation.

    - `table_name_case`: "upper" | "lower" | None — coerces destination table keys.
    - `column_name_case`: "upper" | "lower" | None — coerces projected column labels.
    - `normalize`: deprecated alias for `table_name_case` (kept for compatibility).
    - `extra_modules`: optional list/sequence of fully-qualified module names to merge.
    """
    # Coerce unhashable extra_modules (e.g. lists) into a tuple to satisfy caching
    extra_tuple = tuple(extra_modules or ())
    extra_paths_tuple = tuple(extra_files_or_dirs or ())
    return _load_queries_cached(
        package,
        normalize,
        table_name_case,
        column_name_case,
        extra_tuple,
        extra_paths_tuple,
        scan_package,
    )


# Expose cache control helpers on the public function for tests/back-compat
load_queries.cache_clear = _load_queries_cached.cache_clear  # type: ignore[attr-defined]
load_queries.cache_info = _load_queries_cached.cache_info  # type: ignore[attr-defined]
