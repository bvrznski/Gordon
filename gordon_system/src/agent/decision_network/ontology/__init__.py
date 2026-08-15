# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Ontology Subsystem - Canonical Semantic Classification

This module defines the canonical Action ontology that classifies all possible
Actions in the Gordon cognitive agent system.

ONTOLOGY OVERVIEW
=================

The Action Ontology is a complete semantic classification system describing:

1. ACTION CATEGORIES
   The highest-level taxonomic grouping of Actions:
   
   - Observational: Read-only observation and inspection
   - Informational: Gather information without storage
   - Computational: Perform computation or reasoning
   - Transformational: Modify existing state while preserving identity
   - Communicative: Exchange information with other systems
   - Delegative: Delegate work to other components
   - Resource: Manage system resources
   - Memory: Manage working and long-term memory
   - Workspace: Manage workspace artifacts
   - Planning Support: Enable planning capabilities
   - Executive Support: Enable executive functions
   - Monitoring Support: Enable monitoring capabilities
   - Recovery Support: Enable recovery from failures
   - Security: Handle security-sensitive operations
   - Policy: Define policy-related behavior
   - Configuration: Manage system configuration
   - External Interaction: Interact with external systems
   - Physical: Interact with physical world (if applicable)
   - Composite: Composed of multiple Actions

2. ACTION FAMILIES
   Representative semantic families:
   
   - Read, Inspect, Search, Observe, Compare, Validate
   - Create, Modify, Delete, Replace, Transform, Move, Copy
   - Communicate, Notify, Request, Delegate
   - Acquire, Reserve, Release
   - Persist, Load, Store, Retrieve, Archive
   - Start, Pause, Resume, Stop
   - Recover, Rollback, Compensate
   - Monitor, Audit, Verify
   - Authorize, Escalate, De-escalate
   - Configure

3. ACTION RELATIONSHIPS
   Semantic relationships between Actions:
   
   - is-a: Hierarchical classification
   - specializes: More specific classification
   - generalizes: More general classification
   - composes: Composite Action structure
   - depends-on: Dependencies for execution
   - enables: Enables another Action
   - disables: Disables another Action
   - conflicts-with: Conflicting effects
   - requires: Required preconditions
   - invalidates: Invalidates previous state
   - replaces: Replaces another Action
   - supersedes: Supersedes with stronger authority
   - compensates: Compensates for effects
   - rolls-back: Reverses effects

4. ACTION CAPABILITIES
   The domains where Actions may operate:
   
   - Filesystem, Workspace, Memory, Communication
   - Network, Computation, Planning, Reasoning
   - Vision, Language, Security, Configuration
   - External Service, User Interaction

5. TARGET ONTOLOGY
   What Actions may operate on:
   
   - File, Directory, Repository, Workspace
   - Memory Object, Conversation, Message, User
   - Agent, Capability, Model, Service
   - Configuration, Device, Network Resource
   - Knowledge Object, Abstract Concept

6. EFFECT ONTOLOGY
   Semantic effects of Actions:
   
   - No Change: Observation only
   - Information Acquired: Data retrieved
   - State Observed: Current state seen
   - State Created: New entity created
   - State Updated: Existing modified
   - State Removed: Entity deleted
   - Resource Reserved/Released
   - Message Delivered
   - Configuration Updated
   - Knowledge Expanded
   - Recovery/Rollback/Compensation Requested

ARCHITECTURAL LAWS
==================

ACTION-ONTO-LAW-001: Every Action belongs to the ontology.
ACTION-ONTO-LAW-002: Ontology defines semantics, not implementation.
ACTION-ONTO-LAW-003: Ontology remains acyclic.
ACTION-ONTO-LAW-004: Relationships are explicit.
ACTION-ONTO-LAW-005: Capabilities remain external.
ACTION-ONTO-LAW-006: Ontology is extensible without breaking compatibility.
ACTION-ONTO-LAW-007: Execution concepts are excluded.
ACTION-ONTO-LAW-008: Tool implementations are excluded.
ACTION-ONTO-LAW-009: Ontology is deterministic.
ACTION-ONTO-LAW-010: Ontology is runtime-neutral.

IMPORT SAFETY
=============

This package is designed to be import-safe:
    - No filesystem access during import
    - No network access during import
    - No model loading during import
    - No runtime initialization during import
    - No random identity generation during import
    - No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

__version__ = "1.0.0"

# =============================================================================
# EXPORTS - Ontology Components
# =============================================================================

from .categories import (
    ActionCategory,
    ActionCategories,
)

from .purposes import (
    ActionPurpose,
    ActionPurposes,
)

from .kinds import (
    ActionKind,
    ActionKinds,
)

from .capabilities import (
    ActionCapability,
    ActionCapabilities,
)

from .targets import (
    ActionTargetKind,
    ActionTargetKinds,
)

from .subjects import (
    ActionSubjectKind,
    ActionSubjectKinds,
)

from .effects import (
    ActionEffectKind,
    ActionEffectKinds,
)

from .relationships import (
    ActionRelationship,
    ActionRelationships,
)

from .composition import (
    ActionCompositionType,
    ActionCompositeReference,
    ActionAtomicity,
    ActionGranularity,
)

from .modality import (
    ActionModality,
    ActionModalities,
)

from .validation import (
    OntologyValidationError,
    OntologyValidationResult,
    validate_ontology_consistency,
)

# =============================================================================
# ONTOLOGY ROOT
# =============================================================================

__all__ = [
    # Core categories
    "ActionCategory",
    "ActionCategories",
    
    # Families
    # Purposes
    "ActionPurpose",
    "ActionPurposes",
    
    # Kinds
    "ActionKind",
    "ActionKinds",
    
    # Capabilities
    "ActionCapability",
    "ActionCapabilities",
    
    # Targets
    "ActionTargetKind",
    "ActionTargetKinds",
    
    # Subjects
    "ActionSubjectKind",
    "ActionSubjectKinds",
    
    # Effects
    "ActionEffectKind",
    "ActionEffectKinds",
    
    # Relationships
    "ActionRelationship",
    "ActionRelationships",
    
    # Composition
    "ActionCompositionType",
    "ActionCompositeReference",
    "ActionAtomicity",
    "ActionGranularity",
    
    # Modality
    "ActionModality",
    "ActionModalities",
    
    # Validation
    "OntologyValidationError",
    "OntologyValidationResult",
    "validate_ontology_consistency",
]