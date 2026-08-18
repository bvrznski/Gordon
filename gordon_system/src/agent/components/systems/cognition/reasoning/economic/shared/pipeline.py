# Economic Pipeline - Phase 7.48 Part 1
# ======================================

"""
Economic Pipeline.

Canonical flow:
    Resource Assessment
        ↓
    Scarcity Analysis
        ↓
    Valuation
        ↓
    Opportunity Cost Analysis
        ↓
    Allocation Optimization
        ↓
    Incentive Evaluation
        ↓
    Validation
        ↓
    Publication

Every stage remains independently observable.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from gordon_system.src.agent.components.systems.cognition.reasoning.economic.shared.descriptor import (
    EconomicLifecycleState,
)


class PipelineStage(Enum):
    """Pipeline stages in economic reasoning."""
    
    RESOURCE_ASSESSMENT = "resource_assessment"     # What resources are available?
    SCARCITY_ANALYSIS = "scarcity_analysis"         # Are resources scarce?
    VALUATION = "valuation"                         # How are resources valued?
    OPPORTUNITY_COST = "opportunity_cost"           # What's the opportunity cost?
    ALLOCATION_OPTIMIZATION = "allocation_optimization"  # Best allocation found?
    INCENTIVE_EVALUATION = "incentive_evaluation"   # Are incentives aligned?
    VALIDATION = "validation"                       # Is the solution valid?
    PUBLICATION = "publication"                     # Final results ready


@dataclass(frozen=True)
class PipelineStageResult:
    """Result from a single pipeline stage."""
    
    stage: PipelineStage
    success: bool
    output: Optional[Dict[str, Any]] = None
    diagnostics: List[Dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class EconomicPipeline:
    """
    Complete economic reasoning execution flow.
    
    A pipeline contains:
        - Pipeline identity and lifecycle state
        - Optimization strategy used
        - Results from each stage
        - Final allocation
        - Provenance tracking
    
    Pipelines enable inspection of the reasoning process without re-execution.
    """
    
    # Identity
    pipeline_id: str                  # Unique pipeline identifier
    semantic_identity: str            # Semantic identity for this reasoning task
    
    # Lifecycle
    lifecycle_state: EconomicLifecycleState = EconomicLifecycleState.CREATED
    optimization_strategy: str = "standard"  # e.g., "linear_programming", "dynamic_programming"
    
    # Results
    stage_results: Dict[PipelineStage, PipelineStageResult] = field(default_factory=dict)
    resulting_allocation: Optional[Dict[str, Any]] = None
    
    # Diagnostics and metadata
    diagnostics: List[Dict[str, str]] = field(default_factory=list)
    timestamps: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        optimization_strategy: str = "standard",
    ) -> EconomicPipeline:
        """Create a new economic pipeline."""
        return cls(
            pipeline_id=f"pipeline:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            optimization_strategy=optimization_strategy,
        )
    
    def record_stage(
        self,
        stage: PipelineStage,
        success: bool,
        output: Optional[Dict[str, Any]] = None,
        diagnostics: Optional[List[Dict[str, str]]] = None,
    ) -> EconomicPipeline:
        """Record a pipeline stage result."""
        return dataclass_replace(
            self,
            stage_results={**self.stage_results, stage: PipelineStageResult(
                stage=stage,
                success=success,
                output=output,
                diagnostics=diagnostics or [],
            )},
            lifecycle_state=EconomicLifecycleState.COMPLETED if stage == PipelineStage.PUBLICATION else self.lifecycle_state,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "EconomicPipeline",
    "PipelineStage",
    "PipelineStageResult",
]