"""Environment loading utilities for PaymentProcess.

This module provides a tiny ``.env`` parser so we do not rely on an
additional dependency (e.g., ``python-dotenv``). The loader is intentionally
minimal yet strict enough to catch misconfigurations early.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict
import os

from .config_models import (
    AuditMongoConfig,
    AuditMongoDB,
    BusinessConfig,
    DirEnv,
    EnvConfig,
    MCPMongoDB,
    MongoConfig,
    NHOracleConfig,
    OracleConfig,
    PbmFinOracleConfig,
    PbmProdOracleConfig,
)
from .error_handling import ConfigurationError

_ENV_FILENAME = ".env"
_DEFAULT_ENV_PATH = Path(__file__).resolve().parents[1] / "data" / "config" / _ENV_FILENAME


def _parse_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()

    if not stripped or stripped.startswith("#"):
        return None

    if "=" not in stripped:
        raise ConfigurationError(f"Invalid .env line (missing '='): {line!r}")

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")

    if not key:
        raise ConfigurationError("Environment variable key cannot be empty.")

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


_CONFIG_CACHE: dict[str, EnvConfig] = {}


def _determine_env_path(env_name: str | None, env_path: str | Path | None) -> Path:
    if env_path is not None:
        return Path(env_path).expanduser().resolve()

    explicit_env = env_name or os.environ.get("PYTHON_RUN_ENV_FILE")
    if explicit_env:
        candidate = _DEFAULT_ENV_PATH.with_name(f"{_ENV_FILENAME}.{explicit_env}")
        return candidate

    return _DEFAULT_ENV_PATH


def _infer_env_name(path: Path) -> str:
    filename = path.name
    prefix = f"{_ENV_FILENAME}."
    if filename.startswith(prefix):
        return filename[len(prefix) :]
    if filename == _ENV_FILENAME:
        return "default"
    return filename


def _get_optional_value(key: str, values: Dict[str, str]) -> str | None:
    env_value = os.environ.get(key)
    if env_value is not None and env_value != "":
        return env_value
    return values.get(key)


def _get_required_value(key: str, values: Dict[str, str]) -> str:
    value = _get_optional_value(key, values)
    if value is None or value == "":
        raise ConfigurationError(f"Required environment variable '{key}' is missing.")
    return value


def _get_int_value(key: str, values: Dict[str, str], default: int = 0) -> int:
    raw_value = _get_optional_value(key, values)
    if raw_value is None or raw_value == "":
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"Environment variable '{key}' must be an integer.") from exc


def load_env(
    env_name: str | None = None,
    env_path: str | Path | None = None,
    *,
    override_process_env: bool = False,
) -> EnvConfig:
    """Load ``.env`` variables and optionally inject them into ``os.environ``."""

    path = _determine_env_path(env_name, env_path)

    if not path.exists():
        raise ConfigurationError(f".env file not found at {path}")

    values = _read_env_file(path)

    for key, value in values.items():
        if override_process_env or key not in os.environ:
            os.environ[key] = value

    timezone = _get_optional_value("TIMEZONE", values) or "UTC"

    directories = DirEnv(
        arch_dir=_get_optional_value("ARCH_DIR", values),
        data_dir=_get_optional_value("DATA_DIR", values),
        log_dir=_get_optional_value("LOG_DIR", values),
        utils_dir=_get_optional_value("UTILS_DIR", values),
        scripts_dir=_get_optional_value("SCRIPTS_DIR", values),
        app_dir=_get_optional_value("PROJECT_DIR", values),
    )

    mongo_config = MongoConfig(
        host=_get_optional_value("MONGO_MCP_CLAIM_HOST", values),
        auth=_get_optional_value("MONGO_MCP_CLAIM_AUTH", values),
        replicaset=_get_optional_value("MONGO_MCP_CLAIM_REPLICASET", values),
        user=_get_optional_value("MONGO_USER", values),
        password=_get_optional_value("MONGO_PASSWD", values),
        timezone=timezone,
    )

    audit_mongo_config = AuditMongoConfig(
        host=_get_optional_value("MONGO_MCP_AUDIT_HOST", values),
        auth=_get_optional_value("MONGO_MCP_AUDIT_AUTH", values),
        replicaset=_get_optional_value("MONGO_MCP_AUDIT_REPLICASET", values),
        user=_get_optional_value("MONGO_AUDIT_USER", values),
        password=_get_optional_value("MONGO_AUDIT_PASSWD", values),
        timezone=timezone,
    )

    mcp_mongo_db = MCPMongoDB(
        fin=_get_optional_value("FIN_DB", values),
        mcp=_get_optional_value("MCP_DB", values),
        import_db=_get_optional_value("IMPRT_DB", values),
    )

    audit_mongo_db = AuditMongoDB(
        eh=_get_optional_value("EH_PROD_AUDIT", values),
        hta=_get_optional_value("HTA_PROD_AUDIT", values),
    )

    oracle = OracleConfig(
        user=_get_optional_value("ORACLE_USER", values),
        password=_get_optional_value("ORACLE_PASSWD", values),
        tns=_get_optional_value("ORACLE_TNS", values),
        host=_get_optional_value("ORACLE_HOST", values),
        port=_get_optional_value("ORACLE_PORT", values),
        protocol=_get_optional_value("ORACLE_PROTOCOL", values),
        service_name=_get_optional_value("ORACLE_SERVICE_NAME", values),
    )

    pbm_fin_oracle = PbmFinOracleConfig(
        user=_get_optional_value("PBM_FIN_ORACLE_USER", values),
        password=_get_optional_value("PBM_FIN_ORACLE_PASSWD", values),
        tns=_get_optional_value("PBM_FIN_ORACLE_TNS", values),
        host=_get_optional_value("PBM_FIN_ORACLE_HOST", values),
        port=_get_optional_value("PBM_FIN_ORACLE_PORT", values),
        protocol=_get_optional_value("PBM_FIN_ORACLE_PROTOCOL", values),
        service_name=_get_optional_value("PBM_FIN_ORACLE_SERVICE_NAME", values),
    )

    pbm_prod_oracle = PbmProdOracleConfig(
        user=_get_optional_value("PBM_PROD_ORACLE_USER", values),
        password=_get_optional_value("PBM_PROD_ORACLE_PASSWD", values),
        tns=_get_optional_value("PBM_PROD_ORACLE_TNS", values),
        host=_get_optional_value("PBM_PROD_ORACLE_HOST", values),
        port=_get_optional_value("PBM_PROD_ORACLE_PORT", values),
        protocol=_get_optional_value("PBM_PROD_ORACLE_PROTOCOL", values),
        service_name=_get_optional_value("PBM_PROD_ORACLE_SERVICE_NAME", values),
    )

    nh_oracle = NHOracleConfig(
        user=_get_optional_value("NH_ORACLE_USER", values),
        password=_get_optional_value("NH_ORACLE_PASSWD", values),
        tns=_get_optional_value("NH_ORACLE_TNS", values),
        host=_get_optional_value("NH_ORACLE_HOST", values),
        port=_get_optional_value("NH_ORACLE_PORT", values),
        protocol=_get_optional_value("NH_ORACLE_PROTOCOL", values),
        service_name=_get_optional_value("NH_ORACLE_SERVICE_NAME", values),
    )

    business = BusinessConfig(
        business_id=_get_int_value("BUSINESS_ID", values, default=0),
        name=_get_optional_value("BUSINESS_NAME", values),
        code=_get_optional_value("BUSINESS_ACRONYM", values),
    )

    payment_db_uri = _get_required_value("PAYMENT_DB_URI", values)
    env_label = _infer_env_name(path)
    os.environ["PYTHON_RUN_ENV_FILE"] = env_label

    return EnvConfig(
        env_name=env_label,
        env_file=path,
        payment_db_uri=payment_db_uri,
        timezone=timezone,
        directories=directories,
        mongo_config=mongo_config,
        audit_mongo_config=audit_mongo_config,
        mcp_mongo_db=mcp_mongo_db,
        audit_mongo_db=audit_mongo_db,
        oracle=oracle,
        pbm_fin_oracle=pbm_fin_oracle,
        pbm_prod_oracle=pbm_prod_oracle,
        nh_oracle=nh_oracle,
        business=business,
    )


def get_env_config(env_name: str | None = None, env_path: str | Path | None = None) -> EnvConfig:
    """Cached accessor around :func:`load_env` to avoid duplicate IO."""

    resolved_path = _determine_env_path(env_name, env_path)
    cache_key = str(resolved_path)

    cached = _CONFIG_CACHE.get(cache_key)
    if cached is not None:
        return cached

    config = load_env(env_path=resolved_path)
    _CONFIG_CACHE[cache_key] = config
    return config
