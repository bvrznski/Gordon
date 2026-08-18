# Legal Evolution - Phase 7.47 Part 1
# ====================================

"""
Evolution Contract.

Legal evolution tracks:
    - legislative amendments
    - judicial decisions
    - regulatory updates
    - administrative guidance
    - jurisdictional changes
    
Legal identity remains stable while interpretations evolve.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class LegalEvolution:
    """
    Evolution record for a legal interpretation.
    
    An evolution includes:
        - Original interpretation identity
        - Changes made to the interpretation
        - Triggering events (new legislation, court decision, etc.)
        - Updated interpretation
    
    Legal history is preserved and never overwritten.
    """
    
    # Identity
    evolution_id: str                         # Unique identifier
    
    # Target of evolution
    target_type: str                          # e.g., "interpretation", "obligation"
    target_id: str                            # ID being evolved
    original_interpretation_hash: str = ""    # Hash for verification
    
    # Changes
    change_description: str = ""              # What changed?
    previous_version: Optional[str] = None    # Previous interpretation
    updated_version: Optional[str] = None     # Current interpretation
    
    # Triggers
    triggering_event: Tuple[str, ...] = ()    # Events causing the evolution
    event_timestamp_utc: float = field(default_factory=time.time)
    
    # Status
    is_active: bool = True                    # Is this evolution active?
    effective_from_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_id: str,
        original_hash: str,
        change_description: str,
    ) -> LegalEvolution:
        """Create a new evolution record."""
        return cls(
            evolution_id=f"evolution:{uuid.uuid4().hex[:16]}",
            target_type=target_type,
            target_id=target_id,
            original_interpretation_hash=original_hash,
            change_description=change_description,
        )


@dataclass(frozen=True)
class EvolutionManager:
    """
    Manager for legal evolution tracking.
    
    Tracks all evolutions of interpretations over time.
    """
    
    manager_id: str                           # Unique identifier
    
    # Evolution history
    evolutions: Dict[str, LegalEvolution] = field(default_factory=dict)  # ID -> evolution
    
    # Current versions
    current_versions: Dict[str, Any] = field(default_factory=dict)  # target_id -> current
    
    # Query filters
    target_types: Tuple[str, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_types: Optional[List[str]] = None,
    ) -> EvolutionManager:
        """Create a new evolution manager."""
        return cls(
            manager_id=f"evolution_manager:{uuid.uuid4().hex[:16]}",
            target_types=tuple(target_types or []),
        )
    
    def add_evolution(self, evolution: LegalEvolution) -> EvolutionManager:
        """Add an evolution record to the manager."""
        new_evolutions = dict(self.evolutions)
        new_evolutions[evolution.evolution_id] = evolution
        return dataclass_replace(
            self,
            evolutions=new_evolutions,
            current_versions={**self.current_versions, evolution.target_id: evolution.updated_version},
        )
    
    def get_evolution_history(
        self,
        target_id: str,
    ) -> Tuple[LegalEvolution, ...]:
        """Get all evolutions for a specific target."""
        return tuple(
            e for e in self.evolutions.values()
            if e.target_id == target_id
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "LegalEvolution",
    "EvolutionManager",
]