# Perception Processing Pipeline - Phase 5.2.2
# =============================================

"""
Processing Pipeline: Composes stages into transformation sequences.

A Pipeline defines how multiple Processing Stages are ordered and connected.
It preserves stage independence while enabling complex transformations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid

from gordon_system.src.agent.components.systems.perception.foundations.confidence import PerceptionConfidence, PerceptionUncertainty
from gordon_system.src.agent.components.systems.perception.foundations.provenance import PerceptionProvenance
from .stage import ProcessingStage, ProcessingStageInput, ProcessingStageOutput


# =============================================================================
# PIPELINE ORDERING - How are stages ordered?
# =============================================================================


class PipelineOrdering(Enum):
    """
    Ordering strategy for processing stages.
    
    Strategies:
        SEQUENTIAL:   Stages execute in explicit order (default)
        PARALLEL:     Independent stages can run concurrently
        ADAPTIVE:     Order determined at runtime based on conditions
    """
    
    SEQUENTIAL = "sequential"     # Explicit ordered execution
    PARALLEL = "parallel"         # Concurrent execution when independent
    ADAPTIVE = "adaptive"         # Runtime-determined ordering


# =============================================================================
# STAGE DEPENDENCY - Stage-to-stage dependencies
# =============================================================================


@dataclass(frozen=True)
class ProcessingStageDependency:
    """
    Dependency between processing stages.
    
    Fields:
        source_stage:       Which stage is the dependency source?
        destination_stage:  Which stage depends on it?
        dependency_kind:    What kind of dependency?
        required_artifacts: Which artifacts must be produced?
        mandatory:          Is this dependency required?
    """
    
    source_stage: str               # Stage that produces needed output
    destination_stage: str          # Stage that requires the input
    
    dependency_kind: str = "data"   # data, config, calibration, schema, temporal, spatial, validation
    required_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    mandatory: bool = True         # Must this dependency be satisfied?
    
    @classmethod
    def for_data(cls, source: str, dest: str) -> "ProcessingStageDependency":
        """Create a data dependency between stages."""
        return cls(
            source_stage=source,
            destination_stage=dest,
            dependency_kind="data",
            mandatory=True,
        )
    
    @classmethod
    def for_config(cls, source: str, dest: str) -> "ProcessingStageDependency":
        """Create a configuration dependency."""
        return cls(
            source_stage=source,
            destination_stage=dest,
            dependency_kind="config",
            mandatory=False,
        )


# =============================================================================
# PROCESSING PIPELINE - Stage composition
# =============================================================================


@dataclass(frozen=True)
class ProcessingPipeline:
    """
    A sequence of processing stages with defined dependencies.
    
    Fields:
        pipeline_identity:     Unique pipeline identifier
        input_contract:        What artifacts does this pipeline accept?
        stages:                Ordered list of stage IDs to execute
        dependencies:          Stage-to-stage dependency constraints
        ordering:              Execution strategy (sequential, parallel, etc.)
        intermediate_contracts: Expected output kinds after each stage
        output_contract:       Final output artifact kinds produced
        failure_policy:        What happens on stage failure?
        revision:              Pipeline version
        provenance:            Origin tracking
    """
    
    pipeline_identity: str                # Unique ID
    
    input_contract: Tuple[str, ...]       # e.g., ("Percept", "Signal")
    
    stages: Tuple[str, ...]               # Stage IDs in execution order
    
    dependencies: Tuple[ProcessingStageDependency, ...] = field(default_factory=tuple)
    
    ordering: PipelineOrdering = PipelineOrdering.SEQUENTIAL
    
    intermediate_contracts: Dict[int, Tuple[str, ...]] = field(
        default_factory=dict
    )  # stage_index -> output kinds
    
    output_contract: Tuple[str, ...] = field(default_factory=tuple)  # Final output kinds
    
    failure_policy: str = "stop"          # stop, continue, fallback, retry
    
    revision: int = 1
    provenance: PerceptionProvenance = field(
        default_factory=lambda: PerceptionProvenance(
            origin="system",
            creation_process="ProcessingPipeline created",
            semantic_time_utc=time.time(),
            created_at_utc=time.time(),
        )
    )
    
    def get_stage_index(self, stage_id: str) -> int:
        """Get the index of a stage in the pipeline."""
        for i, sid in enumerate(self.stages):
            if sid == stage_id:
                return i
        raise ValueError(f"Stage '{stage_id}' not found in pipeline")
    
    def get_dependencies_for_stage(self, stage_id: str) -> Tuple[ProcessingStageDependency, ...]:
        """Get all dependencies for a specific stage."""
        return tuple(
            d for d in self.dependencies 
            if d.destination_stage == stage_id
        )
    
    def validate_ordering(self) -> Tuple[bool, List[str]]:
        """
        Validate that pipeline ordering is correct.
        
        Checks:
            - No circular dependencies
            - All referenced stages exist
            - Dependencies are satisfied
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check all stages in dependencies exist
        for dep in self.dependencies:
            if dep.source_stage not in self.stages:
                errors.append(
                    f"Dependency source '{dep.source_stage}' is not a stage in pipeline"
                )
            if dep.destination_stage not in self.stages:
                errors.append(
                    f"Dependency destination '{dep.destination_stage}' is not a stage in pipeline"
                )
        
        # Check for circular dependencies using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(stage_id: str) -> bool:
            visited.add(stage_id)
            rec_stack.add(stage_id)
            
            for dep in self.dependencies:
                if dep.source_stage == stage_id:
                    next_stage = dep.destination_stage
                    if next_stage not in visited:
                        if has_cycle(next_stage):
                            return True
                    elif next_stage in rec_stack:
                        return True
            
            rec_stack.remove(stage_id)
            return False
        
        for stage_id in self.stages:
            if stage_id not in visited:
                if has_cycle(stage_id):
                    errors.append("Circular dependency detected in pipeline")
                    break
        
        # Validate dependencies don't violate ordering
        if self.ordering == PipelineOrdering.SEQUENTIAL:
            dep_indices = {}
            for dep in self.dependencies:
                try:
                    source_idx = self.get_stage_index(dep.source_stage)
                    dest_idx = self.get_stage_index(dep.destination_stage)
                    
                    if dest_idx <= source_idx and dep.mandatory:
                        errors.append(
                            f"Mandatory dependency '{dep.source_stage} -> {dep.destination_stage}' "
                            f"violates sequential ordering"
                        )
                except ValueError:
                    pass  # Already reported
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary."""
        return {
            "pipeline_identity": self.pipeline_identity,
            "input_contract": list(self.input_contract),
            "stages": list(self.stages),
            "dependencies": [
                {
                    "source_stage": d.source_stage,
                    "destination_stage": d.destination_stage,
                    "dependency_kind": d.dependency_kind,
                    "required_artifacts": list(d.required_artifacts),
                    "mandatory": d.mandatory,
                }
                for d in self.dependencies
            ],
            "ordering": self.ordering.value,
            "intermediate_contracts": {
                str(k): list(v) for k, v in self.intermediate_contracts.items()
            },
            "output_contract": list(self.output_contract),
            "failure_policy": self.failure_policy,
            "revision": self.revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingPipeline":
        """Create pipeline from dictionary."""
        dependencies = tuple(
            ProcessingStageDependency(
                source_stage=d["source_stage"],
                destination_stage=d["destination_stage"],
                dependency_kind=d.get("dependency_kind", "data"),
                required_artifacts=tuple(d.get("required_artifacts", [])),
                mandatory=d.get("mandatory", True),
            )
            for d in data.get("dependencies", [])
        )
        
        return cls(
            pipeline_identity=data.get("pipeline_identity", str(uuid.uuid4())),
            input_contract=tuple(data.get("input_contract", ["Percept"])),
            stages=tuple(data.get("stages", [])),
            dependencies=dependencies,
            ordering=PipelineOrdering(data.get("ordering", "sequential")),
            intermediate_contracts={
                int(k): tuple(v) for k, v in data.get("intermediate_contracts", {}).items()
            },
            output_contract=tuple(data.get("output_contract", ["Percept"])),
            failure_policy=data.get("failure_policy", "stop"),
            revision=data.get("revision", 1),
        )