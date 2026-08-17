"""Knowledge Service Descriptor - Phase 6.9 Part 2 Section 1.

This module implements the canonical contract for knowledge service metadata
exposure according to Gordon Cognitive Architecture specifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SERVICE KINDS - Phase 6.9 Part 2 Section 1
# =============================================================================


class ServiceKind(Enum):
    """
    Kinds of Knowledge Services.
    
    Core Services:
        RETRIEVAL       -> Semantic artifact retrieval
        LOOKUP          -> Semantic identity resolution
        NAVIGATION      -> Graph traversal and navigation
        EXPLANATION     -> Explanation generation
        DISCOVERY       -> Missing knowledge discovery
    
    Support Services:
        EXPANSION       -> Context expansion
        RESOLUTION      -> Identity resolution (aliases, duplicates)
        ANALYTICS       -> Service evaluation and metrics
    
    Quality Assurance:
        GOVERNANCE      -> Service governance and compliance
        VALIDATION      -> Query and result validation
    """
    
    RETRIEVAL = "retrieval"
    LOOKUP = "lookup"
    NAVIGATION = "navigation"
    EXPLANATION = "explanation"
    DISCOVERY = "discovery"
    EXPANSION = "expansion"
    RESOLUTION = "resolution"
    ANALYTICS = "analytics"
    GOVERNANCE = "governance"
    VALIDATION = "validation"


# =============================================================================
# LIFECYCLE STATES - Phase 6.9 Part 2 Section 1
# =============================================================================


class LifecycleState(Enum):
    """
    States of service lifecycle progression.
    
    Progression:
        CREATED     -> Service defined but not yet active
        INITIALIZING-> Service initialization in progress
        ACTIVE      -> Service is operational and accepting queries
        RECONFIGURING-> Service configuration changes in progress
        DEPRECATED  -> Service will be removed soon
        TERMINATED  -> Service no longer accepts queries
    """
    
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    RECONFIGURING = "reconfiguring"
    DEPRECATED = "deprecated"
    TERMINATED = "terminated"


# =============================================================================
# SUPPORTED ARTIFACTS - Phase 6.9 Part 1 Section 20
# =============================================================================


class SupportedArtifact(Enum):
    """
    Types of semantic artifacts services can handle.
    
    Core Artifacts:
        CONCEPT       -> Concept definitions and instances
        ASSERTION     -> Propositional assertions
        BELIEF        -> Accepted/rejected beliefs
        RELATION      -> Semantic relations between artifacts
    
    Graph Structures:
        NODE          -> Graph nodes
        EDGE          -> Graph edges
        GRAPH         -> Complete knowledge graphs
    """
    
    CONCEPT = "concept"
    ASSERTION = "assertion"
    BELIEF = "belief"
    RELATION = "relation"
    NODE = "node"
    EDGE = "edge"
    GRAPH = "graph"


# =============================================================================
# PROVENANCE RECORD - Phase 6.9 Service-LAW-004
# =============================================================================


@dataclass(frozen=True)
class ProvenanceRecord:
    """
    Records the origin and execution history of a service call.
    
    Per SERVICE-LAW-004: Services shall preserve provenance.
    Per SERVICE-LAW-005: Services shall preserve execution history.
    
    Fields:
        provenance_identity: Unique identifier for this record
        originating_request: Request that triggered the service call
        originating_system: System that initiated the request
        originating_service: Service that executed the request
        timestamp_utc: UTC timestamp of the event
        sequence_number: Order in execution history
    """
    
    provenance_identity: str
    originating_request: str
    originating_system: str
    originating_service: str
    timestamp_utc: float
    sequence_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance record to dictionary."""
        return {
            "provenance_identity": self.provenance_identity,
            "originating_request": self.originating_request,
            "originating_system": self.originating_system,
            "originating_service": self.originating_service,
            "timestamp_utc": self.timestamp_utc,
            "sequence_number": self.sequence_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProvenanceRecord:
        """Create provenance record from dictionary."""
        return cls(
            provenance_identity=data.get("provenance_identity", ""),
            originating_request=data.get("originating_request", ""),
            originating_system=data.get("originating_system", "unknown"),
            originating_service=data.get("originating_service", "unknown"),
            timestamp_utc=float(data.get("timestamp_utc", time.time())),
            sequence_number=int(data.get("sequence_number", 0)),
        )


# =============================================================================
# KNOWLEDGE SERVICE DESCRIPTOR - Phase 6.9 Part 2 Section 1
# =============================================================================


@dataclass(frozen=True)
class KnowledgeServiceDescriptor:
    """
    Descriptor for a Knowledge Service.
    
    This is the canonical metadata contract that exposes service information
    independently of its implementation, per Phase 6.9 Part 2 Section 1.
    
    Per SERVICE-LAW-001: Every Knowledge Service possesses one immutable Semantic Identity.
    Per SERVICE-LAW-004: Services shall preserve provenance.
    Per SERVICE-LAW-007: Services shall remain deterministic.
    Per SERVICE-LAW-008: Published Service Contracts remain immutable.
    
    Fields:
        service_identity: Unique identifier for the service
        service_kind: Kind of service (retrieval, lookup, etc.)
        supported_artifacts: Types of artifacts this service handles
        lifecycle_state: Current state in the lifecycle progression
        compatibility_revision: API compatibility version
        provenance: Complete origin and execution trail
        
    Invariants:
        * service_identity remains immutable once created
        * supported_artifacts defines the service's semantic scope
        * All operations remain deterministic for equivalent inputs
    """
    
    # Core identity (required - immutable per SERVICE-LAW-001)
    service_identity: str  # Unique service identifier
    
    # Service kind (required)
    service_kind: ServiceKind
    
    # Supported artifacts (required)
    supported_artifacts: Tuple[SupportedArtifact, ...]
    
    # Lifecycle tracking (required)
    lifecycle_state: LifecycleState
    compatibility_revision: int = 1
    
    # Provenance (required per SERVICE-LAW-004)
    provenance: Tuple[ProvenanceRecord, ...] = field(default_factory=tuple)
    
    # Service metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    def __post_init__(self) -> None:
        """Validate descriptor after creation."""
        if not self.service_identity:
            raise ValueError("service_identity cannot be empty")
        if self.compatibility_revision < 1:
            raise ValueError("compatibility_revision must be >= 1")
    
    @property
    def is_active(self) -> bool:
        """Check if service is in active state."""
        return self.lifecycle_state == LifecycleState.ACTIVE
    
    @property
    def has_provenance(self) -> bool:
        """Check if service has provenance records."""
        return len(self.provenance) > 0
    
    @classmethod
    def create_initial(
        cls,
        service_kind: ServiceKind,
        supported_artifacts: List[SupportedArtifact],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeServiceDescriptor":
        """
        Create a new initial service descriptor.
        
        Args:
            service_kind: Kind of service to create
            supported_artifacts: Types of artifacts this service handles
            metadata: Additional service metadata (optional)
            
        Returns:
            New KnowledgeServiceDescriptor in CREATED state with revision 1
            
        This method creates the initial version of a service, setting up:
            - Unique service_identity
            - Initial provenance record
            - Created_at timestamp
            - LifecycleState.CREATED state
            - Revision 1
        """
        service_id = f"service:{uuid.uuid4().hex[:16]}"
        
        initial_provenance = (
            ProvenanceRecord(
                provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                originating_request="Service initialization",
                originating_system="knowledge-services-system",
                originating_service=service_id,
                timestamp_utc=time.time(),
                sequence_number=0,
            ),
        )
        
        return cls(
            service_identity=service_id,
            service_kind=service_kind,
            supported_artifacts=tuple(supported_artifacts),
            lifecycle_state=LifecycleState.CREATED,
            compatibility_revision=1,
            provenance=initial_provenance,
            metadata=metadata or {},
            created_at_utc=time.time(),
        )
    
    def with_active(self) -> "KnowledgeServiceDescriptor":
        """
        Transition service to active state.
        
        Returns:
            New descriptor with lifecycle_state set to ACTIVE
        """
        return KnowledgeServiceDescriptor(
            service_identity=self.service_identity,
            service_kind=self.service_kind,
            supported_artifacts=self.supported_artifacts,
            lifecycle_state=LifecycleState.ACTIVE,
            compatibility_revision=self.compatibility_revision,
            provenance=tuple(list(self.provenance) + [
                ProvenanceRecord(
                    provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                    originating_request="Service activation",
                    originating_system="knowledge-services-system",
                    originating_service=self.service_identity,
                    timestamp_utc=time.time(),
                    sequence_number=len(self.provenance) + 1,
                ),
            ]),
            metadata=dict(self.metadata),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def with_revision(
        self,
        new_revision: int,
        change_summary: Optional[str] = None,
    ) -> "KnowledgeServiceDescriptor":
        """
        Create a new revision of this service descriptor.
        
        Args:
            new_revision: The revision number
            change_summary: Brief description of changes (optional)
            
        Returns:
            New KnowledgeServiceDescriptor with updated revision
            
        Per SERVICE-LAW-004: Provenance is preserved across revisions.
        """
        new_provenance = tuple(list(self.provenance) + [
            ProvenanceRecord(
                provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                originating_request=f"Revision {new_revision}: {change_summary or 'unknown change'}",
                originating_system="knowledge-services-system",
                originating_service=self.service_identity,
                timestamp_utc=time.time(),
                sequence_number=len(self.provenance) + 1,
            ),
        ])
        
        return KnowledgeServiceDescriptor(
            service_identity=self.service_identity,
            service_kind=self.service_kind,
            supported_artifacts=self.supported_artifacts,
            lifecycle_state=self.lifecycle_state,
            compatibility_revision=new_revision,
            provenance=new_provenance,
            metadata=dict(self.metadata),
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert descriptor to dictionary for serialization."""
        return {
            "service_identity": self.service_identity,
            "service_kind": self.service_kind.value,
            "supported_artifacts": [a.value for a in self.supported_artifacts],
            "lifecycle_state": self.lifecycle_state.value,
            "compatibility_revision": self.compatibility_revision,
            "provenance": [p.to_dict() for p in self.provenance],
            "metadata": dict(self.metadata),
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeServiceDescriptor":
        """Create descriptor from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(ProvenanceRecord.from_dict(p_data))
        
        return cls(
            service_identity=data.get("service_identity", str(uuid.uuid4())),
            service_kind=ServiceKind(data.get("service_kind", "unknown")),
            supported_artifacts=tuple(
                SupportedArtifact(a) for a in data.get("supported_artifacts", [])
            ),
            lifecycle_state=LifecycleState(data.get("lifecycle_state", "created")),
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            provenance=tuple(provenance),
            metadata=dict(data.get("metadata", {})),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )
    
    def update_metadata(self, key: str, value: Any) -> "KnowledgeServiceDescriptor":
        """Update a metadata field and return new descriptor."""
        new_metadata = self.metadata.copy()
        new_metadata[key] = value
        return KnowledgeServiceDescriptor(
            service_identity=self.service_identity,
            service_kind=self.service_kind,
            supported_artifacts=self.supported_artifacts,
            lifecycle_state=self.lifecycle_state,
            compatibility_revision=self.compatibility_revision + 1,
            provenance=tuple(list(self.provenance) + [
                ProvenanceRecord(
                    provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
                    originating_request=f"Metadata update: {key}",
                    originating_system="knowledge-services-system",
                    originating_service=self.service_identity,
                    timestamp_utc=time.time(),
                    sequence_number=len(self.provenance) + 1,
                ),
            ]),
            metadata=new_metadata,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Service kinds (Part 2 Section 1)
    "ServiceKind",
    # Lifecycle states (Part 2 Section 1)
    "LifecycleState",
    # Supported artifact types (Part 1 Section 20)
    "SupportedArtifact",
    # Provenance record
    "ProvenanceRecord",
    # Knowledge service descriptor (Part 2 Section 1)
    "KnowledgeServiceDescriptor",
]