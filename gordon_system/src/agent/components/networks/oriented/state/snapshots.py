# Oriented Network State Snapshots - Phase 4.7.4
# ================================================

"""
Snapshot types for representing semantic states at different points in time.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

SNAPSHOT TYPES:
    - CurrentState: The present condition
    - HistoricalState: Past conditions for reference
    - CandidateState: Potential future conditions
    - SuspendedState: Paused conditions for resumption
    - RecoveredState: Restored conditions
    - ReferenceState: Canonical authoritative conditions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


@dataclass(frozen=True)
class CurrentState:
    """
    Represents the current semantic snapshot of a state.
    
    SEMANTIC ROLE:
        - Captures the present condition at a logical point in time
        - Never represents runtime execution
        
    COMPOSITION INVARIANTS:
        CSN-INV-001: Immutable representation
        CSN-INV-002: Logical timestamp only (no wall-clock)
        CSN-INV-003: Semantic snapshot, not runtime state
    """
    
    state_id: str
    """ID of the current state instance"""
    
    revision: int = 1
    """Revision at this point in time"""
    
    logical_timestamp: Optional[int] = None
    """Optional logical timestamp (not wall-clock time)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "logical_timestamp": self.logical_timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CurrentState:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            logical_timestamp=data.get("logical_timestamp"),
        )


@dataclass(frozen=True)
class HistoricalState:
    """
    Represents a historical semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures past conditions for reference and analysis
        - Never modifies history
        
    COMPOSITION INVARIANTS:
        HS-INV-001: Immutable representation
        HS-INV-002: Past condition only
        HS-INV-003: No runtime state associated
    """
    
    state_id: str
    """ID of the historical state"""
    
    revision: int = 1
    """Revision at that point in time"""
    
    logical_timestamp: Optional[int] = None
    """Optional logical timestamp when this state was recorded"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "logical_timestamp": self.logical_timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HistoricalState:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            logical_timestamp=data.get("logical_timestamp"),
        )


@dataclass(frozen=True)
class CandidateState:
    """
    Represents a candidate future semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures potential conditions under consideration
        - Never guarantees execution
        
    COMPOSITION INVARIANTS:
        CAND-INV-001: Immutable representation
        CAND-INV-002: Potential, not guaranteed
        CAND-INV-003: No runtime state associated
    """
    
    state_id: str
    """ID of the candidate state"""
    
    confidence: float = 0.0
    """Confidence level (0.0 to 1.0) in this state being realized"""
    
    revision: int = 1
    """Revision for this candidate"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "confidence": self.confidence,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CandidateState:
        return cls(
            state_id=data["state_id"],
            confidence=data.get("confidence", 0.0),
            revision=data.get("revision", 1),
        )


@dataclass(frozen=True)
class SuspendedState:
    """
    Represents a suspended (paused) semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures paused conditions for later resumption
        - Never executes while suspended
        
    COMPOSITION INVARIANTS:
        SS-INV-001: Immutable representation
        SS-INV-002: Paused state only
        SS-INV-003: No runtime execution while suspended
    """
    
    state_id: str
    """ID of the suspended state"""
    
    revision: int = 1
    """Revision when suspension occurred"""
    
    suspended_at_timestamp: Optional[int] = None
    """Logical timestamp when suspension occurred"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "suspended_at_timestamp": self.suspended_at_timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SuspendedState:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            suspended_at_timestamp=data.get("suspended_at_timestamp"),
        )


@dataclass(frozen=True)
class RecoveredState:
    """
    Represents a recovered semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures restored conditions
        - Never modifies recovery history
        
    COMPOSITION INVARIANTS:
        RS-INV-001: Immutable representation
        RS-INV-002: Restored condition only
        RS-INV-003: No runtime state during recovery
    """
    
    state_id: str
    """ID of the recovered state"""
    
    revision: int = 1
    """Revision at recovery time"""
    
    from_state_id: Optional[str] = None
    """ID of the state it was recovered from (if any)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "from_state_id": self.from_state_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RecoveredState:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            from_state_id=data.get("from_state_id"),
        )


@dataclass(frozen=True)
class ReferenceState:
    """
    Represents a reference (canonical) semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures authoritative conditions for comparison
        - Never executes or modifies
        
    COMPOSITION INVARIANTS:
        REF-INV-001: Immutable representation
        REF-INV-002: Canonical authority only
        REF-INV-003: No runtime state associated
    """
    
    state_id: str
    """ID of the reference state"""
    
    revision: int = 1
    """Revision for this reference"""
    
    canonical: bool = True
    """Whether this is the canonical reference"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "canonical": self.canonical,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ReferenceState:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            canonical=data.get("canonical", True),
        )


__all__ = [
    "CurrentState",
    "HistoricalState",
    "CandidateState",
    "SuspendedState",
    "RecoveredState",
    "ReferenceState",
]