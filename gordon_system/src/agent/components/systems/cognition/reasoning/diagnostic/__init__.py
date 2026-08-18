# Diagnostic Reasoning Module - Phase 7.39
# ========================================

"""
Diagnostic Reasoning subsystem for Gordon Cognitive Architecture.

This module provides:
    - Anomaly management and classification
    - Fault localization and identification
    - Root-cause analysis
    - Failure propagation analysis
    - Recovery hypothesis generation
    - Validation and governance

The diagnostic reasoning engine transforms observations, symptoms and failures into
explicit explanations, ranked diagnostic hypotheses and recovery hypotheses.
"""

from agent.components.systems.cognition.reasoning.diagnostic.shared.descriptor import (
    DiagnosticDescriptor,
    DiagnosticSessionIdentity,
    DiagnosticMode,
    DiagnosticLifecycle,
)

from agent.components.systems.cognition.reasoning.diagnostic.shared.pipeline import (
    DiagnosticStage,
    DiagnosticPipelineState,
    DiagnosticSetIdentity,
    Observations,
    DiagnosticSet,
    DiagnosticPipelineResult,
    DiagnosticPipeline,
)

from agent.components.systems.cognition.reasoning.diagnostic.anomalies.model import (
    AnomalyKind,
    AnomalyClassification,
    AnomalySeverity,
    AnomalyModel,
    AnomalySetIdentity,
)

from agent.components.systems.cognition.reasoning.diagnostic.faults.model import (
    FaultKind,
    FaultSeverity,
    FaultModel,
    FaultSetIdentity,
)

__all__ = [
    # Shared contracts
    "DiagnosticDescriptor",
    "DiagnosticSessionIdentity", 
    "DiagnosticMode",
    "DiagnosticLifecycle",
    
    "DiagnosticStage",
    "DiagnosticPipelineState",
    "DiagnosticSetIdentity",
    "Observations",
    "DiagnosticSet",
    "DiagnosticPipelineResult",
    "DiagnosticPipeline",
    
    # Anomaly management
    "AnomalyKind",
    "AnomalyClassification",
    "AnomalySeverity",
    "AnomalyModel",
    "AnomalySetIdentity",
    
    # Fault management
    "FaultKind",
    "FaultSeverity",
    "FaultModel",
    "FaultSetIdentity",
]