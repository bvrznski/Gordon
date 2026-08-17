# Gordon Phase 5.7.9-T: Consciousness Capability Compatibility Layer
# ===============================================================================
#
# THIS IS A TEMPORARY COMPATIBILITY LAYER.
# The canonical implementation has moved to:
#     gordon.agent.components.systems.consciousness
#
# This file exists only to maintain import compatibility during migration.
# It should be removed once all consumers have migrated to the system path.

"""
Consciousness Capability Package - DEPRECATED

DEPRECATION NOTICE:
This package path is deprecated as of Phase 5.7.9-T.
The canonical implementation has moved to:

    gordon.agent.components.systems.consciousness

Please update your imports from:
    from agent.capabilities.consciousness import ...
To:
    from agent.components.systems.consciousness import ...

This compatibility layer will be removed in a future phase.
"""

from __future__ import annotations

# Re-export from the canonical system path
from gordon.agent.components.systems.consciousness import (
    ConsciousnessConfiguration,
    ContextState,
    ContributionKind,
    DegradationMode,
    HealthState,
    QueryMode,
    TransitionStatus,
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
    ContributionId,
    ProjectionId,
    TransitionId,
    CorrelationId,
    CausationId,
    PrivacyClassification,
    TrustClassification,
    ConsciousnessCapabilityId,
    ContextId,
    ContextGeneration,
    SourceId,
    ExtensionId,
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
    SourceRegistry,
    ExtensionRegistry,
    ConsciousnessFacade,
)

# Export the compatibility layer marker
__compatibility_layer__ = True

# Deprecated package name (keep for backwards compatibility)
__name__ = "gordon.agent.capabilities.consciousness"

__version__ = "5.7.9-T"
"""Package semantic version - compatibility layer for Phase 5.7.9-T migration."""

# Export __all__ to match the original interface
__all__: tuple[str, ...] = (
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

# ============================================================================
# DEPRECATION WARNINGS (optional - uncomment if needed)
# ============================================================================

import warnings


def _warn_deprecation(module_name: str) -> None:
    """Issue deprecation warning for module access."""
    warnings.warn(
        f"Import from '{module_name}' is deprecated. "
        f"Use 'gordon.agent.components.systems.consciousness' instead.",
        DeprecationWarning,
        stacklevel=2,
    )