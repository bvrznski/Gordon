# Salience Network Content Model
# ==============================
#
# Canonical implementation of the Salience Content Model (Phase 4.8.3).
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# This module defines the immutable semantic representation of all information
# flowing through the Salience Network.
#
# CONTENT MODEL PHILOSOPHY:
#     - Content represents semantic information
#     - Content never evaluates itself
#     - Content never computes salience
#     - Content remains deterministic and immutable
#     - Content preserves provenance and lineage
#

"""
Salience Network Content Model (Phase 4.8.3)

ARCHITECTURAL LAYER:
    Semantic Content Layer - Information Representation

OWNERSHIP:
    Sole owner of: semantic observations, semantic evidence, semantic cues,
    semantic hypotheses, semantic descriptors, semantic annotations,
    semantic metadata, content identity, content lineage.
    
FORBIDDEN RESPONSIBILITIES:
    - No evaluation
    - No statistical estimation
    - No runtime computation
    - No attention allocation
    - No executive control

CONTENT HIERARCHY (semantic dependency):
    SalienceContent
        ↓
    Observation
        ↓
    Evidence
        ↓
    Cue
        ↓
    Hypothesis
        ↓
    Descriptor
        ↓
    Annotation
        ↓
    Metadata

CONNECTIONS:
    - Integration: gordon_system/src/agent/networks/salience/integration/
    - Serialization: gordon_system/src/agent/networks/salience/serialization/
    - Validation: gordon_system/src/agent/networks/salience/validation/

CONTENT LAWS (Phase 4.8.3):
    SALIENCE-CONTENT-LAW-001 through SALIENCE-CONTENT-LAW-010
"""

from __future__ import annotations

# Base content abstractions
from .base import (
    BaseSalienceContent,
    SalienceContentIdentity,
    ContentAuthority,
    ContentOwnership,
    ContentOrigin,
    ContentLineage,
)

# Observation model hierarchy
from .observations.base import BaseObservation
from .observations.sensory import SensoryObservation
from .observations.environmental import EnvironmentalObservation
from .observations.goal import GoalObservation
from .observations.task import TaskObservation
from .observations.memory import MemoryObservation
from .observations.executive import ExecutiveObservation
from .observations.planning import PlanningObservation
from .observations.reasoning import ReasoningObservation
from .observations.context import ContextObservation

# Evidence model hierarchy
from .evidence.base import BaseEvidence
from .evidence.novelty import NoveltyEvidence
from .evidence.urgency import UrgencyEvidence
from .evidence.conflict import ConflictEvidence
from .evidence.prediction_error import PredictionErrorEvidence
from .evidence.context import ContextEvidence
from .evidence.memory import MemoryEvidence
from .evidence.goal import GoalEvidence
from .evidence.mission import MissionEvidence
from .evidence.relationship import RelationshipEvidence

# Cue model hierarchy
from .cues.base import BaseCue
from .cues.novelty import NoveltyCue
from .cues.threat import ThreatCue
from .cues.opportunity import OpportunityCue
from .cues.goal import GoalCue
from .cues.temporal import TemporalCue
from .cues.context import ContextCue
from .cues.memory import MemoryCue
from .cues.conflict import ConflictCue
from .cues.expectation import ExpectationCue

# Hypothesis model hierarchy
from .hypotheses.base import BaseHypothesis
from .hypotheses.potential import PotentialSalience
from .hypotheses.candidate import CandidateSalience
from .hypotheses.context import ContextHypothesis
from .hypotheses.conflict import ConflictHypothesis
from .hypotheses.urgency import UrgencyHypothesis
from .hypotheses.novelty import NoveltyHypothesis
from .hypotheses.prediction import PredictionHypothesis

# Descriptor model hierarchy
from .descriptors.base import BaseDescriptor
from .descriptors.importance import ImportanceDescriptor
from .descriptors.urgency import UrgencyDescriptor
from .descriptors.novelty import NoveltyDescriptor
from .descriptors.conflict import ConflictDescriptor
from .descriptors.relevance import RelevanceDescriptor
from .descriptors.uncertainty import UncertaintyDescriptor
from .descriptors.context import ContextDescriptor
from .descriptors.relationship import RelationshipDescriptor

# Annotation model hierarchy
from .annotations.base import BaseAnnotation
from .annotations.source import SourceAnnotation
from .annotations.context import ContextAnnotation
from .annotations.ownership import OwnershipAnnotation
from .annotations.relationship import RelationshipAnnotation
from .annotations.validation import ValidationAnnotation
from .annotations.lifecycle import LifecycleAnnotation
from .annotations.governance import GovernanceAnnotation

# Metadata model hierarchy
from .metadata.base import BaseMetadata
from .metadata.identity import IdentityMetadata
from .metadata.authority import AuthorityMetadata
from .metadata.ownership import OwnershipMetadata
from .metadata.schema import SchemaMetadata
from .metadata.revision import RevisionMetadata
from .metadata.provenance import ProvenanceMetadata
from .metadata.version import VersionMetadata

# Composite content
from .composite import (
    CompositeObservation,
    CompositeEvidence,
    CompositeCue,
    CompositeDescriptor,
    CompositeAnnotation,
)

# Context models
from .context import (
    MissionContext,
    GoalContext,
    TaskContext,
    ExecutiveContext,
    PlanningContext,
    MemoryContext,
    EnvironmentalContext,
    ReasoningContext,
    RepositoryContext,
)

__all__ = [
    # Base abstractions
    "BaseSalienceContent",
    "SalienceContentIdentity",
    "ContentAuthority",
    "ContentOwnership",
    "ContentOrigin",
    "ContentLineage",
    
    # Observations
    "BaseObservation",
    "SensoryObservation",
    "EnvironmentalObservation",
    "GoalObservation",
    "TaskObservation",
    "MemoryObservation",
    "ExecutiveObservation",
    "PlanningObservation",
    "ReasoningObservation",
    "ContextObservation",
    
    # Evidence
    "BaseEvidence",
    "NoveltyEvidence",
    "UrgencyEvidence",
    "ConflictEvidence",
    "PredictionErrorEvidence",
    "ContextEvidence",
    "MemoryEvidence",
    "GoalEvidence",
    "MissionEvidence",
    "RelationshipEvidence",
    
    # Cues
    "BaseCue",
    "NoveltyCue",
    "ThreatCue",
    "OpportunityCue",
    "GoalCue",
    "TemporalCue",
    "ContextCue",
    "MemoryCue",
    "ConflictCue",
    "ExpectationCue",
    
    # Hypotheses
    "BaseHypothesis",
    "PotentialSalience",
    "CandidateSalience",
    "ContextHypothesis",
    "ConflictHypothesis",
    "UrgencyHypothesis",
    "NoveltyHypothesis",
    "PredictionHypothesis",
    
    # Descriptors
    "BaseDescriptor",
    "ImportanceDescriptor",
    "UrgencyDescriptor",
    "NoveltyDescriptor",
    "ConflictDescriptor",
    "RelevanceDescriptor",
    "UncertaintyDescriptor",
    "ContextDescriptor",
    "RelationshipDescriptor",
    
    # Annotations
    "BaseAnnotation",
    "SourceAnnotation",
    "ContextAnnotation",
    "OwnershipAnnotation",
    "RelationshipAnnotation",
    "ValidationAnnotation",
    "LifecycleAnnotation",
    "GovernanceAnnotation",
    
    # Metadata
    "BaseMetadata",
    "IdentityMetadata",
    "AuthorityMetadata",
    "OwnershipMetadata",
    "SchemaMetadata",
    "RevisionMetadata",
    "ProvenanceMetadata",
    "VersionMetadata",
    
    # Composite content
    "CompositeObservation",
    "CompositeEvidence",
    "CompositeCue",
    "CompositeDescriptor",
    "CompositeAnnotation",
    
    # Context models
    "MissionContext",
    "GoalContext",
    "TaskContext",
    "ExecutiveContext",
    "PlanningContext",
    "MemoryContext",
    "EnvironmentalContext",
    "ReasoningContext",
    "RepositoryContext",
]