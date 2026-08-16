# Oriented Network Base Evaluation Models - Phase 4.7.10
# =========================================================

"""
Base abstractions for semantic evaluation within the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

SEMANTIC LAWS:
    ORIENTED-EVALUATION-LAW-001 through 010: Evaluation remains descriptive
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references for evaluation
# =============================================================================

EvaluationIdentity = str
"""
Unique identifier for an evaluation instance.

Rules:
    - Deterministically derived from input orientation and context
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Hash of orientation identity + evaluation timestamp + schema version.
"""

EvaluationRevision = int
"""
Monotonically increasing revision number for evaluation.

Rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Meaning change always requires revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""

EvaluationVersion = int
"""
Schema version for evaluation compatibility.

Rules:
    - Version N+1 may add fields but not remove existing ones
    - Schema changes require version increment
    - Compatibility is determined by version comparison
"""


# =============================================================================
# OWNERSHIP TYPES
# =============================================================================

class EvaluationAuthority(Enum):
    """
    Authority types that can own evaluation results.
    
    SEMANTIC LAWS:
        ORIENTED-EVALUATION-LAW-011: Orientation Evaluation owns semantic 
            assessment only
        ORIENTED-EVALUATION-LAW-012 through 018: Reference ownership constraints
    """
    
    ORIENTED_NETWORK = "oriented_network"
    """Owned by the Oriented Network (semantic evaluation)"""
    
    GOAL_SYSTEM = "goal_system"
    """Owned by Goal System (evaluation reference only)"""
    
    EXECUTIVE = "executive"
    """Owned by Executive Network"""
    
    PLANNING = "planning"
    """Owned by Planning subsystem"""
    
    DECISION_NETWORK = "decision_network"
    """Owned by Decision Network"""
    
    WORKSPACE = "workspace"
    """Owned by Workspace Network"""
    
    COGNITIVE_ARTIFACT = "cognitive_artifact"
    """External cognitive artifact (not owned by any subsystem)"""


EvaluationOwner = str
"""
Architectural owner of evaluation.

Format: "subsystem_name" or "external:<source>"
Examples:
    "oriented_network"
    "goal_system"
    "external:planning_subsystem"
"""


# =============================================================================
# BASE EVALUATION MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseEvaluationModel(ABC):
    """
    Abstract base class for all Oriented Network evaluation models.
    
    ARCHITECTURAL INVARIANTS:
        BE-INV-001: Evaluation never represents runtime execution
        BE-INV-002: Evaluation is deeply immutable (frozen dataclass)
        BE-INV-003: Evaluation possesses stable semantic identity
        BE-INV-004: Evaluation possesses explicit ownership
        BE-INV-005: Evaluation possesses immutable provenance
        
    NOT RESPONSIBLE FOR:
        - Runtime execution
        - State management
        - Scheduling or coordination
        - Planning or reasoning
        - Correction or repair
    """
    
    identity: EvaluationIdentity
    """Unique semantic identifier"""
    
    revision: EvaluationRevision = 1
    """Semantic revision number (starts at 1)"""
    
    version: EvaluationVersion = 1
    """Schema version for compatibility"""
    
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    """Source of authority for this evaluation"""
    
    owner: EvaluationOwner = "oriented_network"
    """Architectural owner of this evaluation"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize evaluation to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseEvaluationModel:
        """
        Create evaluation from a dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the evaluation type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate evaluation against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
            
        INVARIANT: Validation is deterministic (same input = same output)
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate evaluation on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} evaluation:\n{error_list}"
            )


# =============================================================================
# BASE COHERENCE MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseCoherenceModel(ABC):
    """
    Abstract base class for coherence evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic compatibility between orientation elements
        - Never resolves inconsistencies
        - Never repairs structures
        
    OWNERSHIP CONTRACT:
        - Owns: coherence semantics, relationships, context
        - Never owns: resolution, repair, runtime synchronization
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseCoherenceModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


# =============================================================================
# BASE CONSISTENCY MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseConsistencyModel(ABC):
    """
    Abstract base class for consistency evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic agreement between orientation elements
        - Never enforces correctness
        - Never modifies relationships
        
    OWNERSHIP CONTRACT:
        - Owns: consistency semantics, relationships, validation
        - Never owns: enforcement, correction, behavioural modification
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseConsistencyModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


# =============================================================================
# BASE CONFLICT MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseConflictModel(ABC):
    """
    Abstract base class for conflict evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic incompatibility between orientation elements
        - Never performs arbitration
        - Never prioritizes alternatives
        
    OWNERSHIP CONTRACT:
        - Owns: conflict semantics, classification, relationships
        - Never owns: arbitration, prioritization, resolution
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseConflictModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


# =============================================================================
# BASE INTEGRITY MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseIntegrityModel(ABC):
    """
    Abstract base class for integrity evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic soundness of orientation structures
        - Never repairs structures
        - Never reconstructs relationships
        
    OWNERSHIP CONTRACT:
        - Owns: integrity semantics, relationships, context
        - Never owns: repair mechanisms, synchronization, recovery
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseIntegrityModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


# =============================================================================
# BASE ALIGNMENT MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseAlignmentModel(ABC):
    """
    Abstract base class for alignment evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic correspondence between orientation elements
        - Never changes Goals, Missions, Strategy
        
    OWNERSHIP CONTRACT:
        - Owns: alignment semantics, relationships, context
        - Never owns: strategic adaptation, executive control, planning decisions
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseAlignmentModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


# =============================================================================
# BASE VALIDITY MODEL
# =============================================================================

@dataclass(frozen=True)
class BaseValidityModel(ABC):
    """
    Abstract base class for validity evaluation models.
    
    SEMANTIC ROLE:
        - Describes semantic correctness of orientation
        - Never certifies runtime behaviour
        - Never modifies semantic models
        
    OWNERSHIP CONTRACT:
        - Owns: validity semantics, relationships, requirements
        - Never owns: certification, enforcement, correction
    """
    
    identity: EvaluationIdentity
    revision: EvaluationRevision = 1
    version: EvaluationVersion = 1
    authority: EvaluationAuthority = EvaluationAuthority.ORIENTED_NETWORK
    owner: EvaluationOwner = "oriented_network"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseValidityModel:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        raise NotImplementedError


__all__ = [
    "EvaluationIdentity",
    "EvaluationRevision",
    "EvaluationVersion",
    "EvaluationAuthority",
    "EvaluationOwner",
    "BaseEvaluationModel",
    "BaseCoherenceModel",
    "BaseConsistencyModel",
    "BaseConflictModel",
    "BaseIntegrityModel",
    "BaseAlignmentModel",
    "BaseValidityModel",
]