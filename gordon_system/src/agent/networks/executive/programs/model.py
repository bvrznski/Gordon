# Executive Program Model
# =======================

"""
Canonical ExecutiveProgram and ExecutiveTaskSet immutable dataclasses.

These are the core semantic structures for Phase 4.4.3 - the authoritative,
bounded, revisioned representations of executive task organization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from enum import Enum

# Import from sibling modules
from gordon_system.src.agent.networks.executive.programs.state import (
    ExecutiveProgramState,
    ExecutiveProgramRevision,
)


# =============================================================================
# EXECUTIVE PROGRAM - THE CORE SEMANTIC STRUCTURE
# =============================================================================


@dataclass(frozen=True)
class ExecutiveProgram:
    """
    Canonical semantic description of one coherent cognitive undertaking
    currently coordinated by the Executive Network.
    
    An ExecutiveProgram is NOT:
        - Executable code
        - A runtime Thread or coroutine
        - A plan to be executed (it's a semantic organization)
        - A goal (goals are components of programs)
        - Working Memory content
    
    An ExecutiveProgram IS:
        - The bounded semantic description of one cognitive undertaking
        - Immutable data describing WHAT is being pursued and HOW it's organized
        - Owned exclusively by the Executive Network
        - The central representation through which Gordon organizes cognition
    
    Program properties:
        - Immutable: No in-place modification; use transitions for changes
        - Bounded: All collections have capacity limits
        - Revisioned: Each program has an increasing revision number
        - Deterministic: Identical inputs produce identical outputs
        - Serializable: Can be converted to/from dict for storage
    
    Ownership hierarchy:
        ExecutiveProgram (owned by Executive Network)
            |
            +-- ExecutiveTaskSet (owned BY the program, not referenced)
            |     |
            |     +-- Active goals
            |     +-- Active commitments
            |     +-- Constraints
            |     +-- Policies
            |
            +-- Child programs (delegated/parent relationship)
    
    PROGRAM-OWNED RESOURCES:
        - Task set and all its contents
        - All child programs
        - Control agenda, stack, focus for this program
        - Program history and revision chain
    
    EXTERNAL REFERENCES (not ownership):
        - Strategy reference (strategy is owned by Strategy Network)
        - External request/result references (external systems own these)
        - Working memory state references (WM owns content)
        - Workspace admission state references (Workspace owns admission)
    """
    
    # Identity and revisioning
    program_id: str = "exec_program_initial"
    """Unique identifier for this program instance."""
    
    revision: ExecutiveProgramRevision = field(default_factory=ExecutiveProgramRevision.initial)
    """Current revision number with schema version tracking."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # State and lifecycle
    state: ExecutiveProgramState = ExecutiveProgramState.CREATED
    """Current semantic lifecycle state."""
    
    priority: int = 50
    """Priority level (higher = more urgent)."""
    
    activation: float = 1.0
    """Activation strength (0.0 to 1.0)."""
    
    # Task set - program OWNS this, does not reference it
    task_set_id: str = "exec_taskset_initial"
    """ID of the task set owned by this program."""
    
    task_set_created_at_utc: float = 0.0
    """When the task set was created (seconds since epoch)."""
    
    # Goal bindings - program-owned collection of goal references with metadata
    goal_bindings: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals bound to this program."""
    
    # Commitment bindings - program-owned collection of commitment references
    commitment_bindings: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of commitments bound to this program."""
    
    # Strategy reference (program does NOT own strategy)
    strategy_reference_id: Optional[str] = None
    """ID of referenced strategy (owned by Strategy Network)."""
    
    # Control policy - program-owned semantic policy for how organization proceeds
    control_policy_id: str = "exec_policy_default"
    """ID of the control policy applied to this program."""
    
    # Control agenda - ordered semantic objectives for this program
    agenda_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of agenda entries in order of priority."""
    
    # Control stack - nested executive programs (semantic frames, not function calls)
    control_stack_frame_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of stack frames representing nested program ownership."""
    
    # Control focus - which program currently owns resources
    focus_program_id: Optional[str] = None
    """ID of the program that currently has executive focus."""
    
    # Completion conditions - when this program is considered complete
    completion_conditions_met: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of satisfied completion conditions."""
    
    # Interruption policy - what may interrupt this program
    interruption_policy_id: str = "interruptible"
    """ID of the interruption policy (e.g., 'non-interruptible', 'preemptive')."""
    
    # Recovery policy - how to handle failure
    recovery_policy_id: str = "retry-on-failure"
    """ID of the recovery policy (e.g., 'abort-on-failure', 'fallback-to-alternative')."""
    
    # Authority and ownership
    authority_id: Optional[str] = None
    """ID of the authority that authorized this program."""
    
    created_by: str = "executive_network"
    """Who/what created this program."""
    
    created_from: Optional[str] = None
    """Source that triggered creation (e.g., 'user_request_123')."""
    
    # Hierarchy - parent-child relationships
    parent_program_id: Optional[str] = None
    """ID of parent program (if delegated)."""
    
    child_program_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child programs created by this program."""
    
    history: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of historical events in this program's lifecycle."""
    
    # Semantic evaluations
    confidence: float = 0.5
    """Confidence that the program is well-formed."""
    
    consistency: float = 1.0
    """Consistency of goals, commitments, and constraints."""
    
    coherence: float = 1.0
    """Coherence of organizational structure."""
    
    # Privacy and provenance
    privacy_classification: str = "internal"
    """Privacy classification (e.g., 'public', 'internal', 'confidential')."""
    
    provenance_created_at_utc: float = 0.0
    """When program was created (seconds since epoch)."""
    
    @classmethod
    def initial(
        cls,
        program_id: str = "exec_program_initial",
        task_set_id: str = "exec_taskset_initial",
    ) -> ExecutiveProgram:
        """
        Create an initial executive program.
        
        Args:
            program_id: Unique identifier for the new program
            task_set_id: ID of the initially created task set
            
        Returns:
            New program in CREATED state with initial revision
        """
        return cls(
            program_id=program_id,
            revision=ExecutiveProgramRevision.initial(),
            schema_version="1.0.0",
            state=ExecutiveProgramState.CREATED,
            task_set_id=task_set_id,
            task_set_created_at_utc=0.0,
            priority=50,
            activation=1.0,
        )
    
    @property
    def is_terminal(self) -> bool:
        """Check if program has reached a terminal state."""
        return self.state in (
            ExecutiveProgramState.COMPLETED,
            ExecutiveProgramState.FAILED,
            ExecutiveProgramState.ABANDONED,
            ExecutiveProgramState.TERMINATED,
        )
    
    @property
    def is_active(self) -> bool:
        """Check if program is currently active."""
        return self.state in (
            ExecutiveProgramState.ACTIVE,
            ExecutiveProgramState.RESUMING,
            ExecutiveProgramState.WAITING,
        )


# =============================================================================
# EXECUTIVE TASK SET - THE COLLECTION OF COGNITIVE RESOURCES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveTaskSet:
    """
    Collection of cognitive resources, commitments, control policies, and
    references currently required to pursue one ExecutiveProgram.
    
    Task Sets are owned by the Executive Program (not vice versa).
    
    A task set is NOT:
        - An execution queue
        - A list of actions to perform
        - Working Memory content
        - Workspace contents
    
    A task set IS:
        - The semantic collection of resources needed for one program
        - Bounded by capacity limits
        - Revisioned for deterministic reconstruction
        - Referenced BY the ExecutiveProgram, owned BY it
    
    Task Set properties:
        - Immutable: No in-place modification; create new instance for changes
        - Bounded: All collections have maximum capacities
        - Revisioned: Each task set has an increasing revision number
        - Deterministic: Same inputs produce same outputs
    """
    
    # Identity and revisioning
    task_set_id: str = "exec_taskset_initial"
    """Unique identifier for this task set."""
    
    revision: int = 1
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Active goals - goals currently being pursued
    active_goals: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active goals."""
    
    # Active commitments - binding obligations
    active_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently active commitments."""
    
    # Constraints that must be satisfied
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of applicable constraints."""
    
    # Required capabilities (external system capabilities needed)
    required_capabilities: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required capability references."""
    
    # External state references (not contents - just references)
    required_memory_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required Working Memory state references."""
    
    required_workspace_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required Workspace admission state references."""
    
    # Attention requirements (how much focus is needed)
    required_attention: int = 1
    """Amount of executive attention required (1-10)."""
    
    # Reasoning requirements
    required_planning: bool = False
    """Whether planning capability is required."""
    
    required_reasoning: bool = True
    """Whether reasoning capability is required."""
    
    required_monitoring: bool = False
    """Whether monitoring capability is required."""
    
    required_predictions: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required prediction references."""
    
    required_evaluations: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required evaluation references."""
    
    # Policy requirements
    required_policies: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required policy references."""
    
    required_security_constraints: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required security constraint references."""
    
    # Execution context references (external state only)
    required_execution_context_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of required execution context state references."""
    
    # Active control bindings - external systems providing resources
    active_control_bindings: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active control binding references."""
    
    # Bounded capacities
    max_goals: int = 20
    """Maximum goals allowed in this task set."""
    
    max_commitments: int = 20
    """Maximum commitments allowed in this task set."""
    
    max_constraints: int = 50
    """Maximum constraints allowed in this task set."""
    
    @classmethod
    def initial(
        cls,
        task_set_id: str = "exec_taskset_initial",
    ) -> ExecutiveTaskSet:
        """
        Create an initial executive task set.
        
        Args:
            task_set_id: Unique identifier for the new task set
            
        Returns:
            New task set with empty collections
        """
        return cls(
            task_set_id=task_set_id,
            revision=1,
            schema_version="1.0.0",
        )
    
    def is_capacity_exceeded(self) -> Tuple[str, ...]:
        """
        Check if any capacity limits are exceeded.
        
        Returns:
            Tuple of constraint names that are violated (empty if all OK)
        """
        violations = []
        if len(self.active_goals) > self.max_goals:
            violations.append("max_goals")
        if len(self.active_commitments) > self.max_commitments:
            violations.append("max_commitments")
        if len(self.constraints) > self.max_constraints:
            violations.append("max_constraints")
        return tuple(violations)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveProgram",
    "ExecutiveTaskSet",
)