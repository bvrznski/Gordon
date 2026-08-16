# Salience Network Serialization Framework
# =========================================

"""
Serialization framework for the Salience Network.

This module provides deterministic serialization contracts without runtime behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, FrozenSet, Mapping, Tuple


@dataclass(frozen=True)
class SalienceSerializer:
    """
    Serializer artifact for Salience Network components.
    
    Provides deterministic serialization without runtime dependencies.
    """
    
    serializer_id: str = field(default="salience_serializer")
    """Unique identifier for this serializer."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Serializer version tuple."""
    
    supported_types: FrozenSet[str] = field(
        default=frozenset((
            "architecture",
            "identity",
            "ownership",
            "responsibility",
            "context",
            "integration",
            "evaluation",
            "governance",
        ))
    )
    """Types that can be serialized by this serializer."""
    
    @property
    def is_deterministic(self) -> bool:
        """
        Validate that serialization is deterministic.
        
        Returns:
            True if same inputs always produce same outputs.
        """
        return True


@dataclass(frozen=True)
class SalienceDeserializer:
    """
    Deserializer artifact for Salience Network components.
    
    Provides deterministic deserialization without runtime dependencies.
    """
    
    deserializer_id: str = field(default="salience_deserializer")
    """Unique identifier for this deserializer."""
    
    version: Tuple[int, ...] = field(default_factory=lambda: (0, 1, 0))
    """Deserializer version tuple."""
    
    supported_schemas: FrozenSet[str] = field(
        default=frozenset((
            "architecture",
            "identity",
            "ownership",
            "responsibility",
            "context",
        ))
    )
    """Schema versions that can be deserialized."""
    
    @property
    def is_deterministic(self) -> bool:
        """
        Validate that deserialization is deterministic.
        
        Returns:
            True if same inputs always produce same outputs.
        """
        return True


@dataclass(frozen=True)
class SalienceSchemaVersion:
    """
    Schema version artifact for Salience Network serialization.
    
    Defines schema versions without runtime dependencies.
    """
    
    version_id: str = field(default="salience_v0_1")
    """Unique identifier for this schema version."""
    
    major: int = field(default=0)
    """Major version number."""
    
    minor: int = field(default=1)
    """Minor version number."""
    
    patch: int = field(default=0)
    """Patch version number."""
    
    @property
    def full_version(self) -> str:
        """
        Return the full semantic version string.
        
        Format: v{major}.{minor}.{patch}
        """
        return f"v{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class SalienceRevision:
    """
    Revision artifact for Salience Network components.
    
    Defines component revisions without runtime dependencies.
    """
    
    revision_id: str = field(default="")
    """Unique identifier for this revision."""
    
    component_type: str = field(default="architecture")
    """Type of component being revised."""
    
    revision_number: int = field(default=0)
    """Revision number (incremental)."""
    
    @property
    def canonical_revision(self) -> str:
        """
        Return the fully qualified canonical revision identifier.
        
        Format: type:revision_id:v{number}
        """
        return f"{self.component_type}:{self.revision_id}:v{self.revision_number}"