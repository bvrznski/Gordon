# Salience Network State Enums
# ============================
#
# Canonical implementation of State enums (Phase 4.8.4).
#

"""
State enums defining canonical semantic categories for Salience State.

These enums represent:
    - Snapshot kinds: CURRENT, CANDIDATE, HISTORICAL, etc.
    - Salience levels: UNKNOWN, NEGLIGIBLE, LOW, MODERATE, HIGH, CRITICAL
    - Activation statuses: INACTIVE, LATENT, PRIMED, ACTIVE, ELEVATED, DOMINANT, SUPPRESSED, DEGRADED
    - Readiness states: UNAVAILABLE, INCOMPLETE, PROVISIONAL, READY, DEGRADED, INVALID, STALE
    - Persistence kinds: TRANSIENT, SHORT_LIVED, SUSTAINED, PERSISTENT, RECURRENT, DORMANT
    - Decay kinds: NONE, SLOW, MODERATE, RAPID, EXPIRED
    - Competition statuses: UNRESOLVED, RESOLVED, CONFLICTED, SUPPRESSED
"""

from __future__ import annotations

from enum import Enum


class SalienceSnapshotKind(Enum):
    """
    Canonical snapshot semantic kind.
    
    Snapshot kinds distinguish between:
        - CURRENT: The present salience assessment
        - CANDIDATE: A proposed or provisional assessment under consideration
        - HISTORICAL: A past assessment preserved for lineage
        - BASELINE: A reference state for comparison
        - PROVISIONAL: An incomplete assessment marked with limitations
        - SUPERSEDED: A replaced state preserved for lineage
        - INVALID: A structurally invalid state (for quarantine)
        - REFERENCE: An external reference state
    """
    
    CURRENT = "current"
    """The present salience assessment."""
    
    CANDIDATE = "candidate"
    """A proposed or provisional assessment under consideration."""
    
    HISTORICAL = "historical"
    """A past assessment preserved for lineage."""
    
    BASELINE = "baseline"
    """A reference state for comparison."""
    
    PROVISIONAL = "provisional"
    """An incomplete assessment marked with limitations."""
    
    SUPERSEDED = "superseded"
    """A replaced state preserved for lineage."""
    
    INVALID = "invalid"
    """A structurally invalid state (for quarantine)."""
    
    REFERENCE = "reference"
    """An external reference state."""


class SalienceLevel(Enum):
    """
    Canonical salience level semantic scale.
    
    This enum defines bounded levels of significance without numeric scoring.
    It preserves UNKNOWN as a distinct semantic category from NEGLIGIBLE.
    
    Levels:
        - UNKNOWN: Insufficient evidence to classify
        - NEGLIGIBLE: No meaningful significance
        - LOW: Minimal significance
        - MODERATE: Noticeable significance
        - HIGH: Strong significance
        - CRITICAL: Maximum significance requiring immediate attention
    """
    
    UNKNOWN = "unknown"
    """Insufficient evidence to classify significance."""
    
    NEGLIGIBLE = "negligible"
    """No meaningful significance (not zero, just minimal)."""
    
    LOW = "low"
    """Minimal but non-zero significance."""
    
    MODERATE = "moderate"
    """Noticeable significance requiring some attention."""
    
    HIGH = "high"
    """Strong significance warranting priority consideration."""
    
    CRITICAL = "critical"
    """Maximum significance requiring immediate attention and action."""
    
    @property
    def is_defined(self) -> bool:
        """Indicates whether this level has been determined (not UNKNOWN)."""
        return self != SalienceLevel.UNKNOWN
    
    @property
    def numeric_value(self) -> int:
        """
        Return the numeric ordering value of this level.
        
        Returns:
            0 for UNKNOWN, 1-6 for defined levels.
        """
        values = {
            SalienceLevel.UNKNOWN: 0,
            SalienceLevel.NEGLIGIBLE: 1,
            SalienceLevel.LOW: 2,
            SalienceLevel.MODERATE: 3,
            SalienceLevel.HIGH: 4,
            SalienceLevel.CRITICAL: 5,
        }
        return values.get(self, 0)


class SalienceActivationStatus(Enum):
    """
    Canonical activation status category.
    
    Activation describes semantic availability without runtime behavior:
        - INACTIVE: Not semantically available
        - LATENT: Available but not prominent
        - PRIMED: Ready for immediate consideration
        - ACTIVE: Currently under consideration
        - ELEVATED: Above normal prominence
        - DOMINANT: Primary focus of attention
        - SUPPRESSED: Explicitly prevented from consideration
        - DEGRADED: Available but with reduced reliability
    """
    
    INACTIVE = "inactive"
    """Not semantically available for downstream consumption."""
    
    LATENT = "latent"
    """Semantically available but not prominent."""
    
    PRIMED = "primed"
    """Ready for immediate consideration when needed."""
    
    ACTIVE = "active"
    """Currently under consideration by downstream systems."""
    
    ELEVATED = "elevated"
    """Above normal prominence without being primary."""
    
    DOMINANT = "dominant"
    """Primary focus of current processing."""
    
    SUPPRESSED = "suppressed"
    """Explicitly prevented from consideration despite significance."""
    
    DEGRADED = "degraded"
    """Available but with reduced reliability or completeness."""


class SalienceReadiness(Enum):
    """
    Canonical readiness status for downstream consumption.
    
    Readiness distinguishes:
        - UNAVAILABLE: Not accessible
        - INCOMPLETE: Lacking complete information
        - PROVISIONAL: Acceptable with known limitations
        - READY: Fully acceptable for normal use
        - DEGRADED: Usable but with meaningful limitations
        - INVALID: Cannot be used due to structural issues
        - STALE: Information may no longer be current
    """
    
    UNAVAILABLE = "unavailable"
    """Not accessible or not intended for consumption."""
    
    INCOMPLETE = "incomplete"
    """Lacking some information but structurally valid."""
    
    PROVISIONAL = "provisional"
    """Acceptable with explicit known limitations."""
    
    READY = "ready"
    """Fully acceptable for normal downstream consumption."""
    
    DEGRADED = "degraded"
    """Usable but with meaningful semantic limitations."""
    
    INVALID = "invalid"
    """Cannot be used due to structural or semantic issues."""
    
    STALE = "stale"
    """May no longer reflect current conditions despite validity."""


class SaliencePersistenceKind(Enum):
    """
    Canonical persistence classification.
    
    Persistence describes expected semantic continuity without temporal computation:
        - TRANSIENT: Very short-lived significance
        - SHORT_LIVED: Brief but meaningful persistence
        - SUSTAINED: Moderate duration significance
        - PERSISTENT: Long-term semantic relevance
        - RECURRENT: Returns periodically
        - DORMANT: Preserved potential for re-emergence
    """
    
    TRANSIENT = "transient"
    """Expected to last only briefly."""
    
    SHORT_LIVED = "short_lived"
    """Expected to persist for a limited duration."""
    
    SUSTAINED = "sustained"
    """Expected to maintain significance for moderate time."""
    
    PERSISTENT = "persistent"
    """Expected to remain relevant over extended periods."""
    
    RECURRENT = "recurrent"
    """Expected to re-emerge periodically after intervals."""
    
    DORMANT = "dormant"
    """Preserved potential for re-emergence without current activity."""


class SalienceDecayKind(Enum):
    """
    Canonical decay classification.
    
    Decay describes expected loss of salience or validity:
        - NONE: No expected decay
        - SLOW: Gradual semantic degradation
        - MODERATE: Noticeable degradation over time
        - RAPID: Quick loss of relevance
        - EXPIRED: No longer valid
    """
    
    NONE = "none"
    """No expected semantic decay or loss of validity."""
    
    SLOW = "slow"
    """Expected to degrade gradually over extended periods."""
    
    MODERATE = "moderate"
    """Expected to degrade at a noticeable rate."""
    
    RAPID = "rapid"
    """Expected to lose relevance quickly."""
    
    EXPIRED = "expired"
    """No longer considered valid or relevant."""


class SalienceCompetitionStatus(Enum):
    """
    Canonical competition resolution status.
    
    Competition status describes the state of multiple salient candidates:
        - UNRESOLVED: Multiple candidates remain in contention
        - RESOLVED: A winner has been selected (by external process)
        - CONFLICTED: Candidates are in direct conflict
        - SUPPRESSED: All candidates suppressed by higher-order decision
    """
    
    UNRESOLVED = "unresolved"
    """Multiple candidates remain in contention."""
    
    RESOLVED = "resolved"
    """A dominant candidate has been selected externally."""
    
    CONFLICTED = "conflicted"
    """Candidates are in direct semantic conflict."""
    
    SUPPRESSED = "suppressed"
    """All candidates suppressed by higher-order decision."""


class ValidationSeverity(Enum):
    """
    Canonical validation finding severity.
    
    Severity categories distinguish blocking from non-blocking issues:
        - INFO: Informational, not a finding
        - WARNING: Non-blocking concern
        - ERROR: Blocking structural or semantic issue
        - FATAL: Invalid state requiring quarantine
    """
    
    INFO = "info"
    """Informational message, not a validation issue."""
    
    WARNING = "warning"
    """Non-blocking concern that should be noted."""
    
    ERROR = "error"
    """Blocking issue preventing normal use."""
    
    FATAL = "fatal"
    """Invalid state requiring quarantine or rejection."""