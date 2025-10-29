"""Flask application entry point."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask

from .config import Config
from .routes import register_blueprints
from .services.file_service import prepare_runtime_directories

LOGGER = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""

    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    _prepare_directories(app)
    register_blueprints(app)

    return app


def _prepare_directories(app: Flask) -> None:
    """Ensure all runtime directories exist before handling requests."""

    directories = [
        Path(app.config["UPLOAD_FOLDER"]),
        Path(app.config["SAVED_FOLDER"]),
        Path(app.config["THUMBNAIL_FOLDER"]),
        Path(app.config["RESULT_FOLDER"]),
        Path(app.config["SPLIT_FOLDER"]),
        Path(app.config["MERGE_FOLDER"]),
        Path(app.config["OUTPUT_FOLDER"]),
    ]
    prepare_runtime_directories(directories)


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    LOGGER.info("Starting development server on port %s", port)
    app.run(debug=True, port=port)
