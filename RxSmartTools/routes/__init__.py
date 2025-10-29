"""Blueprint registration helpers."""

from __future__ import annotations

from flask import Flask

from . import excel, files, main, pdf


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""

    app.register_blueprint(main.bp)
    app.register_blueprint(pdf.bp)
    app.register_blueprint(excel.bp)
    app.register_blueprint(files.bp)
