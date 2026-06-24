"""Semantic memory for an agent: pin fixed facts, store memories, retrieve fast.

Run with the recommended extras for the real static embedder + ANN index:

    uv run --with model2vec --with usearch python examples/memory.py

Without those extras it falls back to the dependency-free HashingEmbedder (lexical
only) and the exact brute-force index — still fully functional, just less semantic.
"""

from livekit.memory import MemoryStore

try:
    from livekit.memory import Model2VecEmbedder

    embedder = Model2VecEmbedder()  # static, ~0.03ms/query, no transformer forward pass
except ImportError:
    embedder = None  # -> HashingEmbedder default
    print("(model2vec not installed; using the dependency-free HashingEmbedder)\n")


def main() -> None:
    # One store per user/session. `expected_size` lets `auto` pick the HNSW backend.
    store = MemoryStore(embedder=embedder, backend="auto", expected_size=1_000_000)

    # "Fixed" facts about the user — pinned, always available to context().
    store.upsert("name", "The user's name is Ada Lovelace.")
    store.upsert("units", "The user prefers metric units and a 24-hour clock.")

    # Free-form semantic memories accumulated over the conversation.
    store.add("We talked about the analytical engine and Bernoulli numbers.")
    store.add("The user is planning a trip to Turin next spring.")
    store.add("The user dislikes phone calls and prefers async messages.")

    # The latency-critical call an agent makes each turn: one prompt-ready string.
    print("=== context() for 'what should I call them and any travel plans?' ===")
    print(store.context("what should I call them and any travel plans?", limit=3))

    print("\n=== search() ranked hits for 'communication preferences' ===")
    for hit in store.search("how does the user like to communicate?", limit=3):
        print(f"  {hit.score:+.3f}  {hit.text}")


if __name__ == "__main__":
    main()
