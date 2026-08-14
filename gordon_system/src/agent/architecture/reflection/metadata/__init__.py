"""Metadata Taxonomy - Phase 3.23 Canonical Reflection Architecture.
================================================================================

Canonical metadata system for Gordon Core reflection architecture.

METAPHILOSOPHY:
- Metadata describes, it does not execute
- Metadata is immutable once captured  
- Metadata is discoverable, structured, and typed
- Metadata is never the implementation

ARCHITECTURAL BOUNDARIES:
- Reflection (this module) = DESCRIBES what exists
- Execution (phase 3.10+) = PERFORMS actions
- State (phase 3.15+) = MAINTAINS runtime conditions
- Identity (phase 3.19+) = IDENTIFIES who/what
- Security (phase 3.22+) = PROTECTS boundaries

One canonical metadata system shall exist for the entire repository.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


# =============================================================================
# METADATA VERSIONING & PROVENANCE
# =============================================================================


class MetadataVersion(Enum):
    """Metadata schema versions for evolution tracking."""
    
    V1_0_0 = "1.0.0"
    V2_0_0 = "2.0.0"


@dataclass(frozen=True)
class Provenance:
    """
    Where metadata came from.
    
    Immutable record of creation and modification history.
    """
    
    created_by: str  # System, human, automated process
    created_at_utc: float
    schema_version: MetadataVersion = MetadataVersion.V1_0_0
    source_type: str = "discovery"  # discovery, annotation, manual, migration
    source_location: Optional[str] = None


# =============================================================================
# IDENTITY METADATA - What is this?
# =============================================================================


@dataclass(frozen=True)
class IdentityMetadata:
    """
    Identity metadata for any architectural entity.
    
    Answers: "What IS this?"
    
    Immutable and canonical. Never changes after initial capture.
    """
    
    # Canonical identity
    id: str  # Unique identifier (UUID or deterministic hash)
    name: str
    type_: str  # Class, Function, Module, Package, Service, etc.
    
    # Location
    location: str  # file:line or module.path
    package_name: str
    
    # Classification
    category: str  # e.g., "core", "runtime", "execution"
    layer: str  # Architectural layer (Phase X.Y.Z)
    
    # Metadata for identity
    version: str = "1.0.0"
    stability: str = "stable"  # stable, beta, experimental, deprecated


# =============================================================================
# OWNERSHIP METADATA - Who owns this?
# =============================================================================


@dataclass(frozen=True)
class OwnerMetadata:
    """Owner information for an entity."""
    
    name: str
    contact: Optional[str] = None
    team: Optional[str] = None
    category: str = "unknown"  # Core, Runtime, Execution, etc.


@dataclass(frozen=True)
class OwnershipMetadata:
    """
    Ownership metadata for any architectural entity.
    
    Answers: "Who owns this?"
    
    One owner per entity. Immutable once assigned.
    """
    
    owner: OwnerMetadata
    ownership_type: str = "primary"  # primary, co-owner, stakeholder
    
    # Responsibility domain
    responsibility: str  # What the owner is responsible for
    scope: str = "runtime"  # runtime, design, documentation, testing


# =============================================================================
# VERSION & GENERATION METADATA - Which version?
# =============================================================================


@dataclass(frozen=True)
class VersionMetadata:
    """Version information for an entity."""
    
    semantic_version: str  # MAJOR.MINOR.PATCH
    build_number: Optional[str] = None
    release_channel: str = "release"  # alpha, beta, rc, release
    
    # Generation tracking
    generation: int = 1  # How many times this has been regenerated
    last_generated_at_utc: float = field(default_factory=time.time)


# =============================================================================
# LIFECYCLE METADATA - What is its lifecycle?
# =============================================================================


class LifecyclePhase(Enum):
    """Lifecycle phases for an entity."""
    
    PLANNED = "planned"
    DESIGNING = "designing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    OBSOLETE = "obsolete"


@dataclass(frozen=True)
class LifecycleMetadata:
    """
    Lifecycle state metadata for an entity.
    
    Answers: "Where is this in its lifecycle?"
    
    State machine: Planned -> Designing -> Implementing -> Testing -> Stable -> Deprecated -> Obsolete
    """
    
    current_phase: LifecyclePhase
    phase_started_at_utc: float
    
    # Transition tracking
    next_expected_phase: Optional[LifecyclePhase] = None
    expected_completion_at_utc: Optional[float] = None
    
    # Exit criteria (what must be true to move to next phase)
    exit_criteria_met: bool = False


# =============================================================================
# CAPABILITY METADATA - What can it do?
# =============================================================================


class CapabilityType(Enum):
    """Types of capabilities an entity may provide."""
    
    COMPUTATION = "computation"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    COORDINATION = "coordination"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    EXECUTION = "execution"
    INFRASTRUCTURE = "infrastructure"


@dataclass(frozen=True)
class CapabilityMetadata:
    """
    Capability metadata for an entity.
    
    Answers: "What can this do?"
    
    A capability is something the entity CAN do, not what it IS doing.
    """
    
    name: str  # e.g., "Schedule Tasks", "Store State"
    type_: CapabilityType
    description: str
    
    # Contract details
    interface: Optional[str] = None  # Interface class or protocol
    guarantees: Tuple[str, ...] = ()  # e.g., "at-least-once delivery"
    
    # Scope
    scope: str = "runtime"  # runtime, design-time, compile-time


# =============================================================================
# INTERFACE METADATA - How does it interface?
# =============================================================================


@dataclass(frozen=True)
class InterfaceContract:
    """A contract defined by an interface."""
    
    name: str
    parameters: Tuple[str, ...] = ()
    returns: Optional[str] = None
    throws: Tuple[str, ...] = ()


@dataclass(frozen=True)
class InterfaceMetadata:
    """
    Interface metadata for an entity.
    
    Answers: "What interfaces does this expose?"
    
    Describes public contracts without revealing implementation.
    """
    
    # Exposed interfaces
    interfaces: Tuple[str, ...]  # Fully qualified interface names
    
    # Public API surface
    public_api: Tuple[str, ...]
    
    # Contract details
    contracts: Tuple[InterfaceContract, ...] = ()
    
    # Compatibility
    is_stable: bool = True
    breaking_changes_in_next: Optional[str] = None


# =============================================================================
# DEPENDENCY METADATA - What does it need?
# =============================================================================


class DependencyType(Enum):
    """Types of dependencies."""
    
    RUNTIME = "runtime"  # Required at runtime
    CONSTRUCTION = "construction"  # Required for construction
    OPTIONAL = "optional"  # May be provided
    TRANSPORT = "transport"  # Network/transport dependency
    CONFIGURATION = "configuration"  # Configuration data


@dataclass(frozen=True)
class DependencyMetadata:
    """
    Dependency metadata for an entity.
    
    Answers: "What does this need?"
    
    Complete dependency graph representation.
    """
    
    entity_id: str  # The dependent entity
    depends_on: str  # What it depends on
    
    type_: DependencyType
    required: bool = True
    
    # Qualifiers
    optional_alternative: Optional[str] = None  # Fallback if primary fails
    condition: Optional[str] = None  # e.g., "if feature_flag_x is enabled"


# =============================================================================
# SECURITY METADATA - What are its security properties?
# =============================================================================


class SecurityClassification(Enum):
    """Security classification levels."""
    
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


@dataclass(frozen=True)
class SecurityMetadata:
    """
    Security properties of an entity.
    
    Answers: "What are its security properties?"
    
    Never changes - security classification is fundamental.
    """
    
    classification: SecurityClassification
    access_control: str  # e.g., "role-based", "attribute-based"
    required_roles: Tuple[str, ...] = ()
    encryption_at_rest: bool = False
    encryption_in_transit: bool = True
    
    # Audit
    audit_enabled: bool = True
    sensitive_data_handled: bool = False


# =============================================================================
# CONFIGURATION METADATA - How is it configured?
# =============================================================================


@dataclass(frozen=True)
class ConfigOption:
    """A single configuration option."""
    
    name: str
    type_: str  # e.g., "str", "int", "bool"
    required: bool
    default_value: Optional[str] = None
    description: str = ""


@dataclass(frozen=True)
class ConfigurationMetadata:
    """
    Configuration metadata for an entity.
    
    Answers: "How is this configured?"
    
    Describes the configuration surface without runtime state.
    """
    
    options: Tuple[ConfigOption, ...]
    required_options: Tuple[str, ...]  # Options that must be provided
    optional_options: Tuple[str, ...] = ()
    
    # Environment
    environment_prefix: Optional[str] = None  # e.g., "GORDON_"


# =============================================================================
# EXECUTION METADATA - How does it execute?
# =============================================================================


class ExecutionMode(Enum):
    """Execution modes for an entity."""
    
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BACKGROUND = "background"
    ON_DEMAND = "on_demand"


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Execution metadata for an entity.
    
    Answers: "How does this execute?"
    
    Describes execution characteristics without behavior.
    """
    
    mode: ExecutionMode
    concurrency_model: str  # e.g., "thread-pool", "asyncio", "worker"
    
    # Performance
    estimated_latency_ms: Optional[int] = None
    throughput_rps: Optional[int] = None
    
    # Fault tolerance
    retry_policy: Optional[str] = None
    circuit_breaker_enabled: bool = False


# =============================================================================
# DIAGNOSTIC METADATA - What diagnostics are available?
# =============================================================================


class DiagnosticType(Enum):
    """Types of diagnostics."""
    
    HEALTH = "health"  # Is it running?
    READINESS = "readiness"  # Can it accept traffic?
    LIVENESS = "liveness"  # Should it keep running?
    METRICS = "metrics"  # Performance and resource usage
    LOGGING = "logging"  # Log output configuration


@dataclass(frozen=True)
class DiagnosticMetadata:
    """
    Diagnostic metadata for an entity.
    
    Answers: "What diagnostics are available?"
    
    Describes observability without affecting behavior.
    """
    
    diagnostic_types: Tuple[DiagnosticType, ...]
    endpoint: Optional[str] = None  # HTTP endpoint or path
    metrics_enabled: bool = True
    
    # Health check details
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 5


# =============================================================================
# DOCUMENTATION METADATA - What is documented?
# =============================================================================


@dataclass(frozen=True)
class DocumentationMetadata:
    """
    Documentation metadata for an entity.
    
    Answers: "What is documented about this?"
    
    Complete documentation state without the actual content.
    """
    
    has_readme: bool = False
    has_api_docs: bool = False
    has_examples: bool = False
    
    # Doc coverage
    public_api_documented: float = 0.0  # 0.0 to 1.0
    
    # Last updated
    last_documented_at_utc: Optional[float] = None


# =============================================================================
# ENTITY METADATA - The complete package
# =============================================================================


@dataclass(frozen=True)
class EntityMetadata:
    """
    Complete metadata for an architectural entity.
    
    This is the canonical representation of any discoverable component.
    All other metadata types are subsets of this.
    
    Immutable once captured. Cannot be modified after creation.
    """
    
    # Identity (required - no defaults)
    identity: IdentityMetadata
    ownership: OwnershipMetadata
    
    # Versioning & lifecycle
    version: VersionMetadata
    lifecycle: LifecycleMetadata
    
    # Capabilities & interfaces
    capabilities: Tuple[CapabilityMetadata, ...]
    interfaces: InterfaceMetadata
    
    # Dependencies (as a tuple to avoid mutation)
    dependencies: Tuple[DependencyMetadata, ...] = ()
    
    # Security & configuration
    security: SecurityMetadata
    configuration: ConfigurationMetadata
    
    # Execution & diagnostics
    execution: ExecutionMetadata
    diagnostics: DiagnosticMetadata
    
    # Documentation state
    documentation: DocumentationMetadata
    
    # Provenance (required - no defaults)
    provenance: Provenance


# =============================================================================
# METADATA BUILDER - For controlled creation
# =============================================================================


class MetadataBuilder:
    """
    Builder for EntityMetadata with immutability guarantees.
    
    Ensures all required metadata fields are present before freezing.
    Once built, the result is frozen and immutable.
    """
    
    def __init__(self) -> None:
        self._identity: Optional[IdentityMetadata] = None
        self._ownership: Optional[OwnershipMetadata] = None
        self._version: Optional[VersionMetadata] = None
        self._lifecycle: Optional[LifecycleMetadata] = None
        self._capabilities: List[CapabilityMetadata] = []
        self._interfaces: Optional[InterfaceMetadata] = None
        self._dependencies: List[DependencyMetadata] = []
        self._security: Optional[SecurityMetadata] = None
        self._configuration: Optional[ConfigurationMetadata] = None
        self._execution: Optional[ExecutionMetadata] = None
        self._diagnostics: Optional[DiagnosticMetadata] = None
        self._documentation: Optional[DocumentationMetadata] = None
        self._provenance: Optional[Provenance] = None
    
    def set_identity(self, identity: IdentityMetadata) -> "MetadataBuilder":
        """Set the identity metadata."""
        self._identity = identity
        return self
    
    def set_ownership(self, ownership: OwnershipMetadata) -> "MetadataBuilder":
        """Set the ownership metadata."""
        self._ownership = ownership
        return self
    
    def set_version(self, version: VersionMetadata) -> "MetadataBuilder":
        """Set the version metadata."""
        self._version = version
        return self
    
    def set_lifecycle(self, lifecycle: LifecycleMetadata) -> "MetadataBuilder":
        """Set the lifecycle metadata."""
        self._lifecycle = lifecycle
        return self
    
    def add_capability(self, capability: CapabilityMetadata) -> "MetadataBuilder":
        """Add a capability to the metadata."""
        self._capabilities.append(capability)
        return self
    
    def set_interfaces(self, interfaces: InterfaceMetadata) -> "MetadataBuilder":
        """Set the interface metadata."""
        self._interfaces = interfaces
        return self
    
    def add_dependency(self, dependency: DependencyMetadata) -> "MetadataBuilder":
        """Add a dependency to the metadata."""
        self._dependencies.append(dependency)
        return self
    
    def set_security(self, security: SecurityMetadata) -> "MetadataBuilder":
        """Set the security metadata."""
        self._security = security
        return self
    
    def set_configuration(self, configuration: ConfigurationMetadata) -> "MetadataBuilder":
        """Set the configuration metadata."""
        self._configuration = configuration
        return self
    
    def set_execution(self, execution: ExecutionMetadata) -> "MetadataBuilder":
        """Set the execution metadata."""
        self._execution = execution
        return self
    
    def set_diagnostics(self, diagnostics: DiagnosticMetadata) -> "MetadataBuilder":
        """Set the diagnostic metadata."""
        self._diagnostics = diagnostics
        return self
    
    def set_documentation(self, documentation: DocumentationMetadata) -> "MetadataBuilder":
        """Set the documentation metadata."""
        self._documentation = documentation
        return self
    
    def set_provenance(self, provenance: Provenance) -> "MetadataBuilder":
        """Set the provenance metadata."""
        self._provenance = provenance
        return self
    
    def build(self) -> EntityMetadata:
        """
        Build the EntityMetadata.
        
        Validates all required fields are present before returning.
        Returns an immutable EntityMetadata instance.
        """
        if not all([
            self._identity,
            self._ownership,
            self._version,
            self._lifecycle,
            self._interfaces,
            self._security,
            self._configuration,
            self._execution,
            self._diagnostics,
            self._documentation,
            self._provenance
        ]):
            raise ValueError(
                "All required metadata fields must be set before building. "
                f"Missing: {self._missing_fields()}"
            )
        
        return EntityMetadata(
            identity=self._identity,
            ownership=self._ownership,
            version=self._version,
            lifecycle=self._lifecycle,
            capabilities=tuple(self._capabilities),
            interfaces=self._interfaces,
            dependencies=tuple(self._dependencies),
            security=self._security,
            configuration=self._configuration,
            execution=self._execution,
            diagnostics=self._diagnostics,
            documentation=self._documentation,
            provenance=self._provenance
        )
    
    def _missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        missing = []
        if not self._identity:
            missing.append("identity")
        if not self._ownership:
            missing.append("ownership")
        if not self._version:
            missing.append("version")
        if not self._lifecycle:
            missing.append("lifecycle")
        if not self._interfaces:
            missing.append("interfaces")
        if not self._security:
            missing.append("security")
        if not self._configuration:
            missing.append("configuration")
        if not self._execution:
            missing.append("execution")
        if not self._diagnostics:
            missing.append("diagnostics")
        if not self._documentation:
            missing.append("documentation")
        if not self._provenance:
            missing.append("provenance")
        return missing


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Versioning & Provenance
    "MetadataVersion",
    "Provenance",
    
    # Core metadata types
    "IdentityMetadata",
    "OwnerMetadata",
    "OwnershipMetadata",
    "VersionMetadata",
    "LifecyclePhase",
    "LifecycleMetadata",
    "CapabilityType",
    "CapabilityMetadata",
    "InterfaceContract",
    "InterfaceMetadata",
    "DependencyType",
    "DependencyMetadata",
    "SecurityClassification",
    "SecurityMetadata",
    "ConfigOption",
    "ConfigurationMetadata",
    "ExecutionMode",
    "ExecutionMetadata",
    "DiagnosticType",
    "DiagnosticMetadata",
    "DocumentationMetadata",
    
    # Complete metadata
    "EntityMetadata",
    "MetadataBuilder",
]