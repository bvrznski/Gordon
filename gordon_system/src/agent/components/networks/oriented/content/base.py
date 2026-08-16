# Oriented Network Base Content Abstractions - Phase 4.7.3
# =========================================================

"""
Base abstractions for all Oriented Network Content types.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-001: Every Content object represents semantic information
    ORIENTED-CONTENT-LAW-002: Every Content object is deeply immutable
    ORIENTED-CONTENT-LAW-003: Every Content object possesses stable semantic identity
    ORIENTED-CONTENT-LAW-004: Every Content object possesses explicit ownership
    ORIENTED-CONTENT-LAW-005: Every Content object possesses explicit authority
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum


# =============================================================================
# IDENTITY TYPES - Immutable references
# =============================================================================

ContentIdentity = str
"""
Unique identifier for a content instance.

Rules:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Content hash, source system ID with context prefix.
"""

ContentRevision = int
"""
Monotonically increasing revision number for content.

Rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Meaning change always requires revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""

ContentVersion = int
"""
Schema version for content compatibility.

Rules:
    - Version N+1 may add fields but not remove existing ones
    - Schema changes require version increment
    - Compatibility is determined by version comparison
"""


# =============================================================================
# AUTHORITY TYPES - Ownership and authority specifications
# =============================================================================

class ContentAuthority(Enum):
    """
    Authority types that can own content.
    
    SEMANTIC LAWS:
        ORIENTED-CONTENT-LAW-011: Orientation Content owns semantic Orientation representations only
        ORIENTED-CONTENT-LAW-012 through 018: Reference ownership constraints
    """
    
    ORIENTED_NETWORK = "oriented_network"
    """Owned by the Oriented Network (orientation semantics)"""
    
    GOAL_SYSTEM = "goal_system"
    """Owned by Goal System ( Goals remain externally authoritative)"""
    
    EXECUTIVE = "executive"
    """Owned by Executive Network"""
    
    PLANNING = "planning"
    """Owned by Planning subsystem"""
    
    DECISION_NETWORK = "decision_network"
    """Owned by Decision Network"""
    
    WORKSPACE = "workspace"
    """Owned by Workspace Network"""
    
    WORKING_MEMORY = "working_memory"
    """Owned by Working Memory subsystem"""
    
    ATTENTION = "attention"
    """Owned by Attention Network"""
    
    STRATEGY = "strategy"
    """Owned by Strategy subsystem"""
    
    COGNITIVE_ARTIFACT = "cognitive_artifact"
    """External cognitive artifact (not owned by any subsystem)"""


ContentOwner = str
"""
Architectural owner of content.

Format: "subsystem_name" or "external:<source>"
Examples:
    "oriented_network"
    "goal_system"
    "external:planning_subsystem"
"""

# =============================================================================
# BASE CONTENT INTERFACE
# =============================================================================

@dataclass(frozen=True)
class BaseContent(ABC):
    """
    Abstract base class for all Oriented Network Content.
    
    ARCHITECTURAL INVARIANTS:
        BC-INV-001: Content never represents runtime execution
        BC-INV-002: Content is deeply immutable (frozen dataclass)
        BC-INV-003: Content possesses stable semantic identity
        BC-INV-004: Content possesses explicit ownership
        BC-INV-005: Content possesses immutable provenance
        
    NOT RESPONSIBLE FOR:
        - Runtime execution
        - State management
        - Scheduling or coordination
        - Planning or reasoning
    """
    
    identity: ContentIdentity
    """Unique semantic identifier"""
    
    revision: ContentRevision = 1
    """Semantic revision number (starts at 1)"""
    
    version: ContentVersion = 1
    """Schema version for compatibility"""
    
    authority: ContentAuthority = ContentAuthority.ORIENTED_NETWORK
    """Source of authority for this content"""
    
    owner: ContentOwner = "oriented_network"
    """Architectural owner of this content"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize content to a dictionary.
        
        Returns:
            Dictionary representation suitable for JSON serialization.
            
        INVARIANT: Serialization must be deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaseContent:
        """
        Create content from a dictionary.
        
        Args:
            data: Dictionary produced by to_dict()
            
        Returns:
            New instance of the content type
            
        INVARIANT: from_dict(to_dict(x)) == x for valid inputs
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate content against semantic requirements.
        
        Returns:
            (is_valid, list_of_errors) tuple
            
        INVARIANT: Validation is deterministic (same input = same output)
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_provenance(self) -> Dict[str, Any]:
        """
        Get immutable provenance information.
        
        Returns:
            Dictionary containing provenance data (created_by, derived_from, etc.)
            
        INVARIANT: Provenance is immutable and cannot be modified after creation
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        """
        Get immutable lineage (ancestral chain).
        
        Returns:
            Tuple of ancestor identity values from most recent to oldest
            
        INVARIANT: Lineage is immutable and cannot be modified after creation
        """
        raise NotImplementedError
    
    def __post_init__(self) -> None:
        """Validate content on construction."""
        is_valid, errors = self.validate()
        if not is_valid:
            error_list = "\n".join(errors)
            raise ValueError(
                f"Invalid {self.__class__.__name__} content:\n{error_list}"
            )

# =============================================================================
# CONTENT TYPE TAGS
# =============================================================================

class ContentTypeTag(Enum):
    """
    Canonical tags for categorizing content by type.
    
    Used for semantic validation and routing without runtime dependencies.
    """
    
    # Orientation Content
    CURRENT_ORIENTATION = "current_orientation"
    DESIRED_ORIENTATION = "desired_orientation"
    CANDIDATE_ORIENTATION = "candidate_orientation"
    HISTORICAL_ORIENTATION = "historical_orientation"
    SUSPENDED_ORIENTATION = "suspended_orientation"
    RECOVERED_ORIENTATION = "recovered_orientation"
    
    # Reference Content
    GOAL_REFERENCE = "goal_reference"
    OBJECTIVE_REFERENCE = "objective_reference"
    TASK_REFERENCE = "task_reference"
    MISSION_REFERENCE = "mission_reference"
    PURPOSE_REFERENCE = "purpose_reference"
    CONSTRAINT_REFERENCE = "constraint_reference"
    DEPENDENCY_REFERENCE = "dependency_reference"
    
    # Context Content
    MISSION_CONTEXT = "mission_context"
    GOAL_CONTEXT = "goal_context"
    OBJECTIVE_CONTEXT = "objective_context"
    TASK_CONTEXT = "task_context"
    
    # Assessment Content
    PROGRESS_ASSESSMENT = "progress_assessment"
    ALIGNMENT_ASSESSMENT = "alignment_assessment"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    
    # Relationship Content
    GOAL_RELATIONSHIP = "goal_relationship"
    OBJECTIVE_RELATIONSHIP = "objective_relationship"
    TASK_RELATIONSHIP = "task_relationship"
    
    # Metadata Content
    CONTENT_IDENTITY = "content_identity"
    CONTENT_REVISION = "content_revision"
    CONTENT_VERSION = "content_version"
    CONTENT_AUTHORITY = "content_authority"
    CONTENT_OWNER = "content_owner"


__all__ = [
    "ContentIdentity",
    "ContentRevision",
    "ContentVersion",
    "ContentAuthority",
    "ContentOwner",
    "BaseContent",
    "ContentTypeTag",
]