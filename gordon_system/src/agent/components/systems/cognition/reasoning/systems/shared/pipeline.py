# System Pipeline - Phase 7.38
# ============================

"""
Canonical System Pipeline.

Canonical pipeline:
    System Decomposition
    ↓
    Topology Construction
    ↓
    Interaction Analysis
    ↓
    Emergence Analysis
    ↓
    Feedback Analysis
    ↓
    Stability Analysis
    ↓
    Validation
    ↓
    Publication

Systems Reasoning remains deterministic.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto


class PipelineStage(Enum):
    """Pipeline stages for systems reasoning."""
    
    SYSTEM_DECOMPOSITION = "system_decomposition"
    TOPOLOGY_CONSTRUCTION = "topology_construction"
    INTERACTION_ANALYSIS = "interaction_analysis"
    EMERGENCE_ANALYSIS = "emergence_analysis"
    FEEDBACK_ANALYSIS = "feedback_analysis"
    STABILITY_ANALYSIS = "stability_analysis"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class SystemPipeline:
    """
    Pipeline configuration for systems reasoning.
    
    The pipeline defines the flow of analysis from system decomposition
    through to final publication of results.
    """
    
    # Identity
    pipeline_id: str                            # Unique identifier
    
    # Modeling strategy
    modeling_strategy: str                      # e.g., "bottom-up", "top-down", "mixed"
    
    # Pipeline configuration
    stages: List[PipelineStage] = field(default_factory=lambda: [
        PipelineStage.SYSTEM_DECOMPOSITION,
        PipelineStage.TOPOLOGY_CONSTRUCTION,
        PipelineStage.INTERACTION_ANALYSIS,
        PipelineStage.EMERGENCE_ANALYSIS,
        PipelineStage.FEEDBACK_ANALYSIS,
        PipelineStage.STABILITY_ANALYSIS,
        PipelineStage.VALIDATION,
        PipelineStage.PUBLICATION,
    ])
    
    # Results from each stage
    stage_results: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: List[str] = field(default_factory=list)
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @classmethod
    def create(
        cls,
        modeling_strategy: str = "mixed",
        stages: Optional[List[PipelineStage]] = None,
    ) -> SystemPipeline:
        """Create a new system pipeline."""
        return cls(
            pipeline_id=f"pipeline:{uuid.uuid4().hex[:16]}",
            modeling_strategy=modeling_strategy,
            stages=stages or [
                PipelineStage.SYSTEM_DECOMPOSITION,
                PipelineStage.TOPOLOGY_CONSTRUCTION,
                PipelineStage.INTERACTION_ANALYSIS,
                PipelineStage.EMERGENCE_ANALYSIS,
                PipelineStage.FEEDBACK_ANALYSIS,
                PipelineStage.STABILITY_ANALYSIS,
                PipelineStage.VALIDATION,
                PipelineStage.PUBLICATION,
            ],
        )
    
    def record_result(self, stage: PipelineStage, result: Any) -> SystemPipeline:
        """Return a new pipeline with the stage result recorded."""
        return dataclass_replace(
            self,
            stage_results={**self.stage_results, stage.value: result},
        )
    
    def add_diagnostic(self, diagnostic: str) -> SystemPipeline:
        """Return a new pipeline with the diagnostic added."""
        return dataclass_replace(
            self,
            diagnostics=self.diagnostics + [diagnostic],
        )
    
    @property
    def current_stage(self) -> Optional[PipelineStage]:
        """Get the first incomplete stage, if any."""
        for stage in self.stages:
            if stage.value not in self.stage_results:
                return stage
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if all pipeline stages have been completed."""
        return len(self.stage_results) == len(self.stages)


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SystemPipeline",
    "PipelineStage",
]