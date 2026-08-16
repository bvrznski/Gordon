# Oriented Network Base Abstractions
# ===================================

"""
Base abstractions for the Canonical Orientation Meta-Model.

These provide repository-wide semantic abstractions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseMetaModel(ABC):
    """Abstract base class for meta-model implementations."""
    pass


@dataclass(frozen=True)
class BaseMetaView(ABC):
    """Abstract base class for meta-view implementations."""
    pass


@dataclass(frozen=True)
class BaseMetaContext(ABC):
    """Abstract base class for meta-context implementations."""
    pass


@dataclass(frozen=True)
class BaseMetaRelationship(ABC):
    """Abstract base class for meta-relationship implementations."""
    pass


@dataclass(frozen=True)
class BaseMetaValidation(ABC):
    """Abstract base class for meta-validation implementations."""
    pass


@dataclass(frozen=True)
class BaseMetaArchitecture(ABC):
    """Abstract base class for meta-architecture implementations."""
    pass