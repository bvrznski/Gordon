# Spatial Reasoning Shared Contracts - Phase 7.9
# =============================================

"""
Shared contract types for the spatial reasoning subsystem.

This module provides canonical implementations of all spatial reasoning contracts:

    SpatialDescriptor          - Metadata about spatial reasoning operations
    SpatialEntitySet           - Set of participating entities and constraints
    GeometryPipeline           - Geometric reasoning pipeline result
    TopologyAnalysis           - Topological analysis result
    CoordinateTransformation   - Coordinate transformation between frames
    NavigationSemantics        - Navigation analysis result
    SpatialConsistency         - Consistency validation result
    SpatialRefinement          - Model refinement record
    SpatialFailure             - Failure record for spatial sessions
    SpatialGovernance          - Governance evaluation
    SpatialHealth              - Health metrics
    SpatialDiagnostics         - Diagnostics records

Spatial reasoning operates over explicit entities and produces deterministic,
inspectable results independent of perception or motion execution.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.descriptor import (
    SpatialDescriptor,
    SpatialMode,
    SpatialLifecycle,
    SpatialEntitySetIdentity,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.entity_set import (
    SpatialEntitySet,
    SpatialEntity,
    EntityKind,
    GeometryType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.geometry_pipeline import (
    GeometryPipeline,
    GeometricMeasurement,
    PropertyComputation,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.topology import (
    TopologyAnalysis,
    TopologicalGraph,
    ConnectivityKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.transformations import (
    CoordinateTransformation,
    TransformMatrix,
    ReferenceFrame,
    FrameType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.navigation import (
    NavigationSemantics,
    ReachableRegion,
    ObstacleSet,
    TraversabilityAnalysis,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.consistency import (
    SpatialConsistency,
    ConsistencyFinding,
    ConsistencyType,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.refinement import (
    SpatialRefinement,
    RefinementChange,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.validation import (
    SpatialValidation,
    ValidationResult,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.failure import (
    SpatialFailure,
    FailureKind,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.governance import (
    SpatialGovernance,
    GovernanceFinding,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.health import (
    SpatialHealth,
    HealthMetric,
)

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared.diagnostics import (
    SpatialDiagnostics,
    DiagnosticRecord,
)

__all__ = [
    # Descriptor
    "SpatialDescriptor",
    "SpatialMode", 
    "SpatialLifecycle",
    "SpatialEntitySetIdentity",
    
    # Entity Set
    "SpatialEntitySet",
    "SpatialEntity",
    "EntityKind",
    "GeometryType",
    
    # Geometry Pipeline
    "GeometryPipeline",
    "GeometricMeasurement",
    "PropertyComputation",
    
    # Topology Analysis
    "TopologyAnalysis", 
    "TopologicalGraph",
    "ConnectivityKind",
    
    # Coordinate Transformation
    "CoordinateTransformation",
    "TransformMatrix",
    "ReferenceFrame",
    "FrameType",
    
    # Navigation Semantics
    "NavigationSemantics",
    "ReachableRegion",
    "ObstacleSet",
    "TraversabilityAnalysis",
    
    # Consistency
    "SpatialConsistency",
    "ConsistencyFinding",
    "ConsistencyType",
    
    # Refinement
    "SpatialRefinement",
    "RefinementChange",
    
    # Validation
    "SpatialValidation",
    "ValidationResult",
    
    # Failure
    "SpatialFailure",
    "FailureKind",
    
    # Governance
    "SpatialGovernance",
    "GovernanceFinding",
    
    # Health
    "SpatialHealth",
    "HealthMetric",
    
    # Diagnostics
    "SpatialDiagnostics",
    "DiagnosticRecord",
]
