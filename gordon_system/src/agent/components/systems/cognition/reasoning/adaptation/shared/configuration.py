# Configuration Refinement - Phase 7.25
# =====================================

"""
Canonical Configuration Refinement contract.

Configuration refinement determines parameter updates, threshold adjustments,
policy activation/deactivation, and resource tuning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConfigurationRefinement:
    """
    A configuration refinement that modifies Gordon's operational parameters.
    
    Configuration refinement determines:
        - Parameter updates
        - Threshold adjustments
        - Policy activation
        - Policy deactivation
        - Resource tuning
    
    Configuration refinements remain explicit and are never permanent.
    """
    
    # Identity
    refinement_identity: str              # Unique refinement identifier
    
    # Previous configuration state
    previous_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Refined configuration
    refined_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Rationale for the change
    refinement_rationale: str             # Why this change was made
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Lifecycle
    created_at_utc: float = field(default_factory=time.time)
    applied_at_utc: Optional[float] = None
    reverted_at_utc: Optional[float] = None
    
    @property
    def is_applied(self) -> bool:
        """Check if refinement has been applied."""
        return self.applied_at_utc is not None and self.reverted_at_utc is None
    
    @classmethod
    def create(
        cls,
        refined_configuration: Dict[str, Any],
        previous_configuration: Optional[Dict[str, Any]] = None,
        refinement_rationale: str = "default",
        provenance: Optional[Dict[str, Any]] = None,
    ) -> ConfigurationRefinement:
        """Create a new configuration refinement."""
        return cls(
            refinement_identity=f"refinement:{uuid.uuid4().hex[:16]}",
            previous_configuration=previous_configuration or {},
            refined_configuration=refined_configuration,
            refinement_rationale=refinement_rationale,
            provenance=provenance or {},
            applied_at_utc=time.time(),
        )
    
    def revert(self) -> ConfigurationRefinement:
        """Return a copy with this refinement reverted."""
        return dataclass_replace(
            self,
            reverted_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ConfigurationManagement:
    """
    Management of configuration refinements.
    
    Configuration management evaluates:
        - Parameter consistency
        - Policy compatibility
        - Configuration integrity
        - Resource limits
        - Activation conditions
    
    Configuration remains explicit.
    """
    
    # Identity
    configuration_identity: str           # Unique management identifier
    
    # Configuration model
    configuration_model: Dict[str, Any]   # The managed configuration
    
    # Activation policy
    activation_policy: str = "default"    # When/how to activate
    
    # Rollback policy
    rollback_policy: str = "immediate"    # How to rollback if needed
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ConfigurationRefinement",
    "ConfigurationManagement",
]