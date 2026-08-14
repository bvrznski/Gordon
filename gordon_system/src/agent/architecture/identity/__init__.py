# Core Identity Architecture - Phase 3.19
# ========================================

"""
Canonical Identity, Provenance, and Lineage Architecture for Gordon Core.

This module provides:

    * Canonical identity types for all architectural entities
    * Strongly typed identifiers with domain separation
    * Immutable, unique identities throughout the system
    * Correlation and causation tracking for traceability
    * Provenance and lineage tracking for artifacts

IDENTITY ARCHITECTURE:

    Core Identity (gordon_system/src/agent/architecture/identity/)
        ├── core.py               - Base identity types
        ├── domains/
        │   ├── runtime.py        - Runtime, Process, Boot-Session Identities
        │   └── component.py      - Component, Service, Capability Identities
        ├── correlation.py        - Correlation & Causation identities
        ├── provenance.py         - Provenance tracking
        ├── lineage.py            - Data & Artifact lineage
        ├── serialization.py      - Serialization & compatibility
        └── validation.py         - Integrity & collision handling

IDENTITY DOMAINS:

    Runtime Identity          - Application runtime sessions
    Process Identity          - Operating system processes  
    Boot Session Identity     - System boot instances
    Component Identity        - Software components/modules
    Service Identity          - Exposed service interfaces
    Capability Identity       - Concrete capability implementations
    Module Identity           - Python modules
    Package Identity          - Python packages
    
    Request/Response Identities - Client-server interactions
    Event/Stream Identities   - Streaming operations
    Task/Action Identities    - Execution units
    Transaction Identities    - Atomic operations

CORRELATION & CAUSATION:

    CorrelationId             - Group related operations
    CausationId               - Track creation relationships
    ExecutionChainId          - Full execution sequences
    DependencyChainId         - Dependency resolution chains
    TraceId                   - Distributed tracing identifiers
    SpanId                    - Individual trace spans

PROVENANCE & LINEAGE:

    ProvenanceRecord          - Complete provenance trail
    Origin                    - Source origin information
    Creator                   - Creation entity information
    LineageId                 - Complete lineage traces
    DerivationId              - Derivation relationships
    TransformationId          - Transformation operations

SERIALIZATION & VALIDATION:

    IdentitySerializer        - Serialization engine
    CompatibilityMode         - Version compatibility modes
    CollisionDetector         - Duplicate detection
    ReplayDetector            - Stale identifier detection
    ForgeryDetector           - Identity forgery detection

USAGE:

    from gordon_system.src.agent.architecture.identity import (
        RuntimeId,
        ComponentId,
        ServiceId,
        CorrelationId,
        ProvenanceRecord,
        CollisionDetector,
    )
    
    # Create strongly-typed identities
    runtime = RuntimeId.generate()
    component = ComponentId(name="state_manager")
    
    # Track correlations
    corr = CorrelationId.generate()
    corr.register_operation("op_12345")
    
    # Validate identities
    detector = CollisionDetector(domain="runtime")
    valid, error = detector.validate(runtime.value)

IDENTITY PRINCIPLES:

    * Identity is immutable - never changes after creation
    * Identity is unique - no duplicates within domain  
    * Identity is strongly typed - domains are separated
    * Identity enables traceability - correlations and causation
    * Identity preserves provenance - origin tracking
"""

from __future__ import annotations

# Core types
from gordon_system.src.agent.architecture.identity.core import (
    Identity,
    Domain,
    Namespace,
)

# Runtime identities  
from gordon_system.src.agent.architecture.identity.domains.runtime import (
    RuntimeId,
    ProcessId,
    BootSessionId,
    ApplicationId,
)

# Component/service identities
from gordon_system.src.agent.architecture.identity.domains.component import (
    ComponentId,
    ServiceId,
    CapabilityId,
    ModuleId,
    PackageId,
    ComponentIdentityRegistry,
)

# Correlation & causation
from gordon_system.src.agent.architecture.identity.correlation import (
    CorrelationId,
    CausationId,
    ExecutionChainId,
    DependencyChainId,
    TraceId,
    SpanId,
    CorrelationRegistry,
)

# Provenance & lineage
from gordon_system.src.agent.architecture.identity.provenance import (
    ProvenanceRecord,
    Origin,
    Creator,
    SourceReference,
    TransformationStep,
    ProvenanceVerifier,
)

from gordon_system.src.agent.architecture.identity.lineage import (
    LineageId,
    DerivationId,
    TransformationId,
    VersionLineageId,
    RevisionLineageId,
    LineageRegistry,
)

# Serialization & compatibility
from gordon_system.src.agent.architecture.identity.serialization import (
    SerializationFormat,
    IdentitySerializer,
    IdentityDeserializer,
    CompatibilityMode,
    IdentityCompatibilityChecker,
    SchemaEvolutionValidator,
    IdentitySerializationRegistry,
)

# Validation & integrity
from gordon_system.src.agent.architecture.identity.validation import (
    CollisionDetector,
    ReplayDetector,
    ForgeryDetector,
    IdentityIntegrityVerifier,
    IdentityIntegrityRegistry,
)

__all__ = [
    # Core
    "Identity",
    "Domain", 
    "Namespace",
    # Runtime domains
    "RuntimeId",
    "ProcessId",
    "BootSessionId",
    "ApplicationId",
    # Component/service domains  
    "ComponentId",
    "ServiceId",
    "CapabilityId",
    "ModuleId",
    "PackageId",
    "ComponentIdentityRegistry",
    # Correlation & causation
    "CorrelationId",
    "CausationId",
    "ExecutionChainId",
    "DependencyChainId",
    "TraceId",
    "SpanId",
    "CorrelationRegistry",
    # Provenance & lineage
    "ProvenanceRecord",
    "Origin",
    "Creator",
    "SourceReference", 
    "TransformationStep",
    "ProvenanceVerifier",
    "LineageId",
    "DerivationId",
    "TransformationId",
    "VersionLineageId",
    "RevisionLineageId",
    "LineageRegistry",
    # Serialization & compatibility
    "SerializationFormat",
    "IdentitySerializer",
    "IdentityDeserializer",
    "CompatibilityMode",
    "IdentityCompatibilityChecker",
    "SchemaEvolutionValidator",
    "IdentitySerializationRegistry",
    # Validation & integrity
    "CollisionDetector",
    "ReplayDetector",
    "ForgeryDetector",
    "IdentityIntegrityVerifier",
    "IdentityIntegrityRegistry",
]

__version__ = "3.19.0"

