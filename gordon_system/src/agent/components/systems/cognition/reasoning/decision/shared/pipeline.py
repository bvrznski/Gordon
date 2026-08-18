# Decision Pipeline - Phase 7.41
# ==============================

"""
Canonical Decision Pipeline Contract.

The canonical pipeline:

Alternative Collection
    ↓
Constraint Evaluation
    ↓
Utility Estimation
    ↓
Tradeoff Analysis
    ↓
Dominance Analysis
    ↓
Commitment Selection
    ↓
Validation
    ↓
Publication

Every stage remains independently observable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PipelineStage(Enum):
    """Stages in the decision pipeline."""
    
    ALTERNATIVE_COLLECTION = "alternative_collection"
    CONSTRAINT_EVALUATION = "constraint_evaluation"
    UTILITY_ESTIMATION = "utility_estimation"
    TRADEOFF_ANALYSIS = "tradeoff_analysis"
    DOMINANCE_ANALYSIS = "dominance_analysis"
    COMMITMENT_SELECTION = "commitment_selection"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class PipelineStageResult:
    """Result of a pipeline stage."""
    
    stage: PipelineStage
    success: bool
    findings: Tuple[str, ...] = ()
    errors: Tuple[str, ...] = ()
    duration_seconds: float = 0.0


@dataclass(frozen=True)
class DecisionPipeline:
    """
    A decision pipeline representing the full reasoning process.
    
    The canonical flow:
        Alternative Collection -> Constraint Evaluation -> Utility Estimation ->
        Tradeoff Analysis -> Dominance Analysis -> Commitment Selection ->
        Validation -> Publication
    
    Every stage remains independently observable.
    """
    
    # Identity
    pipeline_id: str                          # Unique identifier
    decision_set_id: str                      # Reference to the decision set being processed
    
    # Pipeline strategy
    decision_strategy: str = "standard"       # standard, fast, thorough, adaptive
    
    # Stage results
    stage_results: Tuple[PipelineStageResult, ...] = ()
    
    # Final output
    committed_decision: Optional[str] = None  # The selected alternative
    rejected_alternatives: Tuple[str, ...] = ()  # Alternatives not chosen
    
    # Diagnostics
    total_duration_seconds: float = 0.0       # Total pipeline duration
    stages_executed: int = 0                  # Number of completed stages
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        """Check if pipeline completed all stages."""
        return self.stages_executed == len(PipelineStage)
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of stage executions."""
        if not self.stage_results:
            return 0.0
        successful = sum(1 for r in self.stage_results if r.success)
        return successful / len(self.stage_results)
    
    def get_stage_result(self, stage: PipelineStage) -> Optional[PipelineStageResult]:
        """Get result for a specific stage."""
        for result in self.stage_results:
            if result.stage == stage:
                return result
        return None
    
    @classmethod
    def create(
        cls,
        decision_set_id: str,
        decision_strategy: str = "standard",
    ) -> DecisionPipeline:
        """Create a new pipeline instance."""
        return cls(
            pipeline_id=f"decision_pipeline:{uuid.uuid4().hex[:16]}",
            decision_set_id=decision_set_id,
            decision_strategy=decision_strategy,
            started_at_utc=time.time(),
        )
    
    def with_stage_result(self, result: PipelineStageResult) -> DecisionPipeline:
        """Add a stage result and return new instance."""
        new_results = list(self.stage_results)
        new_results.append(result)
        return dataclass_replace(
            self,
            stage_results=tuple(new_results),
            stages_executed=self.stages_executed + 1,
            total_duration_seconds=time.time() - (self.started_at_utc or time.time()),
        )
    
    def with_commitment(self, committed: str, rejected: List[str]) -> DecisionPipeline:
        """Record the commitment decision."""
        return dataclass_replace(
            self,
            committed_decision=committed,
            rejected_alternatives=tuple(rejected),
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DecisionPipeline",
    "PipelineStage",
    "PipelineStageResult",
]