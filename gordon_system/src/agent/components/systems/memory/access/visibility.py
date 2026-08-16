# Memory Visibility - Phase 5.1.3 Canonical Filter Control
# =========================================================

"""
Memory Visibility: Controls which artifacts are visible in a projection.

Visibility determines:
    - Which artifacts appear in results
    - What metadata is exposed
    - Which constraints apply to viewing

Visibility Laws:
    VISIBILITY-LAW-001: Visibility determines publication only
    VISIBILITY-LAW-002: Never alter semantic content
    VISIBILITY-LAW-003: Invisible artifacts remain valid memory
    VISIBILITY-LAW-004: Policies remain explicit
    VISIBILITY-LAW-005: Preserve provenance
    VISIBILITY-LAW-006: Filters are inspectable
    VISIBILITY-LAW-007: Side-effect free evaluation
    VISIBILITY-LAW-008: Deterministic behavior
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# FILTER KINDS - What kind of filter?
# =============================================================================


class VisibilityFilterKind(Enum):
    """
    Types of visibility filters.
    
    | Kind          | Description                                |
    |---------------|-------------------------------------------|
    | INCLUDE       | Only include matching artifacts           |
    | EXCLUDE       | Exclude matching artifacts                |
    | REQUIRE       | Require certain properties                |
    | HIDE_IF       | Hide if condition is met                  |
    """
    
    INCLUDE = "include"
    EXCLUDE = "exclude"
    REQUIRE = "require"
    HIDE_IF = "hide_if"


# =============================================================================
# VISIBILITY FILTER - A single visibility rule
# =============================================================================


@dataclass(frozen=True)
class VisibilityFilter:
    """
    Single visibility filter.
    
    Fields:
        filter_id:       Unique identifier
        
        # Match criteria
        artifact_kinds:  Which kinds to match (empty = all)
        confidence_min:  Minimum confidence threshold
        validity_states: Validity states to include/exclude
        
        # Metadata filters
        tag_match:       Required tags (or, if excluded, forbidden tags)
        
        # Time-based
        after_utc:       Only artifacts after this time
        before_utc:      Only artifacts before this time
        
        # Action
        kind:            Include, exclude, require, hide_if
        enabled:         Is this filter active?
    """
    
    filter_id: str
    
    artifact_kinds: Tuple[str, ...] = field(default_factory=tuple)
    confidence_min: float = 0.0
    validity_states: Tuple[str, ...] = field(default_factory=tuple)
    
    tag_match: Optional[str] = None
    
    after_utc: Optional[float] = None
    before_utc: Optional[float] = None
    
    kind: VisibilityFilterKind = VisibilityFilterKind.INCLUDE
    enabled: bool = True


# =============================================================================
# VISIBILITY POLICY - Collection of filters
# =============================================================================


@dataclass(frozen=True)
class VisibilityPolicy:
    """
    Policy containing visibility filters.
    
    Fields:
        policy_id:       Unique identifier
        
        name:           Human-readable name
        description:    What does this policy do?
        
        # Filters
        include_filters: Filters to apply first
        exclude_filters: Filters that hide artifacts
        
        # Behavior
        default_visible: Default if no filter matches (true = visible)
        
        # Metadata
        version:        Policy version
        created_at_utc: When was it created?
    """
    
    policy_id: str
    
    name: str
    description: Optional[str] = None
    
    include_filters: Tuple[VisibilityFilter, ...] = field(default_factory=tuple)
    exclude_filters: Tuple[VisibilityFilter, ...] = field(default_factory=tuple)
    
    default_visible: bool = True  # Visible by default unless filtered out
    
    version: int = 1
    created_at_utc: float = field(default_factory=time.time)


# =============================================================================
# VISIBILITY RESULT - Filter evaluation outcome
# =============================================================================


@dataclass(frozen=True)
class VisibilityResult:
    """
    Result of visibility filtering for an artifact.
    
    Fields:
        result_id:       Unique identifier
        
        visible:        Is the artifact visible?
        filter_matched: Which filter caused this (if any)?
        
        # Filtered attributes
        hidden_attributes: Tuple[str, ...]  # Which attrs were hidden?
        
        # Evidence
        evaluation_time_ms: float         # Filtering took how long?
        notes: Optional[str]              # Explanation
    """
    
    result_id: str
    
    visible: bool = True
    filter_matched: Optional[str] = None
    
    hidden_attributes: Tuple[str, ...] = field(default_factory=tuple)
    
    evaluation_time_ms: float = 0.0
    notes: Optional[str] = None


# =============================================================================
# VISIBILITY ENGINE - Core filtering engine
# =============================================================================


class MemoryVisibilityEngine:
    """
    Core visibility filter engine for memory access.
    
    Processes artifacts through filters to determine visibility.
    
    The engine is side-effect free - it never modifies artifacts,
    only evaluates their visibility.
    """
    
    def __init__(self):
        self._policies: Dict[str, VisibilityPolicy] = {}
        self._filters: Dict[str, VisibilityFilter] = {}
        self._evaluation_count: int = 0
    
    @property
    def policy_count(self) -> int:
        """Count of registered policies."""
        return len(self._policies)
    
    @property
    def evaluation_count(self) -> int:
        """Total filtering operations performed."""
        return self._evaluation_count
    
    def register_policy(self, policy: VisibilityPolicy) -> None:
        """
        Register a new visibility policy.
        
        Args:
            policy: Policy to add
        """
        self._policies[policy.policy_id] = policy
        for f in policy.include_filters + policy.exclude_filters:
            if f.enabled:
                self._filters[f.filter_id] = f
    
    def register_filter(self, filter_: VisibilityFilter) -> None:
        """Register a standalone visibility filter."""
        self._filters[filter_.filter_id] = filter_
    
    def evaluate_artifact(
        self,
        artifact: Any,
        policy_id: Optional[str] = None,
    ) -> VisibilityResult:
        """
        Evaluate visibility for a single artifact.
        
        Args:
            artifact: MemoryArtifact to check
            policy_id: Which policy to use (None = all active)
            
        Returns:
            VisibilityResult with visible/deny decision
            
        The evaluation is deterministic - same artifact always gets same result.
        """
        start_time = time.time()
        
        # Build artifact context
        ctx = self._build_artifact_context(artifact)
        
        # Find applicable policies
        applicable_policies = self._get_applicable_policies(policy_id, ctx)
        
        # Check exclude filters first (most restrictive)
        for policy in applicable_policies:
            for f in policy.exclude_filters:
                if not f.enabled:
                    continue
                
                if self._filter_matches(f, ctx):
                    evaluation_time_ms = (time.time() - start_time) * 1000
                    return VisibilityResult(
                        result_id=str(time.time_ns()),
                        visible=False,
                        filter_matched=f.filter_id,
                        notes=f"Artifact excluded by filter: {f.filter_id}",
                        evaluation_time_ms=evaluation_time_ms,
                    )
        
        # Check include filters (if any policy has them)
        if applicable_policies:
            has_includes = any(
                len(p.include_filters) > 0
                for p in applicable_policies
            )
            
            if has_includes:
                # Must match at least one include filter
                matched_include = False
                
                for policy in applicable_policies:
                    for f in policy.include_filters:
                        if not f.enabled:
                            continue
                        
                        if self._filter_matches(f, ctx):
                            matched_include = True
                            break
                    
                    if matched_include:
                        break
                
                if not matched_include:
                    evaluation_time_ms = (time.time() - start_time) * 1000
                    return VisibilityResult(
                        result_id=str(time.time_ns()),
                        visible=False,
                        filter_matched="include:none",
                        notes="Artifact did not match any include filters",
                        evaluation_time_ms=evaluation_time_ms,
                    )
        
        # Artifact is visible (or policy has default_visible=True)
        evaluation_time_ms = (time.time() - start_time) * 1000
        self._evaluation_count += 1
        
        return VisibilityResult(
            result_id=str(time.time_ns()),
            visible=True,
            filter_matched=None,
            notes="Artifact passed visibility filters",
            evaluation_time_ms=evaluation_time_ms,
        )
    
    def evaluate_projection(
        self,
        artifacts: Tuple[Any, ...],
        policy_id: Optional[str] = None,
    ) -> Tuple[Tuple[Any, ...], Tuple[VisibilityResult, ...]]:
        """
        Evaluate visibility for a collection of artifacts.
        
        Args:
            artifacts: Artifacts to check
            policy_id: Which policy to use
            
        Returns:
            (visible_artifacts, results) tuple
        """
        visible: List[Any] = []
        results: List[VisibilityResult] = []
        
        for artifact in artifacts:
            result = self.evaluate_artifact(artifact, policy_id)
            
            if result.visible:
                visible.append(artifact)
            
            results.append(result)
        
        return tuple(visible), tuple(results)
    
    def _build_artifact_context(self, artifact: Any) -> Dict[str, Any]:
        """Build context for filtering from an artifact."""
        return {
            "artifact_id": getattr(artifact, "artifact_id", ""),
            "artifact_kind": str(getattr(artifact, "artifact_kind", "unknown")),
            "semantic_content": dict(getattr(artifact, "semantic_content", {})),
            "confidence": float(getattr(artifact, "confidence", {}).get("confidence", 1.0)),
            "validity": getattr(artifact, "validity", {}).get("status", "unknown"),
            "tags": tuple(getattr(artifact, "tags", ())),
            "created_at_utc": getattr(artifact, "created_at_utc", 0.0),
        }
    
    def _get_applicable_policies(
        self,
        policy_id: Optional[str],
        context: Dict[str, Any],
    ) -> Tuple[VisibilityPolicy, ...]:
        """Get policies applicable to this evaluation."""
        if policy_id:
            policy = self._policies.get(policy_id)
            if policy and policy.enabled:
                return (policy,)
            return ()
        
        # Return all enabled policies
        return tuple(
            p for p in self._policies.values()
            if p.enabled
        )
    
    def _filter_matches(self, filter_: VisibilityFilter, ctx: Dict[str, Any]) -> bool:
        """Check if a visibility filter matches the context."""
        if not filter_.enabled:
            return False
        
        # Check artifact kinds
        if filter_.artifact_kinds:
            kind = ctx.get("artifact_kind", "")
            if kind not in filter_.artifact_kinds:
                return False
        
        # Check confidence threshold
        if filter_.confidence_min > 0.0:
            confidence = ctx.get("confidence", 1.0)
            if confidence < filter_.confidence_min:
                return False
        
        # Check validity states
        if filter_.validity_states:
            validity = ctx.get("validity", "")
            if validity not in filter_.validity_states:
                return False
        
        # Check time range
        created_at = ctx.get("created_at_utc", 0.0)
        
        if filter_.after_utc is not None:
            if created_at <= filter_.after_utc:
                return False
        
        if filter_.before_utc is not None:
            if created_at >= filter_.before_utc:
                return False
        
        # Check tag match
        if filter_.tag_match is not None:
            tags = ctx.get("tags", ())
            if filter_.tag_match not in tags:
                return False
        
        return True
    
    def get_filtered_artifacts(
        self,
        artifacts: Tuple[Any, ...],
        policy_id: Optional[str] = None,
        visible_only: bool = True,
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        """
        Get artifacts with visibility applied.
        
        Args:
            artifacts: Artifacts to filter
            policy_id: Policy to use
            visible_only: If True, return only visible artifacts
            
        Returns:
            (filtered_artifacts, metadata) tuple
        """
        if visible_only:
            visible, results = self.evaluate_projection(artifacts, policy_id)
            
            metadata = {
                "total_count": len(artifacts),
                "visible_count": len(visible),
                "filtered_count": len(artifacts) - len(visible),
                "filtering_time_ms": sum(r.evaluation_time_ms for r in results),
            }
            
            return visible, metadata
        
        # Return all artifacts with visibility info
        return artifacts, {
            "total_count": len(artifacts),
            "visible_only": False,
        }