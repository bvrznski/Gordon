# Jurisdiction Management - Phase 7.47 Part 1
# =============================================

"""
Canonical Jurisdiction Contract.

Jurisdiction management evaluates:
    - territorial scope
    - applicable authorities
    - legal hierarchy
    - cross-border applicability
    - conflicts of law
    - governing jurisdiction

Jurisdictions remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class JurisdictionType(Enum):
    """Types of jurisdictions."""
    
    TERRITORIAL = "territorial"           # Based on physical location
    PERSONAL = "personal"                 # Based on personal status
    SUBJECT_MATTER = "subject_matter"     # Based on subject matter
    SUPRANATIONAL = "supranational"       # International bodies
    FEDERAL = "federal"                   # Federal systems


@dataclass(frozen=True)
class Jurisdiction:
    """
    A jurisdiction with explicit boundaries and authority.
    
    A jurisdiction includes:
        - Governing authority (who makes law here?)
        - Applicable sources (what laws apply?)
        - Territorial scope (where does it apply?)
        - Hierarchical position (how does it rank?)
    
    Jurisdictions remain explicitly defined for traceable analysis.
    """
    
    # Identity
    jurisdiction_id: str                      # Unique identifier
    
    # Authority
    governing_authority: str                  # Who governs here?
    authority_level: str                      # e.g., "federal", "state", "local"
    
    # Scope
    jurisdiction_type: JurisdictionType       # What type of jurisdiction?
    territorial_scope: Tuple[str, ...] = ()   # Geographic scope
    subject_matter_scope: Tuple[str, ...] = ()  # What topics apply?
    
    # Hierarchy
    hierarchical_position: int = 0            # Lower = higher priority
    
    # Applicable sources
    applicable_sources: Tuple[str, ...] = ()  # Source IDs that apply
    
    # Configuration
    override_jurisdictions: Tuple[str, ...] = ()  # Higher jurisdictions that override
    overridden_by: Tuple[str, ...] = ()           # Lower jurisdictions overridden
    
    # Timing
    effective_from_utc: float = field(default_factory=time.time)
    effective_to_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if jurisdiction is currently active."""
        now = time.time()
        return (
            self.effective_from_utc <= now and 
            (self.effective_to_utc is None or self.effective_to_utc >= now)
        )
    
    @classmethod
    def create(
        cls,
        governing_authority: str,
        authority_level: str,
        jurisdiction_type: JurisdictionType,
        territorial_scope: Optional[List[str]] = None,
        subject_matter_scope: Optional[List[str]] = None,
    ) -> Jurisdiction:
        """Create a new jurisdiction."""
        return cls(
            jurisdiction_id=f"jurisdiction:{uuid.uuid4().hex[:16]}",
            governing_authority=governing_authority,
            authority_level=authority_level,
            jurisdiction_type=jurisdiction_type,
            territorial_scope=tuple(territorial_scope or []),
            subject_matter_scope=tuple(subject_matter_scope or []),
        )
    
    def with_hierarchical_position(self, position: int) -> Jurisdiction:
        """Return a copy with updated hierarchical position."""
        return dataclass_replace(
            self,
            hierarchical_position=position,
        )


@dataclass(frozen=True)
class JurisdictionManager:
    """
    Manager for multiple jurisdictions.
    
    Handles jurisdiction selection, conflict resolution, and
    hierarchy management across multiple legal systems.
    """
    
    manager_id: str                           # Unique identifier
    
    # Known jurisdictions
    jurisdictions: Dict[str, Jurisdiction] = field(default_factory=dict)
    
    # Active jurisdiction selection
    active_jurisdiction_ids: Tuple[str, ...] = ()  # Selected jurisdictions
    
    # Conflict resolution rules
    conflict_resolution_strategy: str = "hierarchical"  # How to resolve conflicts
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        conflict_resolution_strategy: str = "hierarchical",
    ) -> JurisdictionManager:
        """Create a new jurisdiction manager."""
        return cls(
            manager_id=f"jurisdiction_manager:{uuid.uuid4().hex[:16]}",
            conflict_resolution_strategy=conflict_resolution_strategy,
        )
    
    def add_jurisdiction(self, jurisdiction: Jurisdiction) -> JurisdictionManager:
        """Add a jurisdiction to the manager."""
        new_jurisdictions = dict(self.jurisdictions)
        new_jurisdictions[jurisdiction.jurisdiction_id] = jurisdiction
        return dataclass_replace(
            self,
            jurisdictions=new_jurisdictions,
        )
    
    def select_active_jurisdictions(
        self, 
        jurisdiction_ids: List[str],
    ) -> JurisdictionManager:
        """Select which jurisdictions to consider active."""
        return dataclass_replace(
            self,
            active_jurisdiction_ids=tuple(jurisdiction_ids),
        )
    
    def get_highest_priority_jurisdiction(self) -> Optional[Jurisdiction]:
        """Get the highest priority (lowest hierarchical position) jurisdiction."""
        if not self.active_jurisdiction_ids:
            return None
        
        active = [
            self.jurisdictions[jid] 
            for jid in self.active_jurisdiction_ids
            if jid in self.jurisdictions
        ]
        
        if not active:
            return None
        
        # Return jurisdiction with lowest hierarchical position (highest priority)
        return min(active, key=lambda j: j.hierarchical_position)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Jurisdiction",
    "JurisdictionType",
    "JurisdictionManager",
]