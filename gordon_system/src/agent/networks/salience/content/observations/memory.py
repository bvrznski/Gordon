# Salience Memory Observation
# =========================
#
# Canonical implementation of memory observations (Phase 4.8.3).
#

"""
Memory observation for the Salience Network.

MEMORY OBSERVATION:
    Represents raw semantic information from memory without interpretation.
    
SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → MemoryObservation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import FrozenSet, Tuple

from gordon_system.src.agent.networks.salience.content.observations.base import BaseObservation


@dataclass(frozen=True)
class MemoryObservation(BaseObservation):
    """
    Observation of raw memory-related information without interpretation.
    
    MEMORY TYPES:
        - episodic: Event-based memories
        - semantic: Fact-based knowledge
        - procedural: Skill and habit memories
        - working: Active memory content
    
    SEMANTIC HIERARCHY:
        BaseObservation → MemoryObservation
    """
    
    memory_type: str = field(default="episodic")
    """Type of memory (episodic, semantic, procedural, working)."""
    
    memory_id: str = field(default="")
    """Identifier for the memory source."""
    
    confidence: float = field(default=1.0)
    """Confidence level in the memory (0.0 to 1.0)."""
    
    @property
    def is_memory(self) -> bool:
        """Indicates whether this is a memory observation."""
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this memory observation."""
        return f"salience.memory.{self.memory_type}"
    
    def validate_memory_compliance(self) -> bool:
        """
        Validate that this memory observation satisfies Salience Network laws.
        
        Returns:
            True if compliance is valid, False otherwise.
        """
        return (
            super().validate_observation_compliance() and
            self._validate_memory_type()
        )
    
    def _validate_memory_type(self) -> bool:
        """Validate that memory type is explicit and recognized."""
        recognized_types = {"episodic", "semantic", "procedural", "working"}
        return self.memory_type in recognized_types