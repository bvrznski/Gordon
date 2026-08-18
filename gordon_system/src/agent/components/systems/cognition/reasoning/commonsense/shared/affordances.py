# Affordance Analysis - Phase 7.45
# ================================

"""
Canonical affordance contracts for Commonsense Reasoning.

Affordance analysis evaluates:
- What objects can be used for
- Possible interactions
- Expected functions
- Physical capabilities
- Limitations
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# AFFORDANCE IDENTITY
# =============================================================================

@dataclass(frozen=True)
class AffordanceIdentity:
    """
    Immutable identity for an affordance.
    """
    
    semantic_identity: str                    # Stable identity across runs
    context_hash: str                         # Hash of context that triggered this
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, context_hash: str) -> AffordanceIdentity:
        """Create a new affordance identity."""
        return cls(
            semantic_identity=semantic_identity,
            context_hash=context_hash,
        )


# =============================================================================
# POSSIBLE ACTION
# =============================================================================

@dataclass(frozen=True)
class PossibleAction:
    """
    An action that an object affords.
    
    Each action includes:
        - The action description
        - Required conditions
        - Expected outcome
        - Confidence estimate
    """
    
    action_id: str                            # Unique identifier
    action_name: str                          # e.g., "grasp", "push", "open"
    required_conditions: List[str] = field(default_factory=list)  # What must be true?
    expected_outcome: str = ""                # What happens if performed?
    
    confidence: float = 0.5                   # Confidence in this affordance
    
    @classmethod
    def create(
        cls,
        action_id: str,
        action_name: str,
        required_conditions: Optional[List[str]] = None,
        expected_outcome: str = "",
        confidence: float = 0.5,
    ) -> PossibleAction:
        """Create a new possible action."""
        return cls(
            action_id=action_id,
            action_name=action_name,
            required_conditions=required_conditions or [],
            expected_outcome=expected_outcome,
            confidence=confidence,
        )


# =============================================================================
# AFFORDANCE MODEL
# =============================================================================

@dataclass(frozen=True)
class AffordanceModel:
    """
    Model representing an affordance.
    
    Each model includes:
        - What the object affords
        - Physical basis for the affordance
        - Constraints on usage
        - Confidence estimate
    
    Affordances remain explicit and inspectable.
    """
    
    # Identity
    affordance_id: str                        # Unique affordance identifier
    semantic_identity: str                    # Semantic identity of this affordance type
    
    # Object being analyzed
    affected_object: str                      # e.g., "object_123"
    
    # Supported actions
    possible_actions: List[PossibleAction] = field(default_factory=list)
    
    # Constraints
    physical_constraints: List[str] = field(default_factory=list)  # What limits this?
    operational_limits: List[str] = field(default_factory=list)   # When does it work?
    
    # Confidence
    confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        affected_object: str,
        possible_actions: Optional[List[PossibleAction]] = None,
        physical_constraints: Optional[List[str]] = None,
        operational_limits: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> AffordanceModel:
        """Create a new affordance model."""
        return cls(
            affordance_id=f"affordance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            affected_object=affected_object,
            possible_actions=possible_actions or [],
            physical_constraints=physical_constraints or [],
            operational_limits=operational_limits or [],
            confidence=confidence,
        )
    
    def get_action(self, action_name: str) -> Optional[PossibleAction]:
        """Find a specific action by name."""
        for action in self.possible_actions:
            if action.action_name == action_name:
                return action
        return None
    
    @property
    def minimum_confidence(self) -> float:
        """Get the minimum confidence from possible actions."""
        if not self.possible_actions:
            return 0.0
        return min(action.confidence for action in self.possible_actions)


# =============================================================================
# AFFORDANCE MANAGEMENT RECORD
# =============================================================================

@dataclass(frozen=True)
class AffordanceManagement:
    """
    Record of affordance management.
    
    Each record includes:
        - The affordance model itself
        - Contextual evaluation
        - Confidence assessment
        - Provenance tracking
    
    This is the primary contract for accessing affordances during reasoning.
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity of this record
    
    # Affordance data
    affordance_model: AffordanceModel         # The actual affordance
    
    # Evaluation
    context_compatible: bool = True           # Is current context compatible?
    
    # Confidence assessment
    effective_confidence: float = 0.5         # Final confidence after evaluation
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        affordance_model: AffordanceModel,
        context_compatible: bool,
        effective_confidence: float = 0.5,
    ) -> AffordanceManagement:
        """Create a new affordance management record."""
        return cls(
            management_id=f"affordance_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            affordance_model=affordance_model,
            context_compatible=context_compatible,
            effective_confidence=effective_confidence,
        )


# =============================================================================
# AFFORDANCE TYPES
# =============================================================================

class AffordanceType(Enum):
    """Types of affordances."""
    
    GRASP = "grasp"                           # Can be grasped/held
    PUSH_PULL = "push_pull"                   # Can be pushed or pulled
    ROTATE = "rotate"                         # Can be rotated/turned
    INSERT = "insert"                         # Can be inserted into something
    LIFT = "lift"                             # Can be lifted (has weight)
    BREAK = "break"                           # Can be broken/crushed
    CONTAIN = "contain"                       # Can contain other objects


# =============================================================================
# AFFORDANCE TRACE
# =============================================================================

@dataclass(frozen=True)
class AffordanceTrace:
    """
    Complete trace of affordance through reasoning.
    
    A trace contains:
        - Original affordance model
        - All contexts it was applied in
        - Validation results
        - Confidence evolution
    """
    
    # Identity
    trace_id: str                             # Unique trace identifier
    
    # Affordance data
    affordance_model: AffordanceModel         # The original affordance
    
    # Application history
    applications: List[Tuple[str, float]] = field(default_factory=list)
    
    # Validation history
    validations: List[Tuple[bool, Optional[str], float]] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, affordance_model: AffordanceModel) -> AffordanceTrace:
        """Create a new affordance trace."""
        return cls(
            trace_id=f"affordance_trace:{uuid.uuid4().hex[:16]}",
            affordance_model=affordance_model,
        )


__all__ = [
    "AffordanceIdentity",
    "PossibleAction",
    "AffordanceModel",
    "AffordanceManagement",
    "AffordanceType",
    "AffordanceTrace",
]