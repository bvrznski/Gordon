# Metadata Authority - Canonical Authority
# =========================================

"""
Metadata authority for metadata schemas, validation,
enrichment, and versioning.

PHASE 3.7.21 REMEDIATION:
- Records own their metadata (part of InformationRecord)
- MetadataAuthority validates schemas and tracks versions
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .models import (
    MetadataSchema,
    MetadataVersion,
    MetadataSnapshot,
    MetadataRecord,
)


# =============================================================================
# Schema Registry - PHASE 3.7.21 REMEDIATION
# =============================================================================

class SchemaRegistry:
    """Registry of metadata schemas."""
    
    def __init__(self) -> None:
        self._schemas: Dict[str, MetadataSchema] = {}
        self._lock = threading.RLock()
    
    def register_schema(self, schema: MetadataSchema) -> None:
        """Register a new schema."""
        with self._lock:
            self._schemas[schema.schema_id] = schema
    
    def get_schema(self, schema_id: str) -> Optional[MetadataSchema]:
        """Get schema by ID."""
        with self._lock:
            return self._schemas.get(schema_id)
    
    def validate(
        self,
        schema_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Validate metadata against schema."""
        schema = self.get_schema(schema_id)
        if schema is None:
            raise ValueError(f"Schema '{schema_id}' not found")
        return schema.is_valid(metadata)


# =============================================================================
# Metadata Authority - PHASE 3.7.21 REMEDIATION
# =============================================================================

class MetadataAuthority:
    """
    Canonical authority for metadata management.
    
    PHASE 3.7.21 REMEDIATION PRINCIPLES:
    1. Records own their metadata (MetadataRecord in InformationRecord)
    2. Authority validates schemas and tracks versions for provenance
    3. Versioning creates new snapshots, not mutations
    
    Core Responsibilities:
    1. Metadata schema registration and validation
    2. Metadata record creation and updates (versioned)
    3. Metadata snapshotting at key points
    
    Non-Responsibilities (moved to records):
    - Storing metadata on records (InformationRecord.metadata)
    
    Usage:
        # Create authority
        authority = MetadataAuthority()
        
        # Register a schema for validation
        schema = MetadataSchema(
            schema_id="user_profile",
            version=1,
            fields={"name": str, "email": str},
            required_fields=["name", "email"]
        )
        await authority.register_schema(schema)
        
        # Record owns its metadata field:
        record = InformationRecord(
            information_id="data-123",
            content_hash="hash123",
            owner=OwnerIdentity(...),
            classification=ClassificationLevel.INTERNAL,
            lifecycle_state=LifecycleState.ACTIVE,
            metadata=MetadataRecord(
                information_id="data-123",
                schema=schema,
                values={"name": "John Doe", "email": "john@example.com"}
            ),
        )
    """
    
    def __init__(self) -> None:
        """Initialize the metadata authority."""
        self._lock = threading.RLock()
        
        # Schema registry
        self._schema_registry = SchemaRegistry()
        
        # Version history by information ID (for provenance)
        self._versions: Dict[str, List[MetadataVersion]] = {}
        
        # Statistics
        self._stats = {
            "total_schemas": 0,
            "version_creations": 0,
        }
    
    async def register_schema(self, schema: MetadataSchema) -> None:
        """Register a metadata schema."""
        with self._lock:
            self._schema_registry.register_schema(schema)
            self._stats["total_schemas"] += 1
    
    async def get_schema(self, schema_id: str) -> Optional[MetadataSchema]:
        """Get schema by ID."""
        with self._lock:
            return self._schema_registry.get_schema(schema_id)
    
    async def validate(
        self,
        schema_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Validate metadata against schema."""
        with self._lock:
            return self._schema_registry.validate(schema_id, metadata)
    
    async def create_record(
        self,
        information_id: str,
        schema_id: str,
        values: Dict[str, Any],
        author: str = "system",
    ) -> MetadataRecord:
        """
        Create a metadata record.
        
        PHASE 3.7.21: The record itself owns its metadata field.
        This method creates the record for validation and provenance.
        
        Args:
            information_id: ID of the information
            schema_id: Schema to use
            values: Initial metadata values
            author: Who created the record
            
        Returns:
            Created MetadataRecord (record owns the actual value)
        """
        with self._lock:
            schema = self._schema_registry.get_schema(schema_id)
            if schema is None:
                raise ValueError(f"Schema '{schema_id}' not registered")
            
            # Validate
            if not schema.is_valid(values):
                raise ValueError(f"Metadata does not conform to schema '{schema_id}'")
            
            # Create record
            record = MetadataRecord(
                information_id=information_id,
                schema=schema,
                version=1,
                values=dict(values),
            )
            
            # Record version history for provenance
            if information_id not in self._versions:
                self._versions[information_id] = []
            self._versions[information_id].append(MetadataVersion(
                version_number=record.version,
                metadata=dict(values),
                timestamp=time.time(),
                author=author
            ))
            
            self._stats["version_creations"] += 1
            
            return record
    
    async def update_record(
        self,
        information_id: str,
        values: Dict[str, Any],
        author: str = "system",
    ) -> MetadataRecord:
        """
        Update a metadata record (creates new version).
        
        PHASE 3.7.21: Versioning creates new snapshots, not mutations.
        
        Args:
            information_id: ID of the information
            values: New metadata values
            author: Who made the update
            
        Returns:
            Updated MetadataRecord with incremented version
        """
        with self._lock:
            # Get current record (if exists)
            versions = self._versions.get(information_id, [])
            
            if not versions:
                raise ValueError(f"No metadata found for {information_id}")
            
            current = versions[-1]
            
            # Create new version (not mutation)
            new_version = current.version_number + 1
            
            new_record = MetadataRecord(
                information_id=information_id,
                schema=current.metadata.get("_schema", None) if hasattr(current, 'metadata') else None,
                version=new_version,
                values=dict(values),
                history=list(versions),  # Include previous versions
            )
            
            self._versions[information_id].append(MetadataVersion(
                version_number=new_version,
                metadata=dict(values),
                timestamp=time.time(),
                author=author
            ))
            
            self._stats["version_creations"] += 1
            
            return new_record
    
    async def get_record(self, information_id: str) -> Optional[MetadataRecord]:
        """Get the current metadata record."""
        with self._lock:
            versions = self._versions.get(information_id)
            if not versions:
                return None
            return MetadataRecord(
                information_id=information_id,
                schema=MetadataSchema(schema_id="unknown"),
                version=versions[-1].version_number,
                values=dict(versions[-1].metadata),
                history=list(versions[:-1]) if len(versions) > 1 else []
            )
    
    async def get_version_history(self, information_id: str) -> List[MetadataVersion]:
        """Get full version history for an item."""
        with self._lock:
            return list(self._versions.get(information_id, []))
    
    async def take_snapshot(
        self,
        information_id: str,
        timestamp: Optional[float] = None,
    ) -> MetadataSnapshot:
        """
        Take a snapshot of metadata at a point in time.
        
        Args:
            information_id: ID of the information
            timestamp: Snapshot timestamp (default: now)
            
        Returns:
            Immutable MetadataSnapshot
        """
        with self._lock:
            versions = self._versions.get(information_id, [])
            current_values = dict(versions[-1].metadata) if versions else {}
            
            return MetadataSnapshot(
                information_id=information_id,
                version=len(versions),
                metadata=current_values,
                timestamp=timestamp or time.time(),
                author="system"
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metadata statistics."""
        with self._lock:
            return {
                "total_schemas": self._stats["total_schemas"],
                "records_with_metadata": len(self._versions),
                "version_creations": self._stats["version_creations"],
            }


__all__ = [
    "SchemaRegistry",
    "MetadataAuthority",
]