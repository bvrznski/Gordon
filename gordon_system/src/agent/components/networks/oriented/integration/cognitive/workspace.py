# Oriented Network Workspace Integration Contracts
# ================================================

"""
Workspace Network integration contracts for Phase 4.7.7.

OWNERSHIP:
    - Workspace Network owns: globally available cognitive representations,
      workspace organization, broadcasting
    - Oriented Network references: workspace state, projections, requirements

SEMANTIC INTEGRATION PRINCIPLES:
    - Never manage or own workspace
    - Consume workspace projections only
    - Express requirements, never implement them

INTEGRATION LAWS:
    ORIENTED-COGNITIVE-INTEGRATION-LAW-005: Workspace Network remains sole owner
    ORIENTED-COGNITIVE-INTEGRATION-LAW-018: Integration shall never manage Workspace
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# WORKSPACE REFERENCES - Semantic references to workspace concepts
# =============================================================================


@dataclass(frozen=True)
class WorkspaceReference:
    """
    Reference to a workspace concept without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every reference shall be explicit
        INTEGRATION-LAW-014: Every dependency shall be explicit
    """
    
    workspace_id: str = field(default="unnamed")
    """Unique identifier for the workspace concept being referenced"""
    
    reference_type: str = field(default="context")
    """Type of workspace reference (context, projection, requirement)"""
    
    visibility_level: Optional[str] = None
    """Visibility level hint (private, team, global - semantic only)"""
    
    retention_hint_seconds: Optional[float] = None
    """Optional retention duration hint in seconds"""
    
    @classmethod
    def context(cls, workspace_id: str) -> "WorkspaceReference":
        """
        Create a reference to workspace context.
        
        Args:
            workspace_id: ID of the workspace context
            
        Returns:
            New WorkspaceReference instance
        """
        return cls(workspace_id=workspace_id, reference_type="context")
    
    @classmethod
    def projection(cls, workspace_id: str) -> "WorkspaceReference":
        """
        Create a reference to a workspace projection.
        
        Args:
            workspace_id: ID of the workspace projection
            
        Returns:
            New WorkspaceReference instance
        """
        return cls(workspace_id=workspace_id, reference_type="projection")
    
    @classmethod
    def requirement(cls, workspace_id: str) -> "WorkspaceReference":
        """
        Create a reference to a workspace requirement.
        
        Args:
            workspace_id: ID of the workspace requirement
            
        Returns:
            New WorkspaceReference instance
        """
        return cls(workspace_id=workspace_id, reference_type="requirement")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "workspace_id": self.workspace_id,
            "reference_type": self.reference_type,
            "visibility_level": self.visibility_level,
            "retention_hint_seconds": self.retention_hint_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceReference":
        """Deserialize from dictionary."""
        return cls(
            workspace_id=data.get("workspace_id", "unnamed"),
            reference_type=data.get("reference_type", "context"),
            visibility_level=data.get("visibility_level"),
            retention_hint_seconds=data.get("retention_hint_seconds"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the reference."""
        errors = []
        if not self.workspace_id:
            errors.append("workspace_id must be non-empty")
        if self.reference_type not in ("context", "projection", "requirement"):
            errors.append(f"invalid reference_type: {self.reference_type}")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceReference:\n{error_str}")


# =============================================================================
# WORKSPACE CONTEXT - Immutable workspace state projection
# =============================================================================


@dataclass(frozen=True)
class WorkspaceContext:
    """
    Projection of current workspace state without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-018: Integration shall never manage Workspace
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
    """
    
    context_id: str = field(default="unnamed")
    """Unique identifier for this workspace context"""
    
    available_items: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of currently available items in workspace"""
    
    item_visibility_map: Dict[str, str] = field(default_factory=dict)
    """Visibility levels per item (semantic only)"""
    
    total_item_count: int = 0
    """Total number of items in workspace"""
    
    estimated_stable_seconds: Optional[float] = None
    """Estimated duration of current workspace state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceContext":
        """Deserialize from dictionary."""
        available = tuple(data.get("available_items", []))
        visibility = dict(data.get("item_visibility_map", {}))
        
        return cls(
            context_id=data.get("context_id", "unnamed"),
            available_items=available,
            item_visibility_map=visibility,
            total_item_count=int(data.get("total_item_count", 0)),
            estimated_stable_seconds=data.get("estimated_stable_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "context_id": self.context_id,
            "available_items": list(self.available_items),
            "item_visibility_map": dict(self.item_visibility_map),
            "total_item_count": self.total_item_count,
            "estimated_stable_seconds": self.estimated_stable_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the context."""
        errors = []
        if not self.context_id:
            errors.append("context_id must be non-empty")
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceContext:\n{error_str}")


# =============================================================================
# WORKSPACE PROJECTION - Information about workspace state
# =============================================================================


@dataclass(frozen=True)
class WorkspaceProjection:
    """
    Projection of workspace information without ownership.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-018: Integration shall never manage Workspace
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    projection_id: str = field(default="unnamed")
    """Unique identifier for this projection"""
    
    context: WorkspaceContext = field(default_factory=WorkspaceContext)
    """Current workspace context"""
    
    available_workspace_capacity: float = field(default=1.0)
    """Available workspace capacity as ratio (0.0 to 1.0)"""
    
    estimated_stable_seconds: Optional[float] = None
    """Estimated duration of current workspace state"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceProjection":
        """Deserialize from dictionary."""
        context_data = data.get("context", {})
        if isinstance(context_data, dict):
            context = WorkspaceContext.from_dict(context_data)
        else:
            context = WorkspaceContext()
        
        return cls(
            projection_id=data.get("projection_id", "unnamed"),
            context=context,
            available_workspace_capacity=float(data.get("available_workspace_capacity", 1.0)),
            estimated_stable_seconds=data.get("estimated_stable_seconds"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "projection_id": self.projection_id,
            "context": self.context.to_dict(),
            "available_workspace_capacity": self.available_workspace_capacity,
            "estimated_stable_seconds": self.estimated_stable_seconds,
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the projection."""
        errors = []
        if not self.projection_id:
            errors.append("projection_id must be non-empty")
        if not (0.0 <= self.available_workspace_capacity <= 1.0):
            errors.append(f"invalid capacity value: {self.available_workspace_capacity}")
        
        context_valid, context_errors = self.context.validate()
        if not context_valid:
            errors.extend(context_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceProjection:\n{error_str}")


# =============================================================================
# WORKSPACE RELATIONSHIP - Semantic relationship to workspace
# =============================================================================


@dataclass(frozen=True)
class WorkspaceRelationship:
    """
    Semantic relationship between orientation and workspace.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-013: Every relationship shall be explicit
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    relationship_id: str = field(default="unnamed")
    """Unique identifier for this relationship"""
    
    workspace_reference: WorkspaceReference = field(
        default_factory=lambda: WorkspaceReference()
    )
    """Reference to the workspace being related to"""
    
    relationship_type: str = field(default="consume")
    """Type of relationship (consume, reference, require)"""
    
    purpose: str = field(default="")
    """Semantic purpose of this relationship"""
    
    @classmethod
    def consume(cls, workspace_id: str, purpose: str = "") -> "WorkspaceRelationship":
        """
        Create a consumption relationship.
        
        Args:
            workspace_id: ID of the workspace to consume
            purpose: Semantic purpose
            
        Returns:
            New WorkspaceRelationship instance
        """
        return cls(
            relationship_id=f"consume_{workspace_id}",
            workspace_reference=WorkspaceReference(workspace_id, "context"),
            relationship_type="consume",
            purpose=purpose,
        )
    
    @classmethod
    def reference(cls, workspace_id: str, purpose: str = "") -> "WorkspaceRelationship":
        """
        Create a reference relationship.
        
        Args:
            workspace_id: ID of the workspace to reference
            purpose: Semantic purpose
            
        Returns:
            New WorkspaceRelationship instance
        """
        return cls(
            relationship_id=f"reference_{workspace_id}",
            workspace_reference=WorkspaceReference(workspace_id, "projection"),
            relationship_type="reference",
            purpose=purpose,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "workspace_reference": self.workspace_reference.to_dict(),
            "relationship_type": self.relationship_type,
            "purpose": self.purpose,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceRelationship":
        """Deserialize from dictionary."""
        ref_data = data.get("workspace_reference", {})
        if isinstance(ref_data, dict):
            workspace_ref = WorkspaceReference.from_dict(ref_data)
        else:
            workspace_ref = WorkspaceReference()
        
        return cls(
            relationship_id=data.get("relationship_id", "unnamed"),
            workspace_reference=workspace_ref,
            relationship_type=data.get("relationship_type", "consume"),
            purpose=data.get("purpose", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the relationship."""
        errors = []
        if not self.relationship_id:
            errors.append("relationship_id must be non-empty")
        if self.relationship_type not in ("consume", "reference", "require"):
            errors.append(f"invalid relationship_type: {self.relationship_type}")
        
        ref_valid, ref_errors = self.workspace_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceRelationship:\n{error_str}")


# =============================================================================
# WORKSPACE INFLUENCE - Semantic influence on workspace
# =============================================================================


@dataclass(frozen=True)
class WorkspaceInfluence:
    """
    Semantic influence that orientation may have on workspace.
    
    DESCRIBES what influence the Oriented Network can express without owning
    or implementing it. This is NOT a directive, only a semantic expectation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-018: Integration shall never manage Workspace
        INTEGRATION-LAW-026: Contracts are immutable
    """
    
    influence_id: str = field(default="unnamed")
    """Unique identifier for this influence"""
    
    influence_type: str = field(default="requirement")
    """Type of influence (requirement, expectation, suggestion)"""
    
    target_workspace: Optional[str] = None
    """Target workspace ID if applicable"""
    
    expected_state: Dict[str, Any] = field(default_factory=dict)
    """Expected state description (semantic only)"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceInfluence":
        """Deserialize from dictionary."""
        return cls(
            influence_id=data.get("influence_id", "unnamed"),
            influence_type=data.get("influence_type", "requirement"),
            target_workspace=data.get("target_workspace"),
            expected_state=dict(data.get("expected_state", {})),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "influence_id": self.influence_id,
            "influence_type": self.influence_type,
            "target_workspace": self.target_workspace,
            "expected_state": dict(self.expected_state),
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the influence."""
        errors = []
        if not self.influence_id:
            errors.append("influence_id must be non-empty")
        if self.influence_type not in ("requirement", "expectation", "suggestion"):
            errors.append(f"invalid influence_type: {self.influence_type}")
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceInfluence:\n{error_str}")


# =============================================================================
# WORKSPACE INTEGRATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class WorkspaceIntegrationContract:
    """
    Complete integration contract for Workspace Network.
    
    Combines all semantic elements needed for orientation to interact with
    the workspace system without ownership or implementation.
    
    SEMANTIC LAWS:
        INTEGRATION-LAW-005: Workspace Network remains sole owner
        INTEGRATION-LAW-018: Integration shall never manage Workspace
        INTEGRATION-LAW-026: Contracts are immutable (frozen dataclass)
        INTEGRATION-LAW-027: Deterministic serialization support
    """
    
    contract_id: str = field(default="unnamed")
    """Unique identifier for this integration contract"""
    
    revision: int = field(default=1)
    """Semantic revision number"""
    
    workspace_reference: WorkspaceReference = field(
        default_factory=lambda: WorkspaceReference()
    )
    """Primary workspace reference"""
    
    workspace_context: Optional[WorkspaceContext] = None
    """Current workspace context (if available)"""
    
    workspace_projection: Optional[WorkspaceProjection] = None
    """Workspace projection (if available)"""
    
    relationships: Tuple[WorkspaceRelationship, ...] = field(default_factory=tuple)
    """Semantic relationships to workspace"""
    
    influences: Tuple[WorkspaceInfluence, ...] = field(default_factory=tuple)
    """Semantic influences on workspace"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceIntegrationContract":
        """Deserialize from dictionary."""
        ref_data = data.get("workspace_reference", {})
        if isinstance(ref_data, dict):
            workspace_ref = WorkspaceReference.from_dict(ref_data)
        else:
            workspace_ref = WorkspaceReference()
        
        context_data = data.get("workspace_context")
        workspace_context: Optional[WorkspaceContext] = None
        if isinstance(context_data, dict):
            workspace_context = WorkspaceContext.from_dict(context_data)
        
        projection_data = data.get("workspace_projection")
        workspace_projection: Optional[WorkspaceProjection] = None
        if isinstance(projection_data, dict):
            workspace_projection = WorkspaceProjection.from_dict(projection_data)
        
        relationships_data = data.get("relationships", [])
        relationships = tuple(
            WorkspaceRelationship.from_dict(r) if isinstance(r, dict) else r
            for r in relationships_data
        )
        
        influences_data = data.get("influences", [])
        influences = tuple(
            WorkspaceInfluence.from_dict(i) if isinstance(i, dict) else i
            for i in influences_data
        )
        
        return cls(
            contract_id=data.get("contract_id", "unnamed"),
            revision=data.get("revision", 1),
            workspace_reference=workspace_ref,
            workspace_context=workspace_context,
            workspace_projection=workspace_projection,
            relationships=relationships,
            influences=influences,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contract_id": self.contract_id,
            "revision": self.revision,
            "workspace_reference": self.workspace_reference.to_dict(),
            "workspace_context": (
                self.workspace_context.to_dict()
                if self.workspace_context
                else None
            ),
            "workspace_projection": (
                self.workspace_projection.to_dict()
                if self.workspace_projection
                else None
            ),
            "relationships": [r.to_dict() for r in self.relationships],
            "influences": [i.to_dict() for i in self.influences],
        }
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """Validate the contract."""
        errors = []
        if not self.contract_id:
            errors.append("contract_id must be non-empty")
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        ref_valid, ref_errors = self.workspace_reference.validate()
        if not ref_valid:
            errors.extend(ref_errors)
        
        if self.workspace_context is not None:
            ctx_valid, ctx_errors = self.workspace_context.validate()
            if not ctx_valid:
                errors.extend(ctx_errors)
        
        if self.workspace_projection is not None:
            proj_valid, proj_errors = self.workspace_projection.validate()
            if not proj_valid:
                errors.extend(proj_errors)
        
        for rel in self.relationships:
            rel_valid, rel_errors = rel.validate()
            if not rel_valid:
                errors.extend(rel_errors)
        
        for inf in self.influences:
            inf_valid, inf_errors = inf.validate()
            if not inf_valid:
                errors.extend(inf_errors)
        
        return (len(errors) == 0, tuple(errors))
    
    def __post_init__(self) -> None:
        """Validate on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_str = "\n".join(errors)
            raise ValueError(f"Invalid WorkspaceIntegrationContract:\n{error_str}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "WorkspaceReference",
    "WorkspaceContext",
    "WorkspaceProjection",
    "WorkspaceRelationship",
    "WorkspaceInfluence",
    "WorkspaceIntegrationContract",
]