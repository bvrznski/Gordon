# Focusing Network Input Contracts
# ==================================

"""
Input contracts for the FocusingNetwork.

These define stable interfaces for providing focus candidates and context
to the network without exposing implementation details.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional

from gordon_system.src.agent.components.networks.focusing.enums import FocusModality


class FocusCandidateProvider(ABC):
    """
    Provider of focus candidates.

    This interface defines how external systems can supply focus targets to
    the FocusingNetwork without exposing internal implementation details.

    The provider NEVER owns the candidates - it only provides access.
    """

    @abstractmethod
    def get_candidates(self) -> Tuple[str, ...]:
        """
        Return the set of candidate target IDs.

        Returns:
            Tuple of unique candidate identifiers. Never None or empty unless
            no candidates are available.
        """

    @abstractmethod
    def get_modality(self, candidate_id: str) -> Optional[FocusModality]:
        """
        Return the modality for a given candidate.

        Args:
            candidate_id: The target ID to query

        Returns:
            FocusModality or None if unknown
        """


class FocusContextProvider(ABC):
    """
    Provider of focus context information.

    Context includes current state from higher layers that may influence
    focus allocation decisions without being part of the candidates themselves.
    """

    @abstractmethod
    def get_current_focus_strength(self) -> Optional[float]:
        """
        Return current overall focus strength (0.0 to 1.0).

        Returns:
            Current global focus intensity, or None if unavailable
        """

    @abstractmethod
    def get_active_targets(self) -> Tuple[str, ...]:
        """
        Return currently active focus target IDs.

        These are targets that have been allocated focus in the recent past
        and may continue to be maintained.
        """

    @abstractmethod
    def get_relevance_hint(self, candidate_id: str) -> Optional[float]:
        """
        Return a relevance hint from external systems.

        Args:
            candidate_id: The target ID to query

        Returns:
            Relevance score (0.0 to 1.0), or None if not available
        """