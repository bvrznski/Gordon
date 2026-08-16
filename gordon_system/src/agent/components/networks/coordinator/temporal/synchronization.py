# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Synchronization Models
===================================

Canonical immutable models for synchronization barriers, snapshots,
and freshness evaluation.

SYNCHRONIZATION OVERVIEW
------------------------
Synchronization ensures all required projections are available and valid
before constructing a CoordinationState. The synchronization barrier
remains purely semantic - it never blocks or waits at runtime.

BARRIER STATES:
- CLOSED: Waiting for required projections
- PARTIALLY_SATISFIED: Some requirements met
- OPEN: All conditions satisfied, can proceed
- BLOCKED: Blocking constraints preventing progress

SNAPSHOT INVARIANTS:
===================
- Snapshot is consistent if all included projections are semantically compatible
- Snapshot does NOT imply cognitive agreement among networks
- Mixed-revision snapshots must be explicitly classified
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# SYNCHRONIZATION BARRIER STATUS
# =============================================================================

class SynchronizationBarrierStatus(Enum):
    """
    Canonical status enumeration for synchronization barriers.
    
    BARRIER-LAW-012: Barrier evaluation shall remain deterministic
    
    STATES:
    - CLOSED: Waiting for required conditions
    - PARTIALLY_SATISFIED: Some requirements met, more needed
    - OPEN: All conditions satisfied, can proceed
    - OPEN_WITH_LIMITATIONS: Open but with known limitations
    - BLOCKED: Blocking constraints prevent progress
    - FAILED: Barrier evaluation failed
    - SUPERSEDED: Superseded by newer barrier
    """
    CLOSED = "closed"
    """Waiting for required projections/conditions."""
    
    PARTIALLY_SATISFIED = "partially_satisfied"
    """Some requirements met, more needed."""
    
    OPEN = "open"
    """All conditions satisfied, can proceed."""
    
    OPEN_WITH_LIMITATIONS = "open_with_limitations"
    """Open but with known limitations."""
    
    BLOCKED = "blocked"
    """Blocking constraints prevent progress."""
    
    FAILED = "failed"
    """Barrier evaluation failed."""
    
    SUPERSEDED = "superseded"
    """Superseded by newer barrier."""
    
    UNKNOWN = "unknown"
    """Barrier status cannot be determined."""


# =============================================================================
# SNAPSHOT CONSISTENCY STATUS
# =============================================================================

class SnapshotConsistencyStatus(Enum):
    """
    Canonical consistency statuses for snapshots.
    
    SNAPSHOT-LAW-010: Snapshot consistency shall never imply cognitive agreement
    
    STATUSES:
    - CONSISTENT: All projections compatible, valid snapshot
    - CONSISTENT_WITH_LIMITATIONS: Valid but with known limitations
    - PARTIALLY_CONSISTENT: Some projections inconsistent
    - INCONSISTENT: Projections have incompatible revisions
    - UNDETERMINED: Cannot determine consistency
    """
    CONSISTENT = "consistent"
    """All included projections are semantically compatible."""
    
    CONSISTENT_WITH_LIMITATIONS = "consistent_with_limitations"
    """Valid but with known limitations."""
    
    PARTIALLY_CONSISTENT = "partially_consistent"
    """Some projections may be inconsistent."""
    
    INCONSISTENT = "inconsistent"
    """Incompatible revisions detected."""
    
    UNDETERMINED = "undetermined"
    """Cannot determine consistency."""
    
    UNKNOWN = "unknown"
    """Consistency status unknown."""


# =============================================================================
# PROJECTION FRESHNESS STATUS
# =============================================================================

class ProjectionFreshnessStatus(Enum):
    """
    Canonical freshness statuses for projections.
    
    FRESHNESS-LAW-010: Reusable shall remain distinct from current
    
    STATUSES:
    - CURRENT: Fresh, valid projection
    - REUSABLE: Old but still acceptable per policy
    - STALE: Invalidated by dependency change
    - SUPERSEDED: Replaced by newer projection
    - INVALID: Projection is invalid
    """
    CURRENT = "current"
    """Fresh projection with current dependencies."""
    
    REUSABLE = "reusable"
    """Old but acceptable per freshness policy."""
    
    STALE = "stale"
    """Invalidated by dependency change."""
    
    SUPERSEDED = "superseded"
    """Replaced by newer projection."""
    
    INVALID = "invalid"
    """Projection is invalid for coordination."""
    
    UNKNOWN = "unknown"
    """Freshness cannot be determined."""


# =============================================================================
# SYNCHRONIZATION BARRIER MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationSynchronizationBarrier:
    """
    Immutable synchronization barrier model.
    
    BARRIER-LAW-001: Exactly one canonical Synchronization Barrier shall exist
    per cycle
    
    BARRIER-LAW-003: Barrier evaluation shall consume semantic state only
    
    COORD-BARRIER-INV-001: Barrier is immutable (deeply frozen)
    COORD-BARRIER-INV-002: Barrier has no runtime references
    """
    barrier_identity: str = ""
    """Unique identifier for this barrier."""
    
    cycle_ref: Optional[str] = None
    """Reference to the parent coordination cycle."""
    
    required_participants: tuple[str, ...] = ()
    """Networks whose participation is required."""
    
    optional_participants: tuple[str, ...] = ()
    """Networks whose participation is optional."""
    
    required_capabilities: tuple[str, ...] = ()
    """Required capabilities for coordination."""
    
    satisfied_requirements: tuple[str, ...] = ()
    """Requirements that are satisfied."""
    
    unsatisfied_requirements: tuple[str, ...] = ()
    """Requirements that remain unsatisfied."""
    
    accepted_projections: tuple[str, ...] = ()
    """References to accepted projections."""
    
    missing_projections: tuple[str, ...] = ()
    """References to missing required projections."""
    
    blocking_constraints: tuple[str, ...] = ()
    """Constraints that are blocking progress."""
    
    unresolved_dependencies: tuple[str, ...] = ()
    """Dependencies that remain unresolved."""
    
    compatibility_status: str = "unknown"
    """Compatibility status of accepted projections."""
    
    status: str = "closed"
    """Barrier status (from SynchronizationBarrierStatus)."""
    
    opening_condition: Optional[str] = None
    """Condition under which barrier opened."""
    
    degradation_condition: Optional[str] = None
    """Condition allowing degraded opening."""
    
    failure_condition: Optional[str] = None
    """Condition causing barrier failure."""
    
    confidence: float = 0.5
    """Confidence in barrier evaluation."""
    
    uncertainty: float = 0.5
    """Uncertainty about barrier state."""
    
    provenance_ref: Optional[str] = None
    """Reference to barrier provenance record."""
    
    @classmethod
    def create_barrier(
        cls,
        cycle_ref: str,
        required_participants: tuple[str, ...],
        optional_participants: tuple[str, ...],
        required_capabilities: tuple[str, ...],
        provenance_ref: Optional[str] = None,
    ) -> CoordinationSynchronizationBarrier:
        """
        Create a new closed synchronization barrier.
        
        Args:
            cycle_ref: Reference to parent coordination cycle
            required_participants: Required network references
            optional_participants: Optional network references
            required_capabilities: Required capability references
            provenance_ref: Provenance reference
            
        Returns:
            A new CoordinationSynchronizationBarrier instance in closed state
        """
        return cls(
            barrier_identity=f"barrier:{cycle_ref}",
            cycle_ref=cycle_ref,
            required_participants=required_participants,
            optional_participants=optional_participants,
            required_capabilities=required_capabilities,
            status="closed",
            provenance_ref=provenance_ref,
        )
    
    def add_projection(
        self,
        projection_ref: str,
    ) -> CoordinationSynchronizationBarrier:
        """
        Create a new barrier with an accepted projection.
        
        Args:
            projection_ref: Reference to the accepted projection
            
        Returns:
            A new CoordinationSynchronizationBarrier instance
        """
        return CoordinationSynchronizationBarrier(
            barrier_identity=self.barrier_identity,
            cycle_ref=self.cycle_ref,
            required_participants=self.required_participants,
            optional_participants=self.optional_participants,
            required_capabilities=self.required_capabilities,
            satisfied_requirements=self.satisfied_requirements,
            unsatisfied_requirements=self.unsatisfied_requirements,
            accepted_projections=self.accepted_projections + (projection_ref,),
            missing_projections=tuple(
                p for p in self.missing_projections
                if p not in self.accepted_projections and p != projection_ref
            ),
            blocking_constraints=self.blocking_constraints,
            unresolved_dependencies=self.unresolved_dependencies,
            compatibility_status=self.compatibility_status,
            status=self.status,
            opening_condition=self.opening_condition,
            degradation_condition=self.degradation_condition,
            failure_condition=self.failure_condition,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance_ref=self.provenance_ref,
        )
    
    def add_requirements(
        self,
        satisfied: tuple[str, ...] = (),
        unsatisfied: tuple[str, ...] = (),
    ) -> CoordinationSynchronizationBarrier:
        """
        Create a new barrier with updated requirements.
        
        Args:
            satisfied: Newly satisfied requirements
            unsatisfied: newly unsatisfied requirements
            
        Returns:
            A new CoordinationSynchronizationBarrier instance
        """
        return CoordinationSynchronizationBarrier(
            barrier_identity=self.barrier_identity,
            cycle_ref=self.cycle_ref,
            required_participants=self.required_participants,
            optional_participants=self.optional_participants,
            required_capabilities=self.required_capabilities,
            satisfied_requirements=self.satisfied_requirements + satisfied,
            unsatisfied_requirements=self.unsatisfied_requirements + unsatisfied,
            accepted_projections=self.accepted_projections,
            missing_projections=self.missing_projections,
            blocking_constraints=self.blocking_constraints,
            unresolved_dependencies=self.unresolved_dependencies,
            compatibility_status=self.compatibility_status,
            status=self.status,
            opening_condition=self.opening_condition,
            degradation_condition=self.degradation_condition,
            failure_condition=self.failure_condition,
            confidence=self.confidence,
            uncertainty=self.uncertainty,
            provenance_ref=self.provenance_ref,
        )
    
    def evaluate(
        self,
        status: str = "open",
        opening_condition: Optional[str] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> CoordinationSynchronizationBarrier:
        """
        Create a new barrier with evaluated status.
        
        Args:
            status: Evaluated barrier status
            opening_condition: Condition that opened the barrier
            confidence: Confidence in evaluation
            uncertainty: Uncertainty about evaluation
            
        Returns:
            A new CoordinationSynchronizationBarrier instance with evaluated status
        """
        return CoordinationSynchronizationBarrier(
            barrier_identity=self.barrier_identity,
            cycle_ref=self.cycle_ref,
            required_participants=self.required_participants,
            optional_participants=self.optional_participants,
            required_capabilities=self.required_capabilities,
            satisfied_requirements=self.satisfied_requirements,
            unsatisfied_requirements=self.unsatisfied_requirements,
            accepted_projections=self.accepted_projections,
            missing_projections=self.missing_projections,
            blocking_constraints=self.blocking_constraints,
            unresolved_dependencies=self.unresolved_dependencies,
            compatibility_status=self.compatibility_status,
            status=status,
            opening_condition=opening_condition,
            degradation_condition=self.degradation_condition,
            failure_condition=self.failure_condition,
            confidence=confidence,
            uncertainty=uncertainty,
            provenance_ref=self.provenance_ref,
        )


# =============================================================================
# COORDINATION SNAPSHOT MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationSnapshot:
    """
    Immutable snapshot model for coordination.
    
    SNAPSHOT-LAW-001: Exactly one canonical Coordination Snapshot shall exist per
    synchronized cycle
    
    SNAPSHOT-LAW-008: The snapshot shall remain immutable
    
    COORD-SNAPSHOT-INV-001: Snapshot is immutable (deeply frozen)
    COORD-SNAPSHOT-INV-002: Snapshot has no runtime references
    """
    snapshot_identity: str = ""
    """Unique identifier for this snapshot."""
    
    epoch_ref: Optional[str] = None
    """Reference to the parent coordination epoch."""
    
    cycle_ref: Optional[str] = None
    """Reference to the synchronized coordination cycle."""
    
    projection_set: tuple[str, ...] = ()
    """References to included projections."""
    
    projection_revision_map: dict[str, int] = field(default_factory=dict)
    """Map of projection reference -> revision number."""
    
    dependency_revision_map: dict[str, int] = field(default_factory=dict)
    """Map of dependency reference -> revision number."""
    
    membership_revision: int = 1
    """Revision of the active membership configuration."""
    
    policy_revision: int = 1
    """Revision of the coordination policy."""
    
    semantic_context_revision: int = 1
    """Revision of the current semantic context."""
    
    consistency_status: str = "unknown"
    """Consistency status (from SnapshotConsistencyStatus)."""
    
    findings: tuple[str, ...] = ()
    """Findings from snapshot construction."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this snapshot."""
    
    provenance_ref: Optional[str] = None
    """Reference to snapshot provenance record."""
    
    @classmethod
    def construct_snapshot(
        cls,
        cycle_ref: str,
        projections: tuple[str, ...],
        epoch_ref: Optional[str] = None,
        membership_rev: int = 1,
        policy_rev: int = 1,
        context_rev: int = 1,
        provenance_ref: Optional[str] = None,
    ) -> CoordinationSnapshot:
        """
        Construct a new coordination snapshot.
        
        Args:
            cycle_ref: Reference to synchronized cycle
            projections: Tuple of accepted projection references
            epoch_ref: Reference to parent epoch (optional)
            membership_rev: Membership configuration revision
            policy_rev: Policy revision
            context_rev: Semantic context revision
            provenance_ref: Provenance reference
            
        Returns:
            A new CoordinationSnapshot instance
        """
        return cls(
            snapshot_identity=f"snapshot:{cycle_ref}",
            epoch_ref=epoch_ref,
            cycle_ref=cycle_ref,
            projection_set=projections,
            membership_revision=membership_rev,
            policy_revision=policy_rev,
            semantic_context_revision=context_rev,
            consistency_status="consistent",
            provenance_ref=provenance_ref,
        )
    
    def with_limitations(
        self,
        limitations: tuple[str, ...],
    ) -> CoordinationSnapshot:
        """
        Create a new snapshot with known limitations.
        
        Args:
            limitations: Limitation descriptions
            
        Returns:
            A new CoordinationSnapshot instance
        """
        return CoordinationSnapshot(
            snapshot_identity=self.snapshot_identity,
            epoch_ref=self.epoch_ref,
            cycle_ref=self.cycle_ref,
            projection_set=self.projection_set,
            projection_revision_map=dict(self.projection_revision_map),
            dependency_revision_map=dict(self.dependency_revision_map),
            membership_revision=self.membership_revision,
            policy_revision=self.policy_revision,
            semantic_context_revision=self.semantic_context_revision,
            consistency_status="consistent_with_limitations",
            findings=self.findings + limitations,
            limitations=limitations + self.limitations,
            provenance_ref=self.provenance_ref,
        )


# =============================================================================
# SEMANTIC FRESHNESS MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProjectionFreshness:
    """
    Immutable freshness model for projections.
    
    FRESHNESS-LAW-001: Projection freshness shall be semantic
    
    FRESHNESS-LAW-002: Projection freshness shall not depend on wall-clock age
    
    COORD-FRESHNESS-INV-001: Freshness is immutable (deeply frozen)
    COORD-FRESHNESS-INV-002: Freshness has no runtime references
    """
    projection_ref: str = ""
    """Reference to the projection being assessed."""
    
    freshness_status: str = "unknown"
    """Freshness status (from ProjectionFreshnessStatus)."""
    
    evidence: tuple[str, ...] = ()
    """Evidence supporting this freshness assessment."""
    
    epoch_compatibility: bool = True
    """Whether projection is compatible with current epoch."""
    
    cycle_compatibility: bool = True
    """Whether projection is compatible with current cycle."""
    
    network_revision_match: bool = True
    """Whether network revision matches expectations."""
    
    projection_revision_match: bool = True
    """Whether projection revision matches expectations."""
    
    dependency_revisions_match: tuple[bool, ...] = ()
    """Whether each dependency revision matches."""
    
    world_state_revision_match: Optional[bool] = None
    """Whether world state revision matches."""
    
    context_revision_match: Optional[bool] = None
    """Whether semantic context revision matches."""
    
    transition_revision_match: Optional[bool] = None
    """Whether transition revision matches."""
    
    semantic_fingerprint: Optional[str] = None
    """Semantic fingerprint of the projection."""
    
    @classmethod
    def current(
        cls,
        projection_ref: str,
        dependencies: tuple[str, ...],
        world_state_rev_match: bool = True,
        context_rev_match: bool = True,
        fingerprint: Optional[str] = None,
    ) -> ProjectionFreshness:
        """
        Create a freshness assessment for a current projection.
        
        Args:
            projection_ref: Reference to the projection
            dependencies: Current dependency references
            world_state_rev_match: Whether world state revision matches
            context_rev_match: Whether context revision matches
            fingerprint: Semantic fingerprint of projection
            
        Returns:
            A new ProjectionFreshness instance with 'current' status
        """
        return cls(
            projection_ref=projection_ref,
            freshness_status="current",
            evidence=("all dependencies match current state",),
            epoch_compatibility=True,
            cycle_compatibility=True,
            network_revision_match=True,
            projection_revision_match=True,
            dependency_revisions_match=tuple(True for _ in dependencies),
            world_state_revision_match=world_state_rev_match,
            context_revision_match=context_rev_match,
            semantic_fingerprint=fingerprint,
        )
    
    @classmethod
    def reusable(
        cls,
        projection_ref: str,
        policy_approved: bool = True,
        fingerprint: Optional[str] = None,
    ) -> ProjectionFreshness:
        """
        Create a freshness assessment for a reusable projection.
        
        Args:
            projection_ref: Reference to the projection
            policy_approved: Whether policy allows reuse
            fingerprint: Semantic fingerprint of projection
            
        Returns:
            A new ProjectionFreshness instance with 'reusable' status
        """
        return cls(
            projection_ref=projection_ref,
            freshness_status="reusable",
            evidence=("policy-approved reuse",) if policy_approved else ("unchanged semantic fingerprint",),
            epoch_compatibility=True,
            cycle_compatibility=False,  # Old but acceptable per policy
            network_revision_match=True,
            projection_revision_match=True,
            dependency_revisions_match=(),
            world_state_revision_match=None,
            context_revision_match=None,
            transition_revision_match=None,
            semantic_fingerprint=fingerprint,
        )
    
    @classmethod
    def stale(
        cls,
        projection_ref: str,
        invalidating_dependency: str,
        current_dependency_rev: int,
    ) -> ProjectionFreshness:
        """
        Create a freshness assessment for a stale projection.
        
        Args:
            projection_ref: Reference to the projection
            invalidating_dependency: Dependency that invalidated this projection
            current_dependency_rev: Current revision of that dependency
            
        Returns:
            A new ProjectionFreshness instance with 'stale' status
        """
        return cls(
            projection_ref=projection_ref,
            freshness_status="stale",
            evidence=(f"dependency '{invalidating_dependency}' changed",),
            epoch_compatibility=False,
            cycle_compatibility=False,
            network_revision_match=True,
            projection_revision_match=False,
            dependency_revisions_match=tuple(False for _ in range(1)),
            world_state_revision_match=None,
            context_revision_match=None,
            transition_revision_match=None,
            semantic_fingerprint=None,
        )
    
    @classmethod
    def superseded(
        cls,
        projection_ref: str,
        new_projection_ref: str,
    ) -> ProjectionFreshness:
        """
        Create a freshness assessment for a superseded projection.
        
        Args:
            projection_ref: Reference to the old projection
            new_projection_ref: Reference to the replacement projection
            
        Returns:
            A new ProjectionFreshness instance with 'superseded' status
        """
        return cls(
            projection_ref=projection_ref,
            freshness_status="superseded",
            evidence=(f"replaced by {new_projection_ref}",),
            epoch_compatibility=False,
            cycle_compatibility=False,
            network_revision_match=True,
            projection_revision_match=False,
            dependency_revisions_match=(),
            world_state_revision_match=None,
            context_revision_match=None,
            transition_revision_match=None,
            semantic_fingerprint=None,
        )


# =============================================================================
# SYNCHRONIZATION BARRIER EVALUATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class SynchronizationBarrierEvaluator:
    """
    Immutable evaluator for synchronization barriers.
    
    BARRIER-EVAL-INV-001: Evaluator is deterministic
    
    Inputs:
    - participant set
    - projection acceptances  
    - requirement satisfactions
    - readiness states
    - availability states
    - dependency graph
    - constraint graph
    - compatibility assessment
    
    Output: CoordinationSynchronizationBarrier
    """
    
    @classmethod
    def evaluate_barrier(
        cls,
        required_participants: tuple[str, ...],
        accepted_projections: tuple[str, ...],
        requirement_satisfactions: tuple[str, ...],
        readiness_states: tuple[str, ...],
        availability_states: tuple[str, ...],
        dependency_graph_refs: tuple[str, ...],
        constraint_graph_refs: tuple[str, ...],
    ) -> CoordinationSynchronizationBarrier:
        """
        Evaluate the synchronization barrier state.
        
        Args:
            required_participants: Required network references
            accepted_projections: Accepted projection references
            requirement_satisfactions: Satisfied requirement refs
            readiness_states: Network readiness states
            availability_states: Network availability states
            dependency_graph_refs: Dependency graph references
            constraint_graph_refs: Constraint graph references
            
        Returns:
            A new CoordinationSynchronizationBarrier with evaluated status
        """
        # Determine satisfied vs missing projections
        required_projections = set(required_participants)
        accepted_projection_set = set(accepted_projections)
        
        missing_projections = tuple(
            p for p in required_projections if p not in accepted_projection_set
        )
        
        all_participants = required_participants + tuple(
            p for p in accepted_projection_set if p not in required_projections
        )
        
        # Determine if barrier is open
        barrier_status = "open" if not missing_projections else "closed"
        
        return CoordinationSynchronizationBarrier(
            barrier_identity="barrier:eval",
            cycle_ref=None,
            required_participants=required_participants,
            optional_participants=(),
            required_capabilities=tuple(dependency_graph_refs),
            satisfied_requirements=requirement_satisfactions,
            unsatisfied_requirements=(),
            accepted_projections=accepted_projections,
            missing_projections=missing_projections,
            blocking_constraints=constraint_graph_refs,
            unresolved_dependencies=dependency_graph_refs,
            compatibility_status="compatible" if not constraint_graph_refs else "undetermined",
            status=barrier_status,
        )