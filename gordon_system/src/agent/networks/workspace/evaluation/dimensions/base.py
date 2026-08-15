# Evaluation Dimension Base
# =========================

"""
Canonical evaluation dimension definitions.

ARCHITECTURAL PRINCIPLES:
    - Immutable dimension definitions
    - No runtime dependencies
    - Semantic-only semantics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


WorkspaceEvaluationDimensionIdentity = str
"""Unique identifier for an evaluation dimension."""


WorkspaceEvaluationDimensionRevision = int
"""Monotonically increasing revision number for dimensions."""


WorkspaceEvaluationDimensionReference = str
"""
Immutable reference to a Dimension.

Format: "identity@revision"
Examples:
    "salience@1"
    "urgency@2"
"""


class WorkspaceEvaluationDirection(Enum):
    """
    Canonical direction semantics for evaluation dimensions.

    Direction must not be inferred from field names.
    """

    HIGHER_IS_MORE_FAVORABLE = "higher_is_more_favorable"
    """Higher values indicate more favorable assessment."""

    LOWER_IS_MORE_FAVORABLE = "lower_is_more_favorable"
    """Lower values indicate more favorable assessment."""

    TARGET_RANGE = "target_range"
    """Values near a target range are most favorable."""

    CONSTRAINT_ONLY = "constraint_only"
    """Dimension is used only for constraint checking, not ranking."""

    DESCRIPTIVE_ONLY = "descriptive_only"
    """Dimension is descriptive only, not used in ranking."""

    CONTEXT_DEPENDENT = "context_dependent"
    """Favorability direction depends on context."""


class WorkspaceEvaluationApplicabilityStatus(Enum):
    """
    Canonical applicability statuses for dimensions.

    A non-applicable Dimension must not receive a fabricated neutral score.
    """

    APPLICABLE = "applicable"
    """Dimension applies to this evaluation."""

    CONDITIONALLY_APPLICABLE = "conditionally_applicable"
    """Dimension may apply under certain conditions."""

    NOT_APPLICABLE = "not_applicable"
    """Dimension does not apply to this evaluation."""

    UNSUPPORTED = "unsupported"
    """Evaluation system does not support this dimension."""

    MISSING_CONTEXT = "missing_context"
    """Insufficient context to determine applicability."""

    PROHIBITED = "prohibited"
    """Dimension is explicitly prohibited in current scope."""


WorkspaceEvaluationApplicability = str
"""
Reference to an applicability assessment.

Format: "status@context_revision"
Examples:
    "applicable@context_123@456"
"""


# =============================================================================
# EVALUATION DIMENSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class WorkspaceEvaluationDimension:
    """
    Immutable dimension definition.

    Every dimension must define all required properties.
    """

    identity: WorkspaceEvaluationDimensionIdentity
    """Unique identifier for this dimension."""

    revision: WorkspaceEvaluationDimensionRevision
    """Dimension revision number."""

    canonical_name: str
    """Human-readable canonical name (e.g., 'Salience')."""

    semantic_meaning: str
    """Description of what this dimension measures."""

    owner: str
    """Owner authority for this dimension definition."""

    scale_ref: str
    """Reference to the evaluation Scale for this dimension."""

    direction: WorkspaceEvaluationDirection
    """Favorability direction."""

    applicability_policy: Tuple[str, ...] = field(default_factory=tuple)
    """Applicability rules."""

    evidence_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Required evidence types."""

    missing_value_behavior: str = "missing"
    """Behavior when value is missing (missing/unavailable/not_applicable)."""

    confidence_behavior: str = "explicit"
    """Confidence is tracked explicitly for this dimension."""

    uncertainty_behavior: str = "explicit"
    """Uncertainty is tracked explicitly for this dimension."""

    normalization_policy_ref: Optional[str] = None
    """Reference to normalization policy (if applicable)."""

    calibration_ref: Optional[str] = None
    """Reference to calibration data (if applicable)."""

    bounds: Tuple[float, float] = (0.0, 1.0)
    """Valid value range for normalized scores."""

    introduced_version: str = "4.6.4"
    """Version when this dimension was introduced."""

    deprecated_version: Optional[str] = None
    """Version when dimension becomes deprecated (if applicable)."""

    provenance_ref: str = ""
    """Reference to origin documentation or specification."""