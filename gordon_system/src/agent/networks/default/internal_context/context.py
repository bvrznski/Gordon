# Internal Context Core Model
# ===========================

"""
Canonical InternalContext aggregate model.

InternalContext is an immutable, bounded, revisioned projection of the information
available for one internally generated cognitive coordination episode.

ARCHITECTURAL INVARIANTS:
    DEFAULT-CONTEXT-INV-001: InternalContext is a projection, not an authoritative data store
    DEFAULT-CONTEXT-INV-002: InternalContext is immutable (deeply frozen)
    DEFAULT-CONTEXT-INV-003: InternalContext is bounded (no unbounded growth)
    DEFAULT-CONTEXT-INV-004: Every projection preserves its source owner and revision
    DEFAULT-CONTEXT-INV-005: Context completeness and confidence remain distinct
    DEFAULT-CONTEXT-INV-006: Semantic conflicts are never silently erased
    DEFAULT-CONTEXT-INV-007: InternalContext does not own Working Memory
    DEFAULT-CONTEXT-INV-008: InternalContext does not own persistent Memory
    DEFAULT-CONTEXT-INV-009: InternalContext does not contain live Execution entities
    DEFAULT-CONTEXT-INV-010: InternalContext assembly performs no cognitive algorithm
    DEFAULT-CONTEXT-INV-011: InternalContext assembly performs no runtime scheduling
    DEFAULT-CONTEXT-INV-012: Missing required context is explicit
    DEFAULT-CONTEXT-INV-013: Omitted capacity-overflow content is observable
    DEFAULT-CONTEXT-INV-014: Every context has one explicit purpose and scope
    DEFAULT-CONTEXT-INV-015: Context revision is distinct from source revisions
    DEFAULT-CONTEXT-INV-016: Provider acquisition and context composition remain separable
    DEFAULT-CONTEXT-INV-017: No source projection transfers semantic ownership to DefaultNetwork
    DEFAULT-CONTEXT-INV-018: A partial context must never be represented as complete
    DEFAULT-CONTEXT-INV-019: Context freshness is evaluated against explicit time
    DEFAULT-CONTEXT-INV-020: Package import performs no acquisition or assembly

CANONICAL DEFINITION:
    InternalContext is an immutable, bounded, revisioned projection of the
    agent-relevant information available for one internally generated cognitive
    coordination episode.

    It represents what internally generated cognition currently has available
    to work with - NOT what Gordon permanently believes, not Working Memory,
    not persistent memory, not the active ExecutionThread.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .enums import InternalContextScope


# =============================================================================
# IDENTITY TYPES
# =============================================================================

InternalContextId = str
"""Stable identifier for an internal context instance."""


# =============================================================================
# CONTEXT PROJECTIONS (contracts - implementations provided elsewhere)
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryContextProjection:
    """Projection of memory state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    items: Tuple[str, ...] = field(default_factory=tuple)  # References only, not full records


@dataclass(frozen=True, slots=True)
class IdentityContextProjection:
    """Projection of identity state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    self_model_ref: Optional[str] = None
    active_values: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ObjectiveContextProjection:
    """Projection of objectives without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    items: Tuple[str, ...] = field(default_factory=tuple)  # References only


@dataclass(frozen=True, slots=True)
class CommitmentContextProjection:
    """Projection of commitments without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    items: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class NarrativeContextProjection:
    """Projection of narrative state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    active_themes: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class PredictiveContextProjection:
    """Projection of predictive state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    active_predictions: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class WorkspaceContextProjection:
    """Projection of workspace state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    broadcast_summary: Optional[str] = None


@dataclass(frozen=True, slots=True)
class WorkingMemoryContextProjection:
    """Projection of working memory without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    items: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ExecutionContextProjection:
    """Projection of execution state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    active_thread_ref: Optional[str] = None


@dataclass(frozen=True, slots=True)
class AttentionContextProjection:
    """Projection of attention state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    focused_targets: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AffectContextProjection:
    """Projection of affective state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    valence: Optional[float] = None  # -1.0 to 1.0


@dataclass(frozen=True, slots=True)
class ConcernContextProjection:
    """Projection of concerns without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    unresolved_items: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ResourceContextProjection:
    """Projection of resource state without ownership."""
    projection_id: str
    source_revision: int
    captured_at_utc: datetime
    confidence: float
    computational_pressure: Optional[float] = None  # 0.0 to 1.0


# =============================================================================
# COMPOSITION MODELS
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalContextCompleteness:
    """
    Structured completeness assessment for internal context.
    
    Completeness is distinct from confidence:
        • Complete = all required projections present with sufficient content
        • High confidence = strong supporting evidence (even if partial)
    """
    
    status: str  # ContextCompleteness.*
    required_count: int
    supplied_required_count: int
    missing_required_kinds: Tuple[str, ...]
    optional_supplied_count: int
    incomplete_details: Tuple[str, ...] = field(default_factory=tuple)
    overall_score: float = 1.0
    
    @classmethod
    def complete(cls) -> InternalContextCompleteness:
        """Create a completeness record for a complete context."""
        return cls(
            status="complete",
            required_count=0,
            supplied_required_count=0,
            missing_required_kinds=(),
            optional_supplied_count=0,
            overall_score=1.0,
        )
    
    @classmethod
    def insufficient(cls, missing: Tuple[str, ...]) -> InternalContextCompleteness:
        """Create a completeness record for an insufficient context."""
        return cls(
            status="insufficient",
            required_count=len(missing),
            supplied_required_count=0,
            missing_required_kinds=missing,
            optional_supplied_count=0,
            overall_score=0.0,
        )


@dataclass(frozen=True, slots=True)
class InternalContextConfidence:
    """
    Structured confidence assessment for internal context.
    
    Confidence measures evidential quality, not truth. High confidence means
    strong supporting evidence; low confidence means weak or conflicting evidence.
    """
    
    overall_confidence: float  # 0.0 to 1.0
    confidence_justification: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def high(cls) -> InternalContextConfidence:
        """Create a high-confidence record."""
        return cls(overall_confidence=0.85, confidence_justification=("Strong evidence base",))
    
    @classmethod
    def low(cls) -> InternalContextConfidence:
        """Create a low-confidence record."""
        return cls(overall_confidence=0.25, confidence_justification=("Weak or conflicting evidence",))


@dataclass(frozen=True, slots=True)
class InternalContextFreshness:
    """
    Structured freshness assessment for internal context.
    
    Freshness evaluates temporal relevance without wall-clock access during
    assembly (uses injected time).
    """
    
    status: str  # ContextFreshness.*
    oldest_projection_age_seconds: float = 0.0
    newest_projection_age_seconds: float = 0.0
    stale_projections: Tuple[str, ...] = field(default_factory=tuple)
    freshness_score: float = 1.0
    
    @classmethod
    def fresh(cls) -> InternalContextFreshness:
        """Create a fresh context record."""
        return cls(
            status="fresh",
            oldest_projection_age_seconds=0.0,
            newest_projection_age_seconds=0.0,
            stale_projections=(),
            freshness_score=1.0,
        )


@dataclass(frozen=True, slots=True)
class ContextConflictId:
    """Unique identifier for a conflict record."""
    value: str


@dataclass(frozen=True, slots=True)
class InternalContextConflict:
    """
    Record of a semantic conflict detected during context assembly.
    
    Conflicts are NEVER silently resolved. They are recorded and may influence
    confidence or completeness assessment.
    """
    
    conflict_id: ContextConflictId
    category: str  # ContextConflictCategory.*
    description: str
    severity: str  # "blocking" or "non-blocking"
    resolution_status: str = "unresolved"  # "unresolved", "acknowledged", "deferred"
    
    @classmethod
    def blocking(cls, category: str, description: str) -> InternalContextConflict:
        """Create a blocking conflict."""
        return cls(
            conflict_id=ContextConflictId(value=f"conflict_{id(category)}"),
            category=category,
            description=description,
            severity="blocking",
        )
    
    @classmethod
    def non_blocking(cls, category: str, description: str) -> InternalContextConflict:
        """Create a non-blocking conflict."""
        return cls(
            conflict_id=ContextConflictId(value=f"conflict_{id(category)}"),
            category=category,
            description=description,
            severity="non-blocking",
        )


@dataclass(frozen=True, slots=True)
class InternalContextProvenance:
    """
    Complete provenance for an internal context.
    
    Bounded record of how the context was assembled, including source
    projection references and assembly metadata.
    """
    
    request_id: str
    captured_at_utc: datetime
    assembler_version: str = "1.0.0"
    configuration_hash: Optional[str] = None
    total_source_projections: int = 0


# =============================================================================
# MAIN AGGREGATE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalContext:
    """
    Immutable canonical aggregate for internal cognitive coordination.
    
    This is the main contract that downstream systems consume. It contains
    projections from external owners without ownership transfer.
    
    ARCHITECTURAL INVARIANTS ENFORCED:
        • Immutable (frozen dataclass with tuples)
        • Bounded (no unbounded collections)
        • Revisioned (revision number + source revisions preserved)
        • Purpose-specific (explicit purpose and scope)
        • Projection-based (no ownership transfer)
        • Conflict-aware (conflicts explicitly recorded)
    
    PROPERTIES:
        • context_id: Unique identifier for this context instance
        • revision: Context-level revision number (changes when content changes)
        • created_at: When this context was assembled
        
    CONTENT PROJECTIONS:
        All projections preserve source ownership and revisions. The DefaultNetwork
        reads from these but does not own or modify the underlying data.
        
    COMPOSITION METADATA:
        • unresolved_conflicts: Conflicts detected during assembly (never silently resolved)
        • missing_requirements: Required projections that were unavailable
        • confidence: Quality assessment of the context content
        • completeness: Completeness assessment relative to purpose requirements
        • freshness: Temporal relevance assessment
        • provenance: Assembly metadata and source tracking
    
    NOT RESPONSIBLE FOR:
        • Executing reflection, imagination, simulation, etc.
        • Updating memory, identity, or other source data
        • Scheduling runtime execution
        • Allocating computational resources
    """
    
    # Identity and revisioning
    context_id: InternalContextId
    revision: int
    created_at_utc: datetime
    
    # Purpose and scope (defining constraints)
    purpose: str  # InternalContextPurpose.*
    scope: InternalContextScope
    
    # Content projections (immutable tuples of references/summaries only)
    objectives: Optional[ObjectiveContextProjection] = None
    commitments: Optional[CommitmentContextProjection] = None
    memory: Optional[MemoryContextProjection] = None
    identity: Optional[IdentityContextProjection] = None
    narrative: Optional[NarrativeContextProjection] = None
    prediction: Optional[PredictiveContextProjection] = None
    workspace: Optional[WorkspaceContextProjection] = None
    working_memory: Optional[WorkingMemoryContextProjection] = None
    execution: Optional[ExecutionContextProjection] = None
    attention: Optional[AttentionContextProjection] = None
    affect: Optional[AffectContextProjection] = None
    concerns: Optional[ConcernContextProjection] = None
    resources: Optional[ResourceContextProjection] = None
    
    # Composition metadata (never silently erased)
    unresolved_conflicts: Tuple[InternalContextConflict, ...] = field(default_factory=tuple)
    missing_requirements: Tuple[str, ...] = field(default_factory=tuple)  # projection kinds
    confidence: InternalContextConfidence = field(default_factory=InternalContextConfidence.high)
    completeness: InternalContextCompleteness = field(default_factory=InternalContextCompleteness.complete)
    freshness: InternalContextFreshness = field(default_factory=InternalContextFreshness.fresh)
    provenance: InternalContextProvenance = field(default_factory=lambda: InternalContextProvenance(request_id=""))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def is_internal_context(value: object) -> bool:
    """Check if a value is an InternalContext instance."""
    return isinstance(value, InternalContext)


def context_revision_key(context: InternalContext) -> str:
    """
    Generate a revision key for cache lookup.
    
    The key combines context_id and revision to enable efficient
    caching and invalidation without storing full contexts.
    """
    return f"{context.context_id}:{context.revision}"