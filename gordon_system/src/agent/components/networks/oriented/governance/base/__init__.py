# Oriented Network Governance Base Abstractions
# =============================================

"""
Base Abstraction Framework for Oriented Network Governance (Phase 4.7.11)

This module provides the foundational abstractions that govern all semantic
governance within the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic operations
    - Repository-independent

BASE ABSTRACTIONS:

BasePolicyModel
    The abstract base for all policy models.
    Defines semantic contracts without implementation.

BaseGovernanceModel
    The abstract base for governance context models.
    Defines immutable governance contexts.

BaseComplianceModel
    The abstract base for compliance models.
    Defines semantic conformance without enforcement.

BaseConstraintModel
    The abstract base for constraint models.
    Defines architectural limitations without enforcement.

BasePermissionModel
    The abstract base for permission models.
    Defines semantic permissions without authorization.

BaseObligationModel
    The abstract base for obligation models.
    Defines mandatory requirements without enforcement.

BaseExceptionModel
    The abstract base for exception models.
    Defines explicit exceptions to governance rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


@dataclass(frozen=True)
class BasePolicyModel(ABC):
    """
    Abstract base for all policy models.
    
    Every policy model must implement:
        - policy_id: Unique identifier
        - version: Semantic version
        - authority: Source of authority
        - semantics: Policy meaning
        
    INVARIANTS:
        BPM-INV-001: Policy is immutable
        BPM-INV-002: Policy never executes runtime logic
        BPM-INV-003: Policy defines semantic rules only
    """
    
    policy_id: str
    """Unique policy identifier"""
    
    version: int = 1
    """Semantic version (>= 1)"""
    
    authority: Optional[str] = None
    """Source of authority (Constitution or higher policy)"""
    
    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check if policy is semantically valid.
        
        Returns:
            True if policy conforms to governance rules
        """
        pass
    
    @abstractmethod
    def validate_contract(self, contract_id: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate against a specific contract.
        
        Args:
            contract_id: Contract identifier to validate against
            
        Returns:
            (is_valid, errors) tuple
        """
        pass


@dataclass(frozen=True)
class BaseGovernanceModel(ABC):
    """
    Abstract base for governance context models.
    
    Every governance model must implement:
        - context_id: Unique identifier
        - scope: Bounded governance scope
        - authority: Source of governing authority
        
    INVARIANTS:
        BGM-INV-001: Context is immutable
        BGM-INV-002: Context never executes runtime logic
        BGM-INV-003: Context represents semantic boundaries only
    """
    
    context_id: str
    """Unique governance context identifier"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of governance application"""
    
    authority: Optional[str] = None
    """Source of governing authority"""
    
    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check if governance context is semantically valid.
        
        Returns:
            True if context conforms to governance rules
        """
        pass
    
    @abstractmethod
    def validate_boundary(self, entity_id: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate that an entity falls within governance boundary.
        
        Args:
            entity_id: Entity identifier to validate
            
        Returns:
            (is_valid, errors) tuple
        """


@dataclass(frozen=True)
class BaseComplianceModel(ABC):
    """
    Abstract base for compliance models.
    
    Every compliance model must implement:
        - compliance_id: Unique identifier
        - status: Compliance status (compliant/non-compliant)
        - basis: Semantic basis for compliance determination
        
    INVARIANTS:
        BCM-INV-001: Compliance is immutable
        BCM-INV-002: Compliance never performs enforcement
        BCM-INV-003: Compliance represents semantic conformance only
    """
    
    compliance_id: str
    """Unique compliance identifier"""
    
    status: str = "unknown"
    """Compliance status: compliant, non-compliant, conditional"""
    
    basis: Optional[str] = None
    """Semantic basis for determination"""
    
    @property
    @abstractmethod
    def is_compliant(self) -> bool:
        """
        Check if entity is semantically compliant.
        
        Returns:
            True if compliant with governance rules
        """
        pass
    
    @abstractmethod
    def get_violations(self) -> Tuple[str, ...]:
        """
        Get list of compliance violations.
        
        Returns:
            Tuple of violation descriptions
        """


@dataclass(frozen=True)
class BaseConstraintModel(ABC):
    """
    Abstract base for constraint models.
    
    Every constraint model must implement:
        - constraint_id: Unique identifier
        - type: Constraint category (architectural/semantic/lifecycle/etc.)
        - restriction: Description of the architectural limitation
        
    INVARIANTS:
        BCM-INV-001: Constraint is immutable
        BCM-INV-002: Constraint never executes runtime logic
        BCM-INV-003: Constraint defines semantic limitations only
    """
    
    constraint_id: str
    """Unique constraint identifier"""
    
    type: str = "general"
    """Constraint category"""
    
    restriction: Optional[str] = None
    """Description of architectural limitation"""
    
    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check if constraint is semantically valid.
        
        Returns:
            True if constraint conforms to governance rules
        """
        pass
    
    @abstractmethod
    def check_constraint(self, entity_id: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Check constraint against an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            (is_valid, errors) tuple
        """


@dataclass(frozen=True)
class BasePermissionModel(ABC):
    """
    Abstract base for permission models.
    
    Every permission model must implement:
        - permission_id: Unique identifier
        - operation: Allowed operation type
        - scope: Bounded permission scope
        
    INVARIANTS:
        BPM-INV-001: Permission is immutable
        BPM-INV-002: Permission never authorizes runtime execution
        BPM-INV-003: Permission defines semantic admissibility only
    """
    
    permission_id: str
    """Unique permission identifier"""
    
    operation: str = "read"
    """Allowed operation type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of permission application"""
    
    @property
    @abstractmethod
    def is_admissible(self) -> bool:
        """
        Check if permission is semantically admissible.
        
        Returns:
            True if admissible within governance framework
        """
        pass
    
    @abstractmethod
    def check_permission(self, entity_id: str, operation: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Check if operation is permitted for entity.
        
        Args:
            entity_id: Entity identifier
            operation: Operation to check
            
        Returns:
            (is_permitted, errors) tuple
        """


@dataclass(frozen=True)
class BaseObligationModel(ABC):
    """
    Abstract base for obligation models.
    
    Every obligation model must implement:
        - obligation_id: Unique identifier
        - requirement: Mandatory requirement type
        - scope: Bounded obligation scope
        
    INVARIANTS:
        BOM-INV-001: Obligation is immutable
        BOM-INV-002: Obligation never executes validation
        BOM-INV-003: Obligation defines semantic requirements only
    """
    
    obligation_id: str
    """Unique obligation identifier"""
    
    requirement: str = "validate"
    """Mandatory requirement type"""
    
    scope: Tuple[str, ...] = field(default_factory=tuple)
    """Bounded scope of obligation application"""
    
    @property
    @abstractmethod
    def is_mandatory(self) -> bool:
        """
        Check if obligation is mandatory within governance.
        
        Returns:
            True if obligation must be satisfied
        """
        pass
    
    @abstractmethod
    def check_requirement(self, entity_id: str) -> Tuple[bool, Tuple[str, ...]]:
        """
        Check if requirement is satisfied for entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            (is_satisfied, errors) tuple
        """


@dataclass(frozen=True)
class BaseExceptionModel(ABC):
    """
    Abstract base for exception models.
    
    Every exception model must implement:
        - exception_id: Unique identifier
        - type: Exception category
        - justification: Architectural justification
        
    INVARIANTS:
        BEM-INV-001: Exception is immutable
        BEM-INV-002: Exception never performs runtime overrides
        BEM-INV-003: Exception represents explicit deviations only
    """
    
    exception_id: str
    """Unique exception identifier"""
    
    type: str = "general"
    """Exception category"""
    
    justification: Optional[str] = None
    """Architectural justification for exception"""
    
    @property
    @abstractmethod
    def is_explicit(self) -> bool:
        """
        Check if exception is explicitly declared.
        
        Returns:
            True if exception is explicitly documented
        """
        pass
    
    @abstractmethod
    def get_scope(self) -> Tuple[str, ...]:
        """
        Get bounded scope of exception application.
        
        Returns:
            Tuple of entity IDs affected by exception
        """


__all__ = [
    "BasePolicyModel",
    "BaseGovernanceModel",
    "BaseComplianceModel",
    "BaseConstraintModel",
    "BasePermissionModel",
    "BaseObligationModel",
    "BaseExceptionModel",
]