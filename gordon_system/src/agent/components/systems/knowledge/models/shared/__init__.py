# Knowledge Models - Phase 6.7
# ============================

"""
Knowledge Models: Gordon's highest-level semantic knowledge structures.

Models organize Concepts, Assertions, Relations and Beliefs into coherent,
predictive structures capable of supporting explanation, simulation and reasoning.

Architectural Position:
- Model descriptors
- Components and submodels  
- Validation and refinement
- Composition strategies
- Predictions, explanations, comparisons
- Dependencies, governance, health

Models remain declarative - they describe systems, not execute reasoning.
"""

from .descriptor import ModelDescriptor, LifecycleState, PublicationStatus
from .component import ModelComponent, ComponentRole, RequiredPolicy
from .submodel import SubModel, IntegrationKind
from .validation import ModelValidation, ValidationResult, ValidationFinding
from .refinement import ModelRefinement, RefinementReason
from .composition import ModelComposition, CompositionStrategy
from .prediction import ModelPrediction, PredictionSession
from .explanation import ModelExplanation, ExplanationGraph, ExplanationPath
from .comparison import ModelComparison, ComparisonMetric
from .dependency import ModelDependency, DependencyKind
from .governance import ModelGovernance, GovernanceFinding, GovernanceViolation
from .health import ModelHealth, HealthStatus, HealthMetrics
from .diagnostics import ModelDiagnostics, DiagnosticReport

__all__ = [
    # Descriptors
    "ModelDescriptor",
    "LifecycleState", 
    "PublicationStatus",
    
    # Components
    "ModelComponent",
    "ComponentRole",
    "RequiredPolicy",
    
    # Submodels
    "SubModel",
    "IntegrationKind",
    
    # Validation
    "ModelValidation",
    "ValidationResult", 
    "ValidationFinding",
    
    # Refinement
    "ModelRefinement",
    "RefinementReason",
    
    # Composition
    "ModelComposition",
    "CompositionStrategy",
    
    # Predictions
    "ModelPrediction",
    "PredictionSession",
    
    # Explanations
    "ModelExplanation",
    "ExplanationGraph",
    "ExplanationPath",
    
    # Comparison
    "ModelComparison",
    "ComparisonMetric",
    
    # Dependencies
    "ModelDependency",
    "DependencyKind",
    
    # Governance
    "ModelGovernance",
    "GovernanceFinding",
    "GovernanceViolation",
    
    # Health
    "ModelHealth", 
    "HealthStatus",
    "HealthMetrics",
    
    # Diagnostics
    "ModelDiagnostics",
    "DiagnosticReport",
]