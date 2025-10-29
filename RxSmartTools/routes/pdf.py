"""Routes powering the smart PDF toolbox."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

from ..services import pdf_service
from ..utils.filesystem import resolve_upload_path, timestamped_name

LOGGER = logging.getLogger(__name__)

bp = Blueprint("pdf", __name__, url_prefix="/smart_split_merge")


@bp.route("/")
def smart_index():
    """Show the smart PDF toolbox UI."""

    return render_template("smart_split_merge.html")


@bp.route("/upload", methods=["POST"])
def smart_upload():
    """Persist an uploaded PDF and return its metadata."""

    uploaded_file = request.files.get("pdf")
    if uploaded_file is None:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    safe_name = secure_filename(uploaded_file.filename or "uploaded.pdf")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    upload_root = Path(current_app.config["UPLOAD_FOLDER"])
    destination_dir = upload_root / date_folder
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / safe_name
    uploaded_file.save(destination_path)

    try:
        reader = PdfReader(destination_path)
        total_pages = len(reader.pages)
    except Exception:  # pragma: no cover - PDF validation
        LOGGER.exception("Failed to read uploaded PDF")
        destination_path.unlink(missing_ok=True)
        return jsonify({"success": False, "error": "Invalid PDF"}), 400

    relative_path = str(Path(date_folder) / safe_name)
    return jsonify(
        {
            "success": True,
            "filename": relative_path.replace("\\", "/"),
            "total_pages": total_pages,
        }
    )


@bp.route("/process", methods=["POST"])
def smart_process():
    """Execute PDF processing actions requested by the client."""

    try:
        payload: dict[str, Any] = request.get_json(force=True)
    except Exception:  # pragma: no cover - request validation
        return jsonify({"error": "Invalid request payload"}), 400

    filename = payload.get("filename")
    actions = set(payload.get("actions", []))
    pages = _as_int_list(payload.get("pages", []))
    rotations = _as_rotation_map(payload.get("rotations", {}))

    if not filename:
        return jsonify({"error": "missing filename"}), 400

    input_path = resolve_upload_path(filename)
    if input_path is None or not input_path.exists():
        return jsonify({"error": "uploaded file not found"}), 404

    output_dir = Path(current_app.config["OUTPUT_FOLDER"])
    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_dir.mkdir(parents=True, exist_ok=True)

    working_path = input_path
    generated: list[str] = []
    split_performed = False

    if "rotate" in actions and rotations:
        rotated_path = output_dir / timestamped_name("rotated", ".pdf")
        try:
            pdf_service.rotate_pages(working_path, rotations, rotated_path)
            working_path = rotated_path
        except Exception as exc:  # pragma: no cover - service level logging handles
            LOGGER.exception("Rotation failed: %s", exc)

    if "remove" in actions and pages:
        removed_path = output_dir / timestamped_name("removed", ".pdf")
        try:
            pdf_service.remove_pages(working_path, pages, removed_path)
            working_path = removed_path
        except Exception as exc:
            LOGGER.exception("Remove pages failed: %s", exc)

    if "merge" in actions and pages:
        merged_path = output_dir / timestamped_name("merged", ".pdf")
        try:
            pdf_service.merge_pages(working_path, pages, merged_path)
            working_path = merged_path
        except Exception as exc:
            LOGGER.exception("Merge pages failed: %s", exc)

    if "split" in actions:
        try:
            split_files = pdf_service.split_pdf(working_path, output_dir)
            generated.extend(pdf_service.copy_outputs_to_saved(split_files, saved_dir))
            split_performed = True
        except Exception as exc:
            LOGGER.exception("Split failed: %s", exc)

    if "compress" in actions and not split_performed:
        compressed_path = output_dir / timestamped_name("compressed", ".pdf")
        try:
            pdf_service.compress_pdf(working_path, compressed_path)
            working_path = compressed_path
        except Exception as exc:
            LOGGER.exception("Compress failed: %s", exc)

    try:
        final_name = timestamped_name("result", ".pdf")
        final_path = saved_dir / final_name
        if working_path != final_path:
            shutil.copy(working_path, final_path)
        generated.append(final_name)
    except Exception as exc:
        LOGGER.exception("Final save failed: %s", exc)

    return jsonify({"generated": generated})


@bp.route("/pdf_to_word", methods=["POST"])
def pdf_to_word():
    """Convert selected PDF pages to a DOCX document."""

    payload = request.get_json(force=True)
    filename = payload.get("filename")
    pages = _as_int_list(payload.get("pages", []))

    if not filename or not pages:
        return jsonify({"error": "missing filename or pages"}), 400

    input_path = resolve_upload_path(filename)
    if input_path is None:
        return jsonify({"error": "file not found"}), 404

    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    saved_dir.mkdir(parents=True, exist_ok=True)
    output_name = timestamped_name("pdf2word", ".docx")
    output_path = saved_dir / output_name
    try:
        pdf_service.pages_to_word(input_path, pages, output_path)
        return jsonify({"generated": [output_name]})
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("PDF to Word conversion failed: %s", exc)
        return jsonify({"error": "conversion failed"}), 500


@bp.route("/pdf_to_excel", methods=["POST"])
def pdf_to_excel():
    """Convert selected PDF pages to an Excel workbook."""

    payload = request.get_json(force=True)
    filename = payload.get("filename")
    pages = _as_int_list(payload.get("pages", []))

    if not filename or not pages:
        return jsonify({"error": "missing filename or pages"}), 400

    input_path = resolve_upload_path(filename)
    if input_path is None:
        return jsonify({"error": "file not found"}), 404

    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    saved_dir.mkdir(parents=True, exist_ok=True)
    output_name = timestamped_name("pdf2excel", ".xlsx")
    output_path = saved_dir / output_name
    try:
        pdf_service.pages_to_excel(input_path, pages, output_path)
        return jsonify({"generated": [output_name]})
    except Exception as exc:
        LOGGER.exception("PDF to Excel conversion failed: %s", exc)
        return jsonify({"error": "conversion failed"}), 500


@bp.route("/uploads/<path:filename>")
def serve_upload(filename: str):
    """Serve files stored in the upload directory."""

    upload_root = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_root, filename)


@bp.route("/generated/<path:filename>")
def serve_generated(filename: str):
    """Serve generated files from the saved directory."""

    saved_root = current_app.config["SAVED_FOLDER"]
    return send_from_directory(saved_root, filename)


def _as_int_list(values: Any) -> list[int]:
    """Convert ``values`` to a sorted list of integers."""

    integers: list[int] = []
    if isinstance(values, list):
        for value in values:
            try:
                integers.append(int(value))
            except (TypeError, ValueError):
                continue
    return sorted(set(integers))


def _as_rotation_map(values: Any) -> dict[int, int]:
    """Convert user supplied rotations into an ``int -> angle`` mapping."""

    mapping: dict[int, int] = {}
    if isinstance(values, dict):
        for key, val in values.items():
            try:
                mapping[int(key)] = int(val) % 360
            except (TypeError, ValueError):
                continue
    return mapping
