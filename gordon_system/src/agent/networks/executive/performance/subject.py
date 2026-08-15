# Executive Performance Subject
# ==============================

"""
Canonical immutable ExecutivePerformanceSubject definitions.

Performance subjects are what is being assessed - programs, task sets,
strategies, decisions, actions, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutivePerformanceSubject:
    """
    Immutable reference to a performance subject.

    A performance subject is the entity being assessed for executive performance.
    Each subject must preserve identity, revision, owner, authority, scope,
    and provenance.
    """

    subject_id: str
    """Unique identifier for this performance subject."""

    kind: str  # ExecutivePerformanceSubjectKind value
    """The semantic category of the performance subject."""

    owner: str = "executive_network_internal"
    """Owner of this subject (authority reference)."""

    authority: str = "EXECUTIVE_NETWORK_INTERNAL"
    """Authority class for this subject."""

    scope: Tuple[str, ...] = ()
    """Bounded scope of affected systems."""

    provenance_created_by: str = "unknown"
    """Who/what created this subject reference."""

    provenance_created_at_utc: float = 0.0
    """When this subject was referenced (seconds since epoch)."""

    @classmethod
    def for_program(cls, program_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing an ExecutiveProgram."""
        return cls(
            subject_id=program_id,
            kind="EXECUTIVE_PROGRAM",
            owner="executive_network_internal",
            authority="EXECUTIVE_NETWORK_INTERNAL",
        )

    @classmethod
    def for_task_set(cls, task_set_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing an ExecutiveTaskSet."""
        return cls(
            subject_id=task_set_id,
            kind="EXECUTIVE_TASK_SET",
            owner="executive_network_internal",
            authority="EXECUTIVE_NETWORK_INTERNAL",
        )

    @classmethod
    def for_goal(cls, goal_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing an executive goal."""
        return cls(
            subject_id=goal_id,
            kind="GOAL",
            owner="executive_network_internal",
            authority="EXECUTIVE_AUTHORITY",
        )

    @classmethod
    def for_commitment(cls, commitment_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing an executive commitment."""
        return cls(
            subject_id=commitment_id,
            kind="COMMITMENT",
            owner="executive_network_internal",
            authority="EXECUTIVE_AUTHORITY",
        )

    @classmethod
    def for_strategy(cls, strategy_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing an executive strategy."""
        return cls(
            subject_id=strategy_id,
            kind="STRATEGY",
            owner="executive_network_internal",
            authority="EXECUTIVE_NETWORK_INTERNAL",
        )

    @classmethod
    def for_control_allocation(cls, control_id: str) -> ExecutivePerformanceSubject:
        """Create a subject referencing a control allocation."""
        return cls(
            subject_id=control_id,
            kind="CONTROL_ALLOCATION",
            owner="executive_network_internal",
            authority="EXECUTIVE_NETWORK_INTERNAL",
        )


class ExecutivePerformanceSubjectKind:
    """
    Typed taxonomy of executive performance subject kinds.

    Each kind represents a distinct semantic category of what can be assessed
    for executive performance.
    """

    # Core program and task set subjects
    EXECUTIVE_PROGRAM = "EXECUTIVE_PROGRAM"
    """An active ExecutiveProgram."""

    EXECUTIVE_TASK_SET = "EXECUTIVE_TASK_SET"
    """An active ExecutiveTaskSet."""

    # Goal and commitment subjects
    GOAL = "GOAL"
    """A goal being pursued."""

    COMMITMENT = "COMMITMENT"
    """A commitment being fulfilled."""

    # Strategy and planning subjects
    STRATEGY = "STRATEGY"
    """An executive strategy being applied."""

    PLAN = "PLAN"
    """An active plan."""

    REASONING_PROCESS = "REASONING_PROCESS"
    """The current reasoning process."""

    DECISION_PROCESS = "DECISION_PROCESS"
    """The current decision process."""

    # Control and execution subjects
    CONTROL_ALLOCATION = "CONTROL_ALLOCATION"
    """A control allocation configuration."""

    INHIBITION_CONFIGURATION = "INHIBITION_CONFIGURATION"
    """An inhibition configuration."""

    SWITCHING_DECISION = "SWITCHING_DECISION"
    """A switching decision."""

    RECOVERY_ATTEMPT = "RECOVERY_ATTEMPT"
    """A recovery attempt."""

    # Monitoring and assessment subjects
    MONITORING_CONFIGURATION = "MONITORING_CONFIGURATION"
    """A monitoring configuration."""

    COMMUNICATION_ATTEMPT = "COMMUNICATION_ATTEMPT"
    """A communication attempt."""

    WORKING_MEMORY_MAINTENANCE = "WORKING_MEMORY_MAINTENANCE"
    """Working memory maintenance effort."""

    FOCUS_CONFIGURATION = "FOCUS_CONFIGURATION"
    """Focus configuration."""

    # General subjects
    GENERAL_EXECUTIVE_UNDERTAKING = "GENERAL_EXECUTIVE_UNDERTAKING"
    """A general executive undertaking not fitting other categories."""

    UNKNOWN = "UNKNOWN"
    """Unknown or unclassified subject kind."""

    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds as a tuple."""
        return (
            cls.EXECUTIVE_PROGRAM,
            cls.EXECUTIVE_TASK_SET,
            cls.GOAL,
            cls.COMMITMENT,
            cls.STRATEGY,
            cls.PLAN,
            cls.REASONING_PROCESS,
            cls.DECISION_PROCESS,
            cls.CONTROL_ALLOCATION,
            cls.INHIBITION_CONFIGURATION,
            cls.SWITCHING_DECISION,
            cls.RECOVERY_ATTEMPT,
            cls.MONITORING_CONFIGURATION,
            cls.COMMUNICATION_ATTEMPT,
            cls.WORKING_MEMORY_MAINTENANCE,
            cls.FOCUS_CONFIGURATION,
            cls.GENERAL_EXECUTIVE_UNDERTAKING,
            cls.UNKNOWN,
        )


__all__: Tuple[str, ...] = (
    "ExecutivePerformanceSubject",
    "ExecutivePerformanceSubjectKind",
)