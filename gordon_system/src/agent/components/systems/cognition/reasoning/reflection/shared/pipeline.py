# Reflection Pipeline - Phase 7.28
# ==================================

"""
Reflection Pipeline orchestrates the reflection reasoning process.

Canonical pipeline flow:
Experience Collection -> Experience Synthesis -> Self-Explanation
-> Lesson Extraction -> Consolidation Planning -> Validation -> Publication

Every stage remains independently observable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ReflectionStage(Enum):
    """Pipeline stages in reflection reasoning."""
    
    EXPERIENCE_COLLECTION = "experience_collection"   # Collect completed sessions
    SYNTHESIS = "synthesis"                            # Experience synthesis
    EXPLANATION = "explanation"                        # Self-explanation
    LESSON_EXTRACTION = "lesson_extraction"            # Lesson extraction
    CONSOLIDATION_PLANNING = "consolidation_planning"  # Consolidation planning
    VALIDATION = "validation"                          # Validation
    PUBLICATION = "publication"                        # Publication


@dataclass(frozen=True)
class ReflectionPipeline:
    """
    Pipeline orchestrating reflection reasoning.
    
    A pipeline contains:
        - Pipeline identity and strategy
        - Current stage of execution
        - Results from each stage
        - Provenance tracking
    
    The pipeline remains independently observable at each stage.
    """
    
    # Identity
    pipeline_id: str                          # Unique pipeline identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Pipeline configuration
    reflection_strategy: str                  # Strategy for reflection
    
    # Current state
    current_stage: ReflectionStage = ReflectionStage.EXPERIENCE_COLLECTION
    
    # Stage results (can be None if not yet completed)
    experience_collection_result: Optional[Dict[str, Any]] = None
    synthesis_result: Optional[Dict[str, Any]] = None
    explanation_result: Optional[Dict[str, Any]] = None
    lesson_extraction_result: Optional[Dict[str, Any]] = None
    consolidation_planning_result: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    
    # Pipeline-level metadata
    total_stages: int = 7                     # Total number of stages
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_pipeline_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did pipeline originate?
    
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
        """Check if pipeline completed."""
        return self.current_stage == ReflectionStage.PUBLICATION
    
    @property
    def progress(self) -> float:
        """Calculate completion progress (0.0 to 1.0)."""
        stage_order = [
            ReflectionStage.EXPERIENCE_COLLECTION,
            ReflectionStage.SYNTHESIS,
            ReflectionStage.EXPLANATION,
            ReflectionStage.LESSON_EXTRACTION,
            ReflectionStage.CONSOLIDATION_PLANNING,
            ReflectionStage.VALIDATION,
            ReflectionStage.PUBLICATION,
        ]
        try:
            current_idx = stage_order.index(self.current_stage)
            return (current_idx + 1) / len(stage_order)
        except ValueError:
            return 0.0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reflection_strategy: str,
        origin_context: str = "unknown",
        source_pipeline_id: Optional[str] = None,
    ) -> ReflectionPipeline:
        """Create a new reflection pipeline."""
        return cls(
            pipeline_id=f"reflection_pipeline:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reflection_strategy=reflection_strategy,
            origin_context=origin_context,
            source_pipeline_id=source_pipeline_id,
            started_at_utc=time.time(),
        )
    
    def advance_stage(self, next_stage: ReflectionStage) -> ReflectionPipeline:
        """Return a copy with updated stage."""
        return dataclass_replace(
            self,
            current_stage=next_stage,
        )
    
    def record_result(
        self,
        stage: ReflectionStage,
        result: Dict[str, Any],
    ) -> ReflectionPipeline:
        """Record result for a completed stage."""
        result_field = f"{stage.value}_result"
        return dataclass_replace(
            self,
            **{result_field: result},
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ReflectionPipeline",
    "ReflectionStage",
]