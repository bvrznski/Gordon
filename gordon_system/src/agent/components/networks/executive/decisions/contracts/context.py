# Gordon Executive Decision Context - Phase 4.4.10A
# ==================================================

"""
Decision Context and Scope System.

This module defines the context and scope system for Executive Decisions.
Context describes the operational environment within which a decision
remains meaningful.


CONTEXT OVERVIEW
================

    Every decision exists inside an operational context.

    Without context, a decision is semantically incomplete.
    Without scope, a decision is operationally ambiguous.
    Without assumptions, a decision is epistemically invalid.
    Without constraints, a decision is behaviorally unsafe.

ARCHITECTURAL LAWS
==================

E-016: Every Executive Decision shall possess exactly one semantic context.
E-017: Every Executive Decision shall declare explicit scope.
"""

from dataclasses import dataclass, field
from typing import Tuple
from enum import Enum


# =============================================================================
# CONTEXT SCOPES - Scope dimensions for decisions
# =============================================================================

class ContextScope(Enum):
    """
    Scope dimensions for Executive Decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    LOCAL = "local"
    """Local subsystem scope."""
    
    SUBSYSTEM = "subsystem"
    """Specific subsystem scope."""
    
    CAPABILITY = "capability"
    """Capability-level scope."""
    
    NETWORK = "network"
    """Network-level scope."""
    
    SESSION = "session"
    """Session-level scope."""
    
    CONVERSATION = "conversation"
    """Conversation-level scope."""
    
    TASK = "task"
    """Task-level scope."""
    
    WORKFLOW = "workflow"
    """Workflow-level scope."""
    
    MISSION = "mission"
    """Mission-level scope."""
    
    GLOBAL = "global"
    """Global system-wide scope."""


# =============================================================================
# CONTEXT KINDS - Context categorization
# =============================================================================

class ContextKind(Enum):
    """
    Kinds of operational contexts for decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    OPERATIONAL = "operational"
    """Current operational context."""
    
    PLANNING = "planning"
    """Planning-related context."""
    
    RECOVERY = "recovery"
    """Recovery or error state context."""
    
    TRANSITIONAL = "transitional"
    """Transitional context between states."""
    
    MONITORING = "monitoring"
    """Monitoring and observation context."""


# =============================================================================
# DECISION CONTEXT - Operational environment record
# =============================================================================

@dataclass(frozen=True)
class DecisionContext:
    """
    Record of the operational environment for an Executive Decision.
    
    Context describes the bounded operational environment within which the
    decision remains meaningful. Outside this context, the decision may
    become invalid.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - scope: Scope dimension governed by the decision
        - kind: Category of operational context
        - environmental_assumptions: Assumptions about the environment
        - active_objectives: Objectives being pursued
        - active_commitments: Existing commitments affecting this decision
        
    Example:
        >>> context = DecisionContext(
        ...     scope=ContextScope.SUBSYSTEM,
        ...     kind=ContextKind.OPERATIONAL,
        ... )
    """
    
    scope: ContextScope = ContextScope.LOCAL
    """Scope dimension governed by the decision."""
    
    kind: ContextKind = ContextKind.OPERATIONAL
    """Category of operational context."""
    
    environmental_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions about the external environment."""
    
    active_objectives: Tuple[str, ...] = field(default_factory=tuple)
    """Objectives currently being pursued."""
    
    active_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """Existing commitments affecting this decision."""
    
    temporal_bounds: Tuple[float, float] = field(default=(0.0, 0.0))
    """(start_timestamp, end_timestamp) for context validity."""
    
    @property
    def is_context(self) -> bool:
        """Return True for all context records."""
        return True
    
    def is_valid_at_time(self, timestamp_utc: float) -> bool:
        """
        Check if the context is valid at a given time.
        
        Runtime-neutral: Yes
        Executable: No
        """
        start, end = self.temporal_bounds
        if start == 0.0 and end == 0.0:
            return True  # No temporal bounds set
        return start <= timestamp_utc <= end
    
    @classmethod
    def for_scope(cls, scope: ContextScope) -> "DecisionContext":
        """Create a context with the specified scope."""
        return cls(scope=scope)


# =============================================================================
# CONTEXT VALIDATION - Validation utilities
# =============================================================================

class ContextValidation:
    """
    Static validation utilities for DecisionContext.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_scope(scope: ContextScope) -> bool:
        """Validate that a context scope is valid."""
        return isinstance(scope, ContextScope)
    
    @staticmethod
    def is_valid_kind(kind: ContextKind) -> bool:
        """Validate that a context kind is valid."""
        return isinstance(kind, ContextKind)