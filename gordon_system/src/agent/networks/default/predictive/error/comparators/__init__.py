# Comparator Package - Phase 4.9.3
# ==================================
"""
Comparator implementations for the Prediction Error Processing Engine.

This package contains all comparator modules:

    scalar.py      - Scalar value comparison
    categorical.py - Categorical classification comparison  
    structural.py  - Graph/hierarchy structure comparison
    temporal.py    - Temporal ordering comparison
    spatial.py     - Spatial location/geometry comparison
    causal.py      - Cause-effect relationship comparison
    relational.py  - Semantic relation comparison
    latent.py      - Latent state projection comparison
    distribution.py - Probability distribution comparison
    multimodal.py  - Cross-modality agreement check
    unknown.py     - Unknown value handling

All comparators share the same interface:
    compare(expected, observed, policy) -> Residual
    
LAW COMPLIANCE:
    * COMPARATOR-LAW-001: Each comparator owns exactly one semantic domain
    * COMPARATOR-LAW-002: Pure functions (no side effects)
    * COMPARATOR-LAW-003: Deterministic outputs (same inputs = same outputs)
    * COMPARATOR-LAW-004: Stateless (no internal state between calls)
    * COMPARATOR-LAW-005: Return only Residual objects
    * COMPARATOR-LAW-006: Never construct PredictionError directly
    * COMPARATOR-LAW-007: Never construct PredictionErrorState
    * COMPARATOR-LAW-008: Never invoke other comparators
"""

from __future__ import annotations

# Import all comparator implementations
from gordon_system.src.agent.networks.default.predictive.error.comparators.scalar import (
    ScalarComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.categorical import (
    CategoricalComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.structural import (
    StructuralComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.temporal import (
    TemporalComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.spatial import (
    SpatialComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.causal import (
    CausalComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.relation import (
    RelationalComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.latent import (
    LatentComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.distribution import (
    DistributionComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.multimodal import (
    MultimodalComparator,
)
from gordon_system.src.agent.networks.default.predictive.error.comparators.unknown import (
    UnknownComparator,
)

# Import base types
from gordon_system.src.agent.networks.default.predictive.error.comparators.base import (
    Residual,
    Comparator,
    ComparatorEntry,
)

__all__ = [
    # Base types
    "Residual",
    "Comparator", 
    "ComparatorEntry",
    
    # Comparator implementations
    "ScalarComparator",
    "CategoricalComparator",
    "StructuralComparator",
    "TemporalComparator",
    "SpatialComparator",
    "CausalComparator",
    "RelationalComparator",
    "LatentComparator",
    "DistributionComparator",
    "MultimodalComparator",
    "UnknownComparator",
]