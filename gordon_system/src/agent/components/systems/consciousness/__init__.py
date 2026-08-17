# Gordon Phase 5.7.9-T: Consciousness System
# ===============================================================================

"""
Consciousness System Package

Canonical implementation of the Consciousness capability as a first-class
system component.
"""

__version__ = "5.7.9-T"

__name__ = "gordon.agent.components.systems.consciousness"
"""Fully qualified package name (system path)."""

SYSTEM_ID = "system.consciousness"
"""Canonical system identifier."""

CAPABILITY_ID = "capability.consciousness"
"""Emergent capability identifier."""

IS_SYSTEM = True
"""Flag indicating this is a system implementation."""

EMERGENT_CAPABILITY = True
"""Flag indicating this system provides an emergent composite capability."""

# Relative imports from internal modules
from .config import ConsciousnessConfiguration
from .constants import (
    ContextState,
    ContributionKind,
    DegradationMode,
    HealthState,
    QueryMode,
    TransitionStatus,
)
from .exceptions import (
    ConsciousnessUnavailable,
    ConsciousnessNotReady,
    InvalidContribution,
    InvalidProjection,
    UnknownSource,
    DuplicateSource,
    UnknownExtension,
    DuplicateExtension,
    ExtensionDependencyCycle,
    SourceGenerationMismatch,
    ContextTransitionConflict,
    ContextPublicationFailure,
)
from .types import (
    ContributionId,
    ProjectionId,
    TransitionId,
    CorrelationId,
    CausationId,
    PrivacyClassification,
    TrustClassification,
)
from .identities import (
    ConsciousnessCapabilityId,
    ContextId,
    ContextGeneration,
    SourceId,
    ExtensionId,
)
from .contracts import (
    CurrentContextSnapshot,
    CurrentContextReference,
    ContributionEnvelope,
    ProjectionEnvelope,
    ContextTransition,
    TransitionResult,
    QueryRequest,
    ConsumerViewFilter,
    DiagnosticsSnapshot,
    HealthSnapshot,
)
from .registry import SourceRegistry, ExtensionRegistry
from .facade import ConsciousnessFacade

__all__: tuple[str, ...] = (
    "SYSTEM_ID",
    "CAPABILITY_ID",
    "IS_SYSTEM",
    "EMERGENT_CAPABILITY",
    "__version__",
    # Configuration
    "ConsciousnessConfiguration",
    # Constants and enums
    "ContextState",
    "ContributionKind",
    "DegradationMode",
    "HealthState",
    "QueryMode",
    "TransitionStatus",
    # Exceptions
    "ConsciousnessUnavailable",
    "ConsciousnessNotReady",
    "InvalidContribution",
    "InvalidProjection",
    "UnknownSource",
    "DuplicateSource",
    "UnknownExtension",
    "DuplicateExtension",
    "ExtensionDependencyCycle",
    "SourceGenerationMismatch",
    "ContextTransitionConflict",
    "ContextPublicationFailure",
    # Types
    "ContributionId",
    "ProjectionId",
    "TransitionId",
    "CorrelationId",
    "CausationId",
    "PrivacyClassification",
    "TrustClassification",
    # Identities
    "ConsciousnessCapabilityId",
    "ContextId",
    "ContextGeneration",
    "SourceId",
    "ExtensionId",
    # Contracts
    "CurrentContextSnapshot",
    "CurrentContextReference",
    "ContributionEnvelope",
    "ProjectionEnvelope",
    "ContextTransition",
    "TransitionResult",
    "QueryRequest",
    "ConsumerViewFilter",
    "DiagnosticsSnapshot",
    "HealthSnapshot",
    # Registries
    "SourceRegistry",
    "ExtensionRegistry",
    # Public facade
    "ConsciousnessFacade",
)