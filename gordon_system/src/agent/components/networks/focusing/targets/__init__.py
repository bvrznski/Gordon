# Focusing Network Targets Module
# ================================

"""
Target models for the FocusingNetwork.

This module defines abstract target representations without computational
implementation. Concrete implementations belong to future phases.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class FocusTarget(ABC):
    """
    Abstract focus target representation.

    Defines the interface for focus targets without specifying how they are
    evaluated or prioritized.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this target."""

    @property
    @abstractmethod
    def modality(self) -> str:
        """The attention modality of this target."""

    @property
    @abstractmethod
    def source(self) -> str:
        """Origin of the focus candidate."""