# Stability Pipeline - Phase 7.26
# ===============================

"""
Canonical Stability Pipeline.

The stability pipeline defines the canonical flow from operational analysis
to publication of stabilization decisions.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class StabilityStage(Enum):
    """Stages in the stability pipeline."""
    
    OPERATIONAL_ANALYSIS = "operational_analysis"
    HOMEOSTASIS_EVALUATION = "homeostasis_evaluation"
    DEGRADATION_ANALYSIS = "degradation_analysis"
    CONTAINMENT_PLANNING = "containment_planning"
    STABILIZATION_PLANNING = "stabilization_planning"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class StabilityPipeline:
    """
    A stability pipeline defines the complete stability analysis flow.
    
    The canonical pipeline:
        
        Operational Analysis
              ↓
        Homeostasis Evaluation
              ↓
        Degradation Analysis
              ↓
        Containment Planning
              ↓
        Stabilization Planning
              ↓
        Validation
              ↓
        Publication
    
    Every stage remains independently observable to support tracing and
    debugging of stability decisions.
    """
    
    pipeline_id: str                          # Unique identifier for this pipeline run
    pipeline_identity: str                    # Semantic identity (stable across runs)
    
    # Pipeline configuration
    stability_strategy: Optional[str] = None  # Strategy to apply
    
    # Stage states
    stage_states: Dict[StabilityStage, Any] = field(default_factory=dict)
    
    # Results from each stage
    operational_analysis_result: Optional[Any] = None
    homeostasis_result: Optional[Any] = None
    degradation_results: List[Any] = field(default_factory=list)
    containment_plans: List[Any] = field(default_factory=list)
    stabilization_plan: Optional[Any] = None
    validation_result: Optional[Any] = None
    
    # Final resulting configuration
    resulting_configuration: Optional[Dict[str, Any]] = None
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: str = "unknown"
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    def record_stage_completion(self, stage: StabilityStage, result: Any) -> StabilityPipeline:
        """Return a new pipeline with the stage result recorded."""
        stage_states = dict(self.stage_states)
        stage_states[stage] = "completed"
        
        return dataclass_replace(
            self,
            stage_states=stage_states,
            completed_at_utc=time.time(),
        )
    
    def get_stage_result(self, stage: StabilityStage) -> Optional[Any]:
        """Get the result for a specific stage."""
        if stage == StabilityStage.OPERATIONAL_ANALYSIS:
            return self.operational_analysis_result
        elif stage == StabilityStage.HOMEOSTASIS_EVALUATION:
            return self.homeostasis_result
        elif stage == StabilityStage.DEGRADATION_ANALYSIS:
            return self.degradation_results
        elif stage == StabilityStage.CONTAINMENT_PLANNING:
            return self.containment_plans
        elif stage == StabilityStage.STABILIZATION_PLANNING:
            return self.stabilization_plan
        elif stage == StabilityStage.VALIDATION:
            return self.validation_result
        elif stage == StabilityStage.PUBLICATION:
            return self.resulting_configuration
        return None
    
    @classmethod
    def create(
        cls,
        pipeline_identity: str,
        stability_strategy: Optional[str] = None,
        provenance: str = "unknown",
    ) -> StabilityPipeline:
        """Create a new stability pipeline."""
        return cls(
            pipeline_id=f"stability-pipeline:{uuid.uuid4().hex[:16]}",
            pipeline_identity=pipeline_identity,
            stability_strategy=stability_strategy,
            provenance=provenance,
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "StabilityPipeline",
    "StabilityStage",
]