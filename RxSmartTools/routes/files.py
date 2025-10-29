"""Routes that expose saved and uploaded files."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, redirect, render_template, url_for

bp = Blueprint("files", __name__)


@bp.route("/saved_files")
def saved_files():
    """List saved/generated files."""

    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    files = (
        sorted(file.name for file in saved_dir.iterdir()) if saved_dir.exists() else []
    )
    return render_template("saved_files.html", files=files)


@bp.route("/uploaded_files")
def uploaded_files():
    """List uploaded files by their relative path."""

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    if not upload_dir.exists():
        return render_template("uploaded_files.html", files=[])
    files = sorted(
        str(path.relative_to(upload_dir)).replace("\\", "/")
        for path in upload_dir.rglob("*")
        if path.is_file()
    )
    return render_template("uploaded_files.html", files=files)


@bp.route("/delete/<path:filename>")
def delete_file(filename: str):
    """Delete a saved file and redirect back to the listing."""

    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    target = saved_dir / filename
    if target.exists():
        target.unlink(missing_ok=True)
    return redirect(url_for("files.saved_files"))
