# Internal Consistency - Phase 7.29
# ==================================

"""
Internal Consistency evaluates Gordon's cognitive state consistency.

Consistency determines:
    - Goal consistency
    - Belief consistency
    - Plan consistency
    - Configuration consistency
    - Reasoning consistency
    - Identity consistency

Consistency remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any


@dataclass(frozen=True)
class InternalConsistency:
    """
    Assessment of Gordon's internal cognitive consistency.
    
    A consistency assessment contains:
        - Explicit identity
        - Evaluated domains
        - Consistency metrics
        - Detected conflicts
        - Provenance tracking
    
    Consistency assessments remain independently inspectable.
    """
    
    # Identity
    consistency_id: str                       # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Evaluated domains
    evaluated_domains: Set[str] = field(default_factory=set)  # What was assessed
    
    # Consistency metrics
    overall_consistency_score: float = 1.0    # 0.0 to 1.0
    belief_consistency: float = 1.0           # Belief consistency score
    goal_consistency: float = 1.0             # Goal consistency score
    plan_consistency: float = 1.0             # Plan consistency score
    
    # Detected conflicts
    detected_conflicts: List[Dict[str, Any]] = field(default_factory=list)  # Conflicts found
    conflict_count: int = 0                   # Number of conflicts
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    assessment_strategy: str = "default"      # How was consistency assessed?
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluated_domains: Optional[Set[str]] = None,
        strategy: str = "default",
    ) -> InternalConsistency:
        """Create a new consistency assessment."""
        return cls(
            consistency_id=f"consistency:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_domains=evaluated_domains or set(),
            assessment_strategy=strategy,
        )
    
    def with_conflicts(self, conflicts: List[Dict[str, Any]]) -> InternalConsistency:
        """Return a copy with detected conflicts."""
        return dataclass_replace(
            self,
            detected_conflicts=conflicts,
            conflict_count=len(conflicts),
            overall_consistency_score=max(0.0, 1.0 - len(conflicts) * 0.1),
        )


@dataclass(frozen=True)
class ConsistencyManagement:
    """
    Management of consistency assessment process.
    
    A management object contains:
        - Consistency identity and configuration
        - Current state
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Configuration
    assessment_strategy: str                  # Strategy used
    
    # Current state
    current_stage: str = "initializing"       # Assessment stage
    
    # Results (can be None if not yet completed)
    consistency_result: Optional[InternalConsistency] = None  # Result
    
    # Quality metrics
    quality_score: float = 0.0                # Assessment quality score
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        assessment_strategy: str = "default",
    ) -> ConsistencyManagement:
        """Create a new consistency management."""
        return cls(
            management_id=f"consistency_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            assessment_strategy=assessment_strategy,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "InternalConsistency",
    "ConsistencyManagement",
]