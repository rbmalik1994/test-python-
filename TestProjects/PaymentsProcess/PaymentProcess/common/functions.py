"""Common helper functions shared across the PaymentProcess project.

Keep these helpers narrowly focused on environment access and connection
management. Business logic should live within the :mod:`core` package while
utilities that are widely used but not domain-specific can stay here.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def get_env(name: str, default: str | None = None) -> str | None:
    """Retrieve an environment variable with a default fallback.

    Parameters
    ----------
    name:
        Name of the environment variable to read.
    default:
        Optional default value returned when the environment variable is not
        set. Use ``None`` when the variable is required and upstream code must
        perform additional validation.
    """

    return os.environ.get(name, default)


def get_default_workers() -> int:
    """Determine a reasonable default number of workers.

    The heuristic should be refined once workload characteristics are known.
    The current implementation favors CPU count while capping at eight to
    reduce context switching in early iterations.
    """

    cpu_count = os.cpu_count() or 4
    return min(cpu_count, 8)


def resolve_db_uri(cli_value: str | None) -> str:
    """Resolve the database URI using CLI override or environment variable.

    Parameters
    ----------
    cli_value:
        Value passed via ``--db-uri``. When ``None`` the function falls back to
        ``PAYMENT_DB_URI``.

    Returns
    -------
    str
        Resolved connection string.

    Raises
    ------
    RuntimeError
        If no value can be resolved.
    """

    if cli_value:
        return cli_value

    env_value = get_env("PAYMENT_DB_URI")
    if env_value:
        return env_value

    raise RuntimeError("Database URI is required but was not provided.")


_CONNECTION_SINGLETON: Any | None = None


def get_connection(db_uri: str) -> Any:
    """Return a process-wide singleton connection object.

    Replace this stub with concrete connection pooling. The function is
    designed to abstract away connection state so downstream modules can remain
    agnostic of the underlying datastore client implementation.
    """

    global _CONNECTION_SINGLETON

    if _CONNECTION_SINGLETON is None:
        # Delay importing heavy drivers until implementation time.
        _CONNECTION_SINGLETON = {"db_uri": db_uri}

    return _CONNECTION_SINGLETON


def close_connection() -> None:
    """Clean up the cached connection if the underlying client exposes close.

    The placeholder implementation simply clears the singleton cache. Update
    this function to gracefully shut down the actual connection when the real
    client is integrated.
    """

    global _CONNECTION_SINGLETON
    _CONNECTION_SINGLETON = None
