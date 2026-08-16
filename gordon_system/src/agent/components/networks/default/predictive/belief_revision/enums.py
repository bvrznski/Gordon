# Canonical Belief Revision Enums - Phase 4.9.5
# ===============================================
"""
Immutable enum definitions for BeliefRevision subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


# =============================================================================
# REVISION TYPE ENUM (EXPLICIT Kinds)
# =============================================================================

@dataclass(frozen=True, slots=True)
class RevisionKind:
    """
    Canonical revision kinds.
    
    Rules:
        - Each kind represents exactly one semantic operation
        - No implicit conversions between kinds
        - All kinds are explicitly enumerated
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("RevisionKind must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"RevisionKind({self.value})"


# Canonical revision kinds (immutable constants)
CREATE: Final[RevisionKind] = RevisionKind(value="CREATE")
UPDATE: Final[RevisionKind] = RevisionKind(value="UPDATE")
MERGE: Final[RevisionKind] = RevisionKind(value="MERGE")
SPLIT: Final[RevisionKind] = RevisionKind(value="SPLIT")
WEAKEN: Final[RevisionKind] = RevisionKind(value="WEAKEN")
STRENGTHEN: Final[RevisionKind] = RevisionKind(value="STRENGTHEN")
REMOVE: Final[RevisionKind] = RevisionKind(value="REMOVE")
DEFER: Final[RevisionKind] = RevisionKind(value="DEFER")
REJECT: Final[RevisionKind] = RevisionKind(value="REJECT")
UNKNOWN: Final[RevisionKind] = RevisionKind(value="UNKNOWN")


# =============================================================================
# CONTRADICTION KIND ENUM
# =============================================================================

@dataclass(frozen=True, slots=True)
class ContradictionKind:
    """
    Canonical contradiction categories.
    
    Rules:
        - Each kind represents exactly one semantic conflict type
        - All kinds are explicitly enumerated
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("ContradictionKind must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"ContradictionKind({self.value})"


# Canonical contradiction kinds
LOGICAL_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="logical")
SEMANTIC_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="semantic")
TEMPORAL_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="temporal")
HIERARCHICAL_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="hierarchical")
CAUSAL_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="causal")
SCHEMA_CONTRADICTION: Final[ContradictionKind] = ContradictionKind(value="schema")


# =============================================================================
# DEPENDENCY RELATIONSHIP TYPE ENUM
# =============================================================================

@dataclass(frozen=True, slots=True)
class DependencyRelationship:
    """
    Canonical dependency relationship types.
    
    Rules:
        - Each type represents exactly one semantic relationship
        - All types are explicitly enumerated
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("DependencyRelationship must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"DependencyRelationship({self.value})"


# Canonical dependency relationship types
SUPPORTS: Final[DependencyRelationship] = DependencyRelationship(value="supports")
DEPENDS_ON: Final[DependencyRelationship] = DependencyRelationship(value="depends_on")
CONTRADICTS: Final[DependencyRelationship] = DependencyRelationship(value="contradicts")
REFINES: Final[DependencyRelationship] = DependencyRelationship(value="refines")
GENERALIZES: Final[DependencyRelationship] = DependencyRelationship(value="generalizes")
SPECIALIZES: Final[DependencyRelationship] = DependencyRelationship(value="specializes")
EXPLAINS: Final[DependencyRelationship] = DependencyRelationship(value="explains")


# =============================================================================
# CONFLICT RESOLUTION STRATEGY ENUM
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConflictResolutionStrategy:
    """
    Canonical contradiction resolution strategies.
    
    Rules:
        - Each strategy represents exactly one policy outcome
        - Strategies are explicit and policy-driven
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("ConflictResolutionStrategy must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"ConflictResolutionStrategy({self.value})"


# Canonical resolution strategies
RETAIN_BOTH: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="retain_both")
REPLACE: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="replace")
MERGE_CONFLICTING: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="merge")
DEFER_RESOLUTION: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="defer")
REJECT_CONTRADICTION: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="reject")
MARK_UNRESOLVED: Final[ConflictResolutionStrategy] = ConflictResolutionStrategy(value="mark_unresolved")


# =============================================================================
# HIERARCHY LEVEL ENUM
# =============================================================================

@dataclass(frozen=True, slots=True)
class BeliefHierarchyLevel:
    """
    Canonical belief hierarchy levels.
    
    Rules:
        - Each level represents exactly one semantic abstraction tier
        - Levels are ordered: sensory < contextual < conceptual < abstract
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("BeliefHierarchyLevel must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"BeliefHierarchyLevel({self.value})"


# Canonical hierarchy levels
SENSORY: Final[BeliefHierarchyLevel] = BeliefHierarchyLevel(value="sensory")
CONTEXTUAL: Final[BeliefHierarchyLevel] = BeliefHierarchyLevel(value="contextual")
CONCEPTUAL: Final[BeliefHierarchyLevel] = BeliefHierarchyLevel(value="conceptual")
ABSTRACT: Final[BeliefHierarchyLevel] = BeliefHierarchyLevel(value="abstract")


# =============================================================================
# STATUS ENUMS
# =============================================================================

@dataclass(frozen=True, slots=True)
class RevisionStatus:
    """
    Canonical revision status values.
    
    Rules:
        - Each status represents exactly one state in the revision lifecycle
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("RevisionStatus must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"RevisionStatus({self.value})"


# Canonical statuses
PENDING: Final[RevisionStatus] = RevisionStatus(value="pending")
VALIDATED: Final[RevisionStatus] = RevisionStatus(value="validated")
EVALUATED: Final[RevisionStatus] = RevisionStatus(value="evaluated")
CONTRADICTION_ANALYZED: Final[RevisionStatus] = RevisionStatus(value="contradiction_analyzed")
CONSISTENCY_VALIDATED: Final[RevisionStatus] = RevisionStatus(value="consistency_validated")
PROPAGATION_COMPLETED: Final[RevisionStatus] = RevisionStatus(value="propagation_completed")
REVISION_GRAPH_CREATED: Final[RevisionStatus] = RevisionStatus(value="revision_graph_created")
BELIEF_STATE_CREATED: Final[RevisionStatus] = RevisionStatus(value="belief_state_created")
COMPLETED: Final[RevisionStatus] = RevisionStatus(value="completed")
FAILED: Final[RevisionStatus] = RevisionStatus(value="failed")


# =============================================================================
# TRACE EVENT ENUMS
# =============================================================================

@dataclass(frozen=True, slots=True)
class TraceEvent:
    """
    Canonical trace events for revision pipeline.
    
    Rules:
        - Each event represents exactly one stage in the revision process
        - Events are ordered and stable
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("TraceEvent must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"TraceEvent({self.value})"


# Canonical trace events
REQUEST_VALIDATED: Final[TraceEvent] = TraceEvent(value="request_validated")
BELIEF_STATE_VALIDATED: Final[TraceEvent] = TraceEvent(value="belief_state_validated")
PRECISION_VALIDATED: Final[TraceEvent] = TraceEvent(value="precision_validated")
CANDIDATES_GENERATED: Final[TraceEvent] = TraceEvent(value="candidates_generated")
EVIDENCE_EVALUATED: Final[TraceEvent] = TraceEvent(value="evidence_evaluated")
CONTRADICTIONS_ANALYZED: Final[TraceEvent] = TraceEvent(value="contradictions_analyzed")
CONSISTENCY_CHECKED: Final[TraceEvent] = TraceEvent(value="consistency_checked")
BELIEFS_UPDATED: Final[TraceEvent] = TraceEvent(value="beliefs_updated")
REVISION_GRAPH_CREATED: Final[TraceEvent] = TraceEvent(value="revision_graph_created")
STATE_VALIDATED: Final[TraceEvent] = TraceEvent(value="state_validated")


# =============================================================================
# FAILURE KIND ENUMS (for findings)
# =============================================================================

@dataclass(frozen=True, slots=True)
class FailureKind:
    """
    Canonical failure categories for revision.
    
    Rules:
        - Each kind represents exactly one failure mode
        - Failures are typed and explicit
    """
    value: str
    
    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("FailureKind must have a non-empty string value")
    
    def __str__(self) -> str:
        return f"FailureKind({self.value})"


# Canonical failure kinds
INVALID_BELIEF: Final[FailureKind] = FailureKind(value="invalid_belief")
INVALID_PRECISION: Final[FailureKind] = FailureKind(value="invalid_precision")
INVALID_POLICY: Final[FailureKind] = FailureKind(value="invalid_policy")
UNSUPPORTED_SCHEMA: Final[FailureKind] = FailureKind(value="unsupported_schema")
DEPENDENCY_CYCLE: Final[FailureKind] = FailureKind(value="dependency_cycle")
CONTRADICTION_UNRESOLVED: Final[FailureKind] = FailureKind(value="contradiction_unresolved")
UNKNOWN_FAILURE: Final[FailureKind] = FailureKind(value="unknown_failure")