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

"""LiveKit Memory — in-process semantic memory for agents.

`pip install livekit-memory[recommended]`

Sub-10ms end-to-end (embed query + ANN search) retrieval of a user's fixed context,
fully self-hosted. The default route is a static Model2Vec embedder (no transformer
forward pass) plus an in-memory index (exact brute-force, upgrading to a usearch HNSW
graph for large per-user corpora).

    from livekit.memory import MemoryStore, Model2VecEmbedder

    store = MemoryStore(embedder=Model2VecEmbedder())
    store.upsert("name", "The user's name is Ada.")          # a fixed fact
    store.add("They prefer metric units and dark mode.")      # semantic memory
    ctx = store.context("what should I call them?")           # prompt-ready string
"""

from ._index import ANN_CROSSOVER, BruteForceIndex, UsearchIndex, VectorIndex
from ._types import DEFAULT_NAMESPACE, FACTS_NAMESPACE, MemoryItem
from .embeddings import (
    CallableEmbedder,
    Embedder,
    EmbedFn,
    HashingEmbedder,
    Model2VecEmbedder,
)
from .store import MemoryStore, QueryLike
from .version import __version__

__all__ = [
    "MemoryStore",
    "MemoryItem",
    "QueryLike",
    "Embedder",
    "Model2VecEmbedder",
    "HashingEmbedder",
    "CallableEmbedder",
    "EmbedFn",
    "VectorIndex",
    "BruteForceIndex",
    "UsearchIndex",
    "ANN_CROSSOVER",
    "DEFAULT_NAMESPACE",
    "FACTS_NAMESPACE",
    "__version__",
]
