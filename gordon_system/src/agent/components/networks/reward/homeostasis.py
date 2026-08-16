# Reward Network - Reward Homeostasis Module (Phase 4.10.4)
# ============================================================

"""
Reward homeostasis module for modeling long-term reward equilibrium states.

Reward Homeostasis represents the system's equilibrium state regarding reward,
modeling reward surplus, deficit, and adaptation pressure without being
regulatory or corrective.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True)
class RewardHomeostasis:
    """
    Semantic representation of long-term reward equilibrium state.
    
    Homeostasis models the system's overall balance regarding reward, tracking
    whether rewards are accumulating or depleting over time. Unlike regulatory
    systems, homeostasis is descriptive - it does not directly modify behavior
    but provides context for interpreting reward values.
    
    HOMEOSTATIC STATES:
        • equilibrium: Balanced state with minimal deviation
        • surplus: Accumulating rewards above equilibrium
        • deficit: Depleting rewards below equilibrium  
        • adaptation_pressure: System adapting to new baseline
        
    CRITICAL DISTINCTIONS:
        • Homeostasis ≠ Regulation: Describes state, doesn't control it
        • Homeostasis ≠ Motivation: Current balance vs. drive generation
        • Homeostasis ≠ Learning: Observation vs. adaptation mechanism
        
    PROPERTIES:
        • homeostasis_id: Unique identifier for this homeostatic state
        • domain: Semantic domain being analyzed
        • equilibrium_estimate: Expected long-term average reward
        • current_state: Current deviation from equilibrium (surplus/deficit)
        • adaptation_pressure: Pressure to adapt baseline
        • recovery_trend: Direction of adjustment toward equilibrium
        
    NOT RESPONSIBLE FOR:
        • Regulating behavior based on homeostatic state
        • Modifying reward estimates
        • Learning or adapting from homeostatic imbalances
    """
    
    # Identity and reference (no defaults first)
    homeostasis_id: str
    """Unique identifier for this homeostatic state."""
    
    domain: str  # BaselineDomain.*
    """Semantic domain being analyzed."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Equilibrium measures (always preserved)
    equilibrium_estimate: float = 0.0
    """Expected long-term average reward value."""
    
    current_state: str = "equilibrium"  # equilibrium/surplus/deficit/adaptation_pressure
    """Current deviation from equilibrium state."""
    
    deviation_from_equilibrium: float = 0.0
    """Signed distance from equilibrium (positive=surplus, negative=deficit)."""
    
    # Adaptation measures
    adaptation_pressure: float = 0.0
    """Pressure to adapt baseline (0.0=no pressure, 1.0=max pressure)."""
    
    recovery_trend: str = "stable"  # increasing/decreasing/stable/unknown
    """Direction of adjustment toward equilibrium."""
    
    # Semantic evaluation fields
    confidence: float = 1.0
    """Confidence in the homeostatic assessment."""
    
    uncertainty: float = 0.0
    """Uncertainty about the homeostatic state."""
    
    observation_window: int = 1
    """Number of time units analyzed."""
    
    data_points: Tuple[float, ...] = field(default_factory=tuple)
    """Raw observations used for analysis."""
    
    provenance: Optional[str] = None
    """Provenance reference for this homeostasis assessment."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from homeostasis analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.homeostasis_id}@v{self.revision}"
    
    # Factory methods for homeostatic states
    @classmethod
    def create_equilibrium(
        cls,
        homeostasis_id: str,
        domain: str = "reward",
        equilibrium_estimate: float = 0.0,
        confidence: float = 0.95,
    ) -> RewardHomeostasis:
        """Create an equilibrium homeostatic state."""
        return cls(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=equilibrium_estimate,
            current_state="equilibrium",
            deviation_from_equilibrium=0.0,
            adaptation_pressure=0.0,
            recovery_trend="stable",
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def create_surplus(
        cls,
        homeostasis_id: str,
        domain: str = "reward",
        equilibrium_estimate: float = 0.0,
        surplus_amount: float = 1.0,
        adaptation_pressure: float = 0.3,
    ) -> RewardHomeostasis:
        """Create a surplus homeostatic state."""
        return cls(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=equilibrium_estimate,
            current_state="surplus",
            deviation_from_equilibrium=surplus_amount,
            adaptation_pressure=min(adaptation_pressure, 1.0),
            recovery_trend="decreasing",  # moving toward equilibrium
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def create_deficit(
        cls,
        homeostasis_id: str,
        domain: str = "reward",
        equilibrium_estimate: float = 0.0,
        deficit_amount: float = -1.0,
        adaptation_pressure: float = 0.3,
    ) -> RewardHomeostasis:
        """Create a deficit homeostatic state."""
        return cls(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=equilibrium_estimate,
            current_state="deficit",
            deviation_from_equilibrium=deficit_amount,
            adaptation_pressure=min(abs(adaptation_pressure), 1.0),
            recovery_trend="increasing",  # moving toward equilibrium
            confidence=0.85,
            uncertainty=0.15,
        )
    
    @classmethod
    def create_adaptation_pressure(
        cls,
        homeostasis_id: str,
        domain: str = "reward",
        equilibrium_estimate: float = 0.0,
        pressure_level: float = 0.7,
        recovery_trend: str = "unknown",
    ) -> RewardHomeostasis:
        """Create an adaptation-pressure homeostatic state."""
        return cls(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=equilibrium_estimate,
            current_state="adaptation_pressure",
            deviation_from_equilibrium=0.0,  # at equilibrium but adapting
            adaptation_pressure=min(pressure_level, 1.0),
            recovery_trend=recovery_trend if recovery_trend != "unknown" else "stable",
            confidence=0.7,
            uncertainty=0.3,
        )
    
    @classmethod
    def create_unknown_state(
        cls,
        homeostasis_id: str,
        domain: str = "reward",
        uncertainty: float = 0.5,
    ) -> RewardHomeostasis:
        """Create an unknown homeostatic state (insufficient data)."""
        return cls(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=0.0,
            current_state="equilibrium",  # neutral default
            deviation_from_equilibrium=0.0,
            adaptation_pressure=0.5,  # neutral
            recovery_trend="unknown",
            confidence=1.0 - uncertainty,
            uncertainty=uncertainty,
        )
    
    @property
    def is_equilibrium(self) -> bool:
        """Check if current state is equilibrium."""
        return self.current_state == "equilibrium"
    
    @property
    def is_surplus(self) -> bool:
        """Check if current state is surplus."""
        return self.current_state == "surplus"
    
    @property
    def is_deficit(self) -> bool:
        """Check if current state is deficit."""
        return self.current_state == "deficit"
    
    @property
    def has_adaptation_pressure(self) -> bool:
        """Check if there's significant adaptation pressure."""
        return self.adaptation_pressure > 0.3
    
    @property
    def is_recovery_increasing(self) -> bool:
        """Check if recovery trend is increasing (moving from deficit)."""
        return self.recovery_trend == "increasing"
    
    @property
    def is_recovery_decreasing(self) -> bool:
        """Check if recovery trend is decreasing (moving from surplus)."""
        return self.recovery_trend == "decreasing"


@dataclass(frozen=True)
class HomeostasisCollection:
    """
    Collection of homeostatic states across multiple domains.
    
    Aggregates individual homeostatic assessments into a semantic summary
    while preserving all individual state details for downstream analysis.
    """
    
    # Identity and reference (no defaults first)
    collection_id: str
    """Unique identifier for this homeostasis collection."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    # Homeostasis storage (always preserved)
    states: Tuple[RewardHomeostasis, ...] = field(default_factory=tuple)
    """Individual homeostatic states in this collection."""
    
    # Semantic aggregation fields
    dominant_state: str = "equilibrium"
    """Most common state across domains."""
    
    aggregate_adaptation_pressure: float = 0.0
    """Average adaptation pressure across states."""
    
    aggregate_deviation: float = 0.0
    """Average deviation from equilibrium across states."""
    
    # Domain coverage
    domains_analyzed: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic domains covered by this collection."""
    
    provenance: Optional[str] = None
    """Provenance reference for this collection."""
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    """Key findings from homeostasis collection analysis."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Collection analysis trace for provenance."""
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.collection_id}@v{self.revision}"
    
    @property
    def state_count(self) -> int:
        """Get count of homeostatic states in this collection."""
        return len(self.states)
    
    @classmethod
    def create_empty(cls, collection_id: str) -> HomeostasisCollection:
        """Create an empty homeostasis collection."""
        return cls(
            collection_id=collection_id,
            states=tuple(),
            dominant_state="equilibrium",
            aggregate_adaptation_pressure=0.0,
            aggregate_deviation=0.0,
        )
    
    @classmethod
    def from_states(cls, collection_id: str, states: Tuple[RewardHomeostasis, ...]) -> HomeostasisCollection:
        """
        Create a homeostasis collection from individual states.
        
        Analyzes the distribution of states and computes
        aggregate semantic measures.
        """
        if not states:
            return cls.create_empty(collection_id)
        
        # Count state frequencies
        state_counts: dict[str, int] = {}
        for s in states:
            state_counts[s.current_state] = state_counts.get(s.current_state, 0) + 1
        
        # Find dominant state (most common)
        dominant_state = max(state_counts.items(), key=lambda x: x[1])[0]
        
        # Compute aggregate metrics
        total_pressure = sum(s.adaptation_pressure for s in states)
        aggregate_adaptation_pressure = total_pressure / len(states)
        
        total_deviation = sum(abs(s.deviation_from_equilibrium) for s in states)
        aggregate_deviation = sum(s.deviation_from_equilibrium for s in states) / len(states)
        
        # Collect domains analyzed
        domains = tuple(set(s.domain for s in states))
        
        return cls(
            collection_id=collection_id,
            states=states,
            dominant_state=dominant_state,
            aggregate_adaptation_pressure=aggregate_adaptation_pressure,
            aggregate_deviation=aggregate_deviation,
            domains_analyzed=domains,
        )


@dataclass(frozen=True)
class HomeostasisAnalyzer:
    """
    Deterministic homeostasis analysis engine.
    
    Analyzes sequences of reward values to extract semantic homeostatic information
    without statistical modeling or prediction.
    """
    
    # Analysis parameters (deterministic configuration)
    equilibrium_threshold: float = 0.1
    """Deviation below which state is considered 'equilibrium'."""
    
    adaptation_threshold: float = 0.3
    """Adaptation pressure above which state is 'adaptation_pressure'."""
    
    @classmethod
    def analyze_homeostasis(
        cls,
        values: Tuple[float, ...],
        domain: str = "reward",
        homeostasis_id: str = "default-homeostasis",
    ) -> RewardHomeostasis:
        """
        Analyze a sequence of reward values and extract homeostatic information.
        
        Args:
            values: Sequence of reward values over time
            domain: Semantic domain being analyzed
            homeostasis_id: Identifier for the resulting homeostatic state
            
        Returns:
            RewardHomeostasis with semantic analysis results
        """
        if len(values) < 2:
            return RewardHomeostasis.create_unknown_state(
                homeostasis_id=homeostasis_id,
                domain=domain,
                uncertainty=0.5,
            )
        
        # Calculate equilibrium estimate (long-term average)
        equilibrium_estimate = sum(values) / len(values)
        
        # Current state is the most recent value
        current_value = values[-1]
        
        # Calculate deviation from equilibrium
        deviation = current_value - equilibrium_estimate
        
        # Determine current state based on deviation
        if abs(deviation) <= cls.equilibrium_threshold:
            current_state = "equilibrium"
            adaptation_pressure = 0.0
            recovery_trend = "stable"
        elif deviation > 0:
            current_state = "surplus"
            adaptation_pressure = min(abs(deviation), 1.0)
            recovery_trend = "decreasing"  # moving toward equilibrium
        else:
            current_state = "deficit"
            adaptation_pressure = min(abs(deviation), 1.0)
            recovery_trend = "increasing"  # moving toward equilibrium
        
        # Check if system is under significant adaptation pressure
        if len(values) >= 3:
            # Calculate recent trend
            recent_differences = tuple(
                values[i + 1] - values[i] for i in range(len(values) - 1)
            )
            
            # If there's consistent movement away from equilibrium, increase pressure
            if (deviation > 0 and sum(recent_differences) > cls.equilibrium_threshold) or \
               (deviation < 0 and sum(recent_differences) < -cls.equilibrium_threshold):
                adaptation_pressure = min(adaptation_pressure * 1.5, 1.0)
        
        return RewardHomeostasis(
            homeostasis_id=homeostasis_id,
            domain=domain,
            equilibrium_estimate=equilibrium_estimate,
            current_state=current_state,
            deviation_from_equilibrium=deviation,
            adaptation_pressure=adaptation_pressure,
            recovery_trend=recovery_trend,
            confidence=min(0.95, 1.0 - abs(deviation) * 2),
            uncertainty=abs(deviation) * 2,
            observation_window=len(values),
            data_points=values,
        )