# Knowledge Shared - Phase 5.4
# ============================

"""
Shared components for Gordon's knowledge system.

This module provides canonical models, validators, and utilities used across
all knowledge capability implementations.
"""

from __future__ import annotations

from .assertion import KnowledgeAssertion, AssertionState, AssertionValidator
from .proposition import KnowledgeProposition, PropositionState, PropositionBuilder
from .concept import KnowledgeConcept, ConceptRelationType, ConceptHierarchyBuilder
from .relation import KnowledgeRelation, RelationKind, RelationBuilder
from .model import KnowledgeModel, ModelScope, ModelBuilder
from .belief import KnowledgeBelief, BeliefState, BeliefValidator
from .evidence import KnowledgeEvidence, EvidenceKind, EvidenceChain
from .justification import KnowledgeJustification, JustificationKind, JustificationBuilder
from .confidence import KnowledgeConfidence, ConfidenceSource, ConfidenceAggregator
from .uncertainty import KnowledgeUncertainty, UncertaintySource, UncertaintyAggregator
from .provenance import ProvenanceEvent, KnowledgeProvenance
from .validation import (
    ValidationResult,
    ValidationFailure,
    KnowledgeValidation,
    KnowledgeValidationEngine,
)
from .health import KnowledgeHealthMetrics, KnowledgeHealthInspector
from .diagnostics import DiagnosticFinding, KnowledgeDiagnosticReport, KnowledgeDiagnosticsEngine

__all__ = [
    # Assertion
    "KnowledgeAssertion",
    "AssertionState",
    "AssertionValidator",
    # Proposition
    "KnowledgeProposition",
    "PropositionState",
    "PropositionBuilder",
    # Concept
    "KnowledgeConcept",
    "ConceptRelationType",
    "ConceptHierarchyBuilder",
    # Relation
    "KnowledgeRelation",
    "RelationKind",
    "RelationBuilder",
    # Model
    "KnowledgeModel",
    "ModelScope",
    "ModelBuilder",
    # Belief
    "KnowledgeBelief",
    "BeliefState",
    "BeliefValidator",
    # Evidence
    "KnowledgeEvidence",
    "EvidenceKind",
    "EvidenceChain",
    # Justification
    "KnowledgeJustification",
    "JustificationKind",
    "JustificationBuilder",
    # Confidence
    "KnowledgeConfidence",
    "ConfidenceSource",
    "ConfidenceAggregator",
    # Uncertainty
    "KnowledgeUncertainty",
    "UncertaintySource",
    "UncertaintyAggregator",
    # Provenance
    "ProvenanceEvent",
    "KnowledgeProvenance",
    # Validation
    "ValidationResult",
    "ValidationFailure",
    "KnowledgeValidation",
    "KnowledgeValidationEngine",
    # Health
    "KnowledgeHealthMetrics",
    "KnowledgeHealthInspector",
    # Diagnostics
    "DiagnosticFinding",
    "KnowledgeDiagnosticReport",
    "KnowledgeDiagnosticsEngine",
]