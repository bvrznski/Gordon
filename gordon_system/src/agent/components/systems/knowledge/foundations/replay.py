# Knowledge Replay - Phase 6.1
# ============================

"""
Knowledge Replay: Historical state reconstruction in Gordon's knowledge system.

Semantic replay reconstructs historical semantic states, preserving:
    
    * Identity
    * Revision lineage
    * Authority assignment
    * Scope definition  
    * Provenance trail
    * Grounding references
    
Replay never modifies history - it only observes and reconstructs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# REPLAY STATUS - Reconstruction outcome
# =============================================================================


class ReplayStatus(Enum):
    """
    Status of replay operation.
    
    Defines the result of a historical state reconstruction attempt:
        SUCCESS      -> Historical state fully reconstructed
        PARTIAL      -> Some information recovered, some missing
        FAILED       -> Reconstruction could not be completed
        INCOMPLETE   -> History exists but is fragmented
    """
    
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    INCOMPLETE = "incomplete"


# =============================================================================
# REPLAY RECORD - Historical state reconstruction
# =============================================================================


@dataclass(frozen=True)
class ReplayRecord:
    """
    Record of a historical state reconstruction.
    
    Captures what was reconstructed from history for analysis or replay.
    
    Fields:
        replay_identity:     Unique identifier for this replay record
        semantic_identity:   Identity of artifact being replayed
        replay_revision:     Revision number at time of replay
        replay_timestamp:    When the historical state existed
        reconstructed_state: What was recovered from history
        replay_status:       Result of the reconstruction attempt
        provenance:          Where the data came from
    """
    
    # Identity and metadata (required)
    replay_identity: str                  # Unique replay ID
    
    semantic_identity: str                # Artifact identity being replayed
    
    replay_revision: int = 1              # Revision number at that time
    replay_timestamp: float = field(default_factory=time.time)  # Historical timestamp
    
    reconstructed_state: Dict[str, Any] = field(default_factory=dict)  # Recovered state
    
    replay_status: ReplayStatus = ReplayStatus.SUCCESS
    
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Data sources
    
    @property
    def is_success(self) -> bool:
        """Check if replay was successful."""
        return self.replay_status == ReplayStatus.SUCCESS
    
    @property
    def has_full_state(self) -> bool:
        """Check if full state was reconstructed."""
        return len(self.reconstructed_state) > 0 and self.is_success
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "replay_identity": self.replay_identity,
            "semantic_identity": self.semantic_identity,
            "replay_revision": self.replay_revision,
            "replay_timestamp": self.replay_timestamp,
            "reconstructed_state": dict(self.reconstructed_state),
            "replay_status": self.replay_status.value,
            "provenance_count": len(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayRecord":
        """Create record from dictionary."""
        return cls(
            replay_identity=data.get("replay_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            replay_revision=int(data.get("replay_revision", 1)),
            replay_timestamp=float(data.get("replay_timestamp", time.time())),
            reconstructed_state=dict(data.get("reconstructed_state", {})),
            replay_status=ReplayStatus(data.get("replay_status", "success")),
            provenance=tuple(data.get("provenance", [])),
        )


# =============================================================================
# REPLAY ENGINE - Historical state reconstruction
# =============================================================================


class ReplayEngine:
    """
    Engine for reconstructing historical semantic states.
    
    Enables replay of past states for auditing, debugging, or recovery purposes.
    The engine preserves all history while allowing observation of previous states.
    """
    
    def __init__(
        self,
        preserve_history: bool = True,
        verify_consistency: bool = True,
    ):
        """
        Initialize the replay engine.
        
        Args:
            preserve_history: Whether to keep historical records
            verify_consistency: Whether to validate reconstructed state
        """
        self._preserve_history = preserve_history
        self._verify_consistency = verify_consistency
        
        # Internal history store (in real implementation, this would be persistent)
        self._history_store: Dict[str, List[Dict[str, Any]]] = {}
    
    def register_revision(
        self,
        semantic_identity: str,
        revision_data: Dict[str, Any],
    ) -> bool:
        """
        Register a new revision for replay.
        
        Args:
            semantic_identity: Artifact identity
            revision_data: Data from this revision
            
        Returns:
            True if registered successfully
        """
        if semantic_identity not in self._history_store:
            self._history_store[semantic_identity] = []
        
        self._history_store[semantic_identity].append({
            **revision_data,
            "timestamp": time.time(),
        })
        return True
    
    def replay_revision(
        self,
        semantic_identity: str,
        revision_number: int = 1,
    ) -> ReplayRecord:
        """
        Reconstruct a specific historical state.
        
        Args:
            semantic_identity: Artifact identity
            revision_number: Which revision to reconstruct (1-indexed)
            
        Returns:
            ReplayRecord with reconstructed state
        """
        revisions = self._history_store.get(semantic_identity, [])
        
        if not revisions:
            return ReplayRecord(
                replay_identity=f"replay:{uuid.uuid4().hex[:16]}",
                semantic_identity=semantic_identity,
                replay_revision=revision_number,
                replay_status=ReplayStatus.FAILED,
                reconstructed_state={},
                provenance=tuple(),
            )
        
        # Get the requested revision (1-indexed)
        index = revision_number - 1
        
        if index < 0 or index >= len(revisions):
            return ReplayRecord(
                replay_identity=f"replay:{uuid.uuid4().hex[:16]}",
                semantic_identity=semantic_identity,
                replay_revision=revision_number,
                replay_status=ReplayStatus.FAILED,
                reconstructed_state={},
                provenance=tuple(),
            )
        
        revision_data = revisions[index]
        
        return ReplayRecord(
            replay_identity=f"replay:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            replay_revision=revision_number,
            replay_timestamp=revision_data.get("timestamp", time.time()),
            reconstructed_state=dict(revision_data),
            replay_status=ReplayStatus.SUCCESS,
            provenance=tuple([{"source": "history_store", "index": index}]),
        )
    
    def replay_all(
        self,
        semantic_identity: str,
    ) -> List[ReplayRecord]:
        """
        Reconstruct all historical states for an artifact.
        
        Args:
            semantic_identity: Artifact identity
            
        Returns:
            List of ReplayRecords, one per revision
        """
        revisions = self._history_store.get(semantic_identity, [])
        results = []
        
        for i, rev_data in enumerate(revisions):
            record = ReplayRecord(
                replay_identity=f"replay:{uuid.uuid4().hex[:16]}",
                semantic_identity=semantic_identity,
                replay_revision=i + 1,
                replay_timestamp=rev_data.get("timestamp", time.time()),
                reconstructed_state=dict(rev_data),
                replay_status=ReplayStatus.SUCCESS,
                provenance=tuple([{"source": "history_store", "index": i}]),
            )
            results.append(record)
        
        return results
    
    def get_history_chain(
        self,
        semantic_identity: str,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Get the complete history chain for an artifact.
        
        Args:
            semantic_identity: Artifact identity
            
        Returns:
            Tuple of historical records in chronological order
        """
        return tuple(self._history_store.get(semantic_identity, []))
    
    def verify_reconstructed_state(
        self,
        record: ReplayRecord,
    ) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of a reconstructed state.
        
        Args:
            record: ReplayRecord to verify
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        state = record.reconstructed_state
        
        # Check required fields
        required_fields = ["semantic_identity", "semantic_revision"]
        for field_name in required_fields:
            if field_name not in state or not state[field_name]:
                issues.append(f"Missing required field: {field_name}")
        
        return len(issues) == 0, issues


# =============================================================================
# HISTORICAL RECORD - Immutable history entry
# =============================================================================


@dataclass(frozen=True)
class HistoricalRecord:
    """
    Immutable historical record of a state change.
    
    Designed to be stored permanently for complete auditability.
    
    Fields:
        record_identity:       Unique identifier for this record
        semantic_identity:     Artifact identity at time of change
        revision_number:       Revision number after the change
        timestamp_utc:         When the change occurred
        previous_revision:     What changed from (for diff)
        change_summary:        Brief description of what changed
        state_after_change:    Complete state after the change
        proof:                 Cryptographic or other integrity proof
    """
    
    # Identity and metadata (required)
    record_identity: str                  # Unique record ID
    
    semantic_identity: str                # Artifact identity at time of change
    
    revision_number: int = 1              # Revision after the change
    timestamp_utc: float = field(default_factory=time.time)  # When it happened
    
    previous_revision: Optional[int] = None  # What changed from
    change_summary: Optional[str] = None     # Brief description
    state_after_change: Dict[str, Any] = field(default_factory=dict)  # Full state
    
    proof: Optional[Dict[str, Any]] = None  # Integrity verification data
    
    @property
    def is_complete(self) -> bool:
        """Check if record has all essential information."""
        return (
            len(self.record_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.revision_number > 0 and
            self.timestamp_utc > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization."""
        return {
            "record_identity": self.record_identity,
            "semantic_identity": self.semantic_identity,
            "revision_number": self.revision_number,
            "timestamp_utc": self.timestamp_utc,
            "previous_revision": self.previous_revision,
            "change_summary": self.change_summary,
            "state_after_change": dict(self.state_after_change),
            "proof": dict(self.proof) if self.proof else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoricalRecord":
        """Create record from dictionary."""
        return cls(
            record_identity=data.get("record_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            revision_number=int(data.get("revision_number", 1)),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            previous_revision=data.get("previous_revision"),
            change_summary=data.get("change_summary"),
            state_after_change=dict(data.get("state_after_change", {})),
            proof=data.get("proof"),
        )


__all__ = [
    # Replay status
    "ReplayStatus",
    # Record types
    "ReplayRecord",
    "HistoricalRecord",
    # Engine
    "ReplayEngine",
]