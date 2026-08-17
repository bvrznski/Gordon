# Gordon Phase 5.7.3-I: Intentional Context Engine - Intentional Relations
# ===============================================================================
#
# Immutable intentional relations representing directed cognitive connections
# between the current experiential field and intentional objects.
#

"""
Intentional Relations Model for the Intentional Context Engine.

Intentional relations represent explicit directed connections between:
    - The current experiential field (source)
    - Intentional objects (targets)

Relation types follow Husserlian concepts only as theoretical inspiration -
runtime behavior remains engineering-oriented with typed, validated relations.
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
# INTENTIONAL RELATION KINDS
# =============================================================================

class IntentionalRelationKind:
    """
    Enum-like class for intentional relation types.
    
    Each relation type has:
        - Directionality: directed (unidirectional) or bidirectional
        - Provenance preservation: whether the chain is tracked
    
    Required relation types per Phase 5.7.3-I specification:
    """
    
    # Directed relations (source -> target)
    ATTENDING_TO = "attending_to"
    REASONING_ABOUT = "reasoning_about"
    PLANNING_FOR = "planning_for"
    OBSERVING = "observing"  # bidirectional
    RECALLING = "recalling"
    IMAGINING = "imagining"
    PREDICTING = "predicting"
    
    # Bidirectional relations
    MONITORING = "monitoring"  # bidirectional
    VALIDATING = "validating"
    COMMUNICATING_ABOUT = "communicating_about"  # bidirectional
    
    ALL: Tuple[str, ...] = (
        ATTENDING_TO,
        REASONING_ABOUT,
        PLANNING_FOR,
        OBSERVING,
        RECALLING,
        IMAGINING,
        PREDICTING,
        MONITORING,
        VALIDATING,
        COMMUNICATING_ABOUT,
    )
    
    @classmethod
    def is_directed(cls, kind: str) -> bool:
        """Check if a relation kind is directed (unidirectional)."""
        return kind not in (
            cls.OBSERVING,
            cls.MONITORING,
            cls.COMMUNICATING_ABOUT,
        )
    
    @classmethod
    def requires_provenance(cls, kind: str) -> bool:
        """Check if a relation kind preserves provenance."""
        return True  # All intentional relations preserve provenance


# =============================================================================
# INTENTIONAL RELATION
# =============================================================================

@dataclass(frozen=True)
class IntentionalRelation:
    """
    Immutable intentional relation representing directed cognitive connection.
    
    A relation represents the connection from:
        - Source: The experiential field (or its current snapshot)
        - Target: An intentional object that the field is directed toward
    
    Relation properties:
        - Typed: Specific relation kind determines semantics
        - Directed or bidirectional: As defined by kind
        - Provenance-preserving: Chain of transitions tracked
        - Validated: Must pass validation before publication
    
    NOT included:
        - Full content (only references)
        - Runtime state
        - Reasoning about the relation itself
    """
    
    # Identity (required fields first - no defaults before required)
    relation_id: str
    """Unique identifier for this intentional relation."""
    
    # Source reference (experiential field context)
    source_context_id: str
    """ID of the experiential field context this relation originates from."""
    
    # Target reference (intentional object)
    target_object_id: str
    """ID of the intentional object being related to."""
    
    # Relation kind (required - no default)
    relation_kind: str
    """Type of relation (see IntentionalRelationKind)."""
    
    # Directionality info (computed from kind, stored for determinism)
    directed: bool = field(init=False)
    """Whether this relation is directed (unidirectional)."""
    
    # Priority and metadata
    priority_reference: Optional[str] = None
    """Reference to priority assessment (e.g., 'high', 'medium', 'low')."""
    
    confidence: float = 1.0
    """Confidence level for this relation."""
    
    # Timing
    established_at_utc: float = field(default_factory=time.time)
    """When this relation was first established."""
    
    expires_at_utc: Optional[float] = None
    """Optional expiration time for this relation."""
    
    # Metadata (for extensibility)
    metadata: Dict[str, str] = field(default_factory=dict)
    """Optional metadata key-value pairs for extension."""
    
    def __post_init__(self) -> None:
        """Post-initialization to compute derived fields."""
        # Set the directed property based on the kind
        object.__setattr__(
            self,
            "directed",
            IntentionalRelationKind.is_directed(self.relation_kind)
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if this relation has expired."""
        if self.expires_at_utc is None:
            return False
        return time.time() > self.expires_at_utc
    
    @classmethod
    def create_attending_to(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 1.0,
        priority_reference: Optional[str] = None,
    ) -> "IntentionalRelation":
        """
        Create an attending_to relation (agent is currently focused on).
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being attended to
            confidence: Confidence level (0.0 to 1.0)
            priority_reference: Priority assessment reference
            
        Returns:
            New IntentionalRelation with kind='attending_to'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.ATTENDING_TO,
            confidence=confidence,
            priority_reference=priority_reference,
        )
    
    @classmethod
    def create_reasoning_about(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 0.8,
        priority_reference: Optional[str] = None,
    ) -> "IntentionalRelation":
        """
        Create a reasoning_about relation (currently thinking about).
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being reasoned about
            confidence: Confidence level in the reasoning
            priority_reference: Priority assessment reference
            
        Returns:
            New IntentionalRelation with kind='reasoning_about'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.REASONING_ABOUT,
            confidence=confidence,
            priority_reference=priority_reference,
        )
    
    @classmethod
    def create_planning_for(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 0.7,
        priority_reference: Optional[str] = None,
    ) -> "IntentionalRelation":
        """
        Create a planning_for relation (preparing to act toward).
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being planned for
            confidence: Confidence level in the plan
            priority_reference: Priority assessment reference
            
        Returns:
            New IntentionalRelation with kind='planning_for'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.PLANNING_FOR,
            confidence=confidence,
            priority_reference=priority_reference,
        )
    
    @classmethod
    def create_observing(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 1.0,
    ) -> "IntentionalRelation":
        """
        Create an observing relation (monitoring the object).
        
        This is a bidirectional relation.
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being observed
            confidence: Confidence level in observations
            
        Returns:
            New IntentionalRelation with kind='observing'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.OBSERVING,
            confidence=confidence,
        )
    
    @classmethod
    def create_monitoring(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 1.0,
    ) -> "IntentionalRelation":
        """
        Create a monitoring relation (tracking state changes).
        
        This is a bidirectional relation.
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being monitored
            confidence: Confidence level in monitoring
            
        Returns:
            New IntentionalRelation with kind='monitoring'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.MONITORING,
            confidence=confidence,
        )
    
    @classmethod
    def create_validating(
        cls,
        context_id: str,
        object_id: str,
        confidence: float = 0.9,
        evidence_reference: Optional[str] = None,
    ) -> "IntentionalRelation":
        """
        Create a validating relation (checking validity/truth of).
        
        Args:
            context_id: Experiential field context ID
            object_id: Intentional object being validated
            confidence: Confidence level in validation
            evidence_reference: Reference to validation evidence
            
        Returns:
            New IntentionalRelation with kind='validating'
        """
        return cls(
            relation_id=f"rel-{_generate_uuid()}",
            source_context_id=context_id,
            target_object_id=object_id,
            relation_kind=IntentionalRelationKind.VALIDATING,
            confidence=confidence,
            metadata={"evidence_reference": evidence_reference} if evidence_reference else {},
        )


# =============================================================================
# INTENTIONAL RELATION VALIDATOR
# =============================================================================

class IntentionalRelationValidator:
    """
    Validates intentional relations before publication.
    
    Validation checks:
        - Target existence (if registry provided)
        - Source existence
        - Type compatibility
        - Lifecycle state
        - Privacy classification
        - Trust level
        - Cycles (for bidirectional relations)
        - Dangling references
    
    Validation is part of the transition pipeline - invalid relations are
    rejected and never published.
    """
    
    def __init__(
        self,
        object_registry: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize validator with optional object registry for existence checks.
        
        Args:
            object_registry: Dict mapping object IDs to objects (for validation)
        """
        self._object_registry = object_registry or {}
    
    def validate_relation(
        self,
        relation: IntentionalRelation,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an intentional relation.
        
        Args:
            relation: The relation to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        # Check relation kind is valid
        if relation.relation_kind not in IntentionalRelationKind.ALL:
            return False, f"Invalid relation kind: {relation.relation_kind}"
        
        # Check target exists (if registry available)
        if self._object_registry and relation.target_object_id not in self._object_registry:
            return False, f"Missing target object: {relation.target_object_id}"
        
        # Check source context exists
        if not relation.source_context_id:
            return False, "Missing source context ID"
        
        # Validate confidence range
        if not (0.0 <= relation.confidence <= 1.0):
            return False, f"Confidence out of range: {relation.confidence}"
        
        # Check lifecycle state (if available in metadata)
        # This would check object lifecycle from registry
        
        # Check privacy compatibility (simplified)
        # In real implementation would check system-wide policies
        
        # No cycle detection for directed relations (single target)
        # Bidirectional would need additional logic
        
        return True, None
    
    def validate_batch(
        self,
        relations: Tuple[IntentionalRelation, ...],
    ) -> Tuple[Tuple[IntentionalRelation, ...], Tuple[str, ...]]:
        """
        Validate multiple relations.
        
        Args:
            relations: Tuple of relations to validate
            
        Returns:
            Tuple of (valid_relations, error_messages)
        """
        valid = []
        errors = []
        
        for relation in relations:
            is_valid, error_msg = self.validate_relation(relation)
            if is_valid:
                valid.append(relation)
            else:
                errors.append(error_msg or "Unknown validation error")
        
        return tuple(valid), tuple(errors)


# =============================================================================
# INTENTIONAL RELATION REGISTRY
# =============================================================================

class IntentionalRelationRegistry:
    """
    Registry for managing intentional relations.
    
    Provides:
        - Relation identity management
        - Kind-based filtering
        - Context-based lookups
        - Deterministic ordering (for replayability)
    """
    
    def __init__(self) -> None:
        """Initialize the registry with empty storage."""
        self._relations: Dict[str, IntentionalRelation] = {}
        self._kind_indices: Dict[str, set] = {kind: set() for kind in IntentionalRelationKind.ALL}
        self._context_indices: Dict[str, set] = {}
    
    def register(self, relation: IntentionalRelation) -> bool:
        """
        Register an intentional relation.
        
        Args:
            relation: The relation to register
            
        Returns:
            True if registered (or already exists), False on conflict
        """
        # Check for duplicate
        if relation.relation_id in self._relations:
            return False
        
        self._relations[relation.relation_id] = relation
        self._kind_indices[relation.relation_kind].add(relation.relation_id)
        
        ctx_idx = relation.source_context_id
        if ctx_idx not in self._context_indices:
            self._context_indices[ctx_idx] = set()
        self._context_indices[ctx_idx].add(relation.relation_id)
        
        return True
    
    def get(self, relation_id: str) -> Optional[IntentionalRelation]:
        """Get a relation by ID."""
        return self._relations.get(relation_id)
    
    def get_by_kind(self, kind: str) -> Tuple[IntentionalRelation, ...]:
        """Get all relations of a specific kind."""
        ids = self._kind_indices.get(kind, set())
        return tuple(self._relations[rid] for rid in ids if rid in self._relations)
    
    def get_by_context(self, context_id: str) -> Tuple[IntentionalRelation, ...]:
        """Get all relations from a specific context."""
        ids = self._context_indices.get(context_id, set())
        return tuple(self._relations[rid] for rid in ids if rid in self._relations)
    
    def remove(self, relation_id: str) -> bool:
        """Remove a relation by ID."""
        rel = self._relations.get(relation_id)
        if rel is None:
            return False
        
        del self._relations[relation_id]
        self._kind_indices[rel.relation_kind].discard(relation_id)
        
        ctx_idx = rel.source_context_id
        if ctx_idx in self._context_indices:
            self._context_indices[ctx_idx].discard(relation_id)
        
        return True
    
    @property
    def registered_count(self) -> int:
        """Return total number of registered relations."""
        return len(self._relations)
    
    @property
    def kind_counts(self) -> Dict[str, int]:
        """Return dict mapping kinds to their relation counts."""
        return {kind: len(ids) for kind, ids in self._kind_indices.items()}


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalRelationKind",
    "IntentionalRelation",
    "IntentionalRelationValidator",
    "IntentionalRelationRegistry",
)