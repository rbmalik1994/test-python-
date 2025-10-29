"""File handling helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..utils.filesystem import clear_directories, ensure_directories


def prepare_runtime_directories(directories: Iterable[Path]) -> None:
    """Ensure that working directories exist."""

    ensure_directories(directories)


def reset_runtime_directories(directories: Iterable[Path]) -> None:
    """Clear and recreate working directories."""

    clear_directories(directories)
    ensure_directories(directories)
