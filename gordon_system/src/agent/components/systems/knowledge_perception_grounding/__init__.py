# Knowledge-Perception Grounding - Phase 5.6
# ============================================

"""
Knowledge-Perception Grounding: The architectural bridge between perception and knowledge.

This module provides the canonical contracts for grounding semantic knowledge in
current perceptual evidence, ensuring Gordon's semantic world remains connected to reality.

Canonical flow:
    Environment → Sensory Perception → Percept Processing → Percepts
        ↓
    Knowledge–Perception Grounding → Semantic Candidates → Knowledge Validation
        ↓
    Grounded Knowledge

Key responsibilities:
- Percept interpretation requests
- Semantic grounding requests
- Observation packaging
- Semantic candidate generation
- Concept correspondence
- Ambiguity preservation
- Confidence propagation
- Provenance tracking
"""

from __future__ import annotations

# Core contracts (Part 1)
from .shared.observation import (
    ObservationSourceKind,
    ObservationType,
    Observation,
    ObservationSession,
    ObservationSource,
)

from .shared.percept import (
    PerceptKind,
    Percept,
    PerceptGroup,
    PerceptEmbedding,
    PerceptClassification,
    PerceptRepresentation,
)

# Correspondence contracts (Part 2)
from .shared.correspondence import (
    CorrespondenceKind,
    SemanticCorrespondence,
    VectorCorrespondence,
    StructuralCorrespondence,
    HybridCorrespondence,
)

# Novelty detection (Part 2)
from .shared.novelty import (
    NoveltyKind,
    NoveltyAssessment,
    NoveltyDetection,
    NoveltyDetectionEngineResult,
)

# Grounding and candidates (Part 2)
from .shared.grounding import (
    GroundingKind,
    GroundedEvent,
    KnowledgePerceptionGrounding,
    KnowledgePerceptionGroundingRequest,
    KnowledgePerceptionGroundingAssessment,
    SemanticCandidateKind,
    SemanticCandidate,
)

# Active perception and reality validation (Part 2)
from .shared.active_reality import (
    ActivePerceptionOutcome,
    ActivePerceptionRequest,
    ActivePerceptionResponse,
    RealityValidationRecommendation,
    RealityValidationRequest,
    RealityValidationResult,
    RealityValidationEngineResult,
)

from .shared.ambiguity import (
    PerceptAmbiguity,
    AmbiguityResolution,
    AmbiguityGroup,
    AmbiguityContext,
)

__all__ = [
    # Observation
    "ObservationSourceKind",
    "ObservationType",
    "Observation",
    "ObservationSession",
    "ObservationSource",
    
    # Percept
    "PerceptKind",
    "Percept",
    "PerceptGroup",
    "PerceptEmbedding",
    "PerceptClassification",
    "PerceptRepresentation",
    
    # Correspondence
    "CorrespondenceKind",
    "SemanticCorrespondence",
    "VectorCorrespondence",
    "StructuralCorrespondence",
    "HybridCorrespondence",
    
    # Novelty
    "NoveltyKind",
    "NoveltyAssessment",
    "NoveltyDetection",
    "NoveltyDetectionEngineResult",
    
    # Grounding and candidates
    "GroundingKind",
    "GroundedEvent",
    "KnowledgePerceptionGrounding",
    "KnowledgePerceptionGroundingRequest",
    "KnowledgePerceptionGroundingAssessment",
    "SemanticCandidateKind",
    "SemanticCandidate",
    
    # Active perception and reality validation
    "ActivePerceptionOutcome",
    "ActivePerceptionRequest",
    "ActivePerceptionResponse",
    "RealityValidationRecommendation",
    "RealityValidationRequest",
    "RealityValidationResult",
    "RealityValidationEngineResult",
    
    # Ambiguity
    "PerceptAmbiguity",
    "AmbiguityResolution",
    "AmbiguityGroup",
    "AmbiguityContext",
]

__version__ = "1.0.0"
