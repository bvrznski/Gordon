# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Cycle Lifecycle Models
===================================

Canonical immutable models for coordination cycle lifecycle states.

CYCLE LIFECYCLE OVERVIEW
------------------------
A CoordinationCycle progresses through explicit lifecycle states:

CREATED -> COLLECTING -> VALIDATING -> WAITING/READY -> SYNCHRONIZING ->
BUILDING_STATE -> READY_TO_PUBLISH -> COMPLETE

Any stage may transition to:
- FAILED (if an error occurs)
- SUPERSEDED (if a newer cycle replaces this one)

LIFECYCLE INVARIANTS
====================
- Lifecycle transitions remain explicit and validated
- Cycles remain immutable after completion
- Failed cycles preserve failure findings
- Completed cycles preserve all state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# COORDINATION CYCLE LIFECYCLE STATUS
# =============================================================================

class CoordinationCycleLifecycleStatus(Enum):
    """
    Canonical lifecycle status for coordination cycles.
    
    CYCLE-LIFECYCLE-INV-001: Lifecycle status is immutable once set
    
    VALID TRANSITIONS:
    - CREATED -> COLLECTING
    - COLLECTING -> VALIDATING
    - VALIDATING -> WAITING (if barrier not ready)
    - VALIDATING -> READY_TO_SYNCHRONIZE (if ready to synchronize)
    - WAITING -> VALIDATING (after conditions met)
    - READY_TO_SYNCHRONIZE -> SYNCHRONIZING
    - SYNCHRONIZING -> BUILDING_STATE
    - BUILDING_STATE -> READY_TO_PUBLISH
    - READY_TO_PUBLISH -> COMPLETE
    
    ANY STATUS MAY TRANSITION TO:
    - FAILED (error condition)
    - SUPERSEDED (replaced by newer cycle)
    
    COMPLETED CYCLES ARE IMMUTABLE
    """
    CREATED = "created"
    """Cycle has been created but not yet processed."""
    
    COLLECTING = "collecting"
    """Collecting projections from participating networks."""
    
    VALIDATING = "validating"
    """Validating collected projections."""
    
    WAITING = "waiting"
    """Waiting for synchronization conditions (semantic waiting)."""
    
    READY_TO_SYNCHRONIZE = "ready_to_synchronize"
    """All conditions met, ready to synchronize."""
    
    SYNCHRONIZING = "synchronizing"
    """Performing synchronization."""
    
    BUILDING_STATE = "building_state"
    """Constructing CoordinationState."""
    
    READY_TO_PUBLISH = "ready_to_publish"
    """State is ready for publication."""
    
    COMPLETE = "complete"
    """Cycle completed successfully."""
    
    DEGRADED = "degraded"
    """Cycle completed with degraded coordination."""
    
    FAILED = "failed"
    """Cycle failed due to error or policy violation."""
    
    SUPERSEDED = "superseded"
    """Cycle has been superseded by a newer cycle."""
    
    UNKNOWN = "unknown"
    """Lifecycle status cannot be determined."""


# =============================================================================
# CYCLE KIND ENUM
# =============================================================================

class CoordinationCycleKind(Enum):
    """
    Canonical kinds of coordination cycles.
    
    CYCLE-KIND-INV-001: Cycle kind is immutable once set
    
    KINDS:
    - INITIAL: First cycle in an epoch
    - INCREMENTAL: Updates existing state incrementally
    - REVALIDATION: Revalidates existing projections without new output
    - TRANSITION: Handles network transition states
    - RECOVERY: Follows a failed or blocked cycle
    - DEGRADED: Intentionally scoped coordination with limitations
    - TERMINAL: Final cycle in an epoch
    """
    INITIAL = "initial"
    """Initial cycle in an epoch, establishes base state."""
    
    INCREMENTAL = "incremental"
    """Incremental update to existing CoordinationState."""
    
    REVALIDATION = "revalidation"
    """Revalidates existing projections without new output."""
    
    TRANSITION = "transition"
    """Handles network transition states."""
    
    RECOVERY = "recovery"
    """Follows a failed or blocked cycle."""
    
    DEGRADED = "degraded"
    """Intentionally scoped coordination with known limitations."""
    
    TERMINAL = "terminal"
    """Final cycle in an epoch."""
    
    UNKNOWN = "unknown"
    """Cycle kind cannot be determined."""


# =============================================================================
# VALID LIFECYCLE TRANSITIONS
# =============================================================================

@dataclass(frozen=True, slots=True)
class LifecycleTransitionValidator:
    """
    Immutable validator for lifecycle transitions.
    
    CYCLE-LIFECYCLE-VALID-INV-001: Validator is deterministic
    
    ALLOWED TRANSITIONS:
    - CREATED -> COLLECTING
    - COLLECTING -> VALIDATING
    - VALIDATING -> WAITING
    - VALIDATING -> READY_TO_SYNCHRONIZE
    - WAITING -> VALIDATING
    - READY_TO_SYNCHRONIZE -> SYNCHRONIZING
    - SYNCHRONIZING -> BUILDING_STATE
    - BUILDING_STATE -> READY_TO_PUBLISH
    - READY_TO_PUBLISH -> COMPLETE
    
    DEGRADED/FAILED/SUPERSEDED are terminal states
    """
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """
        Check if a transition is allowed.
        
        Args:
            from_status: Source lifecycle status
            to_status: Target lifecycle status
            
        Returns:
            True if the transition is valid, False otherwise
        """
        # Valid progressions
        progressions = {
            "created": ["collecting"],
            "collecting": ["validating"],
            "validating": ["waiting", "ready_to_synchronize"],
            "waiting": ["validating"],
            "ready_to_synchronize": ["synchronizing"],
            "synchronizing": ["building_state"],
            "building_state": ["ready_to_publish"],
            "ready_to_publish": ["complete"],
        }
        
        # Terminal states (cannot transition to another state)
        terminal = {"failed", "complete", "superseded", "degraded"}
        
        if from_status in terminal:
            return False
        
        allowed_targets = progressions.get(from_status, [])
        return to_status in allowed_targets
    
    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> tuple[bool, Optional[str]]:
        """
        Validate a lifecycle transition.
        
        Args:
            from_status: Source lifecycle status
            to_status: Target lifecycle status
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Check if target is terminal state that already exists
        terminal = {"failed", "complete", "superseded", "degraded"}
        if from_status in terminal and to_status != from_status:
            return False, f"Cannot transition from terminal status {from_status}"
        
        # Check if source is terminal
        if from_status in terminal:
            return True, None  # Terminal states allow staying in same state
        
        # Validate against progressions
        allowed_targets = {
            "created": ["collecting"],
            "collecting": ["validating"],
            "validating": ["waiting", "ready_to_synchronize"],
            "waiting": ["validating"],
            "ready_to_synchronize": ["synchronizing"],
            "synchronizing": ["building_state"],
            "building_state": ["ready_to_publish"],
            "ready_to_publish": ["complete"],
        }
        
        if to_status in allowed_targets.get(from_status, []):
            return True, None
        
        # Check for terminal transitions
        if from_status not in terminal and to_status in terminal:
            return True, None  # Can transition to any terminal state
        
        return False, f"Invalid transition: {from_status} -> {to_status}"


# =============================================================================
# COORDINATION CYCLE IDENTITY (re-exported with lifecycle context)
# =============================================================================

@dataclass(frozen=True, slots=True)
class TemporalCoordinationCycleIdentity:
    """
    Immutable identity for a coordination cycle.
    
    CYCLE-LAW-001: Every CoordinationCycle possesses stable semantic identity
    CYCLE-LAW-002: Cycle identity remains stable
    
    COORD-CYCLE-ID-INV-001: Identity is immutable (deeply frozen)
    COORD-CYCLE-ID-INV-002: Identity has no runtime references
    """
    cycle_id: str = ""
    """Unique identifier for the cycle."""
    
    sequence_index: int = 0
    """Sequence index within a coordination epoch."""
    
    parent_cycle_identity: Optional[str] = None
    """Reference to parent cycle if this is a revision."""
    
    cycle_kind: str = "unknown"
    """Kind of this cycle (from CoordinationCycleKind)."""
    
    @classmethod
    def from_epoch(cls, epoch_id: str) -> TemporalCoordinationCycleIdentity:
        """
        Create a cycle identity from an epoch string.
        
        Args:
            epoch_id: Epoch identifier
            
        Returns:
            A new CoordinationCycleIdentity instance
        """
        return cls(
            cycle_id=f"cycle:{epoch_id}",
            sequence_index=0,
            parent_cycle_identity=None,
            cycle_kind="initial",
        )
    
    @classmethod
    def from_parent(cls, parent_ref: str, kind: str = "incremental") -> TemporalCoordinationCycleIdentity:
        """
        Create a cycle identity from a parent reference.
        
        Args:
            parent_ref: Parent cycle reference
            kind: Kind of this cycle
            
        Returns:
            A new CoordinationCycleIdentity instance
        """
        return cls(
            cycle_id=f"cycle:{parent_ref}:r1",
            sequence_index=1,
            parent_cycle_identity=parent_ref,
            cycle_kind=kind,
        )
    
    def __str__(self) -> str:
        if self.parent_cycle_identity and self.sequence_index > 0:
            return f"{self.cycle_id}:r{self.sequence_index}"
        return self.cycle_id


# =============================================================================
# COORDINATION CYCLE MODEL (with lifecycle)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationCycle:
    """
    Immutable cycle model for coordination with lifecycle awareness.
    
    CYCLE-LAW-005: Cycle lifecycle state shall remain explicit
    CYCLE-LAW-006: Cycle transitions shall follow the canonical lifecycle contract
    
    COORD-CYCLE-INV-001: Cycle is immutable (deeply frozen)
    COORD-CYCLE-INV-002: Cycle has no runtime references
    """
    cycle_identity: TemporalCoordinationCycleIdentity = field(default_factory=TemporalCoordinationCycleIdentity)
    """Identity of this coordination cycle."""
    
    epoch_ref: Optional[str] = None
    """Reference to the parent coordination epoch."""
    
    lifecycle_status: str = "created"
    """Current lifecycle status (from CoordinationCycleLifecycleStatus)."""
    
    publication_window_ref: Optional[str] = None
    """Reference to the publication window for this cycle."""
    
    accepted_projections: tuple[str, ...] = ()
    """References to accepted projections."""
    
    rejected_projections: tuple[str, ...] = ()
    """References to rejected projections."""
    
    requirement_satisfactions: tuple[str, ...] = ()
    """Requirement satisfactions in this cycle."""
    
    readiness_states: tuple[str, ...] = ()
    """Readiness states of participants."""
    
    availability_states: tuple[str, ...] = ()
    """Availability states of participants."""
    
    dependency_graph_ref: Optional[str] = None
    """Reference to the dependency graph."""
    
    constraint_graph_ref: Optional[str] = None
    """Reference to the constraint graph."""
    
    transition_graph_ref: Optional[str] = None
    """Reference to the transition graph."""
    
    interaction_graph_ref: Optional[str] = None
    """Reference to the interaction graph."""
    
    conflicts: tuple[str, ...] = ()
    """Conflicts detected in this cycle."""
    
    compatibility_ref: Optional[str] = None
    """Reference to compatibility assessment."""
    
    coordination_plan_ref: Optional[str] = None
    """Reference to the coordination plan."""
    
    synchronization_barrier_ref: Optional[str] = None
    """Reference to the synchronization barrier."""
    
    convergence_status: str = "unknown"
    """Convergence status (from CoordinationConvergenceStatus)."""
    
    state_reference: Optional[str] = None
    """Reference to the produced CoordinationState."""
    
    semantic_time_ref: Optional[str] = None
    """Reference to semantic time for this cycle."""
    
    findings: tuple[str, ...] = ()
    """Findings from coordination."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this cycle."""
    
    trace: tuple[str, ...] = ()
    """Trace of lifecycle events."""
    
    provenance_ref: Optional[str] = None
    """Reference to cycle provenance record."""
    
    revision: int = 1
    """Revision number of this cycle."""
    
    @classmethod
    def create_initial(
        cls,
        epoch_ref: str,
        cycle_id: Optional[str] = None,
        provenance_ref: Optional[str] = None,
    ) -> CoordinationCycle:
        """
        Create a new initial coordination cycle.
        
        Args:
            epoch_ref: Reference to parent epoch
            cycle_id: Optional cycle ID override
            provenance_ref: Provenance reference
            
        Returns:
            A new CoordinationCycle instance in 'created' state
        """
        identity = TemporalCoordinationCycleIdentity.from_epoch(epoch_ref) if not cycle_id else TemporalCoordinationCycleIdentity(cycle_id=cycle_id)
        return cls(
            cycle_identity=identity,
            epoch_ref=epoch_ref,
            lifecycle_status="created",
            provenance_ref=provenance_ref,
        )
    
    def transition_to(self, new_status: str) -> CoordinationCycle:
        """
        Create a new cycle with updated lifecycle status.
        
        Args:
            new_status: Target lifecycle status
            
        Returns:
            A new CoordinationCycle instance with updated status
        """
        is_valid, reason = LifecycleTransitionValidator.validate_transition(
            self.lifecycle_status,
            new_status,
        )
        if not is_valid:
            raise ValueError(f"Invalid lifecycle transition: {reason}")
        
        return CoordinationCycle(
            cycle_identity=TemporalCoordinationCycleIdentity(
                cycle_id=self.cycle_identity.cycle_id,
                sequence_index=self.cycle_identity.sequence_index,
                parent_cycle_identity=str(self.cycle_identity),
                cycle_kind=self.cycle_identity.cycle_kind,
            ),
            epoch_ref=self.epoch_ref,
            lifecycle_status=new_status,
            publication_window_ref=self.publication_window_ref,
            accepted_projections=self.accepted_projections,
            rejected_projections=self.rejected_projections,
            requirement_satisfactions=self.requirement_satisfactions,
            readiness_states=self.readiness_states,
            availability_states=self.availability_states,
            dependency_graph_ref=self.dependency_graph_ref,
            constraint_graph_ref=self.constraint_graph_ref,
            transition_graph_ref=self.transition_graph_ref,
            interaction_graph_ref=self.interaction_graph_ref,
            conflicts=self.conflicts,
            compatibility_ref=self.compatibility_ref,
            coordination_plan_ref=self.coordination_plan_ref,
            synchronization_barrier_ref=self.synchronization_barrier_ref,
            convergence_status=self.convergence_status,
            state_reference=self.state_reference,
            semantic_time_ref=self.semantic_time_ref,
            findings=self.findings,
            limitations=self.limitations,
            trace=self.trace + (f"transition:{self.lifecycle_status}->{new_status}",),
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )
    
    def mark_complete(
        self,
        state_ref: str,
        convergence: str = "stable",
        findings: tuple[str, ...] = (),
        limitations: tuple[str, ...] = (),
    ) -> CoordinationCycle:
        """
        Mark this cycle as complete with a produced state.
        
        Args:
            state_ref: Reference to the produced CoordinationState
            convergence: Convergence status
            findings: Additional findings
            limitations: Additional limitations
            
        Returns:
            A new CoordinationCycle instance in 'complete' state
        """
        return CoordinationCycle(
            cycle_identity=TemporalCoordinationCycleIdentity(
                cycle_id=self.cycle_identity.cycle_id,
                sequence_index=self.cycle_identity.sequence_index,
                parent_cycle_identity=str(self.cycle_identity),
                cycle_kind=self.cycle_identity.cycle_kind,
            ),
            epoch_ref=self.epoch_ref,
            lifecycle_status="complete",
            publication_window_ref=self.publication_window_ref,
            accepted_projections=self.accepted_projections,
            rejected_projections=self.rejected_projections,
            requirement_satisfactions=self.requirement_satisfactions,
            readiness_states=self.readiness_states,
            availability_states=self.availability_states,
            dependency_graph_ref=self.dependency_graph_ref,
            constraint_graph_ref=self.constraint_graph_ref,
            transition_graph_ref=self.transition_graph_ref,
            interaction_graph_ref=self.interaction_graph_ref,
            conflicts=self.conflicts,
            compatibility_ref=self.compatibility_ref,
            coordination_plan_ref=self.coordination_plan_ref,
            synchronization_barrier_ref=self.synchronization_barrier_ref,
            convergence_status=convergence,
            state_reference=state_ref,
            semantic_time_ref=self.semantic_time_ref,
            findings=findings + self.findings,
            limitations=limitations + self.limitations,
            trace=self.trace + (f"complete:state={state_ref}",),
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )
    
    def fail(
        self,
        failure_findings: tuple[str, ...],
    ) -> CoordinationCycle:
        """
        Mark this cycle as failed.
        
        Args:
            failure_findings: Findings describing the failure
            
        Returns:
            A new CoordinationCycle instance in 'failed' state
        """
        return CoordinationCycle(
            cycle_identity=TemporalCoordinationCycleIdentity(
                cycle_id=self.cycle_identity.cycle_id,
                sequence_index=self.cycle_identity.sequence_index,
                parent_cycle_identity=str(self.cycle_identity),
                cycle_kind=self.cycle_identity.cycle_kind,
            ),
            epoch_ref=self.epoch_ref,
            lifecycle_status="failed",
            publication_window_ref=self.publication_window_ref,
            accepted_projections=self.accepted_projections,
            rejected_projections=self.rejected_projections + failure_findings,
            requirement_satisfactions=self.requirement_satisfactions,
            readiness_states=self.readiness_states,
            availability_states=self.availability_states,
            dependency_graph_ref=self.dependency_graph_ref,
            constraint_graph_ref=self.constraint_graph_ref,
            transition_graph_ref=self.transition_graph_ref,
            interaction_graph_ref=self.interaction_graph_ref,
            conflicts=self.conflicts + failure_findings,
            compatibility_ref=self.compatibility_ref,
            coordination_plan_ref=self.coordination_plan_ref,
            synchronization_barrier_ref=self.synchronization_barrier_ref,
            convergence_status="failed",
            state_reference=self.state_reference,
            semantic_time_ref=self.semantic_time_ref,
            findings=failure_findings + self.findings,
            limitations=self.limitations,
            trace=self.trace + (f"fail:{failure_findings}",),
            provenance_ref=self.provenance_ref,
            revision=self.revision + 1,
        )