# Canonical World Synchronization Enums - Phase 4.9.6
# =====================================================
"""
Immutable enum definitions for WorldModelSynchronization subsystem.
No runtime dependencies; pure semantic definitions.
"""
from __future__ import annotations

from enum import Enum, auto


# =============================================================================
# ENTITY LIFECYCLE OPERATIONS (IMMUTABLE)
# =============================================================================

class EntityLifecycleOperation(Enum):
    """
    Immutable entity lifecycle operation types.
    
    Rules:
        - CREATE: Introduce new entity not present in world
        - UPDATE: Modify attributes of existing entity
        - MERGE: Combine two entities into one
        - SPLIT: Divide entity into multiple entities
        - DEPRECATE: Mark as outdated but retain for reference
        - REMOVE: Delete entity (only if unused)
        - ARCHIVE: Move to historical archive
        - RESTORE: Restore from archive
        - UNKNOWN: Error state or undefined
    """
    CREATE = auto()
    UPDATE = auto()
    MERGE = auto()
    SPLIT = auto()
    DEPRECATE = auto()
    REMOVE = auto()
    ARCHIVE = auto()
    RESTORE = auto()
    UNKNOWN = auto()


# Alias exports for backward compatibility
CREATE = EntityLifecycleOperation.CREATE
UPDATE = EntityLifecycleOperation.UPDATE
MERGE = EntityLifecycleOperation.MERGE
SPLIT = EntityLifecycleOperation.SPLIT
DEPRECATE = EntityLifecycleOperation.DEPRECATE
REMOVE = EntityLifecycleOperation.REMOVE
ARCHIVE = EntityLifecycleOperation.ARCHIVE
RESTORE = EntityLifecycleOperation.RESTORE
UNKNOWN = EntityLifecycleOperation.UNKNOWN


# =============================================================================
# RELATIONSHIP TYPES (IMMUTABLE)
# =============================================================================

class RelationshipType(Enum):
    """
    Immutable relationship type identifiers.
    
    Rules:
        - All relationships are typed and semantic
        - Endpoints reference valid entities
        - No inheritance of relationship semantics
    """
    # Spatial/Containment
    CONTAINS = auto()       # A contains B (e.g., container, namespace)
    LOCATED_IN = auto()     # A located in B (e.g., physical location)
    ADJACENT_TO = auto()    # A adjacent to B (e.g., spatial proximity)
    
    # Ownership
    OWNS = auto()           # A owns B (e.g., property, resources)
    
    # Dependency
    DEPENDS_ON = auto()     # A depends on B (e.g., causal dependency)
    CONNECTED_TO = auto()   # A connected to B (e.g., network, logical)
    
    # Causality
    CAUSES = auto()         # A causes B (e.g., event causation)
    AFFECTS = auto()        # A affects B (e.g., influence)
    INFLUENCES = auto()     # A influences B (e.g., modulatory)
    
    # Taxonomic
    IS_A = auto()           # A is a kind of B (e.g., class-subclass)
    PART_OF = auto()        # A is part of B (e.g., mereology)
    
    # Semantic
    ENABLES = auto()        # A enables B (e.g., capability)
    PREVENTS = auto()       # A prevents B (e.g., constraint)


# Alias exports
CONTAINS = RelationshipType.CONTAINS
LOCATED_IN = RelationshipType.LOCATED_IN
ADJACENT_TO = RelationshipType.ADJACENT_TO
OWNS = RelationshipType.OWNS
DEPENDS_ON = RelationshipType.DEPENDS_ON
CONNECTED_TO = RelationshipType.CONNECTED_TO
CAUSES = RelationshipType.CAUSES
AFFECTS = RelationshipType.AFFECTS
INFLUENCES = RelationshipType.INFLUENCES
IS_A = RelationshipType.IS_A
PART_OF = RelationshipType.PART_OF
ENABLES = RelationshipType.ENABLES
PREVENTS = RelationshipType.PREVENTS


# =============================================================================
# ONTOLOGY OPERATIONS (IMMUTABLE)
# =============================================================================

class OntologyOperation(Enum):
    """
    Immutable ontology evolution operation types.
    
    Rules:
        - Concept identities remain stable
        - Evolution is explicit and versioned
        - No inference-based changes
    """
    CONCEPT_CREATE = auto()         # Introduce new concept
    CONCEPT_MERGE = auto()          # Merge two concepts
    CONCEPT_SPECIALIZE = auto()     # Add specialization
    CONCEPT_GENERALIZE = auto()     # Generalize concept boundaries
    CONCEPT_RENAME = auto()         # Rename concept (identity preserved)
    CONCEPT_DEPRECATED = auto()     # Mark as deprecated


# Alias exports
CONCEPT_CREATE = OntologyOperation.CONCEPT_CREATE
CONCEPT_MERGE = OntologyOperation.CONCEPT_MERGE
CONCEPT_SPECIALIZE = OntologyOperation.CONCEPT_SPECIALIZE
CONCEPT_GENERALIZE = OntologyOperation.CONCEPT_GENERALIZE
CONCEPT_RENAME = OntologyOperation.CONCEPT_RENAME
CONCEPT_DEPRECATED = OntologyOperation.CONCEPT_DEPRECATED


# =============================================================================
# TRANSACTION STATUS (IMMUTABLE)
# =============================================================================

class TransactionStatus(Enum):
    """
    Immutable transaction lifecycle states.
    
    Rules:
        - PENDING: Request received, validation in progress
        - VALIDATED: All inputs validated successfully
        - APPLIED: Changes applied to graph
        - COMMITTED: Changes made permanent
        - ROLLED_BACK: Changes reverted to previous state
        - FAILED: Transaction encountered unrecoverable error
    """
    PENDING = auto()
    VALIDATED = auto()
    APPLIED = auto()
    COMMITTED = auto()
    ROLLED_BACK = auto()
    FAILED = auto()


# Alias exports
PENDING = TransactionStatus.PENDING
VALIDATED = TransactionStatus.VALIDATED
APPLIED = TransactionStatus.APPLIED
COMMITTED = TransactionStatus.COMMITTED
ROLLED_BACK = TransactionStatus.ROLLED_BACK
FAILED = TransactionStatus.FAILED


# =============================================================================
# FAILURE KINDS (IMMUTABLE)
# =============================================================================

class FailureKind(Enum):
    """
    Immutable failure category identifiers.
    
    Rules:
        - INVALID_ENTITY: Entity schema or identity violation
        - INVALID_RELATIONSHIP: Relationship integrity violation
        - INVALID_SCHEMA: Schema compatibility error
        - ONTOLOGY_CONFLICT: Ontology evolution conflict
        - GRAPH_CYCLE: Circular dependency in graph
        - FAILED_TRANSACTION: Transaction execution failure
        - ROLLBACK_COMPLETED: Rollback succeeded
        - UNKNOWN_FAILURE: Unrecognized error
    """
    INVALID_ENTITY = auto()
    INVALID_RELATIONSHIP = auto()
    INVALID_SCHEMA = auto()
    ONTOLOGY_CONFLICT = auto()
    GRAPH_CYCLE = auto()
    FAILED_TRANSACTION = auto()
    ROLLBACK_COMPLETED = auto()
    UNKNOWN_FAILURE = auto()


# Alias exports
INVALID_ENTITY = FailureKind.INVALID_ENTITY
INVALID_RELATIONSHIP = FailureKind.INVALID_RELATIONSHIP
INVALID_SCHEMA = FailureKind.INVALID_SCHEMA
ONTOLOGY_CONFLICT = FailureKind.ONTOLOGY_CONFLICT
GRAPH_CYCLE = FailureKind.GRAPH_CYCLE
FAILED_TRANSACTION = FailureKind.FAILED_TRANSACTION
ROLLBACK_COMPLETED = FailureKind.ROLLBACK_COMPLETED
UNKNOWN_FAILURE = FailureKind.UNKNOWN_FAILURE


# =============================================================================
# TRACE EVENTS (IMMUTABLE)
# =============================================================================

class TraceEvent(Enum):
    """
    Immutable trace event identifiers for audit logging.
    
    Rules:
        - Events are ordered chronologically
        - Each event has deterministic payload
        - No side-effect events
    """
    REQUEST_VALIDATED = auto()
    BELIEF_STATE_VALIDATED = auto()
    WORLD_MODEL_VALIDATED = auto()
    TRANSACTION_STARTED = auto()
    ENTITY_SYNCHRONIZED = auto()
    ATTRIBUTE_SYNCHRONIZED = auto()
    RELATIONSHIP_SYNCHRONIZED = auto()
    ONTOLOGY_SYNCHRONIZED = auto()
    GRAPH_VALIDATED = auto()
    TRANSACTION_COMMITTED = auto()
    SNAPSHOT_CREATED = auto()
    VALIDATION_COMPLETED = auto()


# Alias exports
REQUEST_VALIDATED = TraceEvent.REQUEST_VALIDATED
BELIEF_STATE_VALIDATED = TraceEvent.BELIEF_STATE_VALIDATED
WORLD_MODEL_VALIDATED = TraceEvent.WORLD_MODEL_VALIDATED
TRANSACTION_STARTED = TraceEvent.TRANSACTION_STARTED
ENTITY_SYNCHRONIZED = TraceEvent.ENTITY_SYNCHRONIZED
ATTRIBUTE_SYNCHRONIZED = TraceEvent.ATTRIBUTE_SYNCHRONIZED
RELATIONSHIP_SYNCHRONIZED = TraceEvent.RELATIONSHIP_SYNCHRONIZED
ONTOLOGY_SYNCHRONIZED = TraceEvent.ONTOLOGY_SYNCHRONIZED
GRAPH_VALIDATED = TraceEvent.GRAPH_VALIDATED
TRANSACTION_COMMITTED = TraceEvent.TRANSACTION_COMMITTED
SNAPSHOT_CREATED = TraceEvent.SNAPSHOT_CREATED
VALIDATION_COMPLETED = TraceEvent.VALIDATION_COMPLETED


# =============================================================================
# CONTEXT TYPES (IMMUTABLE)
# =============================================================================

class ContextType(Enum):
    """
    Immutable context partition identifiers.
    
    Rules:
        - Contexts remain independent
        - No cross-context inference
        - Explicit context boundaries
    """
    TASK = auto()           # Current task context
    CONVERSATION = auto()   # Conversation history context
    ENVIRONMENT = auto()    # Physical/environmental context
    SOCIAL = auto()         # Social/relational context
    INTERNAL = auto()       # Internal mental state context


# Alias exports
CONTEXT_TASK = ContextType.TASK
CONTEXT_CONVERSATION = ContextType.CONVERSATION
CONTEXT_ENVIRONMENT = ContextType.ENVIRONMENT
CONTEXT_SOCIAL = ContextType.SOCIAL
CONTEXT_INTERNAL = ContextType.INTERNAL


# =============================================================================
# VALIDATION STATUS (IMMUTABLE)
# =============================================================================

class ValidationStatus(Enum):
    """
    Immutable validation outcome identifiers.
    
    Rules:
        - PASSED: All checks succeeded
        - FAILED: One or more checks failed
        - SKIPPED: Check not applicable
        - PENDING: Validation in progress
    """
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    PENDING = auto()


# Alias exports
VALIDATION_PASSED = ValidationStatus.PASSED
VALIDATION_FAILED = ValidationStatus.FAILED
VALIDATION_SKIPPED = ValidationStatus.SKIPPED
VALIDATION_PENDING = ValidationStatus.PENDING