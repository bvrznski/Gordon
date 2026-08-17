# Perception Interface Request - Phase 5.2.5
# ===========================================

"""
Perception Interface Request: Transport mechanism for interface requests.

Every request crossing the Perception boundary shall:
- Have an explicit identity
- Identify the target Interface and requesting consumer
- Declare one supported Request kind
- Preserve scope, compatibility and authorization context
- Preserve provenance

REQUEST-LAW-001: Every Interface Request shall possess one explicit identity.
REQUEST-LAW-002: Every Request shall identify the target Interface and requesting consumer.
REQUEST-LAW-003: Every Request shall declare one supported Request kind.
REQUEST-LAW-004: Every Request shall preserve scope, compatibility and authorization context.
REQUEST-LAW-005: Every Request shall preserve provenance.
REQUEST-LAW-006: Requests shall remain immutable after submission.
REQUEST-LAW-007: Requests shall validate before routing or execution.
REQUEST-LAW-008: Equivalent Requests shall produce equivalent communication semantics.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
import uuid


# =============================================================================
# REQUEST KINDS (per interface)
# =============================================================================


class RequestKind:
    """Categories of request kinds."""
    
    # Sensors Interface
    ACQUISITION = "acquisition"
    DESCRIPTOR_QUERY = "descriptor_query"
    CAPABILITY_QUERY = "capability_query"
    
    # Workspace Interface  
    PROJECTION_REQUEST = "projection_request"
    SNAPSHOT_REQUEST = "snapshot_request"
    STREAM_SUBSCRIBE = "stream_subscribe"
    
    # Memory Interface
    CANDIDATE_SUBMISSION = "candidate_submission"
    ADMISSION_QUERY = "admission_query"
    
    # Knowledge Interface
    GROUNDING_REQUEST = "grounding_request"
    SCHEMA_QUERY = "schema_query"
    
    # Attention Interface
    CANDIDATE_PUBLICATION = "candidate_publication"
    INSPECTION_REQUEST = "inspection_request"
    
    # Learning Interface
    EVIDENCE_PUBLICATION = "evidence_publication"
    PROPOSAL_SUBMISSION = "proposal_submission"
    
    # Identity Interface
    IDENTITY_GROUNDING = "identity_grounding"
    
    # Reasoning Interface
    EVIDENCE_REQUEST = "evidence_request"
    
    # World Model Interface
    UPDATE_PUBLICATION = "update_publication"
    
    # Coordination Interface
    STATUS_REQUEST = "status_request"
    SYNCHRONIZATION_REQUEST = "synchronization_request"
    
    # Governance Interface
    EVIDENCE_REQUEST = "governance_evidence"
    
    # External Interface
    PUBLIC_PROJECTION = "public_projection"


# =============================================================================
# PRIORITY CLASSES
# =============================================================================


class RequestPriority:
    """Request priority classes for scheduling."""
    
    CRITICAL = 0      # Must be processed immediately
    HIGH = 1          # High priority processing
    NORMAL = 2        # Standard priority
    LOW = 3           # Low priority (can be deferred)
    BACKGROUND = 4    # Background processing


# =============================================================================
# SCOPE DEFINITIONS
# =============================================================================


@dataclass(frozen=True)
class RequestScope:
    """
    Scope constraints for a request.
    
    Fields:
        temporal: Temporal scope (time range or revision)
        spatial: Spatial scope (location or region)
        modality: Modality constraints
        artifact: Artifact kind constraints
        projection: Projection-specific constraints
    """
    temporal: Dict[str, Any] = field(default_factory=dict)
    spatial: Dict[str, Any] = field(default_factory=dict)
    modality: Dict[str, Any] = field(default_factory=dict)
    artifact: Dict[str, Any] = field(default_factory=dict)
    projection: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INTERFACE REQUEST
# =============================================================================


@dataclass(frozen=True)
class PerceptionInterfaceRequest:
    """
    Request to an Interface.
    
    Every request crossing the interface boundary shall have:
        - An explicit identity (request_identity)
        - Target Interface reference (interface_reference)
        - Request kind (request_kind)
        - Consumer identity (consumer)
        - Compatibility revision (compatibility_revision)
        - Authorization context (authorization_context)
        
    This is the abstract base for all interface requests.
    
    REQUEST-LAW-001: Every Interface Request shall possess one explicit identity.
    REQUEST-LAW-002: Every Request shall identify the target Interface and requesting consumer.
    REQUEST-LAW-003: Every Request shall declare one supported Request kind.
    REQUEST-LAW-004: Every Request shall preserve scope, compatibility and authorization context.
    REQUEST-LAW-005: Every Request shall preserve provenance.
    REQUEST-LAW-006: Requests shall remain immutable after submission.
    REQUEST-LAW-007: Requests shall validate before routing or execution.
    REQUEST-LAW-008: Equivalent Requests shall produce equivalent communication semantics.
    """
    
    # Identity
    request_identity: str
    
    # Target interface and consumer
    interface_reference: str  # e.g., "sensors", "workspace"
    
    # Request kind (must be supported by the target interface)
    request_kind: str
    
    # Consumer identity
    consumer: str
    
    # Versioning
    compatibility_revision: int = 1  # Contract revision being used
    
    # Priority class
    priority_class: int = RequestPriority.NORMAL
    
    # Scope constraints (dimensional)
    scope: RequestScope = field(default_factory=RequestScope)
    
    # Authorization and policy context
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if request has expired (based on provenance)."""
        if "deadline" not in self.provenance:
            return False
        deadline = self.provenance["deadline"]
        return _time.time() > deadline
    
    @classmethod
    def create(
        cls,
        interface_reference: str,
        request_kind: str,
        consumer_id: str,
        **kwargs
    ) -> "PerceptionInterfaceRequest":
        """Create a generic interface request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference=interface_reference,
            request_kind=request_kind,
            consumer=consumer_id,
            compatibility_revision=kwargs.get("compatibility_revision", 1),
            priority_class=kwargs.get("priority_class", RequestPriority.NORMAL),
            scope=kwargs.get("scope", RequestScope()),
            authorization_context=kwargs.get("authorization_context", {}),
            provenance=kwargs.get("provenance", {"timestamp": _time.time()}),
        )
    
    @classmethod
    def create_sensors_acquisition(
        cls,
        sensor_reference: str,
        consumer_id: str,
        requested_modality: Optional[str] = None,
        sampling_config: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, Any]] = None,
        deadline_seconds: float = 30.0,
    ) -> "PerceptionInterfaceRequest":
        """Create a sensor acquisition request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference="sensors",
            request_kind=RequestKind.ACQUISITION,
            consumer=consumer_id,
            compatibility_revision=1,
            priority_class=RequestPriority.HIGH,
            scope=RequestScope(
                temporal={"deadline": _time.time() + deadline_seconds},
                modality={"selected": requested_modality} if requested_modality else {},
            ),
            authorization_context={
                "required_permission": "sensor:read",
                "sandbox_required": True,
            },
            provenance={
                "timestamp": _time.time(),
                "deadline": _time.time() + deadline_seconds,
                "sensor_reference": sensor_reference,
                "sampling_config": sampling_config or {},
                "quality_requirements": quality_requirements or {},
            },
        )
    
    @classmethod
    def create_workspace_projection(
        cls,
        consumer_id: str,
        temporal_scope: Optional[Dict[str, Any]] = None,
        spatial_scope: Optional[Dict[str, Any]] = None,
        projection_kinds: Optional[List[str]] = None,
        detail_level: str = "percept",
        update_mode: str = "on_demand",
    ) -> "PerceptionInterfaceRequest":
        """Create a workspace projection request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference="workspace",
            request_kind=RequestKind.PROJECTION_REQUEST,
            consumer=consumer_id,
            compatibility_revision=1,
            priority_class=RequestPriority.NORMAL,
            scope=RequestScope(
                temporal=temporal_scope or {},
                spatial=spatial_scope or {},
                projection={
                    "kinds": projection_kinds or [],
                    "detail_level": detail_level,
                    "update_mode": update_mode,
                },
            ),
            authorization_context={"required_permission": "workspace:read"},
        )
    
    @classmethod
    def create_memory_candidate_submission(
        cls,
        consumer_id: str,
        candidate_artifact_kinds: List[str],
        confidence: float = 1.0,
        provenance_data: Optional[Dict[str, Any]] = None,
    ) -> "PerceptionInterfaceRequest":
        """Create a memory candidate submission request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference="memory",
            request_kind=RequestKind.CANDIDATE_SUBMISSION,
            consumer=consumer_id,
            compatibility_revision=1,
            priority_class=RequestPriority.NORMAL,
            scope=RequestScope(
                artifact={"kinds": candidate_artifact_kinds},
            ),
            authorization_context={
                "required_permission": "memory:submit",
                "confidence_threshold": confidence,
            },
            provenance=provenance_data or {"timestamp": _time.time()},
        )
    
    @classmethod
    def create_knowledge_grounding(
        cls,
        consumer_id: str,
        source_percepts: List[Dict[str, Any]],
        candidate_categories: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "PerceptionInterfaceRequest":
        """Create a knowledge grounding request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference="knowledge",
            request_kind=RequestKind.GROUNDING_REQUEST,
            consumer=consumer_id,
            compatibility_revision=1,
            priority_class=RequestPriority.NORMAL,
            scope=RequestScope(),
            authorization_context={"required_permission": "knowledge:read"},
            provenance={
                "timestamp": _time.time(),
                "source_percepts": source_percepts,
                "candidate_categories": candidate_categories or [],
                "context": context or {},
            },
        )
    
    @classmethod
    def create_reasoning_evidence(
        cls,
        consumer_id: str,
        reasoning_context: Dict[str, Any],
        artifact_kinds: Optional[List[str]] = None,
        depth: int = 1,
    ) -> "PerceptionInterfaceRequest":
        """Create a reasoning evidence request."""
        return cls(
            request_identity=f"request:{uuid.uuid4().hex[:16]}",
            interface_reference="reasoning",
            request_kind=RequestKind.EVIDENCE_REQUEST,
            consumer=consumer_id,
            compatibility_revision=1,
            priority_class=RequestPriority.NORMAL,
            scope=RequestScope(),
            authorization_context={"required_permission": "reasoning:evidence"},
            provenance={
                "timestamp": _time.time(),
                "reasoning_context": reasoning_context,
                "artifact_kinds": artifact_kinds or [],
                "evidence_depth": depth,
            },
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "request_identity": self.request_identity,
            "interface_reference": self.interface_reference,
            "request_kind": self.request_kind,
            "consumer": self.consumer,
            "compatibility_revision": self.compatibility_revision,
            "priority_class": self.priority_class,
            "scope": {
                "temporal": dict(self.scope.temporal),
                "spatial": dict(self.scope.spatial),
                "modality": dict(self.scope.modality),
                "artifact": dict(self.scope.artifact),
                "projection": dict(self.scope.projection),
            },
            "authorization_context": dict(self.authorization_context),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptionInterfaceRequest":
        """Create request from dictionary."""
        return cls(
            request_identity=data.get("request_identity", f"request:{uuid.uuid4().hex[:16]}"),
            interface_reference=data.get("interface_reference", ""),
            request_kind=data.get("request_kind", ""),
            consumer=data.get("consumer", "unknown"),
            compatibility_revision=data.get("compatibility_revision", 1),
            priority_class=data.get("priority_class", RequestPriority.NORMAL),
            scope=RequestScope(
                temporal=dict(data.get("scope", {}).get("temporal", {})),
                spatial=dict(data.get("scope", {}).get("spatial", {})),
                modality=dict(data.get("scope", {}).get("modality", {})),
                artifact=dict(data.get("scope", {}).get("artifact", {})),
                projection=dict(data.get("scope", {}).get("projection", {})),
            ),
            authorization_context=dict(data.get("authorization_context", {})),
            provenance=dict(data.get("provenance", {})),
        )
    
    @property
    def is_valid(self) -> bool:
        """Validate request data."""
        if not self.request_identity or len(self.request_identity) == 0:
            return False
        
        if not self.interface_reference or len(self.interface_reference) == 0:
            return False
        
        if not self.request_kind or len(self.request_kind) == 0:
            return False
        
        if not self.consumer or len(self.consumer) == 0:
            return False
        
        return True


# =============================================================================
# REQUEST BUILDER
# =============================================================================


class PerceptionInterfaceRequestBuilder:
    """Mutable builder for constructing interface requests."""
    
    def __init__(self):
        self._request_identity: str = f"request:{uuid.uuid4().hex[:16]}"
        self._interface_reference: str = ""
        self._request_kind: str = ""
        self._consumer: str = "unknown"
        self._compatibility_revision: int = 1
        self._priority_class: int = RequestPriority.NORMAL
        self._scope: RequestScope = RequestScope()
        self._authorization_context: Dict[str, Any] = {}
        self._provenance: Dict[str, Any] = {"timestamp": _time.time()}
    
    def set_identity(self, identity: str) -> "PerceptionInterfaceRequestBuilder":
        """Set the request identity."""
        self._request_identity = identity
        return self
    
    def set_interface(self, interface_ref: str) -> "PerceptionInterfaceRequestBuilder":
        """Set the target interface reference."""
        self._interface_reference = interface_ref
        return self
    
    def set_kind(self, kind: str) -> "PerceptionInterfaceRequestBuilder":
        """Set the request kind."""
        self._request_kind = kind
        return self
    
    def set_consumer(self, consumer_id: str) -> "PerceptionInterfaceRequestBuilder":
        """Set the consumer identity."""
        self._consumer = consumer_id
        return self
    
    def set_revision(self, revision: int) -> "PerceptionInterfaceRequestBuilder":
        """Set the compatibility revision."""
        self._compatibility_revision = revision
        return self
    
    def set_priority(self, priority: int) -> "PerceptionInterfaceRequestBuilder":
        """Set the priority class."""
        self._priority_class = priority
        return self
    
    def set_temporal_scope(self, scope: Dict[str, Any]) -> "PerceptionInterfaceRequestBuilder":
        """Set temporal scope."""
        self._scope.temporal = dict(scope)
        return self
    
    def set_spatial_scope(self, scope: Dict[str, Any]) -> "PerceptionInterfaceRequestBuilder":
        """Set spatial scope."""
        self._scope.spatial = dict(scope)
        return self
    
    def set_modality_scope(self, scope: Dict[str, Any]) -> "PerceptionInterfaceRequestBuilder":
        """Set modality scope."""
        self._scope.modality = dict(scope)
        return self
    
    def set_artifact_scope(self, scope: Dict[str, Any]) -> "PerceptionInterfaceRequestBuilder":
        """Set artifact scope."""
        self._scope.artifact = dict(scope)
        return self
    
    def set_projection_scope(self, scope: Dict[str, Any]) -> "PerceptionInterfaceRequestBuilder":
        """Set projection scope."""
        self._scope.projection = dict(scope)
        return self
    
    def add_authorization(self, key: str, value: Any) -> "PerceptionInterfaceRequestBuilder":
        """Add authorization context entry."""
        self._authorization_context[key] = value
        return self
    
    def add_provenance(self, key: str, value: Any) -> "PerceptionInterfaceRequestBuilder":
        """Add provenance entry."""
        self._provenance[key] = value
        return self
    
    def build(self) -> PerceptionInterfaceRequest:
        """Build an immutable request."""
        if not self._interface_reference:
            raise ValueError("interface reference is required")
        
        if not self._request_kind:
            raise ValueError("request kind is required")
        
        return PerceptionInterfaceRequest(
            request_identity=self._request_identity,
            interface_reference=self._interface_reference,
            request_kind=self._request_kind,
            consumer=self._consumer,
            compatibility_revision=self._compatibility_revision,
            priority_class=self._priority_class,
            scope=self._scope,
            authorization_context=dict(self._authorization_context),
            provenance=dict(self._provenance),
        )


# =============================================================================
# REQUEST RESULT
# =============================================================================


@dataclass(frozen=True)
class RequestResult:
    """
    Result of request processing.
    
    Fields:
        status: Processing status (success, partial, empty, restricted, failed)
        payload: Response data if successful
        limitations: Any constraints that applied
        confidence: Confidence in the result (0.0-1.0)
        uncertainty: Uncertainty about the result (0.0-1.0)
        diagnostics: Diagnostic information
    """
    
    status: str  # SUCCESS, PARTIAL, EMPTY, RESTRICTED, FAILED
    payload: Optional[Any] = None
    limitations: Set[str] = field(default_factory=set)
    confidence: float = 0.0
    uncertainty: float = 1.0
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    def is_success(self) -> bool:
        """Check if request succeeded."""
        return self.status == "SUCCESS"
    
    def is_partial(self) -> bool:
        """Check if request partially succeeded."""
        return self.status == "PARTIAL"
    
    def is_empty(self) -> bool:
        """Check if result has no payload."""
        return self.payload is None or len(str(self.payload)) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status,
            "payload": self.payload,
            "limitations": list(self.limitations),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "diagnostics": dict(self.diagnostics),
        }


__all__ = [
    # Request kinds
    "RequestKind",
    
    # Priority classes
    "RequestPriority",
    
    # Scope
    "RequestScope",
    
    # Core request types
    "PerceptionInterfaceRequest",
    "PerceptionInterfaceRequestBuilder",
    
    # Result
    "RequestResult",
]