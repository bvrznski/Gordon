# Salience Network Adaptive State Models
# ======================================

"""
Canonical adaptive state models (Phase 4.8.7).

Each Candidate maintains immutable adaptive descriptors tracking:
    - accumulation_level: Accumulated reinforcement evidence
    - decay_state: Current decay descriptor
    - habituation_level: Habituated response level (0-1 scale)
    - sensitization_level: Sensitized response level
    - fatigue_level: Current fatigue level (0-1 scale)
    - recovery_state: Recovery progress descriptor
    - persistence_kind: Persistence classification
    - stability_status: Temporal stability status
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class AccumulationState:
    """
    Current accumulation level for a Candidate.
    
    ACCUMULATION LEVELS (0-5 scale):
        - 0: NONE - No accumulation detected
        - 1: WEAK - Initial repetitions observed
        - 2: WEAK - Sustained but low-level accumulation
        - 3: MODERATE - Noticeable reinforcement pattern
        - 4: STRONG - High confidence in accumulated significance
        - 5: SATURATED - Maximum accumulated level reached
    
    ACCUMULATION INVARIANTS:
        ACCUM-INV-001: Level is bounded (0 <= level <= maximum)
        ACCUM-INV-002: No evidence is invented
        ACCUM-INV-003: State is immutable
    """
    
    level: int = field(default=0)
    """Current accumulation level (0-5 scale)."""
    
    repetitions: int = field(default=0)
    """Total repetition count triggering this level."""
    
    reinforcement_strength: float = field(default=1.0)
    """Cumulative reinforcement strength factor."""
    
    saturation_status: str = field(default="none")
    """
    Saturation state:
        - none: Below saturation threshold
        - low: Approaching saturation
        - moderate: Near saturation
        - high: Close to maximum
        - saturated: At or above saturation threshold
    """
    
    last_reinforcement_delta: int = field(default=0)
    """Delta since last reinforcement event."""
    
    @property
    def is_saturated(self) -> bool:
        """Check if accumulation has reached saturation."""
        return self.saturation_status == "saturated"
    
    @property
    def level_category(self) -> str:
        """
        Get human-readable category for current level.
        
        Returns:
            Category string: none, weak, moderate, strong, saturated
        """
        if self.level <= 0:
            return "none"
        elif self.level <= 2:
            return "weak"
        elif self.level <= 3:
            return "moderate"
        elif self.level <= 4:
            return "strong"
        else:
            return "saturated"


@dataclass(frozen=True)
class DecayState:
    """
    Current decay state for a Candidate.
    
    DECAY STATE FIELDS:
        - current_level: Current salience level
        - base_level: Level at start of decay period
        - elapsed_delta: Delta since last increase
        - half_life_reached: Number of half-lives passed
    
    DECAY INVARIANTS:
        DECAY-INV-001: Decay never erases identity
        DECAY-INV-002: Decay is bounded (never negative)
        DECAY-INV-003: State is immutable
    """
    
    current_level: float = field(default=1.0)
    """Current salience level after decay."""
    
    base_level: float = field(default=1.0)
    """Baseline level before decay began."""
    
    elapsed_delta: int = field(default=0)
    """Delta units since last increase."""
    
    half_life_reached: int = field(default=0)
    """Number of half-lives completed."""
    
    @property
    def decay_fraction(self) -> float:
        """
        Calculate fraction of decay (0.0 = no decay, 1.0 = fully decayed).
        
        Returns:
            Decay fraction (bounded 0-1)
        """
        if self.base_level == 0:
            return 0.0
        base_diff = self.base_level - self.current_level
        return max(0.0, min(1.0, base_diff / self.base_level))


@dataclass(frozen=True)
class HabituationState:
    """
    Current habituation state for a Candidate.
    
    HABITUATION (0-1 scale):
        - 0.0: No habituation (full response)
        - 0.5: Moderate habituation (half response)
        - 1.0: Maximum habituation (minimal response)
    
    HABITUATION INVARIANTS:
        HAB-INV-001: Level is bounded (0-1 scale)
        HAB-INV-002: Habituation affects salience only
        HAB-INV-003: State is immutable
    """
    
    level: float = field(default=0.0)
    """Current habituation level (0.0 to 1.0)."""
    
    repetitions: int = field(default=0)
    """Total repetition count triggering habituation."""
    
    last_stimulus_delta: int = field(default=0)
    """Delta since last stimulus event."""
    
    @property
    def is_fully_habituated(self) -> bool:
        """Check if habituation has reached maximum."""
        return self.level >= 1.0
    
    @property
    def response_multiplier(self) -> float:
        """
        Calculate multiplier for salience after habituation.
        
        Returns:
            Multiplier (1.0 = no reduction, 0.0 = fully suppressed)
        """
        # Linear decay: level 0.5 → 50% of response
        return max(0.0, 1.0 - self.level)


@dataclass(frozen=True)
class SensitizationState:
    """
    Current sensitization state for a Candidate.
    
    SENSITIZATION (0-2 scale):
        - 0.0: No sensitization (baseline response)
        - 1.0: Moderate sensitization (doubled response threshold)
        - 2.0: Maximum sensitization (response threshold ×4)
    
    SENSITIZATION INVARIANTS:
        SEN-INV-001: Level is bounded (0 <= level <= maximum)
        SEN-INV-002: Sensitization increases future responses
        SEN-INV-003: State is immutable
    """
    
    level: float = field(default=0.0)
    """Current sensitization level."""
    
    repetitions: int = field(default=0)
    """Repetition count triggering sensitization."""
    
    last_significant_delta: int = field(default=0)
    """Delta since last significant event."""
    
    @property
    def is_max_sensitized(self) -> bool:
        """Check if sensitization has reached maximum."""
        return self.level >= 2.0


@dataclass(frozen=True)
class FatigueState:
    """
    Current fatigue state for a Candidate.
    
    FATIGUE (0-1 scale):
        - 0.0: No fatigue (full contribution capacity)
        - 0.5: Moderate fatigue (half capacity)
        - 1.0: Maximum fatigue (no effective contribution)
    
    FATIGUE INVARIANTS:
        FAT-INV-001: Level is bounded (0-1 scale)
        FAT-INV-002: Fatigue reduces contribution, not identity
        FAT-INV-003: State is immutable
    """
    
    level: float = field(default=0.0)
    """Current fatigue level (0.0 to 1.0)."""
    
    activation_duration: int = field(default=0)
    """Duration of continuous activation."""
    
    last_deactivation_delta: int = field(default=0)
    """Delta since deactivation started."""
    
    @property
    def is_suppressed(self) -> bool:
        """
        Check if fatigue suppresses contribution.
        
        Returns:
            True if contribution is suppressed (fatigue >= 70%)
        """
        return self.level >= 0.7
    
    @property
    def effective_contribution(self) -> float:
        """
        Calculate effective contribution after fatigue reduction.
        
        Returns:
            Contribution factor (1.0 = full, 0.0 = zero)
        """
        return max(0.0, 1.0 - self.level)


@dataclass(frozen=True)
class RecoveryState:
    """
    Current recovery state for a Candidate.
    
    RECOVERY (0-1 scale):
        - 0.0: No recovery progress
        - 0.5: Halfway to full recovery
        - 1.0: Fully recovered
    
    RECOVERY INVARIANTS:
        REC-INV-001: Level is bounded (0-1 scale)
        REC-INV-002: Recovery reverses fatigue/habituation
        REC-INV-003: State is immutable
    """
    
    level: float = field(default=0.0)
    """Current recovery progress (0.0 to 1.0)."""
    
    inactivity_delta: int = field(default=0)
    """Delta since last activation/increase."""
    
    @property
    def is_full_recovery(self) -> bool:
        """Check if full recovery has been achieved."""
        return self.level >= 1.0


@dataclass(frozen=True)
class PersistenceState:
    """
    Current persistence classification.
    
    PERSISTENCE KINDS:
        - TRANSIENT: Very short expected lifetime
        - SHORT_LIVED: Brief relevance period
        - SUSTAINED: Moderately long duration
        - PERSISTENT: Long-term significance
        - RECURRENT: Returns periodically
    
    PERSISTENCE INVARIANTS:
        PER-INV-001: Classification is semantic (not memory permanence)
        PER-INV-002: State evolves through policy only
        PER-INV-003: State is immutable
    """
    
    kind: str = field(default="unknown")
    """Persistence classification."""
    
    elapsed_delta: int = field(default=0)
    """Delta since persistence classification was set."""
    
    @property
    def is_transient(self) -> bool:
        """Check if persistence is transient."""
        return self.kind == "transient"
    
    @property
    def is_persistent(self) -> bool:
        """Check if persistence is persistent."""
        return self.kind == "persistent"


@dataclass(frozen=True)
class StabilityState:
    """
    Current stability classification.
    
    STABILITY STATUSES:
        - VOLATILE: Rapid change expected
        - UNSTABLE: Some instability present
        - STABLE: Reasonable consistency
        - ROBUST: High temporal consistency
    
    STABILITY INVARIANTS:
        STA-INV-001: Status is semantic (not uncertainty)
        STA-INV-002: State evolves through policy only
        STA-INV-003: State is immutable
    """
    
    status: str = field(default="unknown")
    """Stability classification."""
    
    elapsed_delta: int = field(default=0)
    """Delta since last stability assessment."""
    
    @property
    def is_robust(self) -> bool:
        """Check if stability is robust."""
        return self.status == "robust"
    
    @property
    def is_volatile(self) -> bool:
        """Check if stability is volatile."""
        return self.status == "volatile"


@dataclass(frozen=True)
class AdaptiveCandidateState:
    """
    Complete adaptive state for a single Candidate.
    
    Contains all adaptive descriptors that evolve over semantic time.
    
    ADAPTIVE CANDIDATE STATE INVARIANTS:
        ACST-INV-001: All fields are immutable
        ACST-INV-002: Identity matches source candidate
        ACST-INV-003: State is fully specified
    """
    
    candidate_id: str = field(default="")
    """Matching state_identity from source Candidate."""
    
    accumulation: AccumulationState = field(default_factory=AccumulationState)
    """Current accumulation state."""
    
    decay: DecayState = field(default_factory=DecayState)
    """Current decay state."""
    
    habituation: HabituationState = field(default_factory=HabituationState)
    """Current habituation state."""
    
    sensitization: SensitizationState = field(default_factory=SensitizationState)
    """Current sensitization state."""
    
    fatigue: FatigueState = field(default_factory=FatigueState)
    """Current fatigue state."""
    
    recovery: RecoveryState = field(default_factory=RecoveryState)
    """Current recovery state."""
    
    persistence: PersistenceState = field(default_factory=PersistenceState)
    """Current persistence classification."""
    
    stability: StabilityState = field(default_factory=StabilityState)
    """Current stability classification."""
    
    @property
    def total_adaptive_level(self) -> float:
        """
        Calculate combined adaptive effect on salience.
        
        Returns:
            Combined factor (multiplier for base salience)
        """
        # Base multiplier (no change)
        base = 1.0
        
        # Apply habituation reduction
        habituated = base * self.habituation.response_multiplier
        
        # Apply recovery boost if not fully fatigued
        if not self.fatigue.is_suppressed:
            # Recovery adds to effective contribution
            return habituated * self.fatigue.effective_contribution
        
        return habituated


@dataclass(frozen=True)
class CandidateAdaptiveDeltas:
    """
    Changes in adaptive state during a single update.
    
    Used for traceability and debugging.
    
    DELTAS INVARIANTS:
        DLT-INV-001: All fields are immutable
        DLT-INV-002: Contains change deltas only (not absolute values)
        DLT-INV-003: State is immutable
    """
    
    candidate_id: str = field(default="")
    """Candidate identity."""
    
    accumulation_delta: float = field(default=0.0)
    """Change in accumulation level."""
    
    decay_delta: float = field(default=0.0)
    """Change in decay state."""
    
    habituation_delta: float = field(default=0.0)
    """Change in habituation level."""
    
    sensitization_delta: float = field(default=0.0)
    """Change in sensitization level."""
    
    fatigue_delta: float = field(default=0.0)
    """Change in fatigue level."""
    
    recovery_delta: float = field(default=0.0)
    """Change in recovery progress."""
    
    persistence_kind_changed: bool = field(default=False)
    """Whether persistence classification changed."""
    
    stability_status_changed: bool = field(default=False)
    """Whether stability status changed."""