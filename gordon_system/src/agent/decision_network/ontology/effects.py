# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Effects Ontology

This module defines the canonical Action effect taxonomy that describes
the semantic outcomes of Actions.

ACTION EFFECTS TAXONOMY
=======================

Effects represent the semantic consequences or results of an Action.
Each effect kind represents a coherent category of outcome.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION EFFECT KINDS - Semantic outcome types
# =============================================================================

class ActionEffectKind(Enum):
    """
    The semantic effect or outcome of an Action.
    
    Effects represent the semantic consequences or results of Actions.
    They describe what changes (or doesn't change) as a result of the
    Action, independent of execution timing or success/failure.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # NO CHANGE EFFECTS
    # =============================================================================
    
    NO_CHANGE = "no_change"
    """No change in state."""
    
    OBSERVATION_ONLY = "observation_only"
    """Only observation, no state change."""
    
    QUERY_RESULT = "query_result"
    """Result of a query without modification."""
    
    # =============================================================================
    # INFORMATION EFFECTS
    # =============================================================================
    
    INFORMATION_ACQUIRED = "information_acquired"
    """Information retrieved or acquired."""
    
    STATE_OBSERVED = "state_observed"
    """Current state observed."""
    
    KNOWLEDGE_EXPANDED = "knowledge_expanded"
    """Knowledge base expanded with new facts."""
    
    CONTEXT_UPDATED = "context_updated"
    """Context information updated."""
    
    # =============================================================================
    # CREATION EFFECTS
    # =============================================================================
    
    STATE_CREATED = "state_created"
    """New state or entity created."""
    
    ENTITY_GENERATED = "entity_generated"
    """Entity generated from scratch."""
    
    ARTIFACT_CREATED = "artifact_created"
    """Artifact or document created."""
    
    DATA_STORED = "data_stored"
    """Data persisted to storage."""
    
    # =============================================================================
    # UPDATE EFFECTS
    # =============================================================================
    
    STATE_UPDATED = "state_updated"
    """Existing state updated."""
    
    ENTITY_MODIFIED = "entity_modified"
    """Entity modified in place."""
    
    VALUE_CHANGED = "value_changed"
    """Value or property changed."""
    
    CONFIGURATION_UPDATED = "configuration_updated"
    """Configuration settings updated."""
    
    # =============================================================================
    # DELETION EFFECTS
    # =============================================================================
    
    STATE_REMOVED = "state_removed"
    """State or entity removed."""
    
    ENTITY_DELETED = "entity_deleted"
    """Entity deleted."""
    
    DATA_PURGED = "data_purged"
    """Data permanently removed."""
    
    RESOURCE_FREED = "resource_freed"
    """Resource released back to pool."""
    
    # =============================================================================
    # RESOURCE EFFECTS
    # =============================================================================
    
    RESOURCE_RESERVED = "resource_reserved"
    """Resource reserved for use."""
    
    RESOURCE_RELEASED = "resource_released"
    """Resource released from reservation."""
    
    CAPABILITY_ACQUIRED = "capability_acquired"
    """New capability obtained."""
    
    PERMISSION_GRANTED = "permission_granted"
    """Authorization granted."""
    
    # =============================================================================
    # COMMUNICATION EFFECTS
    # =============================================================================
    
    MESSAGE_DELIVERED = "message_delivered"
    """Message successfully delivered."""
    
    NOTIFICATION_SENT = "notification_sent"
    """Notification sent to recipient."""
    
    RESPONSE_PROVIDED = "response_provided"
    """Response generated and provided."""
    
    ACKNOWLEDGMENT_RECEIVED = "acknowledgment_received"
    """Acknowledgment received from recipient."""
    
    # =============================================================================
    # RECOVERY EFFECTS
    # =============================================================================
    
    RECOVERY_REQUESTED = "recovery_requested"
    """Recovery action requested."""
    
    ROLLBACK_REQUESTED = "rollback_requested"
    """Rollback to previous state requested."""
    
    COMPENSATION_REQUESTED = "compensation_requested"
    """Compensation for effects requested."""
    
    RESTORE_REQUESTED = "restore_requested"
    """Restore from backup requested."""
    
    # =============================================================================
    # CONTROL EFFECTS
    # =============================================================================
    
    EXECUTION_STARTED = "execution_started"
    """Execution process started."""
    
    EXECUTION_PAUSED = "execution_paused"
    """Execution process paused."""
    
    EXECUTION_RESUMED = "execution_resumed"
    """Execution process resumed."""
    
    EXECUTION_STOPPED = "execution_stopped"
    """Execution process stopped."""
    
    # =============================================================================
    # VERIFICATION EFFECTS
    # =============================================================================
    
    VALIDATION_PASSED = "validation_passed"
    """Validation check passed."""
    
    VALIDATION_FAILED = "validation_failed"
    """Validation check failed."""
    
    STATUS_REPORTED = "status_reported"
    """Status information reported."""
    
    METRIC_MEASURED = "metric_measured"
    """System metric measured."""
    
    # =============================================================================
    # SPECIAL EFFECTS
    # =============================================================================
    
    TRANSACTION_COMMITTED = "transaction_committed"
    """Transaction committed successfully."""
    
    TRANSACTION_ROLLED_BACK = "transaction_rolled_back"
    """Transaction rolled back."""
    
    STATE_SNAPSHOT_CREATED = "state_snapshot_created"
    """State snapshot created for recovery."""
    
    EVENT_TRIGGERED = "event_triggered"
    """Event triggered or emitted."""
    
    # =============================================================================
    # GENERAL EFFECTS
    # =============================================================================
    
    UNKNOWN = "unknown"
    """Effect is unknown or undetermined."""
    
    COMPOSITE_RESULT = "composite_result"
    """Result of composite action execution."""
    
    PARALLEL_RESULTS = "parallel_results"
    """Multiple results from parallel execution."""


# =============================================================================
# UTILITY TYPES - Effect collections
# =============================================================================

class ActionEffectKinds(FrozenSet[ActionEffectKind]):
    """A collection of ActionEffectKind values."""
    
    def __new__(cls, effects: Tuple[ActionEffectKind, ...] = ()):
        return super().__new__(cls, effects)
    
    @classmethod
    def all(cls) -> "ActionEffectKinds":
        """Get all canonical ActionEffectKinds."""
        return cls(tuple(ActionEffectKind))
    
    @classmethod
    def state_changes(cls) -> "ActionEffectKinds":
        """Get all state-changing effect kinds."""
        return cls((
            ActionEffectKind.STATE_CREATED,
            ActionEffectKind.STATE_UPDATED,
            ActionEffectKind.STATE_REMOVED,
        ))
    
    @classmethod
    def information_effects(cls) -> "ActionEffectKinds":
        """Get all information-related effect kinds."""
        return cls((
            ActionEffectKind.INFORMATION_ACQUIRED,
            ActionEffectKind.KNOWLEDGE_EXPANDED,
            ActionEffectKind.CONTEXT_UPDATED,
        ))


__all__ = [
    "ActionEffectKind",
    "ActionEffectKinds",
]