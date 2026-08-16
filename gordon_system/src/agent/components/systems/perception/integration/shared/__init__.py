# Perception Integration Shared - Phase 5.2.3
# ===========================================

"""
Shared contracts and types for perception integration.
"""

from gordon_system.src.agent.components.systems.perception.integration.shared.request import (
    PerceptionIntegrationRequest,
    IntegrationScope,
    BindingPolicy,
    FusionPolicy,
    ConfidencePolicy,
    UncertaintyPolicy,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.result import (
    PerceptionIntegrationResult,
    IntegrationStatus,
    IntegrationOutcome,
    CorrespondenceRecord,
    BindingRecord,
    FusionRecord,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.session import (
    PerceptionIntegrationSession,
    IntegrationHealth as SessionHealth,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.evidence_group import (
    PerceptualEvidenceGroup,
    GroupingBasis,
    DependencySummary,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.source_dependency import (
    SourceDependencyAssessment,
    DependencyKind,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.confidence import (
    IntegratedPerceptualConfidence,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.uncertainty import (
    IntegratedPerceptualUncertainty,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.conflict import (
    PerceptualConflict,
    ConflictKind,
    PerceptualConflictAssessment,
    PreservedPerceptualConflict,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.partial import (
    PartialPerceptionIntegration,
    MissingPerceptualEvidence,
    IntegrationEvidenceRequirement,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.ambiguity import (
    AmbiguousPerceptionIntegration,
    CorrespondenceAlternative,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.replay import (
    PerceptionIntegrationReplay,
    PerceptionIntegrationValidation,
)
from gordon_system.src.agent.components.systems.perception.integration.shared.health import (
    PerceptionIntegrationHealth,
    PerceptionIntegrationDiagnostics,
)

__all__ = [
    # Request
    "PerceptionIntegrationRequest",
    "IntegrationScope",
    "BindingPolicy",
    "FusionPolicy",
    "ConfidencePolicy",
    "UncertaintyPolicy",
    # Result
    "PerceptionIntegrationResult",
    "IntegrationStatus",
    "IntegrationOutcome",
    "CorrespondenceRecord",
    "BindingRecord",
    "FusionRecord",
    # Session
    "PerceptionIntegrationSession",
    "SessionHealth",
    # Evidence Grouping
    "PerceptualEvidenceGroup",
    "GroupingBasis",
    "DependencySummary",
    # Source Dependency
    "SourceDependencyAssessment",
    "DependencyKind",
    # Confidence & Uncertainty
    "IntegratedPerceptualConfidence",
    "IntegratedPerceptualUncertainty",
    # Conflict
    "PerceptualConflict",
    "ConflictKind",
    "PerceptualConflictAssessment",
    "PreservedPerceptualConflict",
    # Partial & Ambiguous Integration
    "PartialPerceptionIntegration",
    "MissingPerceptualEvidence",
    "IntegrationEvidenceRequirement",
    "AmbiguousPerceptionIntegration",
    "CorrespondenceAlternative",
    # Replay & Validation
    "PerceptionIntegrationReplay",
    "PerceptionIntegrationValidation",
    # Health & Diagnostics
    "PerceptionIntegrationHealth",
    "PerceptionIntegrationDiagnostics",
]