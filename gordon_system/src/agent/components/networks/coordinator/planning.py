# Gordon Cognitive Architecture - Phase 4.11.3
# ===========================================

"""
Cross-Network Dependency Resolution and Coordination Planning
=============================================================

This module implements the declarative coordination planning infrastructure.

PLANNING PRINCIPLES
===================

1. PLANNING IS DECLARATIVE
   The Coordination Network produces immutable structural plans, not executable
   tasks. Plans describe:
   - Which networks participate
   - What capabilities each provides
   - What dependencies exist between participants
   - Why each participant is included

2. NO EXECUTION LOGIC
   Plans contain no runtime code. Execution belongs elsewhere.

3. DETERMINISTIC
   Equivalent inputs produce equivalent outputs. No randomness or runtime ordering.

4. EXPLAINABLE
   Every plan element has explicit provenance and justification.

5. TRACEABLE
   All dependency paths, provider selections, and decisions preserve their
   derivation chain.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# PROVIDER PRIORITY
# =============================================================================

class ProviderPriority(Enum):
    """
    Priority level for a capability provider candidate.
    
    PROVIDER-SELECTION-LAW-001: Provider selection follows explicit policy
    PROVIDER-SELECTION-LAW-002: Priority never inferred from runtime order
    PROVIDER-SELECTION-LAW-003: Tie-breaking remains deterministic
    
    Suggested priority levels per spec:
        PRIMARY
        SECONDARY  
        FALLBACK
        EXPERIMENTAL
        EMERGENCY (added for completeness)
        UNRANKED
        UNKNOWN
    """
    PRIMARY = auto()
    """Primary provider - preferred when available."""
    
    SECONDARY = auto()
    """Secondary provider - used if primary unavailable."""
    
    FALLBACK = auto()
    """Fallback provider - used when primary/secondary fail."""
    
    EXPERIMENTAL = auto()
    """Experimental provider - for testing or future use."""
    
    EMERGENCY = auto()
    """Emergency provider - only in critical scenarios."""
    
    UNRANKED = auto()
    """No priority ranking."""
    
    UNKNOWN = auto()
    """Priority unknown."""


# =============================================================================
# PROVIDER COMPATIBILITY STATUS
# =============================================================================

class ProviderCompatibilityStatus(Enum):
    """
    Compatibility status between a requirement and a candidate provider.
    
    PROVIDER-LAW-001: Provider candidates satisfy declared capability requirements
    PROVIDER-LAW-002: Provider matching validates semantic compatibility
    
    Suggested states per spec:
        COMPATIBLE
        COMPATIBLE_WITH_LIMITATIONS
        CONDITIONALLY_COMPATIBLE
        INCOMPATIBLE
        UNDETERMINED
        UNKNOWN
    """
    COMPATIBLE = "compatible"
    """Provider fully compatible with requirement."""
    
    COMPATIBLE_WITH_LIMITATIONS = "compatible_with_limitations"
    """Provider compatible but with known limitations."""
    
    CONDITIONALLY_COMPATIBLE = "conditionally_compatible"
    """Provider compatible only if conditions are met."""
    
    INCOMPATIBLE = "incompatible"
    """Provider incompatible with requirement."""
    
    UNDETERMINED = "undetermined"
    """Compatibility cannot be determined."""
    
    UNKNOWN = "unknown"
    """Unknown compatibility status."""


# =============================================================================
# PROVIDER SELECTION MODES
# =============================================================================

class ProviderSelectionMode(Enum):
    """
    Mode for selecting capability providers.
    
    Suggested modes per spec:
        SINGLE
        MULTIPLE_REQUIRED
        MULTIPLE_OPTIONAL
        PARALLEL
        PRIMARY_WITH_FALLBACK
        CONSENSUS_REQUIRED
        ANY_COMPATIBLE
        DEFERRED
        UNSATISFIED
        UNKNOWN
    """
    SINGLE = "single"
    """Exactly one provider selected."""
    
    MULTIPLE_REQUIRED = "multiple_required"
    """Multiple providers all required."""
    
    MULTIPLE_OPTIONAL = "multiple_optional"
    """Multiple providers but only some required."""
    
    PARALLEL = "parallel"
    """Providers can operate in parallel."""
    
    PRIMARY_WITH_FALLBACK = "primary_with_fallback"
    """Primary selected with fallback available."""
    
    CONSENSUS_REQUIRED = "consensus_required"
    """All selected providers must agree."""
    
    ANY_COMPATIBLE = "any_compatible"
    """Any compatible provider is acceptable."""
    
    DEFERRED = "deferred"
    """Selection deferred to later stage."""
    
    UNSATISFIED = "unsatisfied"
    """No provider selection - requirement unsatisfied."""
    
    UNKNOWN = "unknown"
    """Unknown selection mode."""


# =============================================================================
# REQUIREMENT SATISFACTION STATUS
# =============================================================================

class RequirementSatisfactionStatus(Enum):
    """
    Status indicating how a requirement is satisfied.
    
    Suggested statuses per spec:
        SATISFIED
        SATISFIED_WITH_LIMITATIONS
        CONDITIONALLY_SATISFIED
        DEFERRED
        BLOCKED
        UNSATISFIED
        IMPOSSIBLE
        UNKNOWN
    """
    SATISFIED = "satisfied"
    """Requirement fully satisfied."""
    
    SATISFIED_WITH_LIMITATIONS = "satisfied_with_limitations"
    """Requirement satisfied but with limitations."""
    
    CONDITIONALLY_SATISFIED = "conditionally_satisfied"
    """Requirement satisfied only if conditions are met."""
    
    DEFERRED = "deferred"
    """Satisfaction deferred to later coordination cycle."""
    
    BLOCKED = "blocked"
    """Satisfaction blocked by active constraints."""
    
    UNSATISFIED = "unsatisfied"
    """Requirement not satisfied."""
    
    IMPOSSIBLE = "impossible"
    """Requirement cannot be satisfied (no provider, etc.)."""
    
    UNKNOWN = "unknown"
    """Satisfaction status unknown."""


# =============================================================================
# DEPENDENCY KINDS
# =============================================================================

class CoordinationDependencyKind(Enum):
    """
    Kinds of dependencies in coordination plans.
    
    DEPENDENCY-LAW-001: Dependencies shall be explicit
    DEPENDENCY-LAW-002: Dependency identity shall remain stable
    
    Suggested kinds adapted from existing enums:
        DEPENDS_ON
        REQUIRES_BEFORE  
        REQUIRES_AFTER
        REQUIRES_TOGETHER
        OPTIONAL_DEPENDENCY
        MUTUAL_SYNCHRONIZATION
        UNKNOWN
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
    
    CONDITIONAL = "conditional"
    """Dependency only active when conditions are met."""
    
    TRANSITIVE = "transitive"
    """Transitively derived dependency."""
    
    FALLBACK = "fallback"
    """Fallback path dependency."""
    
    UNKNOWN = "unknown"
    """Unknown dependency kind."""


# =============================================================================
# SYNCHRONIZATION GROUP KINDS
# =============================================================================

class SynchronizationGroupKind(Enum):
    """
    Kinds of synchronization groups.
    
    Suggested kinds per spec:
        REQUIRED
        OPTIONAL
        PARALLEL
        SERIAL
        HYBRID
        FALLBACK
        RECOVERY
        OBSERVATION
        FEEDBACK
        FIXED_POINT
        UNKNOWN
    """
    REQUIRED = "required"
    """Group members required for plan validity."""
    
    OPTIONAL = "optional"
    """Group members optional."""
    
    PARALLEL = "parallel"
    """Members can execute in parallel."""
    
    SERIAL = "serial"
    """Members must execute in strict order."""
    
    HYBRID = "hybrid"
    """Mixed parallel and serial execution."""
    
    FALLBACK = "fallback"
    """Fallback group for recovery scenarios."""
    
    RECOVERY = "recovery"
    """Recovery-specific group."""
    
    OBSERVATION = "observation"
    """Observation-only group (no direct participation)."""
    
    FEEDBACK = "feedback"
    """Feedback loop participants."""
    
    FIXED_POINT = "fixed_point"
    """Fixed-point iteration participants."""
    
    UNKNOWN = "unknown"
    """Unknown group kind."""


# =============================================================================
# DEADLOCK KINDS
# =============================================================================

class DeadlockKind(Enum):
    """
    Kinds of deadlocks in coordination.
    
    Suggested kinds per spec:
        MUTUAL_WAIT
        CAPABILITY_ABSENCE
        CIRCULAR_REQUIREMENT  
        CONSTRAINT_LOCK
        PARTICIPATION_LOCK
        TRANSITION_LOCK
        REVISION_LOCK
        UNKNOWN
    """
    MUTUAL_WAIT = "mutual_wait"
    """Participants waiting on each other."""
    
    CAPABILITY_ABSENCE = "capability_absence"
    """Required capability not available."""
    
    CIRCULAR_REQUIREMENT = "circular_requirement"
    """Circular requirement chain."""
    
    CONSTRAINT_LOCK = "constraint_lock"
    """Constraints block progress."""
    
    PARTICIPATION_LOCK = "participation_lock"
    """Participation requirements lock execution."""
    
    TRANSITION_LOCK = "transition_lock"
    """Transition state locks progress."""
    
    REVISION_LOCK = "revision_lock"
    """Semantic revision incompatibility."""
    
    UNKNOWN = "unknown"
    """Unknown deadlock kind."""


# =============================================================================
# DEPENDENCY PATH KINDS
# =============================================================================

class DependencyPathKind(Enum):
    """
    Kinds of dependency paths.
    
    Suggested kinds per spec:
        PRIMARY
        ALTERNATIVE
        FALLBACK
        OPTIONAL
        RECOVERY
        BLOCKED
        UNKNOWN
    """
    PRIMARY = "primary"
    """Primary dependency path."""
    
    ALTERNATIVE = "alternative"
    """Alternative valid dependency path."""
    
    FALLBACK = "fallback"
    """Fallback dependency path."""
    
    OPTIONAL = "optional"
    """Optional dependency path."""
    
    RECOVERY = "recovery"
    """Recovery path after failure."""
    
    BLOCKED = "blocked"
    """Blocked path that cannot be satisfied."""
    
    UNKNOWN = "unknown"
    """Unknown path kind."""


# =============================================================================
# CYCLE CLASSIFICATION
# =============================================================================

class CycleClassification(Enum):
    """
    Classification of dependency cycles.
    
    Suggested classifications per spec:
        ACYCLIC
        INVALID_STRUCTURAL_CYCLE
        MUTUAL_SYNCHRONIZATION
        ITERATIVE_FEEDBACK
        FIXED_POINT_LOOP
        RECOVERY_LOOP
        EXECUTIVE_FEEDBACK_LOOP
        SENSORIMOTOR_FEEDBACK_LOOP  
        PREDICTIVE_REWARD_FEEDBACK_LOOP
        UNRESOLVED
        UNKNOWN
    """
    ACYCLIC = "acyclic"
    """No cycle detected."""
    
    INVALID_STRUCTURAL_CYCLE = "invalid_structural_cycle"
    """Invalid structural deadlock."""
    
    MUTUAL_SYNCHRONIZATION = "mutual_synchronization"
    """Valid mutual synchronization loop."""
    
    ITERATIVE_FEEDBACK = "iterative_feedback"
    """Iterative feedback loop (valid)."""
    
    FIXED_POINT_LOOP = "fixed_point_loop"
    """Fixed-point iteration loop."""
    
    RECOVERY_LOOP = "recovery_loop"
    """Recovery mechanism loop."""
    
    EXECUTIVE_FEEDBACK_LOOP = "executive_feedback_loop"
    """Executive feedback loop."""
    
    SENSORIMOTOR_FEEDBACK_LOOP = "sensorimotor_feedback_loop"
    """Sensorimotor feedback loop."""
    
    PREDICTIVE_REWARD_FEEDBACK_LOOP = "predictive_reward_feedback_loop"
    """Predictive-reward feedback loop."""
    
    UNRESOLVED = "unresolved"
    """Cycle classification unresolved."""
    
    UNKNOWN = "unknown"
    """Unknown cycle type."""


# =============================================================================
# NORMALIZED REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class NormalizedRequirement:
    """
    Canonical form of a requirement after normalization.
    
    One normalized requirement may represent several equivalent source
    requirements that have been merged.
    
    Suggested fields per spec:
        identity
        source_requirements
        requesting_networks  
        requested_capability
        capability_version_constraint
        provider_constraints
        requirement_strength
        semantic_scope
        activation_condition
        satisfaction_policy
        semantic_deadline
        confidence
        uncertainty
        provenance
        revision
    """
    identity: str
    """Unique identifier for this normalized requirement."""
    
    requested_capability: str
    """Canonical capability identifier being requested."""
    
    source_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Source requirement references that were merged."""
    
    requesting_networks: tuple[str, ...] = field(default_factory=tuple)
    """Networks that request this capability."""
    
    capability_version_constraint: Optional[str] = None
    """Version constraint on the required capability (e.g., ">=1.0")."""
    
    provider_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Constraints on acceptable providers."""
    
    requirement_strength: str = "required"
    """Strength of requirement (required, optional, preferred)."""
    
    semantic_scope: Optional[str] = None
    """Semantic scope for this requirement."""
    
    activation_condition: Optional[str] = None
    """Condition that activates this requirement."""
    
    satisfaction_policy: str = "best_effort"
    """Policy for satisfying this requirement."""
    
    semantic_deadline: Optional[int] = None
    """Deadline in coordination cycle steps."""
    
    confidence: float = 0.5
    """Confidence in the requirement's validity (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this requirement (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this requirement."""
    
    revision: int = 1
    """Revision number of this normalized requirement."""


# =============================================================================
# NORMALIZED CAPABILITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class NormalizedCapability:
    """
    Canonical form of a capability after normalization.
    
    Suggested fields per spec:
        identity
        source_capabilities  
        capability_kind
        provider_network
        output_contract
        contract_version
        semantic_scope
        availability
        readiness_reference
        limitations
        confidence
        uncertainty
        provenance
        revision
    """
    identity: str
    """Unique identifier for this normalized capability."""
    
    source_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Source capability references that were merged."""
    
    capability_kind: str
    """Canonical kind of capability (e.g., "PredictiveModel")."""
    
    provider_network: str
    """Network identity providing this capability."""
    
    output_contract: Optional[str] = None
    """Output contract specification."""
    
    contract_version: str = "1.0.0"
    """Version of the output contract."""
    
    semantic_scope: Optional[str] = None
    """Semantic scope for this capability."""
    
    availability: str = "available"
    """Availability state (available, unavailable, degraded)."""
    
    readiness_reference: Optional[str] = None
    """Reference to readiness state for this capability."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this capability."""
    
    confidence: float = 0.5
    """Confidence in the capability's accuracy (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this capability (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this capability."""
    
    revision: int = 1
    """Revision number of this normalized capability."""


# =============================================================================
# CAPABILITY PROVIDER CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CapabilityProviderCandidate:
    """
    A candidate provider for satisfying a requirement.
    
    This represents: "This provider may satisfy this requirement."
    It does NOT mean the provider has been selected.
    
    Suggested fields per spec:
        identity
        requirement_reference
        capability_reference
        provider_network
        compatibility
        availability
        readiness
        provider_priority
        limitations
        confidence
        uncertainty
        provenance
    """
    identity: str
    """Unique identifier for this candidate."""
    
    requirement_reference: str
    """Reference to the requirement being satisfied."""
    
    capability_reference: str
    """Reference to the capability being provided."""
    
    provider_network: str
    """Network identity providing the capability."""
    
    compatibility: ProviderCompatibilityStatus = ProviderCompatibilityStatus.COMPATIBLE
    """Compatibility status between requirement and candidate."""
    
    availability: str = "available"
    """Provider's availability state."""
    
    readiness: Optional[str] = None
    """Reference to provider's readiness state."""
    
    provider_priority: ProviderPriority = ProviderPriority.UNKNOWN
    """Priority ranking for this candidate."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this provider candidate."""
    
    confidence: float = 0.5
    """Confidence in this candidate (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this candidate (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this candidate."""


# =============================================================================
# PROVIDER COMPATIBILITY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ProviderCompatibility:
    """
    Detailed compatibility analysis between a requirement and provider.
    
    Suggested fields per spec:
        requirement_reference
        provider_candidate_reference
        status
        contract_compatibility
        semantic_scope_compatibility  
        domain_compatibility
        revision_compatibility
        active_constraints
        limitations
        confidence
        uncertainty
        provenance
    """
    requirement_reference: str
    """Reference to the requirement being analyzed."""
    
    provider_candidate_reference: str
    """Reference to the provider candidate being analyzed."""
    
    status: ProviderCompatibilityStatus = ProviderCompatibilityStatus.UNKNOWN
    """Overall compatibility status."""
    
    contract_compatibility: bool = False
    """Whether contracts are compatible."""
    
    semantic_scope_compatibility: bool = False
    """Whether semantic scopes match."""
    
    domain_compatibility: bool = False
    """Whether domains match."""
    
    revision_compatibility: bool = False
    """Whether revisions are compatible."""
    
    active_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Active constraints affecting compatibility."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Known compatibility limitations."""
    
    confidence: float = 0.5
    """Confidence in compatibility analysis (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about compatibility (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this compatibility analysis."""


# =============================================================================
# PROVIDER SELECTION
# =============================================================================

@dataclass(frozen=True, slots=True)
class CapabilityProviderSelection:
    """
    Declarative selection of provider candidates for a requirement.
    
    Suggested fields per spec:
        identity
        requirement_reference
        selected_provider_candidates
        selection_mode  
        rejected_provider_candidates
        deferred_provider_candidates
        fallback_provider_candidates
        selection_rationale
        policy_reference
        confidence
        uncertainty
        provenance
    """
    identity: str
    """Unique identifier for this selection."""
    
    requirement_reference: str
    """Reference to the requirement being satisfied."""
    
    selected_provider_candidates: tuple[str, ...] = field(default_factory=tuple)
    """References to candidates that were selected."""
    
    selection_mode: ProviderSelectionMode = ProviderSelectionMode.UNKNOWN
    """Mode used to make this selection."""
    
    rejected_provider_candidates: tuple[str, ...] = field(default_factory=tuple)
    """References to candidates that were rejected."""
    
    deferred_provider_candidates: tuple[str, ...] = field(default_factory=tuple)
    """References to candidates that were deferred."""
    
    fallback_provider_candidates: tuple[str, ...] = field(default_factory=tuple)
    """Fallback provider references for this selection."""
    
    selection_rationale: Optional[str] = None
    """Human-readable rationale for the selection."""
    
    policy_reference: Optional[str] = None
    """Reference to policy governing this selection."""
    
    confidence: float = 0.5
    """Confidence in this selection (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this selection (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this selection."""


# =============================================================================
# RESOLVED REQUIREMENT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ResolvedRequirement:
    """
    Final resolution result for a requirement.
    
    Suggested fields per spec:
        normalized_requirement
        provider_selection  
        satisfaction_status
        direct_or_transitive
        activated_condition
        limitations
        confidence
        uncertainty
        provenance
    """
    normalized_requirement: NormalizedRequirement
    """The original normalized requirement."""
    
    provider_selection: Optional[CapabilityProviderSelection] = None
    """Provider selection satisfying this requirement (if any)."""
    
    satisfaction_status: RequirementSatisfactionStatus = RequirementSatisfactionStatus.UNKNOWN
    """Final satisfaction status."""
    
    direct_or_transitive: str = "direct"
    """Whether this is a direct or transitive requirement."""
    
    activated_condition: Optional[str] = None
    """Condition that activated this requirement (if conditional)."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the satisfaction."""
    
    confidence: float = 0.5
    """Confidence in resolution (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about resolution (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this resolution."""


# =============================================================================
# NORMALIZED COORDINATION DEPENDENCY
# =============================================================================

@dataclass(frozen=True, slots=True)
class NormalizedCoordinationDependency:
    """
    Canonical form of a coordination dependency.
    
    Suggested fields per spec:
        identity
        source_dependencies
        dependent_reference  
        prerequisite_reference
        dependency_kind
        strength
        activation_condition
        semantic_scope
        synchronization_semantics
        confidence
        uncertainty
        provenance
        revision
    """
    identity: str
    """Unique identifier for this normalized dependency."""
    
    source_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Source dependency references that were merged."""
    
    dependent_reference: str
    """Reference to the component with the dependency."""
    
    prerequisite_reference: str
    """Reference to what is required."""
    
    dependency_kind: CoordinationDependencyKind = CoordinationDependencyKind.UNKNOWN
    """Kind of this dependency."""
    
    strength: str = "hard"
    """Strength of dependency (hard, soft, optional)."""
    
    activation_condition: Optional[str] = None
    """Condition that activates this dependency."""
    
    semantic_scope: Optional[str] = None
    """Semantic scope for this dependency."""
    
    synchronization_semantics: Optional[str] = None
    """Synchronization semantics (if any)."""
    
    confidence: float = 0.5
    """Confidence in this dependency (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this dependency (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this dependency."""
    
    revision: int = 1
    """Revision number of this normalized dependency."""


# =============================================================================
# COORDINATION DEPENDENCY PATH
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDependencyPath:
    """
    A complete path through the dependency graph.
    
    Suggested fields per spec:
        identity
        root_requirement
        terminal_capability
        nodes
        edges  
        path_kind
        completeness
        confidence
        uncertainty
        provenance
    """
    identity: str
    """Unique identifier for this path."""
    
    root_requirement: str
    """Reference to the starting requirement."""
    
    terminal_capability: str
    """Reference to the terminating capability."""
    
    nodes: tuple[str, ...] = field(default_factory=tuple)
    """All nodes in this dependency path."""
    
    edges: tuple[str, ...] = field(default_factory=tuple)
    """All edges (dependencies) in this path."""
    
    path_kind: DependencyPathKind = DependencyPathKind.UNKNOWN
    """Kind of this path."""
    
    completeness: str = "complete"
    """Completeness status (complete, partial, incomplete)."""
    
    confidence: float = 0.5
    """Confidence in this path (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this path (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this path."""


# =============================================================================
# COORDINATION DEPENDENCY CLOSURE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDependencyClosure:
    """
    Complete closure of all dependencies from root requirements.
    
    Suggested fields per spec:
        root_requirements
        direct_dependencies  
        transitive_dependencies
        optional_dependencies
        conditional_dependencies
        unresolved_dependencies
        closure_depth
        findings
        limitations
        provenance
    """
    root_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Root requirements for this closure."""
    
    direct_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Direct dependencies of root requirements."""
    
    transitive_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Transitively derived dependencies."""
    
    optional_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Optional dependency references."""
    
    conditional_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Conditional dependency references."""
    
    unresolved_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Unresolved dependency references."""
    
    closure_depth: int = 0
    """Maximum depth of the closure tree."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during closure computation."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this closure."""
    
    provenance: Optional[str] = None
    """Provenance reference for this closure."""


# =============================================================================
# COORDINATION SYNCHRONIZATION GROUP
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationSynchronizationGroup:
    """
    A group of participants that synchronize together.
    
    Suggested fields per spec:
        identity
        group_kind
        participant_references  
        capability_references
        requirement_references
        entry_conditions
        exit_conditions
        internal_dependencies
        external_dependencies
        synchronization_barrier_reference
        confidence
        uncertainty
        provenance
    """
    identity: str
    """Unique identifier for this group."""
    
    group_kind: SynchronizationGroupKind = SynchronizationGroupKind.UNKNOWN
    """Kind of this synchronization group."""
    
    participant_references: tuple[str, ...] = field(default_factory=tuple)
    """Network references in this group."""
    
    capability_references: tuple[str, ...] = field(default_factory=tuple)
    """Capability references for this group."""
    
    requirement_references: tuple[str, ...] = field(default_factory=tuple)
    """Requirement references for this group."""
    
    entry_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be true before group execution."""
    
    exit_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be true after group execution."""
    
    internal_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Dependencies between group members."""
    
    external_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Dependencies on participants outside this group."""
    
    synchronization_barrier_reference: Optional[str] = None
    """Reference to the synchronization barrier for this group."""
    
    confidence: float = 0.5
    """Confidence in this group's structure (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this group (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this group."""


# =============================================================================
# COORDINATION DEPENDENCY LAYER
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDependencyLayer:
    """
    A semantic layer in the coordination dependency structure.
    
    Layer index is semantic ordering (not runtime timestamp).
    
    Suggested fields per spec:
        identity
        layer_index
        participant_references  
        capability_references
        requirement_references
        predecessor_layers
        successor_layers
        synchronization_groups
        entry_conditions
        exit_conditions
        findings
        limitations
        provenance
    """
    identity: str
    """Unique identifier for this layer."""
    
    layer_index: int = 0
    """Semantic position in the dependency ordering."""
    
    participant_references: tuple[str, ...] = field(default_factory=tuple)
    """Network references in this layer."""
    
    capability_references: tuple[str, ...] = field(default_factory=tuple)
    """Capability references for this layer."""
    
    requirement_references: tuple[str, ...] = field(default_factory=tuple)
    """Requirement references for this layer."""
    
    predecessor_layers: tuple[int, ...] = field(default_factory=tuple)
    """Layer indices that must execute before this one."""
    
    successor_layers: tuple[int, ...] = field(default_factory=tuple)
    """Layer indices that must execute after this one."""
    
    synchronization_groups: tuple[CoordinationSynchronizationGroup, ...] = field(
        default_factory=tuple
    )
    """Synchronization groups in this layer."""
    
    entry_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions required to enter this layer."""
    
    exit_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions guaranteed after completing this layer."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during layer construction."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this layer."""
    
    provenance: Optional[str] = None
    """Provenance reference for this layer."""


# =============================================================================
# COORDINATION FALLBACK PATH
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationFallbackPath:
    """
    A fallback path when primary providers fail.
    
    Suggested fields per spec:
        identity
        failed_requirement_reference
        primary_provider_reference  
        fallback_provider_references
        activation_conditions
        degraded_capabilities
        semantic_consequences
        confidence_effect
        uncertainty_effect
        provenance
    """
    identity: str
    """Unique identifier for this fallback path."""
    
    failed_requirement_reference: str
    """Reference to the requirement that failed."""
    
    primary_provider_reference: Optional[str] = None
    """Reference to the primary provider (if known)."""
    
    fallback_provider_references: tuple[str, ...] = field(default_factory=tuple)
    """References to fallback providers."""
    
    activation_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that activate this fallback path."""
    
    degraded_capabilities: tuple[str, ...] = field(default_factory=tuple)
    """Capabilities available via fallback (may be reduced)."""
    
    semantic_consequences: tuple[str, ...] = field(default_factory=tuple)
    """Semantic consequences of using this fallback."""
    
    confidence_effect: float = 0.5
    """Effect on plan confidence when using this fallback."""
    
    uncertainty_effect: float = 0.5
    """Effect on plan uncertainty when using this fallback."""
    
    provenance: Optional[str] = None
    """Provenance reference for this fallback path."""


# =============================================================================
# COORDINATION RECOVERY PATH
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationRecoveryPath:
    """
    A recovery plan after a failed coordination cycle.
    
    Recovery differs from fallback:
    - Fallback: Use alternate provider before failure
    - Recovery: Construct new plan after failure
    
    Suggested fields per spec:
        failed_plan_reference
        recoverable_findings  
        replacement_requirements
        replacement_providers
        excluded_participants
        degraded_conditions
        recovery_dependencies
        provenance
    """
    identity: str
    """Unique identifier for this recovery path."""
    
    failed_plan_reference: str
    """Reference to the plan that failed."""
    
    recoverable_findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings from failed plan that may be recovered."""
    
    replacement_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Requirements to re-satisfy in recovery."""
    
    replacement_providers: tuple[str, ...] = field(default_factory=tuple)
    """Provider references for recovery."""
    
    excluded_participants: tuple[str, ...] = field(default_factory=tuple)
    """Participants excluded from recovery plan."""
    
    degraded_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that are acceptable in recovery."""
    
    recovery_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Dependencies for recovery execution."""
    
    provenance: Optional[str] = None
    """Provenance reference for this recovery path."""


# =============================================================================
# COORDINATION DEADLOCK
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDeadlock:
    """
    A deadlock in the coordination plan.
    
    Suggested fields per spec:
        identity
        participating_references  
        blocking_dependencies
        missing_initial_conditions
        unavailable_fallbacks
        deadlock_kind
        severity
        recoverability
        owning_resolution_authority
        findings
        provenance
    """
    identity: str
    """Unique identifier for this deadlock."""
    
    participating_references: tuple[str, ...] = field(default_factory=tuple)
    """Network references involved in the deadlock."""
    
    blocking_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Dependencies causing the deadlock."""
    
    missing_initial_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Initial conditions that are missing."""
    
    unavailable_fallbacks: tuple[str, ...] = field(default_factory=tuple)
    """Fallback options that are unavailable."""
    
    deadlock_kind: DeadlockKind = DeadlockKind.UNKNOWN
    """Kind of deadlock."""
    
    severity: str = "medium"
    """Severity level (low, medium, high, critical)."""
    
    recoverability: str = "unknown"
    """Recoverability status (recoverable, unrecoverable, unknown)."""
    
    owning_resolution_authority: Optional[str] = None
    """Authority responsible for resolving this deadlock."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings about this deadlock."""
    
    provenance: Optional[str] = None
    """Provenance reference for this deadlock."""


# =============================================================================
# COORDINATION PLAN CANDIDATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlanCandidate:
    """
    A candidate coordination plan before final selection.
    
    Suggested fields per spec:
        identity
        participants  
        provider_selections
        resolved_requirements
        dependency_closure
        synchronization_groups
        dependency_layers
        fallback_paths
        unresolved_dependencies
        active_constraints
        deadlocks
        completeness
        consistency
        minimality
        confidence
        uncertainty
        findings
        limitations
        provenance
    """
    identity: str
    """Unique identifier for this candidate."""
    
    participants: tuple[str, ...] = field(default_factory=tuple)
    """Network references that would participate."""
    
    provider_selections: tuple[CapabilityProviderSelection, ...] = field(
        default_factory=tuple
    )
    """Provider selections for requirements."""
    
    resolved_requirements: tuple[ResolvedRequirement, ...] = field(
        default_factory=tuple
    )
    """Resolution results for all requirements."""
    
    dependency_closure: CoordinationDependencyClosure = field(
        default_factory=lambda: CoordinationDependencyClosure()
    )
    """Complete dependency closure for this plan."""
    
    synchronization_groups: tuple[CoordinationSynchronizationGroup, ...] = field(
        default_factory=tuple
    )
    """Synchronization groups in this plan."""
    
    dependency_layers: tuple[CoordinationDependencyLayer, ...] = field(
        default_factory=tuple
    )
    """Semantic layers in this plan."""
    
    fallback_paths: tuple[CoordinationFallbackPath, ...] = field(default_factory=tuple)
    """Fallback paths available for this plan."""
    
    unresolved_dependencies: tuple[str, ...] = field(default_factory=tuple)
    """Dependencies that could not be resolved."""
    
    active_constraints: tuple[str, ...] = field(default_factory=tuple)
    """Active constraints affecting this plan."""
    
    deadlocks: tuple[CoordinationDeadlock, ...] = field(default_factory=tuple)
    """Deadlocks in this plan (if any)."""
    
    completeness: str = "unknown"
    """Completeness status of this plan."""
    
    consistency: str = "unknown"
    """Consistency status of this plan."""
    
    minimality: str = "unknown"
    """Minimality status of this plan."""
    
    confidence: float = 0.5
    """Overall confidence in this candidate (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Overall uncertainty about this candidate (0.0-1.0)."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during candidate construction."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this plan candidate."""
    
    provenance: Optional[str] = None
    """Provenance reference for this candidate."""


# =============================================================================
# COORDINATION PLAN ALTERNATIVE
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlanAlternative:
    """
    An alternative coordination plan to the selected one.
    
    Suggested fields per spec:
        identity
        plan  
        difference_from_selected_plan
        selection_status
        rejection_reasons
        confidence
        uncertainty
        provenance
    """
    identity: str
    """Unique identifier for this alternative."""
    
    plan: CoordinationPlanCandidate = field(
        default_factory=lambda: CoordinationPlanCandidate(identity="")
    )
    """The alternative plan candidate."""
    
    difference_from_selected_plan: tuple[str, ...] = field(default_factory=tuple)
    """Description of differences from selected plan."""
    
    selection_status: str = "candidate"
    """Current status (candidate, rejected, active)."""
    
    rejection_reasons: tuple[str, ...] = field(default_factory=tuple)
    """Reasons why this was not selected (if applicable)."""
    
    confidence: float = 0.5
    """Confidence in this alternative plan (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about this alternative (0.0-1.0)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this alternative."""


# =============================================================================
# COORDINATION PLAN
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlan:
    """
    Final immutable coordination plan.
    
    The plan contains NO executable logic - only semantic structure.
    
    Suggested fields per spec:
        identity
        epoch_identity  
        cycle_identity
        coordination_domain
        root_requirements
        resolved_requirements
        provider_selections
        participants
        synchronization_groups
        dependency_layers
        dependency_closure
        fallback_paths
        recovery_paths
        transition_prerequisites
        synchronization_barriers
        blocked_operations
        deferred_operations
        completion_conditions
        completeness
        consistency
        minimality
        cost
        confidence
        uncertainty
        explanation
        findings
        limitations
        provenance
        revision
    """
    identity: str
    """Unique identifier for this plan."""
    
    epoch_identity: Optional[str] = None
    """Reference to the coordination epoch."""
    
    cycle_identity: Optional[str] = None
    """Reference to the coordination cycle."""
    
    coordination_domain: str = "general"
    """Domain of coordination (language, planning, navigation, vision, etc.)."""
    
    root_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Root requirements that initiated this plan."""
    
    resolved_requirements: tuple[ResolvedRequirement, ...] = field(default_factory=tuple)
    """Final resolution results for all requirements."""
    
    provider_selections: tuple[CapabilityProviderSelection, ...] = field(
        default_factory=tuple
    )
    """Final provider selections."""
    
    participants: tuple[str, ...] = field(default_factory=tuple)
    """Network references that participate in this plan."""
    
    synchronization_groups: tuple[CoordinationSynchronizationGroup, ...] = field(
        default_factory=tuple
    )
    """Synchronization groups for execution."""
    
    dependency_layers: tuple[CoordinationDependencyLayer, ...] = field(
        default_factory=tuple
    )
    """Semantic layers defining execution order."""
    
    dependency_closure: CoordinationDependencyClosure = field(
        default_factory=lambda: CoordinationDependencyClosure()
    )
    """Complete dependency closure."""
    
    fallback_paths: tuple[CoordinationFallbackPath, ...] = field(default_factory=tuple)
    """Available fallback paths for recovery."""
    
    recovery_paths: tuple[CoordinationRecoveryPath, ...] = field(default_factory=tuple)
    """Available recovery paths after failures."""
    
    transition_prerequisites: tuple[str, ...] = field(default_factory=tuple)
    """Prerequisites for transitions between layers."""
    
    synchronization_barriers: tuple[str, ...] = field(default_factory=tuple)
    """Synchronization barriers between layers."""
    
    blocked_operations: tuple[str, ...] = field(default_factory=tuple)
    """Operations that are blocked."""
    
    deferred_operations: tuple[str, ...] = field(default_factory=tuple)
    """Operations that are deferred to later cycles."""
    
    completion_conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions for plan completion."""
    
    completeness: str = "unknown"
    """Completeness status."""
    
    consistency: str = "unknown"
    """Consistency status."""
    
    minimality: str = "unknown"
    """Minimality status."""
    
    cost: Optional[float] = None
    """Semantic cost of executing this plan (optional)."""
    
    confidence: float = 0.5
    """Overall confidence in the plan (0.0-1.0)."""
    
    uncertainty: float = 0.5
    """Overall uncertainty about the plan (0.0-1.0)."""
    
    explanation: Optional[str] = None
    """Human-readable explanation of this plan."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during plan construction."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on this plan."""
    
    provenance: Optional[str] = None
    """Provenance reference for this plan."""
    
    revision: int = 1
    """Revision number of this plan."""


# =============================================================================
# DEPENDENCY RESOLUTION STATE
# =============================================================================

@dataclass(frozen=True, slots=True)
class DependencyResolutionState:
    """
    Complete state of dependency resolution computation.
    
    This supports auditability and testing by preserving all intermediate results.
    
    Suggested fields per spec:
        normalized_requirements
        normalized_capabilities  
        provider_candidates
        provider_compatibilities
        provider_selections
        resolved_requirements
        normalized_dependencies
        dependency_closure
        dependency_paths
        cycle_classifications
        deadlocks
        synchronization_groups
        dependency_layers
        fallback_paths
        plan_candidates
        selected_plan_reference
        alternative_plan_references
        findings
        limitations
        trace
        provenance
    """
    normalized_requirements: tuple[NormalizedRequirement, ...] = field(
        default_factory=tuple
    )
    """All normalized requirements."""
    
    normalized_capabilities: tuple[NormalizedCapability, ...] = field(
        default_factory=tuple
    )
    """All normalized capabilities."""
    
    provider_candidates: tuple[CapabilityProviderCandidate, ...] = field(
        default_factory=tuple
    )
    """All candidate providers."""
    
    provider_compatibilities: tuple[ProviderCompatibility, ...] = field(
        default_factory=tuple
    )
    """Compatibility analyses."""
    
    provider_selections: tuple[CapabilityProviderSelection, ...] = field(
        default_factory=tuple
    )
    """Provider selections (intermediate)."""
    
    resolved_requirements: tuple[ResolvedRequirement, ...] = field(default_factory=tuple)
    """Resolved requirements (intermediate)."""
    
    normalized_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Normalized dependencies."""
    
    dependency_closure: CoordinationDependencyClosure = field(
        default_factory=lambda: CoordinationDependencyClosure()
    )
    """Computed dependency closure."""
    
    dependency_paths: tuple[CoordinationDependencyPath, ...] = field(default_factory=tuple)
    """All dependency paths."""
    
    cycle_classifications: tuple[str, ...] = field(default_factory=tuple)
    """Cycle classification results."""
    
    deadlocks: tuple[CoordinationDeadlock, ...] = field(default_factory=tuple)
    """Detected deadlocks."""
    
    synchronization_groups: tuple[CoordinationSynchronizationGroup, ...] = field(
        default_factory=tuple
    )
    """Constructed synchronization groups."""
    
    dependency_layers: tuple[CoordinationDependencyLayer, ...] = field(
        default_factory=tuple
    )
    """Constructed dependency layers."""
    
    fallback_paths: tuple[CoordinationFallbackPath, ...] = field(default_factory=tuple)
    """Constructed fallback paths."""
    
    plan_candidates: tuple[CoordinationPlanCandidate, ...] = field(
        default_factory=tuple
    )
    """Generated plan candidates."""
    
    selected_plan_reference: Optional[str] = None
    """Reference to the selected plan (if any)."""
    
    alternative_plan_references: tuple[str, ...] = field(default_factory=tuple)
    """References to alternative plans."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during resolution."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on resolution."""
    
    trace: tuple[str, ...] = field(default_factory=tuple)
    """Execution trace for auditability."""
    
    provenance: Optional[str] = None
    """Provenance reference for this state."""


# =============================================================================
# COORDINATION PLANNING REQUEST (INPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlanningRequest:
    """
    Immutable request to the coordination planning engine.
    
    This is the INPUT contract for dependency resolution.
    
    Suggested fields per spec:
        identity
        epoch_identity  
        cycle_identity
        coordination_domain
        membership
        network_projections
        capability_registry
        requirements
        declared_dependencies
        constraints
        transition_intentions
        readiness_states
        availability_states
        participation_preferences
        planning_policy
        semantic_context
        semantic_time
        provenance
    """
    identity: str
    """Unique identifier for this request."""
    
    epoch_identity: Optional[str] = None
    """Reference to the coordination epoch."""
    
    cycle_identity: Optional[str] = None
    """Reference to the coordination cycle."""
    
    coordination_domain: str = "general"
    """Domain of coordination requested."""
    
    membership: tuple[str, ...] = field(default_factory=tuple)
    """Network identities that should participate."""
    
    network_projections: tuple[str, ...] = field(default_factory=tuple)
    """Projections from participating networks (as references)."""
    
    capability_registry: tuple[str, ...] = field(default_factory=tuple)
    """Available capabilities registry entries."""
    
    requirements: tuple[NormalizedRequirement, ...] = field(default_factory=tuple)
    """Root requirements to satisfy."""
    
    declared_dependencies: tuple[NormalizedCoordinationDependency, ...] = field(
        default_factory=tuple
    )
    """Declared dependencies between networks."""
    
    constraints: tuple[str, ...] = field(default_factory=tuple)
    """Active coordination constraints."""
    
    transition_intentions: tuple[str, ...] = field(default_factory=tuple)
    """Network transition intentions (declarative only)."""
    
    readiness_states: tuple[str, ...] = field(default_factory=tuple)
    """Readiness states of networks."""
    
    availability_states: tuple[str, ...] = field(default_factory=tuple)
    """Availability states of networks."""
    
    participation_preferences: tuple[str, ...] = field(default_factory=tuple)
    """Network participation preferences."""
    
    planning_policy: str = "default"
    """Policy for planning decisions."""
    
    semantic_context: Optional[str] = None
    """Semantic context reference."""
    
    semantic_time: Optional[int] = None
    """Semantic time index."""
    
    provenance: Optional[str] = None
    """Provenance reference for this request."""


# =============================================================================
# COORDINATION PLANNING RESULT (OUTPUT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlanningResult:
    """
    Immutable result from the coordination planning engine.
    
    This is the OUTPUT contract for dependency resolution.
    
    Suggested fields per spec:
        request_identity
        selected_plan  
        alternative_plans
        resolution_state
        findings
        limitations
        trace
        status
        provenance
    """
    request_identity: str
    """Reference to the original request."""
    
    selected_plan: Optional[CoordinationPlan] = None
    """The selected coordination plan (if successful)."""
    
    alternative_plans: tuple[CoordinationPlanAlternative, ...] = field(
        default_factory=tuple
    )
    """Alternative plans generated during planning."""
    
    resolution_state: DependencyResolutionState = field(
        default_factory=lambda: DependencyResolutionState()
    )
    """Complete resolution state for auditability."""
    
    findings: tuple[str, ...] = field(default_factory=tuple)
    """Findings during planning."""
    
    limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitations on the plan or planning process."""
    
    trace: tuple[str, ...] = field(default_factory=tuple)
    """Execution trace for auditability."""
    
    status: str = "unknown"
    """Overall planning status (success, partial_success, blocked, failed)."""
    
    provenance: Optional[str] = None
    """Provenance reference for this result."""


# =============================================================================
# COORDINATION PLANNING POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationPlanningPolicy:
    """
    Immutable policy governing coordination planning decisions.
    
    This remains immutable during planning - no executable callbacks allowed.
    
    Suggested concerns per spec:
        allowed providers
        preferred providers  
        fallback providers
        minimum compatibility
        minimum confidence
        accepted limitations
        degraded-provider rules
        parallel-provider rules
        consensus-provider rules
        deterministic tie-breaking
    """
    identity: str = "default"
    """Unique identifier for this policy."""
    
    allowed_providers: tuple[str, ...] = field(default_factory=tuple)
    """Allowed provider identities (empty = all allowed)."""
    
    preferred_providers: tuple[str, ...] = field(default_factory=tuple)
    """Preferred provider identities (ordered by priority)."""
    
    fallback_providers: tuple[str, ...] = field(default_factory=tuple)
    """Fallback providers when preferred unavailable."""
    
    minimum_compatibility: str = "compatible"
    """Minimum compatibility level required (compatible, undetermined, unknown)."""
    
    minimum_confidence: float = 0.5
    """Minimum confidence threshold for selections."""
    
    accepted_limitations: tuple[str, ...] = field(default_factory=tuple)
    """Limitation types that are acceptable."""
    
    degraded_provider_allowed: bool = False
    """Whether degraded providers may be selected."""
    
    parallel_provider_policy: str = "optional"
    """Policy for parallel providers (required, optional, forbidden)."""
    
    consensus_required_for: tuple[str, ...] = field(default_factory=tuple)
    """Requirements requiring consensus among multiple providers."""
    
    tiebreaker_keys: tuple[str, ...] = (
        "provider_priority",
        "network_kind",
        "network_identity",
        "capability_contract_version",
        "capability_identity",
        "projection_revision",
    )
    """Keys for deterministic tie-breaking (in order of precedence)."""
    
    cycle_classification: str = "strict"
    """Strictness of cycle classification (strict, permissive, unknown)."""
    
    deadlock_detection: str = "active"
    """Whether to detect deadlocks (active, passive, disabled)."""
    
    fallback_policy: str = "explicit"
    """Policy for fallback paths (explicit, implicit, none)."""
    
    minimality_requirement: str = "strict"
    """Minimality requirement level (strict, lenient, unknown)."""
    
    completeness_threshold: float = 0.8
    """Minimum completeness threshold for valid plans."""
    
    consistency_check: bool = True
    """Whether to perform consistency checks."""
    
    provenance_tracking: str = "full"
    """Provenance tracking level (none, minimal, full)."""
    
    @classmethod
    def default_policy(cls) -> CoordinationPlanningPolicy:
        """Create the default coordination planning policy."""
        return cls()
    
    @classmethod
    def permissive_policy(cls) -> CoordinationPlanningPolicy:
        """Create a permissive coordination planning policy."""
        return cls(
            minimum_confidence=0.3,
            deadlock_detection="passive",
            minimality_requirement="lenient",
        )