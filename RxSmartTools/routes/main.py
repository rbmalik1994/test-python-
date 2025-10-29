"""Routes for the landing page."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, render_template

from ..services.file_service import reset_runtime_directories

bp = Blueprint("main", __name__)


def _runtime_directories() -> list[Path]:
    """Return the list of directories that should be cleared on each visit."""

    return [
        Path(current_app.config["UPLOAD_FOLDER"]),
        Path(current_app.config["SAVED_FOLDER"]),
        Path(current_app.config["THUMBNAIL_FOLDER"]),
        Path(current_app.config["RESULT_FOLDER"]),
        Path(current_app.config["SPLIT_FOLDER"]),
        Path(current_app.config["MERGE_FOLDER"]),
        Path(current_app.config["OUTPUT_FOLDER"]),
    ]


@bp.route("/")
def index():
    """Display the landing page and reset transient directories."""

    reset_runtime_directories(_runtime_directories())
    cleared_message = datetime.now().strftime(
        "Temporary files cleared at %Y-%m-%d %H:%M:%S"
    )
    return render_template("index.html", cleared_msg=cleared_message)
