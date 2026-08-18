# Self Model - Phase 7.29
# =======================

"""
Self Model represents Gordon's current internal cognitive condition.

The Self Model includes:
    - Active reasoning
    - Active goals
    - Active plans
    - Resource utilization
    - Confidence state
    - Attention allocation
    - Memory utilization
    - Operational stability

The Self Model remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SelfModel:
    """
    Representation of Gordon's current internal cognitive condition.
    
    A self model contains:
        - Explicit identity
        - Represented subsystems
        - Cognitive snapshot
        - Confidence state
        - Provenance tracking
    
    Self models remain independently inspectable.
    """
    
    # Identity
    model_id: str                               # Unique identifier
    semantic_identity: str                      # Semantic identity for replay
    
    # Represented subsystems
    represented_subsystems: Set[str]            # Subsystems included in this model
    
    # Cognitive snapshot (current state)
    active_reasoning: List[str] = field(default_factory=list)       # Active reasoning sessions
    active_goals: List[Dict[str, Any]] = field(default_factory=list)  # Active goals with metadata
    active_plans: List[Dict[str, Any]] = field(default_factory=list)  # Active plans with metadata
    
    # Resource utilization
    resource_utilization: Dict[str, float] = field(default_factory=dict)  # e.g., memory, cpu
    working_memory_items: int = 0                   # Number of items in working memory
    
    # Confidence state
    confidence_estimate: float = 0.5                # Overall confidence (0.0-1.0)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)  # Per-domain confidence
    
    # Attention allocation
    attention_focus: List[str] = field(default_factory=list)       # Currently focused areas
    attention_weights: Dict[str, float] = field(default_factory=dict)  # Weight per area
    
    # Memory utilization
    memory_utilization_percentage: float = 0.0      # Overall memory usage
    recent_memories_count: int = 0                  # Count of recently accessed memories
    
    # Operational stability
    operational_stable: bool = True                 # Is system stable?
    instability_factors: List[str] = field(default_factory=list)  # Current instabilities
    
    # Compatibility
    compatibility_revision: int = 1                 # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    observation_source: str = "introspection"       # Source of observations
    observation_timestamps: List[float] = field(default_factory=list)  # When observed
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        represented_subsystems: Set[str],
        active_reasoning: Optional[List[str]] = None,
        active_goals: Optional[List[Dict[str, Any]]] = None,
        confidence_estimate: float = 0.5,
        source: str = "introspection",
    ) -> SelfModel:
        """Create a new self model."""
        return cls(
            model_id=f"self_model:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            represented_subsystems=represented_subsystems,
            active_reasoning=active_reasoning or [],
            active_goals=active_goals or [],
            confidence_estimate=confidence_estimate,
            observation_source=source,
            observation_timestamps=[time.time()],
        )
    
    def with_confidence(self, new_confidence: float) -> SelfModel:
        """Return a copy with updated confidence."""
        return dataclass_replace(
            self,
            confidence_estimate=new_confidence,
        )
    
    def with_subsystems(self, subsystems: Set[str]) -> SelfModel:
        """Return a copy with updated represented subsystems."""
        return dataclass_replace(
            self,
            represented_subsystems=subsystems,
        )


@dataclass(frozen=True)
class SelfModelManagement:
    """
    Management of self model construction process.
    
    A management object contains:
        - Model identity and strategy
        - Current state
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                          # Unique management identifier
    semantic_identity: str                      # Semantic identity for replay
    
    # Model configuration
    model_strategy: str                         # Strategy used for modeling
    min_confidence_threshold: float = 0.5       # Minimum confidence required
    
    # Current state
    current_stage: str = "initializing"         # Current modeling stage
    
    # Results (can be None if not yet completed)
    self_model_result: Optional[SelfModel] = None   # The constructed model
    
    # Quality metrics
    model_quality_score: float = 0.0            # Overall quality score
    coverage_score: float = 0.0                 # Subsystem coverage score
    
    # Compatibility
    compatibility_revision: int = 1             # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    observation_source: str = "introspection"   # Source of observations
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        model_strategy: str,
        source: str = "introspection",
    ) -> SelfModelManagement:
        """Create a new self model management."""
        return cls(
            management_id=f"self_model_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            model_strategy=model_strategy,
            observation_source=source,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SelfModel",
    "SelfModelManagement",
]