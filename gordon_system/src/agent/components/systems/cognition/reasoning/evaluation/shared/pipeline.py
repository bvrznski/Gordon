# Evaluation Pipeline - Phase 7.23
# ================================

"""
Canonical Evaluation Pipeline for Gordon's Evaluation Reasoning subsystem.

The evaluation pipeline executes:
1. Target Identification
2. Metric Collection
3. Performance Assessment
4. Quality Estimation
5. Objective Verification
6. Cognitive Appraisal
7. Validation
8. Publication

Each stage remains independently observable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class EvaluationStage(Enum):
    """Pipeline stages in the evaluation process."""
    
    TARGET_IDENTIFICATION = "target_identification"
    METRIC_COLLECTION = "metric_collection"
    PERFORMANCE_ASSESSMENT = "performance_assessment"
    QUALITY_ESTIMATION = "quality_estimation"
    OBJECTIVE_VERIFICATION = "objective_verification"
    COGNITIVE_APPRAISAL = "cognitive_appraisal"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class PipelineStageResult:
    """
    Result of a single pipeline stage.
    
    Each result contains:
        - Stage identity
        - Execution status
        - Output data (if successful)
        - Error details (if failed)
        - Timing information
    
    Results remain inspectable for debugging and traceability.
    """
    
    stage: EvaluationStage               # Which stage?
    success: bool                        # Did it succeed?
    output_data: Optional[Dict[str, Any]] = None  # Result data
    error_message: Optional[str] = None           # Error details if failed
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate stage duration."""
        if self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        return time.time() - self.started_at_utc


@dataclass(frozen=True)
class EvaluationPipeline:
    """
    An Evaluation Pipeline executes the canonical evaluation workflow.
    
    A pipeline contains:
        - Pipeline identity
        - Evaluation strategy (how to evaluate)
        - Stage results (progress through pipeline)
        - Overall assessment (final result)
        - Diagnostics and provenance
    
    Pipelines remain deterministic given identical inputs.
    """
    
    # Identity
    pipeline_id: str                    # Unique pipeline identifier
    semantic_identity: str              # Semantic identity for traceability
    
    # Pipeline state
    evaluation_strategy: Dict[str, Any] = field(default_factory=dict)  # Evaluation strategy
    stage_results: List[PipelineStageResult] = field(default_factory=list)
    
    # Final result
    overall_assessment: Optional[str] = None     # Final assessment (success/failure/mixed)
    resulting_metrics: Dict[str, Any] = field(default_factory=dict)  # Aggregated metrics
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    source_pipeline_id: Optional[str] = None
    origin_context: str = "unknown"
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed (all stages executed)."""
        return self.completed_at_utc is not None
    
    @property
    def is_successful(self) -> bool:
        """Check if pipeline succeeded."""
        return self.overall_assessment == "success"
    
    @property
    def stage_count(self) -> int:
        """Return number of stages in this pipeline."""
        return len(EvaluationStage)
    
    @property
    def completed_stages(self) -> int:
        """Count completed stages."""
        return sum(1 for r in self.stage_results if r.success and r.completed_at_utc is not None)
    
    def get_stage_result(self, stage: EvaluationStage) -> Optional[PipelineStageResult]:
        """Get result for a specific stage."""
        for result in self.stage_results:
            if result.stage == stage:
                return result
        return None
    
    def record_stage(
        self,
        stage: EvaluationStage,
        success: bool,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> EvaluationPipeline:
        """Record a stage result and return updated pipeline."""
        new_result = PipelineStageResult(
            stage=stage,
            success=success,
            output_data=output_data,
            error_message=error_message,
            started_at_utc=self.started_at_utc or time.time(),
            completed_at_utc=time.time() if success else None,
        )
        return dataclass_replace(
            self,
            stage_results=list(self.stage_results) + [new_result],
        )
    
    def set_overall_assessment(self, assessment: str, metrics: Dict[str, Any]) -> EvaluationPipeline:
        """Set overall assessment and return updated pipeline."""
        return dataclass_replace(
            self,
            overall_assessment=assessment,
            resulting_metrics=dict(metrics),
            completed_at_utc=time.time() if assessment in ("success", "failure") else None,
        )
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        evaluation_strategy: Optional[Dict[str, Any]] = None,
        origin_context: str = "unknown",
        source_pipeline_id: Optional[str] = None,
    ) -> EvaluationPipeline:
        """Create a new evaluation pipeline."""
        return cls(
            pipeline_id=f"pipeline:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluation_strategy=evaluation_strategy or {},
            origin_context=origin_context,
            source_pipeline_id=source_pipeline_id,
            created_at_utc=time.time(),
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EvaluationStage",
    "PipelineStageResult",
    "EvaluationPipeline",
]