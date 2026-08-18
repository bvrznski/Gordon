# Stability Reasoning Module - Phase 7.26
# =======================================

"""
Canonical Stability Reasoning subsystem for Gordon Cognitive Architecture.

Stability Reasoning is Gordon's cognitive homeostasis engine. It determines
whether Gordon remains cognitively stable and what must be stabilized before
reliable cognition can continue.

This module implements:

    Shared Contracts:
        - StabilityDescriptor: Metadata exposure independent of execution
        - StabilitySet: Monitored subsystems and stability constraints
        - StabilityPipeline: Canonical flow from analysis to publication
        
    Homeostasis Contracts:
        - HomeostasisManagement: Resource equilibrium evaluation
        - HomeostasisVariable: Individual monitored variables
        - EquilibriumModel: Equilibrium metrics model
        
    Degradation Contracts:
        - DegradationAnalysis: Performance decay and failure propagation
        - DegradationMetric: Single degradation measurement
        - DegradationModel: Propagation relationships
        
    Containment Contracts:
        - ContainmentManagement: Fault isolation policies
        - ProtectedComponent: Component protection details
        - ContainmentScope: Scope of containment
    
    Stabilization Contracts:
        - StabilizationManagement: Stabilization strategy planning
        - StabilizationActionPlan: Specific stabilization actions
        - ExitCondition: When to exit stabilized state
        - RollbackStrategy: Fallback plan if stabilization fails
        
    Validation Contracts:
        - StabilityValidation: Result of validation operations
        - StabilityValidationFinding: Findings from validation
        - StabilityValidationGovernance: Governance rules for validation
        - StabilityValidationResult: Possible validation outcomes
        
    Governance Contracts:
        - StabilityGovernance: Evaluation of stability correctness
        - StabilityGovernanceFinding: Governance evaluation findings
        
    Diagnostics Contracts:
        - StabilityTrace: Complete operation history and trace
        - StabilityDiagnostic: Observations about operations

Stability Reasoning is never execution, monitoring, or evaluation.
It determines the stable operational configuration upon which those
can safely proceed.

All contracts are immutable during reasoning to ensure deterministic
analysis results.
"""

__all__ = [
    "StabilityDescriptor",
    "StabilityKind",
    "StabilityState",
    "StabilitySet",
    "StabilityConstraint",
    "SubsystemKind",
    "StabilityPipeline",
    "StabilityStage",
    "HomeostasisManagement",
    "HomeostasisVariable",
    "EquilibriumModel",
    "DegradationAnalysis",
    "DegradationMetric",
    "DegradationModel",
    "DegradationType",
    "ContainmentManagement",
    "ProtectedComponent",
    "ContainmentScope",
    "ContainmentPolicy",
    "StabilizationManagement",
    "StabilizationActionPlan",
    "ExitCondition",
    "RollbackStrategy",
    "StabilizationAction",
    "StabilityValidation",
    "StabilityValidationFinding",
    "StabilityValidationGovernance",
    "StabilityValidationResult",
    "StabilityGovernance",
    "StabilityGovernanceFinding",
    "StabilityTrace",
    "StabilityDiagnostic",
]

# Import stability contracts from shared module
from gordon_system.src.agent.components.systems.cognition.reasoning.stability.shared import (
    # Descriptors
    StabilityDescriptor,
    StabilityKind,
    StabilityState,
    
    # Sets and Pipeline
    StabilitySet,
    StabilityConstraint,
    SubsystemKind,
    StabilityPipeline,
    StabilityStage,
    
    # Homeostasis
    HomeostasisManagement,
    HomeostasisVariable,
    EquilibriumModel,
    
    # Degradation
    DegradationAnalysis,
    DegradationMetric,
    DegradationModel,
    DegradationType,
    
    # Containment
    ContainmentManagement,
    ProtectedComponent,
    ContainmentScope,
    ContainmentPolicy,
    
    # Stabilization
    StabilizationManagement,
    StabilizationActionPlan,
    ExitCondition,
    RollbackStrategy,
    StabilizationAction,
    
    # Validation
    StabilityValidation,
    StabilityValidationFinding,
    StabilityValidationGovernance,
    StabilityValidationResult,
    
    # Governance
    StabilityGovernance,
    StabilityGovernanceFinding,
    
    # Diagnostics and Trace
    StabilityTrace,
    StabilityDiagnostic,
)