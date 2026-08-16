# Executive Programs Package
# =========================

"""
Executive Programs - Canonical semantic architecture for executive task sets
and active programs in Phase 4.4.3.

This package defines the persistent semantic structures through which Gordon
organizes ongoing cognition, without implementing the algorithms that operate on them.

ARCHITECTURAL PRINCIPLES
=========================

EXEC-PROGRAM-001: Program owns Task Set
    An ExecutiveProgram always owns its ExecutiveTaskSet.
    The task set is part of the program's semantic organization,
    not a separate entity.

EXEC-PROGRAM-002: Task Set never owns Program
    Task sets are owned by programs, never vice versa.
    This ensures unambiguous ownership and prevents circular dependencies.

EXEC-PROGRAM-003: Programs are immutable
    ExecutiveProgram instances are completely immutable dataclasses.
    All state changes occur via transitions creating new program instances.

EXEC-PROGRAM-004: Programs contain semantic organization only
    Programs describe WHAT is being pursued, not HOW it's executed.
    They never contain implementation logic, threads, or coroutines.

EXEC-PROGRAM-005: Programs never execute themselves
    Executive programs are descriptions, not executable code.
    They may be interpreted by executive execution systems,
    but they do not perform actions directly.

EXEC-PROGRAM-006: Programs never own runtime Threads
    Runtime execution state is owned by the Execution Network.
    Programs reference external thread state only.

EXEC-PROGRAM-007: Programs reference external state
    Programs may contain references to Working Memory, Workspace,
    and other subsystems, but they never duplicate their contents.

EXEC-PROGRAM-008: Programs never duplicate Working Memory
    Working Memory content is owned by the Working Memory Network.
    Programs reference WM state only.

EXEC-PROGRAM-009: Programs never duplicate Workspace
    Workspace admission state is owned by the Workspace Network.
    Programs reference workspace state only.

EXEC-PROGRAM-010: Programs remain bounded
    All collections have capacity limits. No unbounded growth.

EXEC-PROGRAM-011: Programs are semantic, not executable
    A program is a description of cognitive organization.
    It may be interpreted by executive execution systems,
    but the program itself is not code.

EXEC-PROGRAM-012: Executive owns all programs and task sets
    Only the Executive Network may create or modify programs.
    No other subsystem may alter them directly.

EXEC-PROGRAM-013: Control authority is explicit
    The control_focus identifies which program currently owns
    executive resources. This is distinct from attention allocation.

EXEC-PROGRAM-014: Lifecycle is deterministic
    All transitions between states follow strict, reproducible rules.
    Given the same inputs, the same outputs are always produced.

EXEC-PROGRAM-015: Revisions are explicit
    Every state change produces a new revision with strictly
    increasing revision number. No in-place modification.

EXEC-PROGRAM-016: History is bounded
    Program history maintains only essential transitions,
    not runtime traces or detailed logs.

EXEC-PROGRAM-017: Serialization is stable
    Programs may be serialized and deserialized without loss
    of semantic meaning. Reconstructable from serialized form.

EXEC-PROGRAM-018: Ownership hierarchy is explicit
    Parent programs may delegate to child programs.
    Delegated programs maintain their own identity.

EXEC-PROGRAM-019: Task switching is explicit
    When a program is suspended, its state is preserved.
    Resumption continues from the last suspended state.

EXEC-PROGRAM-020: Priority determines execution order
    Programs and tasks within programs have priorities.
    Higher priority items receive executive resources first.

EXEC-PROGRAM-021: Commitments create obligations
    When a goal is committed, it becomes binding.
    Committed goals may only be abandoned explicitly.

EXEC-PROGRAM-022: Constraints bound behavior
    All programs specify constraints that must be satisfied.
    Violation of constraints may cause program failure.

EXEC-PROGRAM-023: Strategy determines approach
    Each program has an associated strategy reference.
    The strategy describes how objectives will be achieved.

EXEC-PROGRAM-024: Completion conditions are explicit
    A program specifies when it is complete.
    Completion may be partial or full.

EXEC-PROGRAM-025: Interruption policy is specified
    Each program defines what may interrupt it.
    Some programs may be non-interruptible.

EXEC-PROGRAM-026: Recovery policy is specified
    If a program fails, its recovery policy determines
    how failure is handled and whether retry is attempted.

EXEC-PROGRAM-027: Authority must be established
    Programs require authority to operate.
    Authority may come from parent programs or external sources.

EXEC-PROGRAM-028: Privacy classification applies
    All programs have privacy classifications.
    Sensitive programs may not share data with others.

EXEC-PROGRAM-029: Provenance is tracked
    Every program records who/what created it and when.
    This enables auditing and debugging.

EXEC-PROGRAM-030: Confidence measures validity
    Each program has a confidence classification
    indicating how well-formed and valid it is.

EXEC-PROGRAM-031: Coherence measures consistency
    Coherence indicates whether the program's
    goals, commitments, and constraints align.

EXEC-PROGRAM-032: Completeness measures adequacy
    A program is complete when all required elements
    are present for its intended purpose.

EXEC-PROGRAM-033: Goal alignment must be maintained
    All goals within a task set must align with the
    primary objective of the program.

EXEC-PROGRAM-034: Commitment alignment must be maintained
    All commitments must support the goals they serve.
    Conflicting commitments cause program failure.

EXEC-PROGRAM-035: Strategy must match objectives
    The strategy reference must be appropriate for
    achieving the program's primary objective.

EXEC-PROGRAM-036: Control stack is bounded
    The control stack has a maximum depth to prevent
    unbounded nesting and ensure termination.

EXEC-PROGRAM-037: Focus shifts explicitly
    Executive focus may shift from one program to another.
    The previous program may be suspended or terminated.

EXEC-PROGRAM-038: Parent-child relationships are explicit
    Child programs inherit authority from parents.
    Parents may terminate children if necessary.

EXEC-PROGRAM-039: Replacement is possible
    If a program becomes obsolete, it may be replaced
    by another program. The old program is terminated.

EXEC-PROGRAM-040: Temporary programs exist
    Some programs are created for short-term tasks.
    They are automatically cleaned up when complete.

EXEC-PROGRAM-041: Delegated programs execute on behalf
    Delegation allows one program to request another
    perform specific tasks while maintaining control.

EXEC-PROGRAM-042: Background programs run asynchronously
    Background programs operate without direct user
    interaction. They may be interrupted more easily.

EXEC-PROGRAM-043: Recovery programs handle failures
    If a program fails, its recovery program is activated.
    The recovery program attempts to restore normal operation.

EXEC-PROGRAM-044: Maintenance programs ensure health
    Maintenance programs run periodically to check system
    health and perform routine tasks.

EXEC-PROGRAM-045: Monitoring is explicit
    Programs may specify monitoring requirements.
    Monitoring tracks progress and detects issues.

EXEC-PROGRAM-046: Evaluation is part of program structure
    Programs may include evaluation criteria.
    These determine whether objectives are being met.

EXEC-PROGRAM-047: Active control bindings track resources
    Control bindings reference external systems providing
    resources required by the program.

EXEC-PROGRAM-048: Required capabilities are specified
    A task set specifies what capabilities must be available
    for successful completion.

EXEC-PROGRAM-049: Attention requirements are explicit
    Programs may specify attention requirements.
    These determine how much focus is needed.

EXEC-PROGRAM-050: Reasoning and planning requirements are explicit
    Programs may require specific reasoning or planning
    capabilities. These are specified in the task set.
"""

from __future__ import annotations

# =============================================================================
# CORE PROGRAM TYPES (Phase 4.4.3)
# =============================================================================

from gordon_system.src.agent.networks.executive.programs.model import (
    ExecutiveProgram,
    ExecutiveTaskSet,
)

from gordon_system.src.agent.networks.executive.programs.frames import (
    ExecutiveProgramFrame,
)

from gordon_system.src.agent.networks.executive.programs.goals import (
    ExecutiveGoalBinding,
    ExecutiveCommitmentBinding,
)

from gordon_system.src.agent.networks.executive.programs.constraints import (
    ExecutiveConstraintSet,
    ExecutiveControlPolicy,
)

from gordon_system.src.agent.networks.executive.programs.objectives import (
    ExecutiveControlObjective,
    ExecutiveControlAgenda,
)

from gordon_system.src.agent.networks.executive.programs.stack import (
    ExecutiveControlStack,
)

from gordon_system.src.agent.networks.executive.programs.focus import (
    ExecutiveControlFocus,
)

from gordon_system.src.agent.networks.executive.programs.state import (
    ExecutiveProgramState,
    ExecutiveProgramRevision,
)

# Transitions and transitions kind are in focus module
from gordon_system.src.agent.networks.executive.programs.focus import (
    ExecutiveProgramTransition,
    ExecutiveProgramTransitionKind,
)

from gordon_system.src.agent.networks.executive.programs.history import (
    ExecutiveProgramHistoryEntry,
    ExecutiveProgramHistory,
)

from gordon_system.src.agent.networks.executive.programs.snapshots import (
    ExecutiveProgramSnapshot,
)

from gordon_system.src.agent.networks.executive.programs.validation import (
    ExecutiveProgramValidation,
    ExecutiveProgramConsistency,
)

from gordon_system.src.agent.networks.executive.programs.serialization import (
    ExecutiveProgramSerialization,
    serialize_program_to_dict,
    deserialize_program_from_dict,
)

__all__ = (
    # Core program types
    "ExecutiveProgram",
    "ExecutiveTaskSet",
    
    # Program frames
    "ExecutiveProgramFrame",
    
    # Bindings
    "ExecutiveGoalBinding",
    "ExecutiveCommitmentBinding",
    
    # Constraints and policies
    "ExecutiveConstraintSet",
    "ExecutiveControlPolicy",
    
    # Control structures
    "ExecutiveControlObjective",
    "ExecutiveControlAgenda",
    "ExecutiveControlStack",
    "ExecutiveControlFocus",
    
    # Program state and lifecycle
    "ExecutiveProgramState",
    "ExecutiveProgramRevision",
    
    # Transitions and history (from focus module)
    "ExecutiveProgramTransition",
    "ExecutiveProgramTransitionKind",
    
    # History
    "ExecutiveProgramHistoryEntry",
    "ExecutiveProgramHistory",
    
    # Snapshots
    "ExecutiveProgramSnapshot",
    
    # Validation
    "ExecutiveProgramValidation",
    "ExecutiveProgramConsistency",
    
    # Serialization
    "ExecutiveProgramSerialization",
    "serialize_program_to_dict",
    "deserialize_program_from_dict",
)