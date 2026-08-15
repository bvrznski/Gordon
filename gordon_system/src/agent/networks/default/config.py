# Default Network Configuration
# =============================

"""
Immutable configuration for the DefaultNetwork.

Configuration is organized into nested value objects rather than one flat bag.
This phase creates the structure; later phases populate computational fields.

PHASE 4.3.1: Semantic Configuration Only
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# EXCEPTION CLASSES (defined here to avoid circular imports in config.py)
# =============================================================================

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


# =============================================================================
# ACTIVATION CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class ActivationThresholds:
    """
    Thresholds for activation level computation.
    
    Controls when the DefaultNetwork considers internally oriented processing
    to be sufficiently important to emit proposals.
    """
    
    # Minimum internal orientation score to trigger assessment
    minimum_internal_orientation: float = 0.3
    
    # Minimum activation level to emit proposals
    minimum_activation_level: float = 0.2
    
    # Maximum number of proposals to emit in one assessment
    max_proposal_count: int = 10


@dataclass(frozen=True)
class AssociationConfig:
    """
    Configuration for associative memory activation.
    
    Controls how strongly memories and concepts activate each other.
    """
    
    # Association strength bounds (0.0 to 1.0)
    min_association_strength: float = 0.2
    max_association_strength: float = 1.0
    
    # Maximum number of related items per proposal
    max_related_items_per_proposal: int = 5
    
    # Decay rate for associations (per assessment cycle)
    association_decay_rate: float = 0.9


# =============================================================================
# NARRATIVE CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class NarrativeConfig:
    """
    Configuration for narrative integration.
    
    Controls how the network maintains and updates internal narratives.
    """
    
    # Maximum narrative elements to track (bounded)
    max_narrative_elements: int = 50
    
    # Minimum fit score to propose integration
    min_fit_score_for_proposal: float = 0.4
    
    # Narrative continuity threshold for assessment activation
    min_continuity_threshold: float = 0.3


# =============================================================================
# REFLECTION CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class ReflectionConfig:
    """
    Configuration for self-referential processing.
    
    Controls when reflection proposals are generated.
    """
    
    # Minimum depth estimate to propose reflection
    min_depth_estimate: float = 0.25
    
    # Maximum reflection candidates per assessment
    max_reflection_candidates: int = 3


# =============================================================================
# SIMULATION CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class SimulationConfig:
    """
    Configuration for simulation proposals.
    
    Controls prospective and counterfactual simulation generation.
    """
    
    # Maximum simulation candidates per assessment
    max_simulation_candidates: int = 4
    
    # Minimum confidence to propose a simulation
    min_simulation_confidence: float = 0.3


# =============================================================================
# GOAL CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class GoalConfig:
    """
    Configuration for unresolved goal handling.
    
    Controls how goals are resurfaced and incubated.
    """
    
    # Maximum unresolved goal proposals per assessment
    max_unresolved_goal_proposals: int = 5
    
    # Minimum priority adjustment to trigger resurfacing
    min_priority_adjustment_for_resurfacing: float = 0.1


# =============================================================================
# DIAGNOSTIC CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class DiagnosticsConfig:
    """
    Configuration for diagnostic and observability output.
    
    What to record for debugging, testing, and monitoring.
    """
    
    # Record level
    enable_proposal_recording: bool = True
    enable_activation_recording: bool = True
    enable_state_snapshots: bool = False
    
    # Maximum snapshot history (bounded)
    max_snapshot_history: int = 100


# =============================================================================
# MAIN CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class DefaultNetworkConfig:
    """
    Immutable configuration for DefaultNetwork.
    
    Organized as nested value objects. All fields have sensible defaults.
    The network rejects any configuration that fails validation.
    """
    
    # Activation thresholds (when to activate)
    activation: ActivationThresholds = field(default_factory=ActivationThresholds)
    
    # Associative memory parameters
    association: AssociationConfig = field(default_factory=AssociationConfig)
    
    # Narrative maintenance
    narrative: NarrativeConfig = field(default_factory=NarrativeConfig)
    
    # Reflection processing
    reflection: ReflectionConfig = field(default_factory=ReflectionConfig)
    
    # Simulation generation
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    
    # Goal handling
    goal: GoalConfig = field(default_factory=GoalConfig)
    
    # Diagnostics
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)

    def validate(self) -> bool:
        """
        Validate that configuration values are within acceptable bounds.
        
        Returns True if valid, raises ConfigurationError otherwise.
        """
        errors = []
        
        # Activation thresholds must be in [0.0, 1.0]
        if not (0.0 <= self.activation.minimum_internal_orientation <= 1.0):
            errors.append("minimum_internal_orientation must be 0.0-1.0")
        if not (0.0 <= self.activation.minimum_activation_level <= 1.0):
            errors.append("minimum_activation_level must be 0.0-1.0")
        
        # Association strength must be in [0.0, 1.0]
        if not (0.0 <= self.association.min_association_strength <= 1.0):
            errors.append("min_association_strength must be 0.0-1.0")
        if not (self.association.max_association_strength <= 1.0):
            errors.append("max_association_strength must be ≤1.0")
        
        # Count values must be positive
        if self.activation.max_proposal_count <= 0:
            errors.append("max_proposal_count must be positive")
        if self.network_config_invalid():
            errors.append("Network configuration is invalid")
        
        if errors:
            raise ConfigurationError("; ".join(errors))
        
        return True

    def network_config_invalid(self) -> bool:
        """Check for general configuration issues."""
        # Ensure bounded counts are reasonable
        if (self.association.max_related_items_per_proposal <= 0 or
                self.reflection.max_reflection_candidates <= 0 or
                self.simulation.max_simulation_candidates <= 0 or
                self.goal.max_unresolved_goal_proposals <= 0 or
                self.diagnostics.max_snapshot_history <= 0):
            return True
        
        # Ensure thresholds are in [0.0, 1.0]
        for field_name in ["min_fit_score_for_proposal", "min_continuity_threshold"]:
            value = getattr(self.narrative, field_name, None)
            if value is not None and not (0.0 <= value <= 1.0):
                return True
        
        return False