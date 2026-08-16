# Oriented Network Base State Abstractions - Phase 4.7.4
# =======================================================

"""
Base abstractions for all Oriented Network State types.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

STATE LAWS:
    ORIENTED-STATE-LAW-001: Every State object represents a semantic snapshot
    ORIENTED-STATE-LAW-002: Every State object is deeply immutable
    ORIENTED-STATE-LAW-003: Every State object possesses stable semantic identity
    ORIENTED-STATE-LAW-004: Every State object possesses explicit ownership
    ORIENTED-STATE-LAW-005: Every State object possesses explicit authority
    ORIENTED-STATE-LAW-006 through 040: Additional state laws
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

StateIdentity = str
"""
Unique identifier for a state instance.

Rules:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: State hash, source system ID with context prefix.
"""

StateRevision = int
"""
Monotonically increasing revision number for state evolution.

Rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Meaning change always requires revision
    - Identity + Revision = unique state reference

No in-place mutation allowed. Create new revision instead.
"""

StateVersion = int
"""
Schema version for state compatibility.

Rules:
    - Version N+1 may add fields but not remove existing ones
    - Schema changes require version increment
    - Compatibility is determined by version comparison
"""


# =============================================================================
# AUTHORITY TYPES - Ownership and authority specifications
# =============================================================================

class StateAuthority(Enum):
    """
    Authority types that can own state.
    
    STATE LAWS:
        ORIENTED-STATE-LAW-011: Orientation State owns semantic orientation representations only
        ORIENTED-STATE-LAW-012 through 018: Reference ownership constraints
    """
    
    ORIENTED_NETWORK = "oriented_network"
    """Owned by the Oriented Network (orientation semantics)"""
    
    GOAL_SYSTEM = "goal_system"
    """Owned by Goal System (Goals remain externally authoritative)"""
    
    EXECUTIVE = "executive"
    """Owned by Executive Network"""
    
    PLANNING = "planning"
    """Owned by Planning subsystem"""
    
    DECISION_NETWORK = "decision_network"
    """Owned by Decision Network"""
    
    WORKSPACE = "workspace"
    """Owned by Workspace Network"""
    
    WORKING_MEMORY = "working_memory"
    """Owned by Working Memory subsystem"""
    
    ATTENTION = "attention"
    """Owned by Attention Network"""
    
    STRATEGY = "strategy"
    """Owned by Strategy subsystem"""
    
    COGNITIVE_ARTIFACT = "cognitive_artifact"
    """External cognitive artifact (not owned by any subsystem)"""


StateOwner = str
"""
Architectural owner of state.

Format: "subsystem_name" or "external:<source>"
Examples:
    "oriented_network"
    "goal_system"
    "external:planning_subsystem"
"""


# =============================================================================
# BASE STATE INTERFACE
# =============================================================================

@dataclass(frozen=True)
class BaseState(ABC):
    """
    Abstract base class for all Oriented Network State.
    
    ARCHITECTURAL INVARIANTS:
        BS-INV-001: State never represents runtime execution
        BS-INV-002: State is deeply immutable (frozen dataclass)
        BS-INV-003: State possesses stable semantic identity
        BS-INV-004: State possesses explicit ownership
        BS-INV-005: State possesses immutable provenance
        
    NOT RESPONSIBLE FOR:
        - Runtime execution
        - State management
        - Scheduling or coordination
        - Planning or reasoning
    """
    
    state_id: StateIdentity
    """Unique semantic identifier for this state instance"""
    
    revision: StateRevision = 1
    """Semantic revision number (starts at 1)"""
    
    version: StateVersion = 1
    """Schema version for compatibility"""
    
    authority: StateAuthority = StateAuthority.ORIENTED_NETWORK
    """Source of authority for this state"""
    
    owner: StateOwner = "oriented_network"
    """Architectural owner of this state"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize state to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseState:
        """
        Create state from a dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the state type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate state against semantic requirements.
        
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
    def get_lineage(self) -> Tuple[StateIdentity, ...]:
        """
        Get immutable lineage (ancestral chain).
        
        Returns:
            Tuple of ancestor state_id values from most recent to oldest
            
        INVARIANT: Lineage is immutable and cannot be modified after creation
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate state on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} state:\n{error_list}"
            )

    def with_revision(self, new_revision: StateRevision) -> BaseState:
        """
        Return a new state with the specified revision.
        
        Args:
            new_revision: The desired revision number
            
        Returns:
            A new state instance with updated revision
        """
        return type(self)(
            state_id=self.state_id,
            revision=new_revision,
            version=self.version,
            authority=self.authority,
            owner=self.owner,
        )

    def with_metadata(
        self,
        provenance: Optional[Dict[str, Any]] = None,
        lineage: Optional[Tuple[StateIdentity, ...]] = None,
    ) -> BaseState:
        """
        Return a new state with updated metadata.
        
        Args:
            provenance: New provenance information (optional)
            lineage: New lineage tuple (optional)
            
        Returns:
            A new state instance with updated metadata
        """
        return type(self)(
            state_id=self.state_id,
            revision=self.revision,
            version=self.version,
            authority=self.authority,
            owner=self.owner,
        )


# =============================================================================
# STATE METADATA BASE CLASSES
# =============================================================================

@dataclass(frozen=True)
class StateMetadataBase(ABC):
    """
    Base class for state metadata.
    
    INVARIANTS:
        SM-INV-001: Metadata is immutable
        SM-INV-002: Metadata describes state properties only
        SM-INV-003: Metadata never contains runtime data
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateMetadataBase:
        raise NotImplementedError


@dataclass(frozen=True)
class StateIdentityMetadata(StateMetadataBase):
    """
    Identity metadata for a state instance.
    
    INVARIANTS:
        SIM-INV-001: Identity is stable across revisions
        SIM-INV-002: Identity is deterministically derived or externally supplied
    """
    
    state_id: StateIdentity
    """Unique identifier for this state instance"""
    
    canonical_form: bool = True
    """Whether this represents the canonical form of the state"""
    
    @classmethod
    def create(cls, state_id: StateIdentity) -> StateIdentityMetadata:
        return cls(state_id=state_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "canonical_form": self.canonical_form,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateIdentityMetadata:
        return cls(
            state_id=data["state_id"],
            canonical_form=data.get("canonical_form", True),
        )


@dataclass(frozen=True)
class StateRevisionMetadata(StateMetadataBase):
    """
    Revision metadata for a state instance.
    
    INVARIANTS:
        SRM-INV-001: Revision is monotonically increasing
        SRM-INV-002: Each revision represents a semantic change
    """
    
    revision: StateRevision = 1
    """Current revision number"""
    
    previous_revision: Optional[StateRevision] = None
    """Previous revision (None for initial)"""
    
    is_initial: bool = False
    """Whether this is the initial state"""
    
    @classmethod
    def create(cls, revision: StateRevision = 1, is_initial: bool = False) -> StateRevisionMetadata:
        return cls(
            revision=revision,
            previous_revision=None if is_initial else (revision - 1),
            is_initial=is_initial,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "revision": self.revision,
            "previous_revision": self.previous_revision,
            "is_initial": self.is_initial,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateRevisionMetadata:
        return cls(
            revision=data["revision"],
            previous_revision=data.get("previous_revision"),
            is_initial=data.get("is_initial", False),
        )


@dataclass(frozen=True)
class StateVersionMetadata(StateMetadataBase):
    """
    Version metadata for a state schema.
    
    INVARIANTS:
        SVM-INV-001: Version tracks schema compatibility
        SVM-INV-002: Higher versions are backward compatible
    """
    
    version: StateVersion = 1
    """Current schema version"""
    
    min_compatible_version: StateVersion = 1
    """Minimum compatible version (backward compatibility)"""
    
    schema_uri: Optional[str] = None
    """URI reference to schema documentation"""
    
    @classmethod
    def create(cls, version: StateVersion = 1) -> StateVersionMetadata:
        return cls(version=version, min_compatible_version=version)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "min_compatible_version": self.min_compatible_version,
            "schema_uri": self.schema_uri,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateVersionMetadata:
        return cls(
            version=data["version"],
            min_compatible_version=data.get("min_compatible_version", 1),
            schema_uri=data.get("schema_uri"),
        )


# =============================================================================
# STATE COMPOSITION BASE CLASSES
# =============================================================================

@dataclass(frozen=True)
class BaseStateComposition:
    """
    Base class for state composition.
    
    INVARIANTS:
        BSC-INV-001: Composition references immutable content
        BSC-INV-002: Composition never duplicates content
        BSC-INV-003: Composition is explicitly typed
    """
    
    @abstractmethod
    def validate_composition(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate composition structure."""
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StateIdentity",
    "StateRevision",
    "StateVersion",
    "StateAuthority",
    "StateOwner",
    "BaseState",
    "StateMetadataBase",
    "StateIdentityMetadata",
    "StateRevisionMetadata",
    "StateVersionMetadata",
    "BaseStateComposition",
]