# Knowledge SubModel - Phase 6.7
# ==============================

"""
SubModels: Nested models within larger models.

Large Models may contain nested SubModels, enabling hierarchical organization
of semantic knowledge while preserving independently versioned components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INTEGRATION KIND - How submodels integrate with parents
# =============================================================================


class IntegrationKind(Enum):
    """
    Types of integration between parent and child models.
    
    Defines the relationship semantics between nested models.
    """
    
    COMPOSITION = "composition"     # Child is part of parent's structure
    EXTENSION = "extension"         # Child extends parent's capabilities
    SPECIALIZATION = "specialization"  # Child specializes parent's abstraction
    AGGREGATION = "aggregation"     # Child contributes to parent's scope


# =============================================================================
# SUBMODEL - Canonical nested model structure
# =============================================================================


@dataclass(frozen=True)
class SubModel:
    """
    Canonical representation of a submodel in Gordon's knowledge system.
    
    Submodels enable hierarchical model organization while preserving
    independently versioned components.
    
    Fields:
        submodel_identity:     Unique identifier for this submodel reference
        parent_model:          ID of the parent model containing this submodel
        child_model:           ID of the nested/child model
        integration_kind:      How the submodel integrates with parent
        compatibility:         Compatibility requirements between models
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    submodel_identity: str              # Unique ID for this submodel reference
    
    # Parent-child relationship (required)
    parent_model: str                   # Parent model containing this submodel
    child_model: str                    # Nested child model
    
    # Integration semantics
    integration_kind: IntegrationKind = IntegrationKind.COMPOSITION
    
    # Compatibility constraints
    compatibility: Tuple[str, ...] = field(default_factory=tuple)  # Requirements
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_compositional(self) -> bool:
        """Check if this is a compositional integration."""
        return self.integration_kind == IntegrationKind.COMPOSITION
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert submodel to dictionary for serialization."""
        return {
            "submodel_identity": self.submodel_identity,
            "parent_model": self.parent_model,
            "child_model": self.child_model,
            "integration_kind": self.integration_kind.value if self.integration_kind else None,
            "compatibility": list(self.compatibility),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubModel":
        """Create submodel from dictionary."""
        integration_value = data.get("integration_kind", "composition")
        try:
            integration_kind = IntegrationKind(integration_value)
        except ValueError:
            integration_kind = IntegrationKind.COMPOSITION
        
        return cls(
            submodel_identity=data.get("submodel_identity", str(uuid.uuid4())),
            parent_model=data.get("parent_model", ""),
            child_model=data.get("child_model", ""),
            integration_kind=integration_kind,
            compatibility=tuple(data.get("compatibility", [])),
            provenance=dict(data.get("provenance", {})),
        )
    
    def update_integration(
        self,
        new_kind: IntegrationKind,
    ) -> "SubModel":
        """Create a revision with updated integration kind."""
        return SubModel(
            submodel_identity=self.submodel_identity,
            parent_model=self.parent_model,
            child_model=self.child_model,
            integration_kind=new_kind,
            compatibility=self.compatibility,
            provenance={
                **self.provenance,
                "integration_updated_at_utc": time.time(),
                "previous_integration": self.integration_kind.value if self.integration_kind else None,
                "new_integration": new_kind.value,
            },
        )
    
    def add_compatibility(
        self,
        requirement: str,
    ) -> "SubModel":
        """Create a revision with an additional compatibility requirement."""
        if requirement in self.compatibility:
            return self
        return SubModel(
            submodel_identity=self.submodel_identity,
            parent_model=self.parent_model,
            child_model=self.child_model,
            integration_kind=self.integration_kind,
            compatibility=self.compatibility + (requirement,),
            provenance={
                **self.provenance,
                "compatibility_added": requirement,
                "revised_at_utc": time.time(),
            },
        )


# =============================================================================
# SUBMODEL BUILDER
# =============================================================================


class SubModelBuilder:
    """
    Builds and validates submodel references.
    
    Ensures proper parent-child relationships and integration semantics.
    """
    
    def __init__(
        self,
        require_parent_child: bool = True,
        validate_integration_kind: bool = True,
    ):
        """
        Initialize the builder.
        
        Args:
            require_parent_child: Whether both parent and child are required
            validate_integration_kind: Whether to enforce integration rules
        """
        self._require_parent_child = require_parent_child
        self._validate_integration = validate_integration_kind
    
    def validate_submodel(
        self,
        submodel: SubModel,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a submodel reference.
        
        Args:
            submodel: The submodel to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        if not submodel.submodel_identity or len(submodel.submodel_identity) == 0:
            issues.append("Missing submodel identity")
        
        if self._require_parent_child:
            if not submodel.parent_model or len(submodel.parent_model) == 0:
                issues.append("Missing parent model reference")
            if not submodel.child_model or len(submodel.child_model) == 0:
                issues.append("Missing child model reference")
        
        # Validate integration kind
        if self._validate_integration and (
            submodel.integration_kind not in IntegrationKind
        ):
            issues.append(f"Invalid integration kind: {submodel.integration_kind}")
        
        return len(issues) == 0, issues
    
    def build_submodel(
        self,
        parent_model: str,
        child_model: str,
        integration_kind: IntegrationKind = IntegrationKind.COMPOSITION,
        compatibility: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> SubModel:
        """
        Build a new submodel reference.
        
        Args:
            parent_model: ID of the parent model
            child_model: ID of the nested child model
            integration_kind: How child integrates with parent
            compatibility: Compatibility requirements (optional)
            provenance: Provenance data (optional)
            
        Returns:
            A new submodel reference
        """
        return SubModel(
            submodel_identity=f"submodel:{uuid.uuid4().hex[:16]}",
            parent_model=parent_model,
            child_model=child_model,
            integration_kind=integration_kind,
            compatibility=tuple(compatibility or []),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def build_compositional_submodel(
        self,
        parent_model: str,
        child_model: str,
    ) -> SubModel:
        """
        Build a compositional submodel (convenience method).
        
        Args:
            parent_model: ID of the parent model
            child_model: ID of the nested child model
            
        Returns:
            A new compositional submodel reference
        """
        return self.build_submodel(
            parent_model=parent_model,
            child_model=child_model,
            integration_kind=IntegrationKind.COMPOSITION,
        )


__all__ = [
    "IntegrationKind",
    "SubModel",
    "SubModelBuilder",
]