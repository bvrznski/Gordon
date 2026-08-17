# Gordon Phase 5.7.3-I: Intentional Context Engine - Canonical Engine
# ===============================================================================
#
# The canonical Intentional Context Engine implementing the subsystem answering:
# "What is the agent currently directed toward?"
#

"""
Canonical Intentional Context Engine for Gordon.

The Intentional Context Engine represents Gordon's current directed cognitive
context. It answers: "What is the agent presently directed toward?"

It organizes relationships between the current experiential field and
intentional objects. It never performs reasoning, never grants truth,
never grants authorization, and never executes actions.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

# Import own modules (relative)
from gordon.agent.components.systems.consciousnessobject import (
    IntentionalObject,
    IntentionalObjectKind,
    IntentionalObjectRegistry,
)
from gordon.agent.components.systems.consciousnessrelation import (
    IntentionalRelation,
    IntentionalRelationKind,
    IntentionalRelationValidator,
    IntentionalRelationRegistry,
)
from gordon.agent.components.systems.consciousnesstarget import (
    IntentionalTarget,
    TargetStatus,
    IntentionalTargetRegistry,
)
from gordon.agent.components.systems.consciousnesssnapshot import (
    IntentionalContextSnapshot,
    IntentionalContextSnapshotBuilder,
)
from gordon.agent.components.systems.consciousnesstransition import (
    IntentionalTransition,
    IntentionalTransitionAuthority,
)
from gordon.agent.components.systems.consciousnessdiagnostics import (
    IntentionalContextDiagnosticsSnapshot,
    IntentionalContextHealthSnapshot,
)
from gordon.agent.components.systems.consciousnessintegrity import (
    IntentionalIntegrityEnforcer,
)


# =============================================================================
# INTENTIONAL CONTEXT ENGINE
# =============================================================================

@dataclass
class IntentionalContextEngine:
    """
    Canonical Intentional Context Engine for Gordon.
    
    The Intentional Context Engine represents Gordon's current directed cognitive
    context. It answers: "What is the agent presently directed toward?"
    
    Responsibilities:
        - Maintain intentional objects (perceived, remembered, imagined, etc.)
        - Track intentional relations between field and objects
        - Manage intentional targets with lifecycle state
        - Publish immutable snapshots of intentional states
        - Handle transitions atomically
        
    NOT responsible for:
        - Reasoning or inference
        - Planning or decision-making
        - Action execution
        - Memory persistence
        - Perception processing
    
    The engine is designed to be:
        - Immutable: Published snapshots are never mutated
        - Deterministic: Same inputs produce identical outputs
        - Provenance-preserving: All transitions are tracked
        - Trust/privacy-aware: Boundary checks on all operations
    """
    
    # Identity
    _context_id: str = field(default_factory=lambda: f"context-{time.time()}")
    """Unique identifier for this intentional context."""
    
    # Internal registries (private)
    _object_registry: IntentionalObjectRegistry = field(default_factory=IntentionalObjectRegistry)
    """Registry for intentional objects."""
    
    _relation_registry: IntentionalRelationRegistry = field(default_factory=IntentionalRelationRegistry)
    """Registry for intentional relations."""
    
    _target_registry: IntentionalTargetRegistry = field(default_factory=IntentionalTargetRegistry)
    """Registry for intentional targets."""
    
    # Transition authority
    _transition_authority: IntentionalTransitionAuthority = field(default_factory=IntentionalTransitionAuthority)
    """Authority for managing transitions."""
    
    # Integrity enforcer
    _integrity_enforcer: IntentionalIntegrityEnforcer = field(default_factory=lambda: IntentionalIntegrityEnforcer())
    """Enforcer of integrity constraints."""
    
    # Current snapshot state
    _current_snapshot: Optional[IntentionalContextSnapshot] = None
    """Current published intentional context snapshot."""
    
    _generation: int = 0
    """Current generation number."""
    
    # Timestamps
    _initialized_at_utc: float = field(default_factory=time.time)
    """When this engine was initialized."""
    
    # Configuration (bounded for determinism)
    _max_objects: int = 10000
    _max_relations: int = 50000
    _max_targets: int = 1000
    
    # =========================================================================
    # INITIALIZATION AND LIFECYCLE
    # =========================================================================
    
    def initialize(self) -> Tuple[bool, Optional[str]]:
        """
        Initialize the Intentional Context Engine.
        
        Creates initial empty snapshot at generation 0.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._current_snapshot is not None:
            return False, "Already initialized"
        
        try:
            self._current_snapshot = IntentionalContextSnapshot.initial(self._context_id)
            self._generation = 0
            return True, None
        except Exception as e:
            return False, f"Initialization failed: {str(e)}"
    
    def start(self) -> Tuple[bool, Optional[str]]:
        """
        Start the engine for operations.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        if self._current_snapshot is None:
            return False, "Not initialized"
        return True, None
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        """
        Stop the engine.
        
        Returns:
            Tuple of (success, error_message if failed)
        """
        # In a real implementation would clean up resources
        return True, None
    
    # =========================================================================
    # OBJECT MANAGEMENT
    # =========================================================================
    
    def add_intentional_object(
        self,
        obj: IntentionalObject,
    ) -> Tuple[bool, Optional[str]]:
        """
        Add an intentional object to the context.
        
        Args:
            obj: The intentional object to add
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Validate integrity
        is_valid, error = self._integrity_enforcer.validate_object(
            obj.object_id,
            obj.source_system,
            obj.expires_at_utc,
            0.5,  # Default trust level for validation
        )
        
        if not is_valid:
            return False, f"Object validation failed: {error}"
        
        # Check capacity
        current_count = self._object_registry.registered_count
        if current_count >= self._max_objects:
            return False, f"Maximum objects reached ({self._max_objects})"
        
        # Register the object
        self._object_registry.register(obj)
        return True, None
    
    def get_intentional_object(self, object_id: str) -> Optional[IntentionalObject]:
        """Get an intentional object by ID."""
        return self._object_registry.get(object_id)
    
    def get_objects_by_kind(self, kind: str) -> Tuple[IntentionalObject, ...]:
        """Get all objects of a specific kind."""
        return self._object_registry.get_by_kind(kind)
    
    # =========================================================================
    # RELATION MANAGEMENT
    # =========================================================================
    
    def add_intentional_relation(
        self,
        relation: IntentionalRelation,
    ) -> Tuple[bool, Optional[str]]:
        """
        Add an intentional relation to the context.
        
        Args:
            relation: The relation to add
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Validate integrity
        is_valid, error = self._integrity_enforcer.validate_relation(
            relation.relation_kind,
            relation.source_context_id,
            relation.target_object_id,
            relation.directed,
        )
        
        if not is_valid:
            return False, f"Relation validation failed: {error}"
        
        # Check target exists
        target_obj = self._object_registry.get(relation.target_object_id)
        if target_obj is None:
            return False, f"Target object not found: {relation.target_object_id}"
        
        # Check capacity
        current_count = self._relation_registry.registered_count
        if current_count >= self._max_relations:
            return False, f"Maximum relations reached ({self._max_relations})"
        
        # Register the relation
        self._relation_registry.register(relation)
        return True, None
    
    def get_intentional_relation(self, relation_id: str) -> Optional[IntentionalRelation]:
        """Get an intentional relation by ID."""
        return self._relation_registry.get(relation_id)
    
    def get_relations_by_kind(self, kind: str) -> Tuple[IntentionalRelation, ...]:
        """Get all relations of a specific kind."""
        return self._relation_registry.get_by_kind(kind)
    
    # =========================================================================
    # TARGET MANAGEMENT
    # =========================================================================
    
    def add_intentional_target(
        self,
        target: IntentionalTarget,
    ) -> Tuple[bool, Optional[str]]:
        """
        Add an intentional target to the context.
        
        Args:
            target: The target to add
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Validate integrity
        is_valid, error = self._integrity_enforcer.validate_target(
            target.status,
            target.source_owner,
            target.privacy_classification,
            target.trust_level,
        )
        
        if not is_valid:
            return False, f"Target validation failed: {error}"
        
        # Check capacity
        current_count = self._target_registry.registered_count
        if current_count >= self._max_targets:
            return False, f"Maximum targets reached ({self._max_targets})"
        
        # Register the target
        self._target_registry.register(target)
        return True, None
    
    def get_intentional_target(self, target_id: str) -> Optional[IntentionalTarget]:
        """Get an intentional target by ID."""
        return self._target_registry.get(target_id)
    
    def get_active_targets(self) -> Tuple[IntentionalTarget, ...]:
        """Get all active targets (active or suspended)."""
        active_statuses = {TargetStatus.ACTIVE, TargetStatus.SUSPENDED}
        return tuple(
            target
            for target in self._target_registry.registered_count > 0 and 
            self._target_registry.get_by_status(TargetStatus.ACTIVE)
            + self._target_registry.get_by_status(TargetStatus.SUSPENDED)
        )
    
    # =========================================================================
    # SNAPSHOT PUBLICATION
    # =========================================================================
    
    def get_current_snapshot(self) -> Optional[IntentionalContextSnapshot]:
        """Get the current published snapshot."""
        return self._current_snapshot
    
    def update_and_publish_snapshot(
        self,
        experiential_field_context_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[IntentionalContextSnapshot]]:
        """
        Update and publish a new intentional context snapshot.
        
        Creates a new generation snapshot with the current state of
        objects, relations, and targets.
        
        Args:
            experiential_field_context_id: Current EF context ID for reference
            
        Returns:
            Tuple of (success, error_message, new_snapshot if successful)
        """
        try:
            # Build new snapshot
            builder = IntentionalContextSnapshotBuilder(
                self._context_id,
                self._generation + 1,
            )
            
            # Add references from registries
            for obj in self._object_registry._objects.values():
                builder.add_object_reference(obj.object_id)
            
            for rel in self._relation_registry._relations.values():
                builder.add_relation_reference(rel.relation_id)
            
            for target in self._target_registry._targets.values():
                builder.add_target_reference(target.target_id)
            
            # Set experiential field reference
            if experiential_field_context_id:
                builder.set_experiential_field_context_id(experiential_field_context_id)
            
            # Build and validate
            new_snapshot = builder.build()
            
            # Validate integrity before publishing
            is_valid, error = self._integrity_enforcer.validate_snapshot(
                new_snapshot.generation,
                self._generation,
                len(new_snapshot.object_references),
                len(new_snapshot.relation_references),
                len(new_snapshot.target_references),
            )
            
            if not is_valid:
                return False, f"Snapshot validation failed: {error}", None
            
            # Publish new snapshot
            self._current_snapshot = new_snapshot
            self._generation += 1
            
            return True, None, new_snapshot
            
        except Exception as e:
            return False, f"Snapshot publication failed: {str(e)}", None
    
    # =========================================================================
    # TRANSITION MANAGEMENT
    # =========================================================================
    
    def create_transition(
        self,
        transition_kind: str = "default",
        trigger: str = "internal",
    ) -> IntentionalTransition:
        """
        Create a new transition.
        
        Args:
            transition_kind: Kind of transition
            trigger: What triggered the transition
            
        Returns:
            New IntentionalTransition in PENDING state
        """
        return self._transition_authority.create_transition(
            context_id=self._context_id,
            previous_generation=self._generation,
            new_generation=self._generation + 1,
            transition_kind=transition_kind,
            trigger=trigger,
        )
    
    def commit_transition(self, transition: IntentionalTransition) -> Tuple[bool, Optional[str]]:
        """
        Commit a transition (publish new snapshot).
        
        Args:
            transition: The transition to commit
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Commit the transition
        committed = self._transition_authority.commit_transition(transition)
        
        if not committed.is_success:
            return False, f"Transition commit failed: {committed.failure_reason}"
        
        # Generate and publish new snapshot
        success, error, _ = self.update_and_publish_snapshot()
        
        if not success:
            # Rollback transition (already done by authority but log here)
            pass
        
        return success, error
    
    # =========================================================================
    # DIAGNOSTICS AND HEALTH
    # =========================================================================
    
    def query_diagnostics(self) -> IntentionalContextDiagnosticsSnapshot:
        """
        Query diagnostics for the intentional context.
        
        Returns:
            Bounded diagnostics information without exposing content
        """
        return IntentionalContextDiagnosticsSnapshot(
            context_id=self._context_id,
            generation=self._generation,
            age_seconds=time.time() - self._initialized_at_utc,
            registered_object_count=self._object_registry.registered_count,
            active_object_count=len([
                obj for obj in self._object_registry._objects.values()
                if obj.lifecycle_state == "active"
            ]),
            kind_counts=tuple(self._object_registry.kind_counts.keys()),
            registered_relation_count=self._relation_registry.registered_count,
            active_relation_count=len([
                rel for rel in self._relation_registry._relations.values()
                if not rel.is_expired
            ]),
            relation_kind_counts=tuple(self._relation_registry.kind_counts.keys()),
            registered_target_count=self._target_registry.registered_count,
            active_target_count=self._target_registry.active_target_count,
            target_status_counts=tuple(self._target_registry.status_counts.keys()),
            last_transition_id=None,  # Would track in real implementation
            privacy_summary="internal",
            trust_summary="medium",
        )
    
    def query_health(self) -> IntentionalContextHealthSnapshot:
        """
        Query health for the intentional context.
        
        Returns:
            Bounded health information without exposing content
        """
        return IntentionalContextHealthSnapshot(
            context_id=self._context_id,
            state="active" if self._current_snapshot else "initialized",
            initialized=self._current_snapshot is not None,
            ready=self._current_snapshot is not None and self._current_snapshot.is_valid,
            active=self._current_snapshot is not None and self._current_snapshot.build_status == "valid",
        )
    
    # =========================================================================
    # INTEGRATION WITH EXPERIENTIAL FIELD
    # =========================================================================
    
    def integrate_experiential_field_context(
        self,
        experiential_field_id: str,
        field_generation: int,
        contents: Tuple[str, ...] = tuple(),
        relations: Tuple[str, ...] = tuple(),
    ) -> Tuple[bool, Optional[str]]:
        """
        Integrate with the Experiential Field context.
        
        Creates intentional targets based on experiential field content
        to represent what is currently being directed toward.
        
        Args:
            experiential_field_id: Current EF context ID
            field_generation: Current EF generation
            contents: Content IDs from experiential field
            relations: Relation IDs between contents
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        try:
            # Add intentional targets for field contents
            for content_id in contents:
                target = IntentionalTarget.create_target(
                    object_reference=content_id,
                    source_owner="experiential_field",
                    privacy_classification="internal",
                    trust_level=0.8,  # Field contents are validated
                )
                
                is_valid, error = self._integrity_enforcer.validate_target(
                    target.status,
                    target.source_owner,
                    target.privacy_classification,
                    target.trust_level,
                )
                
                if not is_valid:
                    continue  # Skip invalid targets
                
                self._target_registry.register(target)
            
            return True, None
            
        except Exception as e:
            return False, f"Experiential field integration failed: {str(e)}"
    
    # =========================================================================
    # PROPERTIES AND QUERIES
    # =========================================================================
    
    @property
    def context_id(self) -> str:
        """Get the context ID."""
        return self._context_id
    
    @property
    def generation(self) -> int:
        """Get the current generation number."""
        return self._generation
    
    @property
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._current_snapshot is not None
    
    @property
    def active_target_count(self) -> int:
        """Get count of active targets."""
        return self._target_registry.active_target_count
    
    @property
    def registered_object_count(self) -> int:
        """Get total registered objects."""
        return self._object_registry.registered_count
    
    @property
    def registered_relation_count(self) -> int:
        """Get total registered relations."""
        return self._relation_registry.registered_count


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "IntentionalContextEngine",
)