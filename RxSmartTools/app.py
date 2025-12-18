"""Flask application entry point."""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask

# Prefer relative imports when the package is used as a module, but allow
# running the file directly (python RxSmartTools/app.py) by falling back to
# absolute imports after ensuring the parent directory is on sys.path.
try:
    from .config import Config
    from .routes import register_blueprints
    from .services.file_service import prepare_runtime_directories
except ImportError:
    # Running as a script: add project root to sys.path and import by package name
    import sys
    from pathlib import Path as _Path

    sys.path.append(str(_Path(__file__).resolve().parent.parent))
    from RxSmartTools.config import Config
    from RxSmartTools.routes import register_blueprints
    from RxSmartTools.services.file_service import prepare_runtime_directories

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def create_app() -> Flask:
    """Create and configure the Flask application."""
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
        Path(app.config["OUTPUT_FOLDER"]),
    ]
    prepare_runtime_directories(directories)


app = create_app()


if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 5001))
    # LOGGER.info("Starting development server on port %s", port)
    app.run(debug=True)
