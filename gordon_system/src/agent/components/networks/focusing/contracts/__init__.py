# Focusing Network Contracts - Phase 4.2.8
# =========================================

"""
Contract interfaces for the FocusingNetwork.

This package provides the complete architectural integration layer through which
the Focusing Network communicates with the rest of Gordon while preserving
complete decoupling.

ARCHITECTURE:
    Core → Execution → Capabilities → Attention Capability → Focusing Contracts → Focusing Network

DEPENDENCY DIRECTION:
    External systems (Attention Capability, Executive, etc.) depend on contracts.
    FocusingNetwork depends ONLY on contracts, never implementations.

VERSION: 1.0.0
COMPATIBILITY: backward
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

# =============================================================================
# VERSIONING CONSTANTS - Phase 4.2.8
# =============================================================================

CONTRACTS_VERSION = "1.0.0"
COMPATIBILITY_POLICY = "backward"  # Backward compatible with future consumers
DEPRECATION_POLICY = "three_releases"  # Deprecated items removed after 3 releases
EXTENSION_STRATEGY = "additive_only"  # New functionality added without breaking

# =============================================================================
# INPUT CONTRACTS - Network consumes these (providers)
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.inputs import (
    FocusCandidateProvider,
    FocusContextProvider,
    FocusStateProvider,
    ObjectiveProvider,
    WorkspaceProjectionProvider,
    WorkingMemoryProjectionProvider,
    AlertingAssessmentProvider,
    PolicyProjectionProvider,
    ConfigurationProvider,
)

# =============================================================================
# OUTPUT CONTRACTS - Network provides these (consumers)
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.outputs import (
    FocusAssessmentConsumer,
    PriorityAssessmentConsumer,
    CompetitionAssessmentConsumer,
    PrecisionAssessmentConsumer,
    PersistenceAssessmentConsumer,
    AllocationRecommendationConsumer,
    BiasAssessmentConsumer,
    DiagnosticsConsumer,
)

# =============================================================================
# CONTEXT CONTRACTS - Carry projections without ownership
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.context import (
    FocusComputationContext,
    ExecutionProjection,
    PolicyProjection,
    ResourceProjection,
    HistoricalProjection,
)

# =============================================================================
# STATE CONTRACTS - Expose immutable state views (no mutation)
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.state import (
    FocusStateView,
    PriorityStateView,
    PersistenceStateView,
    PrecisionStateView,
    AllocationStateView,
    BiasStateView,
    DiagnosticsView,
)

# =============================================================================
# CONFIGURATION CONTRACTS - Provide runtime-independent config
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.configuration import (
    FocusConfigurationProvider,
    ConfigurationView,
    ConfigurationSnapshot,
    ConfigurationValidator,
    ConfigurationVersion,
)

# =============================================================================
# VALIDATION CONTRACTS - Define expectations without implementation
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.validation import (
    FocusValidationContract,
    AssessmentValidator,
    ContextValidator,
    StateValidator,
    ValidationReport,
)

# =============================================================================
# DIAGNOSTICS CONTRACTS - Observational only (no computation)
# =============================================================================

from gordon_system.src.agent.components.networks.focusing.contracts.diagnostics import (
    DiagnosticsSink,
    PipelineTraceConsumer,
    AssessmentTraceConsumer,
    StateTraceConsumer,
    PerformanceTraceConsumer,
    ExplainabilityConsumer,
)

__all__ = [
    # =============================================================================
    # VERSIONING
    # =============================================================================
    
    "CONTRACTS_VERSION",
    "COMPATIBILITY_POLICY",
    "DEPRECATION_POLICY",
    "EXTENSION_STRATEGY",
    
    # =============================================================================
    # INPUT CONTRACTS (Providers - Network consumes)
    # =============================================================================
    
    "FocusCandidateProvider",
    "FocusContextProvider",
    "FocusStateProvider",
    "ObjectiveProvider",
    "WorkspaceProjectionProvider",
    "WorkingMemoryProjectionProvider",
    "AlertingAssessmentProvider",
    "PolicyProjectionProvider",
    "ConfigurationProvider",
    
    # =============================================================================
    # OUTPUT CONTRACTS (Consumers - Network produces)
    # =============================================================================
    
    "FocusAssessmentConsumer",
    "PriorityAssessmentConsumer",
    "CompetitionAssessmentConsumer",
    "PrecisionAssessmentConsumer",
    "PersistenceAssessmentConsumer",
    "AllocationRecommendationConsumer",
    "BiasAssessmentConsumer",
    "DiagnosticsConsumer",
    
    # =============================================================================
    # CONTEXT CONTRACTS (Projections without ownership)
    # =============================================================================
    
    "FocusComputationContext",
    "ExecutionProjection",
    "PolicyProjection",
    "ResourceProjection",
    "HistoricalProjection",
    
    # =============================================================================
    # STATE CONTRACTS (Immutable views - no mutation)
    # =============================================================================
    
    "FocusStateView",
    "PriorityStateView",
    "PersistenceStateView",
    "PrecisionStateView",
    "AllocationStateView",
    "BiasStateView",
    "DiagnosticsView",
    
    # =============================================================================
    # CONFIGURATION CONTRACTS
    # =============================================================================
    
    "FocusConfigurationProvider",
    "ConfigurationView",
    "ConfigurationSnapshot",
    "ConfigurationValidator",
    "ConfigurationVersion",
    
    # =============================================================================
    # VALIDATION CONTRACTS
    # =============================================================================
    
    "FocusValidationContract",
    "AssessmentValidator",
    "ContextValidator",
    "StateValidator",
    "ConfigurationValidator",
    "ValidationReport",
    
    # =============================================================================
    # DIAGNOSTICS CONTRACTS (Observational only)
    # =============================================================================
    
    "DiagnosticsSink",
    "PipelineTraceConsumer",
    "AssessmentTraceConsumer",
    "StateTraceConsumer",
    "PerformanceTraceConsumer",
    "ExplainabilityConsumer",
]