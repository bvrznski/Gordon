# Hypothetical Reasoning Descriptor - Phase 7.15 Part 2
# =========================================================

"""
Canonical Hypothetical Descriptor.

A descriptor exposes hypothetical reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class HypotheticalMode(Enum):
    """Modes of hypothetical reasoning."""
    
    EXPLORATORY = "exploratory"              # Open-ended possibility exploration
    DIAGNOSTIC = "diagnostic"                # Identify possible causes
    FUTURE_STATE = "future_state"           # Explore potential future states
    ANOMALY = "anomaly"                     # Explain anomalous observations
    DESIGN_SPACE = "design_space"           # Design option exploration
    COUNTERFACTUAL_ANALYSIS = "counterfactual_analysis"  # Counterfactual scenarios


class HypotheticalLifecycle(Enum):
    """Hypothetical reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVATION_COLLECTION = "observation_collection"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    ASSUMPTION_ANALYSIS = "assumption_analysis"
    POSSIBILITY_EXPANSION = "possibility_expansion"
    SCENARIO_CONSTRUCTION = "scenario_construction"
    HYPOTHESIS_COMPARISON = "hypothesis_comparison"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class HypotheticalDescriptor:
    """
    Descriptor exposing hypothetical reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal and mode
        - Lifecycle state
        - Constraints and requirements
        - Provenance tracking
    
    Descriptors allow inspection of what hypothetical reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    hypothetical_mode: HypotheticalMode       # What kind of hypothetical reasoning?
    reasoning_goal: str                       # What are we exploring?
    
    # Lifecycle state
    lifecycle_state: HypotheticalLifecycle = HypotheticalLifecycle.CREATED
    
    # Constraints and requirements
    confidence_threshold: float = 0.5         # Minimum confidence for candidate consideration
    min_hypotheses_required: int = 1          # Minimum hypotheses to generate
    max_candidates: int = 20                  # Maximum candidates to consider
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    required_assumptions: Tuple[str, ...] = ()   # Explicit assumptions required
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did hypothetical reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if hypothetical reasoning completed."""
        return self.lifecycle_state == HypotheticalLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if hypothetical reasoning failed."""
        return self.lifecycle_state == HypotheticalLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        hypothetical_mode: HypotheticalMode = HypotheticalMode.EXPLORATORY,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> HypotheticalDescriptor:
        """Create a new hypothetical reasoning descriptor."""
        return cls(
            descriptor_id=f"hypothetical:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            hypothetical_mode=hypothetical_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: HypotheticalLifecycle) -> HypotheticalDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == HypotheticalLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class HypothesisSessionIdentity:
    """
    Immutable identity for a hypothesis session.
    
    Allows replay and verification of hypothetical reasoning results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> HypothesisSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "HypotheticalDescriptor",
    "HypothesisSessionIdentity",
    "HypotheticalMode",
    "HypotheticalLifecycle",
]