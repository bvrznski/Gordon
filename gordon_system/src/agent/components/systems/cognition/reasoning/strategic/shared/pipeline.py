# Strategic Pipeline - Phase 7.37 Part 2
# ======================================

"""
Strategic Pipeline implementation for Phase 7.37.

This module implements the canonical strategic pipeline flow:

    Mission Analysis
         ↓
    Objective Analysis
         ↓
    Resource Analysis
         ↓
    Opportunity Analysis
         ↓
    Portfolio Construction
         ↓
    Strategy Evaluation
         ↓
    Validation
         ↓
    Publication

Every stage remains independently observable.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class PipelineStage(Enum):
    """Pipeline stages in the canonical strategic reasoning flow."""
    
    MISSION_ANALYSIS = "mission_analysis"
    OBJECTIVE_ANALYSIS = "objective_decomposition"
    RESOURCE_ANALYSIS = "resource_allocation"
    OPPORTUNITY_ANALYSIS = "opportunity_evaluation"
    PORTFOLIO_CONSTRUCTION = "portfolio_construction"
    STRATEGY_EVALUATION = "strategy_evaluation"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class PipelineIdentity:
    """Unique identifier for a strategic pipeline execution."""
    
    pipeline_id: str
    session_identity: str       # Related strategic session


@dataclass(frozen=True)
class PipelineResult:
    """
    Result of a single pipeline stage.
    
    Every stage produces observable output.
    """
    
    result_id: str
    stage: PipelineStage
    timestamp_utc: float
    status: str                 # "success", "pending", "failed"
    data: Dict[str, Any]
    diagnostics: Tuple[str, ...]


@dataclass(frozen=True)
class StrategicPipeline:
    """
    Complete strategic pipeline execution.
    
    LAW: STRATEGIC-PIPELINE - Every stage remains independently observable.
    """
    
    pipeline_identity: PipelineIdentity
    input_state: Dict[str, Any]     # Initial inputs to the pipeline
    results: Tuple[PipelineResult, ...]
    
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total pipeline duration."""
        if len(self.results) < 2:
            return 0.0
        first_time = min(r.timestamp_utc for r in self.results)
        last_time = max(r.timestamp_utc for r in self.results)
        return last_time - first_time
    
    @property
    def is_completed(self) -> bool:
        """Check if all pipeline stages completed."""
        return all(r.status == "success" for r in self.results)
    
    @property
    def succeeded_stages(self) -> Tuple[PipelineStage, ...]:
        """Get list of successfully completed stages."""
        return tuple(r.stage for r in self.results if r.status == "success")
    
    @property
    def failed_stages(self) -> Tuple[Tuple[PipelineStage, str], ...]:
        """Get list of failed stages with error messages."""
        return tuple((r.stage, r.data.get("error", "unknown")) 
                     for r in self.results if r.status == "failed")
    
    def get_stage_result(self, stage: PipelineStage) -> Optional[PipelineResult]:
        """Get result for a specific stage."""
        for result in self.results:
            if result.stage == stage:
                return result
        return None
    
    @property
    def final_recommendation(self) -> Dict[str, Any]:
        """Extract the final strategic recommendation from the pipeline."""
        publication_result = self.get_stage_result(PipelineStage.PUBLICATION)
        if publication_result and publication_result.data:
            return publication_result.data
        # Fallback to strategy evaluation result
        eval_result = self.get_stage_result(PipelineStage.STRATEGY_EVALUATION)
        if eval_result and eval_result.data:
            return eval_result.data
        return {}


@dataclass(frozen=True)
class PipelineMetrics:
    """
    Metrics about pipeline execution.
    
    Used for observability and optimization.
    """
    
    metrics_id: str
    pipeline_identity: PipelineIdentity
    total_duration_seconds: float
    stages_count: int
    succeeded_stages_count: int
    failed_stages_count: int
    average_stage_duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        """Calculate stage success rate (0.0 to 1.0)."""
        if self.stages_count == 0:
            return 0.0
        return self.succeeded_stages_count / self.stages_count


@dataclass(frozen=True)
class PipelineContext:
    """
    Context that flows through the pipeline.
    
    Contains inputs and intermediate results.
    """
    
    context_id: str
    mission_input: Dict[str, Any]
    objective_set_input: Optional[Dict[str, Any]] = None
    resource_input: Optional[Dict[str, Any]] = None
    opportunity_input: Optional[Dict[str, Any]] = None
    
    @property
    def has_complete_inputs(self) -> bool:
        """Check if all required pipeline inputs are present."""
        return bool(self.mission_input)


@dataclass(frozen=True)
class PipelineObservability:
    """
    Observability data for the strategic pipeline.
    
    Enables inspection of every stage without re-execution.
    """
    
    observability_id: str
    pipeline_identity: PipelineIdentity
    timestamps: Dict[str, float]  # stage -> timestamp mapping
    inputs_log: Tuple[Dict[str, Any], ...]
    outputs_log: Tuple[Dict[str, Any], ...]
    errors_log: Tuple[str, ...]