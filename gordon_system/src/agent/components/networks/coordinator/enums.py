# Gordon Cognitive Architecture - Phase 4.11.1
# ===========================================

"""
Coordination Network Enums and Type Definitions
==============================================

Canonical enumerations for the Coordination Network's semantic contracts.
All enums are deeply immutable to ensure deterministic behavior.
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


# =============================================================================
# COORDINATED NETWORK KINDS
# =============================================================================

class CoordinatedNetworkKind(Enum):
    """
    Canonical enumeration of coordinated cognitive networks.
    
    Every coordinated network is a semantic peer. None is superior to another.
    Membership in this enum is explicit and immutable.
    
    COORD-LAW-011: Core membership consists of exactly ten networks
    COORD-LAW-012: Network kind is stable across projection revisions
    """
    ALERTING = auto()
    DEFAULT = auto()
    EXECUTIVE = auto()
    FOCUSING = auto()
    ORIENTED = auto()
    PREDICTIVE = auto()
    REWARD = auto()
    SALIENCE = auto()
    SENSORIMOTOR = auto()
    WORKSPACE = auto()

    @classmethod
    def all_kinds(cls) -> tuple[CoordinatedNetworkKind, ...]:
        """Return all canonical coordinated network kinds in stable order."""
        return tuple(cls)

    @classmethod
    def from_string(cls, value: str) -> CoordinatedNetworkKind:
        """
        Parse a string into a network kind.
        
        Raises:
            ValueError: If the string doesn't match any known network kind
        """
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown coordinated network kind: {value}")


# =============================================================================
# NETWORK COORDINATION STATUS
# =============================================================================

class NetworkCoordinationStatus(Enum):
    """
    Coarse coordination-facing status for a network.
    
    This is a summary status that does NOT replace readiness or availability.
    
    COORD-LAW-013: Status is coarse - not replacement for readiness/availability
    COORD-LAW-014: Status values are canonical and immutable
    """
    NOMINAL = "nominal"
    """Network is functioning within expected parameters."""
    
    DEGRADED = "degraded"
    """Network has reduced capability but remains functional."""
    
    WAITING = "waiting"
    """Network is waiting for external conditions or inputs."""
    
    BLOCKED = "blocked"
    """Network cannot proceed due to active constraints."""
    
    FAILED = "failed"
    """Network operation has failed."""
    
    UNAVAILABLE = "unavailable"
    """Network is not currently accessible."""
    
    UNKNOWN = "unknown"
    """Status cannot be determined at this time."""


# =============================================================================
# NETWORK READINESS STATES
# =============================================================================

class NetworkReadinessState(Enum):
    """
    Readiness state for a network to participate in a coordination operation.
    
    Readiness is operation-relative. A network may be ready to publish one
    projection while blocked from producing another.
    
    COORD-LAW-015: Readiness remains operation-specific
    COORD-LAW-016: Readiness is independent from availability
    """
    READY = "ready"
    """Network can fully participate in the operation."""
    
    PARTIALLY_READY = "partially_ready"
    """Network can partially participate but has some constraints."""
    
    WAITING = "waiting"
    """Network is waiting for a dependency to be satisfied."""
    
    BLOCKED = "blocked"
    """Active constraint prevents participation."""
    
    DEFERRED = "deferred"
    """Network chose to defer participation to another cycle."""
    
    UNAVAILABLE = "unavailable"
    """Network coordination-facing capability is not available."""
    
    FAILED = "failed"
    """Previous attempt has failed."""
    
    UNKNOWN = "unknown"
    """Readiness cannot be determined at this time."""


# =============================================================================
# NETWORK AVAILABILITY STATES
# =============================================================================

class NetworkAvailabilityState(Enum):
    """
    Availability state for a network's coordination-facing capability.
    
    Availability differs from readiness:
    - A network may be available but not ready (e.g., waiting for an outcome)
    - Readiness answers: "Can this network participate NOW?"
    - Availability answers: "Can this capability be accessed?"
    
    COORD-LAW-017: Availability is capability-specific
    COORD-LAW-018: Availability is independent from readiness
    """
    AVAILABLE = "available"
    """Coordination-facing capability is fully accessible."""
    
    DEGRADED = "degraded"
    """Capability exists but with reduced functionality or reliability."""
    
    UNAVAILABLE = "unavailable"
    """Capability is not currently accessible."""
    
    UNKNOWN = "unknown"
    """Availability cannot be determined at this time."""


# =============================================================================
# PARTICIPATION ROLES
# =============================================================================

class ParticipationRole(Enum):
    """
    Role of a network in the current Coordination Cycle.
    
    Participation is cycle-specific. It does not change network ownership.
    
    COORD-LAW-019: Participation is coordination cycle specific
    COORD-LAW-020: Participation preserves role identity
    """
    REQUIRED = "required"
    """Network must participate for valid coordination."""
    
    OPTIONAL = "optional"
    """Network may participate but isn't required."""
    
    OBSERVING = "observing"
    """Network is observing but not directly participating."""
    
    DEFERRED = "deferred"
    """Network participation was deferred to a future cycle."""
    
    EXCLUDED = "excluded"
    """Network has been explicitly excluded from this cycle."""
    
    UNAVAILABLE = "unavailable"
    """Network is unavailable for participation."""
    
    UNKNOWN = "unknown"
    """Participation role cannot be determined."""


# =============================================================================
# DEPENDENCY KINDS
# =============================================================================

class DependencyKind(Enum):
    """
    Kinds of dependencies between coordination elements.
    
    COORD-LAW-021: Dependencies remain typed
    COORD-LAW-022: Dependencies remain directed
    """
    DEPENDS_ON = "depends_on"
    """Basic dependency - this requires that."""
    
    REQUIRES_BEFORE = "requires_before"
    """This must complete before the prerequisite."""
    
    REQUIRES_AFTER = "requires_after"
    """This must complete after the prerequisite."""
    
    REQUIRES_TOGETHER = "requires_together"
    """Both elements must be satisfied together."""
    
    OPTIONAL_DEPENDENCY = "optional_dependency"
    """Dependency that can be skipped if not satisfiable."""
    
    MUTUAL_SYNCHRONIZATION = "mutual_synchronization"
    """Both sides must synchronize for progress."""
    
    UNKNOWN = "unknown"
    """Dependency kind cannot be determined."""


# =============================================================================
# CONSTRAINT KINDS
# =============================================================================

class ConstraintKind(Enum):
    """
    Kinds of coordination constraints.
    
    COORD-LAW-023: Constraints remain explicit
    COORD-LAW-024: Constraint origin remains preserved
    """
    CAPACITY = "capacity"
    """Resource capacity limit."""
    
    AVAILABILITY = "availability"
    """Capability availability constraint."""
    
    READINESS = "readiness"
    """Readiness state constraint."""
    
    VERSION = "version"
    """Contract version compatibility constraint."""
    
    SEMANTIC_REVISION = "semantic_revision"
    """Semantic revision compatibility constraint."""
    
    ORDERING = "ordering"
    """Ordering constraint between operations."""
    
    EXCLUSIVITY = "exclusivity"
    """Mutual exclusion constraint."""
    
    DEPENDENCY = "dependency"
    """Dependency-based constraint."""
    
    SAFETY = "safety"
    """Safety-critical constraint."""
    
    RESOURCE = "resource"
    """Resource allocation constraint."""
    
    TEMPORAL = "temporal"
    """Temporal or timing constraint."""
    
    PARTICIPATION = "participation"
    """Participation requirement constraint."""
    
    TRANSITION = "transition"
    """Transition state constraint."""
    
    UNKNOWN = "unknown"
    """Constraint kind cannot be determined."""


# =============================================================================
# CONFLICT KINDS
# =============================================================================

class ConflictKind(Enum):
    """
    Kinds of coordination conflicts.
    
    COORD-LAW-025: Conflicts shall be classified
    COORD-LAW-026: Structural and cognitive conflicts are distinct
    """
    REQUIREMENT_CONFLICT = "requirement_conflict"
    """Conflicting requirements between networks."""
    
    CAPABILITY_CONFLICT = "capability_conflict"
    """Conflicting capability needs."""
    
    CONSTRAINT_CONFLICT = "constraint_conflict"
    """Mutually incompatible constraints."""
    
    READINESS_CONFLICT = "readiness_conflict"
    """Incompatible readiness states."""
    
    AVAILABILITY_CONFLICT = "availability_conflict"
    """Incompatible availability states."""
    
    TRANSITION_CONFLICT = "transition_conflict"
    """Conflicting transition intentions."""
    
    VERSION_CONFLICT = "version_conflict"
    """Contract version incompatibility."""
    
    REVISION_CONFLICT = "revision_conflict"
    """Semantic revision mismatch."""
    
    PARTICIPATION_CONFLICT = "participation_conflict"
    """Incompatible participation roles."""
    
    COGNITIVE_STATE_CONFLICT = "cognitive_state_conflict"
    """Cognitive state conflict (not for coordination to resolve)."""
    
    UNKNOWN = "unknown"
    """Conflict kind cannot be determined."""


# =============================================================================
# COMPATIBILITY STATUS
# =============================================================================

class CompatibilityStatus(Enum):
    """
    Compatibility status between network projections.
    
    COORD-LAW-027: Compatibility remains explicit
    COORD-LAW-028: Compatibility preserves version checks
    """
    COMPATIBLE = "compatible"
    """All projections are compatible."""
    
    COMPATIBLE_WITH_LIMITATIONS = "compatible_with_limitations"
    """Compatible but with known limitations."""
    
    INCOMPATIBLE = "incompatible"
    """Projections cannot coexist in one cycle."""
    
    UNDETERMINED = "undetermined"
    """Compatibility cannot be determined."""
    
    UNKNOWN = "unknown"
    """Unknown compatibility status."""


# =============================================================================
# FINDING CODES
# =============================================================================

class FindingCode(Enum):
    """
    Canonical codes for coordination findings.
    
    Findings are structured records of issues discovered during coordination.
    
    COORD-LAW-029: Validation findings remain typed
    COORD-LAW-030: Findings preserve provenance
    """
    MISSING_NETWORK_PROJECTION = "missing_network_projection"
    """Required network projection is missing."""
    
    STALE_NETWORK_PROJECTION = "stale_network_projection"
    """Network projection is outdated."""
    
    UNKNOWN_NETWORK = "unknown_network"
    """Network identity not recognized."""
    
    UNSUPPORTED_NETWORK = "unsupported_network"
    """Network kind not supported by this coordinator."""
    
    MISSING_CAPABILITY = "missing_capability"
    """Required capability is not available."""
    
    UNSATISFIED_REQUIREMENT = "unsatisfied_requirement"
    """A requirement cannot be satisfied."""
    
    UNRESOLVED_DEPENDENCY = "unresolved_dependency"
    """Dependency cannot be resolved."""
    
    DEPENDENCY_CYCLE = "dependency_cycle"
    """Circular dependency detected."""
    
    CONSTRAINT_CONFLICT = "constraint_conflict"
    """Conflicting constraints detected."""
    
    TRANSITION_CONFLICT = "transition_conflict"
    """Conflicting transition intentions."""
    
    CONTRACT_VERSION_MISMATCH = "contract_version_mismatch"
    """Contract version incompatibility."""
    
    PROJECTION_REVISION_MISMATCH = "projection_revision_mismatch"
    """Projection revision mismatch."""
    
    PARTICIPANT_UNAVAILABLE = "participant_unavailable"
    """Required participant is unavailable."""
    
    PARTICIPANT_BLOCKED = "participant_blocked"
    """Required participant is blocked."""
    
    WORKSPACE_CAPACITY_CONSTRAINT = "workspace_capacity_constraint"
    """Workspace capacity limit reached."""
    
    EXECUTIVE_DEPENDENCY_UNSATISFIED = "executive_dependency_unsatisfied"
    """Executive network dependency not satisfied."""
    
    REWARD_EVALUATION_PENDING = "reward_evaluation_pending"
    """Reward evaluation waiting for outcome."""
    
    PREDICTIVE_STATE_INCOMPLETE = "predictive_state_incomplete"
    """Predictive state lacks required observations."""
    
    SENSORIMOTOR_READINESS_UNAVAILABLE = "sensorimotor_readiness_unavailable"
    """Sensorimotor readiness cannot be determined."""
    
    ALERTING_INTERRUPTION_ACTIVE = "alerting_interruption_active"
    """Alert interruption active, limiting other networks."""
    
    UNKNOWN = "unknown"
    """Finding type unknown."""


# =============================================================================
# LIMITATION CODES
# =============================================================================

class LimitationCode(Enum):
    """
    Canonical codes for coordination limitations.
    
    Limitations describe degraded completeness without invalidating the state.
    
    COORD-LAW-031: Limitations remain explicit
    COORD-LAW-032: Limitations preserve recoverability information
    """
    PARTIAL_MEMBERSHIP = "partial_membership"
    """Not all networks participated."""
    
    DEGRADED_PARTICIPATION = "degraded_participation"
    """Some networks participated with degraded capability."""
    
    OPTIONAL_NETWORK_UNAVAILABLE = "optional_network_unavailable"
    """Optional network was unavailable."""
    
    INCOMPLETE_PROJECTION_SET = "incomplete_projection_set"
    """Not all required projections were provided."""
    
    UNKNOWN_TRANSITION_STATE = "unknown_transition_state"
    """Transition state cannot be determined."""
    
    UNRESOLVED_COGNITIVE_CONFLICT = "unresolved_cognitive_conflict"
    """Cognitive conflict remains unresolved."""
    
    STALE_SEMANTIC_CONTEXT = "stale_semantic_context"
    """Semantic context may be outdated."""
    
    INSUFFICIENT_PROVENANCE = "insufficient_provenance"
    """Provenance information is incomplete."""
    
    UNKNOWN_CAPABILITY_PROVIDER = "unknown_capability_provider"
    """Capability provider identity unknown."""
    
    POLICY_RESTRICTED_COORDINATION = "policy_restricted_coordination"
    """Policy restricts coordination options."""
    
    PARTIAL_DETERMINISM = "partial_determinism"
    """Deterministic ordering cannot be fully guaranteed."""


# =============================================================================
# PROVENANCE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class Provenance:
    """
    Immutable provenance record for a coordination artifact.
    
    PROVENANCE-INV-001: Provenance is immutable
    PROVENANCE-INV-002: Provenance has no runtime references
    
    COORD-LAW-033: Provenance is preserved throughout coordination
    """
    source_identity: str
    """Identity of the source artifact."""
    
    created_at_sequence: int = 0
    """Sequence number for ordering within a cycle."""
    
    source_version: str = "1.0.0"
    """Version of the source component."""
    
    source_kind: str = "unknown"
    """Kind of source artifact."""
    
    correlation_id: str = ""
    """Correlation ID linking related artifacts."""


# =============================================================================
# SEMANTIC TIME REFERENCE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticTimeReference:
    """
    Reference to a point in semantic time.
    
    Unlike wall-clock time, semantic time represents meaningful coordination
    boundaries that are stable across runs.
    
    COORD-LAW-034: Semantic time remains external (not wall-clock)
    """
    cycle_id: str
    """Identifier for the coordination cycle."""
    
    step_index: int = 0
    """Index of this reference within the cycle."""
    
    @classmethod
    def from_cycle(cls, cycle_id: str) -> SemanticTimeReference:
        """Create a time reference from a cycle ID."""
        return cls(cycle_id=cycle_id)