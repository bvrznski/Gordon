# Gordon Phase 5.7.8-I: Conscious Integration Package
# ===============================================================================

"""
Conscious Integration - Composite context coordination for Gordon's consciousness capability.

The integration layer coordinates committed immutable references from:
    - Experiential Field
    - Intentional Context  
    - Temporal Context
    - Presence
    - Awareness
    - Perspective
    - Situated World

It validates cross-engine compatibility, generation alignment, and publishes
the composite conscious context snapshot.

This is NOT a universal consciousness manager. It does not:
    - Own engine internals or semantics
    - Reason about conflicts
    - Authorize actions
    - Determine truth
"""

from .constants import (
    CONSISTENCY_LEVEL_STRICT,
    REQUIRED_ENGINE_IDS,
    OPTIONAL_ENGINE_IDS,
    INTEGRATION_STATE_IDLE,
    INTEGRATION_STATE_COLLECTING_SNAPSHOTS,
    INTEGRATION_STATE_VALIDATING,
    INTEGRATION_STATE_COMPOSING,
    INTEGRATION_STATE_PUBLISHING,
)

from .types import (
    EngineSnapshotReference,
    EngineGenerationMap,
    UnresolvedReference,
    CompositeSnapshot,
    IntegrationTransition,
    IntegrationResult,
)

from gordon.agent.components.systems.consciousnessdependencies import (
    EngineDependencyOrder,
    DependencyGraph,
    build_default_dependency_graph,
)

from gordon.agent.components.systems.consciousnessvalidation import (
    ValidationResult,
    CrossEngineReference,
    InvariantCheckResult,
    CrossEngineValidator,
)

from gordon.agent.components.systems.consciousnesscomposition import (
    CompositionResult,
    CompositeSnapshotBuilder,
    compose_initial_snapshot,
)

from gordon.agent.components.systems.consciousnesscoordinator import (
    IntegrationRequest,
    IntegrationCoordinator,
    ValidationOutcome,
    AlignmentValidationResult,
)

from gordon.agent.components.systems.consciousnesshealth import (
    EngineHealth,
    CompositeHealthSnapshot,
    CompositeHealthAggregator,
    compute_composite_health_state,
)

from gordon.agent.components.systems.consciousnessdiagnostics import (
    CompositeDiagnosticsSnapshot,
    CompositeDiagnosticsBuilder,
)

__all__ = [
    # Constants
    "CONSISTENCY_LEVEL_STRICT",
    "REQUIRED_ENGINE_IDS",
    "OPTIONAL_ENGINE_IDS",
    "INTEGRATION_STATE_IDLE",
    "INTEGRATION_STATE_COLLECTING_SNAPSHOTS",
    "INTEGRATION_STATE_VALIDATING",
    "INTEGRATION_STATE_COMPOSING",
    "INTEGRATION_STATE_PUBLISHING",
    
    # Types
    "EngineSnapshotReference",
    "EngineGenerationMap",
    "UnresolvedReference",
    "CompositeSnapshot",
    "IntegrationTransition",
    "IntegrationResult",
    
    # Dependencies
    "EngineDependencyOrder",
    "DependencyGraph",
    "build_default_dependency_graph",
    
    # Validation
    "ValidationResult",
    "CrossEngineReference",
    "InvariantCheckResult",
    "CrossEngineValidator",
    
    # Composition
    "CompositionResult",
    "CompositeSnapshotBuilder",
    "compose_initial_snapshot",
    
    # Coordinator
    "IntegrationRequest",
    "IntegrationCoordinator",
    "ValidationOutcome",
    "AlignmentValidationResult",
    
    # Health
    "EngineHealth",
    "CompositeHealthSnapshot",
    "CompositeHealthAggregator",
    "compute_composite_health_state",
    
    # Diagnostics
    "CompositeDiagnosticsSnapshot",
    "CompositeDiagnosticsBuilder",
]