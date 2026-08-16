# Salience Network Dynamic Policy Configuration
# =============================================

"""
Canonical dynamic policy configuration (Phase 4.8.7).

Policy defines immutable rules for accumulation, decay, habituation,
sensitization, fatigue, recovery, context adaptation, persistence,
and stability evolution.

POLICY INVARIANTS:
    POLICY-INV-001: Policy is immutable (frozen dataclass)
    POLICY-INV-002: No executable callbacks
    POLICY-INV-003: All parameters are semantic descriptors only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class AccumulationPolicy:
    """
    Policy for accumulation of repeated evidence.
    
    ACCUMULATION POLICY PARAMETERS:
        - required_repetitions: Minimum repetitions to trigger level change
        - reinforcement_strength: Multiplier for accumulation effect
        - maximum_level: Upper bound on accumulation
        - saturation_threshold: Level at which saturation is declared
        - decay_factor: Rate of accumulation decay without reinforcement
    """
    
    required_repetitions: int = field(default=3)
    """Minimum repetitions to trigger accumulation level change."""
    
    reinforcement_strength: float = field(default=1.0)
    """Multiplier for accumulation effect per repetition."""
    
    maximum_level: int = field(default=5)
    """Upper bound on accumulation level (0-5 scale)."""
    
    saturation_threshold: int = field(default=4)
    """Level at which saturation is declared (threshold for SATURATED status)."""
    
    decay_factor: float = field(default=0.1)
    """Rate of accumulation decay without reinforcement per delta."""
    
    @property
    def is_saturated(self, current_level: int) -> bool:
        """Check if current level has reached saturation threshold."""
        return current_level >= self.saturation_threshold


@dataclass(frozen=True)
class DecayCurve:
    """
    Shape of decay curve over semantic time.
    
    CURVE TYPES:
        - LINEAR: Constant reduction per delta
        - LOGARITHMIC: Rapid initial decay, slowing over time
        - EXPONENTIAL: Proportional to current value
        - PIECEWISE: Different rates for different value ranges
    """
    
    curve_type: str = field(default="linear")
    """Type of decay curve."""
    
    decay_rate: float = field(default=0.1)
    """Base decay rate per delta unit."""
    
    minimum_level: float = field(default=0.0)
    """Minimum bound on salience level after decay."""
    
    maximum_reduction: float = field(default=1.0)
    """Maximum reduction allowed in single update."""
    
    @property
    def is_linear(self) -> bool:
        """Check if curve type is linear."""
        return self.curve_type == "linear"
    
    @property
    def is_exponential(self) -> bool:
        """Check if curve type is exponential."""
        return self.curve_type == "exponential"


@dataclass(frozen=True)
class DecayPolicy:
    """
    Policy for decay of salience without reinforcing evidence.
    
    DECAY POLICY PARAMETERS:
        - base_curve: Shape of decay over time
        - protected_categories: Categories exempt from decay
        - minimum_persistence_threshold: Minimum persistence required to protect
    """
    
    base_curve: DecayCurve = field(default_factory=DecayCurve)
    """Base decay curve configuration."""
    
    protected_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidate IDs exempt from decay (by policy)."""
    
    minimum_persistence_threshold: float = field(default=0.5)
    """Below this persistence, rapid decay applies."""
    
    @property
    def is_protected(self, candidate_id: str) -> bool:
        """Check if candidate is protected from decay."""
        return candidate_id in self.protected_candidates


@dataclass(frozen=True)
class HabituationPolicy:
    """
    Policy for habituation (reduced response to repeated stimulus).
    
    HABITUATION POLICY PARAMETERS:
        - required_repetitions: Repetitions to trigger habituation
        - decay_rate: Rate of response reduction
        - minimum_salience: Floor on salience after habituation
        - recovery_half_life: Time for half-recovery from habituation
    """
    
    required_repetitions: int = field(default=5)
    """Repetitions needed to trigger habituation effect."""
    
    decay_rate: float = field(default=0.15)
    """Rate of response reduction per repetition beyond threshold."""
    
    minimum_salience: float = field(default=0.2)
    """Floor on salience after habituation (as fraction of base)."""
    
    recovery_half_life: int = field(default=10)
    """Semantic delta for half-recovery from habituation."""
    
    novelty_reset_threshold: float = field(default=0.3)
    """Novelty increase above threshold resets habituation."""
    
    @property
    def requires_habituation(self, repetitions: int) -> bool:
        """Check if repetition count triggers habituation."""
        return repetitions >= self.required_repetitions


@dataclass(frozen=True)
class SensitizationPolicy:
    """
    Policy for sensitization (increased response to repeated significant input).
    
    SENSITIZATION POLICY PARAMETERS:
        - required_repetitions: Repetitions to trigger sensitization
        - growth_rate: Rate of response increase
        - maximum_sensitivity: Upper bound on sensitization
        - context_trigger_threshold: Context change magnitude needed
    """
    
    required_repetitions: int = field(default=3)
    """Repetitions needed to trigger sensitization."""
    
    growth_rate: float = field(default=0.2)
    """Rate of response increase per repetition beyond threshold."""
    
    maximum_sensitivity: float = field(default=2.0)
    """Maximum sensitivity multiplier (2x = 200% base)."""
    
    context_trigger_threshold: float = field(default=0.5)
    """Context change magnitude needed to trigger sensitization."""
    
    @property
    def requires_sensitization(self, repetitions: int) -> bool:
        """Check if repetition count triggers sensitization."""
        return repetitions >= self.required_repetitions


@dataclass(frozen=True)
class FatiguePolicy:
    """
    Policy for fatigue (diminished influence after prolonged activation).
    
    FATIGUE POLICY PARAMETERS:
        - activation_duration_threshold: Duration before fatigue builds
        - accumulation_rate: Rate of fatigue accumulation
        - suppression_threshold: Level at which fatigue suppresses contribution
        - recovery_rate: Rate of fatigue reduction during inactivity
    """
    
    activation_duration_threshold: int = field(default=10)
    """Duration (delta) before fatigue begins accumulating."""
    
    accumulation_rate: float = field(default=0.05)
    """Rate of fatigue accumulation per delta beyond threshold."""
    
    suppression_threshold: float = field(default=0.7)
    """Fatigue level above which contribution is suppressed (> 70% fatigued)."""
    
    recovery_rate: float = field(default=0.1)
    """Rate of fatigue reduction during inactivity per delta."""
    
    maximum_fatigue: float = field(default=1.0)
    """Maximum possible fatigue (normalized 0-1 scale)."""
    
    @property
    def is_suppressed(self, fatigue_level: float) -> bool:
        """Check if candidate contribution is suppressed by fatigue."""
        return fatigue_level >= self.suppression_threshold


@dataclass(frozen=True)
class RecoveryPolicy:
    """
    Policy for recovery (reversal of fatigue/habituation).
    
    RECOVERY POLICY PARAMETERS:
        - required_inactivity: Inactivity duration needed to start recovery
        - recovery_speed: Speed of recovery progress
        - interaction_with_decay: How decay interacts with recovery
        - reset_threshold: Threshold that triggers full reset
    """
    
    required_inactivity: int = field(default=5)
    """Semantic delta of inactivity before recovery begins."""
    
    recovery_speed: float = field(default=0.2)
    """Rate of recovery progress per delta."""
    
    interaction_with_decay: str = field(default="additive")
    """How decay and recovery interact ('additive', 'multiplicative')."""
    
    reset_threshold: float = field(default=1.0)
    """Recovery level at which full reset occurs."""
    
    @property
    def can_start_recovery(self, inactivity_delta: int) -> bool:
        """Check if inactivity duration allows recovery to begin."""
        return inactivity_delta >= self.required_inactivity


@dataclass(frozen=True)
class ContextAdaptationPolicy:
    """
    Policy for context-dependent adaptation.
    
    CONTEXT ADAPTATION POLICY PARAMETERS:
        - context_change_threshold: Magnitude change needed to trigger adaptation
        - adaptation_speed: Speed of state adjustment
        - preserve_on_context_change: Whether baseline persists across contexts
    """
    
    context_change_threshold: float = field(default=0.3)
    """Context similarity drop threshold to trigger adaptation."""
    
    adaptation_speed: float = field(default=0.15)
    """Rate of adaptive state adjustment per delta."""
    
    preserve_on_context_change: bool = field(default=True)
    """Whether baseline salience persists across context shifts."""
    
    @property
    def requires_adaptation(self, similarity: float) -> bool:
        """Check if context change magnitude triggers adaptation."""
        return (1.0 - similarity) >= self.context_change_threshold


@dataclass(frozen=True)
class PersistencePolicy:
    """
    Policy for persistence evolution over semantic time.
    
    PERSISTENCE POLICY PARAMETERS:
        - transient_decay_delta: Delta at which transient decays
        - short_lived_decay_delta: Delta at which short-lived decays
        - medium_lived_decay_delta: Delta at which medium-lived decays
        - persistent_threshold: Minimum delta for persistence classification
    """
    
    transient_decay_delta: int = field(default=1)
    """Delta at which TRANSIENT candidates lose salience."""
    
    short_lived_decay_delta: int = field(default=3)
    """Delta at which SHORT_LIVED candidates begin rapid decay."""
    
    medium_lived_decay_delta: int = field(default=10)
    """Delta at which SUSTAINED candidates begin moderate decay."""
    
    persistent_threshold: int = field(default=50)
    """Minimum delta for PERSISTENT classification."""
    
    @property
    def expected_persistence_kind(self, current_delta: int) -> str:
        """
        Determine persistence kind based on elapsed delta.
        
        Args:
            current_delta: Elapsed semantic delta
            
        Returns:
            Persistence kind string
        """
        if current_delta < self.transient_decay_delta:
            return "transient"
        elif current_delta < self.short_lived_decay_delta:
            return "short_lived"
        elif current_delta < self.medium_lived_decay_delta:
            return "sustained"
        else:
            return "persistent"


@dataclass(frozen=True)
class StabilityPolicy:
    """
    Policy for stability evolution.
    
    STABILITY POLICY PARAMETERS:
        - volatile_threshold: Delta below which state is volatile
        - unstable_threshold: Delta below which state is unstable
        - stable_threshold: Delta above which state becomes stable
        - robust_threshold: Delta above which state becomes robust
    """
    
    volatile_threshold: int = field(default=1)
    """Delta < threshold = VOLATILE status."""
    
    unstable_threshold: int = field(default=3)
    """Delta < threshold = UNSTABLE status."""
    
    stable_threshold: int = field(default=10)
    """Delta >= threshold can become STABLE."""
    
    robust_threshold: int = field(default=50)
    """Delta >= threshold = ROBUST status."""
    
    @property
    def expected_stability_status(self, current_delta: int) -> str:
        """
        Determine stability status based on elapsed delta.
        
        Args:
            current_delta: Elapsed semantic delta
            
        Returns:
            Stability status string
        """
        if current_delta < self.volatile_threshold:
            return "volatile"
        elif current_delta < self.unstable_threshold:
            return "unstable"
        elif current_delta < self.stable_threshold:
            return "stable"
        else:
            return "robust"


@dataclass(frozen=True)
class DynamicPolicy:
    """
    Complete dynamic policy configuration.
    
    Contains all sub-policies for accumulation, decay, habituation,
    sensitization, fatigue, recovery, context adaptation, persistence,
    and stability evolution.
    
    POLICY INVARIANTS:
        POLICY-INV-001: Policy is deeply frozen dataclass
        POLICY-INV-002: No executable callbacks
        POLICY-INV-003: All parameters are semantic descriptors only
    """
    
    accumulation: AccumulationPolicy = field(default_factory=AccumulationPolicy)
    """Accumulation policy configuration."""
    
    decay: DecayPolicy = field(default_factory=DecayPolicy)
    """Decay policy configuration."""
    
    habituation: HabituationPolicy = field(default_factory=HabituationPolicy)
    """Habituation policy configuration."""
    
    sensitization: SensitizationPolicy = field(default_factory=SensitizationPolicy)
    """Sensitization policy configuration."""
    
    fatigue: FatiguePolicy = field(default_factory=FatiguePolicy)
    """Fatigue policy configuration."""
    
    recovery: RecoveryPolicy = field(default_factory=RecoveryPolicy)
    """Recovery policy configuration."""
    
    context_adaptation: ContextAdaptationPolicy = field(
        default_factory=ContextAdaptationPolicy
    )
    """Context adaptation policy configuration."""
    
    persistence: PersistencePolicy = field(default_factory=PersistencePolicy)
    """Persistence evolution policy configuration."""
    
    stability: StabilityPolicy = field(default_factory=StabilityPolicy)
    """Stability evolution policy configuration."""