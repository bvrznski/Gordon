# Memory Record Projections
# =========================

"""
Immutable record projection models for memory content.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Bounded semantic summaries
    - No live database objects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from datetime import datetime


# =============================================================================
# MEMORY RECORD PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryRecordProjection:
    """
    Immutable projection of a memory record.
    
    This contains a bounded summary of the record without live database
    objects or full payloads. It's designed for coordination without
    exposing implementation details.
    
    PROPERTIES:
        • memory_id: Unique identifier for this memory
        • memory_kind: Kind of memory (MemoryKind.*)
        • semantic_summary: Bounded semantic representation
        • subject_references: References to subjects in this memory
        • temporal_information: Temporal bounds or references
        • source_references: References to sources
        • factuality: Factuality classification (FactualityClass.*)
        • confidence: Confidence level (0.0 to 1.0)
        • relevance: Relevance assessment (0.0 to 1.0)
        • freshness: Freshness assessment
        • revision: Record revision number
        • relationships: References to related records
        • privacy: Privacy classification
        • provenance: Provenance reference
        
    BOUNDEDNESS:
        Semantic summaries must be bounded. No unbounded payloads.
    """
    
    # Identity and kind
    memory_id: str
    """Unique identifier for this memory record."""
    
    memory_kind: str  # MemoryKind.*
    """Kind of memory (episodic, semantic, etc.)."""
    
    # Semantic content (bounded)
    semantic_summary: str
    """Bounded summary of the semantic content."""
    
    # Subject references
    subject_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to subjects in this memory."""
    
    # Temporal information
    temporal_start_utc: Optional[datetime] = None
    """Start of temporal range (if applicable)."""
    
    temporal_end_utc: Optional[datetime] = None
    """End of temporal range (if applicable)."""
    
    # Source references
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to sources of this memory."""
    
    # Quality assessments
    factuality: str = "unknown"  # FactualityClass.*
    """Factuality classification."""
    
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    relevance: float = 0.5
    """Relevance assessment (0.0 to 1.0)."""
    
    freshness: str = "unknown"
    """Freshness classification."""
    
    # Metadata
    revision: int = 1
    """Record revision number."""
    
    relationships: Tuple[str, ...] = field(default_factory=tuple)
    """References to related records (format: 'kind:target_id')."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    provenance: Optional[str] = None
    """Provenance reference (how this projection was created)."""
    
    @classmethod
    def new(
        cls,
        memory_id: str,
        memory_kind: str,
        semantic_summary: str,
        factuality: str,
        confidence: float = 0.5,
        relevance: float = 0.5,
    ) -> MemoryRecordProjection:
        """Create a new memory record projection."""
        return cls(
            memory_id=memory_id,
            memory_kind=memory_kind,
            semantic_summary=semantic_summary,
            factuality=factuality,
            confidence=confidence,
            relevance=relevance,
        )
    
    def is_factual(self) -> bool:
        """Check if this projection represents factual content."""
        return self.factuality in {
            "observed",
            "recorded",
            "reported",
        }
    
    def is_speculative(self) -> bool:
        """Check if this projection represents speculative content."""
        return self.factuality in {
            "simulated",
            "counterfactual",
            "hypothetical",
            "predicted",
        }


# =============================================================================
# EPISODIC MEMORY PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class EpisodicMemoryProjection:
    """
    Immutable projection of an episodic memory.
    
    This represents a bounded summary of an episode without live objects.
    
    PROPERTIES:
        • episode_reference: Reference to the episode (not full object)
        • event_references: References to events in this episode
        • participant_references: References to participants
        • objective_references: References to objectives
        • action_references: References to actions taken
        • outcome_references: References to outcomes
        • temporal_start_utc: Start time of the episode
        • temporal_end_utc: End time of the episode
        • contextual_summary: Bounded summary of context
        • confidence: Confidence in this projection (0.0 to 1.0)
        • completeness: Completeness classification
        • factuality: Factuality classification
        • retrieval_rationale: Why this memory was retrieved
        • provenance: Provenance reference
        
    NOT:
        - An ExecutionThread or InternalEpisode
        - A live database object
        - Full event details (only references)
    """
    
    # Episode identification
    episode_reference: str
    """Reference to the episode (format: 'episode_id:revision')."""
    
    # Event and participant references
    event_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to events in this episode."""
    
    participant_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to participants."""
    
    objective_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to objectives."""
    
    action_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to actions taken."""
    
    outcome_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to outcomes."""
    
    # Temporal bounds
    temporal_start_utc: Optional[datetime] = None
    """Start time of the episode (if known)."""
    
    temporal_end_utc: Optional[datetime] = None
    """End time of the episode (if known)."""
    
    # Content summary (bounded)
    contextual_summary: str = ""
    """Bounded summary of episode context."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence in this projection (0.0 to 1.0)."""
    
    completeness: str = "partial"
    """Completeness classification."""
    
    factuality: str = "unknown"
    """Factuality classification."""
    
    retrieval_rationale: str = ""
    """Why this memory was retrieved (for provenance)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        episode_reference: str,
        event_references: Tuple[str, ...],
        confidence: float = 0.5,
        completeness: str = "partial",
    ) -> EpisodicMemoryProjection:
        """Create a new episodic memory projection."""
        return cls(
            episode_reference=episode_reference,
            event_references=event_references,
            confidence=confidence,
            completeness=completeness,
        )


# =============================================================================
# SEMANTIC MEMORY PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticMemoryProjection:
    """
    Immutable projection of semantic memory.
    
    Represents conceptual knowledge without live objects or full details.
    
    PROPERTIES:
        • concept_ids: References to concepts
        • propositions: Key propositions in this memory
        • relationships: References to related concepts
        • category_references: Category memberships
        • definitions: Semantic definitions (bounded)
        • confidence: Confidence level (0.0 to 1.0)
        • source_references: References to sources
        • revision: Record revision number
        • provenance: Provenance reference
        
    MUST DISTINGUISH:
        - Accepted knowledge
        - Disputed knowledge
        - Inferred knowledge
        - External report
        - Hypothesis
        - Unknown
    """
    
    # Concept identification
    concept_ids: Tuple[str, ...] = field(default_factory=tuple)
    """References to concepts in this memory."""
    
    # Semantic content
    propositions: Tuple[str, ...] = field(default_factory=tuple)
    """Key propositions in this semantic memory."""
    
    relationships: Tuple[str, ...] = field(default_factory=tuple)
    """References to related concepts (format: 'kind:target_id')."""
    
    # Categorization
    category_references: Tuple[str, ...] = field(default_factory=tuple)
    """Category memberships."""
    
    # Definitions (bounded)
    definitions: str = ""
    """Semantic definitions (bounded representation)."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    source_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to sources."""
    
    revision: int = 1
    """Record revision number."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    # Knowledge status indicators (at least one should be true)
    is_accepted_knowledge: bool = False
    """This is accepted knowledge in the system."""
    
    is_disputed_knowledge: bool = False
    """There is dispute about this knowledge."""
    
    is_inferred_knowledge: bool = False
    """This was inferred from other evidence."""
    
    is_external_report: bool = False
    """This comes from an external source."""
    
    is_hypothesis: bool = False
    """This is a hypothesis (not yet validated)."""
    
    @classmethod
    def new(
        cls,
        concept_ids: Tuple[str, ...],
        propositions: Tuple[str, ...],
        confidence: float = 0.5,
        is_accepted_knowledge: bool = True,
    ) -> SemanticMemoryProjection:
        """Create a new semantic memory projection."""
        return cls(
            concept_ids=concept_ids,
            propositions=propositions,
            confidence=confidence,
            is_accepted_knowledge=is_accepted_knowledge,
        )


# =============================================================================
# AUTOBIOGRAPHICAL MEMORY PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class AutobiographicalMemoryProjection:
    """
    Immutable projection of autobiographical memory.
    
    Represents self-relevant memories without live objects or full details.
    
    PROPERTIES:
        • self_reference: Reference to the self/entity
        • event_references: References to self-relevant events
        • narrative_references: Narrative connections
        • identity_references: Identity relevance links
        • role_references: Role-related information
        • commitment_references: Commitments tied to this memory
        • temporal_start_utc: Start of relevant time range
        • temporal_end_utc: End of relevant time range
        • continuity_links: References to continuity evidence
        • confidence: Confidence level (0.0 to 1.0)
        • factuality: Factuality classification
        • provenance: Provenance reference
        
    REMAINS:
        - Memory-owned (not Identity-owned)
        - Identity-relevant, not Identity-defining
    """
    
    # Self-reference
    self_reference: str
    """Reference to the self/entity."""
    
    # Event references
    event_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to self-relevant events."""
    
    narrative_references: Tuple[str, ...] = field(default_factory=tuple)
    """Narrative connections."""
    
    identity_references: Tuple[str, ...] = field(default_factory=tuple)
    """Identity relevance links."""
    
    # Role and commitment references
    role_references: Tuple[str, ...] = field(default_factory=tuple)
    """Role-related information."""
    
    commitment_references: Tuple[str, ...] = field(default_factory=tuple)
    """Commitments tied to this memory."""
    
    # Temporal bounds
    temporal_start_utc: Optional[datetime] = None
    """Start of relevant time range."""
    
    temporal_end_utc: Optional[datetime] = None
    """End of relevant time range."""
    
    # Continuity evidence
    continuity_links: Tuple[str, ...] = field(default_factory=tuple)
    """References to continuity evidence."""
    
    # Quality assessments
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    factuality: str = "unknown"
    """Factuality classification."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        self_reference: str,
        event_references: Tuple[str, ...],
        identity_references: Tuple[str, ...],
        confidence: float = 0.5,
    ) -> AutobiographicalMemoryProjection:
        """Create a new autobiographical memory projection."""
        return cls(
            self_reference=self_reference,
            event_references=event_references,
            identity_references=identity_references,
            confidence=confidence,
        )


# =============================================================================
# PROCEDURAL MEMORY REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProceduralMemoryReference:
    """
    Optional reference to procedural memory.
    
    Identifies procedures without embedding executable code or invoking them.
    
    PROPERTIES:
        • skill: Skill name (if applicable)
        • procedure: Procedure identifier
        • strategy: Strategy reference
        • workflow: Workflow identifier
        • tool_use_pattern: Tool-use pattern reference
        • action_schema: Action schema reference
        
    IS SEMANTIC EVIDENCE ONLY - DOES NOT:
        - Invoke the procedure
        - Embed executable code
        - Process the action
    """
    
    # References (all optional)
    skill: Optional[str] = None
    """Skill name or identifier."""
    
    procedure: Optional[str] = None
    """Procedure identifier."""
    
    strategy: Optional[str] = None
    """Strategy reference."""
    
    workflow: Optional[str] = None
    """Workflow identifier."""
    
    tool_use_pattern: Optional[str] = None
    """Tool-use pattern reference."""
    
    action_schema: Optional[str] = None
    """Action schema reference."""
    
    confidence: float = 0.5
    """Confidence in this reference (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def new(
        cls,
        procedure: str,
        confidence: float = 0.5,
    ) -> ProceduralMemoryReference:
        """Create a new procedural memory reference."""
        return cls(
            procedure=procedure,
            confidence=confidence,
        )


# =============================================================================
# RECENT EXPERIENCE PROJECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class RecentExperienceProjection:
    """
    Immutable projection of recent experiences.
    
    Represents recent activity without live objects or full details.
    
    PROPERTIES:
        • experience_id: Unique identifier for the experience
        • experience_kind: Kind of experience (cycle, task, etc.)
        • outcome_summary: Brief summary of outcomes
        • feedback_references: References to feedback received
        • reflection_references: References to reflections
        • simulation_references: Simulation products referenced
        • narrative_references: Narrative connections
        • identity_references: Identity relevance links
        • temporal_start_utc: Start time
        • temporal_end_utc: End time
        • confidence: Confidence level (0.0 to 1.0)
        
    IS NOT:
        - Automatically persistent memory
        - Full experience record
    """
    
    # Experience identification
    experience_id: str
    """Unique identifier for this recent experience."""
    
    experience_kind: str = "generic"
    """Kind of recent experience (cycle, task, etc.)."""
    
    # Summary information (bounded)
    outcome_summary: str = ""
    """Brief summary of outcomes."""
    
    feedback_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to feedback received."""
    
    reflection_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to reflections."""
    
    # Product references
    simulation_references: Tuple[str, ...] = field(default_factory=tuple)
    """Simulation products referenced."""
    
    narrative_references: Tuple[str, ...] = field(default_factory=tuple)
    """Narrative connections."""
    
    identity_references: Tuple[str, ...] = field(default_factory=tuple)
    """Identity relevance links."""
    
    # Temporal bounds
    temporal_start_utc: Optional[datetime] = None
    """Start time of the experience."""
    
    temporal_end_utc: Optional[datetime] = None
    """End time of the experience."""
    
    # Quality assessment
    confidence: float = 0.5
    """Confidence level (0.0 to 1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference."""
    
    @classmethod
    def cycle_experience(
        cls,
        experience_id: str,
        outcome_summary: str,
        confidence: float = 0.5,
    ) -> RecentExperienceProjection:
        """Create a recent experience projection for an execution cycle."""
        return cls(
            experience_id=experience_id,
            experience_kind="execution_cycle",
            outcome_summary=outcome_summary,
            confidence=confidence,
        )
    
    @classmethod
    def task_experience(
        cls,
        experience_id: str,
        task_description: str,
        outcome_summary: str,
        confidence: float = 0.5,
    ) -> RecentExperienceProjection:
        """Create a recent experience projection for a task."""
        return cls(
            experience_id=experience_id,
            experience_kind="task",
            outcome_summary=f"Task: {task_description}. Outcome: {outcome_summary}",
            confidence=confidence,
        )