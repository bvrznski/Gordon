# Oriented Network Integration Base Abstractions
# ===============================================

"""
Base Integration Interface for Phase 4.7.6 Semantic Integration Contracts.

ARCHITECTURAL PRINCIPLES:
    - Base interface for all subsystem integration contracts
    - Immutable contract definitions (frozen dataclasses)
    - No runtime execution or scheduling
    - Semantic reference only
    
SEMANTIC INTEGRATION LAWS (Phase 4.7.6):
    INTEGRATION-LAW-001: The Oriented Network coordinates cognitive subsystems.
                         It never replaces them.
    INTEGRATION-LAW-009: Integration shall remain semantic.
    INTEGRATION-LAW-010: Integration shall remain deterministic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# BASE INTEGRATION ABSTRACTION
# =============================================================================

@dataclass(frozen=True)
class BaseIntegration(ABC):
    """
    Abstract base class for all Oriented Network Integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BI-INV-001: Integration never owns subsystem capabilities
        BI-INV-002: Integration is deeply immutable (frozen dataclass)
        BI-INV-003: Integration possesses stable semantic identity
        BI-INV-004: Integration possesses explicit ownership reference
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-001: The Oriented Network coordinates cognitive subsystems.
                             It never replaces them.
        INTEGRATION-LAW-009: Integration shall remain semantic.
        INTEGRATION-LAW-010: Integration shall remain deterministic.
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number (starts at 1)"""
    
    version: int = field(default=1)
    """Schema version for compatibility"""
    
    owner: str = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this integration"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize integration contract to dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseIntegration:
        """
        Create integration contract from dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the integration type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate integration contract against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
            
        INVARIANT: Validation is deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def references(self) -> Tuple[str, ...]:
        """
        Return explicit references to externally owned concepts.
        
        Returns:
            Tuple of reference identifiers
            
        SEMANTIC LAWS (Phase 4.7.6):
            INTEGRATION-LAW-013: Every reference shall be explicit
            INTEGRATION-LAW-014: Every dependency shall be explicit
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate integration on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} integration:\n{error_list}"
            )


# =============================================================================
# EXECUTIVE INTEGRATION BASE
# =============================================================================

@dataclass(frozen=True)
class BaseExecutiveIntegration(BaseIntegration):
    """
    Base class for Executive Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BEI-INV-001: Executive remains externally authoritative
        BEI-INV-002: Integration never owns executive control
        BEI-INV-003: Orientation may reference executive context
        BEI-INV-004: Integration shall never issue executive directives
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-002: Executive Network remains the sole owner of executive control.
        INTEGRATION-LAW-007: Integration never transfers ownership.
    """
    
    @property
    def references(self) -> Tuple[str, ...]:
        return ()
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        if self.version < 1:
            errors.append("version must be >= 1")
        return (len(errors) == 0, tuple(errors))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseExecutiveIntegration:
        raise NotImplementedError


# =============================================================================
# STRATEGY INTEGRATION BASE
# =============================================================================

@dataclass(frozen=True)
class BaseStrategyIntegration(BaseIntegration):
    """
    Base class for Strategy integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BSI-INV-001: Strategy remains externally authoritative
        BSI-INV-002: Integration never owns strategic cognition
        BSI-INV-003: Orientation may reference strategic intent
        BSI-INV-004: Integration shall never create strategy
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-003: Strategy remains the sole owner of strategic cognition.
        INTEGRATION-LAW-007: Integration never transfers ownership.
    """
    
    @property
    def references(self) -> Tuple[str, ...]:
        return ()
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        if self.version < 1:
            errors.append("version must be >= 1")
        return (len(errors) == 0, tuple(errors))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseStrategyIntegration:
        raise NotImplementedError


# =============================================================================
# PLANNING INTEGRATION BASE
# =============================================================================

@dataclass(frozen=True)
class BasePlanningIntegration(BaseIntegration):
    """
    Base class for Planning integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BPI-INV-001: Planning remains externally authoritative
        BPI-INV-002: Integration never owns planning capabilities
        BPI-INV-003: Orientation may request planning services
        BPI-INV-004: Integration shall never create plans
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-004: Planning remains the sole owner of planning.
        INTEGRATION-LAW-007: Integration never transfers ownership.
    """
    
    @property
    def references(self) -> Tuple[str, ...]:
        return ()
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        if self.version < 1:
            errors.append("version must be >= 1")
        return (len(errors) == 0, tuple(errors))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BasePlanningIntegration:
        raise NotImplementedError


# =============================================================================
# REASONING INTEGRATION BASE
# =============================================================================

@dataclass(frozen=True)
class BaseReasoningIntegration(BaseIntegration):
    """
    Base class for Reasoning integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BRI-INV-001: Reasoning remains externally authoritative
        BRI-INV-002: Integration never owns inference capabilities
        BRI-INV-003: Orientation may request reasoning services
        BRI-INV-004: Integration shall never perform reasoning
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-005: Reasoning remains the sole owner of inference.
        INTEGRATION-LAW-007: Integration never transfers ownership.
    """
    
    @property
    def references(self) -> Tuple[str, ...]:
        return ()
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        if self.version < 1:
            errors.append("version must be >= 1")
        return (len(errors) == 0, tuple(errors))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseReasoningIntegration:
        raise NotImplementedError


# =============================================================================
# DECISION INTEGRATION BASE
# =============================================================================

@dataclass(frozen=True)
class BaseDecisionIntegration(BaseIntegration):
    """
    Base class for Decision Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BDI-INV-001: Decision remains externally authoritative
        BDI-INV-002: Integration never owns decision formation
        BDI-INV-003: Orientation may request decision context
        BDI-INV-004: Integration shall never generate decisions
        
    SEMANTIC LAWS (Phase 4.7.6):
        INTEGRATION-LAW-006: Decision Network remains the sole owner of decision formation.
        INTEGRATION-LAW-007: Integration never transfers ownership.
    """
    
    @property
    def references(self) -> Tuple[str, ...]:
        return ()
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        if self.version < 1:
            errors.append("version must be >= 1")
        return (len(errors) == 0, tuple(errors))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseDecisionIntegration:
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BaseIntegration",
    "BaseExecutiveIntegration",
    "BaseStrategyIntegration",
    "BasePlanningIntegration",
    "BaseReasoningIntegration",
    "BaseDecisionIntegration",
]