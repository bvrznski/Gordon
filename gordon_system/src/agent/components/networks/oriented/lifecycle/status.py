# Oriented Network Lifecycle Status Models - Phase 4.7.9
# =========================================================

"""
Lifecycle status models for semantic orientation evolution.

SEMANTIC ROLE:
    - Represents semantic condition of Orientation at each lifecycle stage
    - Never represents runtime execution or state transitions
    
LIFECYCLE STATES:
    Created       - Orientation is identified but not yet active
    Candidate     - Orientation is being considered for activation
    Referenced    - Orientation has been referenced by other components
    Active        - Orientation is available for engagement
    Engaged       - Orientation is actively being used
    Maintained    - Orientation is sustainably engaged
    Suspended     - Orientation is temporarily paused
    Resumed       - Orientation is restored from suspension
    Recovered     - Orientation is restored after interruption
    Completed     - Orientation has achieved its purpose
    Archived      - Orientation is preserved for historical reference
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


# =============================================================================
# ORIENTATION STATUS ENUMERATION
# =============================================================================

class OrientationStatus(Enum):
    """
    Canonical orientation status values.
    
    SEMANTIC ROLE:
        - Defines all valid lifecycle states for Orientation
        - Never represents runtime execution
        
    TRANSITION GRAPH:
        Created → Candidate → Referenced → Active → Engaged → Maintained 
            ↓                                         ↘
          Suspended ← Resumed ← Recovered             Completed → Archived
    """
    
    CREATED = "created"
    CANDIDATE = "candidate"
    REFERENCED = "referenced"
    ACTIVE = "active"
    ENGAGED = "engaged"
    MAINTAINED = "maintained"
    INTERRUPTED = "interrupted"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    RECOVERED = "recovered"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# =============================================================================
# LIFECYCLE STATUS MODELS
# =============================================================================

@dataclass(frozen=True)
class CreatedOrientation:
    """
    The orientation has been identified but is not yet active.
    
    SEMANTIC ROLE:
        - Represents initial state where orientation exists as a concept
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Identity established
        - No activation context present
        - Ready for candidate evaluation
        
    OWNERSHIP:
        - Owns: Identity and basic metadata only
    """
    
    identity: str
    created_at: str = field(default="")
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.CREATED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.CREATED)
        
    @classmethod
    def create(cls, identity: str, created_at: str = "") -> CreatedOrientation:
        return cls(identity=identity, created_at=created_at or "")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "CreatedOrientation",
            "identity": self.identity,
            "created_at": self.created_at,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class CandidateOrientation:
    """
    The orientation is being considered for activation.
    
    SEMANTIC ROLE:
        - Represents potential orientation under evaluation
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Identity and basic metadata present
        - Being evaluated for suitability
        - Not yet referenced
        
    OWNERSHIP:
        - Owns: Evaluation context and candidate criteria
    """
    
    identity: str
    candidate_at: str = field(default="")
    evaluation_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.CANDIDATE)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.CANDIDATE)
        
    @classmethod
    def create(cls, identity: str, candidate_at: str = "") -> CandidateOrientation:
        return cls(identity=identity, candidate_at=candidate_at or "")
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "CandidateOrientation",
            "identity": self.identity,
            "candidate_at": self.candidate_at,
            "evaluation_context": self.evaluation_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ReferencedOrientation:
    """
    The orientation has been referenced by other components.
    
    SEMANTIC ROLE:
        - Represents orientation that is part of a reference context
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Identity established and referenced
        - May have multiple references from different sources
        - Ready for activation consideration
        
    OWNERSHIP:
        - Owns: Reference relationships and context
    """
    
    identity: str
    referenced_at: str = field(default="")
    reference_sources: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.REFERENCED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.REFERENCED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        referenced_at: str = "",
        reference_sources: tuple[str, ...] = (),
    ) -> ReferencedOrientation:
        return cls(identity=identity, referenced_at=referenced_at or "", reference_sources=reference_sources)
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ReferencedOrientation",
            "identity": self.identity,
            "referenced_at": self.referenced_at,
            "reference_sources": list(self.reference_sources),
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ActiveOrientation:
    """
    The orientation is available for engagement.
    
    SEMANTIC ROLE:
        - Represents orientation that is ready to engage
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Fully identified and referenced
        - Available for activation
        - May have activation requirements
        
    OWNERSHIP:
        - Owns: Activation context and requirements
    """
    
    identity: str
    activated_at: str = field(default="")
    activation_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.ACTIVE)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.ACTIVE)
        
    @classmethod
    def create(
        cls,
        identity: str,
        activated_at: str = "",
        activation_context: dict[str, Any] | None = None,
    ) -> ActiveOrientation:
        return cls(identity=identity, activated_at=activated_at or "", activation_context=activation_context or {})
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ActiveOrientation",
            "identity": self.identity,
            "activated_at": self.activated_at,
            "activation_context": self.activation_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class EngagedOrientation:
    """
    The orientation is actively being used.
    
    SEMANTIC ROLE:
        - Represents orientation in active engagement state
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Fully engaged with context
        - May be maintained or suspended
        - Active semantic commitment
        
    OWNERSHIP:
        - Owns: Engagement context and commitment level
    """
    
    identity: str
    engaged_at: str = field(default="")
    engagement_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.ENGAGED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.ENGAGED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        engaged_at: str = "",
        engagement_context: dict[str, Any] | None = None,
    ) -> EngagedOrientation:
        return cls(identity=identity, engaged_at=engaged_at or "", engagement_context=engagement_context or {})
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "EngagedOrientation",
            "identity": self.identity,
            "engaged_at": self.engaged_at,
            "engagement_context": self.engagement_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class MaintainedOrientation:
    """
    The orientation is sustainably engaged.
    
    SEMANTIC ROLE:
        - Represents ongoing engagement with sustained commitment
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Actively maintained over time
        - Has maintenance context and history
        - May evolve or be suspended
        
    OWNERSHIP:
        - Owns: Maintenance context and duration tracking
    """
    
    identity: str
    maintained_at: str = field(default="")
    maintenance_context: dict[str, Any] = field(default_factory=dict)
    maintenance_duration: int = field(default=0)  # In semantic units
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.MAINTAINED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.MAINTAINED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        maintained_at: str = "",
        maintenance_context: dict[str, Any] | None = None,
        maintenance_duration: int = 0,
    ) -> MaintainedOrientation:
        return cls(
            identity=identity,
            maintained_at=maintained_at or "",
            maintenance_context=maintenance_context or {},
            maintenance_duration=maintenance_duration,
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "MaintainedOrientation",
            "identity": self.identity,
            "maintained_at": self.maintained_at,
            "maintenance_context": self.maintenance_context,
            "maintenance_duration": self.maintenance_duration,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class InterruptedOrientation:
    """
    The orientation was interrupted during engagement.
    
    SEMANTIC ROLE:
        - Represents interrupted engagement state
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Engagement was interrupted
        - May require resumption or recovery
        - Preservation of context at interruption point
        
    OWNERSHIP:
        - Owns: Interruption context and reason
    """
    
    identity: str
    interrupted_at: str = field(default="")
    interruption_reason: str = field(default="")
    interruption_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.INTERRUPTED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.INTERRUPTED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        interrupted_at: str = "",
        interruption_reason: str = "",
        interruption_context: dict[str, Any] | None = None,
    ) -> InterruptedOrientation:
        return cls(
            identity=identity,
            interrupted_at=interrupted_at or "",
            interruption_reason=interruption_reason,
            interruption_context=interruption_context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "InterruptedOrientation",
            "identity": self.identity,
            "interrupted_at": self.interrupted_at,
            "interruption_reason": self.interruption_reason,
            "interruption_context": self.interruption_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class SuspendedOrientation:
    """
    The orientation is temporarily paused.
    
    SEMANTIC ROLE:
        - Represents temporary suspension state
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Temporarily paused but not terminated
        - Context preserved for resumption
        - May be resumed or recovered
        
    OWNERSHIP:
        - Owns: Suspension context and duration
    """
    
    identity: str
    suspended_at: str = field(default="")
    suspension_reason: str = field(default="")
    suspension_duration: int = field(default=0)  # In semantic units
    suspension_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.SUSPENDED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.SUSPENDED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        suspended_at: str = "",
        suspension_reason: str = "",
        suspension_duration: int = 0,
        suspension_context: dict[str, Any] | None = None,
    ) -> SuspendedOrientation:
        return cls(
            identity=identity,
            suspended_at=suspended_at or "",
            suspension_reason=suspension_reason,
            suspension_duration=suspension_duration,
            suspension_context=suspension_context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "SuspendedOrientation",
            "identity": self.identity,
            "suspended_at": self.suspended_at,
            "suspension_reason": self.suspension_reason,
            "suspension_duration": self.suspension_duration,
            "suspension_context": self.suspension_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ResumedOrientation:
    """
    The orientation is restored from suspension.
    
    SEMANTIC ROLE:
        - Represents resumption after temporary suspension
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Restored from suspended state
        - Continuity preserved
        - May return to active or maintained engagement
        
    OWNERSHIP:
        - Owns: Resumption context and continuity tracking
    """
    
    identity: str
    resumed_at: str = field(default="")
    resume_source: str = field(default="")  # "Suspended" | "Interrupted"
    resumption_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.RESUMED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.RESUMED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        resumed_at: str = "",
        resume_source: str = "",
        resumption_context: dict[str, Any] | None = None,
    ) -> ResumedOrientation:
        return cls(
            identity=identity,
            resumed_at=resumed_at or "",
            resume_source=resume_source,
            resumption_context=resumption_context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ResumedOrientation",
            "identity": self.identity,
            "resumed_at": self.resumed_at,
            "resume_source": self.resume_source,
            "resumption_context": self.resumption_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class RecoveredOrientation:
    """
    The orientation is restored after interruption.
    
    SEMANTIC ROLE:
        - Represents recovery from interrupted state
        - Never represents runtime execution
        
    CHARACTERISTICS:
        - Restored after unexpected interruption
        - Continuity preserved through archival
        - May return to active or maintained engagement
        
    OWNERSHIP:
        - Owns: Recovery context and historical tracking
    """
    
    identity: str
    recovered_at: str = field(default="")
    recovery_source: str = field(default="")  # "Interrupted" | "Archived"
    recovery_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.RECOVERED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.RECOVERED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        recovered_at: str = "",
        recovery_source: str = "",
        recovery_context: dict[str, Any] | None = None,
    ) -> RecoveredOrientation:
        return cls(
            identity=identity,
            recovered_at=recovered_at or "",
            recovery_source=recovery_source,
            recovery_context=recovery_context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "RecoveredOrientation",
            "identity": self.identity,
            "recovered_at": self.recovered_at,
            "recovery_source": self.recovery_source,
            "recovery_context": self.recovery_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class CompletedOrientation:
    """
    The orientation has achieved its purpose.
    
    SEMANTIC ROLE:
        - Represents semantic fulfillment
        - Never represents runtime termination
        
    CHARACTERISTICS:
        - Purpose achieved or superseded
        - May be archived for historical reference
        - Completion lineage preserved
        
    OWNERSHIP:
        - Owns: Completion context and achievement tracking
    """
    
    identity: str
    completed_at: str = field(default="")
    completion_reason: str = field(default="")
    completion_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.COMPLETED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.COMPLETED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        completed_at: str = "",
        completion_reason: str = "",
        completion_context: dict[str, Any] | None = None,
    ) -> CompletedOrientation:
        return cls(
            identity=identity,
            completed_at=completed_at or "",
            completion_reason=completion_reason,
            completion_context=completion_context or {},
        )
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "CompletedOrientation",
            "identity": self.identity,
            "completed_at": self.completed_at,
            "completion_reason": self.completion_reason,
            "completion_context": self.completion_context,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class ArchivedOrientation:
    """
    The orientation is preserved for historical reference.
    
    SEMANTIC ROLE:
        - Represents semantic closure and preservation
        - Never owns persistence systems
        
    CHARACTERISTICS:
        - Historical record preserved
        - May be referenced but not active
        - Identity and lineage complete
        
    OWNERSHIP:
        - Owns: Archival context and historical tracking
    """
    
    identity: str
    archived_at: str = field(default="")
    archive_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    status: OrientationStatus = field(init=False, default=OrientationStatus.ARCHIVED)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrientationStatus.ARCHIVED)
        
    @classmethod
    def create(
        cls,
        identity: str,
        archived_at: str = "",
        archive_context: dict[str, Any] | None = None,
    ) -> ArchivedOrientation:
        return cls(identity=identity, archived_at=archived_at or "", archive_context=archive_context or {})
        
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "ArchivedOrientation",
            "identity": self.identity,
            "archived_at": self.archived_at,
            "archive_context": self.archive_context,
            "status": self.status.value,
        }


# =============================================================================
# LIFECYCLE TRANSITION GRAPH
# =============================================================================

CANONICAL_TRANSITIONS: tuple[tuple[OrientationStatus, OrientationStatus], ...] = (
    (OrientationStatus.CREATED, OrientationStatus.CANDIDATE),
    (OrientationStatus.CANDIDATE, OrientationStatus.REFERENCED),
    (OrientationStatus.REFERENCED, OrientationStatus.ACTIVE),
    (OrientationStatus.ACTIVE, OrientationStatus.ENGAGED),
    (OrientationStatus.ENGAGED, OrientationStatus.MAINTAINED),
    (OrientationStatus.MAINTAINED, OrientationStatus.SUSPENDED),
    (OrientationStatus.SUSPENDED, OrientationStatus.RESUMED),
    (OrientationStatus.RESUMED, OrientationStatus.ENGAGED),
    (OrientationStatus.ENGAGED, OrientationStatus.COMPLETED),
    (OrientationStatus.COMPLETED, OrientationStatus.ARCHIVED),
)


__all__ = [
    # Status enumeration
    "OrientationStatus",
    # Lifecycle status models
    "CreatedOrientation",
    "CandidateOrientation",
    "ReferencedOrientation",
    "ActiveOrientation",
    "EngagedOrientation",
    "MaintainedOrientation",
    "InterruptedOrientation",
    "SuspendedOrientation",
    "ResumedOrientation",
    "RecoveredOrientation",
    "CompletedOrientation",
    "ArchivedOrientation",
    # Transition graph
    "CANONICAL_TRANSITIONS",
]