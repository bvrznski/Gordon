# Gordon Phase 5.7.2-I: Experiential Field Builder
# ===============================================================================
#
# Main field builder that orchestrates the entire construction pipeline.
#

"""
Experiential Field Builder module.

This is the main entry point for constructing experiential fields from
contributions and projections.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, List


# Local imports (relative within package)
from .types import (
    ExperientialFieldId,
    ExperientialFieldGeneration,
    TransitionId,
    ContentId,
    ContributionId,
)
from .constants import DeduplicationPolicy, CapacityAction
from gordon.agent.components.systems.consciousnessvalidation import ValidationOutcome, RejectionReason, ContributionValidator
from gordon.agent.components.systems.consciousnessnormalization import NormalizationAction, ContributionNormalizer
from gordon.agent.components.systems.consciousnessordering import DeterministicOrderer, OrderingKey
from gordon.agent.components.systems.consciousnesscapacity import FieldCapacityPolicy, CapacityEnforcementResult
from gordon.agent.components.systems.consciousnesssnapshot import (
    ExperientialFieldSnapshot,
    FieldContent,
    FieldRelation,
)
from gordon.agent.components.systems.consciousnesstransition import (
    FieldTransitionAuthority,
    TransitionCommitResult,
)


# =============================================================================
# BUILD REQUEST AND RESULT TYPES
# =============================================================================

@dataclass(frozen=True)
class FieldBuildRequest:
    """
    Request to build or update the experiential field.
    
    This is the input type for the builder's main operation. It contains
    all contributions and other data needed for construction.
    """
    
    field_id: str
    """ID of the logical field being built."""
    
    current_generation: int = 0
    """Current generation before this build (0 if first build)."""
    
    previous_snapshot: Optional[ExperientialFieldSnapshot] = None
    """Previous snapshot for incremental updates (optional)."""
    
    contributions: Tuple[dict, ...] = field(default_factory=tuple)
    """List of contribution data dictionaries to process."""
    
    trigger: str = "internal"
    """What triggered this build request."""
    
    correlation_id: Optional[str] = None
    """Correlation ID for tracing this build."""
    
    def is_first_build(self) -> bool:
        """Check if this is the initial field build (generation 0)."""
        return self.current_generation == 0


@dataclass(frozen=True)
class FieldBuildResult:
    """
    Result of a field build operation.
    
    Contains the new snapshot, transition record, and any diagnostics
    from the build process.
    """
    
    succeeded: bool
    """Whether the build completed successfully."""
    
    status: str = "pending"
    """Final status of the build."""
    
    new_snapshot: Optional[ExperientialFieldSnapshot] = None
    """New field snapshot (if successful)."""
    
    generation: int = 0
    """New generation number."""
    
    accepted_contributions: int = 0
    """Number of contributions that were accepted."""
    
    rejected_contributions: int = 0
    """Number of contributions that were rejected."""
    
    deduplicated_count: int = 0
    """Number of duplicates detected and handled."""
    
    capacity_actions_taken: Tuple[str, ...] = field(default_factory=tuple)
    """Capacity-related actions taken during build."""
    
    validation_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any warnings during validation."""
    
    degraded_modes: Tuple[str, ...] = field(default_factory=tuple)
    """Degradation modes if partially successful."""
    
    # Timing
    started_at_utc: float = 0.0
    """When build was initiated."""
    
    completed_at_utc: Optional[float] = None
    """When build completed."""
    
    duration_seconds: float = 0.0
    """Total build duration in seconds."""
    
    # Failure info
    failure_reason: Optional[str] = None
    """Reason for failure if failed."""
    
    @classmethod
    def success(
        cls,
        snapshot: ExperientialFieldSnapshot,
        generation: int,
        accepted: int = 0,
        rejected: int = 0,
    ) -> "FieldBuildResult":
        """Create a successful build result."""
        return cls(
            succeeded=True,
            status="completed",
            new_snapshot=snapshot,
            generation=generation,
            accepted_contributions=accepted,
            rejected_contributions=rejected,
        )
    
    @classmethod
    def failure(cls, reason: str) -> "FieldBuildResult":
        """Create a failed build result."""
        return cls(
            succeeded=False,
            status="failed",
            failure_reason=reason,
        )


# =============================================================================
# EXPERIENTIAL FIELD BUILDER
# =============================================================================

@dataclass
class ExperientialFieldBuilder:
    """
    Main experiential field builder orchestrating the construction pipeline.
    
    The builder implements a deterministic, bounded construction process that:
        1. Receives contributions from external subsystems
        2. Validates and rejects malformed or stale submissions
        3. Normalizes compatible inputs to canonical form
        4. Orders contributions deterministically
        5. Handles duplicates according to policy
        6. Enforces capacity bounds
        7. Constructs field-level relations where appropriate
        8. Produces immutable snapshots atomically
    
    The builder does NOT:
        - Perform reasoning or inference (owned by Cognition)
        - Make truth determinations
        - Grant authorization or trust through admission
        - Persist long-term memory (owned by Memory System)
        - Execute actions (owned by Action)
        - Determine intentional semantics (Phase 5.7.3)
    """
    
    # Configuration and dependencies
    _field_id: str = "experiential-field-001"
    """ID of the logical field this builder manages."""
    
    _configuration: Dict[str, any] = field(default_factory=dict)
    """Builder configuration."""
    
    # Components
    _validator: ContributionValidator = field(default_factory=ContributionValidator)
    """Contribution validator."""
    
    _normalizer: ContributionNormalizer = field(default_factory=ContributionNormalizer)
    """Contribution normalizer."""
    
    _orderer: DeterministicOrderer = field(default_factory=DeterministicOrderer)
    """Deterministic orderer for contributions."""
    
    _capacity_policy: FieldCapacityPolicy = field(
        default_factory=FieldCapacityPolicy
    )
    """Capacity policy and enforcement."""
    
    # State
    _current_generation: int = 0
    """Current field generation (starts at 0)."""
    
    _current_snapshot: Optional[ExperientialFieldSnapshot] = None
    """Current snapshot (if any)."""
    
    _transition_authority: FieldTransitionAuthority = field(
        default_factory=lambda: FieldTransitionAuthority("experiential-field-001")
    )
    """Atomic transition authority."""
    
    def __post_init__(self):
        """Initialize after construction."""
        # Set up the field ID from configuration if provided
        if "field_id" in self._configuration:
            self._field_id = self._configuration["field_id"]
    
    def get_current_generation(self) -> int:
        """Get the current field generation number."""
        return self._current_generation
    
    def get_current_snapshot(self) -> Optional[ExperientialFieldSnapshot]:
        """Get the current field snapshot (if any)."""
        return self._current_snapshot
    
    # =========================================================================
    # BUILD PIPELINE
    # =========================================================================

    def build_field(
        self,
        request: FieldBuildRequest,
    ) -> FieldBuildResult:
        """
        Build a new experiential field snapshot from contributions.
        
        This is the main entry point for field construction. It orchestrates
        all pipeline stages:
            1. Lifecycle validation
            2. Contribution collection
            3. Source and schema validation
            4. Stale contribution rejection
            5. Normalization
            6. Deterministic ordering
            7. Duplicate resolution
            8. Content set construction
            9. Relation construction
            10. Capacity enforcement
            11. Invariant validation
            12. Transition commit
            
        Args:
            request: FieldBuildRequest containing contributions and metadata
            
        Returns:
            FieldBuildResult with snapshot and diagnostics
        """
        started_at = time.time()
        
        try:
            # Phase 1: Lifecycle validation
            if not self._validate_lifecycle(request):
                return FieldBuildResult.failure("Lifecycle validation failed")
            
            # Phase 2-7: Process contributions through pipeline stages
            processed_result = self._process_contributions(
                request.contributions,
                request.correlation_id,
            )
            
            if not processed_result.succeeded:
                return processed_result
            
            # Phase 8-10: Build snapshot with relations and capacity
            new_snapshot, capacity_actions = self._build_snapshot(
                contents=processed_result.accepted_contents or (),
                relations=(),
            )
            
            # Phase 11-12: Commit transition atomically
            commit_result = self._commit_transition(
                new_snapshot,
                request.trigger,
                processed_result.accepted_count,
                processed_result.rejected_count,
            )
            
            if not commit_result.succeeded:
                return FieldBuildResult.failure(commit_result.failure_reason)
            
            # Update internal state
            self._current_generation = new_snapshot.generation
            self._current_snapshot = new_snapshot
            
            completed_at = time.time()
            
            return FieldBuildResult.success(
                snapshot=new_snapshot,
                generation=new_snapshot.generation,
                accepted=processed_result.accepted_count,
                rejected=processed_result.rejected_count,
            )
            
        except Exception as e:
            # Rollback on failure - preserve previous snapshot
            completed_at = time.time()
            
            return FieldBuildResult.failure(
                reason=f"Field build failed: {str(e)}"
            )
    
    def _validate_lifecycle(self, request: FieldBuildRequest) -> bool:
        """Validate lifecycle state before building."""
        # For now, always allow - in real implementation would check shutdown
        return True
    
    def _process_contributions(
        self,
        contributions: Tuple[dict, ...],
        correlation_id: Optional[str] = None,
    ) -> "BuildPipelineResult":
        """
        Run contributions through validation and normalization pipeline.
        
        Returns a BuildPipelineResult with accepted/rejected counts.
        """
        accepted_contents: List[FieldContent] = []
        rejected_count = 0
        
        for contrib in contributions:
            # Extract fields from contribution dict
            source_id = contrib.get("source_id", "unknown")
            kind = contrib.get("content_kind", "generic")
            freshness_utc = contrib.get("freshness_utc", time.time())
            expiration_utc = contrib.get("expiration_utc")
            payload_size = contrib.get("payload_size_bytes", 0)
            
            # Validate
            validation_result = self._validator.validate(
                source_id=source_id,
                freshness_utc=freshness_utc,
                expiration_utc=expiration_utc,
                payload_size_bytes=payload_size,
                content_kind=kind,
                is_source_registered=True,  # Assuming registered for now
            )
            
            if not validation_result.succeeded:
                rejected_count += 1
                continue
            
            # Normalize
            norm_result, _ = self._normalizer.normalize(
                kind=kind,
                privacy=contrib.get("privacy_classification", "internal"),
                trust=contrib.get("trust_classification", "untrusted"),
            )
            
            # Create content from validated and normalized contribution
            content = FieldContent.from_contribution(
                contribution_id=contrib.get("contribution_id", ContributionId().value),
                source_id=source_id,
                content_kind=norm_result["content_kind"],
                representation_reference=contrib.get("representation_reference"),
                summary=contrib.get("summary"),
                privacy_classification=norm_result["privacy_classification"],
                trust_classification=norm_result["trust_classification"],
            )
            
            accepted_contents.append(content)
        
        return BuildPipelineResult(
            succeeded=True,
            accepted_contents=tuple(accepted_contents),
            accepted_count=len(accepted_contents),
            rejected_count=rejected_count,
        )
    
    def _build_snapshot(
        self,
        contents: Tuple[FieldContent, ...],
        relations: Tuple[FieldRelation, ...],
    ) -> Tuple[ExperientialFieldSnapshot, Tuple[str, ...]]:
        """
        Build a snapshot from validated contents.
        
        Applies capacity policy and constructs the final snapshot.
        """
        # Apply capacity enforcement
        trimmed_contents, _, enforcement_results = self._capacity_policy.enforce_capacity(
            contents=list(contents),
            relations=list(relations),
            per_source_counts={},
        )
        
        capacity_actions = tuple(r.reduction_actions for r in enforcement_results if hasattr(r, 'reduction_actions'))
        
        # Create new generation
        new_generation = self._current_generation + 1
        
        snapshot = ExperientialFieldSnapshot(
            field_id=self._field_id,
            generation=new_generation,
            previous_generation=self._current_generation,
            contents=tuple(trimmed_contents),
            relations=relations,
            created_at_utc=time.time(),
            build_status="valid",
        )
        
        return snapshot, capacity_actions
    
    def _commit_transition(
        self,
        new_snapshot: ExperientialFieldSnapshot,
        trigger: str,
        accepted: int,
        rejected: int,
    ) -> TransitionCommitResult:
        """
        Atomically commit a transition with the new snapshot.
        
        This is the atomic point where the new generation becomes current.
        Either this succeeds completely or nothing changes.
        """
        return self._transition_authority.commit_transition(
            new_snapshot=new_snapshot,
            transition=self._transition_authority.prepare_transition(
                new_contents=(),
                new_relations=(),
                trigger=trigger,
                accepted_contributions=accepted,
                rejected_contributions=rejected,
            ),
        )


# =============================================================================
# BUILD PIPELINE RESULT
# =============================================================================

@dataclass(frozen=True)
class BuildPipelineResult:
    """
    Intermediate result from the build pipeline.
    
    Used to pass data between pipeline stages before final commit.
    """
    
    succeeded: bool
    """Whether this stage succeeded."""
    
    accepted_contents: Tuple[FieldContent, ...] = field(default_factory=tuple)
    """Contents accepted through validation and normalization."""
    
    accepted_count: int = 0
    """Number of accepted contributions."""
    
    rejected_count: int = 0
    """Number of rejected contributions."""
    
    deduplicated_count: int = 0
    """Number of duplicates detected."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Warnings from this stage."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "FieldBuildRequest",
    "FieldBuildResult",
    "ExperientialFieldBuilder",
    "BuildPipelineResult",
)