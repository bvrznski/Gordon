# Workspace Consistency Module
# ============================

"""
Canonical Consistency models for workspace states.

Consistency semantics represent semantic correctness of workspace state,
including revision consistency, lineage consistency, dependency consistency,
provenance consistency, ownership consistency, and authority consistency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SemanticConsistency:
    """
    Record of semantic consistency for a workspace state.
    
    Captures whether the semantic content of a state is internally consistent
    without runtime dependencies.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the state is semantically consistent."""
    
    consistency_kind: str = "semantic"
    """Kind of consistency checked (semantic, revision, lineage, etc.)."""
    
    # Details
    inconsistent_claims: Tuple[str, ...] = field(default_factory=tuple)
    """Any contradictory semantic claims found."""
    
    missing_context: Tuple[str, ...] = field(default_factory=tuple)
    """Required semantic context that is missing."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""
    
    validator_id: str = ""
    """ID of the consistency validator."""


@dataclass(frozen=True)
class RevisionConsistency:
    """
    Record of revision consistency for a workspace state.
    
    Ensures that revision numbers are strictly monotonic and properly connected
    through transitions.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the revision chain is consistent."""
    
    # Revision details
    expected_revision: int = 0
    """The revision number this state should have."""
    
    actual_revision: int = 0
    """The actual revision number in this state."""
    
    # Previous reference
    previous_state_id: str = ""
    """ID of the preceding state in the revision chain."""
    
    previous_revision: int = 0
    """Revision of the preceding state."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""
    
    @property
    def has_monotonic_gap(self) -> bool:
        """Check if there's a gap in monotonic revision progression."""
        return self.actual_revision != self.expected_revision


@dataclass(frozen=True)
class LineageConsistency:
    """
    Record of lineage consistency for a workspace state.
    
    Ensures that the lineage chain is intact, acyclic, and properly connected
    through transitions.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the lineage chain is consistent."""
    
    # Lineage details
    first_state_id: str = ""
    """ID of the origin state in lineage."""
    
    last_state_id: str = ""
    """ID of the current state in lineage."""
    
    total_transitions: int = 0
    """Total number of transitions in lineage."""
    
    cycle_detected: bool = False
    """Whether a circular reference was detected in lineage."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""


@dataclass(frozen=True)
class DependencyConsistency:
    """
    Record of dependency consistency for a workspace state.
    
    Ensures that all semantic dependencies are satisfied and properly connected
    through the state's lineage.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the dependency chain is consistent."""
    
    # Dependency details
    required_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that must be satisfied."""
    
    satisfied_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that are satisfied."""
    
    missing_dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that are not yet satisfied."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""


@dataclass(frozen=True)
class ProvenanceConsistency:
    """
    Record of provenance consistency for a workspace state.
    
    Ensures that all semantic provenance information is preserved and correctly
    connected through the state's lineage.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the provenance chain is consistent."""
    
    # Provenance details
    source_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of source artifacts referenced in this state."""
    
    provenance_chain_intact: bool = True
    """Whether the provenance chain from source to current is intact."""
    
    missing_provenance: Tuple[str, ...] = field(default_factory=tuple)
    """Provenance information that should be present but is missing."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""


@dataclass(frozen=True)
class OwnershipConsistency:
    """
    Record of ownership consistency for a workspace state.
    
    Ensures that ownership boundaries are preserved and no implicit ownership
    transfers have occurred.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the ownership configuration is consistent."""
    
    # Ownership details
    external_owners: Tuple[str, ...] = field(default_factory=tuple)
    """External owners whose artifacts are referenced."""
    
    implicit_transfers_detected: Tuple[str, ...] = field(default_factory=tuple)
    """Any implicit ownership transfers that would violate boundaries."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""


@dataclass(frozen=True)
class AuthorityConsistency:
    """
    Record of authority consistency for a workspace state.
    
    Ensures that authority boundaries are preserved and no unauthorized actions
    have been recorded in the state's history.
    """
    
    # Consistency result
    is_consistent: bool = True
    """Whether the authority configuration is consistent."""
    
    # Authority details
    authorized_actions: Tuple[str, ...] = field(default_factory=tuple)
    """Actions that are authorized for this state."""
    
    unauthorized_actions_detected: Tuple[str, ...] = field(default_factory=tuple)
    """Any actions that exceeded authority boundaries."""
    
    # Validation
    validated_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""


@dataclass(frozen=True)
class ConsistencyResult:
    """
    Complete consistency result combining all consistency checks.
    
    Captures the overall consistency status of a workspace state.
    """
    
    # Overall status
    is_consistent: bool = True
    """Whether the state passes all consistency checks."""
    
    semantic_consistent: SemanticConsistency = field(default_factory=SemanticConsistency)
    revision_consistent: RevisionConsistency = field(default_factory=RevisionConsistency)
    lineage_consistent: LineageConsistency = field(default_factory=LineageConsistency)
    dependency_consistent: DependencyConsistency = field(default_factory=DependencyConsistency)
    provenance_consistent: ProvenanceConsistency = field(default_factory=ProvenanceConsistency)
    ownership_consistent: OwnershipConsistency = field(default_factory=OwnershipConsistency)
    authority_consistent: AuthorityConsistency = field(default_factory=AuthorityConsistency)
    
    # Validation
    validated_at_utc: float = 0.0
    """When all consistency checks were performed."""
    
    validator_id: str = ""
    """ID of the consistency validator."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "SemanticConsistency",
    "RevisionConsistency",
    "LineageConsistency",
    "DependencyConsistency",
    "ProvenanceConsistency",
    "OwnershipConsistency",
    "AuthorityConsistency",
    "ConsistencyResult",
)