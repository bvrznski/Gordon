# Knowledge Capability - Phase 6.0
# =================================

"""
Knowledge Capability: Semantic organization layer for Gordon's cognitive engine.

The Knowledge Capability provides semantic structure upon which reasoning,
planning, and decision making operate. It is not a storage system nor a reasoning
system—it is the semantic substrate that transforms grounded evidence into stable,
revisable semantic structure.

Dependencies:
    - Perception (for current evidence)
    - Memory (for historical evidence)  
    - Knowledge-Perception Grounding (for present grounding)
    - Knowledge-Memory Integration (for historical grounding)

Responsibilities:
    - Semantic identity management
    - Provenance tracking
    - Validity assessment
    - Confidence/uncertainty representation
    - Revision management
    - Semantic scope definition
    - Authority establishment

Architecture Overview:
    Phase 6.0 - Knowledge Architecture       (this phase)
    Phase 6.1 - Knowledge Foundations        (semantic primitives)
    Phase 6.2 - Representations              (symbolic, vector, latent, hybrid)
    Phase 6.3 - Concepts                     (categories, abstraction, hierarchy)
    Phase 6.4 - Assertions                   (statements, evidence, justification)
    Phase 6.5 - Relations                    (structural, semantic, causal, etc.)
    Phase 6.6 - Beliefs                      (acceptance, confidence, revision)
    Phase 6.7 - Hypotheses                   (generation, comparison, falsification)
    Phase 6.8 - Models                       (physical, social, procedural, operational)
    Phase 6.9 - Skills                       (declarative, procedural, transfer)
    Phase 6.10 - Reality Representation       (entities, events, states, processes)
    Phase 6.11 - Knowledge Graph             (nodes, edges, indexing, traversal)
    Phase 6.12 - Semantic Revision           (merge, split, supersession, migration)
    Phase 6.13 - Knowledge Governance        (validation, consistency, health)
"""

from __future__ import annotations

# Core foundations
from gordon_system.src.agent.components.systems.knowledge.foundations import (
    IdentitySource,
    IdentityResolution,
    SemanticIdentity,
    IdentityTracker,
    IdentityValidator,
    
    ProvenanceAction,
    ProvenanceEvent,
    ProvenanceTrail,
    ProvenanceValidator,
    
    ValidityState,
    EvidenceKind,
    ValidityEvidence,
    ValidityAssessment,
    ValidityEngine,
    
    ConfidenceSource,
    SemanticConfidence,
    ConfidenceAggregator,
    
    UncertaintySource,
    SemanticUncertainty,
    UncertaintyAggregator,
    
    RevisionEventType,
    RevisionEvent,
    RevisionHistory,
    RevisionManager,
    
    ScopeDomain,
    ScopeBoundary,
    SemanticScope,
    ScopeValidator,
    
    AuthorityLevel,
    AuthoritySource,
    AuthorityAssessment,
    AuthorityValidator,
)

# Shared artifacts (imported from Phase 5.4 shared)
from gordon_system.src.agent.components.systems.knowledge.shared import (
    KnowledgeAssertion,
    AssertionState,
    AssertionValidator,
    KnowledgeProposition,
    PropositionState,
    PropositionBuilder,
    KnowledgeConcept,
    ConceptRelationType,
    ConceptHierarchyBuilder,
    KnowledgeRelation,
    RelationKind,
    RelationBuilder,
    KnowledgeModel,
    ModelScope,
    ModelBuilder,
    KnowledgeBelief,
    BeliefState,
    BeliefValidator,
    KnowledgeEvidence,
    EvidenceKind as SharedEvidenceKind,
    EvidenceChain,
    KnowledgeJustification,
    JustificationKind,
    JustificationBuilder,
    KnowledgeConfidence,
    ConfidenceSource as SharedConfidenceSource,
    ConfidenceAggregator as SharedConfidenceAggregator,
    KnowledgeUncertainty,
    UncertaintySource as SharedUncertaintySource,
    UncertaintyAggregator as SharedUncertaintyAggregator,
    ProvenanceEvent as SharedProvenanceEvent,
    KnowledgeProvenance,
    ValidationResult,
    ValidationFailure,
    KnowledgeValidation,
    KnowledgeValidationEngine,
    KnowledgeHealthMetrics,
    KnowledgeHealthInspector,
    DiagnosticFinding,
    KnowledgeDiagnosticReport,
    KnowledgeDiagnosticsEngine,
)

__all__ = [
    # Foundations
    "IdentitySource",
    "IdentityResolution",
    "SemanticIdentity",
    "IdentityTracker",
    "IdentityValidator",
    "ProvenanceAction",
    "ProvenanceEvent",
    "ProvenanceTrail",
    "ProvenanceValidator",
    "ValidityState",
    "EvidenceKind",
    "ValidityEvidence",
    "ValidityAssessment",
    "ValidityEngine",
    "ConfidenceSource",
    "SemanticConfidence",
    "ConfidenceAggregator",
    "UncertaintySource",
    "SemanticUncertainty",
    "UncertaintyAggregator",
    "RevisionEventType",
    "RevisionEvent",
    "RevisionHistory",
    "RevisionManager",
    "ScopeDomain",
    "ScopeBoundary",
    "SemanticScope",
    "ScopeValidator",
    "AuthorityLevel",
    "AuthoritySource",
    "AuthorityAssessment",
    "AuthorityValidator",
    # Shared artifacts
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
    "SharedEvidenceKind",
    "EvidenceChain",
    "KnowledgeJustification",
    "JustificationKind",
    "JustificationBuilder",
    "KnowledgeConfidence",
    "SharedConfidenceSource",
    "SharedConfidenceAggregator",
    "KnowledgeUncertainty",
    "SharedUncertaintySource",
    "SharedUncertaintyAggregator",
    "SharedProvenanceEvent",
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