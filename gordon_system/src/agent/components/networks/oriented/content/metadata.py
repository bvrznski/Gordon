# Oriented Network Metadata Content Types - Phase 4.7.3
# =======================================================

"""
Metadata content types for the Oriented Network.

Metadata Content provides identity, lineage, provenance, and other
metadata for all content objects without runtime dependencies.

SEMANTIC LAWS:
    ORIENTED-CONTENT-LAW-003: Every Content object possesses stable semantic identity
    ORIENTED-CONTENT-LAW-006: Every Content object possesses immutable provenance
    ORIENTED-CONTENT-LAW-007: Every Content object possesses immutable lineage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
    ContentRevision,
    ContentVersion,
    ContentAuthority,
    ContentOwner,
)


# =============================================================================
# METADATA CONTENT TYPES
# =============================================================================

@dataclass(frozen=True)
class ContentIdentityMetadata(BaseContent):
    """
    Metadata describing a content object's identity.
    
    SEMANTIC ROLE:
        - Uniquely identifies semantic content
        - Never changes once established
        
    OWNERSHIP CONTRACT:
        - Owns: Identity information only
        - References: The identified content (if external)
    """
    
    content_identity: ContentIdentity = ""
    """The identity being described"""
    
    revision: ContentRevision = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "content_identity": self.content_identity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentIdentityMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            content_identity=data.get("content_identity", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        if not self.content_identity:
            errors.append("content_identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentRevisionMetadata(BaseContent):
    """
    Metadata describing a content revision.
    
    SEMANTIC ROLE:
        - Tracks semantic evolution of content
        - Immutable revision history
        
    OWNERSHIP CONTRACT:
        - Owns: Revision information only
    """
    
    target_identity: ContentIdentity = ""
    """The content being versioned"""
    
    revision_number: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "target_identity": self.target_identity,
            "revision_number": self.revision_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentRevisionMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            target_identity=data.get("target_identity", ""),
            revision_number=data.get("revision_number", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        if not self.target_identity:
            errors.append("target_identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentVersionMetadata(BaseContent):
    """
    Metadata describing a content version/schema compatibility.
    
    SEMANTIC ROLE:
        - Tracks schema version for compatibility
        - Independent from semantic revision
        
    OWNERSHIP CONTRACT:
        - Owns: Version information only
    """
    
    schema_version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "schema_version": self.schema_version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentVersionMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            schema_version=data.get("schema_version", 1),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentAuthorityMetadata(BaseContent):
    """
    Metadata describing content authority.
    
    SEMANTIC ROLE:
        - Specifies which subsystem authorizes the content
        - Never ambiguous
        
    OWNERSHIP CONTRACT:
        - Owns: Authority information only
    """
    
    authority_type: str = ""
    """Type of authority (e.g., 'oriented_network', 'goal_system')"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "authority_type": self.authority_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentAuthorityMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            authority_type=data.get("authority_type", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentOwnerMetadata(BaseContent):
    """
    Metadata describing content ownership.
    
    SEMANTIC ROLE:
        - Specifies which subsystem owns the content
        - Never implicit
        
    OWNERSHIP CONTRACT:
        - Owns: Ownership information only
    """
    
    owner_identity: str = ""
    """Identity of the owner subsystem"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "owner_identity": self.owner_identity,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentOwnerMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            owner_identity=data.get("owner_identity", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentSourceMetadata(BaseContent):
    """
    Metadata describing content source.
    
    SEMANTIC ROLE:
        - Identifies where content originated
        - Immutable source tracking
        
    OWNERSHIP CONTRACT:
        - Owns: Source information only
    """
    
    source_type: str = ""
    """Type of source (e.g., 'external', 'derived')"""
    
    source_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "source_type": self.source_type,
            "source_id": self.source_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentSourceMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            source_type=data.get("source_type", ""),
            source_id=data.get("source_id"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentOriginMetadata(BaseContent):
    """
    Metadata describing content origin.
    
    SEMANTIC ROLE:
        - Traces the origin of content
        - Immutable origin chain
        
    OWNERSHIP CONTRACT:
        - Owns: Origin information only
    """
    
    origin_type: str = ""
    """Type of origin"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "origin_type": self.origin_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentOriginMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            origin_type=data.get("origin_type", ""),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentProvenanceMetadata(BaseContent):
    """
    Metadata describing content provenance (full history).
    
    SEMANTIC ROLE:
        - Complete origin chain
        - Immutable provenance tracking
        
    OWNERSHIP CONTRACT:
        - Owns: Provenance information only
    """
    
    created_by: str = ""
    derived_from: Optional[str] = None
    observed_from: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "created_by": self.created_by,
            "derived_from": self.derived_from,
            "observed_from": self.observed_from,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentProvenanceMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            created_by=data.get("created_by", ""),
            derived_from=data.get("derived_from"),
            observed_from=data.get("observed_from"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


@dataclass(frozen=True)
class ContentLineageMetadata(BaseContent):
    """
    Metadata describing content lineage (ancestral chain).
    
    SEMANTIC ROLE:
        - Complete ancestral history
        - Immutable lineage tracking
        
    OWNERSHIP CONTRACT:
        - Owns: Lineage information only
    """
    
    ancestors: Tuple[ContentIdentity, ...] = field(default_factory=tuple)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority.value,
            "owner": self.owner,
            "ancestors": list(self.ancestors),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContentLineageMetadata:
        return cls(
            identity=data["identity"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=ContentAuthority(data["authority"]),
            owner=data.get("owner", "oriented_network"),
            ancestors=tuple(data.get("ancestors", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.identity:
            errors.append("identity is required")
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        return {"created_by": self.owner, "validated_by": self.authority.value}
    
    def get_lineage(self) -> Tuple[ContentIdentity, ...]:
        return tuple()


__all__ = [
    # Identity types
    "ContentIdentity",
    "ContentRevision",
    "ContentVersion",
    # Authority types
    "ContentAuthority",
    "ContentOwner",
    # Metadata content types
    "ContentIdentityMetadata",
    "ContentRevisionMetadata",
    "ContentVersionMetadata",
    "ContentAuthorityMetadata",
    "ContentOwnerMetadata",
    "ContentSourceMetadata",
    "ContentOriginMetadata",
    "ContentProvenanceMetadata",
    "ContentLineageMetadata",
]