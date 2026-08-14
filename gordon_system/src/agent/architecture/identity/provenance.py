# Provenance Identities - Phase 3.19.8
# =======================================

"""
Provenance identity types for tracking artifact origins and history.

Every artifact in Gordon should preserve:
    - Origin (where it came from)
    - Creator (who/what created it)
    - Timestamp (when it was created)
    - Authority (by what authority)
    - Source reference
    - Transformation history

PROVENANCE HIERARCHY:
    ProvenanceRecord        - Complete provenance trail
        ├── Origin              - Source origin
        ├── Creator             - Creation entity
        ├── SourceReference     - Original source info
        └── TransformationHistory - Evolution path
        
INVARIANTS:
    PROV-001: Every artifact has exactly one complete provenance record
    PROV-002: Provenance is immutable once created
    PROV-003: Provenance can be verified through signatures/keys
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import uuid


# =============================================================================
# PROVENANCE RECORD
# =============================================================================


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Complete provenance record for an artifact.
    
    A provenance record contains all information needed to verify where
    an artifact came from and how it was created.
    
    INVARIANTS:
        PROV-001: Every artifact has exactly one complete provenance record
        PROV-002: Provenance is immutable once created
        PROV-003: Provenance can be verified through cryptographic means
        
    PARAMETERS:
        artifact_id       - ID of the artifact
        origin            - Origin information (where it came from)
        creator           - Creator information (who/what created it)
        timestamp         - When it was created
        authority         - Authority under which it was created
        transformation_history - Evolution path through transformations
    """
    
    artifact_id: str
    origin: "Origin"
    creator: "Creator"
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    authority: Optional[str] = None
    transformation_history: list["TransformationStep"] = field(
        default_factory=list
    )
    signature: Optional[str] = None  # Cryptographic signature for verification
    
    @classmethod
    def create_initial(cls, artifact_id: str) -> "ProvenanceRecord":
        """Create initial (empty) provenance record."""
        return cls(
            artifact_id=artifact_id,
            origin=Origin(),
            creator=Creator(),
            timestamp_utc=0.0,
        )
    
    @classmethod
    def create_with_origin(
        cls,
        artifact_id: str,
        origin: "Origin",
        creator: "Creator",
        timestamp_utc: Optional[float] = None,
    ) -> "ProvenanceRecord":
        """Create provenance record with origin information."""
        return cls(
            artifact_id=artifact_id,
            origin=origin,
            creator=creator,
            timestamp_utc=timestamp_utc or 0.0,
        )
    
    def add_transformation(self, step: "TransformationStep") -> None:
        """Add a transformation step to the history."""
        self.transformation_history.append(step)
    
    def get_final_origin(self) -> Optional["Origin"]:
        """Get the origin after all transformations (if any)."""
        if not self.transformation_history:
            return self.origin
        # Last transformation's target would be the final origin
        return None  # Would require more context


# =============================================================================
# ORIGIN
# =============================================================================


@dataclass(frozen=True)
class Origin:
    """
    Information about where an artifact originated.
    
    The origin identifies the source from which an artifact was created,
    including the location and context.
    
    INVARIANTS:
        ORG-001: Every artifact has exactly one original origin
        ORG-002: Origin information is immutable once recorded
        ORG-003: Origin may be a transformation of another origin
        
    PARAMETERS:
        source_type       - Type of source (file, database, network, etc.)
        location          - Location of the source
        context           - Additional context about the origin
    """
    
    source_type: str = "unknown"  # e.g., "file", "database", "network"
    location: Optional[str] = None
    context: Optional[str] = None
    
    @classmethod
    def file_origin(cls, path: str) -> "Origin":
        """Create an origin for a file-based artifact."""
        return cls(source_type="file", location=path)
    
    @classmethod
    def database_origin(cls, connection_str: str, query: str) -> "Origin":
        """Create an origin for a database query result."""
        return cls(
            source_type="database",
            location=connection_str,
            context=f"query: {query}",
        )
    
    @classmethod
    def network_origin(cls, url: str, method: str = "GET") -> "Origin":
        """Create an origin for a network request."""
        return cls(
            source_type="network",
            location=url,
            context=f"method: {method}",
        )


# =============================================================================
# CREATOR
# =============================================================================


@dataclass(frozen=True)
class Creator:
    """
    Information about who/what created the artifact.
    
    The creator identifies the entity responsible for creating an artifact,
    which could be a user, system component, or external service.
    
    INVARIANTS:
        CR-001: Every artifact has exactly one creator
        CR-002: Creator information is immutable once recorded
        CR-003: Creator may have authority credentials
        
    PARAMETERS:
        type              - Type of creator (user, system, service)
        identifier        - Identifier for the creator
        timestamp         - When the creation occurred
        authority         - Authority under which creation occurred
    """
    
    type: str = "unknown"  # e.g., "user", "system", "service"
    identifier: Optional[str] = None
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    authority: Optional[str] = None
    
    @classmethod
    def system_creator(cls, component_id: str) -> "Creator":
        """Create a creator representing a system component."""
        return cls(
            type="system",
            identifier=component_id,
            timestamp_utc=0.0,
        )
    
    @classmethod
    def user_creator(cls, user_id: str) -> "Creator":
        """Create a creator representing a user."""
        return cls(
            type="user", 
            identifier=user_id,
            timestamp_utc=0.0,
        )


# =============================================================================
# SOURCE REFERENCE
# =============================================================================


@dataclass(frozen=True)
class SourceReference:
    """
    Reference to the original source of an artifact.
    
    A source reference provides enough information to locate and verify
    the original source from which an artifact was derived.
    
    INVARIANTS:
        SRC-001: Every artifact has exactly one source reference (at creation)
        SRC-002: Source references can be followed to verify origin
        SRC-003: Source references may be cryptographic hashes
        
    PARAMETERS:
        type              - Type of reference (hash, url, path, etc.)
        value             - Reference value
        version           - Version at time of creation
        checksum          - Checksum for verification
    """
    
    type: str = "unknown"  # e.g., "hash", "url", "path"
    value: Optional[str] = None
    version: Optional[str] = None
    checksum: Optional[str] = None
    
    @classmethod
    def hash_reference(cls, checksum: str) -> "SourceReference":
        """Create a reference based on cryptographic hash."""
        return cls(
            type="hash",
            value=checksum,
            checksum=checksum,
        )
    
    @classmethod
    def url_reference(cls, url: str, version: Optional[str] = None) -> "SourceReference":
        """Create a reference to a URL source."""
        return cls(type="url", value=url, version=version)


# =============================================================================
# TRANSFORMATION STEP
# =============================================================================


@dataclass(frozen=True)
class TransformationStep:
    """
    A single transformation step in an artifact's history.
    
    Each transformation records what operation was applied and the inputs/outputs.
    
    INVARIANTS:
        TRS-001: Every transformation has exactly one input and output
        TRS-002: Transformations are ordered chronologically
        TRS-003: Transformation steps can be replayed deterministically
        
    PARAMETERS:
        operation         - Name of the transformation operation
        input_ids         - IDs of input artifacts
        output_id         - ID of output artifact
        timestamp         - When transformation occurred
        config            - Configuration used for this transformation
    """
    
    operation: str  # e.g., "filter", "aggregate", "join"
    input_ids: tuple[str, ...] = field(default_factory=tuple)
    output_id: Optional[str] = None
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    config_hash: Optional[str] = None
    
    @classmethod
    def create(cls, operation: str, output_id: str) -> "TransformationStep":
        """Create a transformation step."""
        return cls(
            operation=operation,
            output_id=output_id,
        )


# =============================================================================
# PROVENANCE VERIFICATION
# =============================================================================


class ProvenanceVerifier:
    """
    Verifier for provenance records and their integrity.
    
    Provides utilities for verifying that provenance information is valid
    and hasn't been tampered with.
    
    METHODS:
        verify_signature()  - Verify cryptographic signature
        verify_chain()      - Verify the complete provenance chain
        verify_transformations()- Verify transformation history
    """
    
    def __init__(self):
        self._verified: set[str] = set()
    
    def verify_signature(
        self,
        record: ProvenanceRecord,
        public_key: Optional[str] = None,
    ) -> bool:
        """Verify that the provenance record has a valid signature."""
        if not record.signature:
            return False
        
        # In real implementation, would verify signature against public key
        # For now, assume signature is valid if present
        return True
    
    def verify_chain(
        self,
        record: ProvenanceRecord,
    ) -> bool:
        """Verify the complete provenance chain is consistent."""
        # Verify each transformation has matching inputs/outputs
        for i, step in enumerate(record.transformation_history):
            # Check that this step's output matches next step's input (if any)
            if i + 1 < len(record.transformation_history):
                next_step = record.transformation_history[i + 1]
                if step.output_id not in next_step.input_ids:
                    return False
        return True
    
    def verify_transformations(
        self,
        record: ProvenanceRecord,
    ) -> bool:
        """Verify that transformation history is complete and valid."""
        # Check for gaps or cycles in transformations
        seen_outputs = set()
        
        for step in record.transformation_history:
            if step.output_id in seen_outputs:
                return False  # Cycle detected
            seen_outputs.add(step.output_id)
        
        return True


__all__ = [
    "ProvenanceRecord",
    "Origin", 
    "Creator",
    "SourceReference",
    "TransformationStep",
    "ProvenanceVerifier",
]