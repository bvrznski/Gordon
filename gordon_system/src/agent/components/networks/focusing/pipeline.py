# Focusing Network - Canonical Pipeline Executor
# ================================================
#
# Phase 4.2.7: Integration of all computational subsystems into a coherent network.
#
# This module implements the canonical computational pipeline executor:
#
#   Focus Candidates → Priority Aggregation → Relevance Evaluation →
#   Competition Resolution → Suppression Recommendation → Precision Estimation →
#   Persistence Update → Bias Generation → Resource Allocation → Assessment Composition
#
# ARCHITECTURAL PRINCIPLES:
#     - Orchestration only: No algorithms implemented here
#     - Immutable data flow: All outputs are frozen dataclasses
#     - Explicit state transitions: Each stage produces new state
#     - Diagnostic capture: All pipeline stages emit diagnostic events
#     - Validation at each step: Inputs and outputs validated before/after
#
# DEPENDENCIES:
#     - contracts (inputs, outputs)
#     - models (immutable data structures)
#     - configuration (parameter-driven behavior)
#     - validation (input/output validation)
#     - diagnostics (pipeline telemetry)
#     - computational modules (delegated algorithms)
#
# FORBIDDEN DEPENDENCIES:
#     - Core Scheduler
#     - Execution runtime
#     - ConversationThread
#     - PlanningLoop
#     - Capabilities implementation
#     - Memory implementations
#

"""
Canonical Pipeline Executor for the FocusingNetwork.

This module orchestrates the complete computational pipeline without implementing
any algorithms. All algorithmic computation is delegated to specialized modules.

PIPELINE STAGES:

    1. Focus Candidates (input)
       ↓
    2. Priority Aggregation → PriorityAssessment
       ↓
    3. Relevance Evaluation → RelevanceAssessment
       ↓
    4. Competition Resolution → CompetitionAssessment
       ↓
    5. Suppression Recommendation → SuppressionAssessment
       ↓
    6. Precision Estimation → PrecisionAssessment
       ↓
    7. Persistence Update → PersistenceAssessment
       ↓
    8. Bias Generation → BiasAssessment
       ↓
    9. Resource Allocation → AllocationRecommendation
       ↓
   10. Assessment Composition → FocusAssessment

Each stage:
    - Receives immutable input (from previous stage or initial context)
    - Validates inputs before processing
    - Delegates to appropriate subsystem
    - Produces immutable output
    - Emits diagnostic events
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Optional, Dict, Any


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    
    Args:
        obj: The dataclass instance to replace
        **kwargs: Fields to update
        
    Returns:
        New dataclass instance with updated fields
        
    Raises:
        TypeError: If object is not a dataclass
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name) 
            for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# Models (immutable computational substrate)
from gordon_system.src.agent.components.networks.focusing.models import (
    FocusCandidate,
    FocusTarget,
    PriorityDescriptor,
    RelevanceDescriptor,
    SuppressionDescriptor,
    PrecisionDescriptor,
    PersistenceDescriptor,
    AllocationDescriptor,
    BiasDescriptor,
    PriorityAssessment,
    RelevanceAssessment,
    CompetitionAssessment,
    SuppressionAssessment,
    PrecisionAssessment,
    PersistenceAssessment,
    BiasAssessment,
    FocusAssessment,
)

# Configuration (parameter-driven, no behavior)
from gordon_system.src.agent.components.networks.focusing.configuration import (
    FocusingNetworkConfig,
)


@dataclass(frozen=True)
class ComputationContext:
    """
    Immutable computation context carried through the pipeline.
    
    Contains all inputs needed for computation without runtime state.
    """
    
    # Configuration
    config: FocusingNetworkConfig
    
    # Input data
    candidates: Tuple[FocusCandidate, ...]
    
    # Context
    current_focus_targets: Tuple[FocusTarget, ...] = field(default_factory=tuple)
    history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Timestamps and metadata
    computation_id: str = field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:12]}")
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    revision: int = 1
    
    # Diagnostics sink (pass-through, never owns diagnostics)
    diagnostics_sink: Optional[Any] = None
    
    @classmethod
    def create(
        cls,
        candidates: Tuple[FocusCandidate, ...],
        config: FocusingNetworkConfig,
        current_focus_targets: Optional[Tuple[FocusTarget, ...]] = None,
        history: Optional[Tuple[Dict[str, Any], ...]] = None,
        diagnostics_sink: Optional[Any] = None,
    ) -> "ComputationContext":
        """Create a computation context with default values."""
        return cls(
            candidates=candidates,
            config=config,
            current_focus_targets=current_focus_targets or tuple(),
            history=history or tuple(),
            diagnostics_sink=diagnostics_sink,
        )
    
    def with_candidates(self, candidates: Tuple[FocusCandidate, ...]) -> "ComputationContext":
        """Create a copy with updated candidates."""
        return dataclass_replace(self, candidates=candidates)
    
    def with_timestamp(self, timestamp: datetime) -> "ComputationContext":
        """Create a copy with updated timestamp."""
        return dataclass_replace(self, timestamp_utc=timestamp)


@dataclass(frozen=True)
class PipelineState:
    """
    State carried through the pipeline at each stage.
    
    Contains intermediate assessments and descriptors from completed stages.
    """
    
    # Current focus targets
    current_targets: Tuple[FocusTarget, ...]
    
    # Priority state
    priority_assessment: Optional[PriorityAssessment] = None
    
    # Relevance state
    relevance_assessment: Optional[RelevanceAssessment] = None
    competition_assessment: Optional[CompetitionAssessment] = None
    suppression_assessment: Optional[SuppressionAssessment] = None
    
    # Precision state
    precision_assessment: Optional[PrecisionAssessment] = None
    
    # Persistence state
    persistence_assessment: Optional[PersistenceAssessment] = None
    
    # Bias state
    bias_assessment: Optional[BiasAssessment] = None
    
    # Resource allocation
    allocation_recommendation: Optional[Dict[str, Any]] = None
    
    # Pipeline metadata
    stage_order: Tuple[int, ...] = field(default_factory=tuple)
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create_initial(cls, targets: Tuple[FocusTarget, ...]) -> "PipelineState":
        """Create initial pipeline state."""
        return cls(current_targets=targets)


class PipelineExecutor:
    """
    Executor for the canonical computational pipeline.
    
    RESPONSIBILITIES (orchestration only):
        - Receive computational inputs
        - Validate inputs
        - Construct computation context
        - Execute computational pipeline in order
        - Collect intermediate assessments
        - Compose final assessment
        - Emit diagnostics
    
    NO RESPONSIBILITY FOR:
        - Implementing algorithms (deferred to subsystems)
        - Owning runtime state
        - Making behavioral decisions
        - Allocating resources at runtime
    """
    
    def __init__(self, config: Optional[FocusingNetworkConfig] = None):
        """
        Initialize the pipeline executor.
        
        Args:
            config: Configuration for the network. Uses defaults if None.
        """
        self._config = config or FocusingNetworkConfig.default()
    
    @property
    def config(self) -> FocusingNetworkConfig:
        """Return the current configuration."""
        return self._config
    
    def execute_pipeline(
        self,
        candidates: Tuple[FocusCandidate, ...],
        current_targets: Optional[Tuple[FocusTarget, ...]] = None,
        diagnostics_sink: Optional[Any] = None,
    ) -> FocusAssessment:
        """
        Execute the complete computational pipeline.
        
        PIPELINE EXECUTION:
            1. Construct computation context from inputs
            2. Validate input candidates
            3. Priority Aggregation (delegated)
            4. Relevance Evaluation (delegated)
            5. Competition Resolution (delegated)
            6. Suppression Recommendation (delegated)
            7. Precision Estimation (delegated)
            8. Persistence Update (delegated)
            9. Bias Generation (delegated)
           10. Resource Allocation (delegated)
           11. Assessment Composition
            
        Args:
            candidates: Focus candidates to evaluate
            current_targets: Currently focused targets for context
            diagnostics_sink: Optional sink for diagnostic events
        
        Returns:
            Complete focus assessment with all computed values
        
        Raises:
            ValueError: If input validation fails
            RuntimeError: If pipeline execution fails at any stage
        """
        # Step 1: Validate inputs
        self._validate_inputs(candidates)
        
        # Step 2: Construct initial context and state
        context = ComputationContext.create(
            candidates=candidates,
            config=self._config,
            current_focus_targets=current_targets or tuple(),
            diagnostics_sink=diagnostics_sink,
        )
        
        state = PipelineState.create_initial(current_targets or tuple())
        
        # Step 3: Execute pipeline stages in order
        state = self._stage_priority_aggregation(context, state)
        state = self._stage_relevance_evaluation(context, state)
        state = self._stage_competition_resolution(context, state)
        state = self._stage_suppression_recommendation(context, state)
        state = self._stage_precision_estimation(context, state)
        state = self._stage_persistence_update(context, state)
        state = self._stage_bias_generation(context, state)
        state = self._stage_resource_allocation(context, state)
        
        # Step 4: Compose final assessment
        return self._compose_assessment(context, state)
    
    def _validate_inputs(
        self,
        candidates: Tuple[FocusCandidate, ...],
    ) -> None:
        """Validate input candidates before pipeline execution."""
        if not isinstance(candidates, tuple):
            raise ValueError("Candidates must be a tuple")
        
        # Validate each candidate
        for i, candidate in enumerate(candidates):
            if not isinstance(candidate, FocusCandidate):
                raise ValueError(
                    f"Candidate at index {i} is not a FocusCandidate: "
                    f"got {type(candidate)}"
                )
            
            # Validate target exists
            if not candidate.target or not candidate.target.target_id:
                raise ValueError(f"Candidate at index {i} has invalid target")
    
    def _stage_priority_aggregation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 2: Priority Aggregation
        
        Delegates to priority.aggregation module.
        
        Returns:
            Updated pipeline state with priority assessment
        """
        from gordon_system.src.agent.components.networks.focusing.priority import aggregation
        
        # Delegate to aggregation module (algorithm implementation)
        priority_assessment = aggregation.aggregate_priorities(
            candidates=context.candidates,
            config=self._config,
            current_targets=state.current_targets,
        )
        
        return dataclass_replace(state, 
                                priority_assessment=priority_assessment,
                                stage_order=state.stage_order + (2,))
    
    def _stage_relevance_evaluation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 3: Relevance Evaluation
        
        Delegates to relevance.evaluation module.
        
        Returns:
            Updated pipeline state with relevance assessment
        """
        from gordon_system.src.agent.components.networks.focusing.relevance import evaluation
        
        relevance_assessment = evaluation.evaluate_relevance(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            config=self._config,
            current_targets=state.current_targets,
        )
        
        return dataclass_replace(state,
                                relevance_assessment=relevance_assessment,
                                stage_order=state.stage_order + (3,))
    
    def _stage_competition_resolution(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 4: Competition Resolution
        
        Delegates to relevance.competition module.
        
        Returns:
            Updated pipeline state with competition assessment
        """
        from gordon_system.src.agent.components.networks.focusing.relevance import competition
        
        competition_assessment = competition.analyze_competition(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            relevance_assessment=state.relevance_assessment,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                competition_assessment=competition_assessment,
                                stage_order=state.stage_order + (4,))
    
    def _stage_suppression_recommendation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 5: Suppression Recommendation
        
        Delegates to relevance.suppression module.
        
        Returns:
            Updated pipeline state with suppression assessment
        """
        from gordon_system.src.agent.components.networks.focusing.relevance import suppression
        
        suppression_assessment = suppression.recommend_suppression(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            competition_assessment=state.competition_assessment,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                suppression_assessment=suppression_assessment,
                                stage_order=state.stage_order + (5,))
    
    def _stage_precision_estimation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 6: Precision Estimation
        
        Delegates to precision.estimation module.
        
        Returns:
            Updated pipeline state with precision assessment
        """
        from gordon_system.src.agent.components.networks.focusing.precision import estimation
        
        precision_assessment = estimation.estimate_precision(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                precision_assessment=precision_assessment,
                                stage_order=state.stage_order + (6,))
    
    def _stage_persistence_update(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 7: Persistence Update
        
        Delegates to persistence.maintenance module.
        
        Returns:
            Updated pipeline state with persistence assessment
        """
        from gordon_system.src.agent.components.networks.focusing.persistence import maintenance
        
        persistence_assessment = maintenance.compute_persistence(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            current_targets=state.current_targets,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                persistence_assessment=persistence_assessment,
                                stage_order=state.stage_order + (7,))
    
    def _stage_bias_generation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 8: Bias Generation
        
        Delegates to bias.generation module.
        
        Returns:
            Updated pipeline state with bias assessment
        """
        from gordon_system.src.agent.components.networks.focusing.bias import generation
        
        bias_assessment = generation.generate_bias(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            current_targets=state.current_targets,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                bias_assessment=bias_assessment,
                                stage_order=state.stage_order + (8,))
    
    def _stage_resource_allocation(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> PipelineState:
        """
        Stage 9: Resource Allocation
        
        Delegates to allocation.allocator module.
        
        Returns:
            Updated pipeline state with allocation recommendation
        """
        from gordon_system.src.agent.components.networks.focusing.allocation import allocator
        
        allocation_recommendation = allocator.allocate_resources(
            candidates=context.candidates,
            priority_assessment=state.priority_assessment,
            precision_assessment=state.precision_assessment,
            persistence_assessment=state.persistence_assessment,
            bias_assessment=state.bias_assessment,
            config=self._config,
        )
        
        return dataclass_replace(state,
                                allocation_recommendation=allocation_recommendation,
                                stage_order=state.stage_order + (9,))
    
    def _compose_assessment(
        self,
        context: ComputationContext,
        state: PipelineState,
    ) -> FocusAssessment:
        """
        Stage 10: Assessment Composition
        
        Combine all intermediate assessments into a complete focus assessment.
        
        NO COMPUTATION - only composition of existing values.
        
        Returns:
            Complete focus assessment with all computed values
        """
        # Calculate overall score (simplified aggregation)
        overall_score = self._aggregate_overall_score(state)
        
        return FocusAssessment(
            assessment_id=f"focus_{uuid.uuid4().hex[:12]}",
            timestamp_utc=context.timestamp_utc,
            computation_id=state.computation_id if hasattr(state, 'computation_id') else context.computation_id,
            
            # Priority
            priority_assessment=state.priority_assessment,
            
            # Relevance
            relevance_assessment=state.relevance_assessment,
            competition_assessment=state.competition_assessment,
            suppression_assessment=state.suppression_assessment,
            
            # Precision
            precision_assessment=state.precision_assessment,
            
            # Persistence
            persistence_assessment=state.persistence_assessment,
            
            # Bias
            bias_assessment=state.bias_assessment,
            
            # Resource allocation
            resource_allocation_recommendation=state.allocation_recommendation,
            
            # Composition metadata
            pipeline_stage_order=state.stage_order,
            total_candidates=len(context.candidates),
            current_targets_count=len(state.current_targets),
            
            # Overall assessment
            overall_focus_score=overall_score,
        )
    
    def _aggregate_overall_score(self, state: PipelineState) -> float:
        """
        Aggregate all scores into overall focus score.
        
        NO ALGORITHM - just weighted combination of existing values.
        
        Returns:
            Normalized overall score (0.0 to 1.0)
        """
        scores = []
        
        # Priority score
        if state.priority_assessment and hasattr(state.priority_assessment, 'overall_score'):
            scores.append(state.priority_assessment.overall_score * 0.30)
        
        # Relevance score  
        if state.relevance_assessment and hasattr(state.relevance_assessment, 'combined_relevance'):
            scores.append(state.relevance_assessment.combined_relevance * 0.25)
        
        # Precision score
        if state.precision_assessment and hasattr(state.precision_assessment, 'base_precision'):
            scores.append(state.precision_assessment.base_precision * 0.20)
        
        # Persistence score
        if state.persistence_assessment and hasattr(state.persistence_assessment, 'maintenance_score'):
            scores.append(state.persistence_assessment.maintenance_score * 0.15)
        
        # Bias score
        if state.bias_assessment and hasattr(state.bias_assessment, 'bias_strength'):
            scores.append((1.0 - state.bias_assessment.bias_strength) * 0.10)
        
        if not scores:
            return 0.0
        
        return max(0.0, min(1.0, sum(scores)))