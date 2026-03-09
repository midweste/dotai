"""Tests for DecayEngine."""

import pytest

from src.models import Memory
from src.decay import DecayEngine


class TestDecayEngine:
    def test_decay_reduces_importance(self, db, memory_store, decay_engine):
        """Decay should reduce importance of un-accessed memories."""
        m1 = memory_store.create(Memory(
            summary="Forgotten", type="context", importance=1.0,
        ))
        decayed_count = decay_engine.apply()
        assert decayed_count == 1
        fetched = memory_store.get(m1.id)
        assert fetched.importance == pytest.approx(0.95, abs=0.001)

    def test_decay_exempts_accessed(self, db, memory_store, decay_engine):
        """Accessed memories should not decay."""
        m1 = memory_store.create(Memory(
            summary="Accessed", type="context", importance=1.0,
        ))
        decayed = decay_engine.apply(accessed_ids={m1.id})
        assert decayed == 0
        fetched = memory_store.get(m1.id)
        assert fetched.importance == 1.0

    def test_decay_exempts_reinforced(self, db, memory_store, decay_engine):
        """Reinforced memories should not decay."""
        m1 = memory_store.create(Memory(
            summary="Reinforced", type="context", importance=1.0,
        ))
        decayed = decay_engine.apply(reinforced_ids={m1.id})
        assert decayed == 0

    def test_decay_multiple_cycles(self, db, memory_store, decay_engine):
        """Multiple decay cycles should compound."""
        m1 = memory_store.create(Memory(
            summary="Aging", type="context", importance=1.0,
        ))
        decay_engine.apply()
        decay_engine.apply()
        decay_engine.apply()
        fetched = memory_store.get(m1.id)
        expected = 1.0 * 0.95 * 0.95 * 0.95
        assert fetched.importance == pytest.approx(expected, abs=0.001)
