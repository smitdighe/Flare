"""Chroma vector store lifecycle only — no embedding/indexing (that's Phase 7).

Module-level lazy singleton client; blocking calls are wrapped in
``asyncio.to_thread`` so they are safe to await from async code.
"""

from __future__ import annotations

import asyncio
from typing import Any

import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from app.config import get_settings

_client: ClientAPI | None = None
#: get_or_create_collection is a Chroma sqlite round trip. It ran on every
#: retrieve (i.e. every alert); the handle is stable for a given client, so
#: it is created once and dropped whenever the client is.
_collection: Collection | None = None


def _build_client() -> ClientAPI:
    settings = get_settings()
    return chromadb.PersistentClient(path=str(settings.chroma_persist_dir))


def get_client() -> ClientAPI:
    """Lazily create the module-level PersistentClient."""
    global _client
    if _client is None:
        _client = _build_client()
    return _client


def _get_collection_sync() -> Collection:
    global _collection
    if _collection is None:
        settings = get_settings()
        _collection = get_client().get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


async def get_collection() -> Collection:
    """Get-or-create the configured collection (cosine space)."""
    return await asyncio.to_thread(_get_collection_sync)


def _collection_stats_sync() -> dict[str, Any]:
    col = _get_collection_sync()
    return {"documents": col.count()}


async def collection_stats() -> dict[str, Any]:
    """Return ``{"documents": n}`` for /health/deep."""
    return await asyncio.to_thread(_collection_stats_sync)


def _close_client_sync() -> None:
    client = _client
    if client is None:
        return
    # chromadb's PersistentClient owns a sqlite3 connection. Dropping the
    # reference without releasing it leaves the connection to be closed by the
    # GC at an arbitrary later moment, which surfaces as an "Exception ignored in
    # Connection.__del__" from wherever the collection happened to happen.
    for method in ("reset", "clear_system_cache"):
        closer = getattr(client, method, None)
        if closer is None:
            continue
        try:
            closer()
            return
        except Exception as exc:  # noqa: BLE001 — best effort on the way out
            _log_close_failure(method, exc)
            continue
    _log_close_failure("all", RuntimeError("no usable closer on the Chroma client"))


def _log_close_failure(method: str, exc: BaseException) -> None:
    from app.core.logging import get_logger

    get_logger(__name__).warning("chroma.closer_failed", method=method, error=str(exc))


async def close_client() -> None:
    """Release the Chroma client's resources on shutdown. Never raises."""
    global _client, _collection
    if _client is None:
        return
    try:
        await asyncio.to_thread(_close_client_sync)
    except Exception as exc:  # noqa: BLE001 — shutdown must not fail on cleanup
        from app.core.logging import get_logger

        get_logger(__name__).warning("chroma.close_failed", error=str(exc))
    finally:
        _client = None
        _collection = None
