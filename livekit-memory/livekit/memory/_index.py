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

"""Vector index backends.

Two implementations behind one tiny interface:

* `BruteForceIndex` — exact cosine via a single normalized matmul. Sub-millisecond to
  ~100k vectors (measured ~1.5ms at 100k, 384d), zero dependencies, exact recall, no
  build step. The right default for the common per-user case.
* `UsearchIndex` — HNSW graph (the `usearch` optional dep). Sub-millisecond search even
  at 1M vectors (~0.27ms measured), concurrent-by-design, incremental add/remove. The
  right backend once a single user's corpus crosses ~100k vectors.

Keys are integers (the store maps them to/from string item ids). Scores are cosine
similarity in [-1, 1]; higher is closer.
"""

from __future__ import annotations

import os
from typing import List, Optional, Protocol, Tuple, runtime_checkable

import numpy as np

# Above this many vectors, brute-force starts to threaten the latency budget; `auto`
# backend selection prefers the ANN index past this point (when usearch is installed).
ANN_CROSSOVER = 100_000


@runtime_checkable
class VectorIndex(Protocol):
    """Minimal index interface used by `MemoryStore`."""

    # Concrete backend tag ("bruteforce" | "usearch"); persisted in snapshots so a
    # store created with backend="auto" reloads the same index type it resolved to.
    kind: str

    @property
    def dims(self) -> int: ...

    def __len__(self) -> int: ...

    def add(self, key: int, vector: np.ndarray) -> None: ...

    def remove(self, key: int) -> bool: ...

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]: ...

    def save(self, path: str) -> None: ...

    def load(self, path: str) -> None: ...


class BruteForceIndex:
    """Exact cosine index over a contiguous, capacity-doubling float32 matrix.

    Vectors are stored already L2-normalized so search is one `matrix @ query` plus a
    partial top-k selection. Removal is O(1) swap-with-last to keep the matrix dense.
    """

    kind = "bruteforce"

    def __init__(self, dims: int, *, initial_capacity: int = 1024) -> None:
        self._dims = int(dims)
        self._count = 0
        self._mat = np.zeros((max(initial_capacity, 1), self._dims), dtype=np.float32)
        self._keys: List[int] = []
        self._key_to_row: dict[int, int] = {}

    @property
    def dims(self) -> int:
        return self._dims

    def __len__(self) -> int:
        return self._count

    def _ensure_capacity(self, n: int) -> None:
        cap = self._mat.shape[0]
        if n <= cap:
            return
        new_cap = cap
        while new_cap < n:
            new_cap *= 2
        grown = np.zeros((new_cap, self._dims), dtype=np.float32)
        grown[: self._count] = self._mat[: self._count]
        self._mat = grown

    def add(self, key: int, vector: np.ndarray) -> None:
        if key in self._key_to_row:
            # Upsert semantics: overwrite the existing row in place.
            self._mat[self._key_to_row[key]] = vector
            return
        self._ensure_capacity(self._count + 1)
        row = self._count
        self._mat[row] = vector
        self._keys.append(key)
        self._key_to_row[key] = row
        self._count += 1

    def remove(self, key: int) -> bool:
        row = self._key_to_row.pop(key, None)
        if row is None:
            return False
        last = self._count - 1
        if row != last:
            # Move the last row into the freed slot to stay dense.
            self._mat[row] = self._mat[last]
            moved_key = self._keys[last]
            self._keys[row] = moved_key
            self._key_to_row[moved_key] = row
        self._keys.pop()
        self._count -= 1
        return True

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        if self._count == 0 or k <= 0:
            return []
        q = np.ascontiguousarray(query, dtype=np.float32).reshape(-1)
        scores = self._mat[: self._count] @ q  # cosine, since rows + query are normalized
        k = min(k, self._count)
        # argpartition for the top-k, then sort just those k descending.
        idx = np.argpartition(scores, -k)[-k:]
        idx = idx[np.argsort(scores[idx])[::-1]]
        return [(self._keys[i], float(scores[i])) for i in idx]

    def save(self, path: str) -> None:
        np.savez(
            path,
            mat=self._mat[: self._count],
            keys=np.asarray(self._keys, dtype=np.int64),
            dims=np.asarray([self._dims], dtype=np.int64),
        )

    def load(self, path: str) -> None:
        # numpy appends .npz when saving a bare path; tolerate either form.
        load_path = path if os.path.exists(path) else path + ".npz"
        with np.load(load_path) as data:
            mat = np.ascontiguousarray(data["mat"], dtype=np.float32)
            keys = [int(x) for x in data["keys"].tolist()]
            self._dims = int(data["dims"][0])
        self._count = mat.shape[0]
        self._mat = mat if mat.shape[0] > 0 else np.zeros((1, self._dims), dtype=np.float32)
        self._keys = keys
        self._key_to_row = {key: row for row, key in enumerate(keys)}


class UsearchIndex:
    """HNSW index backed by the optional `usearch` dependency.

    Use for large per-user corpora (≳100k vectors). Cosine metric; scores are returned
    as similarity (1 - distance) to match `BruteForceIndex`.
    """

    kind = "usearch"

    def __init__(
        self,
        dims: int,
        *,
        connectivity: int = 16,
        expansion_add: int = 128,
        expansion_search: int = 96,
    ) -> None:
        try:
            from usearch.index import Index
        except ImportError as e:  # pragma: no cover - depends on optional extra
            raise ImportError(
                "UsearchIndex requires the 'usearch' package. "
                "Install with: pip install 'livekit-memory[ann]'"
            ) from e

        self._dims = int(dims)
        self._index = Index(
            ndim=self._dims,
            metric="cos",
            dtype="f32",
            connectivity=connectivity,
            expansion_add=expansion_add,
            expansion_search=expansion_search,
        )

    @property
    def dims(self) -> int:
        return self._dims

    def __len__(self) -> int:
        return int(len(self._index))

    def add(self, key: int, vector: np.ndarray) -> None:
        # usearch upserts when a key already exists.
        self._index.add(key, np.ascontiguousarray(vector, dtype=np.float32))

    def remove(self, key: int) -> bool:
        try:
            self._index.remove(key)
            return True
        except Exception:
            return False

    def search(self, query: np.ndarray, k: int) -> List[Tuple[int, float]]:
        if len(self._index) == 0 or k <= 0:
            return []
        q = np.ascontiguousarray(query, dtype=np.float32).reshape(-1)
        matches = self._index.search(q, min(k, len(self._index)))
        # cosine distance -> similarity
        return [(int(key), 1.0 - float(dist)) for key, dist in zip(matches.keys, matches.distances)]

    def save(self, path: str) -> None:
        self._index.save(path)

    def load(self, path: str) -> None:
        self._index.load(path)


def make_index(dims: int, backend: str, *, expected_size: Optional[int] = None) -> VectorIndex:
    """Construct an index for `backend` in {"auto", "bruteforce", "usearch"}."""
    if backend == "bruteforce":
        return BruteForceIndex(dims)
    if backend == "usearch":
        return UsearchIndex(dims)
    if backend == "auto":
        large = expected_size is not None and expected_size > ANN_CROSSOVER
        if large:
            try:
                return UsearchIndex(dims)
            except ImportError:
                pass  # fall back to exact brute force if usearch isn't installed
        return BruteForceIndex(dims)
    raise ValueError(f"unknown backend {backend!r}; expected auto|bruteforce|usearch")


__all__ = [
    "VectorIndex",
    "BruteForceIndex",
    "UsearchIndex",
    "make_index",
    "ANN_CROSSOVER",
]
