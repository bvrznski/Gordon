# Oriented Network Base Persistence Model - Phase 4.7.8 Part 1
# =============================================================

"""
Base Persistence Model for the Oriented Network (Phase 4.7.8)

ARCHITECTURAL PRINCIPLES:
    - Persistence represents semantic continuity
    - It never implements runtime persistence mechanisms
    - No checkpointing, no storage ownership, no restart logic
    - Pure semantic representation only

PHASE 4.7.8 PART 1 - PERSISTENCE MODELS:
    BasePersistenceModel: Abstract base for all persistence models
    
PHASE 4.7.8 PART 2 WILL ADD:
    Persistence contracts and relationships
    Ownership rules
    Serialization framework
    Validation framework

NO RUNTIME BEHAVIOR:
    - No persistence engine
    - No checkpoint system
    - No recovery engine
    - No monitoring
    - No scheduling
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


# =============================================================================
# PERSISTENCE IDENTITY TYPES
# =============================================================================

PersistenceIdentity = str
"""
Unique identifier for a persistence instance.

Rules:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Persistence hash, source system ID with context prefix.
"""

PersistenceRevision = int
"""
Monotonically increasing revision number for persistence evolution.

Rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Meaning change always requires revision
    - Identity + Revision = unique persistence reference

No in-place mutation allowed. Create new revision instead.
"""

PersistenceVersion = int
"""
Schema version for persistence compatibility.

Rules:
    - Version N+1 may add fields but not remove existing ones
    - Schema changes require version increment
    - Compatibility is determined by version comparison
"""


# =============================================================================
# PERSISTENCE TYPE ENUMERATIONS
# =============================================================================

class PersistenceType:
    """
    Canonical persistence types for Oriented Network.
    
    SEMANTIC ROLE:
        - Represents semantic persistence categories
        - Never represents runtime state
    
    LAWS:
        ORIENTED-PERSISTENCE-LAW-001: Persistence represents semantic continuity
        ORIENTED-PERSISTENCE-LAW-005: Persistence preserves semantic identity
    """
    
    # Persistent orientation types (maintain identity)
    PERSISTENT = "persistent"
    """Persistent orientation that maintains identity"""
    
    TRANSIENT = "transient"
    """Transient orientation with limited persistence"""
    
    LONG_TERM = "long_term"
    """Long-term persistent orientation"""
    
    SHORT_TERM = "short_term"
    """Short-term persistent orientation"""
    
    DORMANT = "dormant"
    """Dormant orientation (inactive but recoverable)"""
    
    RECOVERED = "recovered"
    """Recovered orientation (restored from persistence)"""
    
    # Continuity types
    CONTINUOUS = "continuous"
    """Continuous orientation with uninterrupted identity"""
    
    INTERRUPTED = "interrupted"
    """Interrupted orientation (identity preserved across interruption)"""
    
    RESUMED = "resumed"
    """Resumed orientation (restarted after interruption)"""
    
    RESTORED = "restored"
    """Restored orientation (recovered from persistence state)"""
    
    INHERITED = "inherited"
    """Inherited orientation (continuity from source)"""


# =============================================================================
# BASE PERSISTENCE MODEL
# =============================================================================

@dataclass(frozen=True)
class BasePersistenceModel(ABC):
    """
    Abstract base class for all Oriented Network Persistence models.
    
    ARCHITECTURAL INVARIANTS:
        BPM-INV-001: Persistence represents semantic continuity only
        BPM-INV-002: Persistence is deeply immutable (frozen dataclass)
        BPM-INV-003: Persistence possesses stable semantic identity
        BPM-INV-004: Persistence never owns runtime persistence mechanisms
        BPM-INV-005: Persistence never implements checkpointing
        BPM-INV-006: Persistence never implements recovery execution
        BPM-INV-007: Serialization must be deterministic
        
    NOT RESPONSIBLE FOR:
        - Runtime persistence (owned by future runtime phases)
        - Checkpoint mechanisms
        - Storage management
        - Recovery execution
        - Monitoring or scheduling
        
    SEMANTIC ROLE:
        Represents what must remain coherent,
        rather than how coherence is maintained.
    """
    
    persistence_id: PersistenceIdentity
    """Unique semantic identifier for this persistence instance"""
    
    revision: PersistenceRevision = 1
    """Semantic revision number (starts at 1)"""
    
    version: PersistenceVersion = 1
    """Schema version for compatibility"""
    
    persistence_type: str = field(default=PersistenceType.PERSISTENT)
    """The type of persistence this represents"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize persistence model to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BasePersistenceModel:
        """
        Create persistence model from a dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the persistence model type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate persistence model against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
            
        INVARIANT: Validation is deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_provenance(self) -> Dict[str, Any]:
        """
        Get immutable provenance information.
        
        Returns:
            Dictionary containing provenance data (created_by, derived_from, etc.)
            
        INVARIANT: Provenance is immutable and cannot be modified after creation
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_lineage(self) -> Tuple[PersistenceIdentity, ...]:
        """
        Get immutable lineage (ancestral chain).
        
        Returns:
            Tuple of ancestor persistence_id values from most recent to oldest
            
        INVARIANT: Lineage is immutable and cannot be modified after creation
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate model on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} persistence model:\n{error_list}"
            )
    
    def with_revision(self, new_revision: PersistenceRevision) -> BasePersistenceModel:
        """
        Return a new persistence model with the specified revision.
        
        Args:
            new_revision: The desired revision number
            
        Returns:
            A new persistence instance with updated revision
        """
        return type(self)(
            persistence_id=self.persistence_id,
            revision=new_revision,
            version=self.version,
            persistence_type=self.persistence_type,
        )
    
    def get_identity_with_revision(self) -> str:
        """
        Get a string representation combining identity and revision.
        
        Returns:
            Formatted string: "{identity}:v{revision}"
        """
        return f"{self.persistence_id}:v{self.revision}"


# =============================================================================
# PERSISTENCE REFERENCE BASE
# =============================================================================

@dataclass(frozen=True)
class BasePersistenceReference:
    """
    Base reference to a persistence model.
    
    INVARIANTS:
        BPR-INV-001: Reference is immutable
        BPR-INV-002: Reference never owns the referenced persistence
        BPR-INV-003: Reference maintains identity across revisions
    
    SEMANTIC ROLE:
        Provides lightweight reference to persistence without ownership.
    """
    
    persistence_id: PersistenceIdentity
    """Reference to the persistence identity"""
    
    revision: PersistenceRevision = 1
    """Reference revision (may differ from current)"""
    
    @classmethod
    def create(cls, persistence_id: PersistenceIdentity, revision: PersistenceRevision = 1) -> BasePersistenceReference:
        """Create a new persistence reference."""
        return cls(persistence_id=persistence_id, revision=revision)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize reference to dictionary."""
        return {
            "persistence_id": self.persistence_id,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BasePersistenceReference:
        """Create reference from dictionary."""
        return cls(
            persistence_id=data["persistence_id"],
            revision=data.get("revision", 1),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PersistenceIdentity",
    "PersistenceRevision",
    "PersistenceVersion",
    "PersistenceType",
    "BasePersistenceModel",
    "BasePersistenceReference",
]