# Perception Integration - Phase 5.2.3
# ======================================

"""
Perception Integration: Combines multimodal perceptual evidence into coherent structures.

Integration combines evidence.

It does not acquire evidence.
It does not reinterpret evidence as Knowledge.
It does not commit Memory.
It does not make executive decisions.

Architecture:
    perception/
    └── integration/
        ├── shared/              # Common contracts and types
        │   ├── request.py       # Integration request
        │   ├── result.py        # Integration result
        │   ├── session.py       # Integration session
        │   ├── stage.py         # Integration stages
        │   ├── evidence_group.py # Evidence grouping
        │   ├── source_dependency.py # Source dependency analysis
        │   ├── confidence.py    # Integrated confidence
        │   ├── uncertainty.py   # Integrated uncertainty
        │   ├── conflict.py      # Conflict preservation
        │   ├── partial.py       # Partial integration state
        │   ├── ambiguity.py     # Ambiguous integration state
        │   ├── replay.py        # Integration replay
        │   ├── query.py         # Integration queries
        │   ├── validation.py    # Validation
        │   ├── health.py        # Health monitoring
        │   └── diagnostics.py   # Diagnostics
        │
        ├── intermodal/          # Cross-modal correspondence
        │   ├── request.py       # Correspondence request
        │   ├── result.py        # Correspondence result
        │   ├── correspondence.py  # Core correspondence logic
        │   ├── evidence.py      # Correspondence evidence
        │   ├── dimension.py     # Correspondence dimensions
        │   └── alternative.py   # Alternative correspondences
        │
        ├── temporal_binding/    # Temporal organization
        │   ├── request.py       # Binding request
        │   ├── result.py        # Binding result
        │   ├── binding.py       # Core binding logic
        │   ├── window.py        # Binding windows
        │   ├── ordering.py      # Event ordering
        │   ├── interval.py      # Interval analysis
        │   └── validation.py    # Validation
        │
        ├── spatial_binding/     # Spatial organization
        │   ├── request.py       # Binding request
        │   ├── result.py        # Binding result
        │   ├── binding.py       # Core binding logic
        │   ├── relation.py      # Spatial relations
        │   ├── topology.py      # Topological structure
        │   ├── hierarchy.py     # Hierarchical structure
        │   └── validation.py    # Validation
        │
        └── fusion/              # Multimodal fusion
            ├── request.py       # Fusion request
            ├── result.py        # Fusion result
            ├── strategy.py      # Fusion strategies
            ├── complementary.py # Complementary fusion
            ├── corroborative.py # Corroborative fusion
            ├── competitive.py   # Competitive fusion
            ├── hierarchical.py  # Hierarchical fusion
            ├── field_level.py   # Field-level fusion
            ├── weighting.py     # Source weighting
            ├── conflict.py      # Conflict-preserving fusion
            ├── fused_percept.py # Fused percept
            ├── multimodal_scene.py # Multimodal scene
            └── multimodal_event.py # Multimodal event

Integration Laws:
    INTEGRATION-LAW-001: Every Integration operation consumes validated processed artifacts.
    INTEGRATION-LAW-002: Integration preserves every participating source artifact.
    INTEGRATION-LAW-003: Integration preserves source identity, provenance, confidence, uncertainty.
    INTEGRATION-LAW-004: Integration constructs new artifacts without replacing source evidence.
    INTEGRATION-LAW-005: Integration preserves unresolved conflicts and plausible alternatives.
    INTEGRATION-LAW-006: Integration publishes only validated canonical Perception artifacts.
    INTEGRATION-LAW-007: Integration mechanisms remain independently testable and replaceable.
    INTEGRATION-LAW-008: Integration semantics are deterministic for equivalent evidence.

Architecture Boundaries:
    Processing Alignment
        converts evidence into compatible reference systems.
    
    Integration Correspondence
        evaluates whether evidence may refer to the same occurrence.
    
    Binding
        groups evidence into coherent temporal or spatial structures.
    
    Fusion
        constructs an integrated perceptual artifact.
    
    Projection
        exposes cognition-ready views.
    
    Knowledge
        interprets meaning.
"""

from gordon_system.src.agent.components.systems.perception.integration.shared import (
    PerceptionIntegrationRequest,
    PerceptionIntegrationResult,
    IntegrationStatus,
    IntegrationOutcome,
    PerceptionIntegrationSession,
    PerceptualEvidenceGroup,
    SourceDependencyAssessment,
    IntegratedPerceptualConfidence,
    IntegratedPerceptualUncertainty,
    PerceptualConflict,
    PartialPerceptionIntegration,
    AmbiguousPerceptionIntegration,
    PerceptionIntegrationReplay,
    PerceptionIntegrationValidation,
    PerceptionIntegrationHealth,
    PerceptionIntegrationDiagnostics,
)

from gordon_system.src.agent.components.systems.perception.integration.engine import (
    PerceptionIntegrationEngine,
)

__all__ = [
    # Shared contracts
    "PerceptionIntegrationRequest",
    "PerceptionIntegrationResult",
    "IntegrationStatus",
    "IntegrationOutcome",
    "PerceptionIntegrationSession",
    "PerceptualEvidenceGroup",
    "SourceDependencyAssessment",
    "IntegratedPerceptualConfidence",
    "IntegratedPerceptualUncertainty",
    "PerceptualConflict",
    "PartialPerceptionIntegration",
    "AmbiguousPerceptionIntegration",
    "PerceptionIntegrationReplay",
    "PerceptionIntegrationValidation",
    "PerceptionIntegrationHealth",
    "PerceptionIntegrationDiagnostics",
    # Engine
    "PerceptionIntegrationEngine",
]