# Context Adaptation - Phase 7.25
# ===============================

"""
Canonical Context Adaptation contract.

Context adaptation derives environment-specific policies, task-specific
configurations, and resource-aware behaviors.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ContextAdaptation:
    """
    A contextual adaptation that modifies Gordon's configuration based on context.
    
    Context adaptation derives:
        - Environment-specific policies
        - Task-specific configurations
        - Resource-aware behaviors
        - Latency-aware strategies
        - Interaction profiles
    
    Context adaptations remain explicit and are never permanent.
    """
    
    # Identity
    context_identity: str                 # Unique context identifier
    
    # Operational context
    operational_context: Dict[str, Any]   # Description of the current context
    
    # Adapted configuration
    adapted_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Applicability conditions
    applicability: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    activated_at_utc: Optional[float] = None
    
    @property
    def is_active(self) -> bool:
        """Check if adaptation is currently active."""
        return self.activated_at_utc is not None
    
    @classmethod
    def create(
        cls,
        operational_context: Dict[str, Any],
        adapted_configuration: Optional[Dict[str, Any]] = None,
        applicability: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> ContextAdaptation:
        """Create a new context adaptation."""
        return cls(
            context_identity=f"context:{uuid.uuid4().hex[:16]}",
            operational_context=operational_context,
            adapted_configuration=adapted_configuration or {},
            applicability=applicability or {},
            provenance=provenance or {},
            activated_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ContextManagement:
    """
    Management of context adaptations.
    
    Context management evaluates:
        - Environmental conditions
        - Resource availability
        - Execution profile
        - Task characteristics
        - Interaction profile
        - Operational priorities
    
    Context remains explicit.
    """
    
    # Identity
    context_identity: str                 # Unique management identifier
    
    # Operational context
    operational_context: Dict[str, Any]   # The managed context
    
    # Context model for inference
    context_model: Optional[Dict[str, Any]] = None  # Model for context inference
    
    # Applicability constraints
    applicability_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ContextAdaptation",
    "ContextManagement",
]