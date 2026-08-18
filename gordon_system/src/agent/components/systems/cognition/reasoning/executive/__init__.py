# Executive Reasoning - Phase 7.30
# ==================================

"""
Executive Reasoning Module.

Executive Reasoning is Gordon's global cognitive executive.
It coordinates the entire cognitive architecture to achieve coherent,
goal-directed behavior.

Unlike Meta-Reasoning (which regulates reasoning strategies), Executive
Reasoning coordinates ALL subsystems: reasoning, memory, attention, planning,
execution and perception.

The Executive Coordination Graph (ECG) becomes the canonical representation
of Gordon's moment-to-moment executive control.
"""

from __future__ import annotations

# Core shared types
from .shared import (
    # Enums
    SubsystemType,
    DirectiveKind,
    DirectiveStatus,
    ConflictKind,
    ResolutionKind,
    ValidationOutcome,
    LifecycleState,
    ViolationType,
    SyncState,
    # Contracts
    ExecutiveDescriptor,
    ExecutiveSet,
    ExecutivePipeline,
    ExecutiveState,
    CoordinationManagement,
    ArbitrationManagement,
    DirectiveManagement,
    SynchronizationManagement,
    ExecutiveGovernance,
)

# Subsystem modules
from . import coordination
from . import arbitration  
from . import directives
from . import synchronization
from . import validation
from . import governance

__all__ = [
    # Enums
    "SubsystemType",
    "DirectiveKind", 
    "DirectiveStatus",
    "ConflictKind",
    "ResolutionKind",
    "ValidationOutcome",
    "LifecycleState",
    "ViolationType",
    "SyncState",
    # Contracts
    "ExecutiveDescriptor",
    "ExecutiveSet",
    "ExecutivePipeline",
    "ExecutiveState",
    "CoordinationManagement",
    "ArbitrationManagement",
    "DirectiveManagement",
    "SynchronizationManagement",
    "ExecutiveGovernance",
    # Submodules
    "coordination",
    "arbitration",
    "directives",
    "synchronization",
    "validation", 
    "governance",
]