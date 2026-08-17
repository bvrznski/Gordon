# Strategy Adaptation - Phase 7.13
# ==================================

"""
Canonical Strategy Adaptation definition.

Adaptation responds to runtime conditions by adjusting orchestration
strategies based on observed behavior and feedback.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AdaptationTrigger(Enum):
    """Triggers that cause adaptation."""
    
    FAILURE = "failure"                       # Reasoning failure detected
    TIMEOUT = "timeout"                       # Time budget exceeded
    RESOURCE_PRESSURE = "resource_pressure"   # Resource exhaustion risk
    NEW_EVIDENCE = "new_evidence"             # New evidence arrived
    LOW_CONFIDENCE = "low_confidence"         # Low confidence in results
    GOAL_CHANGE = "goal_change"               # Reasoning goal changed


@dataclass(frozen=True)
class StrategyAdaptation:
    """
    Adaptation of reasoning strategy during execution.
    
    An adaptation contains:
        - Identity and provenance
        - Previous and adapted strategies
        - Adaptation trigger and rationale
        - Provenance tracking
    
    Adaptations preserve previous reasoning history.
    """
    
    # Identity
    adaptation_id: str                      # Unique adaptation identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Trigger
    trigger: AdaptationTrigger              # What triggered adaptation?
    
    # Strategy change
    previous_strategy: str                  # Previous strategy name
    adapted_strategy: str                   # New strategy name
    
    # Rationale
    adaptation_reason: str                  # Why adaptation occurred
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    applied_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate time from trigger to adaptation."""
        if self.applied_at_utc:
            return self.applied_at_utc - self.created_at_utc
        return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        previous_strategy: str,
        adapted_strategy: str,
        trigger: AdaptationTrigger,
        adaptation_reason: str = "",
    ) -> StrategyAdaptation:
        """Create a new strategy adaptation."""
        return cls(
            adaptation_id=f"adaptation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            previous_strategy=previous_strategy,
            adapted_strategy=adapted_strategy,
            trigger=trigger,
            adaptation_reason=adaptation_reason,
            applied_at_utc=time.time(),
        )
    
    def to_applied(self) -> StrategyAdaptation:
        """Mark adaptation as applied."""
        return dataclass_replace(
            self,
            applied_at_utc=time.time(),
        )


@dataclass(frozen=True)
class AdaptiveOrchestration:
    """
    Orchestration with adaptive adjustment capability.
    
    An adaptive orchestration monitors execution and can adjust
    its strategy in response to runtime conditions.
    """
    
    # Identity
    orchestration_id: str                   # Unique orchestration identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Base orchestration
    base_orchestration: Dict[str, Any]      # Original orchestration plan
    
    # Adaptations applied
    adaptations: List[StrategyAdaptation] = field(default_factory=list)
    
    # Current state
    current_strategy: str                   # Current effective strategy
    
    # Monitoring inputs for adaptation
    monitored_metrics: List[str] = field(default_factory=list)  # Metrics to watch
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate orchestration duration."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    def apply_adaptation(
        self,
        adaptation: StrategyAdaptation,
    ) -> AdaptiveOrchestration:
        """Apply an adaptation and return updated orchestration."""
        return dataclass_replace(
            self,
            adaptations=self.adaptations + [adaptation],
            current_strategy=adaptation.adapted_strategy,
        )
    
    def should_adapt(self, trigger: AdaptationTrigger) -> bool:
        """Check if orchestration should adapt based on trigger."""
        # Can be customized per orchestration type
        return True
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        base_orchestration: Dict[str, Any],
        current_strategy: Optional[str] = None,
        monitored_metrics: Optional[List[str]] = None,
    ) -> AdaptiveOrchestration:
        """Create a new adaptive orchestration."""
        if current_strategy is None and base_orchestration:
            current_strategy = "base"
        
        if monitored_metrics is None:
            monitored_metrics = []
        
        return cls(
            orchestration_id=f"adaptive_orch:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            base_orchestration=base_orchestration,
            current_strategy=current_strategy or "base",
            monitored_metrics=monitored_metrics,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StrategyAdaptation",
    "AdaptationTrigger",
    "AdaptiveOrchestration",
]