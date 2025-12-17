"""Application configuration module."""

from __future__ import annotations

import os
from pathlib import Path


class BaseConfig:
    """Base Flask configuration shared across environments."""

    PROJECT_ROOT = Path(__file__).resolve().parent
    DATA_ROOT = PROJECT_ROOT / "temp_data"
    DATA_ROOT.mkdir(parents=True, exist_ok=True)

    UPLOAD_FOLDER = DATA_ROOT / "uploads"
    SAVED_FOLDER = DATA_ROOT / "saved"
    THUMBNAIL_FOLDER = DATA_ROOT / "thumbnails"
    RESULT_FOLDER = DATA_ROOT / "comparison_results"
    SPLIT_FOLDER = DATA_ROOT / "split"
    MERGE_FOLDER = DATA_ROOT / "merge"
    OUTPUT_FOLDER = DATA_ROOT / "output"

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
