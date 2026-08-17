# Knowledge Model Component - Phase 6.7
# ======================================

"""
Model Components: References to artifacts that compose a model.

Components represent the semantic artifacts (concepts, assertions, relations,
beliefs) that form the content of a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# COMPONENT ROLE - Artifact contribution type
# =============================================================================


class ComponentRole(Enum):
    """
    Roles that components play within a model.
    
    Defines the semantic contribution of each artifact to the model structure.
    """
    
    DEFINING = "defining"           # Essential definition
    SUPPORTING = "supporting"       # Reinforces or extends
    CONTEXTUAL = "contextual"       # Sets boundaries/assumptions
    CONSTRAINING = "constraining"   # Defines limitations


# =============================================================================
# REQUIRED POLICY - Component requirement level
# =============================================================================


class RequiredPolicy(Enum):
    """
    Requirement levels for components.
    
    Controls whether a component is mandatory or optional.
    """
    
    REQUIRED = "required"           # Must be present
    OPTIONAL = "optional"           # May be absent without invalidating model


# =============================================================================
# MODEL COMPONENT - Canonical structure
# =============================================================================


@dataclass(frozen=True)
class ModelComponent:
    """
    Canonical representation of a component in Gordon's model system.
    
    Components reference semantic artifacts that contribute to a model.
    
    Fields:
        component_identity:    Unique identifier for this component reference
        parent_model:          ID of the model containing this component
        referenced_artifact:   Reference to the actual artifact (concept, assertion, etc.)
        contribution:          Semantic contribution type
        required:              Whether this component is mandatory
        provenance:            Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    component_identity: str             # Unique ID for this component reference
    
    # Parent model reference (required)
    parent_model: str                   # Model containing this component
    
    # Referenced artifact (required) - can be concept, assertion, relation, belief, etc.
    referenced_artifact: str            # Artifact identity being referenced
    
    # Contribution type
    contribution: ComponentRole = ComponentRole.SUPPORTING
    
    # Requirement level
    required: RequiredPolicy = RequiredPolicy.OPTIONAL
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_mandatory(self) -> bool:
        """Check if this component is mandatory."""
        return self.required == RequiredPolicy.REQUIRED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary for serialization."""
        return {
            "component_identity": self.component_identity,
            "parent_model": self.parent_model,
            "referenced_artifact": self.referenced_artifact,
            "contribution": self.contribution.value if self.contribution else None,
            "required": self.required.value if self.required else None,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelComponent":
        """Create component from dictionary."""
        contribution_value = data.get("contribution", "supporting")
        try:
            contribution = ComponentRole(contribution_value)
        except ValueError:
            contribution = ComponentRole.SUPPORTING
        
        required_value = data.get("required", "optional")
        try:
            required = RequiredPolicy(required_value)
        except ValueError:
            required = RequiredPolicy.OPTIONAL
        
        return cls(
            component_identity=data.get("component_identity", str(uuid.uuid4())),
            parent_model=data.get("parent_model", ""),
            referenced_artifact=data.get("referenced_artifact", ""),
            contribution=contribution,
            required=required,
            provenance=dict(data.get("provenance", {})),
        )
    
    def make_required(self) -> "ModelComponent":
        """Create a revision with this component marked as required."""
        return ModelComponent(
            component_identity=self.component_identity,
            parent_model=self.parent_model,
            referenced_artifact=self.referenced_artifact,
            contribution=self.contribution,
            required=RequiredPolicy.REQUIRED,
            provenance={
                **self.provenance,
                "required_at_utc": time.time(),
                "previous_required": self.required.value,
            },
        )
    
    def make_optional(self) -> "ModelComponent":
        """Create a revision with this component marked as optional."""
        return ModelComponent(
            component_identity=self.component_identity,
            parent_model=self.parent_model,
            referenced_artifact=self.referenced_artifact,
            contribution=self.contribution,
            required=RequiredPolicy.OPTIONAL,
            provenance={
                **self.provenance,
                "optional_at_utc": time.time(),
                "previous_required": self.required.value,
            },
        )
    
    def update_contribution(
        self,
        new_contribution: ComponentRole,
    ) -> "ModelComponent":
        """Create a revision with updated contribution type."""
        return ModelComponent(
            component_identity=self.component_identity,
            parent_model=self.parent_model,
            referenced_artifact=self.referenced_artifact,
            contribution=new_contribution,
            required=self.required,
            provenance={
                **self.provenance,
                "contribution_updated_at_utc": time.time(),
                "previous_contribution": self.contribution.value if self.contribution else None,
                "new_contribution": new_contribution.value,
            },
        )


# =============================================================================
# COMPONENT BUILDER
# =============================================================================


class ComponentBuilder:
    """
    Builds and validates model components.
    
    Ensures components have proper references and contribution types.
    """
    
    def __init__(
        self,
        require_artifact_reference: bool = True,
        validate_contribution_type: bool = True,
    ):
        """
        Initialize the builder.
        
        Args:
            require_artifact_reference: Whether artifact reference is required
            validate_contribution_type: Whether to enforce contribution rules
        """
        self._require_artifact_ref = require_artifact_reference
        self._validate_contribution = validate_contribution_type
    
    def validate_component(
        self,
        component: ModelComponent,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a model component.
        
        Args:
            component: The component to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        if not component.component_identity or len(component.component_identity) == 0:
            issues.append("Missing component identity")
        
        if not component.parent_model or len(component.parent_model) == 0:
            issues.append("Missing parent model reference")
        
        if self._require_artifact_ref and (
            not component.referenced_artifact or len(component.referenced_artifact) == 0
        ):
            issues.append("Missing artifact reference")
        
        # Validate contribution type
        if self._validate_contribution and (
            component.contribution not in ComponentRole
        ):
            issues.append(f"Invalid contribution type: {component.contribution}")
        
        return len(issues) == 0, issues
    
    def build_component(
        self,
        parent_model: str,
        referenced_artifact: str,
        contribution: ComponentRole = ComponentRole.SUPPORTING,
        required: RequiredPolicy = RequiredPolicy.OPTIONAL,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> ModelComponent:
        """
        Build a new model component.
        
        Args:
            parent_model: ID of the parent model
            referenced_artifact: ID of the artifact being referenced
            contribution: Semantic contribution type
            required: Requirement level
            provenance: Provenance data (optional)
            
        Returns:
            A new component reference
        """
        return ModelComponent(
            component_identity=f"component:{uuid.uuid4().hex[:16]}",
            parent_model=parent_model,
            referenced_artifact=referenced_artifact,
            contribution=contribution,
            required=required,
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )
    
    def build_required_component(
        self,
        parent_model: str,
        referenced_artifact: str,
        contribution: ComponentRole = ComponentRole.DEFINING,
    ) -> ModelComponent:
        """
        Build a required component (convenience method).
        
        Args:
            parent_model: ID of the parent model
            referenced_artifact: ID of the artifact being referenced
            contribution: Semantic contribution type
            
        Returns:
            A new required component reference
        """
        return self.build_component(
            parent_model=parent_model,
            referenced_artifact=referenced_artifact,
            contribution=contribution,
            required=RequiredPolicy.REQUIRED,
        )


__all__ = [
    "ComponentRole",
    "RequiredPolicy",
    "ModelComponent",
    "ComponentBuilder",
]