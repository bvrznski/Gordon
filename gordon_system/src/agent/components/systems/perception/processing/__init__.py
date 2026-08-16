# Perception Processing - Phase 5.2.2
# ======================================
#
# This module provides deterministic transformation of modality-produced evidence.
# It transforms evidence without interpreting knowledge or committing to Memory.
#
# Core functions:
#   - Adaptive processing (response to environmental changes)
#   - Habituation (reduced emphasis for repetitive signals)
#   - Novelty detection (attention to changing patterns)
#   - Temporal/spatial/identity/schema alignment
#   - Translation between modality-specific and canonical representations
#   - Normalization of heterogeneous values and conventions

"""
Perception Processing: Phase 5.2.2

This module implements the deterministic transformation layer for perceptual evidence.

Key responsibilities:
    - Adaptive processing configuration
    - Habituation assessment and novelty detection
    - Temporal, spatial, identity, and schema alignment
    - Translation between modality-specific and canonical representations
    - Normalization of heterogeneous values and conventions
    - Confidence, uncertainty, and information-loss propagation
    - Processing validation and diagnostics

Architectural boundaries:
    - Does NOT perform signal acquisition (owned by Modalities)
    - Does NOT perform multimodal fusion (owned by Integration)
    - Does NOT commit to Memory (owned by Memory subsystem)
    - Does NOT construct Knowledge or perform reasoning
"""

from __future__ import annotations

# Core processing types
from gordon_system.src.agent.components.systems.perception.foundations.confidence import Confidence
from gordon_system.src.agent.components.systems.perception.foundations.uncertainty import Uncertainty  
from gordon_system.src.agent.components.systems.perception.foundations.provenance import Provenance

# Import shared processing components
from .shared.stage import ProcessingStage, ProcessingStageInput, ProcessingStageOutput
from .shared.pipeline import ProcessingPipeline
from .shared.transformation import ProcessingTransformationRecord, PerceptualTransformation
from .shared.request import PerceptionProcessingRequest
from .shared.result import PerceptionProcessingResult, ProcessingStatus, ProcessingOutcome
from .shared.engine import PerceptionProcessingEngine
from .shared.validation import ProcessingValidation, ValidationResult

# Import processing domain modules
from .adaptive.assessment import AdaptiveProcessingAssessment
from .habituation.assessment import HabituationAssessment, HabituationLevel
from .alignment.temporal import TemporalAlignment
from .alignment.spatial import SpatialAlignment
from .alignment.identity import PerceptualIdentityAlignment
from .alignment.schema import PerceptualSchemaAlignment
from .translation.translation import PerceptualTranslation
from .normalization.normalization import PerceptualNormalization

__all__ = [
    # Core components
    "ProcessingStage",
    "ProcessingStageInput", 
    "ProcessingStageOutput",
    "ProcessingPipeline",
    "ProcessingTransformationRecord",
    "PerceptualTransformation",
    "PerceptionProcessingRequest",
    "PerceptionProcessingResult",
    "ProcessingStatus",
    "ProcessingOutcome",
    "PerceptionProcessingEngine",
    "ProcessingValidation",
    "ValidationResult",
    
    # Adaptive processing
    "AdaptiveProcessingAssessment",
    
    # Habituation
    "HabituationAssessment",
    "HabituationLevel",
    
    # Alignment
    "TemporalAlignment",
    "SpatialAlignment",
    "PerceptualIdentityAlignment",
    "PerceptualSchemaAlignment",
    
    # Translation
    "PerceptualTranslation",
    
    # Normalization
    "PerceptualNormalization",
]