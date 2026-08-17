# Gordon Phase 5.7.3-I: Intentional Context Engine - Intentional Objects
# ===============================================================================
#
# Immutable intentional objects representing entities toward which the agent
# is currently oriented (intentional directedness).
#

"""
Intentional Objects Model for the Intentional Context Engine.

Every active conscious field has one or more explicit directed relations
toward intentional objects. Intentionality follows Husserlian concepts only
as theoretical inspiration - runtime behavior remains engineering-oriented.

Possible intentional objects:
    - perceived objects (perception system contributions)
    - remembered objects (memory activations)
    - imagined objects (hypothetical constructs)
    - simulated objects (simulation outputs)
    - goals (desired outcomes)
    - hypotheses (testable propositions)
    - questions (inquiry targets)
    - plans (future action sequences)
    - actions (execution candidates)
    - conversations (dialogue contexts)
    - documents (informational artifacts)
    - users (external participants)
    - environments (contexts/situations)
    - internal concepts (abstract ideas)

Intentional objects never replace canonical ownership of source systems.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
import uuid


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# INTENTIONAL OBJECT IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class IntentionalObjectId:
    """
    Immutable unique identifier for an intentional object instance.
    
    The object ID persists across context transitions while the generation
    number increases. This allows tracking of a logical object's evolution.
    """
    
    value: str = field(default_factory=lambda: f"object-{_generate_uuid()}")
    """The string representation of this object ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "IntentionalObjectId":
        """Create an IntentionalObjectId from a string."""
        return cls(value=s)


# =============================================================================
# INTENTIONAL OBJECT KINDS
# =============================================================================

class IntentionalObjectKind:
    """
    Enum-like class for intentional object categories.
    
    Possible categories:
        - PERCEIVED: Objects from perception system (current sensory input)
        - REMEMBERED: Objects from memory system (past experiences)
        - IMAGINED: Hypothetical/creative objects
        - SIMULATED: Simulation outputs and predictions
        - GOAL: Desired outcomes the agent is working toward
        - HYPOTHESIS: Testable propositions under evaluation
        - QUESTION: Inquiry targets for information gathering
        - PLAN: Future action sequences being considered
        - ACTION: Execution candidates being prepared
        - CONVERSATION: Dialogue contexts and participants
        - DOCUMENT: Informational artifacts being processed
        - USER: External human or system参与者
        - ENVIRONMENT: Contextual/situational frame
        - CONCEPT: Abstract ideas and internal models
    """
    
    PERCEIVED = "perceived"
    REMEMBERED = "remembered"
    IMAGINED = "imagined"
    SIMULATED = "simulated"
    GOAL = "goal"
    HYPOTHESIS = "hypothesis"
    QUESTION = "question"
    PLAN = "plan"
    ACTION = "action"
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    USER = "user"
    ENVIRONMENT = "environment"
    CONCEPT = "concept"
    
    ALL: Tuple[str, ...] = (
        PERCEIVED,
        REMEMBERED,
        IMAGINED,
        SIMULATED,
        GOAL,
        HYPOTHESIS,
        QUESTION,
        PLAN,
        ACTION,
        CONVERSATION,
        DOCUMENT,
        USER,
        ENVIRONMENT,
        CONCEPT,
    )


# =============================================================================
# INTENTIONAL OBJECT
# =============================================================================

@dataclass(frozen=True)
class IntentionalObject:
    """
    Immutable intentional object representing something the agent is directed toward.
    
    Intentional objects are canonical references - they do not replace source
    system ownership but reference objects maintained by those systems.
    
    Properties:
        - Stable identity: Object ID persists across context transitions
        - Kind-specified: Belongs to one of the intentional categories
        - Source-referenced: Points to an object in a source system
        - Provenance-tracked: Origin chain preserved for auditability
        - Trust-estimated: Trust level assigned by source or system
        - Privacy-classified: Privacy level determines access controls
    
    NOT included (external ownership):
        - Full payload content (only references)
        - Runtime state from source systems
        - Action authority over source object
    """
    
    # Identity (required fields first - no defaults before required)
    object_id: str
    """Unique identifier for this intentional object."""
    
    object_kind: str
    """Category of this object (see IntentionalObjectKind)."""
    
    source_system: str
    """Source system that owns the canonical object (e.g., 'perception', 'memory')."""
    
    # Source reference
    source_object_id: Optional[str] = None
    """ID of the object in the source system (if applicable)."""
    
    # Classification
    source_generation: int = 0
    """Generation of the source at time of reference."""
    
    privacy_classification: str = "internal"
    """Privacy level for this intentional object."""
    
    trust_classification: str = "untrusted"
    """Trust level assigned to this object."""
    
    # Stability indicator
    stability_reference: Optional[str] = None
    """Reference to stability assessment (e.g., 'stable', 'transient')."""
    
    # Lifecycle state
    lifecycle_state: str = "active"
    """Current lifecycle state of the intentional object."""
    
    # Timing
    established_at_utc: float = field(default_factory=time.time)
    """When this intentional object was first established."""
    
    expires_at_utc: Optional[float] = None
    """Optional expiration time for this object."""
    
    # Provenance (for auditability)
    provenance_chain: Tuple[str, ...] = field(default_factory=tuple)
    """Chain of transitions that led to this reference."""
    
    # Metadata
    metadata: Dict[str, str] = field(default_factory=dict)
    """Optional metadata key-value pairs for extension."""
    
    @classmethod
    def create_perceived(
        cls,
        source_object_id: str,
        source_generation: int = 0,
        privacy_classification: str = "internal",
        trust_classification: str = "untrusted",
        source_system: str = "perception",
    ) -> "IntentionalObject":
        """
        Create an intentional object representing a perceived entity.
        
        Args:
            source_object_id: ID of the object in perception system
            source_generation: Source's generation at time of reference
            privacy_classification: Privacy level
            trust_classification: Trust level
            source_system: Source system name
            
        Returns:
            New IntentionalObject with kind='perceived'
        """
        import uuid
        object_id = f"object-{uuid.uuid4().hex[:8]}"
        
        return cls(
            object_id=object_id,
            object_kind=IntentionalObjectKind.PERCEIVED,
            source_system=source_system,
            source_object_id=source_object_id,
            source_generation=source_generation,
            privacy_classification=privacy_classification,
            trust_classification=trust_classification,
        )
    
    @classmethod
    def create_remembered(
        cls,
        memory_reference: str,
        source_generation: int = 0,
        provenance_chain: Optional[Tuple[str, ...]] = None,
        privacy_classification: str = "internal",
        trust_classification: str = "medium",
        source_system: str = "memory",
    ) -> "IntentionalObject":
        """
        Create an intentional object representing a remembered entity.
        
        Args:
            memory_reference: Reference to the memory system object
            source_generation: Source's generation at time of reference
            provenance_chain: Chain of transitions leading to this reference
            privacy_classification: Privacy level
            trust_classification: Trust level
            source_system: Source system name
            
        Returns:
            New IntentionalObject with kind='remembered'
        """
        import uuid
        object_id = f"object-{uuid.uuid4().hex[:8]}"
        
        return cls(
            object_id=object_id,
            object_kind=IntentionalObjectKind.REMEMBERED,
            source_system=source_system,
            source_object_id=memory_reference,
            source_generation=source_generation,
            privacy_classification=privacy_classification,
            trust_classification=trust_classification,
            provenance_chain=provenance_chain or tuple(),
        )
    
    @classmethod
    def create_goal(
        cls,
        goal_description: str,
        priority: int = 0,
        source_system: str = "motivation",
    ) -> "IntentionalObject":
        """
        Create an intentional object representing a current goal.
        
        Args:
            goal_description: Description of the goal
            priority: Priority level (higher = more urgent)
            source_system: Source system name
            
        Returns:
            New IntentionalObject with kind='goal'
        """
        import uuid
        object_id = f"object-{uuid.uuid4().hex[:8]}"
        
        return cls(
            object_id=object_id,
            object_kind=IntentionalObjectKind.GOAL,
            source_system=source_system,
            source_object_id=goal_description,
            privacy_classification="internal",
            trust_classification="medium",
            metadata={"priority": str(priority)},
        )
    
    @classmethod
    def create_hypothesis(
        cls,
        hypothesis_statement: str,
        confidence: float = 0.5,
        evidence_count: int = 0,
    ) -> "IntentionalObject":
        """
        Create an intentional object representing a hypothesis.
        
        Args:
            hypothesis_statement: The hypothesis proposition
            confidence: Confidence level (0.0 to 1.0)
            evidence_count: Number of supporting evidence items
            
        Returns:
            New IntentionalObject with kind='hypothesis'
        """
        import uuid
        object_id = f"object-{uuid.uuid4().hex[:8]}"
        
        return cls(
            object_id=object_id,
            object_kind=IntentionalObjectKind.HYPOTHESIS,
            source_system="cognition",
            source_object_id=hypothesis_statement,
            privacy_classification="internal",
            trust_classification="untrusted",  # Hypotheses are unverified
            metadata={
                "confidence": str(confidence),
                "evidence_count": str(evidence_count),
            },
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if this intentional object has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    @property
    def is_stable(self) -> bool:
        """Check if this object has stable lifecycle state."""
        return self.lifecycle_state in ("stable", "active")


# =============================================================================
# INTENTIONAL OBJECT REGISTRY
# =============================================================================

class IntentionalObjectRegistry:
    """
    Registry for managing intentional objects.
    
    Provides:
        - Object identity management
        - Kind-based filtering
        - Provenance tracking
        - Reference counting for lifecycle management
    """
    
    def __init__(self) -> None:
        """Initialize the registry with empty storage."""
        self._objects: Dict[str, IntentionalObject] = {}
        self._kind_indices: Dict[str, set] = {kind: set() for kind in IntentionalObjectKind.ALL}
        self._source_indices: Dict[str, set] = {}
    
    def register(self, obj: IntentionalObject) -> None:
        """
        Register an intentional object.
        
        Args:
            obj: The intentional object to register
        """
        if obj.object_id not in self._objects:
            self._objects[obj.object_id] = obj
            self._kind_indices[obj.object_kind].add(obj.object_id)
            
            source_idx = obj.source_system
            if source_idx not in self._source_indices:
                self._source_indices[source_idx] = set()
            self._source_indices[source_idx].add(obj.object_id)
    
    def get(self, object_id: str) -> Optional[IntentionalObject]:
        """
        Get an intentional object by ID.
        
        Args:
            object_id: The ID of the object to retrieve
            
        Returns:
            The IntentionalObject if found, None otherwise
        """
        return self._objects.get(object_id)
    
    def get_by_kind(self, kind: str) -> Tuple[IntentionalObject, ...]:
        """
        Get all intentional objects of a specific kind.
        
        Args:
            kind: The object kind to filter by
            
        Returns:
            Tuple of IntentionalObjects with matching kind
        """
        ids = self._kind_indices.get(kind, set())
        return tuple(self._objects[oid] for oid in ids if oid in self._objects)
    
    def get_by_source(self, source_system: str) -> Tuple[IntentionalObject, ...]:
        """
        Get all intentional objects from a specific source system.
        
        Args:
            source_system: The source system name to filter by
            
        Returns:
            Tuple of IntentionalObjects from the source
        """
        ids = self._source_indices.get(source_system, set())
        return tuple(self._objects[oid] for oid in ids if oid in self._objects)
    
    def remove(self, object_id: str) -> bool:
        """
        Remove an intentional object by ID.
        
        Args:
            object_id: The ID of the object to remove
            
        Returns:
            True if removed, False if not found
        """
        obj = self._objects.get(object_id)
        if obj is None:
            return False
        
        del self._objects[object_id]
        self._kind_indices[obj.object_kind].discard(object_id)
        
        source_idx = obj.source_system
        if source_idx in self._source_indices:
            self._source_indices[source_idx].discard(object_id)
        
        return True
    
    @property
    def registered_count(self) -> int:
        """Return the total number of registered objects."""
        return len(self._objects)
    
    @property
    def kind_counts(self) -> Dict[str, int]:
        """Return a dict mapping kinds to their object counts."""
        return {kind: len(ids) for kind, ids in self._kind_indices.items()}


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalObjectId",
    "IntentionalObjectKind",
    "IntentionalObject",
    "IntentionalObjectRegistry",
)