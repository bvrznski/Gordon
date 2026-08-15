# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Modality Ontology

This module defines the canonical Action modality taxonomy that describes
the state change behavior of Actions.

ACTION MODALITY TAXONOMY
========================

Modality describes the expected effect on system state, independent
of the specific mechanism used to achieve that effect.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION MODALITIES - State change behavior types
# =============================================================================

class ActionModality(Enum):
    """
    The modality or state change behavior of an Action.
    
    Modality describes the expected effect on system state, independent
    of the specific mechanism used to achieve that effect. It classifies
    Actions by their semantic state transformation properties.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # READ-ONLY MODALITIES - No state change
    # =============================================================================
    
    OBSERVE_ONLY = "observe_only"
    """No state change, observation only."""
    
    READ_ONLY = "read_only"
    """Read access, no modification."""
    
    QUERY_ONLY = "query_only"
    """Query without any side effects."""
    
    # =============================================================================
    # STATE-PRESERVING MODALITIES - Produce effects without local mutation
    # =============================================================================
    
    STATE_PRESERVING = "state_preserving"
    """Preserves existing state while producing effects."""
    
    COMMUNICATIVE = "communicative"
    """Transmits information without local state change."""
    
    INFORMATIVE = "informative"
    """Provides information without altering state."""
    
    # =============================================================================
    # STATE-MODIFYING MODALITIES - Modify existing state
    # =============================================================================
    
    STATE_MODIFYING = "state_modifying"
    """Modifies existing state."""
    
    UPDATE_STATE = "update_state"
    """Update properties of existing entity."""
    
    TRANSFORM_STATE = "transform_state"
    """Transform data or structure in place."""
    
    # =============================================================================
    # STATE-CREATING MODALITIES - Create new state
    # =============================================================================
    
    STATE_CREATING = "state_creating"
    """Creates new state or entities."""
    
    GENERATE_STATE = "generate_state"
    """Generate new content."""
    
    ACQUIRE_STATE = "acquire_state"
    """Acquire and store new information."""
    
    # =============================================================================
    # STATE-DELETING MODALITIES - Remove state
    # =============================================================================
    
    STATE_DELETING = "state_deleting"
    """Deletes or removes state."""
    
    REMOVE_STATE = "remove_state"
    """Remove from collection or location."""
    
    PURGE_STATE = "purge_state"
    """Permanently remove data."""
    
    # =============================================================================
    # RESOURCE MODALITIES - Manage resources
    # =============================================================================
    
    RESOURCE_ACQUIRING = "resource_acquiring"
    """Acquires resources or capabilities."""
    
    RESOURCE_RELEASING = "resource_releasing"
    """Releases resources or capabilities."""
    
    ALLOCATE_RESOURCE = "allocate_resource"
    """Allocate to purpose."""
    
    DEALLOCATE_RESOURCE = "deallocate_resource"
    """Deallocate from purpose."""
    
    # =============================================================================
    # CONTROL MODALITIES - Transfer control
    # =============================================================================
    
    CONTROL_TRANSFERRING = "control_transferring"
    """Transfers control or authority."""
    
    AUTHORITY_CHANGING = "authority_changing"
    """Changes authorization or authority."""
    
    # =============================================================================
    # IRREVERSIBLE MODALITIES
    # =============================================================================
    
    IRREVERSIBLE = "irreversible"
    """Fundamentally irreversible operation."""
    
    ONE_WAY = "one_way"
    """One-way operation with no reversal possible."""
    
    DESTROYING = "destroying"
    """Destruction of entity or state."""
    
    # =============================================================================
    # SPECIAL MODALITIES
    # =============================================================================
    
    UNKNOWN = "unknown"
    """Modality is unknown or undetermined."""
    
    MIXED = "mixed"
    """Combination of multiple modalities."""
    
    CONTEXTUAL = "contextual"
    """Effect depends on execution context."""
    
    @property
    def is_read_only(self) -> bool:
        """Check if modality is read-only (no state change)."""
        return self in (
            ActionModality.OBSERVE_ONLY,
            ActionModality.READ_ONLY,
            ActionModality.QUERY_ONLY,
        )
    
    @property
    def is_state_changing(self) -> bool:
        """Check if modality changes state."""
        return self in (
            ActionModality.STATE_MODIFYING,
            ActionModality.UPDATE_STATE,
            ActionModality.TRANSFORM_STATE,
            ActionModality.STATE_CREATING,
            ActionModality.GENERATE_STATE,
            ActionModality.ACQUIRE_STATE,
            ActionModality.STATE_DELETING,
            ActionModality.REMOVE_STATE,
            ActionModality.PURGE_STATE,
        )
    
    @property
    def is_mutating(self) -> bool:
        """Check if modality involves mutation."""
        return not self.is_read_only


# =============================================================================
# UTILITY TYPES - Modality collections
# =============================================================================

class ActionModalities(FrozenSet[ActionModality]):
    """A collection of ActionModality values."""
    
    def __new__(cls, modalities: Tuple[ActionModality, ...] = ()):
        return super().__new__(cls, modalities)
    
    @classmethod
    def all(cls) -> "ActionModalities":
        """Get all canonical ActionModalities."""
        return cls(tuple(ActionModality))
    
    @classmethod
    def read_only(cls) -> "ActionModalities":
        """Get all read-only modalities."""
        return cls(m for m in ActionModality if m.is_read_only)
    
    @classmethod
    def state_changing(cls) -> "ActionModalities":
        """Get all state-changing modalities."""
        return cls(m for m in ActionModality if m.is_state_changing)


__all__ = [
    "ActionModality",
    "ActionModalities",
]