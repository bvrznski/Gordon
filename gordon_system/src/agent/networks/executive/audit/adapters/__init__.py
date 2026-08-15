# Audit Adapters Package - Gordon Executive Network Audit Subsystem
# ==================================================================

"""
Adapter package for executive subsystem observation.

This package provides read-only adapter interfaces for observing various
executive components without modifying their state.
"""

from typing import Protocol

from gordon_system.src.agent.networks.executive.audit.adapters.executive import (
    ExecutiveStateSnapshot,
    ExecutiveContextSnapshot,
    ExecutiveProgramSnapshot,
    ExecutiveConflictSnapshot,
    ExecutiveDemandSnapshot,
    ExecutiveStateAdapter,
    ExecutiveContextAdapter,
    ExecutiveProgramAdapter,
    ExecutiveConflictAdapter,
    ExecutiveDemandAdapter,
)

__all__ = [
    # Snapshots (read-only data structures)
    "ExecutiveStateSnapshot",
    "ExecutiveContextSnapshot",
    "ExecutiveProgramSnapshot",
    "ExecutiveConflictSnapshot",
    "ExecutiveDemandSnapshot",
    
    # Adapter protocols
    "ExecutiveStateAdapter",
    "ExecutiveContextAdapter",
    "ExecutiveProgramAdapter",
    "ExecutiveConflictAdapter",
    "ExecutiveDemandAdapter",
]