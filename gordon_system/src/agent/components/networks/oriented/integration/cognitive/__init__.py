# Oriented Network Cognitive Support Integration Package
# ======================================================

"""
Cognitive support integration contracts for Phase 4.7.7.

This package defines semantic integration contracts between the Oriented Network
and Gordon's cognitive support systems:

    - Attention Network (attentional allocation)
    - Motivation Network (motivational valuation)
    - Salience Network (salience computation)
    - Workspace Network (global availability)
    - Working Memory (active maintenance)

ARCHITECTURAL PRINCIPLES:
========================

1. SEMANTIC INTEGRATION ONLY
   All integration is semantic - no runtime behavior, no resource allocation,
   no algorithms.

2. OWNERSHIP PRESERVATION
   Every subsystem remains fully authoritative for its own responsibilities.
   Integration never transfers ownership.

3. PROJECTION CONSUMPTION
   The Oriented Network consumes projections from supporting systems.
   It never produces or modifies them.

4. REQUIREMENT EXPRESSION
   The Oriented Network may express requirements but never implements them.

INTEGRATION LAWS:
================

ORIENTED-COGNITIVE-INTEGRATION-LAW-001
    The Oriented Network coordinates cognitive subsystems.
    It never replaces them.

ORIENTED-COGNITIVE-INTEGRATION-LAW-002
    Every subsystem possesses exactly one architectural authority.

ORIENTED-COGNITIVE-INTEGRATION-LAW-009
    Integration shall remain semantic.

ORIENTED-COGNITIVE-INTEGRATION-LAW-010
    Integration shall remain deterministic.

ORIENTED-COGNITIVE-INTEGRATION-LAW-026
    Every integration contract shall be immutable (frozen dataclass).

ORIENTED-COGNITIVE-INTEGRATION-LAW-027
    Every integration contract shall support deterministic serialization.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional, Protocol, runtime_checkable

# =============================================================================
# BASE COGNITIVE INTEGRATION ABSTRACTIONS
# =============================================================================


@dataclass(frozen=True)
class BaseCognitiveIntegration:
    """
    Base class for all cognitive support integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BCI-INV-001: Integration never owns subsystem capabilities
        BCI-INV-002: Integration is deeply immutable (frozen dataclass)
        BCI-INV-003: Integration possesses stable semantic identity
        BCI-INV-004: Integration possesses explicit ownership reference
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-001: Coordinate, never replace
        INTEGRATION-LAW-026: Contracts are immutable
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    identity: str = field(default="unnamed")
    """Unique semantic identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number (starts at 1)"""
    
    version: int = field(default=1)
    """Schema version for compatibility tracking"""
    
    owner: str = field(default="oriented_network")
    """Architectural owner of the coordinated concept"""
    
    authority: str = field(default="semantic")
    """Source of authority for this integration"""
    
    schema_version: str = field(default="1.0.0")
    """Schema version string for compatibility"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize integration contract to dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseCognitiveIntegration":
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
            
        SEMANTIC LAWS:
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
# COGNITIVE PROTOCOLS (for runtime_checkable type checking)
# =============================================================================


@runtime_checkable
class AttentionIntegrationContract(Protocol):
    """
    Protocol for Attention Network integration.
    
    The Oriented Network may:
        - consume attentional context
        - express attentional requirements
        - reference attention projections
        
    The Oriented Network shall never:
        - allocate attention
        - reprioritize attention
        - control attentional resources
    """
    
    @property
    def identity(self) -> str: ...
    
    @property
    def authority(self) -> str: ...
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]: ...


@runtime_checkable
class MotivationIntegrationContract(Protocol):
    """
    Protocol for Motivation Network integration.
    
    The Oriented Network may:
        - consume motivational projections
        - express motivation requirements
        - reference motivation context
        
    The Oriented Network shall never:
        - compute motivation
        - fabricate motivational valuation
        - modify drive state
    """
    
    @property
    def identity(self) -> str: ...
    
    @property
    def authority(self) -> str: ...
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]: ...


@runtime_checkable
class SalienceIntegrationContract(Protocol):
    """
    Protocol for Salience Network integration.
    
    The Oriented Network may:
        - consume salience projections
        - reference salience context
        - express salience requirements
        
    The Oriented Network shall never:
        - compute salience
        - estimate relevance
        - detect novelty
    """
    
    @property
    def identity(self) -> str: ...
    
    @property
    def authority(self) -> str: ...
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]: ...


@runtime_checkable
class WorkspaceIntegrationContract(Protocol):
    """
    Protocol for Workspace Network integration.
    
    The Oriented Network may:
        - reference workspace state
        - consume workspace projections
        - express workspace requirements
        
    The Oriented Network shall never:
        - manage global availability
        - own workspace organization
        - control broadcasting
    """
    
    @property
    def identity(self) -> str: ...
    
    @property
    def authority(self) -> str: ...
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]: ...


@runtime_checkable
class WorkingMemoryIntegrationContract(Protocol):
    """
    Protocol for Working Memory integration.
    
    The Oriented Network may:
        - reference working memory state
        - consume working memory projections
        - express maintenance requirements
        
    The Oriented Network shall never:
        - manage active maintenance
        - own transient representations
        - control refresh policies
    """
    
    @property
    def identity(self) -> str: ...
    
    @property
    def authority(self) -> str: ...
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]: ...


# =============================================================================
# BASE SUBSYSTEM INTEGRATION CLASSES
# =============================================================================


@dataclass(frozen=True)
class BaseAttentionIntegration(BaseCognitiveIntegration):
    """
    Base class for Attention Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BAI-INV-001: Attention remains externally authoritative
        BAI-INV-002: Integration never owns attentional allocation
        BAI-INV-003: Orientation may reference attention context
        BAI-INV-004: Integration shall never allocate or reprioritize
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-002: Attention Network remains sole owner of attention
        INTEGRATION-LAW-007: Integration never transfers ownership
        INTEGRATION-LAW-015: Integration shall never allocate attention
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "owner": self.owner,
            "authority": self.authority,
            "schema_version": self.schema_version,
            "type": "base_attention_integration",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseAttentionIntegration":
        return cls(
            identity=data.get("identity", "unnamed"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            owner=data.get("owner", "oriented_network"),
            authority=data.get("authority", "semantic"),
            schema_version=data.get("schema_version", "1.0.0"),
        )


@dataclass(frozen=True)
class BaseMotivationIntegration(BaseCognitiveIntegration):
    """
    Base class for Motivation Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BMI-INV-001: Motivation remains externally authoritative
        BMI-INV-002: Integration never owns motivational valuation
        BMI-INV-003: Orientation may reference motivation context
        BMI-INV-004: Integration shall never compute motivation
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-003: Motivation Network remains sole owner of motivation
        INTEGRATION-LAW-007: Integration never transfers ownership
        INTEGRATION-LAW-016: Integration shall never compute motivation
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "owner": self.owner,
            "authority": self.authority,
            "schema_version": self.schema_version,
            "type": "base_motivation_integration",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseMotivationIntegration":
        return cls(
            identity=data.get("identity", "unnamed"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            owner=data.get("owner", "oriented_network"),
            authority=data.get("authority", "semantic"),
            schema_version=data.get("schema_version", "1.0.0"),
        )


@dataclass(frozen=True)
class BaseSalienceIntegration(BaseCognitiveIntegration):
    """
    Base class for Salience Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BSI-INV-001: Salience remains externally authoritative
        BSI-INV-002: Integration never owns salience computation
        BSI-INV-003: Orientation may reference salience context
        BSI-INV-004: Integration shall never compute salience
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-004: Salience Network remains sole owner of salience
        INTEGRATION-LAW-007: Integration never transfers ownership
        INTEGRATION-LAW-017: Integration shall never compute salience
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "owner": self.owner,
            "authority": self.authority,
            "schema_version": self.schema_version,
            "type": "base_salience_integration",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseSalienceIntegration":
        return cls(
            identity=data.get("identity", "unnamed"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            owner=data.get("owner", "oriented_network"),
            authority=data.get("authority", "semantic"),
            schema_version=data.get("schema_version", "1.0.0"),
        )


@dataclass(frozen=True)
class BaseWorkspaceIntegration(BaseCognitiveIntegration):
    """
    Base class for Workspace Network integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BWI-INV-001: Workspace remains externally authoritative
        BWI-INV-002: Integration never owns workspace organization
        BWI-INV-003: Orientation may reference workspace state
        BWI-INV-004: Integration shall never manage workspace
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-005: Workspace Network remains sole owner of global availability
        INTEGRATION-LAW-007: Integration never transfers ownership
        INTEGRATION-LAW-018: Integration shall never manage Workspace
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "owner": self.owner,
            "authority": self.authority,
            "schema_version": self.schema_version,
            "type": "base_workspace_integration",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseWorkspaceIntegration":
        return cls(
            identity=data.get("identity", "unnamed"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            owner=data.get("owner", "oriented_network"),
            authority=data.get("authority", "semantic"),
            schema_version=data.get("schema_version", "1.0.0"),
        )


@dataclass(frozen=True)
class BaseWorkingMemoryIntegration(BaseCognitiveIntegration):
    """
    Base class for Working Memory integration contracts.
    
    ARCHITECTURAL PRINCIPLES:
        BWMI-INV-001: Working Memory remains externally authoritative
        BWMI-INV-002: Integration never owns active maintenance
        BWMI-INV-003: Orientation may reference working memory state
        BWMI-INV-004: Integration shall never manage working memory
        
    SEMANTIC LAWS:
        INTEGRATION-LAW-006: Working Memory remains sole owner of active maintenance
        INTEGRATION-LAW-007: Integration never transfers ownership
        INTEGRATION-LAW-019: Integration shall never manage Working Memory
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "owner": self.owner,
            "authority": self.authority,
            "schema_version": self.schema_version,
            "type": "base_working_memory_integration",
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseWorkingMemoryIntegration":
        return cls(
            identity=data.get("identity", "unnamed"),
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            owner=data.get("owner", "oriented_network"),
            authority=data.get("authority", "semantic"),
            schema_version=data.get("schema_version", "1.0.0"),
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base abstractions
    "BaseCognitiveIntegration",
    "BaseAttentionIntegration",
    "BaseMotivationIntegration",
    "BaseSalienceIntegration",
    "BaseWorkspaceIntegration",
    "BaseWorkingMemoryIntegration",
    # Protocols for type checking
    "AttentionIntegrationContract",
    "MotivationIntegrationContract",
    "SalienceIntegrationContract",
    "WorkspaceIntegrationContract",
    "WorkingMemoryIntegrationContract",
]

# =============================================================================
# COGNITIVE INTEGRATION CONTRACTS FROM SUBMODULES
# =============================================================================

from .attention import (
    AttentionReference,
    AttentionContext,
    AttentionProjection,
    AttentionRelationship,
    AttentionInfluence,
    AttentionIntegrationContract,
)

from .motivation import (
    MotivationReference,
    MotivationContext,
    MotivationProjection,
    MotivationRelationship,
    MotivationInfluence,
    MotivationIntegrationContract,
)

from .salience import (
    SalienceReference,
    SalienceContext,
    SalienceProjection,
    SalienceRelationship,
    SalienceInfluence,
    SalienceIntegrationContract,
)

from .workspace import (
    WorkspaceReference,
    WorkspaceContext,
    WorkspaceProjection,
    WorkspaceRelationship,
    WorkspaceInfluence,
    WorkspaceIntegrationContract,
)

from .working_memory import (
    WorkingMemoryReference,
    WorkingMemoryContext,
    WorkingMemoryProjection,
    WorkingMemoryRelationship,
    WorkingMemoryInfluence,
    WorkingMemoryIntegrationContract,
)
