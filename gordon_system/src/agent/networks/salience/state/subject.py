# Salience Network Subject Reference
# ==================================
#
# Canonical implementation of typed immutable subject references (Phase 4.8.4).
#

"""
Typed immutable subject references for Salience State.

A SalienceSubjectReference represents:
    - The identity and kind of the subject whose salience is represented
    - The authoritative owner of that subject (external subsystem)
    - References to source Content where available

The Salience Network does NOT own subjects; it only retains typed references.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceSubjectReference:
    """
    Immutable reference to a subject whose salience is represented in State.
    
    A subject may be from any cognitive domain:
        - Sensory Content (observations of environment)
        - Goal Content (Goals and objectives)
        - Task Content (Tasks and assignments)
        - Memory Content (Memory records)
        - Workspace Content (Active workspace items)
        - Working Memory Content (Maintained representations)
        - Executive Content (Executive decisions and plans)
        - Planning Content (Plans and strategies)
        - Reasoning Content (Reasoned conclusions)
        - Decision Content (Decisions and commitments)
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-SUBJECT-INV-001: Reference preserves external ownership
        - SALIENCE-SUBJECT-INV-002: Reference is immutable
        - SALIENCE-SUBJECT-INV-003: Subject kind is explicit
        - SALIENCE-SUBJECT-INV-004: Authority reference is explicit
    
    REFERENCE LAWS:
        - SALIENCE-SUBJECT-LAW-001: Subject references never own the referenced subject
        - SALIENCE-SUBJECT-LAW-002: Reference always preserves authoritative identity
        - SALIENCE-SUBJECT-LAW-003: Subject kind is never inferred from context
    """
    
    subject_id: str = field(default="")
    """Unique identifier for the subject within its namespace."""
    
    subject_kind: str = field(default="unknown")
    """
    Canonical kind of subject:
        - sensory: Raw sensory Content
        - goal: Goal System Goal
        - task: Task System Task
        - memory: Memory record
        - workspace: Workspace item
        - working_memory: Working Memory representation
        - executive: Executive decision or plan
        - planning: Plan or strategy
        - reasoning: Reasoned conclusion
        - decision: Decision and commitment
    """
    
    subject_namespace: str = field(default="salience")
    """Namespace scoping the subject identity."""
    
    authoritative_owner: str = field(default="")
    """Canonical owner of this subject (external to Salience Network)."""
    
    source_content_id: str = field(default="")
    """Optional reference to canonical Content where available."""
    
    revision: int = field(default=1)
    """Subject revision where available."""
    
    @property
    def canonical_subject_id(self) -> str:
        """
        Return the fully qualified canonical subject ID.
        
        Format: namespace/subject_kind:subject_id:v{revision}
        """
        return f"{self.subject_namespace}/{self.subject_kind}:{self.subject_id}:v{self.revision}"
    
    @property
    def is_external_ownership(self) -> bool:
        """
        Indicates whether this reference preserves external ownership.
        
        External ownership means the subject belongs to another subsystem
        and the Salience Network only retains a semantic projection.
        """
        return len(self.authoritative_owner.strip()) > 0
    
    @property
    def has_source_content(self) -> bool:
        """Indicates whether source Content is referenced."""
        return len(self.source_content_id.strip()) > 0