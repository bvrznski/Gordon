# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Subjects Ontology

This module defines the canonical Action subject taxonomy that describes
who or what an Action serves or affects.

ACTION SUBJECTS TAXONOMY
========================

Subjects represent the primary entities that an Action serves or affects.
While targets are what the Action operates ON, subjects are who/what 
the Action is FOR.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION SUBJECT KINDS - Semantic subject types
# =============================================================================

class ActionSubjectKind(Enum):
    """
    The kind of subject an Action serves or affects.
    
    Subjects represent the primary entities that Actions serve or affect.
    This is distinct from targets - subjects are who/what the Action is FOR,
    while targets are what it operates ON.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # USER SUBJECTS
    # =============================================================================
    
    USER = "user"
    """Human user or actor."""
    
    OPERATOR = "operator"
    """System operator or administrator."""
    
    ASSISTANT = "assistant"
    """AI assistant or agent."""
    
    # =============================================================================
    # AGENT SUBJECTS
    # =============================================================================
    
    AGENT = "agent"
    """Autonomous agent."""
    
    TEAM = "team"
    """Team of agents."""
    
    GROUP = "group"
    """Group of users or agents."""
    
    # =============================================================================
    # SYSTEM SUBJECTS
    # =============================================================================
    
    SYSTEM = "system"
    """The system as a whole."""
    
    PROCESS = "process"
    """Running process."""
    
    SERVICE = "service"
    """Service instance."""
    
    COMPONENT = "component"
    """System component."""
    
    # =============================================================================
    # WORKFLOW SUBJECTS
    # =============================================================================
    
    WORKFLOW = "workflow"
    """Workflow or pipeline."""
    
    TASK = "task"
    """Task unit of work."""
    
    JOB = "job"
    """Batch job or scheduled task."""
    
    # =============================================================================
    # DATA SUBJECTS
    # =============================================================================
    
    DATA = "data"
    """Data object or record."""
    
    DOCUMENT = "document"
    """Document or article."""
    
    MESSAGE = "message"
    """Message or notification."""
    
    EVENT = "event"
    """Event or signal."""
    
    # =============================================================================
    # RESOURCE SUBJECTS
    # =============================================================================
    
    RESOURCE = "resource"
    """System resource."""
    
    CAPABILITY = "capability"
    """Capability or skill."""
    
    PERMISSION = "permission"
    """Permission or authorization."""
    
    # =============================================================================
    # CONTEXTUAL SUBJECTS
    # =============================================================================
    
    CONTEXT = "context"
    """Execution context."""
    
    SESSION = "session"
    """User session."""
    
    TRANSACTION = "transaction"
    """Transaction or unit of work."""
    
    # =============================================================================
    # ABSTRACT SUBJECTS
    # =============================================================================
    
    GOAL = "goal"
    """Goal or objective."""
    
    PLAN = "plan"
    """Plan or strategy."""
    
    POLICY = "policy"
    """Policy or rule."""
    
    RULE = "rule"
    """Rule or constraint."""
    
    # =============================================================================
    # EXTERNAL SUBJECTS
    # =============================================================================
    
    EXTERNAL_SYSTEM = "external_system"
    """External system or service."""
    
    THIRD_PARTY = "third_party"
    """Third-party entity."""
    
    NETWORK = "network"
    """Network infrastructure."""
    
    # =============================================================================
    # GENERAL SUBJECTS
    # =============================================================================
    
    ANY = "any"
    """Any subject type (polymorphic)."""
    
    UNKNOWN = "unknown"
    """Subject kind is unknown or undetermined."""


# =============================================================================
# UTILITY TYPES - Subject collections
# =============================================================================

class ActionSubjectKinds(FrozenSet[ActionSubjectKind]):
    """A collection of ActionSubjectKind values."""
    
    def __new__(cls, subjects: Tuple[ActionSubjectKind, ...] = ()):
        return super().__new__(cls, subjects)
    
    @classmethod
    def all(cls) -> "ActionSubjectKinds":
        """Get all canonical ActionSubjectKinds."""
        return cls(tuple(ActionSubjectKind))
    
    @classmethod
    def user_related(cls) -> "ActionSubjectKinds":
        """Get all user-related subject kinds."""
        return cls((
            ActionSubjectKind.USER,
            ActionSubjectKind.OPERATOR,
            ActionSubjectKind.ASSISTANT,
        ))
    
    @classmethod
    def system_related(cls) -> "ActionSubjectKinds":
        """Get all system-related subject kinds."""
        return cls((
            ActionSubjectKind.SYSTEM,
            ActionSubjectKind.PROCESS,
            ActionSubjectKind.SERVICE,
            ActionSubjectKind.COMPONENT,
        ))


__all__ = [
    "ActionSubjectKind",
    "ActionSubjectKinds",
]