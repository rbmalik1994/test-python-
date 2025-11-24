"""MongoDB connection utilities for PaymentProcess.

This module centralizes the creation of a process-wide MongoDB client so the
rest of the codebase can share a single, thread-safe connection handle. The
functions intentionally avoid embedding business logic so they remain easy to
mock in tests.
"""

from __future__ import annotations

from threading import RLock
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.database import Database

from .load_env import get_env_config


_CLIENT_SINGLETON: MongoClient | None = None
_CLIENT_LOCK = RLock()
_DATABASE_CACHE: dict[str, Database] = {}
_DEFAULT_DB_URI: str | None = None
_DEFAULT_APP_NAME: str | None = None
_DEFAULT_DB_NAME: str | None = None


def configure_default_connection(db_uri: str, app_name: str | None = None, db_name: str | None = None) -> None:
    """Persist default connection details so callers can omit parameters later."""

    global _DEFAULT_DB_URI, _DEFAULT_APP_NAME, _DEFAULT_DB_NAME

    _DEFAULT_DB_URI = db_uri
    _DEFAULT_APP_NAME = app_name
    _DEFAULT_DB_NAME = db_name
    _DATABASE_CACHE.clear()


def _bootstrap_defaults_from_env() -> None:
    if _DEFAULT_DB_URI:
        return

    try:
        env_config = get_env_config()
    except FileNotFoundError:
        return
    except RuntimeError:
        return

    configure_default_connection(env_config.payment_db_uri)


def generate_db_uri(
    host: str,
    user: str | None = None,
    password: str | None = None,
    auth: str | None = None,
    replicaset: str | None = None,
) -> str:
    """Generate a MongoDB URI from the given parameters."""

    credentials = ""
    if user:
        escaped_user = quote_plus(user)
        escaped_password = quote_plus(password or "")
        password_segment = f":{escaped_password}" if password is not None else ""
        credentials = f"{escaped_user}{password_segment}@"

    path = f"/{auth}" if auth else "/"
    options: list[str] = []
    if replicaset:
        options.append(f"replicaSet={quote_plus(replicaset)}")
    query = f"?{'&'.join(options)}" if options else ""
    return f"mongodb://{credentials}{host}{path}{query}"


def _resolve_db_uri(explicit_uri: str | None) -> str:
    if explicit_uri:
        return explicit_uri

    if _DEFAULT_DB_URI is None:
        _bootstrap_defaults_from_env()

    if _DEFAULT_DB_URI is None:
        raise ValueError(
            "A MongoDB URI must be provided or configured via `configure_default_connection` or .env."
        )

    return _DEFAULT_DB_URI


def _resolve_app_name(explicit_app_name: str | None) -> str:
    return explicit_app_name or _DEFAULT_APP_NAME or "PaymentProcess"


def _resolve_db_name(explicit_db_name: str | None) -> str:
    resolved = explicit_db_name or _DEFAULT_DB_NAME
    if not resolved:
        raise ValueError(
            "A database name must be provided directly or stored via `configure_default_connection`."
        )
    return resolved


def get_mongo_client(db_uri: str | None = None, app_name: str | None = None) -> MongoClient:
    """Create and return a cached MongoDB client using the provided URI and application name."""

    global _CLIENT_SINGLETON, _DEFAULT_DB_URI, _DEFAULT_APP_NAME

    if _CLIENT_SINGLETON is None:
        with _CLIENT_LOCK:
            if _CLIENT_SINGLETON is None:
                resolved_uri = _resolve_db_uri(db_uri)
                resolved_app_name = _resolve_app_name(app_name)
                _CLIENT_SINGLETON = MongoClient(resolved_uri, appname=resolved_app_name)
                _DATABASE_CACHE.clear()
                if _DEFAULT_DB_URI is None:
                    _DEFAULT_DB_URI = resolved_uri
                if _DEFAULT_APP_NAME is None:
                    _DEFAULT_APP_NAME = resolved_app_name

    return _CLIENT_SINGLETON


def get_database(db_name: str | None = None) -> Database:
    """Retrieve a database instance by name using the existing MongoDB client."""

    resolved_db_name = _resolve_db_name(db_name)
    with _CLIENT_LOCK:
        cached_db = _DATABASE_CACHE.get(resolved_db_name)
        if cached_db is not None:
            return cached_db

    client = get_mongo_client()
    database = client.get_database(resolved_db_name)
    with _CLIENT_LOCK:
        _DATABASE_CACHE[resolved_db_name] = database
    return database


def close_mongo_client() -> None:
    """Dispose the cached Mongo client if it has been initialized."""

    global _CLIENT_SINGLETON

    if _CLIENT_SINGLETON is not None:
        _CLIENT_SINGLETON.close()
        _CLIENT_SINGLETON = None
        _DATABASE_CACHE.clear()
