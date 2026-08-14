# Focusing Network Provider Contracts
# =====================================

"""
Provider contracts for the FocusingNetwork.

These define stable interfaces for providing state and configuration to
the network without exposing implementation details.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class FocusStateProvider(ABC):
    """
    Provider of current focus state information.

    This interface provides access to existing focus targets and their
    associated metadata without coupling to the FocusingNetwork implementation.
    """

    @abstractmethod
    def get_current_focus_targets(self) -> Tuple[str, ...]:
        """
        Get currently active focus target IDs.

        These are targets that are currently receiving sustained attention.

        Returns:
            Tuple of active target IDs
        """

    @abstractmethod
    def get_target_strength(self, target_id: str) -> float:
        """
        Get the current strength for a focus target.

        Args:
            target_id: The target to query

        Returns:
            Strength value (0.0 to 1.0)
        """


class FocusConfigurationProvider(ABC):
    """
    Provider of configuration for focus allocation.

    This interface provides policy and constraint information without
    coupling to the FocusingNetwork implementation.
    """

    @abstractmethod
    def get_max_focus_targets(self) -> int:
        """
        Get maximum number of simultaneous focus targets allowed.

        Returns:
            Maximum target count (positive integer)
        """

    @abstractmethod
    def get_suppression_threshold(self) -> float:
        """
        Get the suppression threshold for competitive inhibition.

        Targets below this priority may be suppressed by higher-priority ones.

        Returns:
            Threshold value (0.0 to 1.0)
        """

    @abstractmethod
    def get_persistence_mode(self) -> str:
        """
        Get the current persistence mode setting.

        Returns:
            Mode string: 'transient', 'sustained', 'locked', or 'adaptive'
        """