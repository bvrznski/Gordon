# World-Model Reasoning Shared Components - Phase 7.44
# =====================================================

"""
Shared contracts and base classes for world-model reasoning.

This module provides canonical data models that define the world-model reasoning
interface:
    
    * descriptor.py     - World session and pipeline descriptors
    * entities.py       - Entity identity, state, and management
    * scenes.py         - Scene structure and analysis
    * dynamics.py       - State transitions and motion tracking
    * consistency.py    - Physical and causal consistency evaluation
    * evolution.py      - World revision history
    * validation.py     - Validation checks and results
    * failure.py        - Failure kinds and diagnostics
    * governance.py     - Governance findings and recommendations
    * health.py         - Health metrics and status
    * diagnostics.py    - Diagnostic events and logs
"""

from .descriptor import (
    WorldDescriptor,
    WorldKind,
    WorldState,
    WorldSet,
    WorldPipeline,
)

from .entities import (
    EntityIdentity,
    EntityState,
    EntityRelationship,
    EntityAnalysis,
    EntityManagement,
)

from .scenes import (
    SceneRegion,
    SceneObject,
    SceneTopologyGraph,
    SceneAnalysis,
    SceneManagement,
)

from .dynamics import (
    StateTransition,
    MotionTrack,
    CausalTransition,
    WorldDynamics,
    WorldDynamicsManagement,
)

from .consistency import (
    ConsistencyKind,
    ConsistencyState,
    ConsistencyViolation,
    ConsistencyMetric,
    WorldConsistency,
    WorldConsistencyManagement,
)

from .evolution import (
    EvolutionTrigger,
    WorldRevision,
    WorldEvolution,
)

from .validation import (
    ValidationKind,
    ValidationState,
    ValidationResult,
    WorldValidation,
)

from .failure import (
    FailureKind,
    WorldFailure,
)

from .governance import (
    GovernanceFinding,
    WorldGovernance,
)

from .health import (
    HealthMetric,
    WorldHealth,
)

from .diagnostics import (
    DiagnosticEvent,
    WorldDiagnostics,
)

__all__ = [
    "WorldDescriptor",
    "WorldKind",
    "WorldState",
    "WorldSet",
    "WorldPipeline",
    "EntityIdentity",
    "EntityState",
    "EntityRelationship",
    "EntityAnalysis",
    "EntityManagement",
    "SceneRegion",
    "SceneObject",
    "SceneTopologyGraph",
    "SceneAnalysis",
    "SceneManagement",
    "StateTransition",
    "MotionTrack",
    "CausalTransition",
    "WorldDynamics",
    "WorldDynamicsManagement",
    "ConsistencyKind",
    "ConsistencyState",
    "ConsistencyViolation",
    "ConsistencyMetric",
    "WorldConsistency",
    "WorldConsistencyManagement",
    "EvolutionTrigger",
    "WorldRevision",
    "WorldEvolution",
    "ValidationKind",
    "ValidationState",
    "ValidationResult",
    "WorldValidation",
    "FailureKind",
    "WorldFailure",
    "GovernanceFinding",
    "WorldGovernance",
    "HealthMetric",
    "WorldHealth",
    "DiagnosticEvent",
    "WorldDiagnostics",
]