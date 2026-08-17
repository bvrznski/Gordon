# Knowledge Model Descriptor - Phase 6.7
# =======================================

"""
Model Descriptors: Metadata about semantic models.

Descriptors expose model metadata independently of contents, enabling
model discovery, comparison and governance without evaluating full content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LIFECYCLE STATE - Model evolution
# =============================================================================


class LifecycleState(Enum):
    """
    States in the model lifecycle.
    
    Every model shall have an explicit lifecycle state indicating its current
    position in the semantic system pipeline.
    """
    
    CREATED = "created"           # Initial creation, not yet validated
    VALIDATING = "validating"     # Currently undergoing validation
    ACTIVE = "active"             # Valid and currently used
    REVISED = "revised"           # Revised version exists
    SUPERSEDED = "superseded"     # Replaced by newer version
    ARCHIVED = "archived"         # Historical record, not active
    INVALID = "invalid"           # Validation failed


class PublicationStatus(Enum):
    """
    Publication status of a model.
    
    Controls visibility and availability of model to reasoning systems.
    """
    
    DRAFT = "draft"               # Work in progress
    PRIVATE = "private"           # Internal use only
    SHARED = "shared"             # Available within system
    PUBLISHED = "published"       # Public release, stable


# =============================================================================
# MODEL DESCRIPTOR - Canonical metadata structure
# =============================================================================


@dataclass(frozen=True)
class ModelDescriptor:
    """
    Canonical representation of model metadata in Gordon's knowledge system.
    
    Descriptors expose metadata independently of model contents, enabling
    model discovery, comparison and governance without evaluating full content.
    
    Fields:
        model_identity:         Unique identifier for this model
        semantic_identity:      Immutable semantic identity (stable across revisions)
        model_kind:             Type of model (semantic, world, self, etc.)
        lifecycle_state:        Current position in lifecycle
        revision:               Revision number for traceability
        publication_status:     Visibility and availability status
        provenance:             Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    model_identity: str                 # Unique ID for this instance
    
    # Semantic identity - remains stable across revisions
    semantic_identity: str              # Stable identifier for the model concept
    
    # Model classification (required)
    model_kind: str                     # Kind of model
    
    # Lifecycle tracking (required)
    lifecycle_state: LifecycleState = LifecycleState.CREATED
    revision: int = 1
    
    # Publication control
    publication_status: PublicationStatus = PublicationStatus.DRAFT
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if descriptor has minimal required data."""
        return (
            len(self.model_identity) > 0 and
            len(self.semantic_identity) > 0 and
            self.lifecycle_state is not None
        )
    
    @property
    def is_active(self) -> bool:
        """Check if model is active and available for use."""
        return self.lifecycle_state == LifecycleState.ACTIVE
    
    @property
    def is_published(self) -> bool:
        """Check if model is published."""
        return self.publication_status in (
            PublicationStatus.SHARED,
            PublicationStatus.PUBLISHED
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert descriptor to dictionary for serialization."""
        return {
            "model_identity": self.model_identity,
            "semantic_identity": self.semantic_identity,
            "model_kind": self.model_kind,
            "lifecycle_state": self.lifecycle_state.value if self.lifecycle_state else None,
            "revision": self.revision,
            "publication_status": self.publication_status.value if self.publication_status else None,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelDescriptor":
        """Create descriptor from dictionary."""
        state_value = data.get("lifecycle_state", "created")
        try:
            lifecycle_state = LifecycleState(state_value)
        except ValueError:
            lifecycle_state = LifecycleState.CREATED
        
        pub_value = data.get("publication_status", "draft")
        try:
            publication_status = PublicationStatus(pub_value)
        except ValueError:
            publication_status = PublicationStatus.DRAFT
        
        return cls(
            model_identity=data.get("model_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            model_kind=data.get("model_kind", "unknown"),
            lifecycle_state=lifecycle_state,
            revision=int(data.get("revision", 1)),
            publication_status=publication_status,
            provenance=dict(data.get("provenance", {})),
        )
    
    def create_revision(
        self,
        new_state: Optional[LifecycleState] = None,
        provenance_update: Optional[Dict[str, Any]] = None,
    ) -> "ModelDescriptor":
        """
        Create a new revision of this descriptor.
        
        Args:
            new_state: New lifecycle state (optional)
            provenance_update: Additional provenance data (optional)
            
        Returns:
            New descriptor with incremented revision
        """
        return ModelDescriptor(
            model_identity=f"{self.model_identity}_r{self.revision + 1}",
            semantic_identity=self.semantic_identity,
            model_kind=self.model_kind,
            lifecycle_state=new_state or self.lifecycle_state,
            revision=self.revision + 1,
            publication_status=self.publication_status,
            provenance={
                **self.provenance,
                "previous_revision": self.revision,
                "previous_model_identity": self.model_identity,
                "revision_created_at_utc": time.time(),
                **(provenance_update or {}),
            },
        )
    
    def update_state(
        self,
        new_state: LifecycleState,
        provenance_update: Optional[Dict[str, Any]] = None,
    ) -> "ModelDescriptor":
        """
        Create a revision with updated lifecycle state.
        
        Args:
            new_state: The new lifecycle state
            provenance_update: Additional provenance data (optional)
            
        Returns:
            New descriptor with updated state
        """
        return ModelDescriptor(
            model_identity=self.model_identity,
            semantic_identity=self.semantic_identity,
            model_kind=self.model_kind,
            lifecycle_state=new_state,
            revision=self.revision,
            publication_status=self.publication_status,
            provenance={
                **self.provenance,
                "state_changed_at_utc": time.time(),
                "previous_state": self.lifecycle_state.value if self.lifecycle_state else None,
                "new_state": new_state.value,
                **(provenance_update or {}),
            },
        )


# =============================================================================
# DESCRIPTOR BUILDER
# =============================================================================


class DescriptorBuilder:
    """
    Builds and validates model descriptors.
    
    Ensures descriptors have proper identity and state structure.
    """
    
    def __init__(
        self,
        require_semantic_identity: bool = True,
        validate_lifecycle_transitions: bool = True,
    ):
        """
        Initialize the builder.
        
        Args:
            require_semantic_identity: Whether semantic_identity is required
            validate_lifecycle_transitions: Whether to enforce lifecycle rules
        """
        self._require_semantic_identity = require_semantic_identity
        self._validate_lifecycle_transitions = validate_lifecycle_transitions
    
    def validate_descriptor(
        self,
        descriptor: ModelDescriptor,
    ) -> Tuple[bool, List[str]]:
        """
        Validate a model descriptor.
        
        Args:
            descriptor: The descriptor to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        if not descriptor.model_identity or len(descriptor.model_identity) == 0:
            issues.append("Missing model identity")
        
        if self._require_semantic_identity and (
            not descriptor.semantic_identity or len(descriptor.semantic_identity) == 0
        ):
            issues.append("Missing semantic identity")
        
        # Check lifecycle state
        if descriptor.lifecycle_state is None:
            issues.append("Missing lifecycle state")
        
        # Validate lifecycle transitions
        if self._validate_lifecycle_transitions and (
            descriptor.lifecycle_state not in LifecycleState
        ):
            issues.append(f"Invalid lifecycle state: {descriptor.lifecycle_state}")
        
        # Check revision integrity
        if descriptor.revision < 1:
            issues.append("Revision must be positive")
        
        return len(issues) == 0, issues
    
    def build_descriptor(
        self,
        model_kind: str,
        semantic_identity: Optional[str] = None,
        lifecycle_state: LifecycleState = LifecycleState.CREATED,
        revision: int = 1,
        publication_status: PublicationStatus = PublicationStatus.DRAFT,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> ModelDescriptor:
        """
        Build a new model descriptor.
        
        Args:
            model_kind: The kind of model being described
            semantic_identity: Semantic identity (auto-generated if missing)
            lifecycle_state: Initial lifecycle state
            revision: Initial revision number
            publication_status: Publication status
            provenance: Provenance data (optional)
            
        Returns:
            A new descriptor
        """
        return ModelDescriptor(
            model_identity=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity or f"model:{uuid.uuid4().hex[:16]}",
            model_kind=model_kind,
            lifecycle_state=lifecycle_state,
            revision=revision,
            publication_status=publication_status,
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


__all__ = [
    "LifecycleState",
    "PublicationStatus", 
    "ModelDescriptor",
    "DescriptorBuilder",
]