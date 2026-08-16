# Salience Network Evaluation Package
# ====================================

"""
Salience Network Evaluation Foundation (Phase 4.8.5).

This package implements the canonical deterministic salience evaluation
mechanism for evaluating semantic evidence into typed salience assessments.

ARCHITECTURAL PURPOSE:
    The SalienceEvaluator transforms immutable observations, evidence,
    cues, context, and external projections into typed salience assessments
    and Candidate State.

EVALUATION FLOW:
    Input:  Typed immutable salience inputs (observations, evidence, cues, etc.)
    Process: Deterministic evaluation via dimension evaluators
    Output: SalienceAssessmentState and SalienceNetworkState (Candidate)

ARCHITECTURAL BOUNDARIES:
    The SalienceEvaluator owns only the interpretation of salience.
    It does NOT own:
      - Attention allocation (owned by Attention Network)
      - Executive control (owned by Executive Network)
      - Goal selection
      - Action execution
      - Runtime scheduling

ARCHITECTURAL INVARIANTS:
    SAL-EVAL-INV-001: Evaluation is deterministic for equivalent input.
    SAL-EVAL-INV-002: Evaluation produces immutable outputs.
    SAL-EVAL-INV-003: External ownership and authority are preserved.
    SAL-EVAL-INV-004: No side effects during evaluation.
    SAL-EVAL-INV-005: No runtime dependencies (no current time, no UUIDs).
"""

from __future__ import annotations

# =============================================================================
# PHASE 4.8.5: Core Evaluation Abstractions
# =============================================================================

from ._enums import (
    SalienceDimension,
    SalienceEvaluationStatus,
    SalienceDimensionStatus,
    SalienceAggregationStatus,
    SalienceCompositionStatus,
)

from ._request import SalienceEvaluationRequest
from ._context import SalienceEvaluationContext
from ._result import (
    SalienceEvaluationResult,
    SalienceDimensionResult,
    SalienceEvidenceAggregationResult,
    SalienceAssessmentCompositionResult,
)

from ._policy import (
    SalienceEvaluationPolicy,
    SalienceAggregationPolicy,
    SalienceCompositionPolicy,
)

from ._findings import (
    SalienceEvaluationFinding,
    SalienceLimitation,
)

from ._trace import (
    SalienceEvaluationTrace,
    SalienceEvaluationTraceEntry,
)

# =============================================================================
# PHASE 4.8.5: Source Classification
# =============================================================================

from ._sources import SalienceSourceKind

# =============================================================================
# PHASE 4.8.5: Dimension Evaluators (Protocol)
# =============================================================================

from ._protocol import SalienceDimensionEvaluator

# =============================================================================
# PHASE 4.8.5: Evaluation Entry Point
# =============================================================================

from ._evaluator import (
    SalienceEvaluator,
    evaluate_salience,
)

__all__ = [
    # Enums and statuses
    "SalienceDimension",
    "SalienceEvaluationStatus",
    "SalienceDimensionStatus",
    "SalienceAggregationStatus",
    "SalienceCompositionStatus",
    
    # Request and context
    "SalienceEvaluationRequest",
    "SalienceEvaluationContext",
    
    # Results
    "SalienceEvaluationResult",
    "SalienceDimensionResult",
    "SalienceEvidenceAggregationResult",
    "SalienceAssessmentCompositionResult",
    
    # Policies
    "SalienceEvaluationPolicy",
    "SalienceAggregationPolicy",
    "SalienceCompositionPolicy",
    
    # Findings and limitations
    "SalienceEvaluationFinding",
    "SalienceLimitation",
    
    # Trace
    "SalienceEvaluationTrace",
    "SalienceEvaluationTraceEntry",
    
    # Source classification
    "SalienceSourceKind",
    
    # Protocol
    "SalienceDimensionEvaluator",
    
    # Evaluator
    "SalienceEvaluator",
    "evaluate_salience",
]