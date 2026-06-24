"""Tests for livekit.memory. Uses the dependency-free HashingEmbedder so these run
offline with no model downloads (pure-Python, like tests/api/*)."""

from __future__ import annotations

import json

import numpy as np
import pytest

from livekit.memory import (
    FACTS_NAMESPACE,
    BruteForceIndex,
    HashingEmbedder,
    MemoryStore,
    UsearchIndex,
)


def make_store(**kwargs) -> MemoryStore:
    return MemoryStore(embedder=HashingEmbedder(dims=64), **kwargs)


def test_add_and_get_roundtrip():
    store = make_store()
    mid = store.add("the sky is blue", metadata={"src": "obs"})
    assert len(store) == 1
    got = store.get(mid)
    assert got is not None
    assert got.text == "the sky is blue"
    assert got.metadata == {"src": "obs"}
    assert got.score is None  # score only on search results


def test_search_ranks_lexically_similar_first():
    store = make_store()
    store.add("the weather is sunny and warm today")
    store.add("quarterly revenue grew by twelve percent")
    hits = store.search("how is the weather today", limit=1)
    assert len(hits) == 1
    assert "weather" in hits[0].text
    assert hits[0].score is not None


def test_upsert_replaces_in_place():
    store = make_store()
    store.upsert("name", "the user is called Ada")
    store.upsert("name", "the user is called Grace")
    assert len(store) == 1
    facts = store.all(namespace=FACTS_NAMESPACE)
    assert len(facts) == 1
    assert "Grace" in facts[0].text


def test_facts_excluded_from_default_search_but_in_context():
    store = make_store()
    store.upsert("diet", "the user is vegetarian")
    store.add("the user asked about train times")
    # default search hits the semantic collection, not facts
    hits = store.search("vegetarian meals", limit=5)
    assert all(h.namespace != FACTS_NAMESPACE for h in hits)
    # but facts are searchable when explicitly requested
    fact_hits = store.search("vegetarian meals", limit=5, namespace=FACTS_NAMESPACE)
    assert len(fact_hits) == 1
    # and context always includes them
    ctx = store.context("what's for dinner")
    assert "vegetarian" in ctx
    assert "Known facts" in ctx


def test_metadata_filter():
    store = make_store()
    store.add("note one", metadata={"topic": "a"})
    store.add("note two", metadata={"topic": "b"})
    hits = store.search("note", limit=5, filter={"topic": "b"})
    assert len(hits) == 1
    assert hits[0].metadata["topic"] == "b"


def test_delete_and_clear():
    store = make_store()
    a = store.add("first")
    store.add("second")
    assert store.delete(a) is True
    assert store.delete(a) is False
    assert len(store) == 1
    store.clear()
    assert len(store) == 0
    assert store.search("first", limit=5) == []


def test_namespace_change_moves_between_indices():
    store = make_store()
    store.add("movable", id="x", namespace="default")
    store.upsert("x", "now a fact", namespace=FACTS_NAMESPACE)
    assert len(store) == 1
    assert store.all(namespace=FACTS_NAMESPACE)[0].id == "x"
    assert store.all(namespace="default") == []


def test_precomputed_embedding_bypasses_embedder():
    store = make_store()
    vec = np.ones(64, dtype=np.float32)
    store.add("ignored text", embedding=vec, id="v")
    hits = store.search(vec, limit=1)
    assert hits[0].id == "v"


def test_save_and_load(tmp_path):
    store = make_store()
    store.upsert("name", "user is Ada")
    store.add("likes hiking", metadata={"k": 1})
    store.save(tmp_path / "snap")

    loaded = MemoryStore.load(tmp_path / "snap", embedder=HashingEmbedder(dims=64))
    assert len(loaded) == 2
    assert loaded.all(namespace=FACTS_NAMESPACE)[0].text == "user is Ada"
    hits = loaded.search("hiking trips", limit=1)
    assert hits[0].metadata == {"k": 1}


def test_snapshot_records_resolved_backend_not_auto(tmp_path):
    # backend="auto" must persist the concrete backend it resolved to, never "auto",
    # so load() rebuilds the right index type.
    store = make_store(backend="auto")
    store.save(tmp_path / "snap")
    with open(tmp_path / "snap" / "meta.json") as f:
        meta = json.load(f)
    assert meta["backend"] in ("bruteforce", "usearch")
    assert meta["backend"] != "auto"


def test_usearch_auto_save_load_roundtrip(tmp_path):
    # Regression: backend="auto" + large expected_size selects UsearchIndex; the
    # snapshot must reload as UsearchIndex rather than crashing in BruteForceIndex.load.
    pytest.importorskip("usearch")
    emb = HashingEmbedder(dims=64)
    store = MemoryStore(embedder=emb, backend="auto", expected_size=200_000)
    assert isinstance(store._collection, UsearchIndex)

    store.upsert("name", "user is Ada")  # fact -> brute force
    for i in range(20):
        store.add(f"memory number {i} about topic {i % 5}")
    store.save(tmp_path / "snap")

    loaded = MemoryStore.load(tmp_path / "snap", embedder=HashingEmbedder(dims=64))
    assert isinstance(loaded._collection, UsearchIndex)
    assert len(loaded) == 21
    assert loaded.all(namespace=FACTS_NAMESPACE)[0].text == "user is Ada"
    hits = loaded.search("memory number 7 about topic 2", limit=1)
    assert hits and "number 7" in hits[0].text


def test_dimension_mismatch_rejected():
    store = make_store()  # dims=64
    with pytest.raises(ValueError):
        store.add("x", embedding=np.ones(10, dtype=np.float32))


def test_brute_force_index_remove_keeps_dense():
    idx = BruteForceIndex(dims=4)
    for k in range(5):
        v = np.zeros(4, dtype=np.float32)
        v[k % 4] = 1.0
        idx.add(k, v)
    assert len(idx) == 5
    assert idx.remove(2) is True
    assert len(idx) == 4
    # surviving keys still searchable
    res = idx.search(np.array([1, 0, 0, 0], dtype=np.float32), k=4)
    keys = {k for k, _ in res}
    assert 2 not in keys
