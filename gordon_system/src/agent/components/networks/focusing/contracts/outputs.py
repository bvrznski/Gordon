# Focusing Network Output Contracts
# ===================================

"""
Output contracts for the FocusingNetwork.

These define stable interfaces for consuming focus assessments without exposing
implementation details of how they were computed.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class FocusAssessmentConsumer(ABC):
    """
    Consumer of focus assessment outputs.

    This interface defines how external systems can consume assessment results
    without being coupled to the implementation of the FocusingNetwork.
    """

    @abstractmethod
    def accept_assessment(self, assessment_id: str) -> bool:
        """
        Accept an assessment for processing.

        Args:
            assessment_id: The unique identifier of the assessment

        Returns:
            True if the assessment was accepted, False otherwise
        """

    @abstractmethod
    def get_confirmed_targets(self, assessment_id: str) -> Tuple[str, ...]:
        """
        Get confirmed focus targets from an assessment.

        These are targets that have been validated and approved for allocation.

        Args:
            assessment_id: The assessment to query

        Returns:
            Tuple of target IDs confirmed by the consumer
        """

    @abstractmethod
    def get_rejected_targets(self, assessment_id: str) -> Tuple[str, ...]:
        """
        Get rejected focus targets from an assessment.

        These are targets that were recommended but rejected by the consumer.

        Args:
            assessment_id: The assessment to query

        Returns:
            Tuple of target IDs rejected by the consumer
        """


class FocusDiagnosticsSink(ABC):
    """
    Consumer of diagnostic and telemetry data.

    This interface allows external systems to receive diagnostics without
    coupling them to the FocusingNetwork implementation.
    """

    @abstractmethod
    def log_diagnostic(self, message: str) -> None:
        """
        Log a diagnostic message.

        Args:
            message: The diagnostic information to record
        """

    @abstractmethod
    def record_metric(self, name: str, value: float) -> None:
        """
        Record a numeric metric.

        Args:
            name: The metric identifier
            value: The metric value
        """