# Knowledge Model Dependency - Phase 6.7
# =======================================

"""
Model Dependencies: Track relationships between models.

Dependencies track which models rely on other models, enabling proper
evolution and change propagation tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DEPENDENCY KIND - Type of dependency relationship
# =============================================================================


class DependencyKind(Enum):
    """
    Types of dependencies between models.
    
    Each dependency shall have an explicit kind indicating the nature of the
    relationship.
    """
    
    COMPOSITIONAL = "compositional"   # Model composed of dependency
    CAUSAL = "causal"                 # Causal influence on behavior
    SEMANTIC = "semantic"             # Shared semantic concepts
    VALIDATION = "validation"         # Used in validation process
    REFINEMENT = "refinement"         # Based on/refined from dependency


# =============================================================================
# MODEL DEPENDENCY - Canonical dependency record
# =============================================================================


@dataclass(frozen=True)
class ModelDependency:
    """
    Canonical representation of model dependencies in Gordon's knowledge system.
    
    Dependencies track which models rely on other models, enabling proper
    evolution and change propagation tracking.
    
    Fields:
        dependency_identity:   Unique identifier for this dependency
        source_model:          ID of the model with the dependency
        target_model:          ID of the model being depended upon
        dependency_kind:       Type of relationship
        required_revision:     Minimum required revision of target
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    dependency_identity: str            # Unique ID for this dependency
    
    # Source reference (required)
    source_model: str                   # Model that depends on something
    
    # Target reference (required)
    target_model: str                   # What the source model depends on
    
    # Dependency kind
    dependency_kind: DependencyKind = DependencyKind.COMPOSITIONAL
    
    # Version requirements
    required_revision: int = 1          # Minimum revision of target needed
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if dependency has minimal required data."""
        return (
            len(self.dependency_identity) > 0 and
            len(self.source_model) > 0 and
            len(self.target_model) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dependency to dictionary for serialization."""
        return {
            "dependency_identity": self.dependency_identity,
            "source_model": self.source_model,
            "target_model": self.target_model,
            "dependency_kind": self.dependency_kind.value if self.dependency_kind else None,
            "required_revision": self.required_revision,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelDependency":
        """Create dependency from dictionary."""
        kind_value = data.get("dependency_kind", "compositional")
        try:
            dependency_kind = DependencyKind(kind_value)
        except ValueError:
            dependency_kind = DependencyKind.COMPOSITIONAL
        
        return cls(
            dependency_identity=data.get("dependency_identity", str(uuid.uuid4())),
            source_model=data.get("source_model", ""),
            target_model=data.get("target_model", ""),
            dependency_kind=dependency_kind,
            required_revision=int(data.get("required_revision", 1)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        source_model: str,
        target_model: str,
        kind: DependencyKind = DependencyKind.COMPOSITIONAL,
        required_revision: int = 1,
    ) -> "ModelDependency":
        """
        Create a new model dependency record.
        
        Args:
            source_model: ID of the model with the dependency
            target_model: ID of what is being depended upon
            kind: Type of dependency relationship
            required_revision: Minimum revision needed of target
            
        Returns:
            A new dependency record
        """
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            source_model=source_model,
            target_model=target_model,
            dependency_kind=kind,
            required_revision=required_revision,
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


__all__ = [
    "DependencyKind",
    "ModelDependency",
]