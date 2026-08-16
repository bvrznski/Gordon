# =============================================================================
# PREDICTIVE NETWORK TREE METADATA - PHASE 4.9.9
# =============================================================================

"""
Predictive Network Canonical Architecture Tree

This module provides the canonical structural metadata for the Predictive Network,
defining ownership, relationships, and semantic boundaries.

PHASE 4.9.9: COHERENCE ENHANCEMENT
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# =============================================================================
# CANONICAL OWNERSHIP
# =============================================================================


@dataclass(frozen=True, slots=True)
class PredictiveNetworkTree:
    """
    Canonical Predictive Network tree structure.

    The Predictive Network is a canonical owner of:

        - Prediction generation (expectation formation)
        - Prediction comparison (expectation vs observation)
        - Prediction error representation (structured discrepancy)
        - Precision estimation (epistemic weighting of errors)

    The Predictive Network coordinates:

        - Belief revision proposals (evidence for epistemic change)
        - World model synchronization requests (semantic propagation)

    The Predictive Network NEVER owns:

        - Salience computation
        - Attention allocation
        - Runtime execution
        - Scheduling
        - Action selection
        - Memory persistence
        - Learning adaptation
    """

    # Network identity
    network_name: str = "PredictiveNetwork"
    network_role: str = "Canonical semantic predictive processing"

    # Core responsibilities (what Predictive owns)
    owns: tuple[str, ...] = (
        "Prediction semantics",
        "Prediction error representation",
        "Precision estimation",
        "Belief revision proposals",
        "World model synchronization requests",
        "Error landscape structure",
        "Precision landscape structure",
        "Temporal prediction horizons",
        "Hierarchical prediction structure",
        "Counterfactual prediction isolation",
    )

    # Coordinator relationships (what Predictive uses but doesn't own)
    coordinates: tuple[str, ...] = (
        "Belief revision implementation",
        "World model synchronization implementation",
        "Error comparison implementation",
        "Precision estimation implementation",
    )

    # External boundaries (what Predictive explicitly does NOT own)
    does_not_own: tuple[str, ...] = (
        "Salience computation",  # Consumes predictive evidence
        "Attention allocation",
        "Runtime scheduling",
        "Thread management",
        "Action selection",
        "Memory persistence",
        "Learning adaptation",
        "Execution control",
        "Global salience priority",
    )

    # Pipeline stages (canonical semantic pipeline)
    pipeline_stages: tuple[str, ...] = (
        "Context",
        "Prediction formation",
        "Prediction generation",
        "Observation comparison",
        "Prediction error computation",
        "Prediction error landscape construction",
        "Precision estimation",
        "Precision landscape construction",
        "Belief revision proposal",
        "World model synchronization",
        "Predictive outcome",
    )


# =============================================================================
# SEMANTIC TYPE TREE
# =============================================================================


@dataclass(frozen=True, slots=True)
class PredictiveTypeTree:
    """
    Canonical type ownership tree for the Predictive Network.

    Every major concept has exactly one canonical owner and representation.
    """

    # Core semantic types (owned by Predictive)
    prediction_types: tuple[str, ...] = (
        "Prediction",
        "Observation",
        "PredictionError",
        "Mismatch",
        "Residual",
    )

    # Landscape types
    landscape_types: tuple[str, ...] = (
        "PredictionErrorLandscape",
        "PrecisionLandscape",
        "BeliefRevisionGraph",
        "WorldModelProjection",
    )

    # Estimation types
    estimation_types: tuple[str, ...] = (
        "PrecisionEstimate",
        "ReliabilitySource",
    )

    # Request/Result types
    contract_types: tuple[str, ...] = (
        "PredictionRequest",
        "PredictionResult",
        "PrecisionRequest",
        "PrecisionResult",
        "BeliefRevisionRequest",
        "BeliefRevisionResult",
        "WorldModelSynchronizationRequest",
        "WorldModelSynchronizationResult",
    )

    # Infrastructure types
    infra_types: tuple[str, ...] = (
        "SemanticIdentity",
        "PredictionIdentity",
        "Revision",
        "Provenance",
        "SchemaVersion",
    )


# =============================================================================
# IMPORT BOUNDARIES (WHAT CAN IMPORT WHAT)
# =============================================================================


CANONICAL_IMPORT_RULES: Final[tuple[str, ...]] = (
    "Predictive modules may import other Predictive modules",
    "Salience may consume Predictive outputs but not import internal engines",
    "Core may orchestrate Predictive but must not import implementation details",
    "Integration may coordinate Predictive and other networks",
    "No module may import Core runtime machinery",
    "No circular dependencies allowed",
)


# =============================================================================
# CANONICAL EXPORTS (PUBLIC API)
# =============================================================================

CANONICAL_EXPORTS: Final[tuple[str, ...]] = (
    # Prediction
    "Prediction",
    "PredictionRequest",
    "ObservationProjection",
    
    # Error
    "PredictionError",
    "Mismatch",
    "Residual",
    "PredictionComparisonResult",
    "PredictionErrorState",
    
    # Precision
    "PrecisionEstimate",
    "PrecisionLandscape",
    "ReliabilitySource",
    "PrecisionRequest",
    "PrecisionResult",
    
    # Belief Revision
    "BeliefRevisionRequest",
    "BeliefRevisionResult",
    
    # World Model
    "WorldModelSynchronizationRequest",
    "WorldModelSynchronizationResult",
    
    # Infrastructure
    "SemanticIdentity",
    "PredictionIdentity",
    "Revision",
    "SchemaVersion",
)


# =============================================================================
# PHASE CONSTANTS
# =============================================================================

PHASE_VERSION: Final[str] = "4.9.9"
PHASE_STATUS: Final[str] = "ENHANCED_AND_COHERENT"