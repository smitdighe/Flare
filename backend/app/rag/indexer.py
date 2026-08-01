"""Build the MITRE ATT&CK vector index in Chroma — idempotent via upsert.

Running ``build_index`` twice leaves the collection identical: deterministic
chunk ids + upsert, plus a stored corpus hash that lets a matching index skip
work entirely (unless ``force=True``).
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from datetime import UTC, datetime
from functools import partial
from typing import Any

from app.config import get_settings
from app.core.logging import get_logger
from app.rag.chunker import Chunk, chunk_corpus
from app.rag.mitre_loader import load_corpus

log = get_logger(__name__)

_model: Any = None
_PROGRESS_EVERY = 25


class OnnxEmbedder:
    """all-MiniLM-L6-v2 through chromadb's bundled ONNX runtime.

    Same weights and the same 384-dim output as the sentence-transformers build,
    without importing torch. That matters because torch is ~400MB of resident
    memory on its own; on top of the ~130MB the app already holds it puts a
    512MB container over the line and the process is OOM-killed during startup,
    long before it can answer a health check.

    Only ``encode`` is implemented, because ``encode`` is the entire surface the
    rest of the codebase uses of a SentenceTransformer. Keeping the signature
    identical (including the ignored ``show_progress_bar``) is what lets
    :func:`get_embedding_model` swap backends without any caller knowing.
    """

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._fn = ONNXMiniLM_L6_V2()
        # Instance-level override of the class attribute chromadb downloads into.
        # Its default is ~/.cache; pinning it under the app's own data directory
        # means a build step that warms the model leaves the weights where the
        # runtime is certain to find them.
        self._fn.DOWNLOAD_PATH = get_settings().embedding_cache_dir
        # Embed one throwaway string so construction really does leave the model
        # resident. chromadb downloads the weights and builds the ORT session
        # lazily, on first call — without this the startup warmup would return in
        # milliseconds having loaded nothing, and the whole cost would land in
        # the first alert's retrieve node, which is exactly what the warmup
        # exists to prevent. Constructing a SentenceTransformer loads eagerly, so
        # this is also what keeps the two backends behaving the same way.
        self._fn(["warmup"])

    def encode(self, texts: Any, show_progress_bar: bool = False) -> Any:  # noqa: ARG002
        import numpy as np

        if isinstance(texts, str):
            return np.asarray(self._fn([texts])[0])
        return np.asarray(self._fn(list(texts)))


def get_embedding_model() -> Any:
    """Cached embedding model for settings.EMBEDDING_BACKEND.

    Returns an object exposing ``encode(texts) -> ndarray`` regardless of which
    backend is configured.
    """
    global _model
    if _model is None:
        settings = get_settings()
        if settings.embedding_backend == "sentence-transformers":
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(settings.embedding_model)
        else:
            _model = OnnxEmbedder()
    return _model


def reset_embedding_model() -> None:
    """Drop the cached model (tests, and switching backends at runtime)."""
    global _model
    _model = None


def embedding_model_id() -> str:
    """Identifier stamped into the collection metadata and /health/deep.

    Names the BACKEND as well as the model, because "which weights built this
    index" is the question that matters when a rebuilt index stops matching the
    queries being run against it.
    """
    settings = get_settings()
    if settings.embedding_backend == "sentence-transformers":
        return settings.embedding_model
    return "onnx/all-MiniLM-L6-v2"


def corpus_hash(chunks: list[Chunk]) -> str:
    h = hashlib.sha256()
    for c in sorted(chunks, key=lambda x: x.id):
        h.update(c.id.encode())
        h.update(b"\x1f")
        h.update(c.embed_text.encode())
        h.update(b"\x1e")
    return h.hexdigest()


async def _get_default_collection() -> Any:
    from app.store.chroma import get_collection

    return await get_collection()


def _embed_all(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), _PROGRESS_EVERY):
        batch = texts[start : start + _PROGRESS_EVERY]
        vecs = model.encode(batch, show_progress_bar=False)
        embeddings.extend(v.tolist() for v in vecs)
        log.info("rag.embed_progress", done=len(embeddings), total=len(texts))
    return embeddings


async def build_index(force: bool = False, collection: Any = None) -> dict[str, Any]:
    """Build/refresh the index. Every chromadb and file call goes to a thread.

    chromadb's client and the corpus reader are both synchronous; run bare in a
    coroutine they block the loop for the whole index build (tens of seconds on
    a cold embedding model), which stalls the API if this is ever triggered from
    a running app rather than the CLI.
    """
    t0 = time.perf_counter()
    docs = await asyncio.to_thread(load_corpus)
    chunks = chunk_corpus(docs)
    chash = corpus_hash(chunks)
    expected = len(chunks)

    col = collection or await _get_default_collection()

    meta = dict(col.metadata or {})
    if not force and await asyncio.to_thread(col.count) == expected:
        if meta.get("corpus_hash") == chash:
            log.info("rag.index_skip", reason="up-to-date", documents=expected)
            return await asyncio.to_thread(index_stats, col)

    ids = [c.id for c in chunks]
    texts = [c.embed_text for c in chunks]
    metadatas = [c.metadata for c in chunks]

    embeddings = await asyncio.to_thread(_embed_all, texts)

    built_at = datetime.now(UTC).isoformat()
    await asyncio.to_thread(
        partial(col.upsert, ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    )
    await asyncio.to_thread(
        partial(
            col.modify,
            metadata={
                "corpus_hash": chash,
                "built_at": built_at,
                "model": embedding_model_id(),
                "techniques": len(docs),
            },
        )
    )

    elapsed = time.perf_counter() - t0
    log.info(
        "rag.index_built",
        documents=expected,
        techniques=len(docs),
        elapsed_s=round(elapsed, 1),
    )
    return {
        "documents": await asyncio.to_thread(col.count),
        "techniques": len(docs),
        "model": embedding_model_id(),
        "built_at": built_at,
        "corpus_hash": chash,
    }


def index_stats(collection: Any) -> dict[str, Any]:
    meta = dict(collection.metadata or {})
    return {
        "documents": collection.count(),
        "techniques": meta.get("techniques"),
        "model": meta.get("model"),
        "built_at": meta.get("built_at"),
        "corpus_hash": meta.get("corpus_hash"),
    }
