# Perception Projection Result - Phase 5.2.4
# ==========================================

"""
Projection Result: The outcome of a projection request.

A valid projection either produces one immutable view or an explicit failure.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# PROJECTION STATUSES
# =============================================================================


class ProjectionStatus:
    """Possible statuses for projection results."""
    
    COMPLETE = "complete"
    PARTIAL = "partial"
    DEGRADED = "degraded"
    STALE = "stale"
    AMBIGUOUS = "ambiguous"
    CONFLICTED = "conflicted"
    RESTRICTED = "restricted"
    EMPTY = "empty"
    REJECTED = "rejected"
    FAILED = "failed"
    UNKNOWN = "unknown"


# =============================================================================
# SELECTION RECORDS
# =============================================================================


class SelectionStatus:
    """Status of artifact selection decisions."""
    
    INCLUDED = "included"
    EXCLUDED_BY_SCOPE = "excluded_by_scope"
    EXCLUDED_BY_AUTHORIZATION = "excluded_by_authorization"
    EXCLUDED_BY_POLICY = "excluded_by_policy"
    EXCLUDED_AS_STALE = "excluded_as_stale"
    EXCLUDED_AS_INCOMPATIBLE = "excluded_as_incompatible"
    EXCLUDED_AS_INVALID = "excluded_as_invalid"
    CONDITIONALLY_INCLUDED = "conditionally_included"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProjectionSelectionRecord:
    """
    Record of a selection decision for an artifact.
    
    Every candidate artifact shall receive an inspectable inclusion or exclusion
    record with its basis and any applied constraints.
    """
    
    record_identity: str
    
    # Request reference
    request_reference: str
    
    # Artifact being selected
    candidate_artifact: str  # Artifact ID
    
    # Decision
    selection_status: str  # From SelectionStatus enum
    selection_basis: str   # Why this artifact was included/excluded
    
    # Applied constraints (if excluded)
    applied_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    # Exclusion reason (if not included)
    excluded_reason: Optional[str] = None
    
    # Confidence/uncertainty at selection time
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    @classmethod
    def include(
        cls,
        request_ref: str,
        artifact_id: str,
        basis: str,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "ProjectionSelectionRecord":
        """Create a record for an included artifact."""
        return cls(
            record_identity=f"selection:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            candidate_artifact=artifact_id,
            selection_status=SelectionStatus.INCLUDED,
            selection_basis=basis,
            confidence=confidence,
            uncertainty=uncertainty,
        )
    
    @classmethod
    def exclude(
        cls,
        request_ref: str,
        artifact_id: str,
        reason: str,
        basis: str = "scope_match",
        excluded_reason: Optional[str] = None,
    ) -> "ProjectionSelectionRecord":
        """Create a record for an excluded artifact."""
        return cls(
            record_identity=f"selection:{uuid.uuid4().hex[:16]}",
            request_reference=request_ref,
            candidate_artifact=artifact_id,
            selection_status=SelectionStatus.EXCLUDED_BY_SCOPE,
            selection_basis=basis,
            excluded_reason=excluded_reason or reason,
            confidence=0.5,  # Lower confidence for excluded items
        )


# =============================================================================
# FILTER RECORDS
# =============================================================================


class FilterKind:
    """Kinds of filters that may be applied."""
    
    AUTHORIZATION = "authorization"
    PRIVACY = "privacy"
    SANDBOX = "sandbox"
    COMPATIBILITY = "compatibility"
    DETAIL_REDUCTION = "detail_reduction"
    PAYLOAD_OMISSION = "payload_omission"
    FRESHNESS = "freshness"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    UNCERTAINTY_THRESHOLD = "uncertainty_threshold"
    POLICY = "policy"
    CONSUMER_CONTRACT = "consumer_contract"


@dataclass(frozen=True)
class PerceptionProjectionFilterRecord:
    """
    Record of a filter applied to an artifact.
    
    Filtering shall never silently convert unknown information into absent
    information. Omissions must be disclosed where they affect interpretation.
    """
    
    filter_identity: str
    
    # Target artifact
    target_artifact: str  # Artifact ID
    
    # Target fields (which fields were filtered)
    target_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Filter details
    filter_kind: str  # From FilterKind enum
    filter_reason: str  # Why the filter was applied
    
    # Authority
    authority: Optional[str] = None  # Policy or authorization that mandated this
    
    # Replacement representation (if any)
    replacement_representation: Optional[str] = None
    
    # Semantic impact
    semantic_impact: str = "none"  # none, reduced_precision, missing_context
    
    # Confidence/uncertainty effects
    confidence_effect: float = 0.0  # Change in confidence
    uncertainty_effect: float = 0.0  # Change in uncertainty
    
    @classmethod
    def payload_mask(
        cls,
        artifact_id: str,
        field_name: str,
        reason: str,
        authority: Optional[str] = None,
    ) -> "PerceptionProjectionFilterRecord":
        """Create a record for a payload masking filter."""
        return cls(
            filter_identity=f"filter:{uuid.uuid4().hex[:16]}",
            target_artifact=artifact_id,
            target_fields=(field_name,),
            filter_kind=FilterKind.PRIVACY,
            filter_reason=reason,
            authority=authority,
            replacement_representation="content present but hidden",
            semantic_impact="reduced_precision",
            confidence_effect=0.0,
            uncertainty_effect=0.1,
        )
    
    @classmethod
    def confidence_threshold(
        cls,
        artifact_id: str,
        threshold: float,
    ) -> "PerceptionProjectionFilterRecord":
        """Create a record for a confidence threshold exclusion."""
        return cls(
            filter_identity=f"filter:{uuid.uuid4().hex[:16]}",
            target_artifact=artifact_id,
            filter_kind=FilterKind.CONFIDENCE_THRESHOLD,
            filter_reason=f"below_confidence_threshold_{threshold}",
            semantic_impact="missing_context",
            confidence_effect=-0.5,  # Lower confidence due to exclusion
        )


# =============================================================================
# LIMITATION RECORDS
# =============================================================================


class LimitationKind:
    """Kinds of limitations that may affect a projection."""
    
    FILTERED_CONTENT = "filtered_content"
    STALE_SOURCE = "stale_source"
    MISSING_MODALITY = "missing_modality"
    PARTIAL_INTEGRATION = "partial_integration"
    AMBIGUOUS_INTEGRATION = "ambiguous_integration"
    CONFLICTED_EVIDENCE = "conflicted_evidence"
    AUTHORIZATION_RESTRICTION = "authorization_restriction"
    SANDBOX_RESTRICTION = "sandbox_restriction"
    DETAIL_REDUCTION = "detail_reduction"
    SUMMARY_LOSS = "summary_loss"
    UNSUPPORTED_FIELD = "unsupported_field"
    UPDATE_GAP = "update_gap"


@dataclass(frozen=True)
class PerceptionProjectionLimitation:
    """
    A limitation affecting a projection.
    
 Every material Projection limitation shall become an explicit Limitation
 artifact.
    """
    
    limitation_identity: str
    
    # Limitation details
    limitation_kind: str  # From LimitationKind enum
    
    # Affected scope
    affected_scope: Tuple[str, ...] = field(default_factory=tuple)
    
    # Cause
    cause: str
    
    # Semantic impact
    semantic_impact: str = "none"
    
    # Confidence/uncertainty effects
    confidence_effect: float = 0.0
    uncertainty_effect: float = 0.0
    
    # Recoverability
    recoverable: bool = True
    
    @classmethod
    def modality_missing(
        cls,
        modality_id: str,
    ) -> "PerceptionProjectionLimitation":
        """Create a limitation for missing modality."""
        return cls(
            limitation_identity=f"limitation:{uuid.uuid4().hex[:16]}",
            limitation_kind=LimitationKind.MISSING_MODALITY,
            affected_scope=(modality_id,),
            cause="modality_unavailable",
            semantic_impact="missing_evidence",
            uncertainty_effect=0.2,
        )
    
    @classmethod
    def stale_source(
        cls,
        artifact_id: str,
    ) -> "PerceptionProjectionLimitation":
        """Create a limitation for stale source."""
        return cls(
            limitation_identity=f"limitation:{uuid.uuid4().hex[:16]}",
            limitation_kind=LimitationKind.STALE_SOURCE,
            affected_scope=(artifact_id,),
            cause="source_revision_outdated",
            semantic_impact="reduced_precision",
            uncertainty_effect=0.15,
        )
    
    @classmethod
    def authorization_restriction(
        cls,
        artifact_id: str,
        restricted_fields: Tuple[str, ...],
    ) -> "PerceptionProjectionLimitation":
        """Create a limitation for authorization restrictions."""
        return cls(
            limitation_identity=f"limitation:{uuid.uuid4().hex[:16]}",
            limitation_kind=LimitationKind.AUTHORIZATION_RESTRICTION,
            affected_scope=(artifact_id,) + restricted_fields,
            cause="authorization_policy",
            semantic_impact="reduced_precision",
            recoverable=False,  # Cannot be recovered without authorization
        )


# =============================================================================
# PROJECTION RESULT
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionResult:
    """
    Result of a projection request.
    
    A Projection shall either produce one valid immutable Projection or an explicit
    failure result. Partial Projections shall use explicit Partial status.
    """
    
    request_reference: str
    
    # The actual projection (one per kind)
    projection_identity: Optional[str] = None  # ID if successful
    projection_kind: Optional[str] = None      # Kind of projection
    
    # Selection results
    selected_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    excluded_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    # Applied filters (for transparency)
    applied_filters: Tuple[PerceptionProjectionFilterRecord, ...] = field(
        default_factory=tuple
    )
    
    # Selection records
    selection_records: Tuple[ProjectionSelectionRecord, ...] = field(
        default_factory=tuple
    )
    
    # Summary information
    summary_records: Tuple[str, ...] = field(default_factory=tuple)
    
    # Conflict/ambiguity/missing evidence visibility
    conflicts_visible: bool = True
    ambiguities_visible: bool = True
    missing_evidence_visible: bool = True
    
    # Quality metrics
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    # Limitations
    limitations: Tuple[PerceptionProjectionLimitation, ...] = field(
        default_factory=tuple
    )
    
    # Freshness and revision info
    freshness_state: str = "current"  # current, recent, stale, expired, gapped
    freshness_timestamp_utc: float = field(default_factory=_time.time)
    source_revision_reference: Optional[str] = None
    projection_revision: int = 1
    
    # Status
    status: str = ProjectionStatus.COMPLETE  # From ProjectionStatus enum
    
    # Diagnostics and provenance
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def success(
        cls,
        request_ref: str,
        projection_id: str,
        projection_kind: str,
        selected_artifacts: List[str],
        confidence: float = 1.0,
        uncertainty: float = 0.0,
        status: str = ProjectionStatus.COMPLETE,
    ) -> "PerceptionProjectionResult":
        """Create a successful result."""
        return cls(
            request_reference=request_ref,
            projection_identity=projection_id,
            projection_kind=projection_kind,
            selected_artifacts=tuple(selected_artifacts),
            confidence=confidence,
            uncertainty=uncertainty,
            status=status,
        )
    
    @classmethod
    def partial(
        cls,
        request_ref: str,
        projection_id: str,
        projection_kind: str,
        selected_artifacts: List[str],
        limitations: Optional[List[PerceptionProjectionLimitation]] = None,
        confidence: float = 0.75,
    ) -> "PerceptionProjectionResult":
        """Create a partial result."""
        limit_list = list(limitations) if limitations else []
        return cls(
            request_reference=request_ref,
            projection_identity=projection_id,
            projection_kind=projection_kind,
            selected_artifacts=tuple(selected_artifacts),
            status=ProjectionStatus.PARTIAL,
            confidence=confidence,
            uncertainty=0.25,
            limitations=tuple(limit_list),
        )
    
    @classmethod
    def empty(
        cls,
        request_ref: str,
        reason: str = "no_matching_evidence",
    ) -> "PerceptionProjectionResult":
        """Create an empty result."""
        return cls(
            request_reference=request_ref,
            status=ProjectionStatus.EMPTY,
            confidence=0.5,  # No evidence means low confidence
            uncertainty=0.5,
            diagnostics=(f"Empty projection: {reason}",),
        )
    
    @classmethod
    def rejected(
        cls,
        request_ref: str,
        rejection_reason: str,
    ) -> "PerceptionProjectionResult":
        """Create a rejected result."""
        return cls(
            request_reference=request_ref,
            status=ProjectionStatus.REJECTED,
            confidence=0.0,
            uncertainty=1.0,
            diagnostics=(f"Rejection reason: {rejection_reason}",),
        )
    
    @classmethod
    def failed(
        cls,
        request_ref: str,
        failure_message: str,
    ) -> "PerceptionProjectionResult":
        """Create a failed result."""
        return cls(
            request_reference=request_ref,
            status=ProjectionStatus.FAILED,
            confidence=0.0,
            uncertainty=1.0,
            diagnostics=(f"Failure: {failure_message}",),
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if the result is complete (not partial/empty/rejected/failed)."""
        return self.status in (ProjectionStatus.COMPLETE,)


__all__ = [
    "ProjectionStatus",
    "SelectionStatus",
    "ProjectionSelectionRecord",
    "FilterKind",
    "PerceptionProjectionFilterRecord",
    "LimitationKind",
    "PerceptionProjectionLimitation",
    "PerceptionProjectionResult",
]