# Oriented Network State Metadata Types - Phase 4.7.4
# =====================================================

"""
Metadata types for the Oriented Network State Model.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

METADATA CATEGORIES:
    - Identity: Stable semantic identity for state instances
    - Revision: Monotonic revision tracking for state evolution
    - Lineage: Immutable ancestral chain of states
    - Provenance: Immutable origin and validation history
    - Authority: Ownership and authority specifications
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum


# =============================================================================
# PROVENANCE TYPES - Origin and validation history
# =============================================================================

@dataclass(frozen=True)
class StateProvenance:
    """
    Immutable provenance information for a state instance.
    
    SEMANTIC ROLE:
        - Records origin of the state (CreatedFrom, DerivedFrom, ObservedFrom)
        - Records validation chain (ValidatedBy, CertifiedBy)
        - Never contains mutable audit history
        
    PROVENANCE INVARIANTS:
        SP-INV-001: Provenance is immutable
        SP-INV-002: Provenance never contains runtime data
        SP-INV-003: Provenance records semantic origin only
    """
    
    created_from: Optional[str] = None
    """Source of initial creation (external state ID, if any)"""
    
    derived_from: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of states this was derived from"""
    
    observed_from: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of states this observes/monitors"""
    
    validated_by: Optional[str] = None
    """Validator that certified this state (validator ID)"""
    
    certified_by: Optional[str] = None
    """Certifier that authorized this state (authority ID)"""
    
    @classmethod
    def create(
        cls,
        created_from: Optional[str] = None,
        derived_from: Optional[Tuple[str, ...]] = None,
        observed_from: Optional[Tuple[str, ...]] = None,
        validated_by: Optional[str] = None,
        certified_by: Optional[str] = None,
    ) -> StateProvenance:
        return cls(
            created_from=created_from,
            derived_from=tuple(derived_from) if derived_from else tuple(),
            observed_from=tuple(observed_from) if observed_from else tuple(),
            validated_by=validated_by,
            certified_by=certified_by,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_from": self.created_from,
            "derived_from": list(self.derived_from),
            "observed_from": list(self.observed_from),
            "validated_by": self.validated_by,
            "certified_by": self.certified_by,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateProvenance:
        return cls(
            created_from=data.get("created_from"),
            derived_from=tuple(data.get("derived_from", [])),
            observed_from=tuple(data.get("observed_from", [])),
            validated_by=data.get("validated_by"),
            certified_by=data.get("certified_by"),
        )


# =============================================================================
# LINEAGE TYPES - Ancestral chain
# =============================================================================

@dataclass(frozen=True)
class StateLineage:
    """
    Immutable ancestral chain for a state instance.
    
    SEMANTIC ROLE:
        - Records root ancestor (RootState)
        - Records immediate parent (ParentState, PreviousState)
        - Records related states (RelatedState, OriginState)
        - Never contains runtime history
        
    LINEAGE INVARIANTS:
        SL-INV-001: Lineage is immutable
        SL-INV-002: Lineage represents semantic ancestry only
        SL-INV-003: Lineage graph remains acyclic
    """
    
    root_state_id: Optional[str] = None
    """ID of the root ancestor state"""
    
    parent_state_id: Optional[str] = None
    """ID of the immediate parent state"""
    
    previous_state_id: Optional[str] = None
    """ID of the immediately preceding state in sequence"""
    
    related_state_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of semantically related states (siblings, cousins, etc.)"""
    
    origin_state_id: Optional[str] = None
    """ID of the original state in a chain of derivation"""
    
    @classmethod
    def create(
        cls,
        root_state_id: Optional[str] = None,
        parent_state_id: Optional[str] = None,
        previous_state_id: Optional[str] = None,
        related_state_ids: Optional[Tuple[str, ...]] = None,
        origin_state_id: Optional[str] = None,
    ) -> StateLineage:
        return cls(
            root_state_id=root_state_id,
            parent_state_id=parent_state_id,
            previous_state_id=previous_state_id,
            related_state_ids=tuple(related_state_ids) if related_state_ids else tuple(),
            origin_state_id=origin_state_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_state_id": self.root_state_id,
            "parent_state_id": self.parent_state_id,
            "previous_state_id": self.previous_state_id,
            "related_state_ids": list(self.related_state_ids),
            "origin_state_id": self.origin_state_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateLineage:
        return cls(
            root_state_id=data.get("root_state_id"),
            parent_state_id=data.get("parent_state_id"),
            previous_state_id=data.get("previous_state_id"),
            related_state_ids=tuple(data.get("related_state_ids", [])),
            origin_state_id=data.get("origin_state_id"),
        )


# =============================================================================
# ORIGIN TYPES - State source information
# =============================================================================

@dataclass(frozen=True)
class StateOrigin:
    """
    Immutable origin information for a state instance.
    
    SEMANTIC ROLE:
        - Records where the state originated
        - Never contains runtime location
        
    ORIGIN INVARIANTS:
        SO-INV-001: Origin is immutable
        SO-INV-002: Origin records semantic source only
    """
    
    source_type: str = "internal"
    """Type of source ('internal', 'external', 'derived')"""
    
    source_system: Optional[str] = None
    """Name of the system that produced the state"""
    
    source_version: Optional[str] = None
    """Version of the source system"""
    
    @classmethod
    def create(
        cls,
        source_type: str = "internal",
        source_system: Optional[str] = None,
        source_version: Optional[str] = None,
    ) -> StateOrigin:
        return cls(source_type=source_type, source_system=source_system, source_version=source_version)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_system": self.source_system,
            "source_version": self.source_version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateOrigin:
        return cls(
            source_type=data.get("source_type", "internal"),
            source_system=data.get("source_system"),
            source_version=data.get("source_version"),
        )


# =============================================================================
# METADATA COMBINED TYPE
# =============================================================================

@dataclass(frozen=True)
class StateMetadata:
    """
    Combined metadata for a state instance.
    
    SEMANTIC ROLE:
        - Provides identity, revision, version info
        - Records provenance and lineage
        - Specifies authority and ownership
        
    METADATA INVARIANTS:
        STM-INV-001: All metadata fields are immutable
        STM-INV-002: Metadata never contains runtime data
        STM-INV-003: Metadata is deterministically serializable
    """
    
    # Identity information
    state_id: str
    """Unique identifier for this state instance"""
    
    revision: int = 1
    """Current semantic revision number"""
    
    version: int = 1
    """Schema version for compatibility"""
    
    # Authority information
    authority: str = "oriented_network"
    """Source of authority (authority name)"""
    
    owner: str = "oriented_network"
    """Architectural owner"""
    
    # Origin information
    origin: StateOrigin = field(default_factory=StateOrigin)
    """Where the state originated"""
    
    provenance: StateProvenance = field(default_factory=StateProvenance)
    """Validation and derivation history"""
    
    lineage: StateLineage = field(default_factory=StateLineage)
    """Ancestral chain of states"""
    
    @classmethod
    def create(
        cls,
        state_id: str,
        revision: int = 1,
        version: int = 1,
        authority: str = "oriented_network",
        owner: str = "oriented_network",
        origin: Optional[StateOrigin] = None,
        provenance: Optional[StateProvenance] = None,
        lineage: Optional[StateLineage] = None,
    ) -> StateMetadata:
        return cls(
            state_id=state_id,
            revision=revision,
            version=version,
            authority=authority,
            owner=owner,
            origin=origin or StateOrigin(),
            provenance=provenance or StateProvenance(),
            lineage=lineage or StateLineage(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority,
            "owner": self.owner,
            "origin": self.origin.to_dict(),
            "provenance": self.provenance.to_dict(),
            "lineage": self.lineage.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StateMetadata:
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "oriented_network"),
            owner=data.get("owner", "oriented_network"),
            origin=StateOrigin.from_dict(data.get("origin", {})),
            provenance=StateProvenance.from_dict(data.get("provenance", {})),
            lineage=StateLineage.from_dict(data.get("lineage", {})),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StateProvenance",
    "StateLineage",
    "StateOrigin",
    "StateMetadata",
]