# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Incremental Coordination Models
===============================

Canonical immutable models for incremental coordination, deltas,
and convergence.

INCREMENTAL COORDINATION OVERVIEW
---------------------------------
Incremental coordination allows reusing previous CoordinationState when
only some projections have changed. This preserves the base state while
producing new revisions for updated components.

DELTA INVARIANTS:
- Delta is immutable and describes semantic changes only
- Base state remains unchanged during incremental update
- Full and incremental rebuilds must be semantically equivalent

CONVERGENCE INVARIANTS:
- Convergence is semantic, not runtime-iteration based
- Convergence does not require cognitive conflicts to resolve
- Blocked convergence preserves blocking causes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# =============================================================================
# CONVERGENCE STATUS
# =============================================================================

class CoordinationConvergenceStatus(Enum):
    """
    Canonical convergence statuses.
    
    CONVERGENCE-LAW-010: Blocked convergence shall preserve blocking causes
    
    STATUSES:
    - NOT_EVALUATED: Convergence not yet evaluated
    - CHANGING: State is still changing
    - STABLE: State has stabilized
    - STABLE_WITH_LIMITATIONS: Stable but with known limitations
    - BLOCKED: Blocked by unresolved constraints
    - FAILED: Convergence evaluation failed
    """
    NOT_EVALUATED = "not_evaluated"
    """Convergence not yet evaluated."""
    
    CHANGING = "changing"
    """State is still changing."""
    
    STABLE = "stable"
    """State has stabilized."""
    
    STABLE_WITH_LIMITATIONS = "stable_with_limitations"
    """Stable but with known limitations."""
    
    BLOCKED = "blocked"
    """Blocked by unresolved constraints."""
    
    FAILED = "failed"
    """Convergence evaluation failed."""
    
    UNKNOWN = "unknown"
    """Convergence status unknown."""


# =============================================================================
# COORDINATION DELTA MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationDelta:
    """
    Immutable delta model for coordination.
    
    DELTA-LAW-001: Exactly one Coordination Delta shall describe the transition
    from one base state to one candidate state
    
    DELTA-LAW-002: Coordination Delta shall remain immutable
    
    COORD-DELTA-INV-001: Delta is immutable (deeply frozen)
    COORD-DELTA-INV-002: Delta has no runtime references
    """
    delta_identity: str = ""
    """Unique identifier for this delta."""
    
    base_state_ref: Optional[str] = None
    """Reference to the base CoordinationState."""
    
    changed_projection_refs: tuple[str, ...] = ()
    """References to projections that changed."""
    
    added_projection_refs: tuple[str, ...] = ()
    """References to newly added projections."""
    
    removed_projection_refs: tuple[str, ...] = ()
    """References to removed projections."""
    
    reused_projection_refs: tuple[str, ...] = ()
    """References to reused (unchanged) projections."""
    
    invalidated_graph_regions: tuple[str, ...] = ()
    """Graph regions that were invalidated."""
    
    changed_requirements: tuple[str, ...] = ()
    """Requirements that changed."""
    
    changed_constraints: tuple[str, ...] = ()
    """Constraints that changed."""
    
    changed_dependencies: tuple[str, ...] = ()
    """Dependencies that changed."""
    
    changed_transitions: tuple[str, ...] = ()
    """Transitions that changed."""
    
    findings: tuple[str, ...] = ()
    """Findings from delta analysis."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this delta."""
    
    provenance_ref: Optional[str] = None
    """Reference to delta provenance record."""
    
    @classmethod
    def compute_delta(
        cls,
        base_state_ref: str,
        current_projections: tuple[str, ...],
        previous_projections: tuple[str, ...],
    ) -> CoordinationDelta:
        """
        Compute the delta between two states.
        
        Args:
            base_state_ref: Reference to base CoordinationState
            current_projections: Current projection references
            previous_projections: Previous projection references
            
        Returns:
            A new CoordinationDelta instance
        """
        current_set = set(current_projections)
        previous_set = set(previous_projections)
        
        added = tuple(p for p in current_set - previous_set)
        removed = tuple(p for p in previous_set - current_set)
        common = current_set & previous_set
        
        # In a real implementation, this would compare projection content
        changed = tuple(common)  # Would be filtered by actual change detection
        
        return cls(
            delta_identity=f"delta:{base_state_ref}",
            base_state_ref=base_state_ref,
            added_projection_refs=added,
            removed_projection_refs=removed,
            reused_projection_refs=tuple(p for p in common if p not in changed),
            changed_projection_refs=changed,
        )
    
    def merge(
        self,
        other_delta: CoordinationDelta,
    ) -> CoordinationDelta:
        """
        Merge another delta into this one.
        
        Args:
            other_delta: Delta to merge
            
        Returns:
            A new merged CoordinationDelta instance
        """
        return CoordinationDelta(
            delta_identity=f"merged:{self.delta_identity}",
            base_state_ref=self.base_state_ref,
            changed_projection_refs=tuple(set(self.changed_projection_refs) | set(other_delta.changed_projection_refs)),
            added_projection_refs=tuple(set(self.added_projection_refs) | set(other_delta.added_projection_refs)),
            removed_projection_refs=tuple(set(self.removed_projection_refs) | set(other_delta.removed_projection_refs)),
            reused_projection_refs=tuple(set(self.reused_projection_refs) & set(other_delta.reused_projection_refs)),
            invalidated_graph_regions=tuple(set(self.invalidated_graph_regions) | set(other_delta.invalidated_graph_regions)),
            changed_requirements=tuple(set(self.changed_requirements) | set(other_delta.changed_requirements)),
            changed_constraints=tuple(set(self.changed_constraints) | set(other_delta.changed_constraints)),
            changed_dependencies=tuple(set(self.changed_dependencies) | set(other_delta.changed_dependencies)),
            changed_transitions=tuple(set(self.changed_transitions) | set(other_delta.changed_transitions)),
            findings=self.findings + other_delta.findings,
            limitations=self.limitations + other_delta.limitations,
            provenance_ref=self.provenance_ref,
        )


# =============================================================================
# SEMANTIC FINGERPRINT MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticFingerprint:
    """
    Immutable semantic fingerprint model.
    
    FINGERPRINT-LAW-001: Semantic fingerprints shall be deterministic
    
    FINGERPRINT-LAW-002: Fingerprints shall derive from canonical semantic serialization
    
    COORD-FINGERPRINT-INV-001: Fingerprint is immutable (deeply frozen)
    COORD-FINGERPRINT-INV-002: Fingerprint has no runtime references
    """
    fingerprint_id: str = ""
    """Unique identifier for this fingerprint."""
    
    schema_version: str = "1.0.0"
    """Version of fingerprint schema."""
    
    algorithm: str = "canonical_hash"
    """Algorithm used to compute the fingerprint."""
    
    content_hash: str = ""
    """Canonical hash of content."""
    
    metadata: dict[str, str] = field(default_factory=dict)
    """Additional metadata for fingerprint."""
    
    @classmethod
    def from_content(
        cls,
        content_ref: str,
        content_data: str,
    ) -> SemanticFingerprint:
        """
        Create a fingerprint from content.
        
        Args:
            content_ref: Reference to the content
            content_data: Canonical serialized content
            
        Returns:
            A new SemanticFingerprint instance
        """
        # In implementation, this would compute hash from canonical serialization
        import hashlib
        content_hash = hashlib.sha256(content_data.encode()).hexdigest()[:16]
        
        return cls(
            fingerprint_id=f"fingerprint:{content_ref}",
            schema_version="1.0.0",
            algorithm="sha256_canonical",
            content_hash=content_hash,
            metadata={"ref": content_ref},
        )
    
    @classmethod
    def compare(cls, fp1: SemanticFingerprint, fp2: SemanticFingerprint) -> tuple[bool, Optional[str]]:
        """
        Compare two fingerprints for equality.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Tuple of (are_equal, difference_reason_if_not)
        """
        if fp1.schema_version != fp2.schema_version:
            return False, f"schema_version mismatch: {fp1.schema_version} vs {fp2.schema_version}"
        
        if fp1.algorithm != fp2.algorithm:
            return False, f"algorithm mismatch: {fp1.algorithm} vs {fp2.algorithm}"
        
        if fp1.content_hash != fp2.content_hash:
            return False, "content_hash mismatch"
        
        return True, None


# =============================================================================
# COORDINATION CHANGE DETECTOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationChangeDetector:
    """
    Immutable detector for coordination changes.
    
    CHANGE-DETECTOR-INV-001: Detector is deterministic
    
    Inputs:
    - Previous CoordinationState
    - Candidate projection set
    - Current membership revision
    - Current policy revision
    - Current semantic context revision
    
    Output: CoordinationDelta
    """
    
    @classmethod
    def detect_changes(
        cls,
        previous_state_ref: str,
        current_projections: tuple[str, ...],
        current_membership_rev: int,
        current_policy_rev: int,
        current_context_rev: int,
    ) -> CoordinationDelta:
        """
        Detect changes from a previous state.
        
        Args:
            previous_state_ref: Reference to previous CoordinationState
            current_projections: Current projection references
            current_membership_rev: Current membership revision
            current_policy_rev: Current policy revision
            current_context_rev: Current semantic context revision
            
        Returns:
            A new CoordinationDelta describing the changes
        """
        # In a real implementation, this would compare actual content
        return CoordinationDelta(
            delta_identity=f"delta:{previous_state_ref}",
            base_state_ref=previous_state_ref,
            added_projection_refs=current_projections[:1] if current_projections else (),
            changed_projection_refs=tuple(current_projections[1:]) if len(current_projections) > 1 else (),
        )


# =============================================================================
# COORDINATION CONVERGENCE MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationConvergence:
    """
    Immutable convergence model for coordination.
    
    CONVERGENCE-LAW-001: Coordination convergence shall be semantic
    
    CONVERGENCE-LAW-008: Convergence evaluation shall remain deterministic
    
    COORD-CONVERGENCE-INV-001: Convergence is immutable (deeply frozen)
    COORD-CONVERGENCE-INV-002: Convergence has no runtime references
    """
    convergence_identity: str = ""
    """Unique identifier for this convergence assessment."""
    
    cycle_ref: Optional[str] = None
    """Reference to the coordination cycle."""
    
    projection_set_stable: bool = False
    """Whether the projection set has stabilized."""
    
    graph_topology_stable: bool = False
    """Whether the graph topology has stabilized."""
    
    compatibility_stable: bool = False
    """Whether compatibility classification is stable."""
    
    barrier_terminal: bool = False
    """Whether the synchronization barrier reached a terminal state."""
    
    convergence_status: str = "not_evaluated"
    """Convergence status (from CoordinationConvergenceStatus)."""
    
    unresolved_conflicts: tuple[str, ...] = ()
    """Conflicts that remain unresolved (allowed in converged state)."""
    
    blocking_conditions: tuple[str, ...] = ()
    """Conditions preventing convergence."""
    
    confidence: float = 0.5
    """Confidence in convergence assessment."""
    
    uncertainty: float = 0.5
    """Uncertainty about convergence assessment."""
    
    provenance_ref: Optional[str] = None
    """Reference to convergence provenance record."""
    
    @classmethod
    def stable(
        cls,
        cycle_ref: str,
        unresolved_conflicts: tuple[str, ...] = (),
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> CoordinationConvergence:
        """
        Create a convergence assessment for a stable state.
        
        Args:
            cycle_ref: Reference to coordination cycle
            unresolved_conflicts: Conflicts that remain unresolved
            confidence: Confidence in convergence
            uncertainty: Uncertainty about convergence
            
        Returns:
            A new CoordinationConvergence instance with 'stable' status
        """
        return cls(
            convergence_identity=f"convergence:{cycle_ref}",
            cycle_ref=cycle_ref,
            projection_set_stable=True,
            graph_topology_stable=True,
            compatibility_stable=True,
            barrier_terminal=True,
            convergence_status="stable",
            unresolved_conflicts=unresolved_conflicts,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def blocked(
        cls,
        cycle_ref: str,
        blocking_conditions: tuple[str, ...],
    ) -> CoordinationConvergence:
        """
        Create a convergence assessment for a blocked state.
        
        Args:
            cycle_ref: Reference to coordination cycle
            blocking_conditions: Conditions that are blocking
            
        Returns:
            A new CoordinationConvergence instance with 'blocked' status
        """
        return cls(
            convergence_identity=f"convergence:{cycle_ref}",
            cycle_ref=cycle_ref,
            projection_set_stable=False,
            graph_topology_stable=False,
            compatibility_stable=False,
            barrier_terminal=False,
            convergence_status="blocked",
            blocking_conditions=blocking_conditions,
        )


# =============================================================================
# CONVERGENCE EVALUATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class CoordinationConvergenceEvaluator:
    """
    Immutable evaluator for coordination convergence.
    
    CONVERGENCE-EVAL-INV-001: Evaluator is deterministic
    
    Inputs:
    - Current cycle components
    - Prior cycle reference
    - Current Coordination Delta
    - Barrier status
    - Graph revisions
    - Compatibility assessment
    - Policy
    
    Output: CoordinationConvergence
    """
    
    @classmethod
    def evaluate_convergence(
        cls,
        cycle_ref: str,
        barrier_status: str,
        compatibility_status: str,
        graph_stable: bool = True,
    ) -> CoordinationConvergence:
        """
        Evaluate convergence for a coordination cycle.
        
        Args:
            cycle_ref: Reference to the coordination cycle
            barrier_status: Current barrier status
            compatibility_status: Compatibility assessment status
            graph_stable: Whether graphs are stable
            
        Returns:
            A new CoordinationConvergence instance with evaluated status
        """
        # Check if barrier is in terminal state
        terminal_statuses = {"open", "open_with_limitations", "failed"}
        barrier_is_terminal = barrier_status in terminal_statuses
        
        convergence_status = (
            "stable"
            if barrier_is_terminal and graph_stable
            else "not_evaluated"
        )
        
        return CoordinationConvergence(
            convergence_identity=f"convergence:eval:{cycle_ref}",
            cycle_ref=cycle_ref,
            projection_set_stable=True,
            graph_topology_stable=graph_stable,
            compatibility_stable=compatibility_status in ("compatible", "consistent_with_limitations"),
            barrier_terminal=barrier_is_terminal,
            convergence_status=convergence_status,
        )


# =============================================================================
# INCREMENTAL INVALIDATION MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class IncrementalInvalidation:
    """
    Immutable invalidation model for incremental coordination.
    
    INVALIDATION-LAW-001: Invalidation shall follow explicit dependency relations
    
    INVALIDATION-LAW-006: Invalidation shall remain deterministic
    
    COORD-INVALIDATION-INV-001: Invalidation is immutable (deeply frozen)
    COORD-INVALIDATION-INV-002: Invalidation has no runtime references
    """
    invalidation_identity: str = ""
    """Unique identifier for this invalidation."""
    
    cause_ref: Optional[str] = None
    """Reference to the cause of invalidation."""
    
    affected_regions: tuple[str, ...] = ()
    """Graph regions that are invalidated."""
    
    preserved_regions: tuple[str, ...] = ()
    """Graph regions that remain valid."""
    
    invalidated_graphs: tuple[str, ...] = ()
    """Specific graph instances invalidated."""
    
    @classmethod
    def invalidate_region(
        cls,
        cause_ref: str,
        affected_region_refs: tuple[str, ...],
    ) -> IncrementalInvalidation:
        """
        Create an invalidation for a specific region.
        
        Args:
            cause_ref: Reference to the cause of invalidation
            affected_region_refs: References to affected graph regions
            
        Returns:
            A new IncrementalInvalidation instance
        """
        return cls(
            invalidation_identity=f"invalidate:{cause_ref}",
            cause_ref=cause_ref,
            affected_regions=affected_region_refs,
            preserved_regions=(),
            invalidated_graphs=tuple(affected_region_refs),
        )
    
    @classmethod
    def preserve_region(
        cls,
        preserved_region_refs: tuple[str, ...],
    ) -> IncrementalInvalidation:
        """
        Create an invalidation that preserves specific regions.
        
        Args:
            preserved_region_refs: References to preserved graph regions
            
        Returns:
            A new IncrementalInvalidation instance
        """
        return cls(
            invalidation_identity=f"invalidate:preserve",
            cause_ref=None,
            affected_regions=(),
            preserved_regions=preserved_region_refs,
            invalidated_graphs=(),
        )


# =============================================================================
# INCREMENTAL GRAPH REBUILDER
# =============================================================================

@dataclass(frozen=True, slots=True)
class IncrementalGraphRebuilder:
    """
    Immutable rebuilder for incremental graph construction.
    
    GRAPH-REBUILD-LAW-001: Every rebuilt graph shall be a new immutable revision
    
    GRAPH-REBUILD-LAW-004: Incremental graph rebuild shall be semantically
    equivalent to full rebuild
    
    COORD-REBUILD-INV-001: Rebuilder is deterministic
    
    Inputs:
    - Previous graph revision
    - Coordination Delta
    - Current projection set
    
    Output: New immutable graph revision
    """
    
    @classmethod
    def rebuild_graph(
        cls,
        previous_graph_ref: str,
        delta: CoordinationDelta,
        current_projections: tuple[str, ...],
    ) -> IncrementalInvalidation:
        """
        Rebuild a graph incrementally.
        
        Args:
            previous_graph_ref: Reference to previous graph revision
            delta: CoordinationDelta describing changes
            current_projections: Current projection references
            
        Returns:
            A new IncrementalInvalidation describing the rebuild
        """
        # In a real implementation, this would rebuild graphs based on delta
        
        affected = []
        if delta.changed_projection_refs:
            affected.append("dependency_graph")
        if delta.changed_constraints:
            affected.append("constraint_graph")
        
        return IncrementalInvalidation(
            invalidation_identity=f"rebuild:{previous_graph_ref}",
            cause_ref=str(delta),
            affected_regions=tuple(affected),
            preserved_regions=("unchanged_projection_graphs",) if current_projections else (),
            invalidated_graphs=tuple(affected),
        )