# Legal Reasoning Shared Components - Phase 7.47 Part 1
# ======================================================

"""
Shared components for Legal Reasoning subsystem.

This module exports the canonical contracts governing:
    - legal sessions and descriptors;
    - legal sets and pipelines;
    - jurisdiction identification;
    - legal source discovery;
    - obligation analysis;
    - rights analysis;
    - compliance assessment;
    - validation;
    - governance;
    - evolution tracking;
    - failure handling;
    - diagnostics and health monitoring.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.descriptor import (
    LegalDescriptor,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.legal_set import (
    LegalSet,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.pipeline import (
    LegalPipeline,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.jurisdictions import (
    JurisdictionAnalysis,
    JurisdictionManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.statutes import (
    StatuteAnalysis,
    StatuteManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.regulations import (
    RegulationAnalysis,
    RegulationManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.precedents import (
    PrecedentAnalysis,
    PrecedentManagement,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.obligations import (
    Obligation,
    ObligationAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.rights import (
    Right,
    RightsAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.compliance import (
    ComplianceAssessment,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.validation import (
    ValidationResult,
    ValidationSession,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.governance import (
    GovernanceEvaluation,
    GovernanceSession,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.evolution import (
    LegalEvolution,
    EvolutionManager,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.failure import (
    LegalFailure,
    FailureManager,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.diagnostics import (
    DiagnosticReport,
    HealthMetrics,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.legal.shared.health import (
    HealthStatus,
    HealthMonitor,
)

__all__ = [
    # Core contracts
    "LegalDescriptor",
    "LegalSet",
    "LegalPipeline",
    # Analysis modules
    "JurisdictionAnalysis",
    "JurisdictionManagement",
    "StatuteAnalysis",
    "StatuteManagement",
    "RegulationAnalysis",
    "RegulationManagement",
    "PrecedentAnalysis",
    "PrecedentManagement",
    # Rights and obligations
    "Obligation",
    "ObligationAnalysis",
    "Right",
    "RightsAnalysis",
    # Compliance
    "ComplianceAssessment",
    # Validation and governance
    "ValidationResult",
    "ValidationSession",
    "GovernanceEvaluation",
    "GovernanceSession",
    # Evolution and failure tracking
    "LegalEvolution",
    "EvolutionManager",
    "LegalFailure",
    "FailureManager",
    # Diagnostics and health
    "DiagnosticReport",
    "HealthMetrics",
    "HealthStatus",
    "HealthMonitor",
]

