# Canonical Prediction Error Policy Configuration
# ==============================================
"""
Policy configuration for Prediction Error Network Phase 4.9.2.

This module provides:
    - ComparisonPolicy: Immutable comparison configuration

PHASE BOUNDARY:
    This is pure semantic infrastructure with NO runtime dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass


# =============================================================================
# COMPARISON POLICY (IMMUTABLE CONFIGURATION)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ComparisonPolicy:
    """
    Immutable comparison policy configuration.
    
    Fields:
        comparison_strictness:     How strict the comparison is
        categorical_tolerance:     Tolerance for category mismatches
        numeric_tolerance:         Tolerance for value differences
        latent_tolerance:          Tolerance for latent space distance
        temporal_tolerance:        Tolerance for time differences
        hierarchy_policy:          Hierarchy-level comparison rules
        unknown_handling:          How to handle unknown values
        missing_observation_policy: Policy when observation is missing
        
    Rules:
        - Policy is immutable (frozen dataclass)
        - No callbacks, no model instances, no service references
    """
    comparison_strictness: str = "normal"  # RELAXED/NORMAL/STRICT/CANONICAL
    categorical_tolerance: str = "exact"  # exact/relaxed/strict
    numeric_tolerance: float | None = None  # Absolute difference allowed
    latent_tolerance: float | None = None  # Distance threshold
    temporal_tolerance: str = "semantic"  # semantic/absolute/relative
    hierarchy_policy: str = "preserve"  # preserve/constrain/propagate
    unknown_handling: str = "report"  # report/reject/treat_as_match
    missing_observation_policy: str = "report_absence"  # report_absence/reject


# =============================================================================
# VALUE COMPARISON STRATEGY (FOR SCALAR VALUES)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValueComparisonStrategy:
    """
    Strategy for scalar value comparison.
    
    Fields:
        tolerance:              Allowed difference
        units:                  Units of measurement
        normalize_values:       Whether to normalize before comparison
        
    Rules:
        - Deterministic comparison
    """
    tolerance: float = 0.0
    units: str | None = None
    normalize_values: bool = False


# =============================================================================
# CATEGORICAL COMPARISON STRATEGY (FOR CLASSIFICATIONS)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CategoricalComparisonStrategy:
    """
    Strategy for categorical comparison.
    
    Fields:
        matching_rule:          How categories are matched
        ignore_case:            Whether to ignore case in strings
        
    Rules:
        - Semantic classification comparison
    """
    matching_rule: str = "exact"  # exact/subset/superset/overlap
    ignore_case: bool = False


# =============================================================================
# STRUCTURED COMPARISON STRATEGY (FOR GRAPHS/TREES)
# =============================================================================

@dataclass(frozen=True, slots=True)
class StructuredComparisonStrategy:
    """
    Strategy for structured comparison.
    
    Fields:
        node_matching:          How nodes are matched
        edge_matching:          How edges/relationships are matched
        structural_tolerance:   Tolerance for structure differences
        
    Rules:
        - Graph/hierarchy comparison strategy
    """
    node_matching: str = "identity"  # identity/semantic/type
    edge_matching: str = "type"  # type/direction/weight
    structural_tolerance: float = 0.0


# =============================================================================
# LATENT COMPARISON CONTRACT (FOR EMBEDDINGS)
# =============================================================================

@dataclass(frozen=True, slots=True)
class LatentComparisonContract:
    """
    Contract for latent space comparison.
    
    Fields:
        schema_id:              Latent schema identifier
        embedding_dimensions:   Expected dimensionality
        distance_metric:        Metric to use (cosine/euclidean/manhattan)
        threshold:              Distance threshold for mismatch
        
    Rules:
        - Compatible schemas required
        - No encoder training in Phase 4.9.2
    """
    schema_id: str
    embedding_dimensions: int
    distance_metric: str = "cosine"  # LatentMetric or string code
    threshold: float | None = None


# =============================================================================
# MULTIMODAL COMPARISON CONTRACT (FOR CROSS-MODAL ALIGNMENT)
# =============================================================================

@dataclass(frozen=True, slots=True)
class MultimodalComparisonContract:
    """
    Contract for multimodal comparison.
    
    Fields:
        modalities:             Modalities to compare
        alignment_policy:       How to align across modalities
        agreement_threshold:    Agreement level required
        
    Rules:
        - Modalities remain explicit
        - No fusion in Phase 4.9.2 (only disagreement representation)
    """
    modalities: tuple[str, ...] = ()  # e.g., ("vision", "language")
    alignment_policy: str = "semantic"  # semantic/structural/temporal
    agreement_threshold: float = 1.0