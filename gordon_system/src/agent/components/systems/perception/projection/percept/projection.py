# Perception Percept Projection - Phase 5.2.4
# ============================================

"""
Percept Projection: Exposes selected Percepts or Fused Percepts.

A Percept Projection exposes selected Percepts or Fused Percepts.
It may expose artifact identity, percept kind, source Modalities,
observed properties, temporal extent, spatial extent, confidence,
uncertainty, conflicts, alternatives, limitations, and provenance.

A Percept Projection shall not assign canonical environmental entity identity.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# PERCEPT PROJECTION FIELDS
# =============================================================================


@dataclass(frozen=True)
class PerceptProjectionFieldSelection:
    """
    Record of which fields were selected for a percept in the projection.
    
    Derived presentation fields shall remain distinguishable from source fields.
    """
    
    field_selection_identity: str
    
    # Reference to the percept
    percept_reference: str  # Percept ID
    
    # Requested vs actual
    requested_fields: Tuple[str, ...] = field(default_factory=tuple)
    included_fields: Tuple[str, ...] = field(default_factory=tuple)
    omitted_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Field metadata
    unsupported_fields: Tuple[str, ...] = field(default_factory=tuple)  # Consumer can't support these
    restricted_fields: Tuple[str, ...] = field(default_factory=tuple)   # Hidden by authorization
    
    # Derived presentation fields (computed for presentation)
    derived_presentation_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Selection basis
    selection_basis: str = "default"  # default, consumer_contract, policy
    
    # Confidence/uncertainty effects
    confidence_effect: float = 0.0
    uncertainty_effect: float = 0.0


@dataclass(frozen=True)
class PerceptProjectionFieldProvenance:
    """
    Provenance tracking for individual fields in a projected percept.
    
    Field-level provenance shall remain inspectable where applicable.
    """
    
    field_provenance_identity: str
    
    # Field reference
    field_name: str
    percept_reference: str  # Which percept this field belongs to
    
    # Origin
    source_field: Optional[str] = None      # Original field name (if different)
    source_artifact: Optional[str] = None   # Source artifact ID
    modality_origin: Optional[str] = None   # Which modality provided this field
    
    # Processing steps
    transformed_by: Tuple[str, ...] = field(default_factory=tuple)  # Processing stages
    filtered_by: Tuple[str, ...] = field(default_factory=tuple)     # Filters applied
    
    # Confidence/uncertainty at source
    source_confidence: float = 1.0
    source_uncertainty: float = 0.0


# =============================================================================
# PERCEPT PROJECTION
# =============================================================================


@dataclass(frozen=True)
class PerceptProjection:
    """
    Projection of selected Percepts.
    
    A Percept Projection exposes selected Percepts or Fused Percepts.
    It preserves the difference between source Percepts and Fused Percepts.
    
    Fields:
        projection_identity:       Unique identifier for this projection
        source_percepts:           IDs of source percepts used
        projected_percepts:        IDs of percepts in this view (may be fused)
        source_modalities:         Modalities that contributed to these percepts
        selected_fields:           Which fields were included per percept
        omitted_fields:            Fields that were filtered out
        field_provenance:          Provenance for each field
        conflicts:                 Conflicting interpretations (if visible)
        alternatives:              Alternative interpretations (if visible)
        confidence:                Overall projection confidence
        uncertainty:               Overall projection uncertainty
        limitations:               Any limitations affecting this view
        freshness_state:           How current is the projection
        revision:                  Projection revision number
    """
    
    projection_identity: str
    
    # Source references
    source_percepts: Tuple[str, ...] = field(default_factory=tuple)
    projected_percepts: Tuple[str, ...] = field(default_factory=tuple)
    
    # Source information
    source_modalities: Tuple[str, ...] = field(default_factory=tuple)
    
    # Field selection (per percept)
    selected_fields: Dict[str, Tuple[str, ...]] = field(default_factory=dict)  # Percept ID -> fields
    omitted_fields: Dict[str, Tuple[str, ...]] = field(default_factory=dict)   # Percept ID -> omitted
    
    # Provenance per field
    field_provenance: Dict[str, List[PerceptProjectionFieldProvenance]] = field(
        default_factory=dict
    )  # Field name -> list of provenances
    
    # Conflict/ambiguity information
    conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Conflict records
    alternatives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Alternative interpretations
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations
    limitations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Freshness and revision
    freshness_state: str = "current"
    freshness_timestamp_utc: float = field(default_factory=_time.time)
    source_revision_reference: Optional[str] = None
    projection_revision: int = 1
    
    @classmethod
    def create(
        cls,
        source_percept_ids: List[str],
        projected_percept_ids: Optional[List[str]] = None,
        source_modalities: Optional[List[str]] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "PerceptProjection":
        """
        Create a new Percept Projection.
        
        Args:
            source_percept_ids: IDs of source percepts
            projected_percept_ids: IDs of percepts in this view (may be fused)
            source_modalities: Modalities that contributed to these percepts
            confidence: Overall projection confidence (0.0-1.0)
            uncertainty: Overall projection uncertainty (0.0-1.0)
            
        Returns:
            New PerceptProjection instance
        """
        return cls(
            projection_identity=f"percept_projection:{uuid.uuid4().hex[:24]}",
            source_percepts=tuple(source_percept_ids),
            projected_percepts=tuple(projected_percept_ids or source_percept_ids),
            source_modalities=tuple(source_modalities or []),
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def with_fused_percepts(
        cls,
        source_percept_ids: List[str],
        fused_percept_id: str,
        source_modalities: Optional[List[str]] = None,
        confidence: float = 0.85,
    ) -> "PerceptProjection":
        """
        Create a Percept Projection with fused percepts.
        
        This preserves the difference between source and fused percepts.
        
        Args:
            source_percept_ids: IDs of source percepts that were fused
            fused_percept_id: The resulting fused percept ID
            source_modalities: Modalities that contributed
            confidence: Confidence after fusion (typically < individual confidences)
            
        Returns:
            New PerceptProjection with fused representation
        """
        return cls(
            projection_identity=f"percept_projection:{uuid.uuid4().hex[:24]}",
            source_percepts=tuple(source_percept_ids),
            projected_percepts=(fused_percept_id,),
            source_modalities=tuple(source_modalities or []),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the projection has valid data."""
        if not self.projection_identity or len(self.projection_identity) == 0:
            return False
        if not self.source_percepts:
            # Empty projections are valid for "no evidence" cases
            return True
        if not (0.0 <= self.confidence <= 1.0):
            return False
        if not (0.0 <= self.uncertainty <= 1.0):
            return False
        
        return True


# =============================================================================
# PROJECTION BUILDER
# =============================================================================


class PerceptProjectionBuilder:
    """Mutable builder for constructing percept projections."""
    
    def __init__(self):
        self._projection_identity: str = f"percept_projection:{uuid.uuid4().hex[:24]}"
        self._source_percepts: List[str] = []
        self._projected_percepts: List[str] = []
        self._source_modalities: List[str] = []
        self._selected_fields: Dict[str, List[str]] = {}
        self._omitted_fields: Dict[str, List[str]] = {}
        self._field_provenance: Dict[str, List[PerceptProjectionFieldProvenance]] = {}
        self._conflicts: List[Dict[str, Any]] = []
        self._alternatives: List[Dict[str, Any]] = []
        self._limitations: List[Dict[str, Any]] = []
        self._confidence: float = 1.0
        self._uncertainty: float = 0.0
    
    def set_identity(self, identity: str) -> "PerceptProjectionBuilder":
        """Set the projection identity."""
        self._projection_identity = identity
        return self
    
    def add_source_percept(self, percept_id: str) -> "PerceptProjectionBuilder":
        """Add a source percept ID."""
        if percept_id not in self._source_percepts:
            self._source_percepts.append(percept_id)
        return self
    
    def set_projected_percept(self, percept_id: str) -> "PerceptProjectionBuilder":
        """Set the projected (resulting) percept ID."""
        if percept_id not in self._projected_percepts:
            self._projected_percepts.append(percept_id)
        return self
    
    def add_modality(self, modality_id: str) -> "PerceptProjectionBuilder":
        """Add a source modality ID."""
        if modality_id not in self._source_modalities:
            self._source_modalities.append(modality_id)
        return self
    
    def set_selected_fields(
        self,
        percept_id: str,
        fields: List[str],
    ) -> "PerceptProjectionBuilder":
        """Set selected fields for a percept."""
        if percept_id not in self._selected_fields:
            self._selected_fields[percept_id] = []
        self._selected_fields[percept_id] = list(fields)
        return self
    
    def set_omitted_fields(
        self,
        percept_id: str,
        fields: List[str],
    ) -> "PerceptProjectionBuilder":
        """Set omitted fields for a percept."""
        if percept_id not in self._omitted_fields:
            self._omitted_fields[percept_id] = []
        self._omitted_fields[percept_id] = list(fields)
        return self
    
    def add_field_provenance(
        self,
        field_name: str,
        provenance: PerceptProjectionFieldProvenance,
    ) -> "PerceptProjectionBuilder":
        """Add provenance for a field."""
        if field_name not in self._field_provenance:
            self._field_provenance[field_name] = []
        self._field_provenance[field_name].append(provenance)
        return self
    
    def add_conflict(self, conflict: Dict[str, Any]) -> "PerceptProjectionBuilder":
        """Add a conflict record."""
        self._conflicts.append(dict(conflict))
        return self
    
    def add_alternative(self, alternative: Dict[str, Any]) -> "PerceptProjectionBuilder":
        """Add an alternative interpretation record."""
        self._alternatives.append(dict(alternative))
        return self
    
    def add_limitation(
        self,
        limitation: Dict[str, Any],
    ) -> "PerceptProjectionBuilder":
        """Add a limitation affecting this projection."""
        self._limitations.append(dict(limitation))
        return self
    
    def set_confidence(self, confidence: float) -> "PerceptProjectionBuilder":
        """Set overall projection confidence (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "PerceptProjectionBuilder":
        """Set overall projection uncertainty (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_freshness(self, state: str) -> "PerceptProjectionBuilder":
        """Set freshness state (current, recent, stale, expired)."""
        valid_states = ("current", "recent", "stale", "expired")
        if state not in valid_states:
            raise ValueError(f"Invalid freshness state: {state}")
        self._freshness_state = state
        return self
    
    def build(self) -> PerceptProjection:
        """Build an immutable PerceptProjection."""
        if len(self._source_percepts) == 0 and len(self._projected_percepts) == 0:
            raise ValueError("At least one percept is required")
        
        # Convert all lists to tuples
        selected_fields = {
            k: tuple(v) for k, v in self._selected_fields.items()
        }
        omitted_fields = {
            k: tuple(v) for k, v in self._omitted_fields.items()
        }
        field_provenance = {
            k: list(v) for k, v in self._field_provenance.items()
        }
        
        return PerceptProjection(
            projection_identity=self._projection_identity,
            source_percepts=tuple(self._source_percepts),
            projected_percepts=tuple(self._projected_percepts),
            source_modalities=tuple(self._source_modalities),
            selected_fields=selected_fields,
            omitted_fields=omitted_fields,
            field_provenance=field_provenance,
            conflicts=tuple(dict(c) for c in self._conflicts),
            alternatives=tuple(dict(a) for a in self._alternatives),
            limitations=tuple(dict(l) for l in self._limitations),
            confidence=self._confidence,
            uncertainty=self._uncertainty,
        )


__all__ = [
    "PerceptProjectionFieldSelection",
    "PerceptProjectionFieldProvenance",
    "PerceptProjection",
    "PerceptProjectionBuilder",
]