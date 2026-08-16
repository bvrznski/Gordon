# Salience Network Ontology Sources
# =================================

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .._base import BaseSalienceSource


@dataclass(frozen=True)
class BottomUpSalienceSource(BaseSalienceSource):
    """
    Bottom-up salience source: data-driven significance from sensory input.
    
    Definition: Significance originating from raw sensory data without
    top-down influence. Driven by stimulus features and bottom-up processing.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="bottom_up_source")
    canonical_name: str = field(default="BottomUpSalienceSource")
    definition: str = field(
        default=(
            "Significance originating from raw sensory data without top-down "
            "influence. Driven by stimulus features and bottom-up processing."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "novelty", "urgency")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class TopDownSalienceSource(BaseSalienceSource):
    """
    Top-down salience source: goal-driven significance from cognitive context.
    
    Definition: Significance derived from top-down cognitive processes like
    goals, expectations, and prior knowledge.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="top_down_source")
    canonical_name: str = field(default="TopDownSalienceSource")
    definition: str = field(
        default=(
            "Significance derived from top-down cognitive processes like "
            "goals, expectations, and prior knowledge."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "relevance", "prediction_error")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class GoalDrivenSalienceSource(BaseSalienceSource):
    """
    Goal-driven salience source: significance tied to current goals.
    
    Definition: Significance that arises from the relevance of information
    to currently active goals and objectives.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="goal_driven_source")
    canonical_name: str = field(default="GoalDrivenSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from the relevance of information "
            "to currently active goals and objectives."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "relevance", "priority")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class ContextualSalienceSource(BaseSalienceSource):
    """
    Contextual salience source: significance determined by situational context.
    
    Definition: Significance that arises from the current environmental or
    cognitive context in which information appears.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="contextual_source")
    canonical_name: str = field(default="ContextualSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from the current environmental or "
            "cognitive context in which information appears."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "relevance", "urgency")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class MotivationalSalienceSource(BaseSalienceSource):
    """
    Motivational salience source: significance tied to motivational states.
    
    Definition: Significance that arises from an agent's motivational state,
    where information gains importance based on drives and desires.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="motivational_source")
    canonical_name: str = field(default="MotivationalSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from an agent's motivational state, "
            "where information gains importance based on drives and desires."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "urgency", "reward")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class EmotionalSalienceSource(BaseSalienceSource):
    """
    Emotional salience source: significance determined by emotional state.
    
    Definition: Significance that arises from affective states, where
    emotional valence influences perceived importance.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="emotional_source")
    canonical_name: str = field(default="EmotionalSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from affective states, where "
            "emotional valence influences perceived importance."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "urgency", "threat")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class MemoryDrivenSalienceSource(BaseSalienceSource):
    """
    Memory-driven salience source: significance from memory associations.
    
    Definition: Significance that arises from connections to stored memories,
    where familiarity or associative strength influences perceived importance.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="memory_driven_source")
    canonical_name: str = field(default="MemoryDrivenSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from connections to stored memories, "
            "where familiarity or associative strength influences perceived importance."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "novelty", "relevance")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class SensorySalienceSource(BaseSalienceSource):
    """
    Sensory salience source: significance from sensory features.
    
    Definition: Significance that arises directly from sensory characteristics
    like intensity, contrast, or novelty of input patterns.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="sensory_source")
    canonical_name: str = field(default="SensorySalienceSource")
    definition: str = field(
        default=(
            "Significance that arises directly from sensory characteristics "
            "like intensity, contrast, or novelty of input patterns."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "novelty", "urgency")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class ExecutiveSalienceSource(BaseSalienceSource):
    """
    Executive salience source: significance from executive control signals.
    
    Definition: Significance that arises from higher-level cognitive control
    processes that direct attention and resource allocation.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="executive_source")
    canonical_name: str = field(default="ExecutiveSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from higher-level cognitive control "
            "processes that direct attention and resource allocation."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "priority", "urgency")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"


@dataclass(frozen=True)
class PredictiveSalienceSource(BaseSalienceSource):
    """
    Predictive salience source: significance from prediction mechanisms.
    
    Definition: Significance that arises from the brain's predictive coding
    and expectation violation mechanisms.
    
    SOURCE LAWS COMPLIANT:
        - SALIENCE-SOURCE-LAW-001: Represents semantic origin of significance
        - SALIENCE-SOURCE-LAW-002: Never performs computation
        - SALIENCE-SOURCE-LAW-003: Remains descriptive
        - SALIENCE-SOURCE-LAW-004: Possesses explicit ownership
        - SALIENCE-SOURCE-LAW-005: Remains immutable
    """
    source_id: str = field(default="predictive_source")
    canonical_name: str = field(default="PredictiveSalienceSource")
    definition: str = field(
        default=(
            "Significance that arises from the brain's predictive coding "
            "and expectation violation mechanisms."
        )
    )
    owner: str = field(default="Salience Network Ontology")
    authority: str = field(default="Phase 4.8.2 - Canonical Source Definition")
    contributes_to: Tuple[str, ...] = field(
        default_factory=lambda: ("significance", "prediction_error", "uncertainty")
    )
    
    def __post_init__(self) -> None:
        assert self.is_semantic_origin, "Must be semantic origin"
