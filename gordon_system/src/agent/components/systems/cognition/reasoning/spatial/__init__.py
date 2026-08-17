# Spatial Reasoning - Phase 7.9
# =============================

"""
Spatial Reasoning - Gordon's geometric cognition engine.

This module provides the spatial reasoning subsystem implementing:

    * Spatial representation (entities, reference frames)
    * Topological reasoning (connectivity, containment)
    * Geometric reasoning (distance, angle, orientation)
    * Navigation semantics (reachability, obstacles)
    * Coordinate transformations
    * Validation and governance

Spatial Reasoning models space. It does not perceive space directly.
Perception supplies observations; Spatial Reasoning interprets them.

Architectural position:

    Perception -> Knowledge -> World Model -> Spatial Reasoning ->
    Spatial Models -> Spatial Relations -> Reasoning Output

See also: Phase 7.9 Parts 2 and 3 for complete specification.
"""

from gordon_system.src.agent.components.systems.cognition.reasoning.spatial.shared import (
    # Core contracts
    SpatialDescriptor,
    SpatialMode,
    SpatialLifecycle,
    SpatialEntitySetIdentity,
    SpatialEntitySet,
    SpatialEntity,
    EntityKind,
    GeometryType,
    
    # Pipeline results
    GeometryPipeline,
    GeometricMeasurement,
    PropertyComputation,
    TopologyAnalysis,
    TopologicalGraph,
    ConnectivityKind,
    CoordinateTransformation,
    TransformMatrix,
    ReferenceFrame,
    FrameType,
    NavigationSemantics,
    ReachableRegion,
    ObstacleSet,
    TraversabilityAnalysis,
    SpatialConsistency,
    ConsistencyFinding,
    ConsistencyType,
    SpatialRefinement,
    RefinementChange,
    SpatialValidation,
    ValidationResult,
    
    # Failure handling
    SpatialFailure,
    FailureKind,
    
    # Governance
    SpatialGovernance,
    GovernanceFinding,
    
    # Health
    SpatialHealth,
    HealthMetric,
    
    # Diagnostics
    SpatialDiagnostics,
    DiagnosticRecord,
)

__all__ = [
    # Core contracts
    "SpatialDescriptor",
    "SpatialMode",
    "SpatialLifecycle",
    "SpatialEntitySetIdentity",
    "SpatialEntitySet", 
    "SpatialEntity",
    "EntityKind",
    "GeometryType",
    
    # Pipeline results
    "GeometryPipeline",
    "GeometricMeasurement",
    "PropertyComputation",
    "TopologyAnalysis",
    "TopologicalGraph",
    "ConnectivityKind",
    "CoordinateTransformation",
    "TransformMatrix",
    "ReferenceFrame",
    "FrameType",
    "NavigationSemantics",
    "ReachableRegion",
    "ObstacleSet",
    "TraversabilityAnalysis",
    "SpatialConsistency",
    "ConsistencyFinding",
    "ConsistencyType",
    "SpatialRefinement",
    "RefinementChange",
    "SpatialValidation",
    "ValidationResult",
    
    # Failure handling
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

__version__ = "1.0.0"
__phase__ = "7.9"