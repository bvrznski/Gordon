# Memory Integration Outcomes
# ============================

"""
Immutable outcome models for memory integration episodes.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY INTEGRATION OUTCOME KINDS
# =============================================================================

class MemoryIntegrationOutcomeKind:
    """
    Canonical outcome kinds for memory integration episodes.
    
    Each kind represents a terminal state or result category.
    """
    
    MEMORY_CONTEXT_INTEGRATED = "memory_context_integrated"
    """Memory context successfully integrated."""
    
    ASSOCIATIONS_IDENTIFIED = "associations_identified"
    """Associations between memories identified."""
    
    LINKS_PROPOSED = "links_proposed"
    """Links between memories proposed."""
    
    CLUSTERS_PROPOSED = "clusters_proposed"
    """Clusters of related memories proposed."""
    
    CONFLICTS_IDENTIFIED = "conflicts_identified"
    """Conflicts between memories identified."""
    
    GAPS_IDENTIFIED = "gaps_identified"
    """Gaps in memory coverage identified."""
    
    DUPLICATES_IDENTIFIED = "duplicates_identified"
    """Duplicate memory candidates identified."""
    
    INCONSISTENCIES_IDENTIFIED = "inconsistencies_identified"
    """Inconsistencies in memories identified."""
    
    CONSOLIDATION_PROPOSED = "consolidation_proposed"
    """Consolidation candidates proposed."""
    
    ABSTRACTION_PROPOSED = "abstraction_proposed"
    """Abstraction candidates proposed."""
    
    RETRIEVAL_CUES_PROPOSED = "retrieval_cues_proposed"
    """Retrieval cue proposals generated."""
    
    UPDATE_PROPOSED = "update_proposed"
    """Memory update proposals generated."""
    
    CORRECTION_PROPOSED = "correction_proposed"
    """Memory correction proposals generated."""
    
    RETENTION_REVIEW_PROPOSED = "retention_review_proposed"
    """Retention/de-emphasis proposals generated."""
    
    PARTIALLY_COMPLETED = "partially_completed"
    """Episode completed but with incomplete results."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Not enough context to complete integration."""
    
    INSUFFICIENT_MEMORY_EVIDENCE = "insufficient_memory_evidence"
    """No relevant memory evidence found."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Integration produced no meaningful result."""
    
    UNRESOLVED = "unresolved"
    """Episode ended without resolution."""
    
    FAILED = "failed"
    """Episode failed due to error."""
    
    CANCELLED = "cancelled"
    """Episode was cancelled."""
    
    EXPIRED = "expired"
    """Episode expired (timeout)."""
    
    @classmethod
    def all_outcomes(cls) -> Tuple[str, ...]:
        """Return all valid outcome kinds."""
        return (
            cls.MEMORY_CONTEXT_INTEGRATED,
            cls.ASSOCIATIONS_IDENTIFIED,
            cls.LINKS_PROPOSED,
            cls.CLUSTERS_PROPOSED,
            cls.CONFLICTS_IDENTIFIED,
            cls.GAPS_IDENTIFIED,
            cls.DUPLICATES_IDENTIFIED,
            cls.INCONSISTENCIES_IDENTIFIED,
            cls.CONSOLIDATION_PROPOSED,
            cls.ABSTRACTION_PROPOSED,
            cls.RETRIEVAL_CUES_PROPOSED,
            cls.UPDATE_PROPOSED,
            cls.CORRECTION_PROPOSED,
            cls.RETENTION_REVIEW_PROPOSED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.INSUFFICIENT_MEMORY_EVIDENCE,
            cls.NO_MEANINGFUL_RESULT,
            cls.UNRESOLVED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        )


# =============================================================================
# MEMORY INTEGRATION OUTCOME
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationOutcome:
    """
    Immutable outcome of a memory integration episode.
    
    PROPERTIES:
        • outcome_id: Unique identifier for this outcome
        • kind: Outcome kind (MemoryIntegrationOutcomeKind.*)
        • episode_id: ID of the completed episode
        • products: Generated memory integration products
        • confidence: Confidence in the outcome (0.0 to 1.0)
        • completeness: Completeness classification
        • limitations: Known limitations of this outcome
        • continuation: Next steps recommendation
        • provenance: Provenance reference
        
    IS NOT:
        - A permanent record (can be superseded)
        - An authoritative decision
    """
    
    # Outcome identity
    outcome_id: str
    """Unique identifier for this outcome."""
    
    kind: str  # MemoryIntegrationOutcomeKind.*
    """Outcome kind."""
    
    episode_id: str
    """ID of the completed episode."""
    
    # Products generated
    products: Tuple[str, ...] = field(default_factory=tuple)
    """Generated memory integration products."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence in the outcome (0.0 to 1.0)."""
    
    completeness: str = "unknown"
    """Completeness classification."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this outcome."""
    
    # Next steps
    continuation: str = ""  # Serialized MemoryIntegrationContinuation
    """Next steps recommendation."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    produced_at_utc: str = ""
    """When the outcome was produced (ISO format)."""
    
    @classmethod
    def success(
        cls,
        episode_id: str,
        kind: str,
        confidence: float = 0.7,
        completeness: str = "complete",
    ) -> MemoryIntegrationOutcome:
        """Create a successful outcome."""
        return cls(
            outcome_id=f"outcome_{id(cls)}",
            kind=kind,
            episode_id=episode_id,
            confidence=confidence,
            completeness=completeness,
        )
    
    @classmethod
    def partial(
        cls,
        episode_id: str,
        kind: str,
        limitations: Tuple[str, ...],
        confidence: float = 0.5,
        completeness: str = "partial",
    ) -> MemoryIntegrationOutcome:
        """Create a partial outcome."""
        return cls(
            outcome_id=f"outcome_partial_{id(cls)}",
            kind=kind,
            episode_id=episode_id,
            limitations=limitations,
            confidence=confidence,
            completeness=completeness,
        )
    
    @classmethod
    def insufficient_context(
        cls,
        episode_id: str,
    ) -> MemoryIntegrationOutcome:
        """Create an insufficient context outcome."""
        return cls(
            outcome_id=f"outcome_insufficient_{id(cls)}",
            kind=MemoryIntegrationOutcomeKind.INSUFFICIENT_CONTEXT,
            episode_id=episode_id,
            confidence=0.0,
            completeness="invalid",
            limitations=("context too limited for integration",),
        )
    
    @classmethod
    def no_meaningful_result(
        cls,
        episode_id: str,
    ) -> MemoryIntegrationOutcome:
        """Create a no meaningful result outcome."""
        return cls(
            outcome_id=f"outcome_nomatch_{id(cls)}",
            kind=MemoryIntegrationOutcomeKind.NO_MEANINGFUL_RESULT,
            episode_id=episode_id,
            confidence=0.0,
            completeness="invalid",
            limitations=("no relevant memories found",),
        )
    
    def is_success(self) -> bool:
        """Check if this outcome represents successful completion."""
        return self.kind in {
            MemoryIntegrationOutcomeKind.MEMORY_CONTEXT_INTEGRATED,
            MemoryIntegrationOutcomeKind.ASSOCIATIONS_IDENTIFIED,
            MemoryIntegrationOutcomeKind.LINKS_PROPOSED,
            MemoryIntegrationOutcomeKind.CLUSTERS_PROPOSED,
            MemoryIntegrationOutcomeKind.CONSOLIDATION_PROPOSED,
        }
    
    def is_terminal(self) -> bool:
        """Check if this outcome represents a terminal state."""
        return self.kind in {
            MemoryIntegrationOutcomeKind.FAILED,
            MemoryIntegrationOutcomeKind.CANCELLED,
            MemoryIntegrationOutcomeKind.EXPIRED,
        }


# =============================================================================
# MEMORY INTEGRATION CONTINUATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationContinuation:
    """
    Immutable recommendation for next steps.
    
    A continuation is advisory - it doesn't execute anything itself.
    
    PROPERTIES:
        • kind: Continuation kind (ContinuationKind.*)
        • rationale: Why this continuation is recommended
        • required_resources: Any resources needed
        • confidence: Confidence in the recommendation (0.0 to 1.0)
        • provenance: Provenance reference
        
    IS NOT:
        - A commitment to execute
        - An instruction to runtime systems
    """
    
    # Continuation kind
    kind: str  # ContinuationKind.*
    """Next step recommendation."""
    
    # Details
    rationale: str = ""
    """Why this continuation is recommended."""
    
    required_resources: Tuple[str, ...] = field(default_factory=tuple)
    """Resources needed for continuation."""
    
    confidence: float = 0.5
    """Confidence in the recommendation (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def complete(cls) -> MemoryIntegrationContinuation:
        """Recommend completing integration."""
        return cls(
            kind="complete",
            rationale="integration goals achieved",
            confidence=1.0,
        )
    
    @classmethod
    def request_additional_projection(
        cls,
        memory_kind: str,
    ) -> MemoryIntegrationContinuation:
        """Recommend requesting additional projection."""
        return cls(
            kind="request_additional_projection",
            rationale=f"additional {memory_kind} projections needed",
            confidence=0.8,
        )
    
    @classmethod
    def request_context_refresh(cls) -> MemoryIntegrationContinuation:
        """Recommend refreshing context."""
        return cls(
            kind="request_context_refresh",
            rationale="context may be stale or incomplete",
            confidence=0.7,
        )
    
    @classmethod
    def suspend(cls) -> MemoryIntegrationContinuation:
        """Recommend suspending integration."""
        return cls(
            kind="suspend",
            rationale="awaiting external information or resolution",
            confidence=0.9,
        )