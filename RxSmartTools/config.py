"""Application configuration module."""

from __future__ import annotations

import os
from pathlib import Path


class BaseConfig:
    """Base Flask configuration shared across environments."""

    BASE_DIR = Path(__file__).resolve().parent 
    # Use a dedicated temp_data directory as the new base directory
    TEMP_DATA_DIR = BASE_DIR / "temp_data"
    TEMP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    BASE_DIR = TEMP_DATA_DIR
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    SAVED_FOLDER = BASE_DIR / "saved"
    THUMBNAIL_FOLDER = BASE_DIR / "thumbnails"
    RESULT_FOLDER = BASE_DIR / "comparison_results"
    SPLIT_FOLDER = BASE_DIR / "split"
    MERGE_FOLDER = BASE_DIR / "merge"
    OUTPUT_FOLDER = BASE_DIR / "output"

    # Default Excel comparison columns
    DEFAULT_MERGE_KEYS = ["NDC"]
    DEFAULT_COMPARE_COLUMNS = [
        "MEDID",
        "Drug Tier",
        "PA",
        "QL",
        "PA Type",
        "PA Description",
        "QL Days",
        "QL Amount",
    ]

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "rx-smart-tools")
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB uploads


Config = BaseConfig
