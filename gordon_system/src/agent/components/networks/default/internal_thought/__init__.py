# Internal Thought Package
# =======================

"""
Canonical InternalThought model for Gordon's Default Network.

This module provides immutable, bounded, revisioned representations of internally
generated semantic thought units.

ARCHITECTURAL PRINCIPLES:
    - InternalThought is a semantic object, not an execution mechanism
    - InternalThought is immutable (deeply frozen)
    - InternalThought is bounded (no unbounded growth)
    - Every thought preserves its context binding and revision
    - Thought lifecycle remains distinct from runtime execution
    - InternalThought does not own cognitive algorithms or capability implementations

PUBLIC API:
    Core Model:
        - InternalThought: Main aggregate (immutable canonical model)
        - InternalThoughtId: Stable identifier for thought instances
        
    Request and Configuration:
        - InternalThoughtRequest: Description of what thought to generate
        - InternalThoughtConfig: Immutable configuration for thought handling
        
    Type, Kind, Purpose:
        - InternalThoughtKind: Canonical category of internal cognition
        - InternalThoughtPurpose: Concrete reason for this thought instance
        - InternalThoughtScope: Bounded constraints on the thought
        
    Lifecycle and State:
        - InternalThoughtLifecycle: Semantic coordination state
        - InternalThoughtState: Complete state snapshot
        - InternalThoughtTransition: Immutable record of state change
        
    Assessment Model:
        - InternalThoughtAssessment: Quality evaluation of a thought
        - InternalThoughtMetrics: Quantitative measurements
        
    Relationships:
        - InternalThoughtRelationship: Graph relationships between thoughts
        - RelationshipKind: Typed relationship categories
        
    Revision and History:
        - InternalThoughtRevision: Immutable revision record
        - InternalThoughtHistory: Bounded history chain
        
    Serialization:
        - InternalThoughtSnapshot: Serialization-ready immutable snapshot
        - InternalThoughtSerializer: Serialization utility
        
ARCHITECTURAL INVARIANTS:
    THOUGHT-INV-001 through THOUGHT-INV-025 (see module docs)

PHASE: 4.3.4
"""

from __future__ import annotations

# Module version and authorship
from .__meta__ import (
    __version__,
    __author__,
    __description__,
)

# Import core model
from .thought import (
    InternalThought,
    InternalThoughtId,
    InternalThoughtRevision,
)

# Import kind/type enums
from .enums import (
    InternalThoughtKind,
    InternalThoughtPurpose,
    InternalThoughtScope,
    RelationshipKind,
    LifecycleState,
)

# Import request and configuration
from .request import (
    InternalThoughtRequest,
    InternalThoughtRequestId,
)
from .configuration import (
    InternalThoughtConfig,
)

# Import lifecycle model
from .lifecycle import (
    InternalThoughtLifecycle,
    LifecycleTransitionId,
)

# Import state model
from .state.snapshot import (
    InternalThoughtStateSnapshot,
)
from .state.transition import (
    InternalThoughtStateTransition,
)
from .state.history import (
    InternalThoughtHistory,
)

# Import assessment model
from .assessment.assessment import (
    InternalThoughtAssessment,
    AssessmentKind,
)
from .assessment.metrics import (
    InternalThoughtMetrics,
    MetricValue,
)

# Import relationships
from .relationships.relationships import (
    InternalThoughtRelationship,
    RelationshipGraph,
)
from .relationships.kind import (
    RelationshipKind as RKind,
)

# Import revision model
from .revision.revision import (
    InternalThoughtRevision,
    RevisionRecord,
)

# Import serialization
from .serialization.serializer import (
    InternalThoughtSerializer,
    SerializationResult,
)
from .serialization.validator import (
    InternalThoughtValidator,
    ValidationReport,
)

# Import registry
from .registry.registry import (
    ThoughtRegistry,
    RegistryEntry,
)
from .registry.history import (
    ThoughtHistory,
    HistoryRecord,
)

# Import factory and generator
from .factory import (
    ThoughtFactory,
    create_factory,
)
from .generator import (
    ThoughtGenerator,
    create_generator,
)

# Validation exports
from .validation.validation import (
    validate_thought,
    validate_relationships,
    validate_revision,
    validate_context_references,
)

# Expose all public API items
__all__ = [
    # Version and authorship
    "__version__",
    "__author__",
    "__description__",
    
    # Core model
    "InternalThought",
    "InternalThoughtId",
    "InternalThoughtRevision",
    
    # Kind, purpose, scope
    "InternalThoughtKind",
    "InternalThoughtPurpose",
    "InternalThoughtScope",
    
    # Request and configuration
    "InternalThoughtRequest",
    "InternalThoughtRequestId",
    "InternalThoughtConfig",
    
    # Lifecycle
    "InternalThoughtLifecycle",
    "LifecycleTransitionId",
    "LifecycleState",
    
    # State
    "InternalThoughtStateSnapshot",
    "InternalThoughtStateTransition",
    "InternalThoughtHistory",
    
    # Assessment
    "InternalThoughtAssessment",
    "AssessmentKind",
    "InternalThoughtMetrics",
    "MetricValue",
    
    # Relationships
    "InternalThoughtRelationship",
    "RelationshipGraph",
    "RelationshipKind",
    "RKind",
    
    # Revision
    "InternalThoughtRevision",
    "RevisionRecord",
    
    # Serialization
    "InternalThoughtSerializer",
    "SerializationResult",
    "InternalThoughtValidator",
    "ValidationReport",
    
    # Registry and history
    "ThoughtRegistry",
    "RegistryEntry",
    "ThoughtHistory",
    "HistoryRecord",
    
    # Factory and generator
    "ThoughtFactory",
    "create_factory",
    "ThoughtGenerator",
    "create_generator",
    
    # Validation
    "validate_thought",
    "validate_relationships",
    "validate_revision",
    "validate_context_references",
]