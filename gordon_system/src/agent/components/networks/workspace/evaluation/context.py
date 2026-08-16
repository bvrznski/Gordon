# Workspace Evaluation Context
# ============================

"""
Canonical evaluation context definitions.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclass)
    - No runtime dependencies
    - External time providers only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


WorkspaceEvaluationContextIdentity = str
"""Unique identifier for an evaluation context."""


WorkspaceEvaluationContextRevision = int
"""Monotonically increasing revision number for contexts."""


WorkspaceEvaluationContextReference = str
"""
Immutable reference to Workspace Evaluation Context.

Format: "identity@revision"
Examples:
    "context_def123@1"
"""


# =============================================================================
# WORKSPACE EVALUATION CONTEXT
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceEvaluationContext:
    """
    Immutable evaluation context.

    The context must be a bounded semantic projection and must not absorb 
    external subsystem State.

    ARCHITECTURAL INVARIANTS:
        WEC-INV-001: Context never contains runtime objects
        WEC-INV-002: Context is never executable
        WEC-INV-003: Context has no internal time acquisition
    """

    # Identity and References
    identity: WorkspaceEvaluationContextIdentity
    """Unique identifier for this context."""

    revision: WorkspaceEvaluationContextRevision
    """Context revision number."""

    # State references
    workspace_network_state_ref: Optional[str] = None
    """Reference to Workspace Network State."""

    active_task_ref: Optional[str] = None
    """Reference to active task."""

    goals_ref: Tuple[str, ...] = field(default_factory=tuple)
    """References to current Goals."""

    executive_decision_ref: Optional[str] = None
    """Reference to current Executive Decision."""

    decision_network_state_ref: Optional[str] = None
    """Reference to Decision Network State."""

    attention_state_ref: Optional[str] = None
    """Reference to Attention State."""

    focusing_state_ref: Optional[str] = None
    """Reference to Focusing State."""

    alerting_state_ref: Optional[str] = None
    """Reference to Alerting State."""

    motivation_state_ref: Optional[str] = None
    """Reference to Motivation State."""

    working_memory_projection_ref: Optional[str] = None
    """Reference to Working Memory projection."""

    # Context classifications
    temporal_context: str = ""
    """Temporal context (semantic time reference)."""

    environmental_context: str = ""
    """Environmental context."""

    threat_context: str = ""
    """Threat context."""

    policy_context_ref: Optional[str] = None
    """Reference to Policy context."""

    security_context_ref: Optional[str] = None
    """Reference to Security context."""

    resource_context: str = ""
    """Resource availability context."""

    cognitive_load_level: int = 0
    """Cognitive load level (bounded)."""

    broadcast_capacity: int = 100
    """Broadcast capacity limit (bounded)."""

    # Source reliability context
    source_reliability_ref: Optional[str] = None
    """Reference to source reliability data."""

    # Target availability context where relevant
    target_availability_refs: Tuple[str, ...] = field(default_factory=tuple)
    """References to target availability information."""
