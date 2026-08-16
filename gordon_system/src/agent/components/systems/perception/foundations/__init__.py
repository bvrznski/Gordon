# Perception Foundations - Phase 5.2 Canonical Semantic Substrate
# ================================================================

"""
Perception Foundations: The semantic substrate for Gordon's perceptual system.

This module implements the foundation layer of the Perception System as specified in
Phase 5.2 of the Gordon Cognitive Architecture.

Architecture Summary:
    ┌────────────────────────────────────────────────────────────────────┐
    │                    PERCEPTION FOUNDATIONS                          │
    ├────────────────────────────────────────────────────────────────────┤
    │                                                                    │
    │   owns                                                             │
    │   ├── Perceptual Entities (semantic substrate)                   │
    │   │   ├── Observations (raw evidence)                             │
    │   │   ├── Signals (sensor output)                                 │
    │   │   ├── Features (structured properties)                        │
    │   │   ├── Percepts (modality-independent representations)         │
    │   │   ├── Scenes (organized percept collections)                  │
    │   │   └── Events (meaningful transitions)                         │
    │   │                                                              │
    │   │   ├── Confidence (belief measures)                            │
    │   │   ├── Uncertainty (unknowns)                                  │
    │   │   └── Provenance (origin tracking)                            │
    │   │                                                              │
    │   │   ├── Identity (stable identifiers)                           │
    │   │   └── Revision (versioned evolution)                          │
    │   │                                                              │
    │   └── Perception Validation (quality assurance)                  │
    │                                                                    │
    │   exposes                                                         │
    │        └── None (foundational substrate only)                    │
    │                                                                    │
    └────────────────────────────────────────────────────────────────────┘

Core Principles:
    - Perception never creates reality; it constructs internal representations
    - Representations are estimates, never reality itself
    - Perception stops before semantic interpretation begins
    - Observations are raw evidence, not interpretations
    - Higher cognitive systems (Memory, Knowledge, Reasoning) operate after perception
"""

# =============================================================================
# FOUNDATION LAYER EXPORTS
# =============================================================================

from .identity import (
    PerceptionIdentity,
    PerceptionIdentityKind,
    PerceptionIdentityBuilder,
)

from .provenance import (
    PerceptionProvenance,
    PerceptionProvenanceSource,
    PerceptionProvenanceBuilder,
)

from .confidence import (
    PerceptionConfidence,
    ConfidenceBasis,
)

from .uncertainty import PerceptionUncertainty

from .entity import (
    PerceptualEntity,
    EntityKind,
    EntityRevision,
    validate_entity,
)

# Ontology foundations
from .observation import Observation, ObservationBuilder
from .signal import Signal, SignalBuilder
from .feature import Feature, FeatureBuilder
from .percept import Percept, PerceptBuilder
from .scene import Scene, SceneBuilder
from .event import Event, EventBuilder

# Shared contracts and laws
from .ontology import (
    PERCEPTUAL_FOUNDATION_LAWS,
    OBSERVATION_LAWS,
    SIGNAL_LAWS,
    FEATURE_LAWS,
    PERCEPT_LAWS,
    SCENE_LAWS,
    EVENT_LAWS,
    CONFIDENCE_LAWS,
    PROVENANCE_LAWS,
)

__all__ = [
    # Identity
    "PerceptionIdentity",
    "PerceptionIdentityKind",
    "PerceptionIdentityBuilder",
    # Provenance
    "PerceptionProvenance",
    "PerceptionProvenanceSource",
    "PerceptionProvenanceBuilder",
    # Confidence & Uncertainty
    "PerceptionConfidence",
    "ConfidenceBasis",
    "PerceptionUncertainty",
    # Entity system
    "PerceptualEntity",
    "EntityKind",
    "EntityRevision",
    "validate_entity",
    # Ontology - Observations
    "Observation",
    "ObservationBuilder",
    # Ontology - Signals
    "Signal",
    "SignalBuilder",
    # Ontology - Features
    "Feature",
    "FeatureBuilder",
    # Ontology - Percepts
    "Percept",
    "PerceptBuilder",
    # Ontology - Scenes
    "Scene",
    "SceneBuilder",
    # Ontology - Events
    "Event",
    "EventBuilder",
    # Shared contracts and laws
    "PERCEPTUAL_FOUNDATION_LAWS",
    "OBSERVATION_LAWS",
    "SIGNAL_LAWS",
    "FEATURE_LAWS",
    "PERCEPT_LAWS",
    "SCENE_LAWS",
    "EVENT_LAWS",
    "CONFIDENCE_LAWS",
    "PROVENANCE_LAWS",
]