# LiveKit Memory

In-process, in-memory **semantic memory** for LiveKit agents — sub-10ms end-to-end
retrieval (embed the query *and* search) of a user's fixed context, fully self-hosted.

```shell
pip install livekit-memory[recommended]   # static embedder + ANN index
```

## Why it's fast

The hard constraint for a voice agent loop is the *end-to-end* budget: you hand it text,
it must embed and search in under 10ms. A transformer embedding on CPU alone is ~10ms
(p99 ~50ms) and blows that. The route here:

- **Static embeddings (Model2Vec)** — token-lookup + mean-pool, no transformer forward
  pass. ~0.03ms per short query on CPU.
- **In-memory index** — exact brute-force cosine (sub-ms to ~100k vectors), automatically
  upgrading to a [usearch](https://github.com/unum-cloud/usearch) HNSW graph for large
  per-user corpora (~0.27ms search at 1M vectors).

Measured on an Apple M4 Pro: **0.17ms median / 0.31ms p99 end-to-end at 1M vectors** —
~30× under budget.

## Usage

```python
from livekit.memory import MemoryStore, Model2VecEmbedder

# one store per user / session
store = MemoryStore(embedder=Model2VecEmbedder(), backend="auto", expected_size=1_000_000)

# "fixed" facts about the user — pinned, always available
store.upsert("name", "The user's name is Ada Lovelace.")
store.upsert("units", "Prefers metric units.")

# free-form semantic memories — ranked by relevance
store.add("Discussed the analytical engine and Bernoulli numbers.", metadata={"session": 42})

# the latency-critical call your agent makes each turn:
context = store.context("what should I call them, and what did we talk about?")
# -> a prompt-ready string with the pinned facts + top relevant memories

# or rank directly:
for hit in store.search("mathematics history", limit=5):
    print(hit.score, hit.text)
```

### Bring your own embedder

`embedder` accepts an `Embedder`, any batched `list[str] -> vectors` callable (pass
`dims=`), or `None` for the dependency-free `HashingEmbedder` (deterministic, no model
download — good for tests/offline). For higher recall at the cost of latency, an ONNX
transformer embedder can be wrapped via `CallableEmbedder`.

### Persistence

`store.save(dir)` / `MemoryStore.load(dir, embedder=...)` snapshot items and both indices
to disk (the same embedder must be supplied on load).

## Backends

| Backend | When | Latency (384d) |
|---|---|---|
| `bruteforce` (default) | ≲100k vectors / user | exact, ~1.5ms @ 100k |
| `usearch` | ≳100k vectors / user | HNSW, ~0.27ms @ 1M |
| `auto` | picks per `expected_size` | — |

`usearch` is an optional dependency (`pip install livekit-memory[ann]`); without it,
`auto` stays on exact brute force.

See https://docs.livekit.io for more information.
