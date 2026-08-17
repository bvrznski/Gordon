# Gordon Phase 5.7.5-I: Presence Engine - Foundation Tests
# ===============================================================================
"""
Test suite for the canonical Presence Engine foundation components.
"""

import time
import pytest

from gordon_system.src.agent.capabilities.consciousness.presence import (
    PRESENCE_STATE_ACTIVE,
    PRESENCE_STATE_CANDIDATE,
    PRESENCE_STATE_WITHDRAWN,
    PRESENCE_STATE_ADMITTED,
    PRESENCE_STATE_WEAKENING,
    PRESENCE_STATE_FADING,
    PresenceItem,
    PresenceStateSnapshot,
    PresenceEngine,
)


class TestPresenceStates:
    """Test presence state constants and lifecycle."""
    
    def test_state_constants(self):
        """Verify all state constants are defined correctly."""
        assert PRESENCE_STATE_CANDIDATE == "candidate"
        assert PRESENCE_STATE_ADMITTED == "admitted"
        assert PRESENCE_STATE_ACTIVE == "active"
        assert PRESENCE_STATE_WEAKENING == "weakening"
        assert PRESENCE_STATE_FADING == "fading"
    
    def test_presence_item_initial_state(self):
        """Test that a new PresenceItem starts in candidate state."""
        item = PresenceItem.create_candidate(
            item_id="test-1",
            source_id="source-1",
        )
        
        assert item.state == PRESENCE_STATE_CANDIDATE
        assert item.item_id == "test-1"
        assert item.source_id == "source-1"
    
    def test_presence_item_admission(self):
        """Test candidate to admitted transition."""
        now = time.time()
        item = PresenceItem.create_candidate(
            item_id="test-2",
            source_id="source-1",
        )
        
        admitted_item = item.to_admitted(now_utc=now)
        
        assert admitted_item.state == PRESENCE_STATE_ADMITTED
        assert admitted_item.admitted_at_utc == now
    
    def test_presence_item_active(self):
        """Test admitted to active transition."""
        now = time.time()
        item = PresenceItem.create_candidate(
            item_id="test-3",
            source_id="source-1",
        )
        admitted = item.to_admitted(now_utc=now)
        
        active_item = admitted.to_active(now_utc=now + 1.0)
        
        assert active_item.state == PRESENCE_STATE_ACTIVE
        assert active_item.active_from_utc == now + 1.0
    
    def test_presence_item_fade(self):
        """Test fading transition."""
        now = time.time()
        item = PresenceItem.create_candidate(
            item_id="test-4",
            source_id="source-1",
        )
        
        # Direct to active first
        admitted = item.to_admitted(now_utc=now)
        active = admitted.to_active(now_utc=now + 1.0)
        
        # Now fade
        weakening = active.to_weakening(now_utc=now + 2.0)
        assert weakening.state == PRESENCE_STATE_WEAKENING
        
        fading = weakening.to_fading(now_utc=now + 3.0)
        assert fading.state == PRESENCE_STATE_FADING
    
    def test_presence_item_withdrawn(self):
        """Test withdrawal from active."""
        now = time.time()
        item = PresenceItem.create_candidate(
            item_id="test-5",
            source_id="source-1",
        )
        
        admitted = item.to_admitted(now_utc=now)
        active = admitted.to_active(now_utc=now + 1.0)
        withdrawn = active.to_withdrawn(now_utc=now + 2.0)
        
        assert withdrawn.state == PRESENCE_STATE_WITHDRAWN
        assert withdrawn.withdrawn_at_utc == now + 2.0
    
    def test_presence_item_is_active(self):
        """Test is_active method."""
        now = time.time()
        item = PresenceItem.create_candidate(
            item_id="test-6",
            source_id="source-1",
        )
        
        assert not item.is_active()
        
        admitted = item.to_admitted(now_utc=now)
        assert not admitted.is_active()
        
        active = admitted.to_active(now_utc=now + 1.0)
        assert active.is_active()


class TestPresenceStateSnapshot:
    """Test presence state snapshots."""
    
    def test_initial_snapshot(self):
        """Test initial snapshot creation."""
        now = time.time()
        snapshot = PresenceStateSnapshot.initial(snapshot_id="snap-1")
        
        assert snapshot.snapshot_id == "snap-1"
        assert snapshot.generation == 0
        assert snapshot.created_at_utc >= now - 1.0
    
    def test_snapshot_empty_counts(self):
        """Test initial snapshot has zero counts."""
        snapshot = PresenceStateSnapshot.initial()
        
        assert snapshot.candidate_count == 0
        assert snapshot.admitted_count == 0
        assert snapshot.active_count == 0
        assert snapshot.total_present == 0
        assert snapshot.total_active == 0
    
    def test_snapshot_with_items(self):
        """Test snapshot with items."""
        now = time.time()
        
        item1 = PresenceItem.create_candidate(
            item_id="item-1",
            source_id="source-1",
        )
        item2 = PresenceItem.create_candidate(
            item_id="item-2",
            source_id="source-2",
        )
        
        admitted1 = item1.to_admitted(now_utc=now)
        
        snapshot = PresenceStateSnapshot.initial().with_active_items(admitted1, item2)
        
        assert snapshot.active_count == 2
        assert snapshot.total_present == 2


class TestPresenceEngine:
    """Test the canonical presence engine."""
    
    def test_engine_creation(self):
        """Test engine initialization."""
        engine = PresenceEngine()
        
        assert engine.current_generation == 0
    
    def test_propose_candidate(self):
        """Test candidate proposal."""
        engine = PresenceEngine()
        
        success, reason = engine.propose_candidate(
            item_id="item-1",
            source_id="source-1",
        )
        
        assert success is True
        assert reason is None
    
    def test_get_snapshot(self):
        """Test snapshot retrieval."""
        engine = PresenceEngine()
        
        # Propose a candidate
        engine.propose_candidate(item_id="item-1", source_id="source-1")
        
        snapshot = engine.get_snapshot()
        
        assert snapshot.generation == 0
        assert len(snapshot.active_items) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])