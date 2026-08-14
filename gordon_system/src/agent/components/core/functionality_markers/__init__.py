# Core Functionality Markers - Phase 3.13.1
# ============================================

"""
Canonical Functionality Marker Hierarchy for Gordon Core Architecture.

This module provides lightweight marker classes that explicitly declare which
architectural layer a Core component exists to support.

MARKER PHILOSOPHY:
------------------
Markers express architectural intent. They do NOT provide behavior. They do not
contain state. They do not introduce runtime overhead.

A developer shall immediately understand why a Core component exists simply by
looking at its inheritance.

Example:
    class ExecutionScheduler(CoreService, ForExecution):
        ...
    
This immediately communicates: "This Core component primarily exists to support
the Execution layer."

MARKER SEMANTICS:
-----------------
Markers indicate the intended consumer. They do NOT indicate:
    - ownership
    - lifecycle  
    - package
    - implementation
    - dependency
    - execution order

Those concepts remain defined elsewhere.

MARKER CHARACTERISTICS:
-----------------------
Markers shall be:
    - immutable
    - stateless
    - empty
    - deterministic
    - lightweight
    - documentation-friendly
    - reflection-friendly

No runtime logic. No mutable data. No side effects.

MARKER HIERARCHY:
-----------------
CoreFunctionality (base)
├── ForCore          - Core infrastructure services
├── ForExecution     - Execution layer (task scheduling, concurrency)
├── ForEntrypoint    - Entry point initialization and bootstrap
├── ForArchitecture  - Architectural reflection and analysis
├── ForNetworks      - Network/transport layer services
├── ForCapabilities  - Agent capability implementations  
└── ForSystems       - System-level subsystems (memory, perception)
"""

from abc import ABC
from typing import Optional, List

# Import new Phase 3.13.4 modules
from .metaclass import (
    CoreFunctionalityMetadata,
    ClassificationStatus,
    ClassificationSource,
    StrictnessMode,
    Finding,
    ClassificationFindings,
    ExemptionKind,
    FunctionalityExemption,
    SecondaryRole,
    IntegrationBoundary,
    FunctionalityMetaclass,
    FunctionalityAwareMetaclass,
    integrate_with_existing_metaclass,
)

from .registry import (
    RegistryState,
    RegistryEntry,
    RejectedRegistration,
    RegistrySnapshot,
    RegistryStatistics,
    FunctionalityRegistry,
    RegistrySealedError,
    DuplicateRegistrationError,
    get_functionality_metadata,
    get_primary_functionality,
    list_by_functionality,
    snapshot_functionality_registry,
)

from .diagnostics import (
    DiagnosticsSnapshot,
    ClassificationEvent,
    ObservabilityHook,
    DiagnosticsObserver,
    FunctionalityDiagnostics,
)

from .inventory import (
    InventoryGroup,
    FunctionalityInventory,
    create_functionality_inventory,
)

# Phase 3.13.6 - Classification Policy
from .classification_policy import (
    ClassificationEvidence,
    ClassificationDecision,
    ClassificationRecord,
    ClassificationFramework,
    CANONICAL_RESPONSIBILITIES,
    primary_recipient_test,
    disappearance_test,
    create_classification_record,
)

# =============================================================================
# PRIMARY MARKER - Base of the hierarchy
# =============================================================================


class CoreFunctionality(ABC):
    """
    Base class for all functionality markers.
    
    All marker classes inherit from this base. It is an abstract base class
    that provides no behavior but establishes the inheritance relationship.
    """
    
    __slots__ = ()


# =============================================================================
# CANONICAL MARKERS - One per major architectural layer
# =============================================================================


class ForCore(CoreFunctionality):
    """
    Marker for components serving the Core infrastructure layer.
    
    Components marked with ForCore provide foundational runtime substrate:
        - Lifecycle management
        - Registry and dependency resolution  
        - Configuration handling
        - Context and state management
        - Synchronization primitives
        
    Examples:
        Scheduler (core infrastructure)
        Registry (component registry)
        StateStore (state persistence)
        SyncPrimitives (locks, semaphores)
    """
    
    __slots__ = ()


class ForExecution(CoreFunctionality):
    """
    Marker for components serving the Execution layer.
    
    Components marked with ForExecution manage task execution:
        - Task scheduling and prioritization
        - Concurrent execution coordination
        - Cancellation propagation
        - Timeout management
        - Dependency tracking
        
    Examples:
        ExecutionScheduler
        ThreadManager  
        TaskDispatcher
        CancellationCoordinator
    """
    
    __slots__ = ()


class ForEntrypoint(CoreFunctionality):
    """
    Marker for components serving as entry points.
    
    Components marked with ForEntrypoint bootstrap the system:
        - Application initialization
        - Configuration loading
        - Dependency injection setup
        - Lifecycle startup sequences
        - Shutdown coordination
        
    Examples:
        ApplicationMain (main entry point)
        BootstrapLoader
        ConfigInitializer
        ShutdownHandler
    """
    
    __slots__ = ()


class ForArchitecture(CoreFunctionality):
    """
    Marker for components serving architectural reflection.
    
    Components marked with ForArchitecture enable understanding of the system:
        - Dependency analysis
        - Ownership tracking
        - Topology mapping
        - Static validation
        - Architecture documentation
        
    Examples:
        DependencyInspector
        ReflectionRegistry
        ArchitectureValidator
        GraphBuilder
    """
    
    __slots__ = ()


class ForNetworks(CoreFunctionality):
    """
    Marker for components serving the network/transport layer.
    
    Components marked with ForNetworks handle data transport:
        - Stream publication and subscription
        - Message delivery protocols
        - Network topology management
        - Data serialization/deserialization
        
    Examples:
        StreamRegistry (network layer)
        TransportLayer  
        MessageRouter
        SubscriptionManager
    """
    
    __slots__ = ()


class ForCapabilities(CoreFunctionality):
    """
    Marker for components serving capability implementations.
    
    Components marked with ForCapabilities implement agent capabilities:
        - Cognition and reasoning
        - Learning and adaptation
        - Memory operations
        - Motivation and goals
        
    Examples:
        CognitiveEngine
        LearningModule
        MemoryManager
        GoalPlanner
    """
    
    __slots__ = ()


class ForSystems(CoreFunctionality):
    """
    Marker for components serving system-level subsystems.
    
    Components marked with ForSystems provide specialized system functions:
        - Perception processing (vision, audition)
        - Consciousness and awareness
        - Memory storage and retrieval
        - Sensory integration
        
    Examples:
        VisionSystem
        MemorySystem  
        ConsciousnessStream
        PerceptProcessor
    """
    
    __slots__ = ()


def get_functionality_marker(cls: type) -> Optional[type]:
    """
    Get the primary functionality marker for a class.
    
    Args:
        cls: The class to inspect
        
    Returns:
        The marker class if found, None otherwise
    """
    for base in cls.__mro__:
        if (
            base != CoreFunctionality 
            and issubclass(base, CoreFunctionality)
        ):
            return base
    return None


def has_functionality_marker(cls: type) -> bool:
    """
    Check if a class has a functionality marker.
    
    Args:
        cls: The class to check
        
    Returns:
        True if the class inherits from any marker, False otherwise
    """
    return get_functionality_marker(cls) is not None


def get_all_markers() -> List[type]:
    """Get all available marker classes."""
    return [
        ForCore,
        ForExecution,
        ForEntrypoint,
        ForArchitecture,
        ForNetworks,
        ForCapabilities,
        ForSystems,
    ]


from .reflection import (
    FunctionalityIdentity,
    get_functionality_identity,
    UniquenessValidator,
    InheritanceValidator,
    ArchitecturalInterpreter,
)


# Phase 3.13.6 - Classification Policy exports
from .classification_policy import __all__ as classification_policy_all

__all__ = [
    # Base class
    "CoreFunctionality",
    
    # Canonical markers (one per architectural layer)
    "ForCore",
    "ForExecution", 
    "ForEntrypoint",
    "ForArchitecture",
    "ForNetworks",
    "ForCapabilities",
    "ForSystems",
    
    # Reflection helpers (Phase 3.13.1 & 3.13.2 additions)
    "get_functionality_marker",
    "has_functionality_marker",
    "get_all_markers",
    "FunctionalityIdentity",
    "get_functionality_identity",
    "UniquenessValidator",
    "InheritanceValidator", 
    "ArchitecturalInterpreter",
    
    # Phase 3.13.4 - Metaclass & Registry
    "CoreFunctionalityMetadata",
    "ClassificationStatus",
    "ClassificationSource",
    "StrictnessMode",
    "Finding",
    "ClassificationFindings",
    "ExemptionKind",
    "FunctionalityExemption",
    "SecondaryRole",
    "IntegrationBoundary",
    "FunctionalityMetaclass",
    "FunctionalityAwareMetaclass",
    "integrate_with_existing_metaclass",
    "RegistryState",
    "RegistryEntry",
    "RejectedRegistration",
    "RegistrySnapshot",
    "RegistryStatistics",
    "FunctionalityRegistry",
    "RegistrySealedError",
    "DuplicateRegistrationError",
    "get_functionality_metadata",
    "get_primary_functionality",
    "list_by_functionality",
    "snapshot_functionality_registry",
    
    # Diagnostics
    "DiagnosticsSnapshot",
    "ClassificationEvent",
    "ObservabilityHook",
    "DiagnosticsObserver",
    "FunctionalityDiagnostics",
    
    # Inventory
    "InventoryGroup",
    "FunctionalityInventory",
    "create_functionality_inventory",
    
    # Phase 3.13.6 - Classification Policy
] + classification_policy_all
