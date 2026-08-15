# Reflection Subject Models
# =========================

"""
Immutable models for reflection subjects.

ARCHITECTURAL PRINCIPLES:
    - Subjects define what is being reflected upon
    - Each subject has bounded references, not live objects
    - No runtime dependencies in domain objects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# REFLECTION SUBJECT KINDS
# =============================================================================

class ReflectionSubjectKind:
    """
    Canonical kinds of reflection subjects.
    
    Each kind represents a different type of thing that can be
    reflected upon in the system.
    """
    
    EXECUTION_THREAD = "execution_thread"
    """Reflect on an execution thread."""
    
    EXECUTION_CYCLE = "execution_cycle"
    """Reflect on an execution cycle."""
    
    TASK = "task"
    """Reflect on a task."""
    
    PLAN = "plan"
    """Reflect on a plan."""
    
    DECISION = "decision"
    """Reflect on a decision."""
    
    OUTCOME = "outcome"
    """Reflect on an outcome."""
    
    FAILURE = "failure"
    """Reflect on a failure event."""
    
    SUCCESS = "success"
    """Reflect on a success event."""
    
    ACTION = "action"
    """Reflect on an action."""
    
    CONVERSATION = "conversation"
    """Reflect on a conversation."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Reflect on an internal episode."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Reflect on an internal thought."""
    
    MEMORY = "memory"
    """Reflect on memory content."""
    
    IDENTITY_STATE = "identity_state"
    """Reflect on identity state."""
    
    NARRATIVE = "narrative"
    """Reflect on narrative content."""
    
    POLICY = "policy"
    """Reflect on a policy."""
    
    ARCHITECTURE = "architecture"
    """Reflect on system architecture."""
    
    BEHAVIOR_PATTERN = "behavior_pattern"
    """Reflect on behavioral patterns."""
    
    CONTRADICTION = "contradiction"
    """Reflect on a detected contradiction."""
    
    GENERAL_EXPERIENCE = "general_experience"
    """General experience reflection."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all subject kinds."""
        return (
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.TASK,
            cls.PLAN,
            cls.DECISION,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
            cls.ACTION,
            cls.CONVERSATION,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.MEMORY,
            cls.IDENTITY_STATE,
            cls.NARRATIVE,
            cls.POLICY,
            cls.ARCHITECTURE,
            cls.BEHAVIOR_PATTERN,
            cls.CONTRADICTION,
            cls.GENERAL_EXPERIENCE,
        )


# =============================================================================
# REFLECTION SUBJECT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionSubject:
    """
    Immutable subject definition for reflection.
    
    The subject specifies what is being reflected upon. It contains
    references to the subject matter, not the live objects themselves.
    """
    
    kind: str  # ReflectionSubjectKind.*
    """The canonical kind of this subject."""
    
    subject_id: str = ""
    """ID of the subject (if applicable)."""
    
    owner: Optional[str] = None
    """Owner reference for the subject (if any)."""
    
    source_revision: int = 1
    """Revision of the source at reflection time."""
    
    summary: str = ""
    """Brief summary of the subject matter."""
    
    artifact_references: tuple[str, ...] = field(default_factory=tuple)
    """References to relevant artifacts (files, logs, etc.)."""
    
    temporal_bounds_start_utc: Optional[str] = None
    """Start time for temporal bounds (ISO format)."""
    
    temporal_bounds_end_utc: Optional[str] = None
    """End time for temporal bounds (ISO format)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this subject."""
    
    @classmethod
    def task(cls, task_id: str, summary: str) -> ReflectionSubject:
        """Create a task subject."""
        return cls(
            kind=ReflectionSubjectKind.TASK,
            subject_id=task_id,
            summary=summary,
        )
    
    @classmethod
    def outcome(cls, outcome_id: str, summary: str) -> ReflectionSubject:
        """Create an outcome subject."""
        return cls(
            kind=ReflectionSubjectKind.OUTCOME,
            subject_id=outcome_id,
            summary=summary,
        )
    
    @classmethod
    def decision(cls, decision_id: str, summary: str) -> ReflectionSubject:
        """Create a decision subject."""
        return cls(
            kind=ReflectionSubjectKind.DECISION,
            subject_id=decision_id,
            summary=summary,
        )
    
    @classmethod
    def episode(cls, episode_id: str, summary: str) -> ReflectionSubject:
        """Create an internal episode subject."""
        return cls(
            kind=ReflectionSubjectKind.INTERNAL_EPISODE,
            subject_id=episode_id,
            summary=summary,
        )
    
    @classmethod
    def general(cls, summary: str = "General reflection") -> ReflectionSubject:
        """Create a general experience subject."""
        return cls(
            kind=ReflectionSubjectKind.GENERAL_EXPERIENCE,
            summary=summary,
        )
