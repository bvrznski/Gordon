# Negotiation Pipeline - Phase 7.42
# ===================================

"""
Canonical Negotiation Pipeline.

The pipeline defines the flow from initial analysis to agreement.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class PipelineStage(Enum):
    """Stages in the negotiation pipeline."""
    
    STAKEHOLDER_ANALYSIS = "stakeholder_analysis"
    INTEREST_ANALYSIS = "interest_analysis"
    CONFLICT_ANALYSIS = "conflict_analysis"
    CONCESSION_GENERATION = "concession_generation"
    AGREEMENT_CONSTRUCTION = "agreement_construction"
    COALITION_EVALUATION = "coalition_evaluation"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class NegotiationResult:
    """Results from a pipeline stage."""
    
    stage: PipelineStage
    result_type: str                    # Type of result (e.g., "stakeholder_analysis")
    result_data: Dict[str, Any]         # Stage-specific results
    confidence: float = 1.0             # Confidence in the result


@dataclass(frozen=True)
class NegotiationPipeline:
    """
    Pipeline from negotiation analysis to agreement.
    
    A pipeline contains:
        - Identity of the pipeline
        - Strategy being applied
        - Results from each stage
        - Final agreement (if any)
    
    Pipelines remain independently observable at each stage.
    """
    
    # Identity
    pipeline_identity: str                    # Unique identifier for this pipeline
    
    # Strategy
    negotiation_strategy: str                 # What strategy is being used?
    
    # Stages and results
    stages_executed: Tuple[PipelineStage, ...] = ()      # Order of execution
    stage_results: Tuple[NegotiationResult, ...] = ()     # Results from each stage
    
    # Final agreement
    resulting_agreement: Optional[str] = None               # If completed
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()                       # Any diagnostic info
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed."""
        return PipelineStage.PUBLICATION in self.stages_executed
    
    @classmethod
    def create(cls, negotiation_strategy: str) -> NegotiationPipeline:
        """Create a new pipeline."""
        return cls(
            pipeline_identity=f"pipeline:{uuid.uuid4().hex[:16]}",
            negotiation_strategy=negotiation_strategy,
        )
    
    def with_result(self, result: NegotiationResult) -> NegotiationPipeline:
        """Add a stage result to the pipeline."""
        return dataclass_replace(
            self,
            stages_executed=self.stages_executed + (result.stage,),
            stage_results=self.stage_results + (result,),
        )
    
    def mark_completed(self) -> NegotiationPipeline:
        """Mark pipeline as completed."""
        return dataclass_replace(
            self,
            completed_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "NegotiationPipeline",
    "PipelineStage",
    "NegotiationResult",
]