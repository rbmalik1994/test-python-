"""Environment loading utilities for PaymentProcess.

This module provides a tiny ``.env`` parser so we do not rely on an
additional dependency (e.g., ``python-dotenv``). The loader is intentionally
minimal yet strict enough to catch misconfigurations early.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict
import os

_ENV_FILENAME = ".env"
_DEFAULT_ENV_PATH = Path(__file__).resolve().parents[1] / "data" / "config" / _ENV_FILENAME


@dataclass(frozen=True, slots=True)
class EnvConfig:
    """Strongly-typed configuration values sourced from ``.env``."""

    payment_db_uri: str


def _parse_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()

    if not stripped or stripped.startswith("#"):
        return None

    if "=" not in stripped:
        raise ValueError(f"Invalid .env line (missing '='): {line!r}")

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")

    if not key:
        raise ValueError("Environment variable key cannot be empty.")

    return key, value


def _read_env_file(path: Path) -> Dict[str, str]:
    env_map: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as handler:
        for raw_line in handler:
            parsed = _parse_line(raw_line)
            if parsed is None:
                continue

            key, value = parsed
            env_map[key] = value

    return env_map


def _resolve_value(key: str, values: Dict[str, str]) -> str:
    if key in values and values[key]:
        return values[key]

    env_value = os.environ.get(key)
    if env_value:
        return env_value

    raise RuntimeError(f"Required environment variable '{key}' is missing.")


def load_env(env_path: str | Path | None = None, *, override_process_env: bool = False) -> EnvConfig:
    """Load ``.env`` variables and optionally inject them into ``os.environ``."""

    path = Path(env_path) if env_path else _DEFAULT_ENV_PATH

    if not path.exists():
        raise FileNotFoundError(f".env file not found at {path}")

    values = _read_env_file(path)

    for key, value in values.items():
        if override_process_env or key not in os.environ:
            os.environ[key] = value

    payment_db_uri = _resolve_value("PAYMENT_DB_URI", values)

    return EnvConfig(payment_db_uri=payment_db_uri)


@lru_cache(maxsize=1)
def get_env_config(env_path: str | Path | None = None) -> EnvConfig:
    """Cached accessor around :func:`load_env` to avoid duplicate IO."""

    return load_env(env_path)
