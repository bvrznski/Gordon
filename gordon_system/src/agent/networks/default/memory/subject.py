# Memory Integration Subject Models
# ==================================

"""
Immutable subject models for memory integration requests.

ARCHITECTURAL PRINCIPLES:
    - Frozen dataclasses (deeply immutable)
    - Semantic only, no implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# MEMORY INTEGRATION SUBJECT KINDS
# =============================================================================

class MemoryIntegrationSubjectKind:
    """
    Canonical subject kinds for memory integration requests.
    
    Each subject represents what is being integrated.
    """
    
    INTERNAL_CONTEXT = "internal_context"
    """The current internal context."""
    
    INTERNAL_EPISODE = "internal_episode"
    """A specific internal episode."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """A specific internal thought."""
    
    EXECUTION_THREAD = "execution_thread"
    """An execution thread."""
    
    EXECUTION_CYCLE = "execution_cycle"
    """An execution cycle."""
    
    CONVERSATION = "conversation"
    """A conversation context."""
    
    TASK = "task"
    """A task being performed."""
    
    OBJECTIVE = "objective"
    """An objective or goal."""
    
    DECISION = "decision"
    """A decision made."""
    
    ACTION = "action"
    """An action taken."""
    
    OUTCOME = "outcome"
    """An outcome result."""
    
    FAILURE = "failure"
    """A failure event."""
    
    SUCCESS = "success"
    """A success event."""
    
    REFLECTIVE_PRODUCT = "reflective_product"
    """A reflection product."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """A simulation product."""
    
    NARRATIVE_PRODUCT = "narrative_product"
    """A narrative product."""
    
    IDENTITY_PRODUCT = "identity_product"
    """An identity product."""
    
    PREDICTION = "prediction"
    """A prediction."""
    
    CONCERN = "concern"
    """A concern or issue."""
    
    MEMORY_CLUSTER = "memory_cluster"
    """A memory cluster."""
    
    MEMORY_RECORD = "memory_record"
    """A specific memory record."""
    
    TIME_PERIOD = "time_period"
    """A time period."""
    
    RELATIONSHIP = "relationship"
    """A relationship context."""
    
    PROJECT = "project"
    """A project context."""
    
    GENERAL_EXPERIENCE = "general_experience"
    """General experience."""
    
    @classmethod
    def all_subjects(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds."""
        return (
            cls.INTERNAL_CONTEXT,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.CONVERSATION,
            cls.TASK,
            cls.OBJECTIVE,
            cls.DECISION,
            cls.ACTION,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
            cls.REFLECTIVE_PRODUCT,
            cls.SIMULATION_PRODUCT,
            cls.NARRATIVE_PRODUCT,
            cls.IDENTITY_PRODUCT,
            cls.PREDICTION,
            cls.CONCERN,
            cls.MEMORY_CLUSTER,
            cls.MEMORY_RECORD,
            cls.TIME_PERIOD,
            cls.RELATIONSHIP,
            cls.PROJECT,
            cls.GENERAL_EXPERIENCE,
        )


# =============================================================================
# MEMORY INTEGRATION SUBJECT
# =============================================================================

@dataclass(frozen=True, slots=True)
class MemoryIntegrationSubject:
    """
    Immutable subject descriptor for a memory integration episode.
    
    PROPERTIES:
        • kind: Subject kind (MemoryIntegrationSubjectKind.*)
        • references: References to subjects in question
        • temporal_bounds: Temporal bounds if applicable
        • context_notes: Additional notes about the subject
        
    DOES NOT:
        - Embed live objects
        - Contain full record payloads
    """
    
    # Subject kind
    kind: str  # MemoryIntegrationSubjectKind.*
    """The subject kind."""
    
    # References
    references: Tuple[str, ...] = field(default_factory=tuple)
    """References to subjects in question."""
    
    # Temporal bounds (optional)
    temporal_bounds_start_utc: Optional[str] = None
    """Start of temporal bounds (ISO format)."""
    
    temporal_bounds_end_utc: Optional[str] = None
    """End of temporal bounds (ISO format)."""
    
    # Additional context
    context_notes: str = ""
    """Additional notes about the subject."""
    
    @classmethod
    def internal_context(
        cls,
        context_id: str,
    ) -> MemoryIntegrationSubject:
        """Create an internal context subject."""
        return cls(
            kind=MemoryIntegrationSubjectKind.INTERNAL_CONTEXT,
            references=(f"context:{context_id}",),
        )
    
    @classmethod
    def internal_episode(
        cls,
        episode_id: str,
    ) -> MemoryIntegrationSubject:
        """Create an internal episode subject."""
        return cls(
            kind=MemoryIntegrationSubjectKind.INTERNAL_EPISODE,
            references=(f"episode:{episode_id}",),
        )
    
    @classmethod
    def internal_thought(
        cls,
        thought_id: str,
    ) -> MemoryIntegrationSubject:
        """Create an internal thought subject."""
        return cls(
            kind=MemoryIntegrationSubjectKind.INTERNAL_THOUGHT,
            references=(f"thought:{thought_id}",),
        )