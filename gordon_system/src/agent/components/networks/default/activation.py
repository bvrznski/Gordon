# Default Network Activation Model
# ===============================

"""
Semantic activation model for the DefaultNetwork.

Activation represents the degree of internally oriented processing that is
currently relevant and should be coordinated. It does NOT mean:
    - CPU utilization
    - thread scheduling priority  
    - GPU allocation
    - worker count

PHASE 4.3.1: Activation Semantics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# ACTIVATION VALUES (normalized [0.0, 1.0])
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultActivation:
    """
    Semantic activation level for the DefaultNetwork.
    
    Represents degree of internally oriented processing that should be
    coordinated. This is a semantic value, NOT a runtime resource command.
    
    Activation may represent:
        - Degree of internally oriented processing
        - Relevance of autobiographical information  
        - Memory-driven associative pressure
        - Internally generated simulation demand
        - Narrative-integration demand
        - Unresolved-goal activity
        - Spontaneous-association activity
        - Internal reflection demand
    """
    
    # Normalized activation level (0.0 to 1.0)
    level: float = 0.0
    
    # Internal orientation score (0.0 to 1.0)
    internal_orientation_score: float = 0.0
    
    # Reasoning for this activation level
    reasons: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class InternalOrientationScore:
    """
    Score representing the degree of internally oriented processing.
    
    Computed from various internal signals without runtime assumptions.
    """
    
    # Memory-driven association score (0.0 to 1.0)
    memory_association_score: float = 0.0
    
    # Reflection demand score (0.0 to 1.0)  
    reflection_demand_score: float = 0.0
    
    # Simulation pressure score (0.0 to 1.0)
    simulation_pressure_score: float = 0.0
    
    # Narrative integration demand score (0.0 to 1.0)
    narrative_integration_score: float = 0.0
    
    # Unresolved goal resurfacing score (0.0 to 1.0)
    unresolved_goal_score: float = 0.0


# =============================================================================
# ACTIVATION SOURCES
# =============================================================================

class ActivationSource:
    """
    Bounded source types for activation signals.
    
    These are semantic sources, NOT runtime scheduling sources.
    """
    
    # Memory-driven signals
    MEMORY_ASSOCIATION = "memory_association"
    MEMORY_REACTIVATION = "memory_reactivation"
    
    # Cognitive signals  
    REFLECTION_DEMAND = "reflection_demand"
    SIMULATION_REQUEST = "simulation_request"
    
    # Narrative signals
    NARRATIVE_INTEGRATION = "narrative_integration"
    NARRATIVE_DISCONTINUITY = "narrative_discontinuity"
    
    # Goal signals
    UNRESOLVED_GOAL = "unresolved_goal"
    INCUBATION_REQUEST = "incubation_request"


# =============================================================================
# ACTIVATION THRESHOLDS
# =============================================================================

class ActivationThresholds:
    """
    Threshold values for activation levels.
    
    These define when internally oriented processing is considered significant
    enough to warrant proposal generation.
    """
    
    # Minimum level to generate any proposals
    MIN_ACTIVE_LEVEL: float = 0.2
    
    # Minimum internal orientation score to prioritize internal processing
    MIN_INTERNAL_ORIENTATION_SCORE: float = 0.3
    
    # Maximum activation (capped)
    MAX_ACTIVATION: float = 1.0


# =============================================================================
# ACTIVATION REASON CATEGORIES
# =============================================================================

class ActivationReason:
    """
    Reason categories for activation.
    
    Each reason explains why internally oriented processing is being activated.
    """
    
    MEMORY_DRIVEN_ASSOCIATION = "memory_driven_association"
    UNRESOLVED_GOAL_RESURFACING = "unresolved_goal_resurfacing"
    NARRATIVE_DISCONTINUITY = "narrative_discontinuity"
    REFLECTION_DEMAND = "reflection_demand"
    SIMULATION_REQUEST = "simulation_request"
    SPONTANEOUS_ASSOCIATION = "spontaneous_association"