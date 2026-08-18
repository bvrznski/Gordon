# Monitoring Reasoning - Phase 7.22
# ==================================

"""
Monitoring Reasoning provides Gordon's operational awareness engine.

This module implements:
- Observation management (collection, normalization, correlation)
- Execution supervision (progress tracking, stall detection, constraint validation)
- Operational state estimation (active components, resource ownership, system health)
- Anomaly detection (unexpected behavior, missing observations, divergence)
- Progress tracking (completion estimates, velocity metrics, confidence levels)
- Validation (consistency checks, contract verification, finding reporting)
- Governance (evaluation of monitoring quality, violation detection)

The monitoring subsystem constructs an explicit operational model describing
what Gordon is doing and what state the surrounding environment is in.

Unlike logging, Monitoring Reasoning continuously maintains a coherent
operational model that can be queried to understand current execution state.
"""

from __future__ import annotations

# Shared contracts (Part 2)
from .shared.descriptor import MonitoringDescriptor
from .shared.observation_set import ObservationSet
from .shared.supervision import ExecutionSupervision
from .shared.operational_state import OperationalState
from .shared.anomalies import (
    OperationalAnomaly,
    AnomalySet,
    AnomalySeverity,
    AnomalyType,
)
from .shared.progress import ProgressEstimate, CompletionEstimate
from .shared.evolution import MonitoringEvolution, StateTransition
from .shared.validation import (
    MonitoringValidation,
    ValidationFinding,
    ValidationStatus,
)
from .shared.failure import MonitoringFailure, FailureKind
from .shared.governance import MonitoringGovernance, GovernanceFinding
from .shared.health import MonitoringHealth, HealthMetrics

__all__ = [
    # Descriptor and Observation Set
    "MonitoringDescriptor",
    "ObservationSet",
    
    # Supervision
    "ExecutionSupervision",
    
    # Operational State
    "OperationalState",
    
    # Anomalies
    "OperationalAnomaly",
    "AnomalySet",
    "AnomalySeverity",
    "AnomalyType",
    
    # Progress
    "ProgressEstimate",
    "CompletionEstimate",
    
    # Evolution
    "MonitoringEvolution",
    "StateTransition",
    
    # Validation
    "MonitoringValidation",
    "ValidationFinding",
    "ValidationStatus",
    
    # Failure
    "MonitoringFailure",
    "FailureKind",
    
    # Governance
    "MonitoringGovernance",
    "GovernanceFinding",
    
    # Health
    "MonitoringHealth",
    "HealthMetrics",
]