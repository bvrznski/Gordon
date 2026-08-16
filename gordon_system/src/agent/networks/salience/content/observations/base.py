# Salience Observation Base Abstraction
# ====================================
#
# Canonical implementation of observation base abstraction (Phase 4.8.3).
#

"""
Base observation abstraction for the Salience Network.

ARCHITECTURAL PURPOSE:
    Defines the immutable semantic foundation for all observations in the
    Salience Network.
    
CONTENT LAWS:
    SALIENCE-OBSERVATION-LAW-001: Observations represent raw semantic information
    SALIENCE-OBSERVATION-LAW-002: Observations never interpret themselves
    SALIENCE-OBSERVATION-LAW-003: Observations remain immutable
    SALIENCE-OBSERVATION-LAW-004: Every observation possesses explicit ownership
    SALIENCE-OBSERVATION-LAW-005: Observations preserve origin

SEMANTIC HIERARCHY:
    BaseSalienceContent → BaseObservation → ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, FrozenSet, Tuple


@dataclass(frozen=True)
class BaseObservation:
    """
    Base class for all Salience Network observations.
    
    Observations represent raw semantic information without interpretation.
    They are the foundational content type from which other content types derive.
    
    ARCHITECTURAL INVARIANTS:
        - SAL-CONTENT-INV-001: All content is immutable (frozen dataclasses)
        - SAL-OBSERVATION-INV-001: Observations remain raw semantic information
        - SAL-OBSERVATION-INV-002: Observations never interpret themselves
        
    OBSERVATION LAWS:
        - SALIENCE-OBSERVATION-LAW-001: Observations represent raw semantic information
        - SALIENCE-OBSERVATION-LAW-002: Observations never interpret themselves
        - SALIENCE-OBSERVATION-LAW-003: Observations remain immutable
        - SALIENCE-OBSERVATION-LAW-004: Every observation possesses explicit ownership
        - SALIENCE-OBSERVATION-LAW-005: Observations preserve origin
        
    SEMANTIC HIERARCHY:
        BaseObservation → (all specific observations)
        
    CONCRETE OBSERVATION TYPES:
        - SensoryObservation
        - EnvironmentalObservation
        - GoalObservation
        - TaskObservation
        - MemoryObservation
        - ExecutiveObservation
        - PlanningObservation
        - ReasoningObservation
        - ContextObservation
    """
    
    # Identity fields
    observation_id: str = field(default="")
    """Unique identifier for this observation."""
    
    observation_type: str = field(default="base_observation")
    """Type of observation (for categorization)."""
    
    version: str = field(default="1.0.0")
    """Semantic version string."""
    
    # Semantic fields
    content: str = field(default="")
    """The semantic information being observed."""
    
    context: FrozenSet[str] = field(default_factory=frozenset)
    """Context in which this observation was made."""
    
    source_id: str = field(default="")
    """Source of the observation (external system, memory, etc.)."""
    
    # Ownership fields
    owner: str = field(default="Salience Network Content Model")
    """Canonical owner of this observation."""
    
    authority: str = field(default="")
    """Authority that defines this observation's semantics."""
    
    # Origin fields
    origin_id: str = field(default="")
    """Origin identifier for provenance tracking."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    """Timestamp for provenance (not for computation)."""
    
    @property
    def is_raw_information(self) -> bool:
        """
        Indicates whether this observation represents raw semantic information.
        
        Raw observations are uninterpreted and contain only the information
        itself without evaluation or significance assessment.
        """
        return True
    
    @property
    def canonical_type(self) -> str:
        """Return the canonical type identifier for this observation."""
        return f"salience.{self.observation_type}"
    
    def validate_observation_compliance(self) -> bool:
        """
        Validate that this observation satisfies all Salience Network observation laws.
        
        Returns:
            True if observation compliance is valid, False otherwise.
        """
        return (
            self._validate_identity() and
            self._validate_content() and
            self._validate_ownership() and
            self._validate_raw_information()
        )
    
    def _validate_identity(self) -> bool:
        """Validate that identity is explicit and non-empty."""
        return len(self.observation_id.strip()) > 0
    
    def _validate_content(self) -> bool:
        """Validate that content is explicit and non-empty."""
        return len(self.content.strip()) > 0
    
    def _validate_ownership(self) -> bool:
        """Validate that ownership is explicit and non-empty."""
        return len(self.owner.strip()) > 0
    
    def _validate_raw_information(self) -> bool:
        """
        Validate that this observation represents raw semantic information.
        
        Raw observations do not interpret or evaluate the information they contain.
        """
        return True