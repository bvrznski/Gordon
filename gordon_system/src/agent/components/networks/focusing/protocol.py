# Focusing Network Protocol
# ===========================

"""
Abstract interface for the FocusingNetwork.

The protocol defines:
    - Assessment interface
    - State management interface
    - Configuration requirements
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Tuple, Optional, Mapping
from datetime import datetime

from gordon_system.src.agent.components.networks.focusing.models import (
    FocusingInput,
    FocusAssessment,
    NetworkStateSnapshot,
    FocusResetRequest,
)
from gordon_system.src.agent.components.networks.focusing.enums import (
    PriorityLevel,
    PrecisionBandwidth,
    PersistenceMode,
    BiasModality,
)

from gordon_system.src.agent.components.networks.focusing.configuration import (
    FocusingNetworkConfig,
)


class FocusingNetworkProtocol(ABC):
    """
    Abstract interface for the FocusingNetwork.

    This protocol defines the contract that all implementations must satisfy.
    The network:
        - Computes focus policies (NOT execute actions)
        - Is immutable (stateful but produces new outputs)
        - Has no external dependencies (pure computation when possible)
    """

    @property
    @abstractmethod
    def config(self) -> FocusingNetworkConfig:
        """Return the current configuration."""
        raise NotImplementedError

    @abstractmethod
    def assess(
        self,
        input_data: FocusingInput,
    ) -> FocusAssessment:
        """
        Assess focus candidates and return assessment.

        This is the main computational entry point. Given a set of focus
        candidates, it computes priority rankings, relevance evaluations,
        competition analysis, suppression recommendations, precision estimates,
        persistence policies, bias signals, and resource allocation.

        Args:
            input_data: Input containing focus candidates and context

        Returns:
            FocusAssessment with all computed values
        """
        raise NotImplementedError

    @abstractmethod
    def snapshot_state(self) -> NetworkStateSnapshot:
        """
        Return an immutable snapshot of current state.

        This provides a bounded view of the network's internal state without
        exposing mutable implementation details.
        """
        raise NotImplementedError

    @abstractmethod
    def process_reset_request(
        self,
        request: FocusResetRequest,
    ) -> None:
        """
        Process a state reset request.

        This modifies internal state according to the request specification.
        The method is idempotent - repeated calls with same request produce
        same result.
        """
        raise NotImplementedError


class AssessmentPipeline(Protocol):
    """
    Protocol for individual assessment pipeline stages.

    Each stage in the focus computation pipeline follows this interface:
        - Takes inputs from previous stage
        - Computes a specific aspect of focus policy
        - Returns output for next stage or final assessment
    """

    @property
    def name(self) -> str:
        """Return stage name for logging/debugging."""
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        candidates: Tuple[str, ...],
        context: Optional[dict] = None,
    ) -> dict:
        """
        Execute this pipeline stage.

        Args:
            candidates: Current focus targets to assess
            context: Context from previous stages

        Returns:
            Stage-specific output for next stage or final assessment
        """
        raise NotImplementedError


class PriorityPipeline(Protocol):
    """Protocol for priority computation stages."""

    @abstractmethod
    def compute_priority(
        self,
        target_id: str,
        goal_relevance: float,
        context_relevance: float,
        memory_relevance: float,
    ) -> Tuple[float, PriorityLevel]:
        """
        Compute priority score and level for a target.

        Args:
            target_id: Target identifier
            goal_relevance: Alignment with current goals [0.0, 1.0]
            context_relevance: Current situation relevance [0.0, 1.0]
            memory_relevance: Memory priming contribution [0.0, 1.0]

        Returns:
            Tuple of (normalized_priority_score, priority_level)
        """
        raise NotImplementedError


class RelevancePipeline(Protocol):
    """Protocol for relevance computation stages."""

    @abstractmethod
    def compute_relevance(
        self,
        target_id: str,
        goal_weight: float,
        task_weight: float,
        memory_weight: float,
        temporal_factor: float = 1.0,
    ) -> Tuple[float, Tuple[str, ...]]:
        """
        Compute relevance score and reasons for a target.

        Args:
            target_id: Target identifier
            goal_weight: Goal alignment weight [0.0, 1.0]
            task_weight: Task alignment weight [0.0, 1.0]
            memory_weight: Memory priming weight [0.0, 1.0]
            temporal_factor: Time-based relevance modifier

        Returns:
            Tuple of (relevance_score, reason_list)
        """
        raise NotImplementedError


class CompetitionPipeline(Protocol):
    """Protocol for competition resolution stages."""

    @abstractmethod
    def resolve_competition(
        self,
        candidates: Tuple[str, ...],
        priorities: Mapping[str, float],
    ) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        """
        Resolve competition between candidates.

        Args:
            candidates: List of candidate target IDs
            priorities: Mapping of target_id -> priority score

        Returns:
            Tuple of (winners, losers) based on competition rules
        """
        raise NotImplementedError


class SuppressionPipeline(Protocol):
    """Protocol for suppression recommendation stages."""

    @abstractmethod
    def recommend_suppression(
        self,
        candidates: Tuple[str, ...],
        priorities: Mapping[str, float],
        threshold: float = 0.3,
    ) -> Tuple[Tuple[str, ...], Mapping[str, float]]:
        """
        Recommend targets for suppression.

        Args:
            candidates: List of candidate target IDs
            priorities: Mapping of target_id -> priority score
            threshold: Priority below which suppression is recommended

        Returns:
            Tuple of (suppressed_targets, inhibition_strengths)
        """
        raise NotImplementedError


class PrecisionPipeline(Protocol):
    """Protocol for precision estimation stages."""

    @abstractmethod
    def estimate_precision(
        self,
        target_id: str,
        priority: float,
        confidence: float = 0.95,
    ) -> Tuple[float, PrecisionBandwidth]:
        """
        Estimate optimal precision for a focus target.

        Args:
            target_id: Target identifier
            priority: Priority score [0.0, 1.0]
            confidence: Confidence in the assessment [0.0, 1.0]

        Returns:
            Tuple of (precision_estimate, bandwidth_selection)
        """
        raise NotImplementedError


class PersistencePipeline(Protocol):
    """Protocol for persistence policy stages."""

    @abstractmethod
    def compute_persistence(
        self,
        target_id: str,
        current_priority: float,
        maintenance_count: int = 0,
    ) -> Tuple[float, PersistenceMode]:
        """
        Compute persistence policy for a focus target.

        Args:
            target_id: Target identifier
            current_priority: Current priority score [0.0, 1.0]
            maintenance_count: How many cycles already maintained

        Returns:
            Tuple of (persistence_score, persistence_mode)
        """
        raise NotImplementedError


class BiasPipeline(Protocol):
    """Protocol for bias computation stages."""

    @abstractmethod
    def compute_bias(
        self,
        target_id: str,
        goal_weight: float = 0.4,
        task_weight: float = 0.3,
        memory_weight: float = 0.2,
        temporal_weight: float = 0.1,
    ) -> Tuple[float, Tuple[BiasModality, ...]]:
        """
        Compute top-down bias for a focus target.

        Args:
            target_id: Target identifier
            goal_weight: Goal-based bias weight [0.0, 1.0]
            task_weight: Task-based bias weight [0.0, 1.0]
            memory_weight: Memory-based bias weight [0.0, 1.0]
            temporal_weight: Temporal bias weight [0.0, 1.0]

        Returns:
            Tuple of (bias_strength, active_biases_list)
        """
        raise NotImplementedError


class AllocationPipeline(Protocol):
    """Protocol for resource allocation stages."""

    @abstractmethod
    def allocate_resources(
        self,
        candidates: Tuple[str, ...],
        priorities: Mapping[str, float],
        total_budget: float = 1.0,
    ) -> Mapping[str, float]:
        """
        Allocate resources among focus targets.

        Args:
            candidates: List of candidate target IDs
            priorities: Mapping of target_id -> priority score
            total_budget: Total available resources [0.0, 1.0]

        Returns:
            Mapping of target_id -> allocated_resource_ratio
        """
        raise NotImplementedError


class AssessmentAggregation(Protocol):
    """Protocol for final assessment aggregation."""

    @abstractmethod
    def aggregate_assessment(
        self,
        priority_scores: Mapping[str, float],
        relevance_scores: Mapping[str, float],
        precision_estimates: Mapping[str, float],
        persistence_policies: Mapping[str, float],
        bias_signals: Mapping[str, float],
        allocation: Mapping[str, float],
    ) -> FocusAssessment:
        """
        Aggregate all computed values into final assessment.

        Args:
            priority_scores: target_id -> priority
            relevance_scores: target_id -> relevance
            precision_estimates: target_id -> precision
            persistence_policies: target_id -> persistence_score
            bias_signals: target_id -> bias_strength
            allocation: target_id -> resource_allocation

        Returns:
            Complete FocusAssessment object
        """
        raise NotImplementedError