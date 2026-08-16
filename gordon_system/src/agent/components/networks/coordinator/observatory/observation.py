# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Observation Models
=================

The core data structures for architectural observations.

OBSERVATION LAWS (from spec)
----------------------------
OBSERVATION-LAW-001: Every Observation shall possess one stable semantic identity.
OBSERVATION-LAW-002: Observations shall remain immutable.
OBSERVATION-LAW-003: Equivalent observation requests shall produce equivalent observations.
OBSERVATION-LAW-004: Observation scope shall remain explicit.
OBSERVATION-LAW-005: Observation windows shall remain explicit.
OBSERVATION-LAW-006: Observations shall preserve provenance.
OBSERVATION-LAW-007: Observation revisions shall preserve lineage.
OBSERVATION-LAW-008: Observation construction shall remain deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# =============================================================================
# OBSERVATION KINDS
# =============================================================================

class ObservationKind(Enum):
    """
    Canonical kinds of observations.
    
    OBSERVATION-LAW-002: Observation kind is stable and explicit.
    """
    HEALTH = "health"
    """Health status observation."""
    
    PERFORMANCE = "performance"
    """Performance metrics observation."""
    
    LATENCY = "latency"
    """Latency measurements."""
    
    THROUGHPUT = "throughput"
    """Throughput measurements."""
    
    COORDINATION = "coordination"
    """Coordination pattern observations."""
    
    SYNCHRONIZATION = "synchronization"
    """Synchronization observations."""
    
    RESOURCE = "resource"
    """Resource utilization observations."""
    
    DEPENDENCY = "dependency"
    """Dependency analysis observations."""
    
    FAILURE = "failure"
    """Failure and error observations."""
    
    RECOVERY = "recovery"
    """Recovery process observations."""
    
    TREND = "trend"
    """Trend analysis observations."""
    
    ANOMALY = "anomaly"
    """Anomaly detection observations."""
    
    BOTTLENECK = "bottleneck"
    """Bottleneck identification observations."""
    
    OPTIMIZATION = "optimization"
    """Optimization recommendation observations."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified observation kind."""


# =============================================================================
# OBSERVATION WINDOW
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservationWindow:
    """
    Temporal window for an observation.
    
    WINDOW-LAW-001: Window boundaries are explicit and immutable.
    WINDOW-LAW-002: Windows may be absolute or relative to a reference point.
    
    OBSERVATION-LAW-005: Observation windows shall remain explicit.
    """
    
    start_epoch: int = 0
    """Start epoch identifier."""
    
    end_epoch: int = 1
    """End epoch identifier."""
    
    window_kind: str = "epoch"
    """Kind of window (epoch, cycle, session, etc.)."""
    
    reference_time: Optional[str] = None
    """Reference time for relative windows."""
    
    @classmethod
    def current_cycle(cls) -> ObservationWindow:
        """Create a window for the current cycle."""
        return cls(start_epoch=1, end_epoch=1, window_kind="cycle")
    
    @classmethod
    def session_window(cls, session_id: str) -> ObservationWindow:
        """Create a window for a specific session."""
        return cls(
            start_epoch=0,
            end_epoch=999999,
            window_kind="session",
            reference_time=session_id,
        )
    
    @classmethod
    def lifetime_window(cls) -> ObservationWindow:
        """Create a lifetime window spanning all epochs."""
        return cls(start_epoch=0, end_epoch=999999, window_kind="lifetime")
    
    def __str__(self) -> str:
        return f"window:{self.window_kind}:[{self.start_epoch},{self.end_epoch}]"


# =============================================================================
# OBSERVATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class Observation:
    """
    Immutable observation of architectural state.
    
    Every observation has a stable identity and preserves provenance.
    
    OBSERVATION-LAW-001: Every Observation possesses one stable semantic identity.
    OBSERVATION-LAW-002: Observations remain immutable.
    OBSERVATION-LAW-006: Observations preserve provenance.
    """
    
    observation_identity: str
    """Stable semantic identity for this observation."""
    
    observation_kind: str
    """Kind of observation (from ObservationKind)."""
    
    scope: str
    """Scope being observed (network, cycle, goal, etc.)."""
    
    window: ObservationWindow = field(default_factory=ObservationWindow)
    """Temporal window for the observation."""
    
    observed_artifacts: tuple[str, ...] = ()
    """References to artifacts that were observed."""
    
    metrics: tuple[dict[str, Any], ...] = ()
    """Metrics collected during this observation."""
    
    findings: tuple[str, ...] = ()
    """Findings from the observation."""
    
    confidence: float = 0.5
    """Confidence in the observation (0.0 to 1.0)."""
    
    uncertainty: float = 0.5
    """Uncertainty about the observation (0.0 to 1.0)."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for this observation."""
    
    timestamp: Optional[str] = None
    """Timestamp of observation in ISO format."""
    
    def __post_init__(self):
        """Validate observation components."""
        if not self.observation_identity:
            raise ValueError("Observation identity cannot be empty")
        
        if not self.scope:
            raise ValueError("Scope cannot be empty")
        
        # Validate confidence bounds
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("Uncertainty must be between 0.0 and 1.0")
        
        # Ensure timestamp is set if not provided
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow().isoformat())
    
    @classmethod
    def create(
        cls,
        observation_kind: str,
        scope: str,
        metrics: tuple[dict[str, Any], ...] = (),
        findings: tuple[str, ...] = (),
        confidence: float = 0.5,
        provenance: Optional[dict[str, str]] = None,
    ) -> Observation:
        """
        Create a new observation.
        
        Args:
            observation_kind: Kind of observation (from ObservationKind)
            scope: Scope being observed
            metrics: Tuple of metric dictionaries collected
            findings: Tuple of finding descriptions
            confidence: Confidence level (0.0 to 1.0)
            provenance: Optional provenance dictionary
            
        Returns:
            New Observation instance with deterministic identity
        """
        import hashlib
        from datetime import datetime
        
        # Create deterministic identity based on content
        identity_content = f"{observation_kind}:{scope}:{confidence}"
        identity_hash = hashlib.sha256(identity_content.encode()).hexdigest()[:16]
        
        return cls(
            observation_identity=f"obs:{identity_kind(observation_kind)}:{identity_hash}",
            observation_kind=observation_kind,
            scope=scope,
            metrics=metrics,
            findings=findings,
            confidence=confidence,
            uncertainty=1.0 - confidence if confidence < 1.0 else 0.5,
            provenance=provenance or {},
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert observation to dictionary."""
        return {
            "observation_identity": self.observation_identity,
            "observation_kind": self.observation_kind,
            "scope": self.scope,
            "window": {"start_epoch": self.window.start_epoch, "end_epoch": self.window.end_epoch},
            "observed_artifacts": list(self.observed_artifacts),
            "metrics": [dict(m) for m in self.metrics],
            "findings": list(self.findings),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "provenance": dict(self.provenance),
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observation:
        """Create observation from dictionary."""
        window_data = data.get("window", {})
        return cls(
            observation_identity=data["observation_identity"],
            observation_kind=data["observation_kind"],
            scope=data["scope"],
            window=ObservationWindow(
                start_epoch=window_data.get("start_epoch", 0),
                end_epoch=window_data.get("end_epoch", 1),
            ),
            observed_artifacts=tuple(data.get("observed_artifacts", [])),
            metrics=tuple(dict(m) for m in data.get("metrics", [])),
            findings=tuple(data.get("findings", [])),
            confidence=data.get("confidence", 0.5),
            uncertainty=data.get("uncertainty", 0.5),
            provenance=dict(data.get("provenance", {})),
            timestamp=data.get("timestamp"),
        )


def identity_kind(kind: str) -> str:
    """
    Get short identifier for observation kind.
    
    Args:
        kind: Full observation kind string
        
    Returns:
        Short identifier for the kind
    """
    mapping = {
        "health": "h",
        "performance": "p",
        "latency": "l",
        "throughput": "t",
        "coordination": "c",
        "synchronization": "s",
        "resource": "r",
        "dependency": "d",
        "failure": "f",
        "recovery": "rcvry",
        "trend": "tr",
        "anomaly": "a",
        "bottleneck": "bn",
        "optimization": "opt",
    }
    return mapping.get(kind, "x")


# =============================================================================
# OBSERVATION REQUEST
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservationRequest:
    """
    Request to perform an observation.
    
    Requests remain immutable and deterministic.
    
    OBSERVATION-LAW-003: Equivalent requests produce equivalent observations.
    """
    
    request_identity: str = ""
    """Stable identity for this request."""
    
    observation_scope: str = "system"
    """Scope to observe (network, cycle, goal, etc.)."""
    
    observation_window: ObservationWindow = field(default_factory=ObservationWindow)
    """Temporal window for the observation."""
    
    requested_metrics: tuple[str, ...] = ()
    """Specific metrics to collect."""
    
    filtering_policy: str = "include_all"
    """Policy for filtering observations."""
    
    aggregation_policy: str = "none"
    """Policy for aggregating observations."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for the request."""
    
    def __post_init__(self):
        """Validate request components."""
        if not self.observation_scope:
            raise ValueError("Observation scope cannot be empty")
        
        valid_filter_policies = {"include_all", "exclude_unchanged", "only_changes"}
        if self.filtering_policy not in valid_filter_policies:
            raise ValueError(f"Invalid filtering policy: {self.filtering_policy}")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_identity": self.request_identity,
            "observation_scope": self.observation_scope,
            "observation_window": {"start_epoch": self.observation_window.start_epoch, "end_epoch": self.observation_window.end_epoch},
            "requested_metrics": list(self.requested_metrics),
            "filtering_policy": self.filtering_policy,
            "aggregation_policy": self.aggregation_policy,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservationRequest:
        """Create request from dictionary."""
        window_data = data.get("observation_window", {})
        return cls(
            request_identity=data.get("request_identity", ""),
            observation_scope=data.get("observation_scope", "system"),
            observation_window=ObservationWindow(
                start_epoch=window_data.get("start_epoch", 0),
                end_epoch=window_data.get("end_epoch", 1),
            ),
            requested_metrics=tuple(data.get("requested_metrics", [])),
            filtering_policy=data.get("filtering_policy", "include_all"),
            aggregation_policy=data.get("aggregation_policy", "none"),
            provenance=dict(data.get("provenance", {})),
        )


# =============================================================================
# OBSERVATION RESULT
# =============================================================================

@dataclass(frozen=True, slots=True)
class ObservationResult:
    """
    Result of an observation request.
    
    Contains observations along with metadata about the process.
    
    RESULT-LAW-001: Results include complete trace.
    RESULT-LAW-002: Results preserve all validation information.
    """
    
    request_reference: str
    """Reference to the original request."""
    
    observations: tuple[Observation, ...] = ()
    """List of observations produced."""
    
    reports: tuple[str, ...] = ()
    """Generated reports."""
    
    findings: tuple[str, ...] = ()
    """Findings from processing."""
    
    limitations: tuple[str, ...] = ()
    """Limitations of the observation process."""
    
    trace: tuple[str, ...] = ()
    """Processing trace for debugging."""
    
    status: str = "completed"
    """Status of the observation (completed, partial, failed)."""
    
    provenance: dict[str, str] = field(default_factory=dict)
    """Provenance information for the result."""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "request_reference": self.request_reference,
            "observations": [o.to_dict() for o in self.observations],
            "reports": list(self.reports),
            "findings": list(self.findings),
            "limitations": list(self.limitations),
            "trace": list(self.trace),
            "status": self.status,
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObservationResult:
        """Create result from dictionary."""
        return cls(
            request_reference=data.get("request_reference", ""),
            observations=tuple(Observation.from_dict(o) for o in data.get("observations", [])),
            reports=tuple(data.get("reports", [])),
            findings=tuple(data.get("findings", [])),
            limitations=tuple(data.get("limitations", [])),
            trace=tuple(data.get("trace", [])),
            status=data.get("status", "completed"),
            provenance=dict(data.get("provenance", {})),
        )