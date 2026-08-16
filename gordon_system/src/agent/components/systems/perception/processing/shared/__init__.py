# Perception Processing Shared Components
# =======================================

"""
Shared components for perception processing.

This package provides:
    - Core stage definitions
    - Pipeline composition
    - Transformation records
    - Request/result models
    - Validation primitives
"""

from __future__ import annotations

from .stage import (
    ProcessingStage,
    ProcessingStageInput,
    ProcessingStageOutput,
    InformationLossKind,
    ProcessingInformationLoss,
)
from .pipeline import ProcessingPipeline
from .transformation import (
    ProcessingTransformationRecord,
    PerceptualTransformation,
)
from .request import PerceptionProcessingRequest
from .result import (
    PerceptionProcessingResult,
    ProcessingStatus,
    ProcessingOutcome,
)
from .engine import PerceptionProcessingEngine
from .validation import ProcessingValidation, ValidationResult, ValidationFailure


__all__ = [
    # Stage components
    "ProcessingStage",
    "ProcessingStageInput",
    "ProcessingStageOutput",
    
    # Pipeline components
    "ProcessingPipeline",
    
    # Transformation components
    "ProcessingTransformationRecord",
    "PerceptualTransformation",
    
    # Request/Result components
    "PerceptionProcessingRequest",
    "PerceptionProcessingResult",
    "ProcessingStatus",
    "ProcessingOutcome",
    
    # Engine
    "PerceptionProcessingEngine",
    
    # Validation
    "ProcessingValidation",
    "ValidationResult",
    "ValidationFailure",
    
    # Information Loss
    "ProcessingInformationLoss",
    "InformationLossKind",
]