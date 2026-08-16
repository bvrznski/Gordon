# Internal Thought Core Model
# ===========================

"""
Canonical InternalThought aggregate model.

InternalThought is an immutable, bounded, revisioned semantic object representing one
internally generated cognitive product (thought).

ARCHITECTURAL INVARIANTS:
    THOUGHT-INV-001: Thoughts are semantic objects (not language)
    THOUGHT-INV-002: Thoughts are immutable (deeply frozen)
    THOUGHT-INV-003: Thoughts never execute behaviour
    THOUGHT-INV-004: Thought generation never invokes Executive
    THOUGHT-INV-005: Thought generation never schedules Threads
    THOUGHT-INV-006: Thoughts belong exclusively to the Default Network
    THOUGHT-INV-007: Every thought has provenance
    THOUGHT-INV-008: Every thought belongs to an InternalEpisode
    THOUGHT-INV-009: Thoughts remain bounded
    THOUGHT-INV-010: Relationships remain typed

CANONICAL DEFINITION:
    InternalThought is an immutable, bounded, revisioned semantic object representing
    one internally generated cognitive product.

    It represents what internally generated cognition currently has available to work 
    with - NOT what Gordon permanently believes, not Working Memory, not persistent 
    memory, not the active ExecutionThread.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


# =============================================================================
# IDENTITY TYPES
# =============================================================================

InternalThoughtId = str
"""Stable identifier for an internal thought instance."""

InternalThoughtRevision = int
"""Immutable revision number for a thought instance."""


# =============================================================================
# LIFECYCLE STATES - Semantic states (not runtime)
# =============================================================================

class LifecycleState:
    """
    Canonical lifecycle states for internal thoughts.
    
    These represent semantic coordination state, NOT runtime execution state.
    Core and Execution handle actual runtime mechanics.
    """
    
    # Pre-active states
    GENERATED = "generated"
    """Thought has been generated but not yet validated."""
    
    VALIDATED = "validated"
    """Thought has passed validation checks."""
    
    ACTIVE = "active"
    """Thought is available for consideration by consumers."""
    
    # Post-active states
    REFERENCED = "referenced"
    """Thought has been referenced by a consumer process."""
    
    SUPERSEDED = "superseded"
    """Newer revision or alternative thought replaced this one."""
    
    ARCHIVED = "archived"
    """Thought is preserved but no longer actively considered."""
    
    DISCARDED = "discarded"
    """Thought was explicitly rejected or invalid."""
    
    INVALID = "invalid"
    """Thought failed validation and is invalid."""
    
    @classmethod
    def is_pre_active(cls, state: str) -> bool:
        """Check if state is pre-active (before active consideration)."""
        return state in {cls.GENERATED, cls.VALIDATED}
    
    @classmethod
    def is_active(cls, state: str) -> bool:
        """Check if state is active (currently being considered)."""
        return state in {cls.ACTIVE, cls.REFERENCED}
    
    @classmethod
    def is_terminal(cls, state: str) -> bool:
        """Check if state is terminal (no further transitions expected)."""
        return state in {cls.SUPERSEDED, cls.ARCHIVED, cls.DISCARDED, cls.INVALID}


# =============================================================================
# RELATIONSHIP KINDS - Typed semantic relationships between thoughts
# =============================================================================

class RelationshipKind:
    """
    Typed categories of semantic relationships between thoughts.
    
    Each relationship kind describes a specific semantic connection that may
    exist between two thought instances.
    """
    
    # Supportive relationships
    SUPPORTS = "supports"
    """Thought supports the validity or truth of another."""
    
    EXTENDS = "extends"
    """Thought extends or builds upon another thought."""
    
    REFINES = "refines"
    """Thought provides a more detailed version of another."""
    
    MERGES = "merges"
    """Thought merges multiple sources into one."""
    
    SPECIALIZES = "specializes"
    """Thought is a more specific case of another."""
    
    # Contradictory relationships
    CONTRADICTS = "contradicts"
    """Thought contradicts or negates another."""
    
    INVALIDATES = "invalidates"
    """Thought shows another thought to be invalid."""
    
    # Question/answer relationships
    ANSWERS = "answers"
    """Thought answers a question posed by another."""
    
    QUESTIONS = "questions"
    """Thought questions or challenges another."""
    
    # Abstract/concrete relationships
    ABSTRACTS = "abstracts"
    """Thought is an abstraction of another."""
    
    GENERALIZES = "generalizes"
    """Thought generalizes from more specific instances."""
    
    # Causal/dependency relationships
    CAUSES = "causes"
    """Thought describes or implies a cause-effect relationship."""
    
    PREDICTS = "predicts"
    """Thought predicts outcomes of another thought."""
    
    EXPLAINS = "explains"
    """Thought provides explanation for another."""
    
    DEPENDS_ON = "depends_on"
    """Thought depends on the validity of another."""
    
    # Contextual relationships
    CONTEXT_OF = "context_of"
    """Thought provides context for another."""
    
    DERIVES_FROM = "derives_from"
    """Thought derives from another thought."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid relationship kind values."""
        return (
            cls.SUPPORTS,
            cls.EXTENDS,
            cls.REFINES,
            cls.MERGES,
            cls.SPECIALIZES,
            cls.CONTRADICTS,
            cls.INVALIDATES,
            cls.ANSWERS,
            cls.QUESTIONS,
            cls.ABSTRACTS,
            cls.GENERALIZES,
            cls.CAUSES,
            cls.PREDICTS,
            cls.EXPLAINS,
            cls.DEPENDS_ON,
            cls.CONTEXT_OF,
            cls.DERIVES_FROM,
        )
    
    @classmethod
    def is_symmetric(cls, kind: str) -> bool:
        """Check if relationship kind is symmetric (bidirectional)."""
        return kind in {cls.MERGES}
    
    @classmethod
    def is_supportive(cls, kind: str) -> bool:
        """Check if relationship kind is supportive."""
        return kind in {
            cls.SUPPORTS,
            cls.EXTENDS,
            cls.REFINES,
            cls.MERGES,
            cls.SPECIALIZES,
            cls.ANSWERS,
            cls.ABSTRACTS,
            cls.GENERALIZES,
            cls.EXPLAINS,
            cls.DEPENDS_ON,
        }
    
    @classmethod
    def is_contradictory(cls, kind: str) -> bool:
        """Check if relationship kind is contradictory."""
        return kind in {cls.CONTRADICTS, cls.INVALIDATES}


# =============================================================================
# ASSESSMENT METRICS - Quality evaluation dimensions
# =============================================================================

@dataclass(frozen=True, slots=True)
class ThoughtAssessmentMetrics:
    """
    Immutable quantitative measurements for a thought's quality.
    
    These metrics are advisory - they do not determine validity but provide
    guidance for consumers evaluating thoughts.
    """
    
    # Core confidence measure (0.0 to 1.0)
    confidence: float = 0.5
    
    # Semantic novelty measure (0.0 to 1.0)
    novelty: float = 0.0
    
    # Expected utility for decision making (0.0 to 1.0)
    expected_utility: float = 0.0
    
    # Relevance to current context (0.0 to 1.0)
    relevance: float = 0.5
    
    # Consistency with known facts (0.0 to 1.0)
    consistency: float = 0.5
    
    # Coherence with existing models (0.0 to 1.0)
    coherence: float = 0.5
    
    # Risk assessment (0.0 low risk to 1.0 high risk)
    risk: float = 0.0
    
    # Urgency for consideration (0.0 to 1.0)
    urgency: float = 0.0


# =============================================================================
# PROVENANCE - Origin tracking
# =============================================================================

@dataclass(frozen=True, slots=True)
class ThoughtProvenance:
    """
    Immutable record of thought origin and history.
    
    Provenance tracks where a thought came from without embedding implementation
    details or live objects.
    """
    
    # Origin identity
    originating_episode_id: str
    """The InternalEpisode that produced this thought."""
    
    originating_context_version: str
    """Version of context at generation time."""
    
    generator_type: str
    """Type of generator that created the thought (e.g., 'reflection', 'simulation')."""
    
    # Timestamps
    generated_at_utc: datetime
    """When thought was first generated."""
    
    validated_at_utc: Optional[datetime] = None
    """When thought passed validation (if applicable)."""
    
    # Configuration state
    configuration_hash: str = ""
    """Hash of configuration used for generation reproducibility."""
    
    # Version tracking
    initial_revision: InternalThoughtRevision = 1
    
    @classmethod
    def new(
        cls,
        originating_episode_id: str,
        originating_context_version: str,
        generator_type: str,
    ) -> ThoughtProvenance:
        """Create a new provenance record."""
        return cls(
            originating_episode_id=originating_episode_id,
            originating_context_version=originating_context_version,
            generator_type=generator_type,
            generated_at_utc=datetime.utcnow(),
            validated_at_utc=None,
            configuration_hash="",
            initial_revision=1,
        )


# =============================================================================
# INTERNAL THOUGHT - Core model
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalThought:
    """
    Immutable semantic object representing one internally generated cognitive product.
    
    An InternalThought is NOT:
        - Language or text (language generation happens later if needed)
        - Chain-of-Thought reasoning
        - An LLM prompt
        - An execution request
        - A runtime command
    
    An InternalThought IS:
        - A structured semantic object with bounded content
        - Immutable (deeply frozen for safety and determinism)
        - Revisioned (immutable revision history preserved)
        - Explainable (provenance, confidence, relationships documented)
        - Typed (specific kind determines interpretation)
    
    ARCHITECTURAL ROLE:
        The Default Network generates thoughts as semantic candidates that may
        later be evaluated, reflected upon, simulated, integrated, remembered,
        or discarded by other components. Thought generation never executes.
    
    THOUGHT OWNERSHIP:
        Thoughts own:
            - Semantic meaning (the core concept)
            - Generation purpose (why this thought exists)
            - Originating episode (source of context)
            - Originating context (environment at generation)
            - Relationships (connections to other thoughts)
            - Confidence (certainty level)
            - Novelty (uniqueness measure)
            - Expected utility (decision-making value)
            - Provenance (origin tracking)
            - Lifecycle state
            - Revision history
        
        Thoughts never own:
            - Runtime execution
            - Scheduling decisions
            - Thread state
            - Loop state
            - Cycle progression
            - External communication
            - Transport mechanisms
            - Capability execution
    
    BOUNDEDNESS REQUIREMENTS:
        All content must be bounded by explicit limits. No unbounded growth,
        infinite recursion, or arbitrary expansion.
    """
    
    # Identity (stable across revisions)
    thought_id: InternalThoughtId
    """Unique identifier for this thought instance."""
    
    # Semantic kind (determines interpretation)
    thought_kind: str
    """Canonical category of cognition (e.g., 'reflection', 'hypothesis')."""
    
    # Core semantic content (bounded representation)
    concept: str
    """The core semantic concept (not language, not reasoning)."""
    
    purpose: str
    """The cognitive purpose or intent of this thought."""
    
    # Origin and provenance
    provenance: ThoughtProvenance
    """Origin tracking without live objects."""
    
    originating_episode_id: Optional[str] = None
    """Reference to the episode that triggered generation."""
    
    originating_context_version: str = ""
    """Context version reference at generation time."""
    
    # Assessment metrics (advisory, not determinative)
    assessment: ThoughtAssessmentMetrics = field(
        default_factory=ThoughtAssessmentMetrics
    )
    
    # Lifecycle state (semantic, not runtime)
    lifecycle_state: str = LifecycleState.GENERATED
    
    # Relationships to other thoughts
    relationships: Tuple[str, ...] = field(default_factory=tuple)
    """Relationship IDs (not full relationship objects)."""
    
    # Revision tracking
    revision: InternalThoughtRevision = 1
    
    # Serialization-ready metadata
    serialized_at_utc: Optional[datetime] = None
    """When thought was last serialized (for traceability)."""
    
    @classmethod
    def new(
        cls,
        concept: str,
        purpose: str,
        thought_kind: str,
        originating_episode_id: str,
        originating_context_version: str,
        generator_type: str = "default",
    ) -> InternalThought:
        """
        Create a new internally generated thought.
        
        This is the primary constructor for thoughts. All thoughts should
        be created through this method or ThoughtFactory to ensure
        consistent initialization and validation.
        
        Args:
            concept: The core semantic concept (bounded representation)
            purpose: The cognitive purpose of this thought
            thought_kind: Canonical category of cognition
            originating_episode_id: ID of the episode triggering generation
            originating_context_version: Context version reference
            generator_type: Type of generator creating this thought
            
        Returns:
            New InternalThought instance with valid provenance
        """
        thought_id = f"thought:{uuid4().hex[:24]}"
        
        return cls(
            thought_id=thought_id,
            thought_kind=thought_kind,
            concept=concept,
            purpose=purpose,
            provenance=ThoughtProvenance.new(
                originating_episode_id=originating_episode_id,
                originating_context_version=originating_context_version,
                generator_type=generator_type,
            ),
            originating_episode_id=originating_episode_id,
            originating_context_version=originating_context_version,
            revision=1,
        )
    
    def with_revision(self, new_concept: str) -> InternalThought:
        """
        Create a new revision of this thought.
        
        Revisions preserve:
            - Original provenance
            - Relationship history (as references)
            - Semantic continuity
            
        But produce a new identity. This is how we maintain immutability
        while allowing for thought evolution.
        
        Args:
            new_concept: The updated semantic content
            
        Returns:
            New InternalThought with incremented revision
        """
        # Note: In practice, revision handling would be managed by
        # InternalThoughtRevision system. This is a simplified version.
        return InternalThought(
            thought_id=f"{self.thought_id}-r{self.revision + 1}",
            thought_kind=self.thought_kind,
            concept=new_concept,
            purpose=self.purpose,
            provenance= ThoughtProvenance(
                originating_episode_id=self.provenance.originating_episode_id,
                originating_context_version=self.provenance.originating_context_version,
                generator_type=self.provenance.generator_type,
                generated_at_utc=self.provenance.generated_at_utc,
                validated_at_utc=self.provenance.validated_at_utc,
                configuration_hash=self.provenance.configuration_hash,
                initial_revision=self.revision + 1,
            ),
            originating_episode_id=self.originating_episode_id,
            originating_context_version=self.originating_context_version,
            assessment=self.assessment,
            lifecycle_state=self.lifecycle_state,
            relationships=self.relationships,
            revision=self.revision + 1,
        )
    
    def with_lifecycle(self, new_state: str) -> InternalThought:
        """Update the lifecycle state of this thought."""
        return InternalThought(
            thought_id=self.thought_id,
            thought_kind=self.thought_kind,
            concept=self.concept,
            purpose=self.purpose,
            provenance=self.provenance,
            originating_episode_id=self.originating_episode_id,
            originating_context_version=self.originating_context_version,
            assessment=self.assessment,
            lifecycle_state=new_state,
            relationships=self.relationships,
            revision=self.revision,
        )
    
    def with_assessment(self, metrics: ThoughtAssessmentMetrics) -> InternalThought:
        """Update assessment metrics for this thought."""
        return InternalThought(
            thought_id=self.thought_id,
            thought_kind=self.thought_kind,
            concept=self.concept,
            purpose=self.purpose,
            provenance=self.provenance,
            originating_episode_id=self.originating_episode_id,
            originating_context_version=self.originating_context_version,
            assessment=metrics,
            lifecycle_state=self.lifecycle_state,
            relationships=self.relationships,
            revision=self.revision,
        )
    
    def with_relationship(self, relationship_kind: str, target_thought_id: str) -> InternalThought:
        """Add a relationship to this thought."""
        # Format: "kind:target_id"
        new_relation = f"{relationship_kind}:{target_thought_id}"
        return InternalThought(
            thought_id=self.thought_id,
            thought_kind=self.thought_kind,
            concept=self.concept,
            purpose=self.purpose,
            provenance=self.provenance,
            originating_episode_id=self.originating_episode_id,
            originating_context_version=self.originating_context_version,
            assessment=self.assessment,
            lifecycle_state=self.lifecycle_state,
            relationships=(*self.relationships, new_relation),
            revision=self.revision,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize thought to dictionary representation."""
        return {
            "thought_id": self.thought_id,
            "thought_kind": self.thought_kind,
            "concept": self.concept,
            "purpose": self.purpose,
            "provenance": {
                "originating_episode_id": self.provenance.originating_episode_id,
                "originating_context_version": self.provenance.originating_context_version,
                "generator_type": self.provenance.generator_type,
                "generated_at_utc": self.provenance.generated_at_utc.isoformat() if self.provenance.generated_at_utc else None,
                "validated_at_utc": self.provenance.validated_at_utc.isoformat() if self.provenance.validated_at_utc else None,
                "configuration_hash": self.provenance.configuration_hash,
                "initial_revision": self.provenance.initial_revision,
            },
            "originating_episode_id": self.originating_episode_id,
            "originating_context_version": self.originating_context_version,
            "assessment": {
                "confidence": self.assessment.confidence,
                "novelty": self.assessment.novelty,
                "expected_utility": self.assessment.expected_utility,
                "relevance": self.assessment.relevance,
                "consistency": self.assessment.consistency,
                "coherence": self.assessment.coherence,
                "risk": self.assessment.risk,
                "urgency": self.assessment.urgency,
            },
            "lifecycle_state": self.lifecycle_state,
            "relationships": list(self.relationships),
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InternalThought:
        """Deserialize thought from dictionary representation."""
        provenance_data = data.get("provenance", {})
        
        return cls(
            thought_id=data.get("thought_id", ""),
            thought_kind=data.get("thought_kind", ""),
            concept=data.get("concept", ""),
            purpose=data.get("purpose", ""),
            provenance=ThoughtProvenance(
                originating_episode_id=provenance_data.get("originating_episode_id", ""),
                originating_context_version=provenance_data.get("originating_context_version", ""),
                generator_type=provenance_data.get("generator_type", "default"),
                generated_at_utc=datetime.fromisoformat(provenance_data.get("generated_at_utc", "")) if provenance_data.get("generated_at_utc") else None,
                validated_at_utc=datetime.fromisoformat(provenance_data.get("validated_at_utc", "")) if provenance_data.get("validated_at_utc") else None,
                configuration_hash=provenance_data.get("configuration_hash", ""),
                initial_revision=provenance_data.get("initial_revision", 1),
            ),
            originating_episode_id=data.get("originating_episode_id"),
            originating_context_version=data.get("originating_context_version", ""),
            assessment=ThoughtAssessmentMetrics(**data.get("assessment", {})),
            lifecycle_state=data.get("lifecycle_state", LifecycleState.GENERATED),
            relationships=tuple(data.get("relationships", [])),
            revision=data.get("revision", 1),
        )