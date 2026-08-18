# Adaptation Pipeline - Phase 7.25
# ================================

"""
Canonical Adaptation Pipeline.

The adaptation pipeline defines the canonical flow from context analysis to
publication of adapted configurations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AdaptationStage(Enum):
    """Stages in the adaptation pipeline."""
    
    CONTEXT_ANALYSIS = "context_analysis"
    CANDIDATE_GENERATION = "candidate_generation"
    BEHAVIOR_ADAPTATION = "behavior_adaptation"
    CONFIGURATION_REFINEMENT = "configuration_refinement"
    ADAPTATION_INTEGRATION = "adaptation_integration"
    ROLLBACK_PREPARATION = "rollback_preparation"
    VALIDATION = "validation"
    PUBLICATION = "publication"


@dataclass(frozen=True)
class AdaptationPipeline:
    """
    Pipeline defining the canonical adaptation flow.
    
    Canonical pipeline stages:
        
        Context Analysis
            ↓
        Candidate Generation
            ↓
        Behavior Adaptation
            ↓
        Configuration Refinement
            ↓
        Integration
            ↓
        Rollback Preparation
            ↓
        Validation
            ↓
        Publication
    
    Every stage remains independently observable.
    """
    
    # Identity
    pipeline_identity: str                 # Unique pipeline identifier
    
    # Strategy
    adaptation_strategy: str               # How adaptations are determined
    
    # Resulting state
    resulting_configuration: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics per stage
    stage_diagnostics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # Stage tracking
    completed_stages: List[AdaptationStage] = field(default_factory=list)
    failed_stages: List[Tuple[AdaptationStage, str]] = field(default_factory=list)
    
    @property
    def is_completed(self) -> bool:
        """Check if all stages completed."""
        return AdaptationStage.PUBLICATION in self.completed_stages
    
    @property
    def success_rate(self) -> float:
        """Calculate stage success rate."""
        total = len(self.completed_stages) + len(self.failed_stages)
        if total == 0:
            return 1.0
        return len(self.completed_stages) / total
    
    @classmethod
    def create(
        cls,
        adaptation_strategy: str,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> AdaptationPipeline:
        """Create a new adaptation pipeline."""
        return cls(
            pipeline_identity=f"pipeline:{uuid.uuid4().hex[:16]}",
            adaptation_strategy=adaptation_strategy,
            provenance=provenance or {},
        )
    
    def record_stage_completion(self, stage: AdaptationStage, diagnostics: Optional[Dict[str, Any]] = None) -> AdaptationPipeline:
        """Record that a stage completed successfully."""
        new_diagnostics = {**self.stage_diagnostics}
        if diagnostics:
            new_diagnostics[stage.value] = diagnostics
        return dataclass_replace(
            self,
            completed_stages=self.completed_stages + [stage],
            stage_diagnostics=new_diagnostics,
        )
    
    def record_stage_failure(self, stage: AdaptationStage, error_message: str) -> AdaptationPipeline:
        """Record that a stage failed."""
        return dataclass_replace(
            self,
            failed_stages=self.failed_stages + [(stage, error_message)],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AdaptationPipeline",
    "AdaptationStage",
]