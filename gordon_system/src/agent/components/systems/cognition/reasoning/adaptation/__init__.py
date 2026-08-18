# Adaptation Reasoning Module - Phase 7.25
# =======================================

"""
Canonical Adaptation Reasoning subsystem for Gordon Cognitive Architecture.

Adaptation Reasoning transforms evaluation and learning outcomes into temporary,
reversible behavioral modifications. It determines how Gordon should adjust to its
current operational context without permanently changing itself.

This module implements:

    Shared Contracts:
        - AdaptationDescriptor: Metadata exposure independent of execution
        - AdaptationSet: Candidates, constraints, and policies for sessions
        - AdaptationPipeline: Canonical flow from analysis to publication
        
    Behavioral Contracts:
        - BehaviorAdaptation: Behavioral modifications with metrics
        - BehaviorManagement: Evaluation of behavior suitability
        
    Contextual Contracts:
        - ContextAdaptation: Environment-specific policies and configurations
        - ContextManagement: Context evaluation and inference
        
    Configuration Contracts:
        - ConfigurationRefinement: Parameter updates and threshold adjustments
        - ConfigurationManagement: Configuration consistency checks
        
    Integration:
        - AdaptationIntegration: Coherent configuration from multiple adaptations
        
    Evolution:
        - AdaptationEvolution: Preserving identity while adapting to new conditions
        
    Validation:
        - AdaptationValidation: Observational correctness, compatibility, safety
        
    Failure Handling:
        - AdaptationFailure: Explicit failures with recovery options
        - FailureKind: Configuration conflicts, policy incompatibility, etc.
        
    Governance:
        - AdaptationGovernance: Compliance and safety evaluations
        
    Health:
        - AdaptationHealth: Metrics for operational state and stability
        
    Diagnostics:
        - AdaptationTrace: Complete session history and diagnostics
        - AdaptationDiagnostic: Observations about adaptation operations

Adaptation Reasoning never performs permanent cognitive modification.
All adaptations are temporary, reversible, and traceable.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.adaptation.shared import (
    # Descriptors
    AdaptationDescriptor,
    AdaptationMode,
    AdaptationState,
    
    # Sets and Candidates
    AdaptationSet,
    AdaptationCandidate,
    
    # Pipeline
    AdaptationPipeline,
    AdaptationStage,
    
    # Behavior
    BehaviorAdaptation,
    BehaviorManagement,
    
    # Context
    ContextAdaptation,
    ContextManagement,
    
    # Configuration
    ConfigurationRefinement,
    ConfigurationManagement,
    
    # Integration
    AdaptationIntegration,
    
    # Evolution
    AdaptationEvolution,
    
    # Validation
    AdaptationValidation,
    ValidationResult,
    
    # Failure
    AdaptationFailure,
    FailureKind,
    
    # Governance
    AdaptationGovernance,
    
    # Health
    AdaptationHealth,
    
    # Diagnostics and Trace
    AdaptationTrace,
    AdaptationDiagnostic,
)

__all__ = [
    # Descriptors
    "AdaptationDescriptor",
    "AdaptationMode",
    "AdaptationState",
    
    # Sets and Candidates
    "AdaptationSet",
    "AdaptationCandidate",
    
    # Pipeline
    "AdaptationPipeline",
    "AdaptationStage",
    
    # Behavior
    "BehaviorAdaptation",
    "BehaviorManagement",
    
    # Context
    "ContextAdaptation",
    "ContextManagement",
    
    # Configuration
    "ConfigurationRefinement",
    "ConfigurationManagement",
    
    # Integration
    "AdaptationIntegration",
    
    # Evolution
    "AdaptationEvolution",
    
    # Validation
    "AdaptationValidation",
    "ValidationResult",
    
    # Failure
    "AdaptationFailure",
    "FailureKind",
    
    # Governance
    "AdaptationGovernance",
    
    # Health
    "AdaptationHealth",
    
    # Diagnostics and Trace
    "AdaptationTrace",
    "AdaptationDiagnostic",
]