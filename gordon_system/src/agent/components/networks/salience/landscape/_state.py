# Salience Network Landscape State
# ================================

"""
Canonical Global Salience Landscape state model (Phase 4.8.8).

The LandscapeState is the immutable, semantic result of landscape construction.
It represents the global salience field without runtime behavior.

LANDSCAPE STATE INVARIANTS:
    LST-INV-001: State is deeply frozen dataclass
    LST-INV-002: All fields are semantic descriptors
    LST-INV-003: No runtime references or callbacks
    LST-INV-004: Candidate identity preserved throughout
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# GLOBAL ACTIVATION ENUMS
# =============================================================================

GLOBAL_ACTIVATION_LEVELS = (
    "QUIESCENT",  # No activity detected
    "LOW",        # Minimal activation present
    "MODERATE",   # Balanced activation level
    "HIGH",       # Significant activity occurring
    "EXTREME",    # Maximum possible activation
)


@dataclass(frozen=True)
class GlobalActivation:
    """
    Estimated global salience intensity.
    
    ACTIVATION INVARIANTS:
        LACT-INV-001: Level is one of canonical values
        LACT-INV-002: Value is bounded (0.0-1.0 scale)
        LACT-INV-003: Evidence preserved for reconstruction
    """
    
    level: str = field(default="QUIESCENT")
    """Canonical activation level."""
    
    value: float = field(default=0.0)
    """Numeric activation value (0.0-1.0)."""
    
    evidence_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for activation estimation."""
    
    @property
    def is_quiescent(self) -> bool:
        """Check if system is quiescent."""
        return self.level == "QUIESCENT"
    
    @property
    def is_low(self) -> bool:
        """Check if system has low activation."""
        return self.level == "LOW"
    
    @property
    def is_moderate(self) -> bool:
        """Check if system has moderate activation."""
        return self.level == "MODERATE"
    
    @property
    def is_high(self) -> bool:
        """Check if system has high activation."""
        return self.level == "HIGH"
    
    @property
    def is_extreme(self) -> bool:
        """Check if system has extreme activation."""
        return self.level == "EXTREME"


# =============================================================================
# BASELINE SALIENCE
# =============================================================================

BASELINE_LEVELS = (
    "LOW",      # Quiet environment reference point
    "MODERATE", # Balanced environment reference point
    "HIGH",     # Chaotic environment reference point
)


@dataclass(frozen=True)
class BaselineSalience:
    """
    Estimated baseline salience for the current semantic environment.
    
    BASELINE INVARIANTS:
        LBASE-INV-001: Level is one of canonical values
        LBASE-INV-002: Reference point for Candidate interpretation
        LBASE-INV-003: Context-dependent but not Candidate-specific
    """
    
    level: str = field(default="MODERATE")
    """Canonical baseline level."""
    
    reference_delta: int = field(default=0)
    """Semantic delta when baseline was established."""
    
    context_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Context descriptors for baseline interpretation."""
    
    @property
    def is_low_baseline(self) -> bool:
        """Check if baseline is low."""
        return self.level == "LOW"
    
    @property
    def is_moderate_baseline(self) -> bool:
        """Check if baseline is moderate."""
        return self.level == "MODERATE"
    
    @property
    def is_high_baseline(self) -> bool:
        """Check if baseline is high."""
        return self.level == "HIGH"


# =============================================================================
# RESOURCE PRESSURE
# =============================================================================

PRESSURE_LEVELS = (
    "MINIMAL",   # No significant pressure
    "LOW",       # Minor semantic competition
    "MODERATE",  # Noticeable resource demand
    "HIGH",      # Significant semantic competition
    "CRITICAL",  # Maximum pressure - resources strained
)


@dataclass(frozen=True)
class ResourcePressure:
    """
    Estimated semantic competition for cognitive resources.
    
    PRESSURE INVARIANTS:
        LPRES-INV-001: Level is one of canonical values
        LPRES-INV-002: Advisory only (not scheduling)
        LPRES-INV-003: Preserves supporting rationale
    """
    
    level: str = field(default="MINIMAL")
    """Canonical pressure level."""
    
    value: float = field(default=0.0)
    """Numeric pressure value (0.0-1.0)."""
    
    contributors: Tuple[str, ...] = field(default_factory=tuple)
    """Identified contributors to pressure."""
    
    pressure_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for pressure estimation."""
    
    @property
    def is_minimal(self) -> bool:
        """Check if pressure is minimal."""
        return self.level == "MINIMAL"
    
    @property
    def is_low_pressure(self) -> bool:
        """Check if pressure is low."""
        return self.level == "LOW"
    
    @property
    def is_moderate_pressure(self) -> bool:
        """Check if pressure is moderate."""
        return self.level == "MODERATE"
    
    @property
    def is_high_pressure(self) -> bool:
        """Check if pressure is high."""
        return self.level == "HIGH"
    
    @property
    def is_critical_pressure(self) -> bool:
        """Check if pressure is critical."""
        return self.level == "CRITICAL"


# =============================================================================
# COGNITIVE LOAD
# =============================================================================

COGNITIVE_LOAD_LEVELS = (
    "MINIMAL",   # Negligible processing demand
    "LOW",       # Minor processing required
    "MODERATE",  # Noticeable processing load
    "HIGH",      # Significant processing demand
    "OVERLOADED",# Processing capacity exceeded
)


@dataclass(frozen=True)
class CognitiveLoad:
    """
    Estimated overall processing demand.
    
    LOAD INVARIANTS:
        LLOAD-INV-001: Level is one of canonical values
        LLOAD-INV-002: Distinct from environmental load
        LLOAD-INV-003: Advisory only (not scheduling)
    """
    
    level: str = field(default="MINIMAL")
    """Canonical load level."""
    
    value: float = field(default=0.0)
    """Numeric load value (0.0-1.0)."""
    
    processing_demand: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic descriptors of processing demands."""
    
    load_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for load estimation."""
    
    @property
    def is_minimal_load(self) -> bool:
        """Check if load is minimal."""
        return self.level == "MINIMAL"
    
    @property
    def is_low_load(self) -> bool:
        """Check if load is low."""
        return self.level == "LOW"
    
    @property
    def is_moderate_load(self) -> bool:
        """Check if load is moderate."""
        return self.level == "MODERATE"
    
    @property
    def is_high_load(self) -> bool:
        """Check if load is high."""
        return self.level == "HIGH"
    
    @property
    def is_overloaded(self) -> bool:
        """Check if system is overloaded."""
        return self.level == "OVERLOADED"


# =============================================================================
# ENVIRONMENTAL LOAD
# =============================================================================

ENVIRONMENTAL_LOAD_LEVELS = (
    "LOW",       # Simple semantic environment
    "MODERATE",  # Balanced complexity
    "HIGH",      # Complex simultaneous events
    "EXTREME",   # Maximum environmental pressure
)


@dataclass(frozen=True)
class EnvironmentalLoad:
    """
    Estimated external complexity and event density.
    
    ENVIRONMENT INVARIANTS:
        LENV-INV-001: Level is one of canonical values
        LENV-INV-002: External to cognitive system
        LENV-INV-003: Distinct from processing load
    """
    
    level: str = field(default="LOW")
    """Canonical environmental load level."""
    
    event_density: int = field(default=0)
    """Estimated number of concurrent events."""
    
    observation_diversity: int = field(default=0)
    """Number of distinct observation types."""
    
    change_rate: float = field(default=0.0)
    """Rate of semantic change (0-1)."""
    
    environmental_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for environmental assessment."""
    
    @property
    def is_low_environment(self) -> bool:
        """Check if environment is low load."""
        return self.level == "LOW"
    
    @property
    def is_moderate_environment(self) -> bool:
        """Check if environment has moderate load."""
        return self.level == "MODERATE"
    
    @property
    def is_high_environment(self) -> bool:
        """Check if environment has high load."""
        return self.level == "HIGH"
    
    @property
    def is_extreme_environment(self) -> bool:
        """Check if environment is extreme."""
        return self.level == "EXTREME"


# =============================================================================
# DENSITY ESTIMATORS
# =============================================================================

NOVELTY_LEVELS = (
    "NONE",      # No novel information
    "LOW",       # Minimal novelty present
    "MODERATE",  # Noticeable novelty
    "HIGH",      # Significant novelty concentration
    "SATURATED", # Maximum possible novelty
)


@dataclass(frozen=True)
class NoveltyDensity:
    """
    Estimated concentration of novel information.
    
    DENSITY INVARIANTS:
        LDENS-INV-001: Level is one of canonical values
        LDENS-INV-002: Global metric only
        LDENS-INV-003: Not Candidate-specific
    """
    
    level: str = field(default="NONE")
    """Canonical novelty level."""
    
    value: float = field(default=0.0)
    """Numeric density value (0.0-1.0)."""
    
    novel_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of candidates identified as novel."""
    
    novelty_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for novelty estimation."""
    
    @property
    def is_none_novelty(self) -> bool:
        """Check if no novelty detected."""
        return self.level == "NONE"
    
    @property
    def is_low_novelty(self) -> bool:
        """Check if low novelty present."""
        return self.level == "LOW"
    
    @property
    def is_moderate_novelty(self) -> bool:
        """Check if moderate novelty present."""
        return self.level == "MODERATE"
    
    @property
    def is_high_novelty(self) -> bool:
        """Check if high novelty present."""
        return self.level == "HIGH"
    
    @property
    def is_saturated_novelty(self) -> bool:
        """Check if novel information saturated."""
        return self.level == "SATURATED"


# =============================================================================

CONFLICT_LEVELS = (
    "LOW",       # Minimal conflict
    "MODERATE",  # Noticeable conflict concentration
    "HIGH",      # Significant conflicts present
    "EXTREME",   # Maximum conflict density
)


@dataclass(frozen=True)
class ConflictDensity:
    """
    Estimated concentration of unresolved conflicts.
    
    CONFLICT DENSITY INVARIANTS:
        LCD-INV-001: Level is one of canonical values
        LCD-INV-002: Preserves conflict information
        LCD-INV-003: Advisory only (not resolution)
    """
    
    level: str = field(default="LOW")
    """Canonical conflict level."""
    
    value: float = field(default=0.0)
    """Numeric density value (0.0-1.0)."""
    
    conflict_count: int = field(default=0)
    """Number of identified conflicts."""
    
    conflict_types: Tuple[str, ...] = field(default_factory=tuple)
    """Types of conflicts present."""
    
    unresolved_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of unresolved conflicts."""
    
    @property
    def is_low_conflict(self) -> bool:
        """Check if low conflict concentration."""
        return self.level == "LOW"
    
    @property
    def is_moderate_conflict(self) -> bool:
        """Check if moderate conflict concentration."""
        return self.level == "MODERATE"
    
    @property
    def is_high_conflict(self) -> bool:
        """Check if high conflict concentration."""
        return self.level == "HIGH"
    
    @property
    def is_extreme_conflict(self) -> bool:
        """Check if extreme conflict concentration."""
        return self.level == "EXTREME"


# =============================================================================

UNCERTAINTY_LEVELS = (
    "LOW",       # Minimal uncertainty
    "MODERATE",  # Noticeable uncertainty
    "HIGH",      # Significant uncertainty present
    "EXTREME",   # Maximum possible uncertainty
)


@dataclass(frozen=True)
class UncertaintyDensity:
    """
    Estimated global uncertainty level.
    
    UNCERTAINTY DENSITY INVARIANTS:
        LUD-INV-001: Level is one of canonical values
        LUD-INV-002: Distinct from confidence
        LUD-INV-003: Preserves uncertainty basis
    """
    
    level: str = field(default="LOW")
    """Canonical uncertainty level."""
    
    value: float = field(default=0.0)
    """Numeric density value (0.0-1.0)."""
    
    uncertain_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of candidates with high uncertainty."""
    
    missing_information_count: int = field(default=0)
    """Number of identified information gaps."""
    
    @property
    def is_low_uncertainty(self) -> bool:
        """Check if low uncertainty present."""
        return self.level == "LOW"
    
    @property
    def is_moderate_uncertainty(self) -> bool:
        """Check if moderate uncertainty present."""
        return self.level == "MODERATE"
    
    @property
    def is_high_uncertainty(self) -> bool:
        """Check if high uncertainty present."""
        return self.level == "HIGH"
    
    @property
    def is_extreme_uncertainty(self) -> bool:
        """Check if extreme uncertainty present."""
        return self.level == "EXTREME"


# =============================================================================

URGENCY_LEVELS = (
    "SPARSE",      # Minimal urgency present
    "LOCALIZED",   # Urgency in specific regions
    "DISTRIBUTED", # Multiple urgent regions
    "WIDESPREAD",  # Widespread urgency
    "CRITICAL",    # Maximum possible urgency distribution
)


@dataclass(frozen=True)
class UrgencyDensity:
    """
    Estimated distribution of urgent Candidates.
    
    URGENCY DENSITY INVARIANTS:
        LUD-INV-001: Level is one of canonical values
        LUD-INV-002: No scheduling semantics
        LUD-INV-003: Preserves urgency basis
    """
    
    level: str = field(default="SPARSE")
    """Canonical urgency distribution."""
    
    value: float = field(default=0.0)
    """Numeric density value (0.0-1.0)."""
    
    urgent_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of candidates with high urgency."""
    
    urgency_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for urgency estimation."""
    
    @property
    def is_sparse_urgency(self) -> bool:
        """Check if sparse urgency distribution."""
        return self.level == "SPARSE"
    
    @property
    def is_localized_urgency(self) -> bool:
        """Check if localized urgency distribution."""
        return self.level == "LOCALIZED"
    
    @property
    def is_distributed_urgency(self) -> bool:
        """Check if distributed urgency distribution."""
        return self.level == "DISTRIBUTED"
    
    @property
    def is_widespread_urgency(self) -> bool:
        """Check if widespread urgency distribution."""
        return self.level == "WIDESPREAD"
    
    @property
    def is_critical_urgency(self) -> bool:
        """Check if critical urgency distribution."""
        return self.level == "CRITICAL"


# =============================================================================
# CONTEXTUAL GRADIENTS
# =============================================================================

@dataclass(frozen=True)
class ContextualGradient:
    """
    Semantic gradient in a particular context dimension.
    
    GRADIENT INVARIANTS:
        LG-INV-001: Gradient is immutable (frozen dataclass)
        LG-INV-002: No runtime references
        LG-INV-003: Provides semantic bias only
    """
    
    gradient_id: str = field(default="")
    """Unique identifier for this gradient."""
    
    context_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Context descriptors for this gradient."""
    
    direction: float = field(default=0.0)
    """Gradient direction (-1 to +1)."""
    
    strength: float = field(default=0.0)
    """Gradient strength (0-1 scale)."""
    
    active_candidates: Tuple[str, ...] = field(default_factory=tuple)
    """Candidates most affected by this gradient."""
    
    @property
    def is_positive(self) -> bool:
        """Check if gradient direction is positive."""
        return self.direction > 0.0
    
    @property
    def is_negative(self) -> bool:
        """Check if gradient direction is negative."""
        return self.direction < 0.0


# =============================================================================
# HOTSPOTS
# =============================================================================

HOTSPOT_CATEGORIES = (
    "THREAT",      # Threat-related concentration
    "NOVELTY",     # Novel information concentration
    "GOAL",        # Goal-relevant concentration
    "CONFLICT",    # Conflict-related concentration
    "UNCERTAINTY", # Uncertainty-related concentration
)


@dataclass(frozen=True)
class SalienceHotspot:
    """
    Concentrated region of salience in the landscape.
    
    HOTSPOT INVARIANTS:
        LH-INV-001: Hotspot is immutable (frozen dataclass)
        LH-INV-002: Never selects Candidates
        LH-INV-003: Summarizes concentration only
    """
    
    hotspot_id: str = field(default="")
    """Unique identifier for this hotspot."""
    
    category: str = field(default="THREAT")
    """Hotspot category."""
    
    strength: float = field(default=0.0)
    """Hotspot strength (0-1 scale)."""
    
    extent: float = field(default=0.0)
    """Spatial extent of hotspot (0-1 scale)."""
    
    candidate_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Ids of candidates in this hotspot."""
    
    hotspot_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for hotspot detection."""
    
    @property
    def is_threat_hotspot(self) -> bool:
        """Check if this is a threat hotspot."""
        return self.category == "THREAT"
    
    @property
    def is_novelty_hotspot(self) -> bool:
        """Check if this is a novelty hotspot."""
        return self.category == "NOVELTY"
    
    @property
    def is_goal_hotspot(self) -> bool:
        """Check if this is a goal hotspot."""
        return self.category == "GOAL"
    
    @property
    def is_conflict_hotspot(self) -> bool:
        """Check if this is a conflict hotspot."""
        return self.category == "CONFLICT"
    
    @property
    def is_uncertainty_hotspot(self) -> bool:
        """Check if this is an uncertainty hotspot."""
        return self.category == "UNCERTAINTY"


# =============================================================================
# SYSTEM COHERENCE
# =============================================================================

COHERENCE_LEVELS = (
    "COHERENT",         # Semantic consistency maintained
    "PARTIALLY_COHERENT",# Some inconsistency present
    "FRAGMENTED",       # Multiple inconsistent regions
    "CONFLICTED",       # Maximum possible fragmentation
)


@dataclass(frozen=True)
class SystemCoherence:
    """
    Estimated semantic coherence of the landscape.
    
    COHERENCE INVARIANTS:
        LCOH-INV-001: Level is one of canonical values
        LCOH-INV-002: Distinct from confidence
        LCOH-INV-003: Preserves conflict information
    """
    
    level: str = field(default="COHERENT")
    """Canonical coherence level."""
    
    value: float = field(default=1.0)
    """Numeric coherence value (0.0-1.0)."""
    
    consistency_score: float = field(default=1.0)
    """Semantic consistency score."""
    
    conflict_score: float = field(default=0.0)
    """Conflict presence score."""
    
    coherence_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for coherence estimation."""
    
    @property
    def is_coherent(self) -> bool:
        """Check if system is coherent."""
        return self.level == "COHERENT"
    
    @property
    def is_partially_coherent(self) -> bool:
        """Check if system is partially coherent."""
        return self.level == "PARTIALLY_COHERENT"
    
    @property
    def is_fragmented(self) -> bool:
        """Check if system is fragmented."""
        return self.level == "FRAGMENTED"
    
    @property
    def is_conflicted(self) -> bool:
        """Check if system is conflicted."""
        return self.level == "CONFLICTED"


# =============================================================================
# SYSTEM READINESS
# =============================================================================

READINESS_LEVELS = (
    "READY",      # Ready for downstream processing
    "LIMITED",    # Processing available but constrained
    "DEGRADED",   # Reduced processing capacity
    "UNSTABLE",   # Processing unstable or inconsistent
)


@dataclass(frozen=True)
class SystemReadiness:
    """
    Estimated readiness for downstream Attention processing.
    
    READINESS INVARIANTS:
        LRDY-INV-001: Level is one of canonical values
        LRDY-INV-002: Advisory only (no activation)
        LRDY-INV-003: Preserves uncertainty
    """
    
    level: str = field(default="READY")
    """Canonical readiness level."""
    
    value: float = field(default=1.0)
    """Numeric readiness value (0.0-1.0)."""
    
    capacity_available: float = field(default=1.0)
    """Fraction of processing capacity available."""
    
    readiness_basis: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic basis for readiness estimation."""
    
    @property
    def is_ready(self) -> bool:
        """Check if system is ready."""
        return self.level == "READY"
    
    @property
    def is_limited(self) -> bool:
        """Check if system is limited."""
        return self.level == "LIMITED"
    
    @property
    def is_degraded(self) -> bool:
        """Check if system is degraded."""
        return self.level == "DEGRADED"
    
    @property
    def is_unstable(self) -> bool:
        """Check if system is unstable."""
        return self.level == "UNSTABLE"


# =============================================================================
# LANDSCAPE STATE
# =============================================================================

@dataclass(frozen=True)
class LandscapeState:
    """
    Immutable result of Global Salience Landscape construction.
    
    A landscape state contains:
        - Global activation estimate
        - Baseline salience reference point
        - Resource pressure estimate
        - Cognitive load estimate
        - Environmental load estimate
        - Novelty, conflict, uncertainty densities
        - Urgency distribution
        - Contextual gradients
        - Salience hotspots
        - System coherence
        - System readiness
    
    LANDSCAPE STATE INVARIANTS:
        LST-INV-001: State is deeply frozen dataclass
        LST-INV-002: All fields are semantic descriptors
        LST-INV-003: No runtime references or callbacks
        LST-INV-004: Candidate identity preserved throughout
    """
    
    # Identity for traceability
    identity: str = field(default="")
    """Unique identifier matching source request."""
    
    # Global activation
    global_activation: GlobalActivation = field(default_factory=GlobalActivation)
    """Estimated overall salience intensity."""
    
    # Baseline reference point
    baseline_salience: BaselineSalience = field(default_factory=BaselineSalience)
    """Reference point for Candidate interpretation."""
    
    # Resource and processing estimates
    resource_pressure: ResourcePressure = field(default_factory=ResourcePressure)
    """Semantic competition for cognitive resources."""
    
    cognitive_load: CognitiveLoad = field(default_factory=CognitiveLoad)
    """Estimated overall processing demand."""
    
    environmental_load: EnvironmentalLoad = field(default_factory=EnvironmentalLoad)
    """External complexity estimate."""
    
    # Density estimates
    novelty_density: NoveltyDensity = field(default_factory=NoveltyDensity)
    """Concentration of novel information."""
    
    conflict_density: ConflictDensity = field(default_factory=ConflictDensity)
    """Concentration of unresolved conflicts."""
    
    uncertainty_density: UncertaintyDensity = field(default_factory=UncertaintyDensity)
    """Global uncertainty level."""
    
    urgency_density: UrgencyDensity = field(default_factory=UrgencyDensity)
    """Distribution of urgent Candidates."""
    
    # Contextual structure
    contextual_gradients: Tuple[ContextualGradient, ...] = field(default_factory=tuple)
    """Semantic gradients across contexts."""
    
    salience_hotspots: Tuple[SalienceHotspot, ...] = field(default_factory=tuple)
    """Concentrated regions of salience."""
    
    # Global properties
    system_coherence: SystemCoherence = field(default_factory=SystemCoherence)
    """Estimated semantic coherence."""
    
    system_readiness: SystemReadiness = field(default_factory=SystemReadiness)
    """Estimated readiness for downstream processing."""
    
    # Metadata
    landscape_revision: int = field(default=1)
    """Landscape revision number (increments on update)."""
    
    trace: Tuple[str, ...] = field(default_factory=tuple)
    """Trace records of construction decisions."""
    
    @property
    def candidate_count(self) -> int:
        """Return total candidates in hotspots."""
        count = 0
        for hotspot in self.salience_hotspots:
            count += len(hotspot.candidate_ids)
        return count
    
    @property
    def has_hotspots(self) -> bool:
        """Check if any hotspots detected."""
        return len(self.salience_hotspots) > 0
    
    @property
    def is_ready_for_attention(self) -> bool:
        """Check if system is ready for Attention allocation."""
        return self.system_readiness.is_ready and not self.global_activation.is_extreme
    
    def get_hotspots_by_category(self, category: str) -> tuple[SalienceHotspot, ...]:
        """
        Retrieve hotspots of a specific category.
        
        Args:
            category: Hotspot category to filter for
            
        Returns:
            Tuple of matching hotspots (possibly empty)
        """
        return tuple(h for h in self.salience_hotspots if h.category == category)