"""Helpers for discovering .env files relative to a module path."""

from __future__ import annotations

from pathlib import Path

__all__ = ["find_dotenv_path"]


def find_dotenv_path(
    anchor_file: str | Path,
    env_filename: str = ".env",
    max_levels: int = 5,
) -> Path | None:
    """Return the first env file found when walking up from ``anchor_file``.

    Args:
        anchor_file: File path used as the starting point for the search.
        env_filename: The env file name to look for (defaults to ".env").
        max_levels: Maximum number of parent directories to traverse.

    Returns:
        The resolved Path to the env file if found, otherwise ``None``.
    """

    if max_levels < 1:
        raise ValueError("max_levels must be at least 1")

    current_dir = Path(anchor_file).resolve().parent
    levels = 0

    while True:
        candidate = current_dir / env_filename
        if candidate.exists():
            return candidate

        levels += 1
        if levels >= max_levels or current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

    return None
