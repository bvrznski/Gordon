# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cognitive Execution Stage Model
===============================

The CognitiveExecutionStage represents one orchestration phase in a cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from .identity import StageIdentity
from .enums import StageKind, Status


@dataclass(frozen=True, slots=True)
class CognitiveExecutionStage:
    """
    Immutable execution stage model.
    
    STAGE-LAW-001: Every execution stage possesses one stable identity
    STAGE-LAW-002: Every stage belongs to exactly one orchestration plan
    STAGE-LAW-003: Stage dependencies shall remain explicit
    STAGE-LAW-004: Stage completion conditions shall remain explicit
    STAGE-LAW-005: Stage outputs shall remain explicit
    
    STAGE-INV-001: Stage is immutable (deeply frozen)
    STAGE-INV-002: Stage has no runtime references
    """
    
    identity: StageIdentity
    """Unique identity for this stage."""
    
    kind: str  # StageKind.*
    """Type of stage."""
    
    participating_networks: Tuple[str, ...] = ()
    """References to networks executing in this stage."""
    
    required_inputs: Tuple[str, ...] = ()
    """Required input references."""
    
    produced_outputs: Tuple[str, ...] = ()
    """Output references produced by this stage."""
    
    dependencies: Tuple[str, ...] = ()
    """Stage identity references that must complete first."""
    
    synchronization_requirements: str = ""
    """Synchronization requirements for this stage."""
    
    completion_conditions: Tuple[str, ...] = ()
    """Conditions that must be satisfied for completion."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    status: str = Status.CREATED.value
    """Current status of the stage (from Status enum)."""
    
    @classmethod
    def create(
        cls,
        cycle_ref: str,
        kind: str,
        index_in_cycle: int,
        participating_networks: tuple[str, ...] = (),
        dependencies: tuple[str, ...] = (),
    ) -> CognitiveExecutionStage:
        """
        Create a new execution stage.
        
        Args:
            cycle_ref: Reference to parent cycle
            kind: Kind of stage
            index_in_cycle: Index within the cycle
            participating_networks: Networks executing in this stage
            dependencies: Dependencies on other stages
            
        Returns:
            A new CognitiveExecutionStage instance
        """
        identity = StageIdentity.create(
            cycle_ref=cycle_ref,
            kind=kind,
            index_in_cycle=index_in_cycle,
        )
        
        return cls(
            identity=identity,
            kind=kind,
            participating_networks=tuple(participating_networks),
            required_inputs=(),
            produced_outputs=(),
            dependencies=tuple(dependencies),
            synchronization_requirements="",
            completion_conditions=(),
            provenance_ref="",
            status=Status.CREATED.value,
        )
    
    def __str__(self) -> str:
        return f"CognitiveExecutionStage({self.identity}, kind={self.kind}, status={self.status})"


# Alias for type clarity
StageStatus = Status