# Focusing Network Consumer Contracts
# =====================================

"""
Consumer contracts for the FocusingNetwork.

These define stable interfaces for consuming inputs to the network without
exposing implementation details of input sources.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class FocusInputConsumer(ABC):
    """
    Consumer of focus input data.

    This interface allows external systems to supply input to the
    FocusingNetwork without coupling them to its implementation.
    """

    @abstractmethod
    def provide_candidates(self) -> Tuple[str, ...]:
        """
        Provide a set of candidate target IDs for assessment.

        Returns:
            Tuple of candidate target IDs
        """