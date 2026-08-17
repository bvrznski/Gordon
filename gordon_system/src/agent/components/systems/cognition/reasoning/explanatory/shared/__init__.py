# Explanation Shared - Phase 7.14
# ===============================

"""
Shared types and interfaces for explanatory reasoning.

This module provides the canonical contracts for:
    - Explanations
    - Evidence
    - Justifications  
    - Narratives
    - Alternatives
    - Refinements
    - Validation
    - Governance
    - Health metrics
    - Diagnostics
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.descriptor import (
    ExplanationDescriptor,
    ExplanationSessionIdentity,
    ExplanationMode,
    ExplanationLifecycle,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.evidence import (
    EvidenceIdentity,
    ExplanationEvidence,
    EvidenceAggregation,
    EvidenceKind,
    EvidenceRelevance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.justification import (
    JustificationIdentity,
    JustificationStep,
    JustificationAnalysis,
    JustificationKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.explanation_set import (
    ExplanationSetIdentity,
    Claim,
    ExplanationSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.construction import (
    ConstructionIdentity,
    ExplanationStrategy,
    ExplanationConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.narrative import (
    NarrativeIdentity,
    NarrativeStep,
    NarrativeConstruction,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.alternatives import (
    AlternativeIdentity,
    CandidateExplanation,
    AlternativeExplanationAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.refinement import (
    RefinementIdentity,
    ExplanationRefinement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.validation import (
    ValidationIdentity,
    ValidationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.failure import (
    FailureIdentity,
    ExplanationFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.governance import (
    GovernanceIdentity,
    GovernanceFinding,
    ExplanationGovernance,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.health import (
    HealthMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.explanatory.shared.diagnostics import (
    DiagnosticRecord,
    ExplanationDiagnostics,
)


__all__ = [
    # Descriptor
    "ExplanationDescriptor",
    "ExplanationSessionIdentity",
    "ExplanationMode",
    "ExplanationLifecycle",
    # Evidence
    "EvidenceIdentity",
    "ExplanationEvidence",
    "EvidenceAggregation",
    "EvidenceKind",
    "EvidenceRelevance",
    # Justification
    "JustificationIdentity",
    "JustificationStep",
    "JustificationAnalysis",
    "JustificationKind",
    # Explanation Set
    "ExplanationSetIdentity",
    "Claim",
    "ExplanationSet",
    # Construction
    "ConstructionIdentity",
    "ExplanationStrategy",
    "ExplanationConstruction",
    # Narrative
    "NarrativeIdentity",
    "NarrativeStep",
    "NarrativeConstruction",
    # Alternatives
    "AlternativeIdentity",
    "CandidateExplanation",
    "AlternativeExplanationAnalysis",
    # Refinement
    "RefinementIdentity",
    "ExplanationRefinement",
    # Validation
    "ValidationIdentity",
    "ValidationResult",
    # Failure
    "FailureIdentity",
    "ExplanationFailure",
    "FailureKind",
    # Governance
    "GovernanceIdentity",
    "GovernanceFinding",
    "ExplanationGovernance",
    # Health
    "HealthMetrics",
    # Diagnostics
    "DiagnosticRecord",
    "ExplanationDiagnostics",
]