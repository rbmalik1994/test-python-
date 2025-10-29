"""Routes for the Excel comparison tool."""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request, send_file

from ..services import excel_service
from ..utils.filesystem import timestamped_name

LOGGER = logging.getLogger(__name__)

bp = Blueprint("excel", __name__, url_prefix="/excel")


@bp.route("/", methods=["GET", "POST"])
def excel_tool():
    """Render the Excel comparison form and process uploads."""

    download_one = None
    download_two = None
    error_message = None

    if request.method == "POST":
        file_one = request.files.get("file1")
        file_two = request.files.get("file2")

        if not file_one or not file_two:
            error_message = "Both files are required."
            return (
                render_template(
                    "excel.html",
                    download1=download_one,
                    download2=download_two,
                    error_message=error_message,
                ),
                400,
            )

        saved_dir = Path(current_app.config["SAVED_FOLDER"])
        saved_dir.mkdir(parents=True, exist_ok=True)

        upload_one = saved_dir / timestamped_name("uploaded_file1", ".xlsx")
        upload_two = saved_dir / timestamped_name("uploaded_file2", ".xlsx")
        file_one.save(upload_one)
        file_two.save(upload_two)

        merge_keys = request.form.getlist("merge_keys")
        compare_columns = request.form.getlist("compare_columns")

        if not merge_keys:
            merge_keys = list(current_app.config["DEFAULT_MERGE_KEYS"])
        if not compare_columns:
            compare_columns = list(current_app.config["DEFAULT_COMPARE_COLUMNS"])

        try:
            result_dir = Path(current_app.config["RESULT_FOLDER"])
            result_one, result_two = excel_service.highlight_differences(
                upload_one, upload_two, merge_keys, compare_columns, result_dir
            )
            download_one = result_one.name
            download_two = result_two.name
        except Exception as exc:  # pragma: no cover
            LOGGER.exception("Excel comparison failed: %s", exc)
            error_message = "Comparison failed. Please verify your files."

    return render_template(
        "excel.html",
        download1=download_one,
        download2=download_two,
        error_message=error_message,
    )


@bp.route("/get_common_columns", methods=["POST"])
def get_common_columns():
    """Return the shared column names between two supplied Excel files."""

    file_one = request.files.get("file1")
    file_two = request.files.get("file2")

    if file_one is None or file_two is None:
        return jsonify({"error": "Please upload both files"}), 400

    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    saved_dir.mkdir(parents=True, exist_ok=True)

    temp_one = saved_dir / timestamped_name("tmp_file1", ".xlsx")
    temp_two = saved_dir / timestamped_name("tmp_file2", ".xlsx")

    file_one.save(temp_one)
    file_two.save(temp_two)

    try:
        columns = excel_service.common_columns(temp_one, temp_two)
        return jsonify({"columns": columns})
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Reading common columns failed: %s", exc)
        return jsonify({"error": f"Error reading Excel files: {exc}"}), 500
    finally:
        temp_one.unlink(missing_ok=True)
        temp_two.unlink(missing_ok=True)


@bp.route("/download/<path:filename>")
def download_result(filename: str):
    """Provide access to generated comparison files."""

    result_root = Path(current_app.config["RESULT_FOLDER"])
    return send_file(result_root / filename, as_attachment=True)
