"""Routes powering the smart PDF toolbox."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Blueprint,
    abort,
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

bp = Blueprint("pdf", __name__, url_prefix="/pdf")

# Serve the PDF toolbox assets directly from the template folder so the CSS/JS can
# live alongside the HTML instead of in the global static directory.
ASSET_DIR = Path(__file__).resolve().parent.parent / "templates" / "tools" / "pdf"


@bp.route("/")
def smart_index():
    """Show the smart PDF toolbox UI."""

    return render_template("tools/pdf/pdf_toolbox.html")


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

    # Parse JSON payload safely and provide helpful logs on failure
    payload = request.get_json(silent=True)
    if payload is None:
        raw = b""
        try:
            raw = request.get_data() or b""
        except Exception:
            pass
        raw_text = "<binary>" if isinstance(raw, (bytes, bytearray)) and len(raw) > 2000 else raw.decode(errors="replace")
        LOGGER.error("Invalid JSON payload received: %s", raw_text)
        return (
            jsonify({"error": "Invalid or missing JSON payload", "raw": raw_text}),
            400,
        )

    # filename = payload.get("filename")
    filenames = payload.get("filenames")
    actions = set(payload.get("actions", []))
    pages = _as_int_list(payload.get("pages", []))
    rotations = _as_rotation_map(payload.get("rotations", {}))

    # Optional: support batch operations (list of filenames) and a client-chosen compression level
    compression_level = payload.get("compression_level", "default")

    # Expect `filenames` to be a list (batch operations). Use the first entry
    # as the primary input for single-file operations (rotate/remove/merge/split).
    if not isinstance(filenames, list) or len(filenames) == 0:
        return jsonify({"error": "missing filename(s)"}), 400

    if not actions:
        return jsonify({"error": "no actions provided"}), 400

    # Primary filename for single-input operations
    filename = filenames[0]

    input_path = resolve_upload_path(filename)
    if input_path is None or not input_path.exists():
        return jsonify({"error": "uploaded file not found"}), 404

    output_dir = Path(current_app.config["OUTPUT_FOLDER"])
    saved_dir = Path(current_app.config["SAVED_FOLDER"])
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_dir.mkdir(parents=True, exist_ok=True)

    working_path = input_path
    generated: list[str] = []
    progress: list[str] = []
    errors: list[str] = []
    split_performed = False

    if "rotate" in actions and rotations:
        rotated_path = output_dir / timestamped_name("rotated", ".pdf")
        try:
            pdf_service.rotate_pages(working_path, rotations, rotated_path)
            working_path = rotated_path
            generated.extend(pdf_service.copy_outputs_to_saved([rotated_path], saved_dir))
        except Exception as exc:  # pragma: no cover - service level logging handles
            LOGGER.exception("Rotation failed: %s", exc)

    if "remove" in actions and pages:
        print(f" pages : {pages}")
        removed_path = output_dir / timestamped_name("removed", ".pdf")
        print(f" removed_path : {removed_path}")
        try:
            pdf_service.remove_pages(working_path, pages, removed_path)
            working_path = removed_path
            generated.extend(pdf_service.copy_outputs_to_saved([removed_path], saved_dir))
        except Exception as exc:
            LOGGER.exception("Remove pages failed: %s", exc)

    # Merge modes:
    # - pages_per_file: file_page_map provided -> create one output per source using selected pages
    # - files_whole: merge whole files from `filenames` into a single merged output
    # - files_and_pages: file_page_map provided -> extract selected pages from each file and combine into single output
    if "merge" in actions:
        merge_mode = payload.get("merge_mode")
        file_page_map_raw = payload.get("file_page_map")
        

        # pages_per_file: produce one output per source file containing only the chosen pages
        if merge_mode == "pages_per_file" and isinstance(file_page_map_raw, dict):
            for fn, pages_list in file_page_map_raw.items():
                in_path = resolve_upload_path(fn)
                if in_path is None or not in_path.exists():
                    msg = f"Merge (per-file): input not found {fn}"
                    LOGGER.warning(msg)
                    errors.append(msg)
                    continue
                try:
                    out_name = timestamped_name(f"{Path(fn).stem}-pages-merged", ".pdf")
                    out_path = output_dir / out_name
                    pdf_service.merge_pages(in_path, _as_int_list(pages_list), out_path)
                    generated.extend(pdf_service.copy_outputs_to_saved([out_path], saved_dir))
                    progress.append(f"Merged pages for {fn} -> {out_name}")
                except Exception as exc:
                    LOGGER.exception("Merge pages (per-file) failed for %s: %s", fn, exc)
                    errors.append(f"Merge failed for {fn}")

        # files_whole: combine multiple files into a single merged file
        elif merge_mode == "files_whole":
            fns = filenames if isinstance(filenames, list) else []
            paths = []
            for fn in fns:
                p = resolve_upload_path(fn)
                if p is None or not p.exists():
                    msg = f"Merge (files_whole): input not found {fn}"
                    LOGGER.warning(msg)
                    errors.append(msg)
                    continue
                paths.append(p)
            if paths:
                try:
                    merged_name = timestamped_name("merged", ".pdf")
                    merged_path = output_dir / merged_name
                    pdf_service.merge_files(paths, merged_path, progress_callback=lambda m: progress.append(m))
                    generated.extend(pdf_service.copy_outputs_to_saved([merged_path], saved_dir))
                    progress.append(f"Merged {len(paths)} files -> {merged_name}")
                except Exception as exc:
                    LOGGER.exception("Merge files failed: %s", exc)
                    errors.append("Merge files failed")

        # files_and_pages: extract specified pages from each file and combine into one merged file
        elif merge_mode == "files_and_pages" and isinstance(file_page_map_raw, dict):
            mapping: dict[Path, list[int]] = {}
            for fn, pages_list in file_page_map_raw.items():
                p = resolve_upload_path(fn)
                if p is None or not p.exists():
                    msg = f"Merge (files_and_pages): input not found {fn}"
                    LOGGER.warning(msg)
                    errors.append(msg)
                    continue
                mapping[p] = _as_int_list(pages_list)
            if mapping:
                try:
                    merged_name = timestamped_name("merged", ".pdf")
                    merged_path = output_dir / merged_name
                    pdf_service.merge_selected_pages_from_multiple_files(mapping, merged_path, progress_callback=lambda m: progress.append(m))
                    generated.extend(pdf_service.copy_outputs_to_saved([merged_path], saved_dir))
                    progress.append(f"Merged selected pages from {len(mapping)} files -> {merged_name}")
                except ValueError as val_err:
                    LOGGER.exception("Invalid page selection during merge: %s", val_err)
                    errors.append(str(val_err))
                except Exception as exc:
                    LOGGER.exception("Merge files+pages failed: %s", exc)
                    errors.append("Merge files+pages failed")

        # fallback: legacy behavior — merge selected pages from primary file
        elif pages:
            merged_path = output_dir / timestamped_name("merged", ".pdf")
            try:
                pdf_service.merge_pages(working_path, pages, merged_path)
                working_path = merged_path
                generated.extend(pdf_service.copy_outputs_to_saved([merged_path], saved_dir))
                progress.append(f"Merged selected pages from primary file -> {merged_path.name}")
            except Exception as exc:
                LOGGER.exception("Merge pages failed: %s", exc)
                errors.append("Merge pages failed")

        else:
            # nothing to do for merge
            pass

    if "split" in actions:
        try:
            split_files = pdf_service.split_pdf(working_path, output_dir)
            generated.extend(pdf_service.copy_outputs_to_saved(split_files, saved_dir))
            split_performed = True
        except Exception as exc:
            LOGGER.exception("Split failed: %s", exc)

    if "compress" in actions and not split_performed:
        # If the client provided a list of filenames, compress each input in the batch
        try:
            if isinstance(filenames, list) and filenames:
                for fn in filenames:
                    in_path = resolve_upload_path(fn)
                    if in_path is None or not in_path.exists():
                        LOGGER.warning("Batch compress: input not found %s", fn)
                        continue
                    compressed_path = output_dir / timestamped_name("compressed", ".pdf")
                    try:
                        pdf_service.compress_pdf(in_path, compressed_path, quality=compression_level)
                        # copy compressed output to saved folder and record
                        generated.extend(pdf_service.copy_outputs_to_saved([compressed_path], saved_dir))
                    except Exception as exc:  # pragma: no cover - service level logging handles
                        LOGGER.exception("Compress failed for %s: %s", fn, exc)
            else:
                compressed_path = output_dir / timestamped_name("compressed", ".pdf")
                pdf_service.compress_pdf(working_path, compressed_path, quality=compression_level)
                working_path = compressed_path
        except Exception as exc:
            LOGGER.exception("Compress failed: %s", exc)

    # try:
    #     final_name = timestamped_name("result", ".pdf")
    #     final_path = saved_dir / final_name
    #     if working_path != final_path:
    #         shutil.copy(working_path, final_path)
    #     generated.append(final_name)
    # except Exception as exc:
    #     LOGGER.exception("Final save failed: %s", exc) 
    
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


@bp.route("/assets/<path:filename>")
def serve_pdf_asset(filename: str):
    """Serve CSS/JS assets that live next to the toolbox template.

    The files stay in ``templates/tools/pdf`` but are exposed here so the
    browser receives the correct MIME type instead of a 404 HTML page.
    """

    safe_path = (ASSET_DIR / filename).resolve()
    if ASSET_DIR not in safe_path.parents and safe_path != ASSET_DIR:
        abort(404)
    return send_from_directory(ASSET_DIR, filename)


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
