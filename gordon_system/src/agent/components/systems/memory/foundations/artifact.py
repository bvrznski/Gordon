# Memory Artifact - Phase 5.1 Canonical Semantic Unit
# ====================================================

"""
Memory Artifact: The fundamental semantic unit of Gordon's memory system.

Every retained semantic object becomes a MemoryArtifact. Artifacts are:
    - Immutable after creation (revisions create new artifacts)
    - Globally uniquely identifiable
    - Possess stable identity across revisions
    - Have explicit validity, confidence, and uncertainty metrics
    - Participate in semantic relationships

Memory Artifact Kinds:
    - OBSERVATION: Perceived event or fact
    - EVENT: Recorded occurrence with context
    - EXPERIENCE: Subjective encounter with meaning
    - CONCEPT: Abstract idea or category
    - BELIEF: Accepted truth statement
    - PROCEDURE: Method for achieving outcome
    - GOAL: Intended state to achieve
    - PLAN: Strategy to reach goal
    - PREDICTION: Expected future state
    - FAILURE: Event that did not achieve intent
    - RELATIONSHIP: Semantic connection between artifacts
    - LOCATION: Spatial or conceptual position
    - PERSON: Identity reference
    - CONVERSATION: Exchange of information
    - IMAGE: Visual representation
    - DOCUMENT: Structured information object
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto
import time
import uuid


# =============================================================================
# MEMORY ARTIFACT KINDS
# =============================================================================


class MemoryArtifactKind(Enum):
    """
    Categories of memory artifacts.
    
    These classify what type of semantic object is stored but do NOT define
    storage - they are semantic classifications only.
    """
    
    # Core observation types
    OBSERVATION = "observation"           # Perceived event or fact
    EVENT = "event"                       # Recorded occurrence with context
    
    # Experience and cognition types
    EXPERIENCE = "experience"             # Subjective encounter with meaning
    CONCEPT = "concept"                   # Abstract idea or category
    BELIEF = "belief"                     # Accepted truth statement
    
    # Goal-directed types
    PROCEDURE = "procedure"               # Method for achieving outcome
    GOAL = "goal"                         # Intended state to achieve
    PLAN = "plan"                         # Strategy to reach goal
    
    # Prediction and reasoning types
    PREDICTION = "prediction"             # Expected future state
    FAILURE = "failure"                   # Event that did not achieve intent
    
    # Relationship and structure types
    RELATIONSHIP = "relationship"         # Semantic connection between artifacts
    LOCATION = "location"                 # Spatial or conceptual position
    PERSON = "person"                     # Identity reference
    CONVERSATION = "conversation"         # Exchange of information
    IMAGE = "image"                       # Visual representation
    DOCUMENT = "document"                 # Structured information object
    
    # Meta types
    REVISION = "revision"                 # Revision record
    PROJECTION = "projection"             # Projection snapshot
    QUERY_RESULT = "query_result"         # Query result artifact
    
    # Unknown/fallback type
    UNKNOWN = "unknown"                   # Unrecognized kind


# =============================================================================
# MEMORY ARTIFACT STATUS
# =============================================================================


class MemoryArtifactStatus(Enum):
    """
    Status of a memory artifact.
    
    Status reflects accessibility, not truth. A valid artifact may be inactive;
    an invalid artifact may be active.
    """
    
    ACTIVE = "active"                     # Currently accessible and usable
    DORMANT = "dormant"                   # Stored but not currently activated
    ARCHIVED = "archived"                 # Moved to archive storage
    SUPERSEDED = "superseded"             # Replaced by newer revision
    FORGOTTEN = "forgotten"               # Marked for eventual removal
    INVALID = "invalid"                   # Validation failed
    UNKNOWN = "unknown"                   # Status unknown


# =============================================================================
# SIMPLE PLACEHOLDER CLASSES (import at runtime in actual usage)
# =============================================================================


class MemoryIdentity:
    """Placeholder for MemoryIdentity - imports from identity.py at runtime."""
    pass


class MemoryConfidence:
    """Placeholder for MemoryConfidence - imports from confidence.py at runtime."""
    @classmethod
    def high(cls):
        return {"confidence": 0.9}

class MemoryUncertainty:
    """Placeholder for MemoryUncertainty - imports from uncertainty.py at runtime."""
    @classmethod
    def low(cls):
        return {"uncertainty": 0.1}

class MemoryProvenance:
    """Placeholder for MemoryProvenance - imports from provenance.py at runtime."""
    def __init__(self, origin="system", **kwargs):
        self.origin = origin
        self.created_at_utc = time.time()


# =============================================================================
# MEMORY ARTIFACT - Immutable Semantic Unit
# =============================================================================


@dataclass(frozen=True)
class MemoryArtifact:
    """
    Immutable memory artifact representing a semantic unit.
    
    A memory artifact is the fundamental persistent unit in the substrate. Every
    retained semantic object becomes an artifact. Artifacts are immutable -
    when content changes, a new revision artifact is created with the same
    identity but different revision number.
    
    Fields:
        identity:           Stable semantic identity (survives revisions)
        artifact_kind:      Category of this artifact
        semantic_content:   The actual content (can be complex structures)
        
        # Revision tracking
        revision_number:    Which revision in chain (1 = original)
        previous_revision:  Reference to prior revision (if any)
        
        # Validation and trust
        validity:           Explicit validity state
        confidence:         Belief in reliability (0.0-1.0)
        uncertainty:        Uncertainty measures
        
        # Provenance
        provenance:         Origin, sources, processing history
        
        # Lifecycle
        status:             Current accessibility state
        created_at_utc:     When artifact was created
        updated_at_utc:     Last update time (revision creation)
        
        # Graph participation
        relations:          Semantic relationships to other artifacts
    """
    
    # Content - can be any serializable structure (required, no default)
    semantic_content: Dict[str, Any]
    
    # Classification (required, no default)
    artifact_kind: MemoryArtifactKind
    
    # Identity - required before optional fields
    identity: Any                         # MemoryIdentity
    
    # All optional fields below with defaults
    revision_number: int = 1              # Which revision in chain (default: 1)
    subkind: Optional[str] = None         # Optional
    previous_revision_id: Optional[str] = None  # Prior revision reference
    is_current: bool = True               # Is this the current revision?
    
    # Validation and trust metrics
    validity: Any = field(default_factory=lambda: {"status": "valid"})
    confidence: Any = field(default_factory=lambda: {"confidence": 0.9})
    uncertainty: Any = field(default_factory=lambda: {"uncertainty": 0.1})
    
    # Provenance - where did this come from? (optional)
    provenance: Any = field(default_factory=lambda: MemoryProvenance(origin="system"))
    
    # Status (optional with default)
    status: MemoryArtifactStatus = MemoryArtifactStatus.ACTIVE
    
    # Timestamps (optional with defaults)
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    # Graph relationships - who is connected to this? (optional with default)
    relations: Tuple[Any, ...] = field(default_factory=tuple)  # MemoryRelation
    
    # Extra metadata (optional with defaults)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @staticmethod
    def _get_validity():
        """Get a valid validity state (imports at runtime)."""
        try:
            from .validity import MemoryValidity as MV
            return MV.valid()
        except ImportError:
            return {"status": "unknown"}

    
    @classmethod
    def create_builder(
        cls,
        artifact_kind: MemoryArtifactKind,
        semantic_content: Dict[str, Any],
    ) -> "MemoryArtifactBuilder":
        """
        Create a new artifact builder.
        
        Args:
            artifact_kind: What category is this artifact?
            semantic_content: The actual content to store
        """
        return MemoryArtifactBuilder(
            artifact_kind=artifact_kind,
            semantic_content=semantic_content.copy(),
        )
    
    @property
    def artifact_id(self) -> str:
        """Get the artifact's unique ID."""
        if hasattr(self.identity, "artifact_id"):
            return self.identity.artifact_id
        return ""
    
    @property
    def revision_id(self) -> str:
        """Get this revision's unique ID."""
        base = getattr(self.identity, "artifact_id", "")
        rev = getattr(self.identity, "current_revision", 1)
        return f"{base}:r{rev}"
    
    def create_revision(
        self,
        new_content: Dict[str, Any],
        change_reason: str,
        author: Optional[str] = None,
    ) -> "MemoryArtifact":
        """
        Create a new revision of this artifact.
        
        This does NOT mutate the current artifact - it creates a new one
        with incremented revision number and preserves the identity.
        """
        # Import at runtime to avoid circular deps
        from .identity import MemoryIdentity
        from .provenance import MemoryProvenance
        
        # Get previous revision ID
        prev_rev = getattr(self.identity, "revision_identity", None)
        
        # Create provenance for this revision
        prov_data = {
            "origin": author or "system",
            "change_reason": change_reason,
            "created_at_utc": time.time(),
        }
        
        if prev_rev:
            prov_data["creation_process"] = f"Revision from {prev_rev}"
        
        new_provenance = MemoryProvenance(**prov_data)
        
        # Create new identity
        new_identity = MemoryIdentity(
            artifact_id=self.artifact_id,
            semantic_identity=getattr(self.identity, "semantic_identity", ""),
            artifact_kind_str=str(self.artifact_kind.value),
            creation_revision=new_provenance.origin,
            provenance=new_provenance,
        )
        
        # Create the revised artifact
        return dataclass_replace(
            self,
            identity=new_identity,
            semantic_content=dict(new_content),
            revision_number=self.revision_number + 1,
            is_current=True,
            validity=MemoryArtifact._get_validity(),
            provenance=new_provenance,
            updated_at_utc=time.time(),
        )
    
    def with_validity(self, validity: Any) -> "MemoryArtifact":
        """Return a copy with updated validity."""
        return dataclass_replace(self, validity=validity)
    
    def with_status(self, status: MemoryArtifactStatus) -> "MemoryArtifact":
        """Return a copy with updated status."""
        return dataclass_replace(self, status=status)
    
    def add_relation(self, relation: Any) -> "MemoryArtifact":
        """Add a relationship to this artifact."""
        new_relations = tuple(list(self.relations) + [relation])
        return dataclass_replace(self, relations=new_relations)
    
    def remove_relation(self, relation_id: str) -> "MemoryArtifact":
        """Remove a relationship from this artifact."""
        new_relations = tuple(
            r for r in self.relations
            if hasattr(r, "identity") and r.identity != relation_id
        )
        return dataclass_replace(self, relations=new_relations)
    
    def add_tag(self, tag: str) -> "MemoryArtifact":
        """Add a tag to this artifact."""
        new_tags = set(self.tags)
        new_tags.add(tag)
        return dataclass_replace(self, tags=frozenset(new_tags))
    
    def remove_tag(self, tag: str) -> "MemoryArtifact":
        """Remove a tag from this artifact."""
        new_tags = set(self.tags)
        new_tags.discard(tag)
        return dataclass_replace(self, tags=frozenset(new_tags))


# =============================================================================
# MEMORY ARTIFACT BUILDER
# =============================================================================


class MemoryArtifactBuilder:
    """
    Mutable builder for constructing memory artifacts.
    
    Allows mutable construction before producing an immutable artifact via build().
    Follows the pattern of other builders in the architecture.
    """
    
    def __init__(
        self,
        artifact_kind: MemoryArtifactKind,
        semantic_content: Dict[str, Any],
    ):
        # Required fields
        self._artifact_kind = artifact_kind
        self._semantic_content = dict(semantic_content)
        
        # Identity - generated or provided
        self._artifact_id: Optional[str] = None
        self._semantic_identity: Optional[str] = None
        
        # Revision tracking
        self._revision_number: Optional[int] = None  # Will be set in build()
        self._previous_revision_id: Optional[str] = None
        
        # Validation and trust
        self._validity: Any = {"status": "valid"}
        self._confidence: Any = {"confidence": 0.9}
        self._uncertainty: Any = {"uncertainty": 0.1}
        
        # Provenance (runtime import to avoid circular deps)
        self._provenance: Any = MemoryProvenance(origin="system")
        
        # Status and timestamps
        self._status: MemoryArtifactStatus = MemoryArtifactStatus.ACTIVE
        self._created_at_utc: float = time.time()
        self._updated_at_utc: float = time.time()
        
        # Graph relationships
        self._relations: List[Any] = []
        
        # Extra metadata
        self._tags: Set[str] = set()
        self._metadata: Dict[str, Any] = {}
    
    def set_artifact_id(self, artifact_id: str) -> "MemoryArtifactBuilder":
        """Set the artifact ID (should be globally unique)."""
        self._artifact_id = artifact_id
        return self
    
    def set_semantic_identity(self, semantic_identity: str) -> "MemoryArtifactBuilder":
        """Set the semantic identity (what makes this artifact 'this')."""
        self._semantic_identity = semantic_identity
        return self
    
    def set_revision_number(self, revision_number: int) -> "MemoryArtifactBuilder":
        """Set the revision number."""
        if revision_number < 1:
            raise ValueError("Revision number must be >= 1")
        self._revision_number = revision_number
        return self
    
    def set_previous_revision_id(self, prev_id: str) -> "MemoryArtifactBuilder":
        """Set the previous revision ID for revision tracking."""
        self._previous_revision_id = prev_id
        return self
    
    def set_validity(self, validity: Any) -> "MemoryArtifactBuilder":
        """Set the explicit validity state."""
        self._validity = validity
        return self
    
    def set_confidence(self, confidence_value: float) -> "MemoryArtifactBuilder":
        """
        Set confidence (0.0-1.0).
        
        Args:
            confidence_value: Belief in reliability, 0.0 to 1.0
        """
        if not 0.0 <= confidence_value <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence_value}")
        from .confidence import MemoryConfidence
        self._confidence = dataclass_replace_confidence(self._confidence, confidence=confidence_value)
        return self
    
    def set_uncertainty(self, uncertainty: Any) -> "MemoryArtifactBuilder":
        """Set the uncertainty measures."""
        self._uncertainty = uncertainty
        return self
    
    def add_provenance_source(
        self,
        source_type: str,
        source_location: str,
        confidence: float = 1.0,
    ) -> "MemoryArtifactBuilder":
        """Add a provenance source."""
        from .provenance import MemoryProvenanceSource
        new_source = MemoryProvenanceSource(
            source_type=source_type,
            source_location=source_location,
            confidence=confidence,
        )
        self._provenance = dataclass_replace_provenance(self._provenance, supporting_sources=self._provenance.supporting_sources + (new_source,))
        return self
    
    def set_provenance_change_reason(self, reason: str) -> "MemoryArtifactBuilder":
        """Set the change reason in provenance."""
        self._provenance = dataclass_replace_provenance(
            self._provenance,
            change_reason=reason
        )
        return self
    
    def set_status(self, status: MemoryArtifactStatus) -> "MemoryArtifactBuilder":
        """Set the artifact status."""
        self._status = status
        return self
    
    def set_created_at(self, timestamp_utc: float) -> "MemoryArtifactBuilder":
        """Set creation timestamp."""
        self._created_at_utc = timestamp_utc
        return self
    
    def set_updated_at(self, timestamp_utc: float) -> "MemoryArtifactBuilder":
        """Set last update timestamp."""
        self._updated_at_utc = timestamp_utc
        return self
    
    def add_relation(self, relation: Any) -> "MemoryArtifactBuilder":
        """Add a semantic relationship."""
        self._relations.append(relation)
        return self
    
    def add_tag(self, tag: str) -> "MemoryArtifactBuilder":
        """Add a tag to this artifact."""
        self._tags.add(tag)
        return self
    
    def add_metadata(self, key: str, value: Any) -> "MemoryArtifactBuilder":
        """Add metadata to this artifact."""
        self._metadata[key] = value
        return self
    
    def build(self) -> MemoryArtifact:
        """
        Build an immutable MemoryArtifact from this builder.
        
        Validates required fields and returns frozen dataclass instance.
        
        Returns:
            New MemoryArtifact with all settings applied
            
        Raises:
            ValueError: If required fields are missing
        """
        # Generate artifact ID if not provided
        if self._artifact_id is None:
            self._artifact_id = str(uuid.uuid4())
        
        # Set semantic identity if not provided (use content hash as fallback)
        if self._semantic_identity is None:
            import hashlib
            content_str = str(sorted(self._semantic_content.items()))
            self._semantic_identity = hashlib.md5(content_str.encode()).hexdigest()
        
        # Import at runtime to avoid circular deps
        from .identity import MemoryIdentity
        
        # Build identity
        identity = MemoryIdentity(
            artifact_id=self._artifact_id,
            semantic_identity=self._semantic_identity,
            artifact_kind_str=str(self._artifact_kind.value),
            creation_revision=self._provenance.origin if hasattr(self._provenance, 'origin') else "system",
            provenance=self._provenance,
        )
        
        return MemoryArtifact(
            identity=identity,
            artifact_kind=self._artifact_kind,
            semantic_content=dict(self._semantic_content),
            revision_number=self._revision_number,
            previous_revision_id=self._previous_revision_id,
            is_current=True,
            validity=self._validity,
            confidence=self._confidence,
            uncertainty=self._uncertainty,
            provenance=self._provenance,
            status=self._status,
            created_at_utc=self._created_at_utc,
            updated_at_utc=self._updated_at_utc,
            relations=tuple(self._relations),
            tags=frozenset(self._tags),
            metadata=dict(self._metadata),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryArtifact, **kwargs) -> MemoryArtifact:
    """
    Replace fields in a frozen dataclass, returning new instance.
    
    Since dataclasses.replace() doesn't work with frozen=True,
    we use this wrapper that reconstructs the instance.
    """
    return MemoryArtifact(
        identity=kwargs.get("identity", instance.identity),
        artifact_kind=kwargs.get("artifact_kind", instance.artifact_kind),
        semantic_content=dict(instance.semantic_content) if "semantic_content" not in kwargs else kwargs["semantic_content"],
        revision_number=kwargs.get("revision_number", instance.revision_number),
        previous_revision_id=kwargs.get("previous_revision_id", instance.previous_revision_id),
        is_current=kwargs.get("is_current", instance.is_current),
        validity=kwargs.get("validity", instance.validity),
        confidence=kwargs.get("confidence", instance.confidence),
        uncertainty=kwargs.get("uncertainty", instance.uncertainty),
        provenance=kwargs.get("provenance", instance.provenance),
        status=kwargs.get("status", instance.status),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        updated_at_utc=kwargs.get("updated_at_utc", instance.updated_at_utc),
        relations=kwargs.get("relations", instance.relations),
        tags=set(instance.tags) if "tags" not in kwargs else kwargs["tags"],
        metadata=dict(instance.metadata) if "metadata" not in kwargs else kwargs["metadata"],
    )


def dataclass_replace_provenance(instance: Any, **kwargs) -> Any:
    """Replace fields in provenance."""
    origin = kwargs.get("origin", getattr(instance, "origin", "system"))
    
    from .provenance import MemoryProvenance
    return MemoryProvenance(
        origin=origin,
        creation_process=kwargs.get("creation_process"),
        semantic_time_utc=time.time(),
        created_at_utc=time.time(),
        change_reason=kwargs.get("change_reason"),
        changed_by=kwargs.get("changed_by"),
    )


def dataclass_replace_confidence(instance: Any, **kwargs) -> Any:
    """Replace fields in confidence."""
    from .confidence import MemoryConfidence
    return MemoryConfidence(
        confidence=kwargs.get("confidence", getattr(instance, "confidence", 1.0)),
        confidence_basis=getattr(instance, "confidence_basis", None),
        confidence_revision=time.time(),
    )


def create_memory_artifact(
    artifact_kind: MemoryArtifactKind,
    semantic_content: Dict[str, Any],
) -> MemoryArtifact:
    """
    Create a new memory artifact with default settings.
    
    Args:
        artifact_kind: What category is this artifact?
        semantic_content: The actual content to store
        
    Returns:
        New MemoryArtifact with defaults
    """
    return MemoryArtifact.create_builder(
        artifact_kind=artifact_kind,
        semantic_content=semantic_content,
    ).build()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryArtifact",
    "MemoryArtifactKind",
    "MemoryArtifactStatus",
    "MemoryArtifactBuilder",
    "dataclass_replace",
    "create_memory_artifact",
]