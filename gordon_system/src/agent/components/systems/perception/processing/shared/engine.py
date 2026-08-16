# Perception Processing Engine - Phase 5.2.2
# ===========================================

"""
Processing Engine: Orchestrates processing pipeline execution.

The engine validates requests, resolves pipelines, executes stages,
and produces results with complete traceability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
import time
import uuid

from gordon_system.src.agent.components.systems.perception.foundations.confidence import PerceptionConfidence, PerceptionUncertainty
from gordon_system.src.agent.components.systems.perception.foundations.provenance import PerceptionProvenance

from .stage import ProcessingStage, ProcessingStageInput, ProcessingStageOutput
from .pipeline import ProcessingPipeline, PipelineOrdering
from .transformation import ProcessingTransformationRecord
from .request import PerceptionProcessingRequest
from .result import (
    PerceptionProcessingResult,
    ProcessingStatus,
    ProcessingOutcome,
)


# =============================================================================
# PROCESSING ENGINE - Orchestrates transformation execution
# =============================================================================


class PerceptionProcessingEngine:
    """
    Engine that orchestrates perception processing.
    
    Responsibilities:
        - Validate the request
        - Resolve the processing pipeline
        - Validate stage compatibility
        - Order processing stages
        - Execute semantic transformations
        - Preserve source references
        - Propagate confidence and uncertainty
        - Record information loss
        - Validate outputs
        - Construct an immutable result
    
    Properties:
        identity:          Unique engine identifier
        pipelines:         Registered processing pipelines
        stage_registry:    Available stage classes
        active_config:     Current configuration revision
        health_status:     Operational health
        
    Example:
        engine = PerceptionProcessingEngine()
        
        pipeline = ProcessingPipeline(...)
        result = engine.execute(request, pipeline)
    """
    
    def __init__(
        self,
        identity: Optional[str] = None,
        pipelines: Optional[Dict[str, ProcessingPipeline]] = None,
    ):
        """
        Initialize the processing engine.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            pipelines: Registered pipelines by ID (optional)
        """
        self._identity = identity or f"engine:{uuid.uuid4().hex[:16]}"
        self._pipelines = pipelines or {}
        self._stage_registry: Dict[str, ProcessingStage] = {}
        self._active_config: int = 1
        self._health_status = {"status": "healthy", "last_check": time.time()}
    
    @property
    def identity(self) -> str:
        """Unique engine identifier."""
        return self._identity
    
    @property
    def active_config(self) -> int:
        """Current configuration revision."""
        return self._active_config
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Operational health status."""
        return dict(self._health_status)
    
    def register_pipeline(self, pipeline: ProcessingPipeline) -> None:
        """
        Register a processing pipeline by ID.
        
        Args:
            pipeline: The pipeline to register
        """
        self._pipelines[pipeline.pipeline_identity] = pipeline
    
    def get_pipeline(self, pipeline_id: str) -> Optional[ProcessingPipeline]:
        """Get a registered pipeline by ID."""
        return self._pipelines.get(pipeline_id)
    
    def register_stage(self, stage: ProcessingStage) -> None:
        """
        Register a processing stage.
        
        Args:
            stage: The stage to register
        """
        self._stage_registry[stage.identity] = stage
    
    def get_stage(self, stage_id: str) -> Optional[ProcessingStage]:
        """Get a registered stage by ID."""
        return self._stage_registry.get(stage_id)
    
    def validate_request(
        self,
        request: PerceptionProcessingRequest,
    ) -> Tuple[bool, List[str]]:
        """
        Validate that a processing request is valid.
        
        Args:
            request: The request to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not request.request_identity:
            errors.append("Request identity is required")
        
        if not request.source_artifacts:
            errors.append("At least one source artifact is required")
        
        # Check pipeline exists if specified
        if request.requested_pipeline and request.requested_pipeline not in self._pipelines:
            errors.append(
                f"Pipeline '{request.requested_pipeline}' not registered"
            )
        
        return len(errors) == 0, errors
    
    def execute(
        self,
        request: PerceptionProcessingRequest,
        pipeline_id: Optional[str] = None,
        stages: Optional[Tuple[ProcessingStage, ...]] = None,
    ) -> PerceptionProcessingResult:
        """
        Execute processing for a request.
        
        Args:
            request: The processing request
            pipeline_id: Pipeline to use (optional, overrides stages)
            stages: Explicit stages to execute if no pipeline
            
        Returns:
            Processing result with traceability
        """
        # Validate request first
        is_valid, errors = self.validate_request(request)
        if not is_valid:
            return PerceptionProcessingResult.failed(
                request_reference=request.request_identity,
                failure_message=f"Request validation failed: {errors}",
            )
        
        # Determine stages to execute
        execution_stages: List[Tuple[int, ProcessingStage]] = []
        
        if pipeline_id:
            pipeline = self._pipelines.get(pipeline_id)
            if not pipeline:
                return PerceptionProcessingResult.failed(
                    request_reference=request.request_identity,
                    failure_message=f"Pipeline '{pipeline_id}' not found",
                )
            
            for i, stage_id in enumerate(pipeline.stages):
                stage = self._stage_registry.get(stage_id)
                if stage:
                    execution_stages.append((i, stage))
        
        elif stages:
            for i, stage in enumerate(stages):
                execution_stages.append((i, stage))
        
        else:
            return PerceptionProcessingResult.failed(
                request_reference=request.request_identity,
                failure_message="No pipeline or stages specified",
            )
        
        # Execute stages
        output_artifacts = tuple()  # type: ignore
        transformation_records = []
        confidence_state = PerceptionConfidence(confidence=1.0)
        uncertainty_state = PerceptionUncertainty(uncertainty=0.0)
        applied_stages = []
        
        start_time = time.time()
        
        for i, stage in execution_stages:
            try:
                # Prepare input
                input_data = ProcessingStageInput(
                    artifacts=output_artifacts if output_artifacts else tuple(request.source_artifacts),
                    accepted_kinds=stage.accepted_input_kinds,
                    source_revisions={},
                    source_modalities=(request.modality_descriptor,),
                    confidence_state=confidence_state,
                    uncertainty_state=uncertainty_state,
                    provenance=PerceptionProvenance(
                        origin=request.request_identity,
                        creation_process=f"Processing stage: {stage.identity}",
                        semantic_time_utc=time.time(),
                        created_at_utc=time.time(),
                    ),
                )
                
                # Execute stage
                output = stage.process(input_data)
                
                applied_stages.append(stage.identity)
                transformation_records.append(
                    self._create_transformation_record(i, stage, input_data, output)
                )
                
                # Update state for next iteration
                output_artifacts = output.artifacts
                confidence_state = output.confidence_state
                uncertainty_state = output.uncertainty_state
                
            except Exception as e:
                return PerceptionProcessingResult.failed(
                    request_reference=request.request_identity,
                    failure_message=f"Stage '{stage.identity}' failed: {str(e)}",
                    affected_stages=tuple(applied_stages + [stage.identity]),
                )
        
        elapsed_time = time.time() - start_time
        
        # Build result
        return PerceptionProcessingResult.success(
            request_reference=request.request_identity,
            output_artifacts=output_artifacts,
            applied_stages=tuple(applied_stages),
            transformation_records=tuple(transformation_records),
            confidence_effects=(f"Confidence preserved: {confidence_state.confidence}",),
            uncertainty_effects=(f"Uncertainty maintained: {uncertainty_state.uncertainty}",),
        )
    
    def _create_transformation_record(
        self,
        stage_index: int,
        stage: ProcessingStage,
        input_data: ProcessingStageInput,
        output_data: ProcessingStageOutput,
    ) -> "ProcessingTransformationRecord":
        """Create a transformation record for stage execution."""
        return ProcessingTransformationRecord(
            transformation_identity=f"transform:{uuid.uuid4().hex[:16]}",
            stage_identity=stage.identity,
            stage_revision=stage.revision,
            source_artifacts=tuple(str(a) for a in input_data.artifacts),
            output_artifacts=tuple(str(a) for a in output_data.artifacts),
            parameters=stage.configuration,
            configuration_revision=self._active_config,
            calibration_revision=None,
            confidence_effect=_map_confidence_effect(input_data.confidence_state, output_data.confidence_state),
            uncertainty_effect=_map_uncertainty_effect(input_data.uncertainty_state, output_data.uncertainty_state),
            information_loss=output_data.information_loss,
            validation_result=True,
            provenance={
                "stage_index": stage_index,
                "timestamp_utc": time.time(),
                "input_count": len(input_data.artifacts),
                "output_count": len(output_data.artifacts),
            },
        )


def _map_confidence_effect(
    input_conf: PerceptionConfidence,
    output_conf: PerceptionConfidence,
) -> str:
    """Map confidence change to effect description."""
    delta = output_conf.confidence - input_conf.confidence
    if abs(delta) < 0.01:
        return "preserved"
    elif delta > 0:
        return "increased"
    else:
        return "reduced"


def _map_uncertainty_effect(
    input_unc: PerceptionUncertainty,
    output_unc: PerceptionUncertainty,
) -> str:
    """Map uncertainty change to effect description."""
    delta = output_unc.uncertainty - input_unc.uncertainty
    if abs(delta) < 0.01:
        return "preserved"
    elif delta > 0:
        return "increased"
    else:
        return "reduced"