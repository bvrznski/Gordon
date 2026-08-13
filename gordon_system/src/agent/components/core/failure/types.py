# Failure Taxonomy Types
# ======================

"""
Immutable failure artifact types and taxonomy definitions for Phase 3.7.10.

This module defines:
- FailureKind: Classification of failure nature (TRANSIENT, RECOVERABLE, etc.)
- FailureSeverity: Impact level (INFO, WARNING, ERROR, CRITICAL, FATAL)
- FailureDomain: System scope where failure occurs
- FailureDisposition: Suggested recovery action
- RollbackMode and RollbackScope: Rollback strategy parameters

All types use stable string values for deterministic serialization.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import time


# =============================================================================
# Failure Kinds (Nature of the failure)
# =============================================================================

class FailureKind(Enum):
    """
    Classification of failure nature - what kind of failure is this?
    
    This determines:
    - Retry eligibility
    - Rollback eligibility  
    - Recovery options
    - Escalation path
    
    Examples:
        - TRANSIENT: Temporary condition, may recover automatically
        - CONFIGURATION: Invalid configuration, needs correction
        - DATA_CORRUPTION: Data integrity violation, requires special handling
        - FATAL: Terminal condition requiring immediate shutdown
    """
    
    # Transient conditions (may recover)
    TRANSIENT = "transient"
    TIMEOUT = "timeout"
    TEMPORARY_UNAVAILABLE = "temporary_unavailable"
    
    # Recoverable failures
    RECOVERABLE = "recoverable"
    RESOURCE = "resource"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY = "dependency"
    MODEL_FAILURE = "model_failure"
    DEVICE_FAILURE = "device_failure"
    
    # Non-recoverable conditions
    NON_RECOVERABLE = "non_recoverable"
    CONFIGURATION = "configuration"  # Needs manual correction
    PROGRAMMING = "programming"      # Code error, needs fix
    
    # Integrity failures (require special handling)
    DATA_CORRUPTION = "data_corruption"
    STATE_CORRUPTION = "state_corruption"
    INTEGRITY = "integrity"
    
    # Security failures
    SECURITY = "security"
    
    # Infrastructure failures
    NETWORK = "network"
    STORAGE = "storage"
    SERVICE_FAILURE = "service_failure"
    PROCESS_EXIT = "process_exit"
    
    # System-level
    FATAL = "fatal"           # Terminal, must not attempt recovery
    PANIC = "panic"           # Critical failure requiring immediate action
    
    # Cancellation
    CANCELLATION = "cancellation"
    
    # Unknown/other
    UNKNOWN = "unknown"


# =============================================================================
# Failure Severities (Impact level)
# =============================================================================

class FailureSeverity(Enum):
    """
    Severity level - how much impact does this failure have?
    
    Severity is independent from kind. A TRANSIENT failure can be CRITICAL
    if it affects safety-critical systems.
    
    Levels:
        INFO: Informational, no action needed
        NOTICE: Notable event, monitor closely  
        WARNING: May need attention
        ERROR: System impact, recovery may be possible
        CRITICAL: Major system impact, immediate escalation
        FATAL: Terminal condition
        PANIC: Critical failure requiring emergency shutdown
    """
    
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"
    PANIC = "panic"


# =============================================================================
# Failure Domains (Scope of impact)
# =============================================================================

class FailureDomain(Enum):
    """
    System domain where failure occurs.
    
    Each domain defines:
    - Canonical owner responsible for containment
    - Propagation path to higher levels
    - Restart/rollback/recovery capability
    - Fatal conditions specific to this domain
    
    Domains form a hierarchy:
        TASK → EXECUTOR → SCHEDULER → RUNTIME
        SERVICE → KERNEL → RUNTIME
    """
    
    # Core infrastructure
    RUNTIME = "runtime"
    KERNEL = "kernel"
    ENGINE = "engine"
    
    # Coordination
    MANAGER = "manager"
    SCHEDULER = "scheduler"
    EXECUTOR = "executor"
    
    # Execution units
    WORKER = "worker"
    SERVICE = "service"
    DAEMON = "daemon"
    
    # External dependencies
    MODEL = "model"
    DEVICE = "device"
    GPU = "gpu"
    
    # Resource management
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    RESOURCE = "resource"
    
    # Configuration and data
    DATABASE = "database"
    CONFIGURATION = "configuration"
    
    # Plugin/system
    PLUGIN = "plugin"
    BACKGROUND_LOOP = "background_loop"
    
    # External providers
    EXTERNAL_PROVIDER = "external_provider"


# =============================================================================
# Failure Dispositions (Recommended action)
# =============================================================================

class FailureDisposition(Enum):
    """
    Recommended recovery/disposition for a failure.
    
    This is determined by the classifier based on:
    - Failure kind and severity
    - Rollback eligibility  
    - Recovery eligibility
    - Budget constraints
    
    Actions:
        IGNORE_WITH_EVIDENCE: Log but don't act (e.g., informational)
        CONTAIN: Isolate without recovery attempt
        RETRY: Attempt operation retry
        ROLLBACK: Execute rollback to prior state
        RESTART: Restart component
        FAILOVER: Switch to backup
        DEGRADE: Accept degraded operation
        REQUIRE_OPERATOR: Escalate for human intervention
        SHUTDOWN: Graceful shutdown
        TERMINATE: Force termination if needed
    """
    
    IGNORE_WITH_EVIDENCE = "ignore_with_evidence"
    CONTAIN = "contain"
    RETRY = "retry"
    ROLLBACK = "rollback"
    RESTART = "restart"
    FAILOVER = "failover"
    DEGRADE = "degrade"
    REQUIRE_OPERATOR = "require_operator"
    SHUTDOWN = "shutdown"
    TERMINATE = "terminate"


# =============================================================================
# Rollback Parameters
# =============================================================================

class RollbackMode(Enum):
    """
    Rollback strategy mode.
    
    Modes:
        FULL: Complete restoration to known state
        PARTIAL: Restore only affected components
        TRANSACTIONAL: Rollback within transaction boundaries
        COMPENSATING: Counteract effects (not exact rollback)
        CHECKPOINT: Restore from checkpoint
        BEST_EFFORT: Try to roll back what's possible
        LOCAL: Only rollback local component state
        CASCADE: Propagate rollback to dependents
        FORCED: Bypass some safety checks if necessary
    """
    
    FULL = "full"
    PARTIAL = "partial"
    TRANSACTIONAL = "transactional"
    COMPENSATING = "compensating"
    CHECKPOINT = "checkpoint"
    BEST_EFFORT = "best_effort"
    LOCAL = "local"
    CASCADE = "cascade"
    FORCED = "forced"


class RollbackScope(Enum):
    """
    Scope of rollback operation.
    
    Scopes:
        TASK: Single task
        TASK_GRAPH: Related tasks
        TRANSACTION: Database transaction boundary
        COMPONENT: Single component
        SERVICE: Entire service
        SUBSYSTEM: Collection of services
        RESOURCE: Specific resource type
        RUNTIME_PHASE: Current runtime phase
        RUNTIME: Entire runtime
        CONFIGURATION: Configuration state
        CHECKPOINT: Named checkpoint
    """
    
    TASK = "task"
    TASK_GRAPH = "task_graph"
    TRANSACTION = "transaction"
    COMPONENT = "component"
    SERVICE = "service"
    SUBSYSTEM = "subsystem"
    RESOURCE = "resource"
    RUNTIME_PHASE = "runtime_phase"
    RUNTIME = "runtime"
    CONFIGURATION = "configuration"
    CHECKPOINT = "checkpoint"


# =============================================================================
# Recovery Parameters
# =============================================================================

class RecoveryPolicy(Enum):
    """
    Policy for recovery actions.
    
    Policies determine:
        - Retry behavior (immediate, backoff-based)
        - Whether to attempt rollback
        - Restart strategy
        - Degradation acceptance
    
    Policies:
        RETRY_OPERATION: Retry the failed operation
        RETRY_TASK: Retry entire task
        RESTART_WORKER: Restart worker process/thread
        RESTART_SERVICE: Restart service
        RELOAD_SERVICE: Reload service configuration/state
        REINITIALIZE_COMPONENT: Reinitialize without full restart
        RECONSTRUCT_COMPONENT: Build fresh component instance
        ROLLBACK_AND_RETRY: Rollback then retry operation
        ROLLBACK_AND_DEGRADE: Rollback, accept degraded state
        FAILOVER: Switch to alternate provider
        DISABLE_COMPONENT: Temporarily disable affected component
        ENTER_DEGRADED: Accept degraded operational mode
        REQUIRE_OPERATOR: Escalate for manual intervention
        SHUTDOWN: Graceful shutdown attempt
        TERMINATE: Force termination
    """
    
    RETRY_OPERATION = "retry_operation"
    RETRY_TASK = "retry_task"
    RESTART_WORKER = "restart_worker"
    RESTART_SERVICE = "restart_service"
    RELOAD_SERVICE = "reload_service"
    REINITIALIZE_COMPONENT = "reinitialize_component"
    RECONSTRUCT_COMPONENT = "reconstruct_component"
    ROLLBACK_AND_RETRY = "rollback_and_retry"
    ROLLBACK_AND_DEGRADE = "rollback_and_degrade"
    FAILOVER = "failover"
    DISABLE_COMPONENT = "disable_component"
    ENTER_DEGRADED = "enter_degraded"
    REQUIRE_OPERATOR = "require_operator"
    SHUTDOWN = "shutdown"
    TERMINATE = "terminate"


# =============================================================================
# Runtime Failure Artifact (Core)
# =============================================================================

@dataclass(frozen=True)
class RuntimeFailure:
    """
    Immutable runtime failure artifact.
    
    A failure is not merely an exception string. This artifact preserves:
        - Causal chain for root cause analysis
        - Classification results (kind, severity, scope)
        - Recovery eligibility and retryability
        - Affected entities and resources
        - Runtime identity for multi-runtime isolation
    
    Design principles:
        - Immutable (frozen dataclass) for thread safety
        - Deterministic serialization for logging/diagnostics
        - Explicit unknown-outcome state (no guessing from insufficient evidence)
        - Stable failure identity via generated failure_id
        - Source and domain attribution
    """
    
    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------
    
    failure_id: str  # Unique identifier (UUID format recommended)
    
    runtime_id: Optional[str] = None  # Runtime instance identifier (for multi-runtime isolation)
    
    # Causation chain
    operation_id: Optional[str] = None      # What operation was being performed?
    correlation_id: Optional[str] = None    # User/request correlation
    causation_id: Optional[str] = None      # Root cause failure ID
    
    # ------------------------------------------------------------------
    # Classification (from classifier)
    # ------------------------------------------------------------------
    
    source: str = ""  # Component where failure originated
    domain: FailureDomain = FailureDomain.RUNTIME
    kind: FailureKind = FailureKind.UNKNOWN
    severity: FailureSeverity = FailureSeverity.WARNING
    
    scope: List[str] = field(default_factory=list)  # Affected entity IDs
    
    message: str = ""  # Human-readable summary
    
    exception_type: Optional[str] = None      # Exception class name
    exception_summary: Optional[str] = None   # Brief exception description
    stack_reference: Optional[str] = None     # Stack trace reference (not full traceback)
    
    # ------------------------------------------------------------------
    # State at time of failure
    # ------------------------------------------------------------------
    
    affected_entity_ids: List[str] = field(default_factory=list)
    affected_capability_ids: List[str] = field(default_factory=list)
    resource_ids: List[str] = field(default_factory=list)
    
    detected_at: float = field(default_factory=time.time)
    
    logical_sequence: int = 0  # For ordering failures
    
    # ------------------------------------------------------------------
    # Recovery classification
    # ------------------------------------------------------------------
    
    retryability: Optional[bool] = None      # True = safe to retry, False = unsafe, None = unknown
    rollback_eligibility: Optional[bool] = None  # Can rollback to known prior state?
    recovery_eligibility: Optional[bool] = None  # Can recover from this failure?
    
    containment_requirement: bool = False    # Must contain before recovery?
    
    integrity_impact: str = "unknown"        # none, degraded, corrupted, unknown
    security_impact: str = "none"            # none, suspected, confirmed
    
    unknown_outcome: bool = False  # True if we cannot determine state after failure
    
    # ------------------------------------------------------------------
    # Provenance and metadata
    # ------------------------------------------------------------------
    
    provenance: Dict[str, str] = field(default_factory=dict)  # Source tracking
    
    metadata: Dict[str, Any] = field(default_factory=dict)    # Additional context
    
    # ------------------------------------------------------------------
    # Properties for quick inspection
    # ------------------------------------------------------------------
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this failure can potentially be recovered."""
        return self.recovery_eligibility is True and not (self.kind in (
            FailureKind.FATAL, 
            FailureKind.PANIC,
            FailureKind.PROGRAMMING
        ))
    
    @property
    def is_retryable(self) -> bool:
        """Check if this failure can be retried."""
        return self.retryability is True
    
    @property
    def needs_escalation(self) -> bool:
        """Check if failure should be escalated to higher authority."""
        return (
            self.severity in (FailureSeverity.CRITICAL, FailureSeverity.FATAL, FailureSeverity.PANIC)
            or not self.recovery_eligibility
        )
    
    @property
    def has_integrity_impact(self) -> bool:
        """Check if integrity may be affected."""
        return self.integrity_impact != "none"
    
    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert to JSON-serializable dictionary.
        
        This is deterministic - same inputs always produce same output.
        """
        return {
            "failure_id": self.failure_id,
            "runtime_id": self.runtime_id,
            "operation_id": self.operation_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "source": self.source,
            "domain": self.domain.value if hasattr(self.domain, 'value') else str(self.domain),
            "kind": self.kind.value if hasattr(self.kind, 'value') else str(self.kind),
            "severity": self.severity.value if hasattr(self.severity, 'value') else str(self.severity),
            "scope": list(self.scope),
            "message": self.message,
            "exception_type": self.exception_type,
            "exception_summary": self.exception_summary,
            "stack_reference": self.stack_reference,
            "affected_entity_ids": list(self.affected_entity_ids),
            "affected_capability_ids": list(self.affected_capability_ids),
            "resource_ids": list(self.resource_ids),
            "detected_at": self.detected_at,
            "logical_sequence": self.logical_sequence,
            "retryability": self.retryability,
            "rollback_eligibility": self.rollback_eligibility,
            "recovery_eligibility": self.recovery_eligibility,
            "containment_requirement": self.containment_requirement,
            "integrity_impact": self.integrity_impact,
            "security_impact": self.security_impact,
            "unknown_outcome": self.unknown_outcome,
            "provenance": dict(self.provenance),
            "metadata": self._serialize_metadata(self.metadata)
        }
    
    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> "RuntimeFailure":
        """Create RuntimeFailure from serialized dictionary."""
        # Parse enums with defaults for unknown values
        domain = cls._parse_enum(data.get("domain"), FailureDomain, FailureDomain.RUNTIME)
        kind = cls._parse_enum(data.get("kind"), FailureKind, FailureKind.UNKNOWN)
        severity = cls._parse_enum(data.get("severity"), FailureSeverity, FailureSeverity.WARNING)
        
        return cls(
            failure_id=data["failure_id"],
            runtime_id=data.get("runtime_id"),
            operation_id=data.get("operation_id"),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            source=data.get("source", ""),
            domain=domain,
            kind=kind,
            severity=severity,
            scope=data.get("scope", []),
            message=data.get("message", ""),
            exception_type=data.get("exception_type"),
            exception_summary=data.get("exception_summary"),
            stack_reference=data.get("stack_reference"),
            affected_entity_ids=data.get("affected_entity_ids", []),
            affected_capability_ids=data.get("affected_capability_ids", []),
            resource_ids=data.get("resource_ids", []),
            detected_at=data.get("detected_at", time.time()),
            logical_sequence=data.get("logical_sequence", 0),
            retryability=data.get("retryability"),
            rollback_eligibility=data.get("rollback_eligibility"),
            recovery_eligibility=data.get("recovery_eligibility"),
            containment_requirement=data.get("containment_requirement", False),
            integrity_impact=data.get("integrity_impact", "unknown"),
            security_impact=data.get("security_impact", "none"),
            unknown_outcome=data.get("unknown_outcome", False),
            provenance=data.get("provenance", {}),
            metadata=cls._deserialize_metadata(data.get("metadata", {}))
        )
    
    @staticmethod
    def _parse_enum(value: Any, enum_type: type, default: Any) -> Any:
        """Parse an enum value with a safe default."""
        if isinstance(value, enum_type):
            return value
        if isinstance(value, str):
            try:
                return enum_type(value)
            except ValueError:
                pass
        return default
    
    @staticmethod
    def _serialize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize metadata for storage/transmission."""
        result = {}
        for k, v in metadata.items():
            # Convert any non-serializable types to strings
            if isinstance(v, (Enum,)):
                result[k] = v.value if hasattr(v, 'value') else str(v)
            elif isinstance(v, (list, dict)):
                result[k] = v  # Let JSON handle these
            else:
                result[k] = v
        return result
    
    @staticmethod
    def _deserialize_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize metadata from storage/transmission."""
        return dict(data)


# =============================================================================
# Export all failure types
# =============================================================================

__all__ = [
    # Enums (Classification)
    "FailureKind",
    "FailureSeverity",
    "FailureDomain",
    "FailureDisposition",
    "RollbackMode",
    "RollbackScope",
    "RecoveryPolicy",
    
    # Runtime failure artifact
    "RuntimeFailure",
]
