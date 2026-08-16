# Gordon Executive Decision Coordination - Phase 4.4.10C
# =========================================================

"""
Executive Decision Coordination Architecture Specification.

This is Phase 4.4.10C: Executive Decision Coordination.

The Executive Decision Coordination subsystem establishes the canonical
semantic boundary between:

    Executive Intent (Decision Commitments)
              ↓
    Decision Coordination
              ↓
    Action Selection Request
              ↓
    Action Selection Capability

ARCHITECTURAL PRINCIPLES:
========================

COORDINATION MODEL:
    Executive coordinates.
    It does not duplicate subsystem functionality.
    
BOUNDARY MODEL:
    Action Selection Request is the terminal Executive-owned product.
    Everything beyond belongs to downstream capabilities.
    
OWNERSHIP MODEL:
    Subsystem ownership is preserved.
    Coordination never implies authority transfer.

ARCHITECTURAL BOUNDARIES:
========================

EXECUTIVE OWNS (semantic contracts):
    - Decision Coordination requests
    - Decision Projections
    - Coordination contexts
    - Action Selection Requests
    
EXECUTIVE COORDINATES WITH (ownership preserved):
    - Planning: Plan generation requests, dependency resolution
    - Reasoning: Semantic analysis, evidence evaluation
    - Policy: Compliance verification
    - Security: Authorization review
    - Attention Networks: Focus coordination
    - Memory Systems: State projections
    - Action Selection: Candidate assessment and selection
    - Execution: Readiness projections

NO DUPLICATION:
Executive NEVER:
    - Computes planning (owned by Planning)
    - Performs reasoning (owned by Reasoning)
    - Enforces policy (owned by Policy)
    - Grants security authorization (owned by Security)
    - Selects actions (owned by Action Selection)
    - Executes tasks (owned by Execution)

ARCHITECTURAL LAWS:
==================

EXEC-DEC-COORD-LAW-001: Executive coordinates.
                        It does not duplicate subsystem functionality.

EXEC-DEC-COORD-LAW-002: Action Selection Request is the terminal
                        Executive-owned product.

EXEC-DEC-COORD-LAW-003: Action Selection remains downstream of Decision Commitment.

EXEC-DEC-COORD-LAW-004: Execution remains downstream of Action Selection.

EXEC-DEC-COORD-LAW-005: All coordination contracts remain runtime-neutral.

EXEC-DEC-COORD-LAW-006: All coordination artifacts remain immutable.

EXEC-DEC-COORD-LAW-007: Coordination is deterministic and bounded.

EXEC-DEC-COORD-LAW-008: Subsystem ownership is preserved through every projection.

PHASE STRUCTURE:
===============

Phase 4.4.10C Part 1 defines:
    - Decision Coordination semantics
    - Coordination contracts
    - Terminal boundary (Action Selection Request)
    
Part 2 defines:
    - Cross-network integration contracts
    
Part 3 defines:
    - Decision State, History, Lineage, Delta, Transition, Continuation
    
Part 4 defines:
    - Validation, serialization, certification

IMPLEMENTATION STATUS:
=====================

This package is entirely runtime-neutral.
It defines semantic contracts, NOT implementations.

No scheduler, loop, coroutine, thread, executor,
asyncio construct, process, callback, or runtime
implementation is introduced here.

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

# =============================================================================
# CORE IDENTITY TYPES
# =============================================================================

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional, Literal
from enum import Enum, auto
import uuid


@dataclass(frozen=True)
class ExecutiveDecisionCoordinationRequestId:
    """Unique identifier for an executive decision coordination request."""
    value: str = field(default_factory=lambda: f"exec_dec_coord_req_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionCoordinationRequestId":
        return cls(value=f"exec_dec_coord_req_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionProjectionId:
    """Unique identifier for a decision projection."""
    value: str = field(default_factory=lambda: f"exec_dec_proj_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionProjectionId":
        return cls(value=f"exec_dec_proj_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionCoordinationResponseId:
    """Unique identifier for a coordination response."""
    value: str = field(default_factory=lambda: f"exec_dec_coord_resp_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionCoordinationResponseId":
        return cls(value=f"exec_dec_coord_resp_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionCoordinationOutcomeId:
    """Unique identifier for a coordination outcome."""
    value: str = field(default_factory=lambda: f"exec_dec_coord_outcome_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionCoordinationOutcomeId":
        return cls(value=f"exec_dec_coord_outcome_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionStateId:
    """Unique identifier for decision state."""
    value: str = field(default_factory=lambda: f"exec_dec_state_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionStateId":
        return cls(value=f"exec_dec_state_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionHistoryEntryId:
    """Unique identifier for a history entry."""
    value: str = field(default_factory=lambda: f"exec_dec_history_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionHistoryEntryId":
        return cls(value=f"exec_dec_history_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionTransitionId:
    """Unique identifier for a decision transition."""
    value: str = field(default_factory=lambda: f"exec_dec_trans_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionTransitionId":
        return cls(value=f"exec_dec_trans_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveDecisionContinuationId:
    """Unique identifier for a decision continuation."""
    value: str = field(default_factory=lambda: f"exec_dec_cont_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveDecisionContinuationId":
        return cls(value=f"exec_dec_cont_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ActionSelectionRequestId:
    """Unique identifier for an action selection request."""
    value: str = field(default_factory=lambda: f"action_sel_req_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ActionSelectionRequestId":
        return cls(value=f"action_sel_req_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ActionSelectionOutcomeId:
    """Unique identifier for an action selection outcome."""
    value: str = field(default_factory=lambda: f"action_sel_outcome_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ActionSelectionOutcomeId":
        return cls(value=f"action_sel_outcome_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class SelectedActionReferenceId:
    """Unique identifier for a selected action reference."""
    value: str = field(default_factory=lambda: f"selected_action_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "SelectedActionReferenceId":
        return cls(value=f"selected_action_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class ExecutiveExecutionReadinessProjectionId:
    """Unique identifier for an execution readiness projection."""
    value: str = field(default_factory=lambda: f"exec_readiness_{uuid.uuid4().hex[:16]}")

    @classmethod
    def generate(cls) -> "ExecutiveExecutionReadinessProjectionId":
        return cls(value=f"exec_readiness_{uuid.uuid4().hex[:16]}")


# =============================================================================
# DECISION COORDINATION SUBJECT KINDS
# =============================================================================


class ExecutiveDecisionCoordinationSubjectKind(Enum):
    """
    Kinds of coordination subjects.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    DECISION_COMMITMENT = "decision_commitment"
    """The accepted decision commitment being coordinated."""
    
    DECISION_REVISION = "decision_revision"
    """A revision to an existing decision."""
    
    DECISION_REVIEW = "decision_review"
    """A request for decision review."""
    
    DECISION_REPLACEMENT = "decision_replacement"
    """A proposed replacement of a decision."""
    
    DECISION_SUSPENSION = "decision_suspension"
    """A request to suspend a decision."""
    
    DECISION_RESTORATION = "decision_restoration"
    """A request to restore a suspended decision."""
    
    DECISION_TERMINATION = "decision_termination"
    """A request to terminate a decision."""
    
    DECISION_CONTINUATION = "decision_continuation"
    """A continuation of an existing decision."""
    
    DECISION_OUTCOME = "decision_outcome"
    """The outcome of a completed decision process."""
    
    GENERAL_EXECUTIVE_INTENT = "general_executive_intent"
    """General executive intent without specific commitment."""


# =============================================================================
# DECISION COORDINATION TARGET KINDS
# =============================================================================


class ExecutiveDecisionCoordinationTargetKind(Enum):
    """
    Kinds of coordination targets.
    
    Each represents a canonical subsystem that may participate in decision
    realization while retaining full ownership.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Planning-related
    PLANNING = "planning"
    """Plan generation and refinement."""
    
    REASONING = "reasoning"
    """Semantic analysis and evidence evaluation."""
    
    STRATEGY = "strategy"
    """Strategy selection and revision."""
    
    # Goal and commitment systems
    GOAL_SYSTEM = "goal_system"
    """Goal maintenance and progress tracking."""
    
    COMMITMENT_SYSTEM = "commitment_system"
    """Commitment validation and enforcement."""
    
    # Policy and security
    POLICY = "policy"
    """Policy application and compliance verification."""
    
    SECURITY = "security"
    """Authorization review and security evaluation."""
    
    # Attention and focus
    ALERTING_NETWORK = "alerting_network"
    """Exogenous attention notifications."""
    
    FOCUSING_NETWORK = "focusing_network"
    """Endogenous focus coordination."""
    
    DEFAULT_NETWORK = "default_network"
    """Internally oriented cognition coordination."""
    
    # Memory systems
    MEMORY_CAPABILITY = "memory_capability"
    """Durable memory operations."""
    
    WORKING_MEMORY = "working_memory"
    """Active cognitive content maintenance."""
    
    WORKSPACE = "workspace"
    """Shared active representation substrate."""
    
    # Monitoring and recovery
    MONITORING = "monitoring"
    """State observation and anomaly detection."""
    
    RECOVERY = "recovery"
    """Error recovery and state restoration."""
    
    LEARNING = "learning"
    """Pattern recognition and adaptation."""
    
    # Action selection and execution
    ACTION_SELECTION = "action_selection"
    """Action candidate assessment and selection."""
    
    EXECUTION = "execution"
    """Task execution and runtime progression."""
    
    # Executive subsystems
    EXECUTIVE_STATE = "executive_state"
    """Executive state updates through canonical deltas."""
    
    EXECUTIVE_PROGRAM = "executive_program"
    """Program-level coordination."""
    
    EXECUTIVE_TASK_SET = "executive_task_set"
    """Task set coordination."""


# =============================================================================
# DECISION COORDINATION PURPOSES
# =============================================================================


class ExecutiveDecisionCoordinationPurpose(Enum):
    """
    Purposes of decision coordination.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Core coordination purposes
    PROJECT_DECISION_REQUIREMENTS = "project_decision_requirements"
    """Project requirements from accepted Decision Commitment."""
    
    PRESERVE_DECISION_CONSTRAINTS = "preserve_decision_constraints"
    """Preserve constraints defined by the Decision."""
    
    REQUEST_PLANNING = "request_planning"
    """Request plan generation or refinement."""
    
    REQUEST_REASONING = "request_reasoning"
    """Request semantic analysis or evidence evaluation."""
    
    REQUEST_POLICY_REVIEW = "request_policy_review"
    """Request policy compliance review."""
    
    REQUEST_SECURITY_REVIEW = "request_security_review"
    """Request security authorization review."""
    
    REQUEST_ATTENTION_REVIEW = "request_attention_review"
    """Request attention/focus coordination."""
    
    REQUEST_WORKING_MEMORY_SUPPORT = "request_working_memory_support"
    """Request Working Memory support for decision context."""
    
    REQUEST_WORKSPACE_REVIEW = "request_workspace_review"
    """Request Workspace state review."""
    
    REQUEST_MONITORING = "request_monitoring"
    """Request monitoring configuration."""
    
    REQUEST_RECOVERY = "request_recovery"
    """Request recovery planning."""
    
    REQUEST_LEARNING_REVIEW = "request_learning_review"
    """Request Learning system review for adaptation."""
    
    PREPARE_ACTION_SELECTION = "prepare_action_selection"
    """Prepare Action Selection request from Decision Commitment."""
    
    PRESERVE_EXECUTIVE_CONTINUITY = "preserve_executive_continuity"
    """Preserve executive continuity across coordination rounds."""
    
    COORDINATE_DECISION_REVISION = "coordinate_decision_revision"
    """Coordinate a decision revision with downstream systems."""
    
    COORDINATE_DECISION_SUSPENSION = "coordinate_decision_suspension"
    """Coordinate a decision suspension."""
    
    COORDINATE_DECISION_RESTORATION = "coordinate_decision_restoration"
    """Coordinate a decision restoration."""
    
    COORDINATE_DECISION_REPLACEMENT = "coordinate_decision_replacement"
    """Coordinate a decision replacement."""
    
    COORDINATE_DECISION_TERMINATION = "coordinate_decision_termination"
    """Coordinate a decision termination."""
    
    COORDINATE_DECISION_OUTCOME = "coordinate_decision_outcome"
    """Coordinate the outcome of a completed decision process."""
    
    GENERAL_COORDINATION = "general_coordination"
    """General coordination without specific purpose."""


# =============================================================================
# DECISION COORDINATION KINDS
# =============================================================================


class ExecutiveDecisionCoordinationKind(Enum):
    """
    Kinds of coordination activities.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    REQUIREMENT_PROJECTION = "requirement_projection"
    """Project requirements to downstream systems."""
    
    CONSTRAINT_PROJECTION = "constraint_projection"
    """Project constraints to downstream systems."""
    
    CONTEXT_PROJECTION = "context_projection"
    """Project context to downstream systems."""
    
    EVIDENCE_REQUEST = "evidence_request"
    """Request evidence evaluation or synthesis."""
    
    ANALYSIS_REQUEST = "analysis_request"
    """Request semantic analysis."""
    
    PLAN_REQUEST = "plan_request"
    """Request plan generation or refinement."""
    
    REVIEW_REQUEST = "review_request"
    """Request system review or assessment."""
    
    AUTHORITY_REQUEST = "authority_request"
    """Request authority validation."""
    
    MAINTENANCE_REQUEST = "maintenance_request"
    """Request state maintenance or preservation."""
    
    RECONFIGURATION_REQUEST = "reconfiguration_request"
    """Request subsystem reconfiguration."""
    
    MONITORING_REQUEST = "monitoring_request"
    """Request monitoring configuration."""
    
    RECOVERY_REQUEST = "recovery_request"
    """Request recovery planning."""
    
    LEARNING_REVIEW_REQUEST = "learning_review_request"
    """Request Learning system review."""
    
    ACTION_SELECTION_REQUEST_PREPARATION = "action_selection_request_preparation"
    """Prepare Action Selection request."""
    
    STATE_INTEGRATION = "state_integration"
    """Integrate decision state with subsystems."""
    
    CONTINUATION_COORDINATION = "continuation_coordination"
    """Coordinate continuation requirements."""
    
    OUTCOME_COORDINATION = "outcome_coordination"
    """Coordinate outcome integration."""
    
    GENERAL_COORDINATION = "general_coordination"
    """General coordination without specific kind."""


# =============================================================================
# DECISION COORDINATION REQUIREMENT KINDS
# =============================================================================


class ExecutiveDecisionCoordinationRequirementKind(Enum):
    """
    Kinds of coordination requirements.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    PRESERVE_DECISION_IDENTITY = "preserve_decision_identity"
    """Preserve the Decision Identity across all projections."""
    
    PRESERVE_DECISION_REVISION = "preserve_decision_revision"
    """Preserve the current Decision revision number."""
    
    PRESERVE_DECISION_AUTHORITY = "preserve_decision_authority"
    """Preserve the authority that created the Decision."""
    
    PRESERVE_SCOPE = "preserve_scope"
    """Preserve the Decision scope in projections."""
    
    PRESERVE_CONSTRAINT = "preserve_constraint"
    """Preserve Decision constraints."""
    
    PRESERVE_COMMITMENT = "preserve_commitment"
    """Preserve the Decision commitment status."""
    
    PRESERVE_GOAL = "preserve_goal"
    """Preserve goal bindings from Decision."""
    
    PRESERVE_STRATEGY = "preserve_strategy"
    """Preserve strategy bindings from Decision."""
    
    PRESERVE_POLICY = "preserve_policy"
    """Preserve policy constraints from Decision."""
    
    PRESERVE_SECURITY = "preserve_security"
    """Preserve security constraints from Decision."""
    
    PRESERVE_PRIVACY = "preserve_privacy"
    """Preserve privacy requirements from Decision."""
    
    PRESERVE_PROVENANCE = "preserve_provenance"
    """Preserve provenance information across projections."""
    
    SATISFY_PRECONDITION = "satisfy_precondition"
    """Satisfy a precondition before coordination completes."""
    
    RETURN_PLAN = "return_plan"
    """Return a plan from Planning system."""
    
    RETURN_REASONING_RESULT = "return_reasoning_result"
    """Return reasoning results."""
    
    RETURN_POLICY_REVIEW = "return_policy_review"
    """Return policy review assessment."""
    
    RETURN_SECURITY_REVIEW = "return_security_review"
    """Return security review assessment."""
    
    RETURN_ATTENTION_ASSESSMENT = "return_attention_assessment"
    """Return attention/focus assessment."""
    
    RETURN_WORKING_MEMORY_ASSESSMENT = "return_working_memory_assessment"
    """Return Working Memory state assessment."""
    
    RETURN_WORKSPACE_ASSESSMENT = "return_workspace_assessment"
    """Return Workspace state assessment."""
    
    RETURN_MONITORING_ASSESSMENT = "return_monitoring_assessment"
    """Return monitoring configuration assessment."""
    
    RETURN_RECOVERY_ASSESSMENT = "return_recovery_assessment"
    """Return recovery planning assessment."""
    
    RETURN_LEARNING_RECOMMENDATION = "return_learning_recommendation"
    """Return Learning system recommendations."""
    
    RETURN_ACTION_SELECTION_OUTCOME = "return_action_selection_outcome"
    """Return Action Selection outcome."""
    
    REPORT_INCOMPATIBILITY = "report_incompatibility"
    """Report an incompatibility with downstream systems."""
    
    REPORT_MISSING_AUTHORITY = "report_missing_authority"
    """Report missing authority for coordination."""
    
    REPORT_MISSING_CONTEXT = "report_missing_context"
    """Report missing context for coordination."""
    
    REPORT_STALE_REVISION = "report_stale_revision"
    """Report that a revision is stale."""