# Default Network Package
# =======================

"""
Gordon's internally oriented cognitive coordination network scaffold.

The DefaultNetwork coordinates internally oriented cognitive processes,
including memory-driven association, reflection, autobiographical integration,
prospection, simulation, incubation, and narrative integration.

Architectural Role:
    Internally oriented associative/integrative coordination
    
Public API (Phase 4.3):
    - DefaultNetwork: Main orchestration class (primary facade)
    - DefaultNetworkConfig: Immutable configuration
    - DefaultInput: Canonical input contract  
    - DefaultOutput: Canonical output assessment/proposal contract
    - DefaultState: Bounded computational state snapshot

Computational Model (Phase 4.3):
    - InternalAttentionProposal: Coordinated internal attention
    - AssociationProposal: Memory-driven associative activation
    - ReflectionProposal: Self-referential processing candidates
    - SimulationProposal: Prospective/counterfactual simulation candidates
    - NarrativeIntegrationProposal: Narrative continuity proposals
    - UnresolvedGoalProposal: Goal resurfacing and incubation candidates

Runtime-Neutral (Phase 4.3.12):
    - DefaultNetworkRequest: Immutable request contract
    - DefaultNetworkInputs: Immutable inputs for processing cycle  
    - DefaultNetworkResult: Immutable result from coordination
    - DefaultNetworkState: Immutable state snapshot
    
This package does NOT:
    - Own or mutate Memory state
    - Own or mutate Consciousness state  
    - Authorize action or execution
    - Schedule threads or manage runtime state
    - Implement cognitive algorithms (deferred to subsystems)
"""

from __future__ import annotations

from .__meta__ import __version__

# =============================================================================
# PHASE 4.3: Canonical Exports
# =============================================================================

# Types and contracts (Phase 4.3 core types)
from .types import (
    DefaultNetworkId,
    InputId,
    OutputId,
    AssessmentId,
    InternalAttentionProposal,
    AssociationProposal,
    MemoryReactivationProposal,
    ReflectionProposal,
    SimulationProposal,
    ProspectionProposal,
    NarrativeIntegrationProposal,
    UnresolvedGoalProposal,
    IncubationProposal,
    ContextReintegrationProposal,
    DefaultNetworkAssessment,
)

# Configuration
from .config import (
    DefaultNetworkConfig,
)

# Inputs and outputs (Phase 4.3 legacy types)
from .inputs import (
    DefaultInput,
    DefaultInputContext,
    DefaultProvenance,
    DefaultNetworkInputs,  # Phase 4.3.12 addition
)

# State management (Phase 4.3.12 - new canonical structure)
from .state import (
    DefaultNetworkState,
    DefaultNetworkTransition,
)

# Outputs and proposals
from .outputs import (
    DefaultOutput,
    DefaultProposalSet,
)

# Activation tracking
from .activation import (
    DefaultActivation,
    ActivationSource,
    InternalOrientationScore,
)

# Policy decisions
from .policy import (
    DefaultPolicy,
    PolicyDecision,
)

# Semantic boundary ports
from .ports import (
    MemoryProjectionPort,
    ConsciousnessProjectionPort,
    CognitionRequestPort,
    KnowledgeProjectionPort,
    GoalProjectionPort,
    DefaultNetworkOutputPort,
)

# Diagnostics and health
from .diagnostics import (
    DiagnosticEvent,
    NetworkDiagnostics,
    DiagnosticsCollector,
    DiagnosticsSink,
)

from .health import (
    HealthState,
    HealthCheckResult,
)

# Validation
from .validation import (
    ValidationResult,
    validate_input,
    validate_output,
    validate_assessment,
    validate_state_consistency,
)

# Exceptions
from .exceptions import (
    DefaultNetworkError,
    ValidationError,
    ConfigurationError,
    StateError,
)

# =============================================================================
# PHASE 4.3.12: Runtime-Neutral Contracts (New)
# =============================================================================

# Request models
from .request import (
    DefaultNetworkRequest,
    DefaultNetworkRequestId,
    CorrelationId,
    CausationId,
    SemanticTime,
    InternalContextReference,
    InternalEpisodeReference,
    ExecutionThreadReference,
    ExecutionCycleReference,
)

# Result models  
from .result import (
    DefaultNetworkResult,
    DefaultNetworkPathSelection,
    DefaultNetworkProduct,
    DefaultNetworkProposal,
    DefaultNetworkExternalRequest,
)

# State-based result types
from .state import (
    DefaultNetworkOutcome,
    DefaultNetworkContinuation,
    DefaultNetworkDiagnostics,
)

# Path abstraction (Phase 4.3.12)
from .paths import (
    DefaultNetworkPathHandler,
    DefaultNetworkPathContext,
    DefaultNetworkPathResult,
    DefaultNetworkPathRegistry,
    DefaultNetworkPathSelector,
    DefaultNetworkPathSelection as PathSelectionRecord,  # alias
    create_default_path_registry,
    create_default_path_selector,
)

# =============================================================================
# PRIMARY FACADE
# =============================================================================

from .network import (
    DefaultNetwork,
)

# Architecture tree for navigation  
from .__tree__ import DefaultArchitecture

__all__ = [
    "__version__",
    
    # Network orchestration (primary facade)
    "DefaultNetwork",
    
    # Architecture navigation
    "DefaultArchitecture",
    
    # Configuration
    "DefaultNetworkConfig",
    
    # Phase 4.3 Outputs (legacy - kept for compatibility)
    "DefaultOutput",
    "DefaultProposalSet",
    
    # State management
    "DefaultNetworkState",
    "DefaultNetworkTransition",
    
    # Phase 4.3.12 inputs/outputs (runtime-neutral)
    "DefaultNetworkInputs",
    "DefaultNetworkResult",
    "DefaultNetworkPathSelection",  # alias
    "DefaultNetworkProduct",
    "DefaultNetworkProposal", 
    "DefaultNetworkExternalRequest",
    "DefaultNetworkOutcome",
    "DefaultNetworkContinuation",
    "DefaultNetworkDiagnostics",
    
    # Path abstraction (Phase 4.3.12)
    "DefaultNetworkPathHandler",
    "DefaultNetworkPathContext",
    "DefaultNetworkPathResult",
    "DefaultNetworkPathRegistry",
    "DefaultNetworkPathSelector",
    "create_default_path_registry",
    "create_default_path_selector",
    
    # Types
    "DefaultNetworkId",
    "InputId",
    "OutputId", 
    "AssessmentId",
    "InternalAttentionProposal",
    "AssociationProposal",
    "MemoryReactivationProposal",
    "ReflectionProposal",
    "SimulationProposal",
    "ProspectionProposal",
    "NarrativeIntegrationProposal",
    "UnresolvedGoalProposal",
    "IncubationProposal",
    "ContextReintegrationProposal",
    "DefaultNetworkAssessment",
    
    # Activation and policy
    "DefaultActivation", 
    "ActivationSource",
    "InternalOrientationScore",
    "DefaultPolicy",
    "PolicyDecision",
    
    # Ports (semantic boundary)
    "MemoryProjectionPort",
    "ConsciousnessProjectionPort",
    "CognitionRequestPort",
    "KnowledgeProjectionPort",
    "GoalProjectionPort",
    "DefaultNetworkOutputPort",
    
    # Diagnostics and health
    "DiagnosticEvent",
    "NetworkDiagnostics",
    "DiagnosticsCollector", 
    "DiagnosticsSink",
    "HealthState",
    "HealthCheckResult",
    
    # Validation
    "ValidationResult",
    "validate_input",
    "validate_output",
    "validate_assessment",
    "validate_state_consistency",
    
    # Exceptions
    "DefaultNetworkError",
    "ValidationError",
    "ConfigurationError",
    "StateError",
]