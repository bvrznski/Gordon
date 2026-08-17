# Perception Interface Contract - Phase 5.2.5
# ===========================================

"""
Perception Interface Contract: Defines stable communication semantics.

Every interface shall have an explicit, versioned contract that defines:
- What may be requested
- What may be published
- Semantic guarantees
- Compatibility requirements
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
import uuid


# =============================================================================
# INTERFACE KINDS
# =============================================================================


class InterfaceKind:
    """Types of perception interfaces."""
    
    SENSORS = "sensors"
    WORKSPACE = "workspace"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    ATTENTION = "attention"
    LEARNING = "learning"
    IDENTITY = "identity"
    REASONING = "reasoning"
    WORLD_MODEL = "world_model"
    COORDINATION = "coordination"
    GOVERNANCE = "governance"
    EXTERNAL = "external"


# =============================================================================
# STATUS CODES
# =============================================================================


class InterfaceStatus:
    """Interface status codes for discovery and health."""
    
    ACTIVE = "active"         # Interface is fully operational
    DEGRADED = "degraded"     # Some capabilities unavailable
    MAINTENANCE = "maintenance"  # Interface in maintenance mode
    UNAVAILABLE = "unavailable"  # Interface not available


# =============================================================================
# COMPATIBILITY REVISIONS
# =============================================================================


@dataclass(frozen=True)
class CompatibilityRevision:
    """
    Compatibility revision marker.
    
    Fields:
        major: Major version (breaking changes increment this)
        minor: Minor version (additive features)
        patch: Patch version (bug fixes only)
    """
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: "CompatibilityRevision") -> bool:
        """Check if two revisions are compatible (same major)."""
        return self.major == other.major
    
    def is_backward_compatible(self, other: "CompatibilityRevision") -> bool:
        """
        Check if this revision can handle requests from the other.
        
        A revision is backward compatible if it supports at least as many
        features as the other revision (and same major version).
        """
        return (
            self.major == other.major and 
            (self.minor > other.minor or 
             (self.minor == other.minor and self.patch >= other.patch))
        )
    
    def is_forward_compatible(self, other: "CompatibilityRevision") -> bool:
        """Check if this revision can be used by systems expecting 'other'."""
        return (
            self.major == other.major and 
            (self.minor < other.minor or 
             (self.minor == other.minor and self.patch <= other.patch))
        )


# =============================================================================
# AUTHORIZATION CONTEXT
# =============================================================================


@dataclass(frozen=True)
class AuthorizationContext:
    """
    Authorization context for interface communication.
    
    Fields:
        subject: Who is making the request
        audience: Intended recipient of the message
        permissions: Set of allowed operations
        scopes: Scope boundaries for operations
        timestamp: When authorization was issued
        expiration: When authorization expires
    """
    subject: str
    audience: str
    permissions: Set[str] = field(default_factory=set)
    scopes: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=_time.time)
    expiration: Optional[float] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if authorization has expired."""
        if self.expiration is None:
            return False
        return _time.time() > self.expiration
    
    @property
    def remaining_ttl(self) -> float:
        """Get remaining time-to-live in seconds (0 if expired)."""
        if self.expiration is None:
            return float('inf')
        return max(0.0, self.expiration - _time.time())
    
    def has_permission(self, permission: str) -> bool:
        """Check if this context grants a specific permission."""
        return permission in self.permissions
    
    def is_in_scope(self, scope_name: str, value: Any = None) -> bool:
        """Check if an operation is within scope."""
        if scope_name not in self.scopes:
            # No explicit scope means allowed
            return True
        
        scope_rule = self.scopes[scope_name]
        
        if isinstance(scope_rule, dict):
            # Complex scope rule (e.g., {"max_artifacts": 100})
            if value is None:
                return True
            for key, constraint in scope_rule.items():
                if hasattr(constraint, '__call__'):
                    return constraint(value)
                elif isinstance(value, dict) and key in value:
                    # Value has the same key
                    pass
                else:
                    # Basic comparison
                    pass
            return True
        
        return True  # Default: allow if scope exists


# =============================================================================
# INTERFACE CONTRACT
# =============================================================================


@dataclass(frozen=True)
class PerceptionInterfaceContract:
    """
    Formal contract for a Perception Interface.
    
    This defines the stable communication boundary between Perception and
    external subsystems. Consumers interact with Perception exclusively
    through contracts, never through internal implementation details.
    
    Contract fields:
        interface_identity: Unique identifier for this interface type
        provider_identity: Identity of the Perception system
        supported_requests: Set of request kinds this interface accepts
        supported_responses: Set of response kinds this interface produces
        supported_events: Set of event kinds this interface publishes
        supported_projection_kinds: Projection kinds this interface handles
        compatibility_revision: Version of the contract specification
        authorization_requirements: Permissions required for operations
        subscription_support: Types of subscriptions supported
        synchronization_guarantees: guarantees about state consistency
        failure_semantics: How failures are reported and handled
        
    Contract laws:
        CONTRACT-LAW-001: Every Interface shall define one explicit Interface Contract.
        CONTRACT-LAW-002: Every Contract shall identify its provider and intended consumer class.
        CONTRACT-LAW-003: Every Contract shall define supported Requests, Responses, Events and Projection kinds.
        CONTRACT-LAW-004: Every Contract shall declare compatibility and version information.
        CONTRACT-LAW-005: Every Contract shall declare authorization requirements.
        CONTRACT-LAW-006: Every Contract shall declare failure and degradation semantics.
        CONTRACT-LAW-007: Contracts shall not depend on internal module layout or implementation class hierarchy.
        CONTRACT-LAW-008: Contract interpretation shall remain deterministic.
    """
    
    # Identity
    interface_identity: str  # e.g., "sensors", "workspace", "memory"
    provider_identity: str   # The Perception system identifier
    
    # Capabilities
    supported_requests: Set[str]
    supported_responses: Set[str]
    supported_events: Set[str]
    supported_projection_kinds: Set[str] = field(default_factory=set)
    
    # Versioning and compatibility
    compatibility_revision: CompatibilityRevision = field(
        default_factory=lambda: CompatibilityRevision(1, 0, 0)
    )
    
    # Authorization
    authorization_requirements: Dict[str, str] = field(default_factory=dict)
    """
    Maps operation kinds to required permission strings.
    Example: {"acquisition": "sensor:read", "publication": "data:publish"}
    """
    
    # Subscription support
    subscription_support: Set[str] = field(default_factory=set)
    """
    Supported subscription types:
        - snapshot: One-time immutable view
        - stream: Continuous update sequence  
        - delta: Incremental changes only
        - periodic: Scheduled updates
        - event_driven: On-demand events
        - session_bound: For session lifetime
        - revision_bound: Until specific revision
    """
    
    # Synchronization guarantees
    synchronization_guarantees: Set[str] = field(default_factory=set)
    """
    Guarantees about state consistency:
        - causal_order: Messages maintain causal ordering
        - at_least_once: No message loss (may have duplicates)
        - at_most_once: No duplicates (may lose messages)
        - exactly_once: Neither loss nor duplicates
        - revision_aware: Consumers track revisions explicitly
    """
    
    # Failure semantics
    failure_semantics: Set[str] = field(default_factory=set)
    """
    How failures are handled:
        - fail_fast: Fail immediately on error
        - retry_enabled: Automatic retries enabled
        - circuit_breaker: Break circuit after repeated failures
        - partial_responses: Allow partial success
        - graceful_degradation: Reduce quality rather than fail
    """
    
    # Limitations
    max_batch_size: int = 1000
    """Maximum items in a single batch."""
    
    max_message_size_bytes: int = 1_048_576  # 1 MB default
    """Maximum size of any single message."""
    
    default_timeout_seconds: float = 30.0
    """Default timeout for synchronous operations."""
    
    @classmethod
    def create_sensors_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Sensors Interface contract.
        
        The Sensors Interface is inbound-only: it accepts acquired evidence
        into the owning Modality. It does not expose Perception to cognition.
        """
        return cls(
            interface_identity=InterfaceKind.SENSORS,
            provider_identity=provider_id,
            supported_requests={
                "acquisition",       # Request sensor acquisition
                "descriptor_query",  # Query available sensors
                "capability_query",  # Query specific capabilities
                "health_check",      # Check interface health
                "discovery",         # Discover available interfaces
            },
            supported_responses={
                "acquisition_result",
                "descriptor_response",
                "capability_response",
                "health_response",
                "discovery_response",
            },
            supported_events={
                "evidence_published",     # New evidence added to modality
                "sensor_status_change",   # Sensor availability changed
                "acquisition_failure",    # Acquisition failed
                "stream_update",          # Stream state updated
                "health_degraded",        # Interface health degraded
            },
            supported_projection_kinds={
                "signal",      # Raw sensor signals
                "observation", # Processed observations
            },
            authorization_requirements={
                "acquisition": "sensor:read",
                "descriptor_query": "sensor:discover",
                "capability_query": "sensor:info",
            },
            subscription_support={"stream", "snapshot", "event_driven"},
            synchronization_guarantees={"causal_order", "at_least_once"},
            failure_semantics={"fail_fast", "circuit_breaker", "partial_responses"},
        )
    
    @classmethod
    def create_workspace_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Workspace Interface contract.
        
        The Workspace Interface publishes bounded perceptual candidates to the
        Workspace Network and receives explicit Workspace requests.
        """
        return cls(
            interface_identity=InterfaceKind.WORKSPACE,
            provider_identity=provider_id,
            supported_requests={
                "projection_request",    # Request workspace projection
                "snapshot_request",      # Request snapshot view
                "stream_subscribe",      # Subscribe to updates
                "detail_expansion",      # Request more detail on artifact
                "update_delta",          # Request delta from base revision
            },
            supported_responses={
                "projection_response",
                "snapshot_response",
                "stream_subscribed",
                "detail_expansion_response",
                "delta_response",
            },
            supported_events={
                "projection_published",   # New projection available
                "snapshot_published",     # Snapshot published
                "artifact_updated",       # Artifact content changed
                "workspace_conflict",     # Conflict detected in workspace
                "update_gap_detected",    # Stream gap occurred
            },
            authorization_requirements={
                "projection_request": "workspace:read",
                "snapshot_request": "workspace:read",
                "stream_subscribe": "workspace:subscribe",
            },
            subscription_support={"stream", "snapshot", "delta"},
            synchronization_guarantees={"revision_aware", "at_least_once"},
            failure_semantics={"graceful_degradation", "partial_responses"},
        )
    
    @classmethod
    def create_memory_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Memory Interface contract.
        
        The Memory Interface submits validated perceptual artifacts as candidate
        evidence for Memory admission. Perception never writes directly into Memory.
        """
        return cls(
            interface_identity=InterfaceKind.MEMORY,
            provider_identity=provider_id,
            supported_requests={
                "candidate_submission",    # Submit memory candidate
                "admission_query",         # Query admission status
                "correlation_request",     # Request memory correlation
            },
            supported_responses={
                "submission_response",
                "admission_response",
                "correlation_response",
            },
            supported_events={
                "admission_result",      # Memory admission decision
                "correlation_produced",  # New correlation produced
                "memory_update",         # Memory state changed
            },
            authorization_requirements={
                "candidate_submission": "memory:submit",
                "admission_query": "memory:read",
                "correlation_request": "memory:correlate",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"causal_order", "exactly_once"},
            failure_semantics={"fail_fast", "partial_responses"},
        )
    
    @classmethod
    def create_knowledge_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Knowledge Interface contract.
        
        The Knowledge Interface supports perceptual grounding and semantic
        normalization without allowing Knowledge to rewrite observational evidence.
        """
        return cls(
            interface_identity=InterfaceKind.KNOWLEDGE,
            provider_identity=provider_id,
            supported_requests={
                "grounding_request",     # Request concept grounding
                "schema_query",          # Query schema mappings
                "ontology_check",        # Check ontology compatibility
            },
            supported_responses={
                "grounding_response",
                "schema_response",
                "ontology_response",
            },
            supported_events={
                "grounding_produced",    # Grounding result produced
                "mismatch_detected",     # Semantic mismatch detected
            },
            authorization_requirements={
                "grounding_request": "knowledge:read",
                "schema_query": "knowledge:read",
                "ontology_check": "knowledge:check",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"revision_aware"},
            failure_semantics={"graceful_degradation", "partial_responses"},
        )
    
    @classmethod
    def create_attention_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create an Attention Interface contract.
        
        The Attention Interface exposes perceptual candidates for prioritization
        and receives explicit selection or inspection requests.
        Perception does not own Attention.
        """
        return cls(
            interface_identity=InterfaceKind.ATTENTION,
            provider_identity=provider_id,
            supported_requests={
                "candidate_publication",  # Publish attention candidate
                "inspection_request",     # Request detailed inspection
                "detail_expansion",       # Request expanded details
                "refresh_request",        # Request projection refresh
            },
            supported_responses={
                "candidate_accepted",      # Candidate accepted for attention
                "inspection_response",
                "detail_expansion_response",
                "refresh_complete",
            },
            supported_events={
                "attention_assigned",     # Attention allocated to candidate
                "inspection_requested",   # Inspection requested
                "priority_changed",       # Priority changed
            },
            authorization_requirements={
                "candidate_publication": "attention:publish",
                "inspection_request": "attention:inspect",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"causal_order"},
            failure_semantics={"fail_fast"},
        )
    
    @classmethod
    def create_learning_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Learning Interface contract.
        
        The Learning Interface exposes historical performance and receives approved
        improvement proposals. Learning does not mutate Perception directly.
        """
        return cls(
            interface_identity=InterfaceKind.LEARNING,
            provider_identity=provider_id,
            supported_requests={
                "evidence_publication",   # Publish learning evidence
                "proposal_submission",    # Submit learning proposal
            },
            supported_responses={
                "evidence_acknowledged",
                "proposal_response",      # Response to proposal (approved/rejected)
            },
            supported_events={
                "proposal_reviewed",     # Proposal reviewed
                "deployment_ready",      # Deployment ready for approval
                "performance_update",    # Performance metrics updated
            },
            authorization_requirements={
                "evidence_publication": "learning:publish",
                "proposal_submission": "learning:propose",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"revision_aware", "at_least_once"},
            failure_semantics={"fail_fast"},
        )
    
    @classmethod
    def create_identity_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create an Identity Interface contract.
        
        The Identity Interface supports self-related and agent-related perceptual
        grounding without making Perception the owner of personal identity.
        """
        return cls(
            interface_identity=InterfaceKind.IDENTITY,
            provider_identity=provider_id,
            supported_requests={
                "grounding_request",     # Request identity grounding
                "correlation_request",   # Request correlation with existing anchors
            },
            supported_responses={
                "grounding_response",
                "correlation_response",
            },
            supported_events={
                "identity_anchor",       # New identity anchor established
                "conflict_detected",     # Identity conflict detected
            },
            authorization_requirements={
                "grounding_request": "identity:read",
                "correlation_request": "identity:correlate",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"causal_order"},
            failure_semantics={"fail_fast"},
        )
    
    @classmethod
    def create_reasoning_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Reasoning Interface contract.
        
        The Reasoning Interface exposes evidence and accepts requests for bounded
        perceptual clarification. Reasoning may interpret Perception.
        It shall not rewrite it.
        """
        return cls(
            interface_identity=InterfaceKind.REASONING,
            provider_identity=provider_id,
            supported_requests={
                "evidence_request",      # Request evidence for reasoning
                "hypothesis_check",      # Check against existing hypotheses
                "clarification_request", # Request clarification on artifacts
            },
            supported_responses={
                "evidence_response",
                "hypothesis_response",
                "clarification_response",
            },
            supported_events={
                "hypothesis_tested",     # Hypothesis tested
                "contradiction_found",   # Contradiction with hypothesis
                "confirmation_found",    # Evidence confirms hypothesis
            },
            authorization_requirements={
                "evidence_request": "reasoning:evidence",
                "hypothesis_check": "reasoning:check",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"revision_aware", "causal_order"},
            failure_semantics={"fail_fast"},
        )
    
    @classmethod
    def create_world_model_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a World Model Interface contract.
        
        The World Model Interface publishes observational updates and receives
        expectation or state-estimate context. Perception remains the authority
        for observations.
        """
        return cls(
            interface_identity=InterfaceKind.WORLD_MODEL,
            provider_identity=provider_id,
            supported_requests={
                "update_publication",   # Publish world model update
                "expectation_set",      # Set expectations for future state
                "mismatch_report",      # Report expectation mismatch
            },
            supported_responses={
                "update_accepted",
                "expectation_acknowledged",
                "mismatch_response",
            },
            supported_events={
                "world_state_updated",    # World model state updated
                "expectation_mismatch",   # Mismatch with expectations
                "state_transition",       # State transition detected
            },
            authorization_requirements={
                "update_publication": "world_model:write",
                "expectation_set": "world_model:configure",
            },
            subscription_support={"stream", "event_driven"},
            synchronization_guarantees={"revision_aware", "at_least_once"},
            failure_semantics={"fail_fast", "circuit_breaker"},
        )
    
    @classmethod
    def create_coordination_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Coordination Interface contract.
        
        The Coordination Interface exchanges operational status, dependencies,
        availability and synchronization information.
        """
        return cls(
            interface_identity=InterfaceKind.COORDINATION,
            provider_identity=provider_id,
            supported_requests={
                "status_request",       # Request coordination status
                "synchronization_request",  # Request sync operation
                "dependency_query",     # Query dependencies
            },
            supported_responses={
                "status_response",
                "synchronization_result",
                "dependency_response",
            },
            supported_events={
                "coordination_update",    # Coordination state changed
                "dependency_changed",     # Dependencies changed
                "sync_completed",         # Sync operation completed
            },
            authorization_requirements={
                "status_request": "coordination:read",
                "synchronization_request": "coordination:control",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"revision_aware", "causal_order"},
            failure_semantics={"fail_fast", "graceful_degradation"},
        )
    
    @classmethod
    def create_governance_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create a Governance Interface contract.
        
        The Governance Interface exposes the complete evidence required to evaluate
        Perception integrity, compliance, drift and correctness.
        Governance supervises; it does not perform ordinary Perception execution.
        """
        return cls(
            interface_identity=InterfaceKind.GOVERNANCE,
            provider_identity=provider_id,
            supported_requests={
                "evidence_request",     # Request governance evidence
                "certification_request",  # Request certification assessment
                "drift_request",         # Request drift analysis
            },
            supported_responses={
                "evidence_response",
                "certification_response",
                "drift_response",
            },
            supported_events={
                "certification_result",   # Certification result produced
                "drift_detected",        # Drift detected
                "compliance_issue",      # Compliance issue found
            },
            authorization_requirements={
                "evidence_request": "governance:evidence",
                "certification_request": "governance:certify",
            },
            subscription_support={"event_driven"},
            synchronization_guarantees={"revision_aware", "at_least_once"},
            failure_semantics={"fail_fast"},
        )
    
    @classmethod
    def create_external_contract(cls, provider_id: str) -> "PerceptionInterfaceContract":
        """
        Create an External Interface contract.
        
        The External Interface exposes approved Perception capabilities outside Gordon.
        It is the most restrictive Perception Interface.
        """
        return cls(
            interface_identity=InterfaceKind.EXTERNAL,
            provider_identity=provider_id,
            supported_requests={
                "public_projection",    # Request public projection
                "subscription_create",  # Create external subscription
                "rate_limit_query",     # Query rate limits
            },
            supported_responses={
                "projection_response",
                "subscription_created",
                "rate_limit_response",
            },
            supported_events={
                "publication_published",   # Public publication
                "subscription_update",     # Subscription stream update
                "subscription_terminated", # Subscription ended
            },
            authorization_requirements={
                "public_projection": "external:read",
                "subscription_create": "external:subscribe",
            },
            subscription_support={"stream", "snapshot"},
            synchronization_guarantees={"revision_aware", "at_least_once"},
            failure_semantics={"fail_fast", "circuit_breaker"},
            max_message_size_bytes=104_857,  # 100 KB (stricter for external)
        )
    
    def get_required_permission(self, operation: str) -> Optional[str]:
        """Get the required permission for a given operation."""
        return self.authorization_requirements.get(operation)
    
    def check_revision_compatibility(
        self,
        other_revision: CompatibilityRevision
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a given revision is compatible with this contract.
        
        Returns:
            Tuple of (is_compatible, reason_if_not)
        """
        # Must have same major version for breaking change compatibility
        if not self.compatibility_revision.is_compatible_with(other_revision):
            return False, f"Major version mismatch: expected {self.compatibility_revision.major}, got {other_revision.major}"
        
        return True, None


# =============================================================================
# INTERFACE DISCOVERY
# =============================================================================


@dataclass(frozen=True)
class InterfaceDiscoveryResult:
    """
    Result of interface discovery.
    
    Fields:
        interface_identity: The type of interface discovered
        provider_identity: Identity of the provider system
        available_interfaces: List of available interfaces with their contracts
        capabilities: Set of supported capability kinds
        health_status: Current health status of the interface
        revision: Version of the interface specification
    """
    
    interface_identity: str
    provider_identity: str
    available_interfaces: Dict[str, PerceptionInterfaceContract]
    capabilities: Set[str] = field(default_factory=set)
    health_status: str = InterfaceStatus.ACTIVE
    revision: CompatibilityRevision = field(
        default_factory=lambda: CompatibilityRevision(1, 0, 0)
    )
    
    @classmethod
    def empty(cls, provider_id: str) -> "InterfaceDiscoveryResult":
        """Create an empty discovery result."""
        return cls(
            interface_identity="unknown",
            provider_identity=provider_id,
            available_interfaces={},
            health_status=InterfaceStatus.UNAVAILABLE,
        )


# =============================================================================
# INTERFACE HEALTH
# =============================================================================


@dataclass(frozen=True)
class InterfaceHealth:
    """
    Health status of a Perception Interface.
    
    Fields:
        availability: Fraction of time interface is available (0.0-1.0)
        latency_ms: Average response latency in milliseconds
        throughput_rps: Requests per second the interface can handle
        compatibility_health: Status of compatibility checking
        authorization_health: Status of authorization enforcement
        subscription_health: Status of subscription management
        publication_health: Status of publication mechanism
        failure_rate: Rate of failures per operation
        degradation: Current degradation level (if any)
    """
    
    availability: float = 1.0
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    compatibility_health: str = InterfaceStatus.ACTIVE
    authorization_health: str = InterfaceStatus.ACTIVE
    subscription_health: str = InterfaceStatus.ACTIVE
    publication_health: str = InterfaceStatus.ACTIVE
    failure_rate: float = 0.0
    degradation: Optional[str] = None
    
    def is_healthy(self) -> bool:
        """Check if the interface is healthy."""
        return (
            self.availability >= 0.95 and
            self.compatibility_health == InterfaceStatus.ACTIVE and
            self.authorization_health == InterfaceStatus.ACTIVE and
            self.subscription_health == InterfaceStatus.ACTIVE and
            self.publication_health == InterfaceStatus.ACTIVE and
            self.degradation is None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "availability": self.availability,
            "latency_ms": self.latency_ms,
            "throughput_rps": self.throughput_rps,
            "compatibility_health": self.compatibility_health,
            "authorization_health": self.authorization_health,
            "subscription_health": self.subscription_health,
            "publication_health": self.publication_health,
            "failure_rate": self.failure_rate,
            "degradation": self.degradation,
        }


# =============================================================================
# CAPABILITY DESCRIPTOR
# =============================================================================


@dataclass(frozen=True)
class PerceptionCapabilityDescriptor:
    """
    Descriptor for a specific interface capability.
    
    Fields:
        capability_identity: Unique identifier for the capability
        capability_kind: The type of capability (e.g., "acquisition", "projection")
        interface_reference: Which interface provides this capability
        availability: Whether the capability is currently available
        limitations: Any constraints on usage
        revision: Version of the capability specification
        authorization: Required permissions to use
    """
    
    capability_identity: str
    capability_kind: str
    interface_reference: str
    
    availability: bool = True
    limitations: Dict[str, Any] = field(default_factory=dict)
    revision: CompatibilityRevision = field(
        default_factory=lambda: CompatibilityRevision(1, 0, 0)
    )
    authorization: Set[str] = field(default_factory=set)
    
    @classmethod
    def create_acquisition_capability(cls, sensor_kind: str) -> "PerceptionCapabilityDescriptor":
        """Create a sensor acquisition capability descriptor."""
        return cls(
            capability_identity=f"acquisition:{sensor_kind}",
            capability_kind="acquisition",
            interface_reference=InterfaceKind.SENSORS,
            availability=True,
            revision=CompatibilityRevision(1, 0, 0),
        )
    
    @classmethod
    def create_projection_capability(cls, projection_kind: str) -> "PerceptionCapabilityDescriptor":
        """Create a projection capability descriptor."""
        return cls(
            capability_identity=f"projection:{projection_kind}",
            capability_kind="projection",
            interface_reference=InterfaceKind.WORKSPACE,
            availability=True,
            revision=CompatibilityRevision(1, 0, 0),
        )
    
    def is_available(self) -> bool:
        """Check if the capability is currently available."""
        return self.availability and not any(
            # Check for various limitations that might block usage
            isinstance(v, bool) and not v 
            for v in self.limitations.values()
            if isinstance(v, bool)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "capability_identity": self.capability_identity,
            "capability_kind": self.capability_kind,
            "interface_reference": self.interface_reference,
            "availability": self.availability,
            "limitations": dict(self.limitations),
            "revision": str(self.revision),
            "authorization": list(self.authorization),
        }


# =============================================================================
# COMPATIBILITY EVALUATION
# =============================================================================


class CompatibilityEvaluator:
    """
    Evaluates compatibility between contracts and revisions.
    
    COMPATIBILITY-LAW-001: Compatibility evaluation shall precede Request acceptance and Response publication.
    COMPATIBILITY-LAW-002: Provider and consumer contract revisions shall remain explicit.
    COMPATIBILITY-LAW-003: Required, optional, unsupported and deprecated fields shall remain distinguishable.
    COMPATIBILITY-LAW-004: Compatibility migrations shall remain explicit and versioned.
    COMPATIBILITY-LAW-005: Silent field dropping shall not satisfy compatibility.
    COMPATIBILITY-LAW-006: Compatibility failure shall produce an explicit failure or negotiated alternative.
    COMPATIBILITY-LAW-007: Compatibility history shall remain inspectable.
    COMPATIBILITY-LAW-008: Compatibility evaluation shall remain deterministic.
    """
    
    @staticmethod
    def evaluate_contract_compatibility(
        provider_contract: PerceptionInterfaceContract,
        consumer_contract_reference: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate if a consumer contract is compatible with the provider contract.
        
        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        issues = []
        
        # Check version compatibility
        compat_result, reason = provider_contract.check_revision_compatibility(
            consumer_contract_reference or ""
        )
        if not compat_result:
            issues.append(reason)
        
        # TODO: Add more detailed contract field compatibility checks
        
        return len(issues) == 0, issues
    
    @staticmethod
    def evaluate_request_compatibility(
        request_kind: str,
        supported_requests: Set[str],
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluate if a request kind is supported.
        
        Returns:
            Tuple of (is_compatible, reason_if_not)
        """
        if request_kind not in supported_requests:
            return False, f"Unsupported request kind: {request_kind}"
        
        return True, None


# =============================================================================
# VERSION NEGOTIATION
# =============================================================================


@dataclass(frozen=True)
class VersionNegotiationResult:
    """
    Result of version negotiation between provider and consumer.
    
    Fields:
        protocol_revision: Negotiated protocol revision
        schema_revision: Negotiated schema revision  
        contract_revision: Negotiated contract revision
        feature_set: Set of features available at negotiated version
        fallback_used: Whether a fallback was used
    """
    
    protocol_revision: CompatibilityRevision
    schema_revision: CompatibilityRevision
    contract_revision: CompatibilityRevision
    feature_set: Set[str] = field(default_factory=set)
    fallback_used: bool = False
    
    def is_optimal(self) -> bool:
        """Check if optimal version was negotiated (no fallback)."""
        return not self.fallback_used


class VersionNegotiator:
    """
    Negotiates versions between Perception and consumers.
    
    NEGOTIATION-LAW-001: Version negotiation shall precede incompatible communication.
    NEGOTIATION-LAW-002: Protocol, schema, contract and feature revisions shall remain distinguishable.
    NEGOTIATION-LAW-003: Negotiation shall preserve supported minimum and maximum revisions.
    NEGOTIATION-LAW-004: Breaking incompatibilities shall remain explicit.
    NEGOTIATION-LAW-005: Fallback revisions shall require explicit compatibility guarantees.
    NEGOTIATION-LAW-006: Negotiation failure shall not silently degrade required semantics.
    NEGOTIATION-LAW-007: Negotiation history shall remain inspectable.
    NEGOTIATION-LAW-008: Negotiation shall remain deterministic.
    """
    
    def __init__(self, provider_contract: PerceptionInterfaceContract):
        self.provider_contract = provider_contract
    
    def negotiate(
        self,
        consumer_revision: CompatibilityRevision
    ) -> VersionNegotiationResult:
        """
        Negotiate version with a consumer's requested revision.
        
        Returns the highest compatible version the provider can support.
        """
        provider_rev = self.provider_contract.compatibility_revision
        
        # Check if consumer revision is compatible (same major)
        if not consumer_revision.is_compatible_with(provider_rev):
            # Try to find a fallback (minimum supported)
            fallback = CompatibilityRevision(min(provider_rev.major, 1), 0, 0)
            
            return VersionNegotiationResult(
                protocol_revision=fallback,
                schema_revision=fallback,
                contract_revision=fallback,
                feature_set={"fallback"},
                fallback_used=True,
            )
        
        # Choose the minimum of provider and consumer revisions
        # This ensures both can understand each other
        if consumer_revision <= provider_rev:
            negotiated = consumer_revision
            fallback_used = False
        else:
            negotiated = provider_rev
            fallback_used = True
        
        return VersionNegotiationResult(
            protocol_revision=negotiated,
            schema_revision=negotiated,
            contract_revision=negotiated,
            feature_set=self._get_features_for_revision(negotiated),
            fallback_used=fallback_used,
        )
    
    def _get_features_for_revision(self, revision: CompatibilityRevision) -> Set[str]:
        """Get the set of features available at a given revision."""
        features = {"base"}
        
        # Add features based on minor version
        if revision.minor >= 1:
            features.add("streaming")
        if revision.minor >= 2:
            features.add("batch_operations")
        if revision.minor >= 3:
            features.add("revision_tracking")
        if revision.minor >= 4:
            features.add("delta_updates")
        
        return features


__all__ = [
    # Interface kinds
    "InterfaceKind",
    
    # Status codes
    "InterfaceStatus",
    
    # Versioning and compatibility
    "CompatibilityRevision",
    
    # Authorization
    "AuthorizationContext",
    
    # Core contract
    "PerceptionInterfaceContract",
    
    # Discovery and health
    "InterfaceDiscoveryResult",
    "InterfaceHealth",
    
    # Capabilities
    "PerceptionCapabilityDescriptor",
    
    # Compatibility evaluation
    "CompatibilityEvaluator",
    
    # Version negotiation
    "VersionNegotiationResult",
    "VersionNegotiator",
]