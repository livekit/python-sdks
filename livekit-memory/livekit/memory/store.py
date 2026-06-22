# Copyright 2024 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""`MemoryStore` — one user's (or one room's) in-memory semantic memory.

Instantiate one store per user/session rather than threading scope kwargs through every
call. A store holds two collections:

* **facts** (`FACTS_NAMESPACE`) — "fixed" info about the user. Small, exact-scanned, and
  unconditionally available to `context()`. This is the user's pinned profile.
* **the semantic collection** — everything else, ANN-indexed and ranked by `search()`.

The hot path (`search`, `add`, `context`) is allocation-light and accepts a precomputed
`embedding=` to bypass the embedder entirely. A re-entrant lock guards mutations against
concurrent searches (both index backends do the heavy distance math with the GIL
released / concurrently, so contention is minimal).
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from typing import Any, Dict, List, Optional, Sequence, Union, cast

import numpy as np

from ._index import BruteForceIndex, VectorIndex, make_index
from ._types import (
    DEFAULT_NAMESPACE,
    FACTS_NAMESPACE,
    MemoryItem,
    as_float32_2d,
    l2_normalize,
)
from .embeddings import EmbedFn, Embedder, coerce_embedder

QueryLike = Union[str, Sequence[float], np.ndarray]
_SNAPSHOT_VERSION = 1


class MemoryStore:
    def __init__(
        self,
        *,
        embedder: Union[Embedder, EmbedFn, None] = None,
        dims: Optional[int] = None,
        backend: str = "auto",
        expected_size: Optional[int] = None,
    ) -> None:
        """Create a memory store.

        Args:
            embedder: an `Embedder`, a batched `list[str] -> vectors` callable, or
                `None` to use the dependency-free `HashingEmbedder`. For production use
                `Model2VecEmbedder` (sub-millisecond, fits the latency budget).
            dims: vector dimensionality. Required only when `embedder` is a plain
                callable; otherwise taken from the embedder.
            backend: "auto" (brute-force, upgrading to usearch past ~100k when
                `expected_size` says so and usearch is installed), "bruteforce", or
                "usearch".
            expected_size: hint for `auto` backend selection of the semantic collection.
        """
        self._embedder = coerce_embedder(embedder, dims)
        self._dims = self._embedder.dims
        self._backend_name = backend
        self._lock = threading.RLock()

        self._collection: VectorIndex = make_index(self._dims, backend, expected_size=expected_size)
        # Facts are always exact and fully scanned — keep them brute-force regardless.
        self._facts: VectorIndex = BruteForceIndex(self._dims)

        self._items: Dict[str, MemoryItem] = {}
        self._id_to_key: Dict[str, int] = {}
        self._key_to_id: Dict[int, str] = {}
        self._next_key = 1

    @property
    def dims(self) -> int:
        return self._dims

    @property
    def embedder(self) -> Embedder:
        return self._embedder

    def __len__(self) -> int:
        return len(self._items)

    # -- internal helpers -------------------------------------------------

    def _index_for(self, namespace: str) -> VectorIndex:
        return self._facts if namespace == FACTS_NAMESPACE else self._collection

    def _vector_for(self, text: str, embedding: Optional[Sequence[float]]) -> np.ndarray:
        if embedding is not None:
            vec = cast(np.ndarray, l2_normalize(as_float32_2d(embedding))[0])
            if vec.shape[0] != self._dims:
                raise ValueError(
                    f"provided embedding has {vec.shape[0]} dims, store expects {self._dims}"
                )
            return vec
        return self._embedder.embed_one(text)

    def _resolve_query_vector(self, query: QueryLike) -> np.ndarray:
        if isinstance(query, str):
            return self._embedder.embed_one(query)
        return cast(np.ndarray, l2_normalize(as_float32_2d(query))[0])

    # -- write ------------------------------------------------------------

    def add(
        self,
        text: str,
        *,
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[Sequence[float]] = None,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> str:
        """Add a memory to the semantic collection. Returns its id (auto-generated if omitted)."""
        item_id = id or uuid.uuid4().hex
        vec = self._vector_for(text, embedding)
        with self._lock:
            self._put(item_id, text, namespace, metadata or {}, vec)
        return item_id

    def upsert(
        self,
        key: str,
        text: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[Sequence[float]] = None,
        namespace: str = FACTS_NAMESPACE,
    ) -> None:
        """Insert or replace a keyed memory in place (default: the facts namespace)."""
        vec = self._vector_for(text, embedding)
        with self._lock:
            self._put(key, text, namespace, metadata or {}, vec)

    def _put(
        self,
        item_id: str,
        text: str,
        namespace: str,
        metadata: Dict[str, Any],
        vec: np.ndarray,
    ) -> None:
        existing = self._items.get(item_id)
        if existing is not None and existing.namespace != namespace:
            # Namespace changed for an existing id: drop it from the old index first.
            self._index_for(existing.namespace).remove(self._id_to_key[item_id])

        key = self._id_to_key.get(item_id)
        if key is None:
            key = self._next_key
            self._next_key += 1
            self._id_to_key[item_id] = key
            self._key_to_id[key] = item_id

        created_at = existing.created_at if existing is not None else None
        item = MemoryItem(id=item_id, text=text, namespace=namespace, metadata=metadata)
        if created_at is not None:
            item.created_at = created_at
        self._items[item_id] = item
        self._index_for(namespace).add(key, vec)

    # -- read -------------------------------------------------------------

    def search(
        self,
        query: QueryLike,
        *,
        limit: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        min_score: float = -1.0,
    ) -> List[MemoryItem]:
        """Rank memories by cosine similarity to `query` (text or precomputed vector).

        By default searches the semantic collection. Pass `namespace=FACTS_NAMESPACE` to
        rank facts instead, or another namespace to restrict to it. When a `namespace`
        filter or metadata `filter` is applied to an ANN backend, results are over-fetched
        then filtered, so very selective filters may return fewer than `limit`.
        """
        qvec = self._resolve_query_vector(query)
        filtering = filter is not None or (namespace is not None and namespace != FACTS_NAMESPACE)

        with self._lock:
            if namespace == FACTS_NAMESPACE:
                index = self._facts
            else:
                index = self._collection
            fetch = limit if not filtering else max(limit * 10, 100)
            raw = index.search(qvec, fetch)
            out: List[MemoryItem] = []
            for key, score in raw:
                if score < min_score:
                    continue
                item_id = self._key_to_id.get(key)
                if item_id is None:
                    continue
                stored = self._items.get(item_id)
                if stored is None:
                    continue
                if namespace is not None and stored.namespace != namespace:
                    continue
                if filter is not None and not _matches(stored.metadata, filter):
                    continue
                out.append(_with_score(stored, score))
                if len(out) >= limit:
                    break
            return out

    def context(
        self,
        query: QueryLike,
        *,
        limit: int = 5,
        include_facts: bool = True,
        max_facts: int = 32,
        header_facts: str = "Known facts about the user:",
        header_relevant: str = "Relevant memories:",
    ) -> str:
        """Build a prompt-ready context string: pinned facts + top-`limit` semantic hits.

        This is the latency-critical convenience the agent loop calls each turn. Facts are
        included verbatim (not ranked) since they're "fixed"; the semantic collection is
        ranked by relevance to `query`.
        """
        qvec = self._resolve_query_vector(query)
        lines: List[str] = []

        with self._lock:
            if include_facts and len(self._facts) > 0:
                facts = sorted(
                    (i for i in self._items.values() if i.namespace == FACTS_NAMESPACE),
                    key=lambda i: i.created_at,
                )[:max_facts]
                if facts:
                    lines.append(header_facts)
                    lines.extend(f"- {f.text}" for f in facts)

        hits = self.search(qvec, limit=limit)
        if hits:
            if lines:
                lines.append("")
            lines.append(header_relevant)
            lines.extend(f"- {h.text}" for h in hits)

        return "\n".join(lines)

    def get(self, id: str) -> Optional[MemoryItem]:
        with self._lock:
            item = self._items.get(id)
            return _copy(item) if item is not None else None

    def all(self, *, namespace: Optional[str] = None) -> List[MemoryItem]:
        with self._lock:
            return [
                _copy(i)
                for i in self._items.values()
                if namespace is None or i.namespace == namespace
            ]

    # -- delete -----------------------------------------------------------

    def delete(self, id: str) -> bool:
        with self._lock:
            item = self._items.pop(id, None)
            if item is None:
                return False
            key = self._id_to_key.pop(id)
            self._key_to_id.pop(key, None)
            self._index_for(item.namespace).remove(key)
            return True

    def clear(self, *, namespace: Optional[str] = None) -> None:
        with self._lock:
            if namespace is None:
                self._collection = make_index(self._dims, self._backend_name)
                self._facts = BruteForceIndex(self._dims)
                self._items.clear()
                self._id_to_key.clear()
                self._key_to_id.clear()
                self._next_key = 1
                return
            for item_id in [i for i, it in self._items.items() if it.namespace == namespace]:
                self.delete(item_id)

    # -- persistence (cold path) -----------------------------------------

    def save(self, path: Union[str, os.PathLike]) -> None:
        """Snapshot the store to a directory (items + both indices)."""
        path = os.fspath(path)
        os.makedirs(path, exist_ok=True)
        with self._lock:
            meta = {
                "version": _SNAPSHOT_VERSION,
                "dims": self._dims,
                "backend": self._backend_name,
                "next_key": self._next_key,
                "items": [
                    {**it.to_dict(), "_key": self._id_to_key[it.id]} for it in self._items.values()
                ],
            }
            with open(os.path.join(path, "meta.json"), "w") as f:
                json.dump(meta, f)
            self._collection.save(os.path.join(path, "collection"))
            self._facts.save(os.path.join(path, "facts"))

    @classmethod
    def load(
        cls,
        path: Union[str, os.PathLike],
        *,
        embedder: Union[Embedder, EmbedFn, None] = None,
        dims: Optional[int] = None,
    ) -> "MemoryStore":
        """Load a snapshot. The same `embedder` used at save time must be supplied."""
        path = os.fspath(path)
        with open(os.path.join(path, "meta.json")) as f:
            meta = json.load(f)
        if meta.get("version") != _SNAPSHOT_VERSION:
            raise ValueError(f"unsupported snapshot version {meta.get('version')!r}")

        store = cls(embedder=embedder, dims=dims or meta["dims"], backend=meta["backend"])
        if store._dims != meta["dims"]:
            raise ValueError(f"embedder dims {store._dims} != snapshot dims {meta['dims']}")
        store._collection.load(os.path.join(path, "collection"))
        store._facts.load(os.path.join(path, "facts"))
        store._next_key = meta["next_key"]
        for raw in meta["items"]:
            key = int(raw.pop("_key"))
            item = MemoryItem.from_dict(raw)
            store._items[item.id] = item
            store._id_to_key[item.id] = key
            store._key_to_id[key] = item.id
        return store


def _matches(metadata: Dict[str, Any], filter: Dict[str, Any]) -> bool:
    return all(metadata.get(k) == v for k, v in filter.items())


def _with_score(item: MemoryItem, score: float) -> MemoryItem:
    return MemoryItem(
        id=item.id,
        text=item.text,
        namespace=item.namespace,
        metadata=dict(item.metadata),
        created_at=item.created_at,
        score=score,
    )


def _copy(item: MemoryItem) -> MemoryItem:
    return (
        _with_score(item, item.score)
        if item.score is not None
        else MemoryItem(
            id=item.id,
            text=item.text,
            namespace=item.namespace,
            metadata=dict(item.metadata),
            created_at=item.created_at,
        )
    )


__all__ = ["MemoryStore", "QueryLike"]
