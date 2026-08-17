# Self Models - Phase 6.7
# =======================

"""
Self Models: Gordon's representation of its own state, capabilities, and limitations.

Self Models enable introspection by representing:
- Available capabilities and their status
- Current resource availability and utilization
- Memory state and capacity
- Reasoning abilities and constraints
- Running services and their states
- Hardware configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# SELF MODEL - Canonical self-representation
# =============================================================================


@dataclass(frozen=True)
class SelfModel:
    """
    Canonical representation of a self model in Gordon's knowledge system.
    
    Self Models enable introspection while preserving capability boundaries.
    
    Fields:
        model_identity:         Unique identifier for this self model
        semantic_identity:      Stable semantic identity across revisions
        capabilities:           Available capabilities and their status
        resources:              Current resource state
        limitations:            Known limitations and constraints
        assumptions:            Self-model specific assumptions
        confidence:             Confidence in self-assessment (0.0-1.0)
        provenance:             Origin tracking with timestamps and sources
    """
    
    # Identity fields (required)
    model_identity: str                 # Unique ID for this instance
    
    semantic_identity: str              # Stable identifier across revisions
    
    # Capabilities representation
    capabilities: Dict[str, Any] = field(default_factory=dict)  # Capability states
    
    # Resource state
    resources: Dict[str, Any] = field(default_factory=dict)  # Resource availability
    
    # Limitations (required)
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Known constraints
    
    # Assumptions (optional but recommended)
    assumptions: Tuple[str, ...] = field(default_factory=tuple)  # Self-model assumptions
    
    # Confidence in self-assessment
    confidence: float = 0.5             # Confidence score (0.0-1.0)
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if model has minimal required data."""
        return (
            len(self.model_identity) > 0 and
            len(self.limitations) >= 1
        )
    
    @property
    def capability_count(self) -> int:
        """Get the number of tracked capabilities."""
        return len(self.capabilities)
    
    @property
    def resource_count(self) -> int:
        """Get the number of tracked resources."""
        return len(self.resources)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert self model to dictionary for serialization."""
        return {
            "model_identity": self.model_identity,
            "semantic_identity": self.semantic_identity,
            "capabilities": dict(self.capabilities),
            "resources": dict(self.resources),
            "limitations": list(self.limitations),
            "assumptions": list(self.assumptions),
            "confidence": self.confidence,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SelfModel":
        """Create self model from dictionary."""
        return cls(
            model_identity=data.get("model_identity", str(uuid.uuid4())),
            semantic_identity=data.get("semantic_identity", ""),
            capabilities=dict(data.get("capabilities", {})),
            resources=dict(data.get("resources", {})),
            limitations=tuple(data.get("limitations", [])),
            assumptions=tuple(data.get("assumptions", [])),
            confidence=float(data.get("confidence", 0.5)),
            provenance=dict(data.get("provenance", {})),
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        capabilities: Optional[Dict[str, Any]] = None,
        resources: Optional[Dict[str, Any]] = None,
        limitations: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> "SelfModel":
        """
        Create a new self model.
        
        Args:
            semantic_identity: Stable identifier across revisions
            capabilities: Available capabilities (optional)
            resources: Current resource state (optional)
            limitations: Known limitations (required)
            assumptions: Self-model assumptions (optional)
            confidence: Confidence in self-assessment (0.0-1.0)
            
        Returns:
            A new self model
        """
        return cls(
            model_identity=f"self_model:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            capabilities=dict(capabilities or {}),
            resources=dict(resources or {}),
            limitations=tuple(limitations or []),
            assumptions=tuple(assumptions or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            provenance={
                "created_at_utc": time.time(),
                "builder_version": "1.0",
            },
        )


# =============================================================================
# CAPABILITY STATE - Individual capability tracking
# =============================================================================


@dataclass(frozen=True)
class CapabilityState:
    """
    Representation of a single capability state.
    
    Fields:
        capability_id:          Unique identifier for the capability
        name:                   Human-readable name
        enabled:                Whether the capability is currently active
        status:                 Detailed status description
        last_used:              When the capability was last used (UTC timestamp)
        usage_count:            Total number of uses
    """
    
    capability_id: str                  # Unique ID
    
    name: str = ""                      # Human-readable name
    
    enabled: bool = True                # Whether active
    
    status: str = "unknown"             # "active", "inactive", "error", etc.
    
    last_used: float = 0.0              # UTC timestamp of last use
    
    usage_count: int = 0                # Total uses


__all__ = [
    "SelfModel",
    "CapabilityState",
]