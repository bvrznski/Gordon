# Salience Task Observation
# =======================
#
# Canonical implementation of task observations (Phase 4.8.3).
#

"""
Task observation for the Salience Network.

TASK OBSERVATION:
    Represents raw semantic information about tasks without interpretation.
    
SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → TaskObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class TaskObservation(BaseObservation):
    """
    Observation of raw task-related information without interpretation.
    
    TASK TYPES:
        - atomic: Basic indivisible tasks
        - composite: Tasks composed of subtasks
        - sequential: Sequentially ordered tasks
        - parallel: Concurrently executable tasks
    
    SEMANTIC HIERARCHY:
        BaseObservation → TaskObservation
    """
    
    task_type: str = field(default="atomic")
    """Type of task (atomic, composite, sequential, parallel)."""
    
    task_id: str = field(default="")
    """Identifier for the target task."""
    
    @property
    def is_task(self) -> bool:
        """Indicates whether this is a task observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this task observation."""
        return f"salience.task.{self.task_type}"
    
    def validate_task_compliance(self) -> bool:
        """
        Validate that this task observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_task_type()
        )
    
    def _validate_task_type(self) -> bool:
        """Validate that task type is explicit and recognized."""
        recognized_types = {"atomic", "composite", "sequential", "parallel"}
        return self.task_type in recognized_types
