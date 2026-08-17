# Shared Knowledge Foundations - Phase 6.1

"""
Shared foundational components for Gordon's knowledge foundations.

This package provides shared infrastructure including:
    * BaseKnowledgeArtifact - Universal contract for all semantic artifacts
    * ValidationPipeline - Semantic validation engine with multiple check types
"""

from __future__ import annotations

# Core contracts
from .artifact import (
    BaseKnowledgeArtifact,
    SemanticLifecycleState,
    SemanticPublicationStatus,
    SemanticCompatibilityKind,
    SemanticCertificationLevel,
    SemanticValidationLevel,
)

# Validation pipeline
from .validation import (
    SemanticValidation,
    ValidationCheckType,
    ValidationCheckResult,
    ValidationResult,
)

__all__ = [
    # Artifact contract
    "BaseKnowledgeArtifact",
    "SemanticLifecycleState",
    "SemanticPublicationStatus",
    "SemanticCompatibilityKind",
    "SemanticCertificationLevel",
    "SemanticValidationLevel",
    # Validation pipeline
    "SemanticValidation",
    "ValidationCheckType",
    "ValidationCheckResult",
    "ValidationResult",
]