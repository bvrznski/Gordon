# Systems - system-level infrastructure components
# ==================================================

"""
Systems module: System-level infrastructure components.

This module provides system-level components for:
    - Interaction contracts
    - Lifecycle management
    - State access and mutation
    - Security verification
"""

from __future__ import annotations

from .knowledge.shared import (
    # Assertion
    KnowledgeAssertion,
    AssertionState,
    AssertionValidator,
    # Proposition
    KnowledgeProposition,
    PropositionState,
    PropositionBuilder,
    # Concept
    KnowledgeConcept,
    ConceptRelationType,
    ConceptHierarchyBuilder,
    # Relation
    KnowledgeRelation,
    RelationKind,
    RelationBuilder,
    # Model
    KnowledgeModel,
    ModelScope,
    ModelBuilder,
    # Belief
    KnowledgeBelief,
    BeliefState,
    BeliefValidator,
    # Evidence
    KnowledgeEvidence,
    EvidenceKind,
    EvidenceChain,
    # Justification
    KnowledgeJustification,
    JustificationKind,
    JustificationBuilder,
    # Confidence
    KnowledgeConfidence,
    ConfidenceSource,
    ConfidenceAggregator,
    # Uncertainty
    KnowledgeUncertainty,
    UncertaintySource,
    UncertaintyAggregator,
    # Provenance
    ProvenanceEvent,
    KnowledgeProvenance,
    # Validation
    ValidationResult,
    ValidationFailure,
    KnowledgeValidation,
    KnowledgeValidationEngine,
    # Health
    KnowledgeHealthMetrics,
    KnowledgeHealthInspector,
    # Diagnostics
    DiagnosticFinding,
    KnowledgeDiagnosticReport,
    KnowledgeDiagnosticsEngine,
)

__all__ = [
    "KnowledgeAssertion",
    "AssertionState",
    "AssertionValidator",
    "KnowledgeProposition",
    "PropositionState",
    "PropositionBuilder",
    "KnowledgeConcept",
    "ConceptRelationType",
    "ConceptHierarchyBuilder",
    "KnowledgeRelation",
    "RelationKind",
    "RelationBuilder",
    "KnowledgeModel",
    "ModelScope",
    "ModelBuilder",
    "KnowledgeBelief",
    "BeliefState",
    "BeliefValidator",
    "KnowledgeEvidence",
    "EvidenceKind",
    "EvidenceChain",
    "KnowledgeJustification",
    "JustificationKind",
    "JustificationBuilder",
    "KnowledgeConfidence",
    "ConfidenceSource",
    "ConfidenceAggregator",
    "KnowledgeUncertainty",
    "UncertaintySource",
    "UncertaintyAggregator",
    "ProvenanceEvent",
    "KnowledgeProvenance",
    "ValidationResult",
    "ValidationFailure",
    "KnowledgeValidation",
    "KnowledgeValidationEngine",
    "KnowledgeHealthMetrics",
    "KnowledgeHealthInspector",
    "DiagnosticFinding",
    "KnowledgeDiagnosticReport",
    "KnowledgeDiagnosticsEngine",
]