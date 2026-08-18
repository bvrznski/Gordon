# Cognitive Awareness - Phase 7.29
# ================================

"""
Cognitive Awareness evaluates the introspective cognitive state.

Awareness evaluates:
    - Reasoning load
    - Attention focus
    - Resource utilization
    - Execution pressure
    - Uncertainty
    - Confidence distribution

Awareness remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CognitiveAwareness:
    """
    Assessment of Gordon's cognitive awareness state.
    
    Awareness contains:
        - Explicit identity
        - Awareness model (current assessment)
        - Metrics (quantitative measures)
        - State summary
        - Provenance tracking
    
    Awareness remains explicit.
    """
    
    # Identity
    awareness_id: str                         # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Awareness scope
    awareness_scope: Set[str] = field(default_factory=set)  # What is being assessed
    
    # Awareness metrics
    reasoning_load: float = 0.5             # Current reasoning load (0-1)
    attention_focus_score: float = 0.5      # Focus level (0-1)
    resource_utilization: Dict[str, float] = field(default_factory=dict)  # Resource usage
    
    # Confidence distribution
    confidence_distribution: Dict[str, float] = field(default_factory=dict)  # Per-domain confidence
    
    # State summary
    awareness_summary: str = "unknown"      # Human-readable state description
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    observation_source: str = "introspection"
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        awareness_scope: Optional[Set[str]] = None,
        reasoning_load: float = 0.5,
        attention_focus_score: float = 0.5,
        source: str = "introspection",
    ) -> CognitiveAwareness:
        """Create a new cognitive awareness assessment."""
        return cls(
            awareness_id=f"awareness:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            awareness_scope=awareness_scope or set(),
            reasoning_load=reasoning_load,
            attention_focus_score=attention_focus_score,
            observation_source=source,
        )
    
    def with_confidence_distribution(self, distribution: Dict[str, float]) -> CognitiveAwareness:
        """Return a copy with updated confidence distribution."""
        return dataclass_replace(
            self,
            confidence_distribution=distribution,
        )


@dataclass(frozen=True)
class AwarenessManagement:
    """
    Management of awareness assessment process.
    
    A management object contains:
        - Awareness identity and configuration
        - Current state
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Configuration
    awareness_strategy: str                   # Strategy used for assessment
    
    # Current state
    current_stage: str = "initializing"       # Current stage
    
    # Results (can be None if not yet completed)
    awareness_result: Optional[CognitiveAwareness] = None  # Assessment result
    
    # Quality metrics
    quality_score: float = 0.0                # Overall quality score
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        awareness_strategy: str = "default",
    ) -> AwarenessManagement:
        """Create a new awareness management."""
        return cls(
            management_id=f"awareness_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            awareness_strategy=awareness_strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CognitiveAwareness",
    "AwarenessManagement",
]