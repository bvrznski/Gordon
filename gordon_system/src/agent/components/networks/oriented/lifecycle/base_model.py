# Oriented Network Base Lifecycle Models - Phase 4.7.9
# ======================================================

"""
Base lifecycle abstractions for semantic orientation evolution.

SEMANTIC PRINCIPLES:
    - All models are immutable (frozen dataclasses)
    - No runtime execution semantics
    - Pure semantic representation
    - Deterministic serialization support
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# BASE LIFECYCLE MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseLifecycleModel(ABC):
    """
    Abstract base class for all lifecycle representations.
    
    SEMANTIC ROLE:
        - Defines the contract for lifecycle models
        - Never represents runtime execution
        
    PROPERTIES:
        - Immutable: All lifecycle objects are frozen dataclasses
        - Deterministic: Same inputs produce same outputs
        - Semantic: Represents state, not behavior
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        """Set the model type after initialization."""
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        """Return the canonical model type name."""
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        """
        Validate input data against this lifecycle model.
        
        Returns:
            True if data is valid for this model, False otherwise
        """
        raise NotImplementedError
    
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize the model to a dictionary."""
        raise NotImplementedError


# =============================================================================
# BASE ACTIVATION MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseActivationModel(ABC):
    """
    Abstract base class for activation semantics.
    
    SEMANTIC ROLE:
        - Represents semantic availability of orientation
        - Never owns runtime execution
        
    OWNERSHIP:
        - Owns: Semantic activation context and requirements
        - Never owns: Execution engines, schedulers, resources
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        raise NotImplementedError


# =============================================================================
# BASE TRANSITION MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseTransitionModel(ABC):
    """
    Abstract base class for transition semantics.
    
    SEMANTIC ROLE:
        - Represents legal semantic transitions between states
        - Never executes runtime transitions
        
    OWNERSHIP:
        - Owns: Transition definitions and legality
        - Never owns: State machines, workflow engines
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        raise NotImplementedError


# =============================================================================
# BASE EVOLUTION MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseEvolutionModel(ABC):
    """
    Abstract base class for evolution semantics.
    
    SEMANTIC ROLE:
        - Represents semantic refinement and adaptation
        - Never performs learning or optimization
        
    OWNERSHIP:
        - Owns: Semantic evolution definitions
        - Never owns: Learning algorithms, optimizers
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        raise NotImplementedError


# =============================================================================
# BASE COMPLETION MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseCompletionModel(ABC):
    """
    Abstract base class for completion semantics.
    
    SEMANTIC ROLE:
        - Represents semantic fulfillment
        - Never terminates runtime execution
        
    OWNERSHIP:
        - Owns: Completion definitions and relationships
        - Never owns: Runtime shutdown, termination
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        raise NotImplementedError


# =============================================================================
# BASE ARCHIVE MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseArchiveModel(ABC):
    """
    Abstract base class for archival semantics.
    
    SEMANTIC ROLE:
        - Represents semantic closure
        - Never owns persistence systems
        
    OWNERSHIP:
        - Owns: Archival definitions and relationships
        - Never owns: Storage, databases
    """
    
    model_type: str = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "model_type", self._get_model_type())
    
    @abstractmethod
    def _get_model_type(self) -> str:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def validate(cls, data: dict[str, Any]) -> bool:
        raise NotImplementedError


__all__ = [
    "BaseLifecycleModel",
    "BaseActivationModel",
    "BaseTransitionModel",
    "BaseEvolutionModel",
    "BaseCompletionModel",
    "BaseArchiveModel",
]