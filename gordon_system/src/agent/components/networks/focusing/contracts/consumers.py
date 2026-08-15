# Focusing Network Consumer Contracts - Phase 4.2.8
# ==================================================

"""
Consumer contracts for the FocusingNetwork.

These define stable interfaces for consuming outputs from the FocusingNetwork
without exposing implementation details of what happens to those outputs.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class FocusInputConsumer(ABC):
    """
    Consumer of focus input data.

    This interface allows external systems to supply input to the
    FocusingNetwork without coupling them to its implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new input types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def provide_candidates(self) -> Tuple[str, ...]:
        """
        Provide a set of candidate target IDs for assessment.

        Returns:
            Tuple of candidate target IDs
        """


__all__ = [
    # Consumer interfaces (Network outputs)
    "FocusInputConsumer",
]