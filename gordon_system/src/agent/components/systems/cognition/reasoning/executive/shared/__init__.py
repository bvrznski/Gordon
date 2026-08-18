# Executive Shared - Phase 7.30
# =============================

"""
Shared types, contracts, and interfaces for the Executive Reasoning subsystem.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


# =============================================================================
# ENUMERATIONS
# =============================================================================


class SubsystemType:
    """Types of cognitive subsystems in Gordon."""
    
    DEDUCTIVE_REASONING = "deductive_reasoning"
    INDUCTIVE_REASONING = "inductive_reasoning"
    ABDUCTIVE_REASONING = "abductive_reasoning"
    ANALOGICAL_REASONING = "analogical_reasoning"
    CAUSAL_REASONING = "causal_reasoning"
    COUNTERFACTUAL_REASONING = "counterfactual_reasoning"
    PROBABILISTIC_REASONING = "probabilistic_reasoning"
    TEMPORAL_REASONING = "temporal_reasoning"
    SPATIAL_REASONING = "spatial_reasoning"
    SEMANTIC_REASONING = "semantic_reasoning"
    RELATIONAL_REASONING = "relational_reasoning"
    META_REASONING = "meta_reasoning"
    INTROSPECTION = "introspection"
    MONITORING = "monitoring"
    PLANNING = "planning"
    EXECUTION = "execution"
    MEMORY = "memory"
    ATTENTION = "attention"
    GATING = "gating"
    
    ALL_SUBSYSTEMS: Tuple[str, ...] = (
        DEDUCTIVE_REASONING,
        INDUCTIVE_REASONING,
        ABDUCTIVE_REASONING,
        ANALOGICAL_REASONING,
        CAUSAL_REASONING,
        COUNTERFACTUAL_REASONING,
        PROBABILISTIC_REASONING,
        TEMPORAL_REASONING,
        SPATIAL_REASONING,
        SEMANTIC_REASONING,
        RELATIONAL_REASONING,
        META_REASONING,
        INTROSPECTION,
        MONITORING,
        PLANNING,
        EXECUTION,
        MEMORY,
        ATTENTION,
        GATING,
    )


class DirectiveKind:
    """Types of executive directives."""
    
    ACTIVATE = "activate"
    PAUSE = "pause"
    RESUME = "resume"
    ESCALATE = "escalate"
    DEPRIORITIZE = "deprioritize"
    TERMINATE = "terminate"
    RESTART = "restart"
    
    ALL_DIRECTIVES: Tuple[str, ...] = (
        ACTIVATE,
        PAUSE,
        RESUME,
        ESCALATE,
        DEPRIORITIZE,
        TERMINATE,
        RESTART,
    )


class DirectiveStatus:
    """Status of an executive directive."""
    
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    
    ALL_STATUSES: Tuple[str, ...] = (
        PENDING,
        ACTIVE,
        COMPLETED,
        FAILED,
        EXPIRED,
    )


class ConflictKind:
    """Types of conflicts in executive arbitration."""
    
    GOAL_CONFLICT = "goal_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    EXECUTION_CONFLICT = "execution_conflict"
    ATTENTION_CONFLICT = "attention_conflict"
    POLICY_CONFLICT = "policy_conflict"
    
    ALL_CONFLICTS: Tuple[str, ...] = (
        GOAL_CONFLICT,
        RESOURCE_CONFLICT,
        PRIORITY_CONFLICT,
        EXECUTION_CONFLICT,
        ATTENTION_CONFLICT,
        POLICY_CONFLICT,
    )


class ResolutionKind:
    """Types of arbitration resolutions."""
    
    PRIORITY_BASED = "priority_based"
    TIME_SHARING = "time_sharing"
    RESOURCE_ALLOCATION = "resource_allocation"
    DEPRIORITIZE_ONE = "deprioritize_one"
    MERGE_GOALS = "merge_goals"
    SEQUENTIAL_EXECUTION = "sequential_execution"
    
    ALL_RESOLUTIONS: Tuple[str, ...] = (
        PRIORITY_BASED,
        TIME_SHARING,
        RESOURCE_ALLOCATION,
        DEPRIORITIZE_ONE,
        MERGE_GOALS,
        SEQUENTIAL_EXECUTION,
    )


class ValidationOutcome:
    """Outcomes of executive validation."""
    
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    
    ALL_OUTCOMES: Tuple[str, ...] = (
        VALID,
        INVALID,
        WARNING,
    )


class LifecycleState:
    """States in the executive session lifecycle."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    COORDINATING = "coordinating"
    ARBITRATING = "arbitrating"
    DIRECTING = "directing"
    SYNCHRONIZING = "synchronizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    
    ALL_STATES: Tuple[str, ...] = (
        CREATED,
        INITIALIZING,
        COORDINATING,
        ARBITRATING,
        DIRECTING,
        SYNCHRONIZING,
        VALIDATING,
        COMPLETED,
        FAILED,
        ARCHIVED,
    )


class ViolationType:
    """Types of governance violations."""
    
    INVALID_COORDINATION = "invalid_coordination"
    INVALID_ARBITRATION = "invalid_arbitration"
    INVALID_DIRECTIVE = "invalid_directive"
    SYNCHRONIZATION_FAILURE = "synchronization_failure"
    PROVENANCE_MISSING = "provenance_missing"
    POLICY_VIOLATION = "policy_violation"
    
    ALL_VIOLATIONS: Tuple[str, ...] = (
        INVALID_COORDINATION,
        INVALID_ARBITRATION,
        INVALID_DIRECTIVE,
        SYNCHRONIZATION_FAILURE,
        PROVENANCE_MISSING,
        POLICY_VIOLATION,
    )


class SyncState:
    """States in synchronization."""
    
    PENDING = "pending"
    WAITING = "waiting"
    SYNCED = "synced"
    TIMEOUT = "timeout"
    
    ALL_STATES: Tuple[str, ...] = (
        PENDING,
        WAITING,
        SYNCED,
        TIMEOUT,
    )


# =============================================================================
# CANONICAL EXECUTIVE CONTRACTS
# =============================================================================


@dataclass(frozen=True)
class ExecutiveDescriptor:
    """
    Describes an executive session.
    
    Fields:
        executive_identity: Unique semantic identity for this session
        executive_goal: The global objective of the session
        executive_mode: Operational mode (e.g., "default", "emergency")
        lifecycle_state: Current state in lifecycle
        compatibility_revision: Version compatibility marker
        provenance: Origin and lineage information
    """
    
    executive_identity: str                     # Unique ID
    executive_goal: str                         # What are we trying to do?
    
    # Operational parameters
    executive_mode: str = "default"
    lifecycle_state: LifecycleState = LifecycleState.CREATED
    
    # Metadata
    compatibility_revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        goal: str,
        mode: str = "default",
    ) -> "ExecutiveDescriptor":
        """Create a new executive descriptor."""
        return cls(
            executive_identity=f"executive:{uuid.uuid4().hex[:16]}",
            executive_goal=goal,
            executive_mode=mode,
            provenance={
                "created_at_utc": time.time(),
                "version": f"1.0.{cls.__name__}",
            },
        )


@dataclass(frozen=True)
class ExecutiveSet:
    """
    A set of subsystems participating in executive reasoning.
    
    Fields:
        executive_set_identity: Unique identifier
        participating_subsystems: List of subsystems involved
        executive_scope: What area does this cover?
        executive_constraints: Resource/policy constraints
        provenance: Origin information
    """
    
    executive_set_identity: str                 # Unique ID
    participating_subsystems: Tuple[str, ...]   # Which subsystems?
    
    # Scope and constraints
    executive_scope: str = "global"
    executive_constraints: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        subsystem_ids: List[str],
        scope: str = "global",
    ) -> "ExecutiveSet":
        """Create a new executive set."""
        return cls(
            executive_set_identity=f"executive_set:{uuid.uuid4().hex[:16]}",
            participating_subsystems=tuple(subsystem_ids),
            executive_scope=scope,
        )


@dataclass(frozen=True)
class ExecutivePipeline:
    """
    The canonical executive pipeline.
    
    Fields:
        pipeline_identity: Unique identifier
        executive_strategy: How should we execute?
        executive_configuration: Pipeline configuration
        diagnostics: Runtime diagnostics
        provenance: Origin information
    """
    
    pipeline_identity: str                      # Unique ID
    
    # Strategy and config
    executive_strategy: str = "default"
    executive_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        strategy: str = "default",
    ) -> "ExecutivePipeline":
        """Create a new executive pipeline."""
        return cls(
            pipeline_identity=f"executive_pipeline:{uuid.uuid4().hex[:16]}",
            executive_strategy=strategy,
        )


@dataclass(frozen=True)
class ExecutiveState:
    """
    Current global executive state.
    
    Fields:
        executive_identity: Unique identifier
        participating_subsystems: Active subsystems
        executive_snapshot: Moment-in-time snapshot
        executive_confidence: Confidence in the state (0-1)
        provenance: Origin information
    """
    
    executive_identity: str                     # Unique ID
    
    # State components
    active_goals: Tuple[str, ...] = ()
    active_missions: Tuple[str, ...] = ()
    active_priorities: Tuple[str, ...] = ()
    active_reasoning: Tuple[str, ...] = ()
    active_execution: Tuple[str, ...] = ()
    
    # Attention and resources
    attention_allocation: Dict[str, float] = field(default_factory=dict)
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    
    # System-wide directives
    system_directives: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        goals: Optional[List[str]] = None,
        subsystems: Optional[List[str]] = None,
    ) -> "ExecutiveState":
        """Create a new executive state."""
        return cls(
            executive_identity=f"executive_state:{uuid.uuid4().hex[:16]}",
            active_goals=tuple(goals or []),
        )


# =============================================================================
# MANAGEMENT CONTRACTS
# =============================================================================


@dataclass(frozen=True)
class CoordinationManagement:
    """Coordination management contract."""
    
    coordination_identity: str                  # Unique ID
    
    participating_subsystems: Tuple[str, ...]
    coordination_policy: str = "default"
    coordination_metrics: Dict[str, float] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        subsystems: List[str],
        policy: str = "default",
    ) -> "CoordinationManagement":
        """Create coordination management."""
        return cls(
            coordination_identity=f"coordination:{uuid.uuid4().hex[:16]}",
            participating_subsystems=tuple(subsystems),
            coordination_policy=policy,
        )


@dataclass(frozen=True)
class ArbitrationManagement:
    """Arbitration management contract."""
    
    arbitration_identity: str                   # Unique ID
    
    arbitration_policy: str = "priority_based"
    arbitration_scope: Tuple[str, ...] = ()
    selected_resolution: Optional[ResolutionKind] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        policy: str = "priority_based",
    ) -> "ArbitrationManagement":
        """Create arbitration management."""
        return cls(
            arbitration_identity=f"arbitration:{uuid.uuid4().hex[:16]}",
            arbitration_policy=policy,
        )


@dataclass(frozen=True)
class DirectiveManagement:
    """Directive management contract."""
    
    directive_identity: str                     # Unique ID
    
    directive_policy: str = "default"
    target_subsystem: Optional[str] = None
    directive_configuration: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        policy: str = "default",
    ) -> "DirectiveManagement":
        """Create directive management."""
        return cls(
            directive_identity=f"directive_management:{uuid.uuid4().hex[:16]}",
            directive_policy=policy,
        )


@dataclass(frozen=True)
class SynchronizationManagement:
    """Synchronization management contract."""
    
    synchronization_identity: str               # Unique ID
    
    synchronization_policy: str = "default"
    synchronized_subsystems: Tuple[str, ...] = ()
    synchronization_state: Dict[str, Any] = field(default_factory=dict)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        policy: str = "default",
    ) -> "SynchronizationManagement":
        """Create synchronization management."""
        return cls(
            synchronization_identity=f"sync_management:{uuid.uuid4().hex[:16]}",
            synchronization_policy=policy,
        )


@dataclass(frozen=True)
class ExecutiveGovernance:
    """Executive governance contract."""
    
    governance_identity: str                    # Unique ID
    
    evaluated_sessions: Tuple[str, ...] = ()
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    violations: Tuple[ViolationType, ...] = field(default_factory=tuple)
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        session_id: Optional[str] = None,
    ) -> "ExecutiveGovernance":
        """Create executive governance."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple([session_id] if session_id else []),
        )


__all__ = [
    # Enums
    "SubsystemType",
    "DirectiveKind", 
    "DirectiveStatus",
    "ConflictKind",
    "ResolutionKind",
    "ValidationOutcome",
    "LifecycleState",
    "ViolationType",
    "SyncState",
    # Canonical contracts
    "ExecutiveDescriptor",
    "ExecutiveSet",
    "ExecutivePipeline",
    "ExecutiveState",
    # Management contracts
    "CoordinationManagement",
    "ArbitrationManagement",
    "DirectiveManagement", 
    "SynchronizationManagement",
    "ExecutiveGovernance",
]