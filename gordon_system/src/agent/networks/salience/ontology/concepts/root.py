# Salience Network Ontology Root Concepts
# ======================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .._base import BaseSalienceConcept


# =============================================================================
# SALIENCE ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class SalienceConcept(BaseSalienceConcept):
    """
    The root concept of the Salience Network ontology.
    
    Definition: Salience represents the semantic importance of information.
    
    Salience answers: "How significant is this information for cognition?"
    
    Salience never answers: "What should cognition do?" (that is attention,
    motivation, or executive control).
    
    INHERITANCE:
        - BaseSalienceConcept
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance (from BaseSalienceConcept)
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="salience_root")
    canonical_name: str = field(default="Salience")
    definition: str = field(
        default=(
            "The semantic importance of information. Salience represents how "
            "significant information is for cognition without prescribing what "
            "cognition should do."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Ontology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "SalienceConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# SIGNIFICANCE ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class SignificanceConcept(BaseSalienceConcept):
    """
    The significance concept: how much something matters.
    
    Definition: Significance represents the degree to which information or
    events matter within a semantic context.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Significance inherits from BaseSalienceConcept
        - Significance is assessed via signals (NoveltySignal, UrgencySignal, etc.)
        - Significance is classified into levels (CriticalSignificance, HighSignificance, etc.)
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="significance_root")
    canonical_name: str = field(default="Significance")
    definition: str = field(
        default=(
            "The degree to which information or events matter within a semantic "
            "context. Significance quantifies semantic importance."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "SignificanceConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# RELEVANCE ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class RelevanceConcept(BaseSalienceConcept):
    """
    The relevance concept: how connected something is to context.
    
    Definition: Relevance represents the connection between information and
    a contextual frame (mission, goal, task, memory).
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Relevance inherits from BaseSalienceConcept
        - Relevance types include MissionRelevance, GoalRelevance, etc.
        - Relevance is contextual (MissionContext, GoalContext, etc.)
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="relevance_root")
    canonical_name: str = field(default="Relevance")
    definition: str = field(
        default=(
            "The connection between information and a contextual frame. Relevance "
            "describes how information relates to missions, goals, tasks, and memory."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "RelevanceConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# IMPORTANCE ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class ImportanceConcept(BaseSalienceConcept):
    """
    The importance concept: how weighty something is.
    
    Definition: Importance represents the relative weight or significance of
    information within a semantic space.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Importance inherits from BaseSalienceConcept
        - Importance is closely related to Significance
        - Importance influences Priority and Urgency
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="importance_root")
    canonical_name: str = field(default="Importance")
    definition: str = field(
        default=(
            "The relative weight or significance of information within a semantic "
            "space. Importance measures how much cognitive resources should be allocated."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "ImportanceConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# PRIORITY ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class PriorityConcept(BaseSalienceConcept):
    """
    The priority concept: how order is assigned.
    
    Definition: Priority represents the ordering of significance where higher
    priority items should be addressed before lower priority ones.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Priority inherits from BaseSalienceConcept
        - Priority is derived from Significance and Urgency
        - Priority guides executive allocation decisions
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="priority_root")
    canonical_name: str = field(default="Priority")
    definition: str = field(
        default=(
            "The ordering of significance where higher priority items should be "
            "addressed before lower priority ones. Priority is a semantic ordering."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "PriorityConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# URGENCY ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class UrgencyConcept(BaseSalienceConcept):
    """
    The urgency concept: how time-sensitive something is.
    
    Definition: Urgency represents the temporal significance of information,
    where higher urgency demands more immediate attention.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Urgency inherits from BaseSalienceConcept
        - Urgency types include ImmediateUrgency, NearTermUrgency, etc.
        - Urgency is temporal but remains semantic (not computational)
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="urgency_root")
    canonical_name: str = field(default="Urgency")
    definition: str = field(
        default=(
            "The temporal significance of information. Urgency describes the "
            "time-sensitivity of semantic importance without computational timing."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "UrgencyConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# NOVELTY ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class NoveltyConcept(BaseSalienceConcept):
    """
    The novelty concept: how new or unexpected something is.
    
    Definition: Novelty represents the degree to which information deviates
    from expected patterns or prior knowledge.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Novelty inherits from BaseSalienceConcept
        - Novelty types include AbsoluteNovelty, RelativeNovelty, etc.
        - Novelty contributes to salience through unexpectedness
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="novelty_root")
    canonical_name: str = field(default="Novelty")
    definition: str = field(
        default=(
            "The degree to which information deviates from expected patterns or "
            "prior knowledge. Novelty represents semantic newness."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "NoveltyConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# DISTINCTIVENESS ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class DistinctivenessConcept(BaseSalienceConcept):
    """
    The distinctiveness concept: how uniquely identifiable something is.
    
    Definition: Distinctiveness represents the degree to which information
    stands out from its context or competitors.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Distinctiveness inherits from BaseSalienceConcept
        - Distinctiveness is closely related to Novelty
        - Distinctiveness contributes to salience through uniqueness
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="distinctiveness_root")
    canonical_name: str = field(default="Distinctiveness")
    definition: str = field(
        default=(
            "The degree to which information stands out from its context or "
            "competitors. Distinctiveness represents semantic uniqueness."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "DistinctivenessConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# UNEXPECTEDNESS ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class UnexpectednessConcept(BaseSalienceConcept):
    """
    The unexpectedness concept: how surprising something is.
    
    Definition: Unexpectedness represents the degree to which information
    violates expectations or predictions.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Unexpectedness inherits from BaseSalienceConcept
        - Unexpectedness is closely related to Novelty and PredictionError
        - Unexpectedness contributes to salience through violation of expectations
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="unexpectedness_root")
    canonical_name: str = field(default="Unexpectedness")
    definition: str = field(
        default=(
            "The degree to which information violates expectations or predictions. "
            "Unexpectedness represents semantic surprise."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "UnexpectednessConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# CONFLICT ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class ConflictConcept(BaseSalienceConcept):
    """
    The conflict concept: when competing elements interact.
    
    Definition: Conflict represents the semantic tension between competing
    elements (goals, tasks, evidence, interpretations).
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Conflict inherits from BaseSalienceConcept
        - Conflict types include GoalConflict, TaskConflict, etc.
        - Conflict contributes to salience through semantic tension
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="conflict_root")
    canonical_name: str = field(default="Conflict")
    definition: str = field(
        default=(
            "The semantic tension between competing elements. Conflict represents "
            "incompatible goals, tasks, evidence, or interpretations."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "ConflictConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# UNCERTAINTY ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class UncertaintyConcept(BaseSalienceConcept):
    """
    The uncertainty concept: when information is incomplete.
    
    Definition: Uncertainty represents the state of incomplete knowledge or
    indeterminacy about information or its interpretation.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - Uncertainty inherits from BaseSalienceConcept
        - Uncertainty types include KnownUncertainty, UnknownUncertainty, etc.
        - Uncertainty contributes to salience through knowledge gaps
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="uncertainty_root")
    canonical_name: str = field(default="Uncertainty")
    definition: str = field(
        default=(
            "The state of incomplete knowledge or indeterminacy about information "
            "or its interpretation. Uncertainty represents semantic incompleteness."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "UncertaintyConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"


# =============================================================================
# PREDICTION ERROR ROOT CONCEPT
# =============================================================================

@dataclass(frozen=True)
class PredictionErrorConcept(BaseSalienceConcept):
    """
    The prediction error concept: when predictions deviate from reality.
    
    Definition: PredictionError represents the semantic deviation between
    expected outcomes and actual observations.
    
    INHERITANCE:
        - BaseSalienceConcept
    
    SEMANTIC RELATIONSHIPS:
        - PredictionError inherits from BaseSalienceConcept
        - PredictionError types include ExpectedPredictionError, UnexpectedPredictionError, etc.
        - PredictionError contributes to salience through expectation violation
    
    CONCEPT LAWS COMPLIANT:
        - SALIENCE-CONCEPT-LAW-001: Exactly one semantic owner
        - SALIENCE-CONCEPT-LAW-002: Explicit authority
        - SALIENCE-CONCEPT-LAW-003: Explicit inheritance
        - SALIENCE-CONCEPT-LAW-004: Acyclic inheritance
        - SALIENCE-CONCEPT-LAW-005: Immutable definition
        - SALIENCE-CONCEPT-LAW-006: Repository-wide definition
    """
    
    concept_id: str = field(default="prediction_error_root")
    canonical_name: str = field(default="PredictionError")
    definition: str = field(
        default=(
            "The semantic deviation between expected outcomes and actual observations. "
            "PredictionError represents the gap between expectations and reality."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - CanonicalOntology Definition")
    category: str = field(default="root_concept")
    
    parent_concepts: Tuple[str, ...] = field(
        default_factory=lambda: ("BaseSalienceConcept",)
    )
    
    def __post_init__(self) -> None:
        assert self.is_canonical, "PredictionErrorConcept must be a canonical definition"
        assert self.owner == "Salience Network Ontology", "Owner mismatch"