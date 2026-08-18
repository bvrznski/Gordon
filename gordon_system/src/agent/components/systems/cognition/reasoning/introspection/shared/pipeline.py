# Introspection Pipeline - Phase 7.29
# ====================================

"""
Introspection Pipeline orchestrates introspection reasoning stages.

Canonical pipeline:
    Internal Observation
        ↓
    Self Model Construction
        ↓
    Cognitive Awareness
        ↓
    Consistency Analysis
        ↓
    Self Diagnostics
        ↓
    Self-State Publication
        ↓
    Validation
        ↓
    Publication

Introspection remains deterministic.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class IntrospectionStage(Enum):
    """Stages in the introspection pipeline."""
    
    INTERNAL_OBSERVATION = "internal_observation"        # Gather internal telemetry
    SELF_MODEL_CONSTRUCTION = "self_model_construction"  # Build self model
    COGNITIVE_AWARENESS = "cognitive_awareness"          # Assess awareness state
    CONSISTENCY_ANALYSIS = "consistency_analysis"        # Evaluate consistency
    SELF_DIAGNOSTICS = "self_diagnostics"                # Run diagnostics
    PUBLISH_SUMMARY = "publish_summary"                  # Publish results
    VALIDATION = "validation"                            # Validate output
    PUBLICATION = "publication"                          # Final publication


@dataclass(frozen=True)
class IntrospectionPipeline:
    """
    Pipeline orchestrating introspection reasoning stages.
    
    A pipeline contains:
        - Explicit identity
        - Introspection strategy
        - Resulting self model
        - Diagnostics summary
        - Provenance tracking
    
    Every stage remains independently observable.
    """
    
    # Identity
    pipeline_id: str                          # Unique pipeline identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Pipeline configuration
    introspection_strategy: str               # Strategy used for introspection
    
    # Results (can be None if not yet completed)
    resulting_self_model: Optional[Any] = None      # SelfModel or None
    awareness_assessment: Optional[Any] = None      # Awareness assessment or None
    consistency_result: Optional[Any] = None        # Consistency evaluation or None
    diagnostic_summary: Optional[Any] = None        # Diagnostic findings or None
    
    # Pipeline progress
    current_stage: IntrospectionStage = IntrospectionStage.INTERNAL_OBSERVATION
    completed_stages: List[IntrospectionStage] = field(default_factory=list)
    
    # Metrics
    total_duration_seconds: float = 0.0       # Total pipeline duration
    stage_durations: Dict[str, float] = field(default_factory=dict)  # Per-stage timing
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # Where did pipeline originate?
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed."""
        return self.current_stage == IntrospectionStage.PUBLICATION
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        introspection_strategy: str = "default",
        source_descriptor_id: Optional[str] = None,
    ) -> IntrospectionPipeline:
        """Create a new introspection pipeline."""
        return cls(
            pipeline_id=f"introspection_pipeline:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            introspection_strategy=introspection_strategy,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def advance_stage(self, new_stage: IntrospectionStage) -> IntrospectionPipeline:
        """Return a copy with updated stage."""
        elapsed = time.time() - (self.started_at_utc or time.time())
        
        return dataclass_replace(
            self,
            current_stage=new_stage,
            completed_stages=self.completed_stages + [new_stage],
            stage_durations={**self.stage_durations, new_stage.value: elapsed},
        )
    
    def with_result(self, stage: IntrospectionStage, result: Any) -> IntrospectionPipeline:
        """Return a copy with result stored for a specific stage."""
        result_attr = f"{stage.value.replace('_', '_').replace('self_model_construction', 'resulting_self_model')}"
        
        # Map stages to result attributes
        stage_to_attr = {
            IntrospectionStage.SELF_MODEL_CONSTRUCTION: "resulting_self_model",
            IntrospectionStage.COGNITIVE_AWARENESS: "awareness_assessment",
            IntrospectionStage.CONSISTENCY_ANALYSIS: "consistency_result",
            IntrospectionStage.SELF_DIAGNOSTICS: "diagnostic_summary",
        }
        
        attr = stage_to_attr.get(stage, None)
        if attr:
            kwargs = {attr: result}
            return dataclass_replace(self, **kwargs)
        
        return self
    
    def mark_completed(self) -> IntrospectionPipeline:
        """Mark pipeline as completed."""
        return dataclass_replace(
            self,
            current_stage=IntrospectionStage.PUBLICATION,
            completed_at_utc=time.time(),
            total_duration_seconds=self.completed_at_utc - (self.started_at_utc or time.time()),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "IntrospectionPipeline",
    "IntrospectionStage",
]