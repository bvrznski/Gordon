# Gordon Phase 5.7.4-I: Temporal Context Engine - Types
# ===============================================================================
"""
Type definitions for the Temporal Context Engine.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# TEMPORAL CONTEXT TYPE ENUMERATION
# =============================================================================

class TemporalContextType:
    """
    Enumeration of temporal context element types.
    
    This is a class-based enum pattern for type safety without requiring
    Python's Enum metaclass overhead.
    """
    RETENTION = "retention"
    PRESENTATION = "presentation"
    PROTENTION = "protention"
    CONTINUITY_WINDOW = "continuity_window"
    SNAPSHOT = "snapshot"
    TRANSITION = "transition"


# =============================================================================
# ID TYPE DEFINITIONS - SEEDABLE FOR DETERMINISTIC BEHAVIOR
# =============================================================================

def _make_id(prefix: str, id_counter: int = 0) -> str:
    """
    Create a deterministic ID with prefix.
    
    Args:
        prefix: ID prefix (e.g., 'ret', 'pres', 'prot')
        id_counter: Counter for deterministic generation
        
    Returns:
        Formatted ID string
    """
    # Use counter + hash to ensure determinism while still having uniqueness
    import hashlib
    seed_str = f"{prefix}-{id_counter}"
    hash_val = hashlib.md5(seed_str.encode()).hexdigest()[:6]
    return f"{prefix}-{hash_val}"


@dataclass(frozen=True)
class RetentionId:
    """
    Unique identifier for a retention record.
    
    Retention IDs track references to previous-generation contexts that remain
    available in the current continuity window.
    
    For determinism, use from_string() or create with explicit value.
    """
    value: str = ""
    """Unique string identifier."""
    
    @classmethod
    def initial(cls) -> "RetentionId":
        """Create an initial (deterministic) RetentionId."""
        return cls(value=_make_id("ret", 0))
    
    @classmethod
    def from_string(cls, value: str) -> "RetentionId":
        """Create a RetentionId from an existing string."""
        return cls(value=value)


@dataclass(frozen=True)
class PresentationId:
    """
    Unique identifier for a presentation reference.
    
    Presentation IDs identify the current Experiential Field snapshot being
    referenced in the temporal context.
    
    For determinism, use from_string() or create with explicit value.
    """
    value: str = ""
    """Unique string identifier."""
    
    @classmethod
    def initial(cls) -> "PresentationId":
        """Create an initial (deterministic) PresentationId."""
        return cls(value=_make_id("pres", 0))
    
    @classmethod
    def from_string(cls, value: str) -> "PresentationId":
        """Create a PresentationId from an existing string."""
        return cls(value=value)


@dataclass(frozen=True)
class ProtentionId:
    """
    Unique identifier for a protentional expectation.
    
    Protention IDs track individual expectations about the immediate future.
    
    For determinism, use from_string() or create with explicit value.
    """
    value: str = ""
    """Unique string identifier."""
    
    @classmethod
    def initial(cls) -> "ProtentionId":
        """Create an initial (deterministic) ProtentionId."""
        return cls(value=_make_id("prot", 0))
    
    @classmethod
    def from_string(cls, value: str) -> "ProtentionId":
        """Create a ProtentionId from an existing string."""
        return cls(value=value)


@dataclass(frozen=True)
class ContinuityWindowId:
    """
    Unique identifier for a continuity window.
    
    Continuity windows bound the temporal scope of a conscious context,
    defining its history, present, and immediate future.
    
    For determinism, use from_string() or create with explicit value.
    """
    value: str = ""
    """Unique string identifier."""
    
    @classmethod
    def initial(cls) -> "ContinuityWindowId":
        """Create an initial (deterministic) ContinuityWindowId."""
        return cls(value=_make_id("cw", 0))
    
    @classmethod
    def from_string(cls, value: str) -> "ContinuityWindowId":
        """Create a ContinuityWindowId from an existing string."""
        return cls(value=value)


@dataclass(frozen=True)
class TemporalSnapshotId:
    """
    Unique identifier for a temporal snapshot.
    
    Temporal snapshots are immutable publications of the complete temporal
    state at a point in time.
    
    For determinism, use from_string() or create with explicit value.
    """
    value: str = ""
    """Unique string identifier."""
    
    @classmethod
    def initial(cls) -> "TemporalSnapshotId":
        """Create an initial (deterministic) TemporalSnapshotId."""
        return cls(value=_make_id("ts", 0))
    
    @classmethod
    def from_string(cls, value: str) -> "TemporalSnapshotId":
        """Create a TemporalSnapshotId from an existing string."""
        return cls(value=value)


@dataclass(frozen=True)
class GenerationNumber:
    """
    Strictly monotonic generation number.
    
    Each transition increments the generation number by exactly 1.
    """
    value: int = 0
    """Generation count (non-negative)."""
    
    def next(self) -> "GenerationNumber":
        """Return the next generation number."""
        return GenerationNumber(value=self.value + 1)
    
    @classmethod
    def initial(cls) -> "GenerationNumber":
        """Return an initial generation number (0)."""
        return cls(value=0)


@dataclass(frozen=True)
class TrustLevel:
    """
    Bounded trust level for temporal elements.
    
    Trust levels represent confidence in the validity of retention references,
    protention expectations, or other temporal elements.
    """
    value: float = 1.0
    """Trust score between 0.0 (untrusted) and 1.0 (fully trusted)."""
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Trust level must be between 0.0 and 1.0")
    
    @classmethod
    def high(cls) -> "TrustLevel":
        """High trust (>= 0.8)."""
        return cls(value=0.9)
    
    @classmethod
    def medium(cls) -> "TrustLevel":
        """Medium trust (>= 0.5, < 0.8)."""
        return cls(value=0.65)
    
    @classmethod
    def low(cls) -> "TrustLevel":
        """Low trust (< 0.5)."""
        return cls(value=0.3)


@dataclass(frozen=True)
class PrivacyClassification:
    """
    Privacy classification for temporal elements.
    
    Classification determines which external systems may access temporal data.
    """
    value: str = "internal"
    """Privacy level (e.g., 'internal', 'restricted', 'confidential')."""
    
    @classmethod
    def internal(cls) -> "PrivacyClassification":
        """Internal only classification."""
        return cls(value="internal")
    
    @classmethod
    def restricted(cls) -> "PrivacyClassification":
        """Restricted access classification."""
        return cls(value="restricted")


# =============================================================================
# BOUNDED TYPES (immutable collections)
# =============================================================================

@dataclass(frozen=True)
class RetentionHistory:
    """
    Immutable bounded history of retention references.
    
    This represents the collection of previous-generation context references
    that remain immediately available for continuity preservation.
    """
    references: Tuple[str, ...] = field(default_factory=tuple)
    """Tuple of references to previous generations."""
    
    max_size: int = 10
    
    def __post_init__(self):
        if len(self.references) > self.max_size:
            # Keep only the most recent entries
            object.__setattr__(
                self, 
                "references", 
                self.references[-self.max_size:]
            )
    
    @classmethod
    def initial(cls) -> "RetentionHistory":
        """Create an empty retention history."""
        return cls()


@dataclass(frozen=True)
class ProtentionExpectations:
    """
    Immutable bounded set of protentional expectations.
    
    This represents immediate expectations about the forthcoming context,
    distinct from prediction or planning.
    """
    expectations: Tuple[str, ...] = field(default_factory=tuple)
    """Tuple of expectation references."""
    
    max_size: int = 5
    
    def __post_init__(self):
        if len(self.expectations) > self.max_size:
            object.__setattr__(
                self,
                "expectations",
                self.expectations[:self.max_size]
            )


__all__: Tuple[str, ...] = (
    "TemporalContextType",
    "RetentionId",
    "PresentationId",
    "ProtentionId",
    "ContinuityWindowId",
    "TemporalSnapshotId",
    "GenerationNumber",
    "TrustLevel",
    "PrivacyClassification",
    "RetentionHistory",
    "ProtentionExpectations",
)
