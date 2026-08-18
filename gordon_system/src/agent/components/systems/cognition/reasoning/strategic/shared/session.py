# Strategic Session - Phase 7.18
# ==============================

"""
Canonical Strategic Session for Phase 7.18.

Every strategic analysis occurs inside a Strategic Session that defines:
    - Mission
    - Long-term objectives  
    - Resource constraints
    - Success criteria
    - Termination conditions
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicSession:
    """
    A strategic analysis session.
    
    Defines the context for all strategic reasoning activities including mission,
    objectives, constraints, and success criteria.
    """
    
    # Identity
    session_identity: str                   # Unique session identifier
    
    # Mission definition
    mission_statement: str                  # What is the mission?
    
    # Long-term objectives
    long_term_objectives: List[str] = field(default_factory=list)  # Objective IDs
    
    # Resource constraints
    resource_constraints: Dict[str, Any] = field(default_factory=dict)  # constraint_name -> value
    
    # Success criteria
    success_criteria: List[str] = field(default_factory=list)  # Success conditions
    
    # Termination conditions
    termination_conditions: List[str] = field(default_factory=list)
    
    # Strategic model being used
    strategic_model: str = "default"        # e.g., "hierarchical", "portfolio"
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    created_by_identity: str = ""           # Who/what created this session?
    
    @property
    def objective_count(self) -> int:
