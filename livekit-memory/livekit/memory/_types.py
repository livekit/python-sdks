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

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence, Union, cast

import numpy as np

# Anything that can be coerced into a 2-D float32 matrix: a single vector, a list of
# vectors, or an ndarray.
VectorsLike = Union[Sequence[float], Sequence[Sequence[float]], np.ndarray]

# Default namespace for free-form semantic memories (the searchable collection).
DEFAULT_NAMESPACE = "default"
# Namespace for "fixed" facts about the user/agent. These are always exact-scanned
# and can be unconditionally prepended to retrieval context (cf. Letta's `human`
# block / LangMem profiles), so they live separately from the ANN collection.
FACTS_NAMESPACE = "facts"


@dataclass
class MemoryItem:
    """A single stored memory.

    `score` is populated only on items returned from `search`/`context`; it is the
    cosine similarity to the query (range -1..1, higher is closer) and is `None` for
    stored or listed items.
    """

    id: str
    text: str
    namespace: str = DEFAULT_NAMESPACE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "namespace": self.namespace,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MemoryItem":
        return cls(
            id=d["id"],
            text=d["text"],
            namespace=d.get("namespace", DEFAULT_NAMESPACE),
            metadata=d.get("metadata", {}),
            created_at=d.get("created_at", 0.0),
        )


def as_float32_2d(vectors: VectorsLike) -> np.ndarray:
    """Coerce input to a contiguous (n, dims) float32 array."""
    arr = np.asarray(vectors, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2:
        raise ValueError(f"expected 1-D or 2-D vectors, got shape {arr.shape}")
    return np.ascontiguousarray(arr, dtype=np.float32)


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """Row-normalize so that inner product equals cosine similarity.

    Zero vectors are left as-is (they would otherwise divide by zero); they simply
    score 0 against every query.
    """
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    np.maximum(norms, 1e-12, out=norms)
    return cast(np.ndarray, vectors / norms)


__all__ = [
    "DEFAULT_NAMESPACE",
    "FACTS_NAMESPACE",
    "MemoryItem",
    "VectorsLike",
    "as_float32_2d",
    "l2_normalize",
]
