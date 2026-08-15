# Workspace Candidate Models
# ===========================

"""
Immutable candidate models for workspace integration.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
    - Semantic content only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# ID TYPES
# =============================================================================

WorkspaceCandidateId = str
"""Unique identifier for a workspace candidate instance."""

WorkspaceCandidateRevision = int
"""Monotonically increasing revision number for a candidate."""


# =============================================================================
# CANDIDATE KINDS (imported from enums)
# =============================================================================

from .enums import (
    WorkspaceCandidateKind,
    WorkspaceCandidatePurpose,
)


# =============================================================================
# WORKSPACE CANDIDATE CONTENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateContent:
    """
    Immutable semantic content of a workspace candidate.
    
    Content should use canonical semantic structures with typed claims and
    evidence references. Free-form text is optional (for diagnostics).
    
    PROPERTIES:
        • kind: Canonical content category
        • semantic_claims: Typed semantic assertions
        • evidence_references: References to supporting evidence
        • rendering: Optional human-readable rendering for diagnostics
        • factuality: Factuality assessment
        • confidence: Confidence level (0.0 to 1.0)
    """
    
    kind: str
    """Canonical content category."""
    
    semantic_claims: Tuple[str, ...] = field(default_factory=tuple)
    """Typed semantic assertions."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence (e.g., thought IDs)."""
    
    rendering: Optional[str] = None
    """Optional human-readable rendering for diagnostics."""
    
    factuality: Optional[str] = None
    """Factuality assessment (if available)."""
    
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    @classmethod
    def insight(
        cls,
        semantic_claim: str,
        evidence_references: Tuple[str, ...] = (),
        factuality: Optional[str] = None,
        confidence: float = 0.8,
    ) -> WorkspaceCandidateContent:
        """Create an insight content."""
        return cls(
            kind="insight",
            semantic_claims=(semantic_claim,),
            evidence_references=evidence_references,
            factuality=factuality,
            confidence=confidence,
        )
    
    @classmethod
    def concern(
        cls,
        description: str,
        evidence_references: Tuple[str, ...] = (),
        confidence: float = 0.6,
    ) -> WorkspaceCandidateContent:
        """Create a concern content."""
        return cls(
            kind="concern",
            semantic_claims=(description,),
            evidence_references=evidence_references,
            confidence=confidence,
        )


# =============================================================================
# WORKSPACE CANDIDATE ORIGIN
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateOrigin:
    """
    Immutable origin information for a workspace candidate.
    
    Origin tracks where the candidate came from without embedding live objects.
    
    PROPERTIES:
        • originating_network: Network that originated the content
        • originating_package: Package within the network
        • originating_episode_id: Episode that produced or used this content
        • originating_thought_ids: Thoughts that triggered generation
        • originating_product: Source product (if applicable)
        • correlation_id: Correlation ID for tracing
        • causation_id: Causation ID if from another event
        • creation_reason: Why this candidate was created
    """
    
    originating_network: str = "DEFAULT_NETWORK"
    """Network that originated the content."""
    
    originating_package: str = ""
    """Package within the network (e.g., 'reflection', 'simulation')."""
    
    originating_episode_id: Optional[str] = None
    """Episode that produced or used this content."""
    
    originating_thought_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Thoughts that triggered generation."""
    
    originating_product: Optional[str] = None
    """Source product (if applicable)."""
    
    correlation_id: str = ""
    """Correlation ID for distributed tracing."""
    
    causation_id: Optional[str] = None
    """Causation ID if from another event."""
    
    creation_reason: str = "workspace_integration"
    """Why this candidate was created."""
    
    @classmethod
    def from_reflection(
        cls,
        episode_id: str,
        thought_ids: Tuple[str, ...],
        correlation_id: str = "",
    ) -> WorkspaceCandidateOrigin:
        """Create an origin from reflection coordination."""
        return cls(
            originating_network="DEFAULT_NETWORK",
            originating_package="reflection",
            originating_episode_id=episode_id,
            originating_thought_ids=thought_ids,
            correlation_id=correlation_id,
        )
    
    @classmethod
    def from_simulation(
        cls,
        episode_id: str,
        thought_ids: Tuple[str, ...],
        correlation_id: str = "",
    ) -> WorkspaceCandidateOrigin:
        """Create an origin from simulation coordination."""
        return cls(
            originating_network="DEFAULT_NETWORK",
            originating_package="simulation",
            originating_episode_id=episode_id,
            originating_thought_ids=thought_ids,
            correlation_id=correlation_id,
        )


# =============================================================================
# WORKSPACE AUDIENCE RECOMMENDATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceAudienceRecommendation:
    """
    Immutable audience recommendation for a workspace candidate.
    
    This is advisory only. It does not perform actual routing.
    
    PROPERTIES:
        • recommended_audiences: Which consumers should receive this
        • exclude_audiences: Audiences that should NOT receive this
        • minimum_confidence: Minimum confidence for each recipient
    """
    
    recommended_audiences: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds recommended to receive this candidate."""
    
    exclude_audiences: Tuple[str, ...] = field(default_factory=tuple)
    """Audience kinds that should NOT receive this."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence threshold for each recipient."""
    
    @classmethod
    def for_executive_review(cls) -> WorkspaceAudienceRecommendation:
        """Recommend for Executive review."""
        return cls(
            recommended_audiences=("executive",),
            minimum_confidence=0.7,
        )
    
    @classmethod
    def for_general_workspace(cls) -> WorkspaceAudienceRecommendation:
        """Recommend for general workspace availability."""
        return cls(
            recommended_audiences=(
                "working_memory",
                "reasoning",
                "planning",
                "reflection",
            ),
        )


# =============================================================================
# WORKSPACE CANDIDATE VALUE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateValue:
    """
    Immutable value assessment for a workspace candidate.
    
    Value is advisory. It does not determine admission.
    
    PROPERTIES:
        • cognitive_utility: Expected utility for cognition (0.0 to 1.0)
        • relevance_to_objectives: Relevance to active objectives
        • consequence_magnitude: Magnitude of potential consequences
        • uncertainty_reduction: Expected reduction in uncertainty
        • coordination_value: Value for system coordination
        • reuse_value: Expected future reuse value
    """
    
    cognitive_utility: float = 0.5
    """Expected utility for cognition (0.0 to 1.0)."""
    
    relevance_to_objectives: float = 0.5
    """Relevance to active objectives."""
    
    consequence_magnitude: float = 0.5
    """Magnitude of potential consequences."""
    
    uncertainty_reduction: float = 0.5
    """Expected reduction in uncertainty."""
    
    coordination_value: float = 0.5
    """Value for system coordination."""
    
    reuse_value: float = 0.5
    """Expected future reuse value."""
    
    @classmethod
    def high_value(cls) -> WorkspaceCandidateValue:
        """Create a high value assessment."""
        return cls(
            cognitive_utility=0.8,
            relevance_to_objectives=0.9,
            consequence_magnitude=0.7,
            uncertainty_reduction=0.6,
            coordination_value=0.5,
            reuse_value=0.7,
        )
    
    @classmethod
    def low_value(cls) -> WorkspaceCandidateValue:
        """Create a low value assessment."""
        return cls(
            cognitive_utility=0.2,
            relevance_to_objectives=0.3,
            consequence_magnitude=0.1,
            uncertainty_reduction=0.2,
            coordination_value=0.2,
            reuse_value=0.1,
        )


# =============================================================================
# WORKSPACE CANDIDATE RELEVANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateRelevance:
    """
    Immutable relevance assessment for a workspace candidate.
    
    Relevance is distinct from importance and urgency.
    
    PROPERTIES:
        • current_objective_relevance: Relevance to active objectives
        • active_thread_relevance: Relevance to active threads
        • executive_relevance: Relevance to Executive concerns
        • attention_relevance: Relevance to attention mechanisms
        • memory_relevance: Relevance to memory systems
    """
    
    current_objective_relevance: float = 0.5
    """Relevance to active objectives."""
    
    active_thread_relevance: float = 0.5
    """Relevance to active threads."""
    
    executive_relevance: float = 0.5
    """Relevance to Executive concerns."""
    
    attention_relevance: float = 0.5
    """Relevance to attention mechanisms."""
    
    memory_relevance: float = 0.5
    """Relevance to memory systems."""
    
    @classmethod
    def high_relevance(cls) -> WorkspaceCandidateRelevance:
        """Create a high relevance assessment."""
        return cls(
            current_objective_relevance=0.8,
            active_thread_relevance=0.7,
            executive_relevance=0.6,
            attention_relevance=0.5,
            memory_relevance=0.4,
        )


# =============================================================================
# WORKSPACE CANDIDATE URGENCY
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateUrgency:
    """
    Immutable urgency assessment for a workspace candidate.
    
    Urgency is advisory. It must not cause interruption or preempt execution.
    
    PROPERTIES:
        • deadline_proximity: How close to a deadline
        • risk_escalation_potential: Potential for risk escalation
        • opportunity_expiration: Time sensitivity of opportunities
        • blocking_dependency_count: Number of blocked dependencies
    """
    
    deadline_proximity: float = 0.0
    """How close to a deadline (0.0 to 1.0)."""
    
    risk_escalation_potential: float = 0.0
    """Potential for risk escalation."""
    
    opportunity_expiration: float = 0.0
    """Time sensitivity of opportunities."""
    
    blocking_dependency_count: int = 0
    """Number of blocked dependencies."""
    
    @classmethod
    def high_urgency(cls) -> WorkspaceCandidateUrgency:
        """Create a high urgency assessment."""
        return cls(
            deadline_proximity=0.9,
            risk_escalation_potential=0.7,
            opportunity_expiration=0.8,
            blocking_dependency_count=3,
        )
    
    @classmethod
    def low_urgency(cls) -> WorkspaceCandidateUrgency:
        """Create a low urgency assessment."""
        return cls(
            deadline_proximity=0.1,
            risk_escalation_potential=0.0,
            opportunity_expiration=0.0,
            blocking_dependency_count=0,
        )


# =============================================================================
# WORKSPACE CANDIDATE IMPORTANCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateImportance:
    """
    Immutable importance assessment for a workspace candidate.
    
    Importance is distinct from urgency.
    
    PROPERTIES:
        • objective_impact: Impact on objectives
        • commitment_impact: Impact on commitments
        • identity_impact: Impact on identity
        • safety_impact: Safety implications
        • long_term_impact: Long-term consequences
    """
    
    objective_impact: float = 0.5
    """Impact on objectives."""
    
    commitment_impact: float = 0.5
    """Impact on commitments."""
    
    identity_impact: float = 0.5
    """Impact on identity."""
    
    safety_impact: float = 0.0
    """Safety implications."""
    
    long_term_impact: float = 0.5
    """Long-term consequences."""
    
    @classmethod
    def high_importance(cls) -> WorkspaceCandidateImportance:
        """Create a high importance assessment."""
        return cls(
            objective_impact=0.8,
            commitment_impact=0.7,
            identity_impact=0.6,
            safety_impact=0.5,
            long_term_impact=0.9,
        )


# =============================================================================
# WORKSPACE CANDIDATE NOVELTY
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateNovelty:
    """
    Immutable novelty assessment for a workspace candidate.
    
    Novelty rewards new information, not arbitrary variation.
    
    PROPERTIES:
        • difference_from_active_workspace: Difference from active workspace content
        • difference_from_prior_candidates: Difference from prior candidates
        • new_evidence_ratio: Ratio of new to supporting evidence
        • changed_interpretation: Whether interpretation has changed
    """
    
    difference_from_active_workspace: float = 0.0
    """Difference from active workspace content."""
    
    difference_from_prior_candidates: float = 0.0
    """Difference from prior candidates."""
    
    new_evidence_ratio: float = 0.0
    """Ratio of new to supporting evidence."""
    
    changed_interpretation: bool = False
    """Whether interpretation has changed."""
    
    @classmethod
    def high_novelty(cls) -> WorkspaceCandidateNovelty:
        """Create a high novelty assessment."""
        return cls(
            difference_from_active_workspace=0.8,
            difference_from_prior_candidates=0.7,
            new_evidence_ratio=0.6,
            changed_interpretation=True,
        )
    
    @classmethod
    def low_novelty(cls) -> WorkspaceCandidateNovelty:
        """Create a low novelty assessment."""
        return cls(
            difference_from_active_workspace=0.1,
            difference_from_prior_candidates=0.05,
            new_evidence_ratio=0.0,
            changed_interpretation=False,
        )


# =============================================================================
# WORKSPACE CANDIDATE CONFIDENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateConfidence:
    """
    Immutable confidence assessment for a workspace candidate.
    
    Confidence is distinct from value and admission likelihood.
    
    PROPERTIES:
        • source_product_confidence: Confidence in source products
        • evidence_confidence: Confidence in supporting evidence
        • factuality_confidence: Confidence in factuality assessment
        • provenance_quality: Quality of provenance record
    """
    
    source_product_confidence: float = 0.5
    """Confidence in source products."""
    
    evidence_confidence: float = 0.5
    """Confidence in supporting evidence."""
    
    factuality_confidence: float = 0.5
    """Confidence in factuality assessment."""
    
    provenance_quality: float = 0.5
    """Quality of provenance record."""
    
    @classmethod
    def high_confidence(cls) -> WorkspaceCandidateConfidence:
        """Create a high confidence assessment."""
        return cls(
            source_product_confidence=0.8,
            evidence_confidence=0.9,
            factuality_confidence=0.85,
            provenance_quality=0.9,
        )


# =============================================================================
# WORKSPACE CANDIDATE RISK
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateRisk:
    """
    Immutable risk assessment for a workspace candidate.
    
    Risk is assessed across multiple categories.
    
    PROPERTIES:
        • misinterpretation_risk: Risk of misinterpretation (0.0 to 1.0)
        • privacy_risk: Privacy violation risk
        • disclosure_risk: Disclosure control risk
        • false_urgency_risk: False urgency indication
        • factory_confidence_risk: Factory confidence inflation
    """
    
    misinterpretation_risk: float = 0.0
    """Risk of misinterpretation (0.0 to 1.0)."""
    
    privacy_risk: float = 0.0
    """Privacy violation risk."""
    
    disclosure_risk: float = 0.0
    """Disclosure control risk."""
    
    false_urgency_risk: float = 0.0
    """False urgency indication risk."""
    
    factuality_contamination_risk: float = 0.0
    """Factuality contamination risk."""
    
    @classmethod
    def high_risk(cls) -> WorkspaceCandidateRisk:
        """Create a high risk assessment."""
        return cls(
            misinterpretation_risk=0.7,
            privacy_risk=0.5,
            disclosure_risk=0.4,
            false_urgency_risk=0.3,
            factuality_contamination_risk=0.6,
        )
    
    @classmethod
    def low_risk(cls) -> WorkspaceCandidateRisk:
        """Create a low risk assessment."""
        return cls(
            misinterpretation_risk=0.1,
            privacy_risk=0.0,
            disclosure_risk=0.0,
            false_urgency_risk=0.0,
            factuality_contamination_risk=0.0,
        )


# =============================================================================
# WORKSPACE CANDIDATE CONFLICT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateConflict:
    """
    Immutable conflict record for a workspace candidate.
    
    Conflicts must remain visible and cannot be silently merged.
    
    PROPERTIES:
        • kind: Conflict kind (ConflictKind.*)
        • related_candidate_id: ID of the conflicting candidate
        • nature_of_conflict: Description of the conflict
        • resolution_status: Current status (pending, resolved, etc.)
    """
    
    kind: str  # ConflictKind.*
    """The conflict kind."""
    
    related_candidate_id: Optional[str] = None
    """ID of the conflicting candidate (if applicable)."""
    
    nature_of_conflict: str = ""
    """Description of the conflict."""
    
    resolution_status: str = "pending"
    """Current status (pending, resolved, awaiting_resolution, etc.)."""
    
    @classmethod
    def content_conflict(
        cls,
        related_candidate_id: str,
        nature_of_conflict: str = "",
    ) -> WorkspaceCandidateConflict:
        """Create a content conflict record."""
        return cls(
            kind="content_conflict",
            related_candidate_id=related_candidate_id,
            nature_of_conflict=nature_of_conflict or "Content conflicts with another candidate.",
        )


# =============================================================================
# WORKSPACE CANDIDATE LIMITATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidateLimitation:
    """
    Immutable limitation record for a workspace candidate.
    
    Limitations help consumers understand constraints on the candidate.
    
    PROPERTIES:
        • kind: Limitation kind (e.g., 'incomplete_evidence', 'low_confidence')
        • description: Description of the limitation
        • severity: Severity level (minor, moderate, major)
    """
    
    kind: str
    """Limitation kind."""
    
    description: str = ""
    """Description of the limitation."""
    
    severity: str = "moderate"
    """Severity level (minor, moderate, major)."""
    
    @classmethod
    def incomplete_evidence(cls, count: int) -> WorkspaceCandidateLimitation:
        """Create an incomplete evidence limitation."""
        return cls(
            kind="incomplete_evidence",
            description=f"Supporting evidence limited to {count} references.",
            severity="moderate",
        )
    
    @classmethod
    def low_confidence(cls, confidence: float) -> WorkspaceCandidateLimitation:
        """Create a low confidence limitation."""
        return cls(
            kind="low_confidence",
            description=f"Confidence level ({confidence:.2f}) below recommended threshold.",
            severity="major",
        )


# =============================================================================
# WORKSPACE CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceCandidate:
    """
    Immutable workspace candidate model.
    
    A workspace candidate is distinct from admitted workspace content. It is
    a proposal that may deserve evaluation for admission to the shared
    cognitive workspace.
    
    PROPERTIES:
        • candidate_id: Unique identifier for this candidate
        • revision: Current revision number
        • kind: Canonical category of semantic content
        • purpose: Why this candidate is being proposed
        • content: Semantic content
        • origin: Where this candidate came from
        
        • source_product_references: Source products used to create this
        • evidence_references: Supporting evidence references
        • conflicts: Conflicts with other candidates
        
        • audience: Audience recommendation
        • access: Access classification recommendation
        • disclosure: Disclosure classification recommendation
        • lifetime: Lifetime recommendation
        
        • value: Value assessment (advisory)
        • relevance: Relevance assessment
        • urgency: Urgency assessment
        • importance: Importance assessment
        • novelty: Novelty assessment
        • confidence: Confidence assessment
        • risk: Risk assessment
        
        • limitations: Known limitations
        • provenance: Origin tracking
    
    NOT RESPONSIBLE FOR:
        - Admission (external authority)
        - Broadcasting (external infrastructure)
        - Runtime scheduling (ExecutionLoop)
        - Working Memory mutation (Working Memory authority)
    """
    
    # Identity and revisioning
    candidate_id: WorkspaceCandidateId
    """Unique identifier for this candidate."""
    
    revision: WorkspaceCandidateRevision = 1
    """Monotonically increasing revision number."""
    
    # Classification
    kind: str  # WorkspaceCandidateKind.*
    """Canonical category of semantic content."""
    
    purpose: str  # WorkspaceCandidatePurpose.*
    """Why this candidate is being proposed."""
    
    # Content and origin
    content: WorkspaceCandidateContent
    """Semantic content."""
    
    origin: WorkspaceCandidateOrigin
    """Origin information."""
    
    # References
    source_product_references: Tuple[str, ...] = field(default_factory=tuple)
    """Source product reference IDs."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence reference IDs."""
    
    conflicts: Tuple[WorkspaceCandidateConflict, ...] = field(default_factory=tuple)
    """Conflicts with other candidates."""
    
    # Recommendations (advisory, not determinative)
    audience: WorkspaceAudienceRecommendation = field(
        default_factory=WorkspaceAudienceRecommendation
    )
    """Audience recommendation."""
    
    access: str = "internal_general"
    """Access classification recommendation."""
    
    disclosure: str = "internal_only"
    """Disclosure classification recommendation."""
    
    lifetime: str = "transient"
    """Lifetime recommendation."""
    
    # Assessments (advisory)
    value: WorkspaceCandidateValue = field(
        default_factory=WorkspaceCandidateValue
    )
    """Value assessment."""
    
    relevance: WorkspaceCandidateRelevance = field(
        default_factory=WorkspaceCandidateRelevance
    )
    """Relevance assessment."""
    
    urgency: WorkspaceCandidateUrgency = field(
        default_factory=WorkspaceCandidateUrgency
    )
    """Urgency assessment."""
    
    importance: WorkspaceCandidateImportance = field(
        default_factory=WorkspaceCandidateImportance
    )
    """Importance assessment."""
    
    novelty: WorkspaceCandidateNovelty = field(
        default_factory=WorkspaceCandidateNovelty
    )
    """Novelty assessment."""
    
    confidence: WorkspaceCandidateConfidence = field(
        default_factory=WorkspaceCandidateConfidence
    )
    """Confidence assessment."""
    
    risk: WorkspaceCandidateRisk = field(
        default_factory=WorkspaceCandidateRisk
    )
    """Risk assessment."""
    
    # Additional metadata
    limitations: Tuple[WorkspaceCandidateLimitation, ...] = field(default_factory=tuple)
    """Known limitations."""
    
    provenance: str = "canonical"
    """Provenance reference."""
    
    created_at_utc: str = ""
    """When candidate was created (ISO format string for determinism)."""
    
    @classmethod
    def new_insight(
        cls,
        insight_content: WorkspaceCandidateContent,
        origin: WorkspaceCandidateOrigin,
        evidence_references: Tuple[str, ...] = (),
    ) -> WorkspaceCandidate:
        """
        Create a new insight workspace candidate.
        
        Args:
            insight_content: The semantic content of the insight
            origin: Where this insight came from
            evidence_references: Supporting evidence reference IDs
            
        Returns:
            New WorkspaceCandidate with insight classification
        """
        return cls(
            candidate_id=f"candidate_{origin.correlation_id}",
            kind="insight",
            purpose="inform",
            content=insight_content,
            origin=origin,
            source_product_references=evidence_references,
            evidence_references=evidence_references,
            audience=WorkspaceAudienceRecommendation.for_executive_review(),
            access="internal_general",
            disclosure="internal_only",
            lifetime="episode_bound",
        )