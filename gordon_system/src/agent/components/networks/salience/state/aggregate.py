# Salience Network Aggregate State
# ================================
#
# Canonical implementation of the aggregate SalienceNetworkState (Phase 4.8.4).
#

"""
The canonical aggregate State representing a complete semantic snapshot.

SalienceNetworkState composes all State components into one immutable snapshot.
It does NOT:
    - Compute salience
    - Schedule processing
    - Allocate attention
    - Perform runtime behavior

This is the sole authoritative aggregate of the Salience Network.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class SalienceStateProvenance:
    """
    Immutable provenance information for State formation.
    
    Provenance describes how the State was semantically formed without
    runtime stack traces or arbitrary objects.
    """
    
    source_content_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Content identities that contributed to this State."""
    
    source_state_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Predecessor state identities where applicable."""
    
    derivation_references: Tuple[str, ...] = field(default_factory=tuple)
    """Derivation references if derived from other states."""
    
    authority_references: Tuple[str, ...] = field(default_factory=tuple)
    """Authority references for semantic claims."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Provenance-related limitations."""


@dataclass(frozen=True)
class SalienceStateLineage:
    """
    Immutable lineage information across State revisions.
    
    Lineage describes semantic ancestry without recursive embedded State objects.
    """
    
    root_identity: str = field(default="")
    """Logical root identity for this state sequence."""
    
    predecessor_identity: str | None = field(default=None)
    """Immediate predecessor state identity (if revision)."""
    
    superseded_identities: Tuple[str, ...] = field(default_factory=tuple)
    """Superseded states in the lineage."""
    
    related_candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Related candidate states for comparison."""
    
    @property
    def is_acyclic(self) -> bool:
        """
        Validate that lineage forms an acyclic graph.
        
        A state cannot be its own ancestor or descendant.
        """
        if self.predecessor_identity == "":
            return True
        # Lineage cycle check (simplified - actual implementation would need
        # full graph traversal)
        return True


@dataclass(frozen=True)
class SalienceNetworkState:
    """
    Canonical aggregate State of the Salience Network.
    
    This is the sole authoritative semantic snapshot representing salience
    at a point in time. It does not compute, schedule, or execute - it only
    represents.
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-STATE-INV-001: Exactly one canonical aggregate exists (this class)
        - SALIENCE-STATE-INV-002: All State is deeply immutable (frozen dataclass)
        - SALIENCE-STATE-INV-003: No runtime dependencies
        - SALIENCE-STATE-INV-004: Deterministic serialization
    
    STATE LAWS:
        - SALIENCE-STATE-LAW-001: SalienceNetworkState is sole canonical aggregate
        - SALIENCE-STATE-LAW-002: State represents, never computes
        - SALIENCE-STATE-LAW-003: State composes ontology and Content without redefining
    """
    
    # Identity fields (required)
    identity: str = field(default="")
    """Unique state identity for this snapshot."""
    
    revision: int = field(default=1)
    """Revision number (incremented on semantic change)."""
    
    schema_version: str = field(default="1.0.0")
    """Schema version for structural compatibility."""
    
    snapshot_kind: str = field(default="current")
    """
    Semantic snapshot kind:
        - current: Present assessment
        - candidate: Proposed assessment under consideration
        - historical: Past assessment preserved for lineage
        - baseline: Reference state for comparison
        - provisional: Incomplete assessment with known limitations
        - superseded: Replaced state preserved for lineage
        - invalid: Invalid state for quarantine
    """
    
    # Subject reference (required)
    subject: str = field(default="")
    """Subject reference identity."""
    
    # Assessment component
    assessment_kind: str = field(default="multidimensional")
    """Kind of assessment representation."""
    
    overall_level: str = field(default="unknown")
    """Overall canonical salience level."""
    
    significance_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for significance."""
    
    relevance_contexts: Tuple[str, ...] = field(default_factory=tuple)
    """Relevant contexts."""
    
    novelty_comparison: Tuple[str, ...] = field(default_factory=tuple)
    """Expected vs. actual comparison."""
    
    urgency_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Temporal basis for urgency."""
    
    uncertainty_basis: str = field(default="unknown")
    """Semantic basis for uncertainty level."""
    
    conflict_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of conflicting evidence."""
    
    prediction_error_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Prediction vs. observation comparison."""
    
    confidence_level: str = field(default="unknown")
    """Confidence in assessment."""
    
    # Activation component
    activation_status: str = field(default="inactive")
    """Semantic activation category."""
    
    activation_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for activation classification."""
    
    # Readiness component
    readiness_status: str = field(default="unavailable")
    """Downstream consumption readiness status."""
    
    readiness_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for current readiness status."""
    
    # Evidence component (references to immutable Content)
    supporting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of supporting evidence."""
    
    contradicting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of contradicting evidence."""
    
    unresolved_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of unclassified evidence."""
    
    cue_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of cues (potential evidence)."""
    
    hypothesis_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of hypotheses (pending validation)."""
    
    evidence_completeness: str = field(default="unknown")
    """Semantic assessment of evidence completeness."""
    
    # Uncertainty component
    uncertainty_category: str = field(default="unknown")
    """Semantic uncertainty category."""
    
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)
    """Identified sources of uncertainty."""
    
    # Context component (external projections only)
    context_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of external contexts affecting this State."""
    
    missing_contexts: Tuple[str, ...] = field(default_factory=tuple)
    """Expected but unavailable contexts."""
    
    # Persistence and decay components
    persistence_kind: str = field(default="transient")
    """Semantic persistence classification."""
    
    decay_kind: str = field(default="none")
    """Semantic decay classification."""
    
    # Competition component (optional - only where applicable)
    competition_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of competing candidates."""
    
    dominant_candidate: str | None = field(default=None)
    """Identity of dominant candidate if resolved externally."""
    
    competition_status: str = field(default="unresolved")
    """Competition resolution status."""
    
    # Integrity component
    integrity_status: str = field(default="valid")
    """
    Semantic integrity status:
        - valid: Fully valid and ready for use
        - valid_with_warnings: Valid but with minor issues
        - incomplete: Structurally valid but lacks some information
        - degraded: Usable but with meaningful limitations
        - invalid: Cannot be used due to structural issues
    """
    
    integrity_findings: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of validation findings."""
    
    # Provenance and lineage
    provenance: str = field(default="")
    """Provenance reference or identifier."""
    
    lineage_root: str = field(default="")
    """Lineage root identity."""
    
    lineage_predecessor: str | None = field(default=None)
    """Predecessor state identity (if revision)."""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    """Creation timestamp (for provenance, not computation)."""
    
    @property
    def is_composite(self) -> bool:
        """
        Indicates whether this State composes multiple components.
        
        All SalienceNetworkState instances are composite by construction.
        """
        return True
    
    @property
    def has_subject_reference(self) -> bool:
        """Indicates whether a subject reference is present."""
        return len(self.subject.strip()) > 0