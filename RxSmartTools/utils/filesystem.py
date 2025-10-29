"""Filesystem helpers used across the application."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def ensure_directories(directories: Iterable[Path]) -> None:
    """Ensure that each directory in ``directories`` exists."""

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def clear_directories(directories: Iterable[Path]) -> None:
    """Remove all files and folders within the supplied directories."""

    for root in directories:
        try:
            if not root.exists():
                root.mkdir(parents=True, exist_ok=True)
                continue
            for entry in root.iterdir():
                try:
                    if entry.is_dir():
                        shutil.rmtree(entry)
                    else:
                        entry.unlink()
                except Exception as exc:  # pragma: no cover - defensive logging
                    logging.getLogger(__name__).warning(
                        "Failed to remove %s: %s", entry, exc
                    )
        except Exception as exc:  # pragma: no cover
            logging.getLogger(__name__).exception(
                "Error clearing directory %s: %s", root, exc
            )


def timestamped_name(prefix: str, suffix: str = "") -> str:
    """Create a unique file name with timestamp and short UUID."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    token = uuid4().hex[:6]
    return f"{prefix}_{timestamp}_{token}{suffix}"


def resolve_upload_path(relative_path: str) -> Path | None:
    """Locate an uploaded file given its relative path within the upload folder."""

    uploads_root = Path(current_app.config["UPLOAD_FOLDER"])  # type: ignore[arg-type]
    relative = Path(relative_path)
    safe_parts = [secure_filename(part) for part in relative.parts if part]
    if not safe_parts:
        return None
    candidate = uploads_root.joinpath(*safe_parts)
    if candidate.exists():
        return candidate

    target_name = Path(relative_path).name
    for file_path in uploads_root.rglob(target_name):
        return file_path
    return None
