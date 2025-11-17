"""MongoDB connection utilities for PaymentProcess.

This module centralizes the creation of a process-wide MongoDB client so the
rest of the codebase can share a single, thread-safe connection handle. The
functions intentionally avoid embedding business logic so they remain easy to
mock in tests.
"""

from __future__ import annotations

from threading import Lock
from urllib.parse import urlparse

from pymongo import MongoClient
from pymongo.database import Database


_CLIENT_SINGLETON: MongoClient | None = None
_CLIENT_LOCK = Lock()


def _ensure_database_name(db_uri: str, explicit_db: str | None) -> str:
    if explicit_db:
        return explicit_db

    parsed = urlparse(db_uri)
    db_name = parsed.path.lstrip("/") if parsed.path else ""
    if not db_name:
        raise ValueError(
            "MongoDB URI must include a database name or the `db_name` argument must be provided."
        )
    return db_name


def get_mongo_client(db_uri: str) -> MongoClient:
    """Return a cached :class:`~pymongo.mongo_client.MongoClient` instance."""

    global _CLIENT_SINGLETON

    if _CLIENT_SINGLETON is None:
        with _CLIENT_LOCK:
            if _CLIENT_SINGLETON is None:
                _CLIENT_SINGLETON = MongoClient(db_uri, appname="PaymentProcess")

    return _CLIENT_SINGLETON


def get_database(db_uri: str, db_name: str | None = None) -> Database:
    """Convenience helper that returns a :class:`~pymongo.database.Database`."""

    client = get_mongo_client(db_uri)
    resolved_db_name = _ensure_database_name(db_uri, db_name)
    return client.get_database(resolved_db_name)


def close_mongo_client() -> None:
    """Dispose the cached Mongo client if it has been initialized."""

    global _CLIENT_SINGLETON

    if _CLIENT_SINGLETON is not None:
        _CLIENT_SINGLETON.close()
        _CLIENT_SINGLETON = None
