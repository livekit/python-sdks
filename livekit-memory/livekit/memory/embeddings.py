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

"""Embedders.

The hot-path constraint (sub-10ms end-to-end including the query embed) rules out a
transformer forward pass on CPU (~10ms median, ~50ms p99). The recommended default is
a *static* embedder (Model2Vec): token-lookup + mean-pool, no forward pass, measured
~0.03ms per short query. A dependency-free `HashingEmbedder` is provided so the package
is usable and testable offline; any callable `list[str] -> array` can also be supplied.
"""

from __future__ import annotations

import hashlib
from typing import Callable, List, Optional, Sequence, Union, cast

import numpy as np

from ._types import as_float32_2d, l2_normalize

# A user-supplied embedder may be either an `Embedder` instance or a plain batched
# callable that maps a list of strings to a 2-D array-like of vectors.
EmbedFn = Callable[[List[str]], Union[np.ndarray, Sequence[Sequence[float]]]]


class Embedder:
    """Base class for embedders.

    Implementations must set `self._dims` and implement `_embed`. Output is always
    L2-normalized here so downstream inner-product == cosine similarity.
    """

    _dims: int

    @property
    def dims(self) -> int:
        return self._dims

    def _embed(self, texts: List[str]) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """Embed a batch of texts into a normalized (len(texts), dims) float32 array."""
        if isinstance(texts, str):
            raise TypeError("embed() expects a sequence of strings, not a single str")
        out = as_float32_2d(self._embed(list(texts)))
        if out.shape[1] != self._dims:
            raise ValueError(f"embedder produced {out.shape[1]} dims, expected {self._dims}")
        return l2_normalize(out)

    def embed_one(self, text: str) -> np.ndarray:
        """Embed a single string into a normalized (dims,) float32 vector."""
        return cast(np.ndarray, self.embed([text])[0])


class CallableEmbedder(Embedder):
    """Wraps a user-supplied batched callable as an `Embedder`."""

    def __init__(self, fn: EmbedFn, dims: int) -> None:
        self._fn = fn
        self._dims = int(dims)

    def _embed(self, texts: List[str]) -> np.ndarray:
        return as_float32_2d(self._fn(texts))


class Model2VecEmbedder(Embedder):
    """Static (no-transformer) embedder backed by Model2Vec.

    Default model `minishlab/potion-base-8M` is 256-dim and embeds a short query in
    ~0.03ms on CPU — the route that makes a sub-10ms end-to-end budget comfortable.
    Requires the optional `model2vec` dependency: `pip install livekit-memory[model2vec]`.
    """

    def __init__(self, model: str = "minishlab/potion-base-8M") -> None:
        try:
            from model2vec import StaticModel
        except ImportError as e:  # pragma: no cover - depends on optional extra
            raise ImportError(
                "Model2VecEmbedder requires the 'model2vec' package. "
                "Install with: pip install 'livekit-memory[model2vec]'"
            ) from e

        self._model = StaticModel.from_pretrained(model)
        # Probe dimensionality from a trivial encode (cheap for static models).
        probe = np.asarray(self._model.encode(["x"]), dtype=np.float32)
        self._dims = int(probe.reshape(1, -1).shape[1])

    def _embed(self, texts: List[str]) -> np.ndarray:
        return as_float32_2d(self._model.encode(texts))


class HashingEmbedder(Embedder):
    """Dependency-free deterministic embedder (feature hashing over word tokens).

    Not semantically strong — it captures lexical overlap, not meaning — but it needs
    no model download and is fully deterministic, which makes it ideal for tests,
    offline development, and CI. Swap in `Model2VecEmbedder` for real semantics.
    """

    def __init__(self, dims: int = 256) -> None:
        if dims <= 0:
            raise ValueError("dims must be positive")
        self._dims = int(dims)

    def _token_index_sign(self, token: str) -> tuple[int, float]:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        h = int.from_bytes(digest, "little")
        idx = h % self._dims
        sign = 1.0 if (h >> 1) & 1 else -1.0
        return idx, sign

    def _embed(self, texts: List[str]) -> np.ndarray:
        out = np.zeros((len(texts), self._dims), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                idx, sign = self._token_index_sign(token)
                out[row, idx] += sign
        return out


def coerce_embedder(embedder: Union[Embedder, EmbedFn, None], dims: Optional[int]) -> Embedder:
    """Normalize the `embedder` argument accepted by `MemoryStore` into an `Embedder`."""
    if embedder is None:
        return HashingEmbedder(dims=dims or 256)
    if isinstance(embedder, Embedder):
        return embedder
    if callable(embedder):
        if dims is None:
            raise ValueError("dims must be provided when passing a plain embedder callable")
        return CallableEmbedder(embedder, dims)
    raise TypeError(f"unsupported embedder type: {type(embedder)!r}")


__all__ = [
    "Embedder",
    "CallableEmbedder",
    "Model2VecEmbedder",
    "HashingEmbedder",
    "EmbedFn",
    "coerce_embedder",
]
