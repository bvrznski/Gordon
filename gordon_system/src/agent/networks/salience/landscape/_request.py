# Salience Network Landscape Request
# ===================================

"""
Canonical Global Salience Landscape request model (Phase 4.8.8).

The LandscapeRequest is an immutable, semantic request to construct a global
salience landscape from evaluated Candidates.

LANDSCAPE REQUEST INVARIANTS:
    LREQ-INV-001: Request is deeply frozen dataclass
    LREQ-INV-002: All inputs are validated subsystem outputs
    LREQ-INV-003: No runtime scheduling or time access
    LREQ-INV-004: Policy is referenced, not executed
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class LandscapePolicy:
    """
    Immutable policy controlling landscape construction.
    
    POLICY INVARIANTS:
        LPOL-INV-001: Policy is immutable (frozen dataclass)
        LPOL-INV-002: All parameters are semantic descriptors
        LPOL-INV-003: No runtime callbacks or execution logic
    """
    
    # Normalization policy
    normalize_activation: bool = True
    """Whether to normalize activation scores."""
    
    activation_scale_min: float = 0.0
    """Minimum activation scale value."""
    
    activation_scale_max: float = 1.0
    """Maximum activation scale value."""
    
    # Baseline adjustment
    auto_adjust_baseline: bool = False
    """Whether to automatically adjust baseline based on environment."""
    
    baseline_reference_level: str = "moderate"
    """
    Reference baseline level for comparison:
        - quiet: Low-activity reference point
        - moderate: Balanced reference point  
        - busy: High-activity reference point
    """
    
    # Aggregation weights
    weight_candidates_equally: bool = True
    """Whether to weight all candidates equally during aggregation."""
    
    urgency_weight: float = 1.0
    """Weight for urgency in aggregate calculations."""
    
    conflict_weight: float = 1.0
    """Weight for conflict in pressure calculations."""
    
    uncertainty_weight: float = 1.0
    """Weight for uncertainty in pressure calculations."""
    
    # Density estimation bounds
    density_normalization_factor: float = 10.0
    """Factor for normalizing density estimates."""
    
    hotspot_threshold: float = 0.7
    """
    Threshold above which a region is considered a hotspot:
        - 0.5: Low threshold (more regions qualify)
        - 0.7: Moderate threshold (balanced detection)
        - 0.9: High threshold (fewer, more intense hotspots)
    """
    
    # Readiness thresholds
    readiness_ready_threshold: float = 0.7
    """Activation level above which system is READY."""
    
    readiness_limited_threshold: float = 0.5
    """Activation level above which system becomes LIMITED."""
    
    # Coherence estimation
    coherence_conflict_weight: float = 2.0
    """Weight for conflicts in coherence calculation."""
    
    coherence_uncertainty_weight: float = 1.5
    """Weight for uncertainty in coherence calculation."""


@dataclass(frozen=True)
class ContextProjection:
    """
    Semantic context projection for landscape interpretation.
    
    CONTEXT INVARIANTS:
        LCTX-INV-001: Context is immutable (frozen dataclass)
        LCTX-INV-002: No runtime references
        LCTX-INV-003: Context provides semantic bias, not evaluation
    """
    
    context_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of active contexts."""
    
    dominant_context: str = field(default="")
    """Primary context for gradient interpretation."""
    
    context_confidence: float = 0.5
    """Confidence in context identification (0-1)."""
    
    # Context gradients
    activity_gradient: Tuple[str, ...] = field(default_factory=tuple)
    """Gradient descriptors indicating activity patterns."""
    
    novelty_gradient: Tuple[str, ...] = field(default_factory=tuple)
    """Gradient descriptors for novelty sensitivity."""
    
    urgency_gradient: Tuple[str, ...] = field(default_factory=tuple)
    """Gradient descriptors for temporal pressure."""
    
    conflict_gradient: Tuple[str, ...] = field(default_factory=tuple)
    """Gradient descriptors for conflict sensitivity."""


@dataclass(frozen=True)
class LandscapeRequest:
    """
    Immutable request for Global Salience Landscape construction.
    
    A request contains all information needed to construct a landscape
    without runtime behavior or scheduling.
    
    LANDSCAPE REQUEST INVARIANTS:
        LREQ-INV-001: Request is deeply frozen dataclass
        LREQ-INV-002: All inputs are validated subsystem outputs
        LREQ-INV-003: No runtime scheduling or time access
        LREQ-INV-004: Policy is referenced, not executed
    """
    
    # Identity for traceability
    identity: str = field(default="")
    """Unique identifier for this request (external supply)."""
    
    # Candidate states (from evaluation layer)
    candidate_states: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of evaluated Candidate State dictionaries.
    
    Each dictionary contains:
        state_identity: Unique candidate identifier
        assessment: Assessment descriptor dictionary
        confidence: Confidence in assessment (0.0-1.0)
        evidence_ids: Evidence supporting this candidate
    """
    
    # Competition result (from competition layer)
    competition_result: dict = field(default_factory=dict)
    """
    Competition result dictionary containing:
        ordered_candidates: Tuple of candidate identities in ranked order
        candidate_ranks: Mapping from identity to rank
        dominance_graph: Dominance relationships
    """
    
    # Adaptive states (from dynamics layer)
    adaptive_states: Tuple[dict, ...] = field(default_factory=tuple)
    """
    Tuple of adaptive state dictionaries.
    
    Each dictionary contains:
        candidate_id: Matching state_identity
        accumulation_level: Current accumulation level
        decay_state: Current decay descriptor
        habituation_level: Current habituation level
    """
    
    # Landscape policy for construction controls
    landscape_policy: LandscapePolicy = field(default_factory=LandscapePolicy)
    """Policy controlling landscape construction."""
    
    # Previous landscape reference (for temporal continuity)
    previous_landscape: dict | None = None
    """
    Reference to previous landscape state.
    
    Contains:
        identity: Previous request identity
        global_activation: Previously estimated activation
        baseline_salience: Previous baseline estimate
        timestamp_delta: Delta since previous landscape
    """
    
    # Context projection (external semantic bias)
    context_projection: ContextProjection = field(default_factory=ContextProjection)
    """Semantic context for gradient interpretation."""
    
    # Provenance tracking
    provenance_source: str = field(default="")
    """Source that generated this request."""
    
    @property
    def candidate_count(self) -> int:
        """Return number of candidates in request."""
        return len(self.candidate_states)
    
    @property
    def has_candidates(self) -> bool:
        """Check if there are any candidates to process."""
        return self.candidate_count > 0
    
    def get_candidate_by_identity(self, identity: str) -> dict | None:
        """
        Retrieve candidate by state identity.
        
        Args:
            identity: State identity to search for
            
        Returns:
            Candidate dictionary or None if not found
        """
        for candidate in self.candidate_states:
            if candidate.get("state_identity") == identity:
                return candidate
        return None
    
    def get_adaptive_by_candidate_id(self, candidate_id: str) -> dict | None:
        """
        Retrieve adaptive state by candidate ID.
        
        Args:
            candidate_id: Candidate identity to search for
            
        Returns:
            Adaptive state dictionary or None if not found
        """
        for adaptive in self.adaptive_states:
            if adaptive.get("candidate_id") == candidate_id:
                return adaptive
        return None
    
    def get_candidate_rank(self, identity: str) -> int | None:
        """
        Retrieve candidate rank from competition result.
        
        Args:
            identity: Candidate identity to search for
            
        Returns:
            Numeric rank (lower = higher priority) or None if not found
        """
        ranks = self.competition_result.get("candidate_ranks", {})
        return ranks.get(identity)