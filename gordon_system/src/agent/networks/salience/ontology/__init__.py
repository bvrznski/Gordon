# Salience Network Ontology Package
# ==================================
#
# Canonical implementation of the Salience Network ontology (Phase 4.8.2).
#
# ARCHITECTURAL PURPOSE:
# ----------------------
# The Salience Ontology defines the canonical semantic vocabulary describing
# salience concepts without runtime behavior or computation.
#
# ONTOLOGY PHILOSOPHY:
# --------------------
# Salience is not attention, motivation, or executive control.
# Salience represents semantic importance: "How significant is this information for cognition?"
#
# ONTOLOGY LAWS:
# --------------
# SALIENCE-ONTOLOGY-LAW-001: The Salience Ontology is the sole canonical vocabulary
#                            describing salience.
# SALIENCE-ONTOLOGY-LAW-002: Ontology defines meaning. It never computes meaning.
# SALIENCE-ONTOLOGY-LAW-003: Ontology defines semantic relationships. It never executes them.
# SALIENCE-ONTOLOGY-LAW-004: Ontology never estimates significance.
# SALIENCE-ONTOLOGY-LAW-005: Ontology never evaluates salience.
# SALIENCE-ONTOLOGY-LAW-006: Ontology preserves semantic identity.
# SALIENCE-ONTOLOGY-LAW-007: Ontology remains deterministic.
# SALIENCE-ONTOLOGY-LAW-008: Ontology remains immutable.
# SALIENCE-ONTOLOGY-LAW-009: Every concept shall possess one canonical definition.
# SALIENCE-ONTOLOGY-LAW-010: Every semantic relationship shall be explicit.
#
# ARCHITECTURAL INVARIANTS:
# -------------------------
# SAL-ONT-INV-001: Ontology remains semantic and descriptive only.
# SAL-ONT-INV-002: Ontology contains no runtime behavior.
# SAL-ONT-INV-003: Ontology contains no computation or inference.
# SAL-ONT-INV-004: Ontology contains no statistical estimation.
# SAL-ONT-INV-005: Every concept possesses explicit ownership and authority.
# SAL-ONT-INV-006: Taxonomy remains acyclic and hierarchical.
# SAL-ONT-INV-007: No duplicated terminology or semantic hierarchies.
# SAL-ONT-INV-008: All ontology objects are immutable (frozen dataclasses).
# SAL-ONT-INV-009: Serialization is deterministic for equivalent inputs.

from __future__ import annotations

# =============================================================================
# PHASE 4.8.2: Canonical Base Abstractions
# =============================================================================

from ._base import (
    BaseSalienceConcept,
    BaseSalienceSignal,
    BaseSalienceSource,
    BaseSalienceRelationship,
    BaseSalienceClassification,
    BaseSalienceContext,
)

# =============================================================================
# PHASE 4.8.2: Root Concepts
# =============================================================================

from .concepts.root import (
    SalienceConcept,
    SignificanceConcept,
    RelevanceConcept,
    ImportanceConcept,
    PriorityConcept,
    UrgencyConcept,
    NoveltyConcept,
    DistinctivenessConcept,
    UnexpectednessConcept,
    ConflictConcept,
    UncertaintyConcept,
    PredictionErrorConcept,
)

# =============================================================================
# PHASE 4.8.2: Salience Sources
# =============================================================================

from .sources import (
    BottomUpSalienceSource,
    TopDownSalienceSource,
    GoalDrivenSalienceSource,
    ContextualSalienceSource,
    MotivationalSalienceSource,
    EmotionalSalienceSource,
    MemoryDrivenSalienceSource,
    SensorySalienceSource,
    ExecutiveSalienceSource,
    PredictiveSalienceSource,
)

# =============================================================================
# PHASE 4.8.2: Salience Signals
# =============================================================================

from .signals import (
    NoveltySignal,
    UrgencySignal,
    ConflictSignal,
    PredictionErrorSignal,
    RewardSignal,
    ThreatSignal,
    OpportunitySignal,
    GoalSignal,
    ContextSignal,
    MemorySignal,
)

# =============================================================================
# PHASE 4.8.2: Significance Levels
# =============================================================================

from .significance import (
    CriticalSignificance,
    HighSignificance,
    ModerateSignificance,
    LowSignificance,
    NegligibleSignificance,
    UnknownSignificance,
)

# =============================================================================
# PHASE 4.8.2: Relevance Types
# =============================================================================

from .relevance import (
    MissionRelevance,
    GoalRelevance,
    TaskRelevance,
    ContextRelevance,
    MemoryRelevance,
    ExecutiveRelevance,
    TemporalRelevance,
    EnvironmentalRelevance,
)

# =============================================================================
# PHASE 4.8.2: Novelty Types
# =============================================================================

from .novelty import (
    AbsoluteNovelty,
    RelativeNovelty,
    ExpectedNovelty,
    UnexpectedNovelty,
    LearnedNovelty,
    PersistentNovelty,
)

# =============================================================================
# PHASE 4.8.2: Urgency Types
# =============================================================================

from .urgency import (
    ImmediateUrgency,
    NearTermUrgency,
    DeferredUrgency,
    BackgroundUrgency,
    DormantUrgency,
)

# =============================================================================
# PHASE 4.8.2: Uncertainty Types
# =============================================================================

from .uncertainty import (
    KnownUncertainty,
    UnknownUncertainty,
    EpistemicUncertainty,
    ContextualUncertainty,
    PredictiveUncertainty,
)

# =============================================================================
# PHASE 4.8.2: Conflict Types
# =============================================================================

from .conflict import (
    GoalConflict,
    TaskConflict,
    MissionConflict,
    ConstraintConflict,
    EvidenceConflict,
    InterpretationConflict,
)

# =============================================================================
# PHASE 4.8.2: Prediction Error Types
# =============================================================================

from .prediction_error import (
    ExpectedPredictionError,
    UnexpectedPredictionError,
    MajorPredictionError,
    MinorPredictionError,
    PersistentPredictionError,
)

# =============================================================================
# PHASE 4.8.2: Classification Types
# =============================================================================

from .classification import (
    PositiveSalience,
    NegativeSalience,
    NeutralSalience,
    MixedSalience,
    UnknownSalience,
)

# =============================================================================
# PHASE 4.8.2: Context Types
# =============================================================================

from .context import (
    MissionContext,
    GoalContext,
    TaskContext,
    EnvironmentalContext,
    MemoryContext,
    ExecutiveContext,
    PlanningContext,
    ReasoningContext,
)

# =============================================================================
# PHASE 4.8.2: Semantic Relationships
# =============================================================================

from .relationships import (
    SalienceToSourceRelationship,
    SourceToSignalRelationship,
    SignalToSignificanceRelationship,
    SignificanceToClassificationRelationship,
    ClassificationToRelationshipRelationship,
    RelevanceToSalienceRelationship,
    NoveltyToSignificanceRelationship,
    UrgencyToSignificanceRelationship,
    UncertaintyToSignificanceRelationship,
    PredictionErrorToSignificanceRelationship,
    ConflictToSignificanceRelationship,
)

# =============================================================================
# PHASE 4.8.2: Ontology Ownership Contracts
# =============================================================================

from .contracts import (
    SalienceConceptReference,
    SalienceConceptRequirement,
    SalienceConceptAuthority,
    SalienceConceptOwner,
    SalienceConceptProjection,
    
    SalienceSourceReference,
    SalienceSourceRequirement,
    SalienceSourceAuthority,
    SalienceSourceOwner,
    SalienceSourceProjection,
    
    SalienceSignalReference,
    SalienceSignalRequirement,
    SalienceSignalAuthority,
    SalienceSignalOwner,
    SalienceSignalProjection,
    
    SignificanceReference,
    SignificanceRequirement,
    SignificanceAuthority,
    SignificanceOwner,
    SignificanceProjection,
    
    RelevanceReference,
    RelevanceRequirement,
    RelevanceAuthority,
    RelevanceOwner,
    RelevanceProjection,
    
    NoveltyReference,
    NoveltyRequirement,
    NoveltyAuthority,
    NoveltyOwner,
    NoveltyProjection,
    
    UrgencyReference,
    UrgencyRequirement,
    UrgencyAuthority,
    UrgencyOwner,
    UrgencyProjection,
    
    UncertaintyReference,
    UncertaintyRequirement,
    UncertaintyAuthority,
    UncertaintyOwner,
    UncertaintyProjection,
    
    ConflictReference,
    ConflictRequirement,
    ConflictAuthority,
    ConflictOwner,
    ConflictProjection,
    
    PredictionErrorReference,
    PredictionErrorRequirement,
    PredictionErrorAuthority,
    PredictionErrorOwner,
    PredictionErrorProjection,
    
    ClassificationReference,
    ClassificationRequirement,
    ClassificationAuthority,
    ClassificationOwner,
    ClassificationProjection,
)

# =============================================================================
# PHASE 4.8.2: Ontology Constants
# =============================================================================

ONTOLOGY_VERSION: str = "1.0.0"
"""Canonical ontology version string."""

ONTOLOGY_NAME: str = "Salience Network Ontology"
"""Canonical ontology name."""

ONTOLOGY_ROOT_CONCEPTS: Tuple[str, ...] = (
    "salience",
    "significance",
    "relevance",
    "importance",
    "priority",
    "urgency",
    "novelty",
    "distinctiveness",
    "unexpectedness",
    "conflict",
    "uncertainty",
    "prediction_error",
)
"""Canonical root concepts in the ontology."""

ONTOLOGY_SOURCES: Tuple[str, ...] = (
    "bottom_up",
    "top_down",
    "goal_driven",
    "contextual",
    "motivational",
    "emotional",
    "memory_driven",
    "sensory",
    "executive",
    "predictive",
)
"""Canonical salience sources."""

ONTOLOGY_SIGNALS: Tuple[str, ...] = (
    "novelty",
    "urgency",
    "conflict",
    "prediction_error",
    "reward",
    "threat",
    "opportunity",
    "goal",
    "context",
    "memory",
)
"""Canonical salience signals."""

ONTOLOGY_SIGNIFICANCE_LEVELS: Tuple[str, ...] = (
    "critical",
    "high",
    "moderate",
    "low",
    "negligible",
    "unknown",
)
"""Canonical significance levels."""

ONTOLOGY_CLASSIFICATIONS: Tuple[str, ...] = (
    "positive",
    "negative",
    "neutral",
    "mixed",
    "unknown",
)
"""Canonical salience classifications."""

__all__ = [
    # Base Abstractions
    "BaseSalienceConcept",
    "BaseSalienceSignal",
    "BaseSalienceSource",
    "BaseSalienceRelationship",
    "BaseSalienceClassification",
    "BaseSalienceContext",
    
    # Root Concepts
    "SalienceConcept",
    "SignificanceConcept",
    "RelevanceConcept",
    "ImportanceConcept",
    "PriorityConcept",
    "UrgencyConcept",
    "NoveltyConcept",
    "DistinctivenessConcept",
    "UnexpectednessConcept",
    "ConflictConcept",
    "UncertaintyConcept",
    "PredictionErrorConcept",
    
    # Sources
    "BottomUpSalienceSource",
    "TopDownSalienceSource",
    "GoalDrivenSalienceSource",
    "ContextualSalienceSource",
    "MotivationalSalienceSource",
    "EmotionalSalienceSource",
    "MemoryDrivenSalienceSource",
    "SensorySalienceSource",
    "ExecutiveSalienceSource",
    "PredictiveSalienceSource",
    
    # Signals
    "NoveltySignal",
    "UrgencySignal",
    "ConflictSignal",
    "PredictionErrorSignal",
    "RewardSignal",
    "ThreatSignal",
    "OpportunitySignal",
    "GoalSignal",
    "ContextSignal",
    "MemorySignal",
    
    # Significance
    "CriticalSignificance",
    "HighSignificance",
    "ModerateSignificance",
    "LowSignificance",
    "NegligibleSignificance",
    "UnknownSignificance",
    
    # Relevance
    "MissionRelevance",
    "GoalRelevance",
    "TaskRelevance",
    "ContextRelevance",
    "MemoryRelevance",
    "ExecutiveRelevance",
    "TemporalRelevance",
    "EnvironmentalRelevance",
    
    # Novelty
    "AbsoluteNovelty",
    "RelativeNovelty",
    "ExpectedNovelty",
    "UnexpectedNovelty",
    "LearnedNovelty",
    "PersistentNovelty",
    
    # Urgency
    "ImmediateUrgency",
    "NearTermUrgency",
    "DeferredUrgency",
    "BackgroundUrgency",
    "DormantUrgency",
    
    # Uncertainty
    "KnownUncertainty",
    "UnknownUncertainty",
    "EpistemicUncertainty",
    "ContextualUncertainty",
    "PredictiveUncertainty",
    
    # Conflict
    "GoalConflict",
    "TaskConflict",
    "MissionConflict",
    "ConstraintConflict",
    "EvidenceConflict",
    "InterpretationConflict",
    
    # Prediction Error
    "ExpectedPredictionError",
    "UnexpectedPredictionError",
    "MajorPredictionError",
    "MinorPredictionError",
    "PersistentPredictionError",
    
    # Classification
    "PositiveSalience",
    "NegativeSalience",
    "NeutralSalience",
    "MixedSalience",
    "UnknownSalience",
    
    # Context
    "MissionContext",
    "GoalContext",
    "TaskContext",
    "EnvironmentalContext",
    "MemoryContext",
    "ExecutiveContext",
    "PlanningContext",
    "ReasoningContext",
    
    # Relationships
    "SalienceToSourceRelationship",
    "SourceToSignalRelationship",
    "SignalToSignificanceRelationship",
    "SignificanceToClassificationRelationship",
    "ClassificationToRelationshipRelationship",
    "RelevanceToSalienceRelationship",
    "NoveltyToSignificanceRelationship",
    "UrgencyToSignificanceRelationship",
    "UncertaintyToSignificanceRelationship",
    "PredictionErrorToSignificanceRelationship",
    "ConflictToSignificanceRelationship",
    
    # Ownership Contracts
    "SalienceConceptReference",
    "SalienceConceptRequirement",
    "SalienceConceptAuthority",
    "SalienceConceptOwner",
    "SalienceConceptProjection",
    "SalienceSourceReference",
    "SalienceSourceRequirement",
    "SalienceSourceAuthority",
    "SalienceSourceOwner",
    "SalienceSourceProjection",
    "SalienceSignalReference",
    "SalienceSignalRequirement",
    "SalienceSignalAuthority",
    "SalienceSignalOwner",
    "SalienceSignalProjection",
    "SignificanceReference",
    "SignificanceRequirement",
    "SignificanceAuthority",
    "SignificanceOwner",
    "SignificanceProjection",
    "RelevanceReference",
    "RelevanceRequirement",
    "RelevanceAuthority",
    "RelevanceOwner",
    "RelevanceProjection",
    "NoveltyReference",
    "NoveltyRequirement",
    "NoveltyAuthority",
    "NoveltyOwner",
    "NoveltyProjection",
    "UrgencyReference",
    "UrgencyRequirement",
    "UrgencyAuthority",
    "UrgencyOwner",
    "UrgencyProjection",
    "UncertaintyReference",
    "UncertaintyRequirement",
    "UncertaintyAuthority",
    "UncertaintyOwner",
    "UncertaintyProjection",
    "ConflictReference",
    "ConflictRequirement",
    "ConflictAuthority",
    "ConflictOwner",
    "ConflictProjection",
    "PredictionErrorReference",
    "PredictionErrorRequirement",
    "PredictionErrorAuthority",
    "PredictionErrorOwner",
    "PredictionErrorProjection",
    "ClassificationReference",
    "ClassificationRequirement",
    "ClassificationAuthority",
    "ClassificationOwner",
    "ClassificationProjection",
    
    # Constants
    "ONTOLOGY_VERSION",
    "ONTOLOGY_NAME",
    "ONTOLOGY_ROOT_CONCEPTS",
    "ONTOLOGY_SOURCES",
    "ONTOLOGY_SIGNALS",
    "ONTOLOGY_SIGNIFICANCE_LEVELS",
    "ONTOLOGY_CLASSIFICATIONS",
]

from typing import Tuple