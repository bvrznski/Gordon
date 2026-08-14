# Canonical Failure Architecture - Phase 3.14.14
# ================================================
#
# FAILURE PROPAGATION & RECOVERY ARCHITECTURE
#
# This module establishes the canonical architectural model governing Failure
# Propagation and Recovery throughout Gordon.
#
# Failures are first-class architectural events.
# Failures shall never be hidden.
# Failures shall never silently propagate.
# Recovery shall be deterministic.
# Recovery shall preserve architectural integrity.

"""
Canonical Failure Architecture for Gordon Phase 3.14.14.

This module implements the complete failure lifecycle and recovery architecture:

ARCHITECTURAL MODEL
-------------------
    
    Execution
            │
            ▼
    Failure Detection
            │
            ▼
    Classification
            │
            ▼
    Containment
            │
            ▼
    Propagation
            │
            ▼
    Recovery
            │
            ▼
    Certification

Detection discovers.
Containment limits.
Propagation informs.
Recovery restores.
Certification verifies.

ARCHITECTURAL PRINCIPLES
------------------------
    
- Execution progresses work.
- Interactions communicate.
- Failures communicate inability to satisfy architectural expectations.
- Recovery restores architectural consistency.
- Failures shall remain explicit.
- Recovery shall remain observable.
- Neither failures nor recovery shall violate ownership or authority.

FAILURE LIFECYCLE
-----------------

Detected → Classified → Contained → Propagated → Recovered → Verified → Closed

Alternative terminal states:
    - Escalated
    - Aborted  
    - Unrecoverable

SEVERITY LEVELS
---------------
    
- Informational: No action needed
- Warning: Monitor closely
- Recoverable: Recovery possible
- Serious: Significant impact
- Critical: Immediate escalation required
- Fatal: Terminal condition
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import uuid
import time


# =============================================================================
# SECURITY ERROR DEFINITIONS (for classification)
# =============================================================================

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Authentication failure."""
    pass


class AuthorizationError(SecurityError):
    """Authorization failure."""
    pass


# =============================================================================
# FAILURE CATEGORY TAXONOMY (Canonical)
# =============================================================================

class FailureCategory(Enum):
    """
    Canonical failure categories for Gordon.
    
    Every failure shall belong to exactly one primary category.
    
    Categories:
        VALIDATION: Input or constraint validation failed
        ADMISSION: Request not admitted by authority boundary
        SCHEDULING: Scheduling decision could not be made
        EXECUTION: Execution operation encountered error
        STREAM: Stream transport encountered error
        INTERACTION: Interaction contract violated
        NETWORK: Network connectivity or protocol failure
        CAPABILITY: Capability invocation failed
        SYSTEM: System state management failure
        RESOURCE: Resource allocation or access failure
        DEPENDENCY: External dependency unavailable or failed
        SECURITY: Security policy violation detected
        PRIVACY: Privacy constraint violation detected
        INTEGRITY: Data or state integrity violation detected
        TIMEOUT: Operation exceeded time budget
        CANCELLATION: Operation was cancelled (graceful)
        RECOVERY: Recovery operation itself failed
    """
    
    # Validation failures
    VALIDATION = "validation"
    """Input validation or constraint satisfaction failure."""
    
    ADMISSION = "admission"
    """Request not admitted by authority boundary."""
    
    SCHEDULING = "scheduling"
    """Scheduling decision could not be made."""
    
    EXECUTION = "execution"
    """Execution operation encountered error."""
    
    # Stream failures
    STREAM = "stream"
    """Stream transport encountered error."""
    
    INTERACTION = "interaction"
    """Interaction contract or protocol violation."""
    
    NETWORK = "network"
    """Network connectivity, routing, or protocol failure."""
    
    # Component failures
    CAPABILITY = "capability"
    """Capability invocation or execution failed."""
    
    SYSTEM = "system"
    """System state management or persistence failure."""
    
    RESOURCE = "resource"
    """Resource allocation, acquisition, or access failure."""
    
    DEPENDENCY = "dependency"
    """External dependency unavailable or failed."""
    
    # Integrity failures
    SECURITY = "security"
    """Security policy violation detected."""
    
    PRIVACY = "privacy"
    """Privacy constraint violation detected."""
    
    INTEGRITY = "integrity"
    """Data or state integrity violation detected."""
    
    # Terminal conditions
    TIMEOUT = "timeout"
    """Operation exceeded time budget."""
    
    CANCELLATION = "cancellation"
    """Operation was cancelled (graceful exit)."""
    
    RECOVERY = "recovery"
    """Recovery operation encountered error."""


# =============================================================================
# FAILURE SEVERITY LEVELS
# =============================================================================

class FailureSeverity(Enum):
    """
    Severity level for failures.
    
    Severity influences recovery policy but shall never redefine ownership.
    
    Levels:
        INFO: Informational event, no action needed
        NOTICE: Notable event, may need attention
        WARNING: Potential problem, monitor closely
        RECOVERABLE: Can be recovered with effort
        SERIOUS: Significant impact requiring escalation
        CRITICAL: Major system impact, immediate action required
        FATAL: Terminal condition, no recovery possible
    """
    
    INFO = "info"
    """Informational event, no action needed."""
    
    NOTICE = "notice"
    """Notable event that may need attention."""
    
    WARNING = "warning"
    """Potential problem, monitor closely."""
    
    RECOVERABLE = "recoverable"
    """Failure can be recovered with appropriate effort."""
    
    SERIOUS = "serious"
    """Significant impact requiring escalation."""
    
    CRITICAL = "critical"
    """Major system impact requiring immediate escalation."""
    
    FATAL = "fatal"
    """Terminal condition, no recovery possible."""


# =============================================================================
# FAILURE LIFECYCLE STATES
# =============================================================================

class FailureLifecycleState(Enum):
    """
    States in the failure lifecycle.
    
    Lifecycle progression shall remain deterministic.
    
    States:
        DETECTED: Failure discovered but not yet classified
        CLASSIFIED: Category and severity determined
        CONTAINED: Scope limited to prevent propagation
        PROPAGATED: Information shared with stakeholders
        RECOVERED: Recovery action completed
        VERIFIED: Recovery validated successfully
        CLOSED: Lifecycle complete (successful recovery)
        
    Alternative terminal states:
        ESCALATED: Escalated for higher authority intervention
        ABORTED: Lifecycle terminated prematurely
        UNRECOVERABLE: No viable recovery path exists
    """
    
    # Primary lifecycle path
    DETECTED = "detected"
    """Failure discovered but not yet classified."""
    
    CLASSIFIED = "classified"
    """Category and severity determined."""
    
    CONTAINED = "contained"
    """Scope limited to prevent propagation."""
    
    PROPAGATED = "propagated"
    """Information shared with stakeholders."""
    
    RECOVERED = "recovered"
    """Recovery action completed."""
    
    VERIFIED = "verified"
    """Recovery validated successfully."""
    
    CLOSED = "closed"
    """Lifecycle complete (successful recovery)."""
    
    # Alternative terminal states
    ESCALATED = "escalated"
    """Escalated for higher authority intervention."""
    
    ABORTED = "aborted"
    """Lifecycle terminated prematurely."""
    
    UNRECOVERABLE = "unrecoverable"
    """No viable recovery path exists."""


# =============================================================================
# FAILURE PROPAGATION PATH
# =============================================================================

class FailurePropagationPath(Enum):
    """
    Canonical propagation paths for failures.
    
    Each component owns failure handling within its responsibility but
    shall propagate to higher authority when local recovery fails.
    """
    
    # Direct propagation (same level)
    DIRECT = "direct"
    """Direct propagation between peers."""
    
    # Upward escalation
    UPWARD = "upward"
    """Escalation to higher authority."""
    
    # Broadcast
    BROADCAST = "broadcast"
    """Broadcast to all interested parties."""
    
    # Response/return path
    RESPONSE = "response"
    """Response along interaction chain."""
    
    # Error return
    ERROR_RETURN = "error_return"
    """Error propagation along return path."""


# =============================================================================
# RECOVERY STRATEGY TYPES
# =============================================================================

class RecoveryStrategy(Enum):
    """
    Canonical recovery strategies.
    
    No failure shall remain unclassified in terms of recovery approach.
    """
    
    RETRY = "retry"
    """Attempt operation again."""
    
    ROLLBACK = "rollback"
    """Restore to previous verified state."""
    
    RESTART = "restart"
    """Restart component or service."""
    
    REINITIALIZE = "reinitialize"
    """Reinitialize component without full restart."""
    
    DEGRADE = "degrade"
    """Accept degraded operational mode."""
    
    FAILOVER = "failover"
    """Switch to backup system or provider."""
    
    RESTORE_CHECKPOINT = "restore_checkpoint"
    """Restore from verified checkpoint."""
    
    COMPENSATING = "compensating"
    """Execute compensating transaction."""
    
    GRACEFUL_SHUTDOWN = "graceful_shutdown"
    """Perform graceful shutdown sequence."""
    
    TERMINATE = "terminate"
    """Force termination of failing component."""


# =============================================================================
# FAILURE ORIGIN OWNERSHIP
# =============================================================================

class FailureOrigin(Enum):
    """
    Canonical origin points for failures.
    
    Each architectural component owns recovery within its responsibility:
        - Execution owns execution recovery
        - Streams own transport recovery  
        - Networks own network recovery
        - Capabilities own computation recovery
        - Systems own state recovery
        
    Ownership shall never migrate during failure handling.
    """
    
    EXECUTION = "execution"
    """Failure originated in Execution domain."""
    
    STREAM = "stream"
    """Failure originated in Streams domain."""
    
    NETWORK = "network"
    """Failure originated in Networks domain."""
    
    CAPABILITY = "capability"
    """Failure originated in Capabilities domain."""
    
    SYSTEM = "system"
    """Failure originated in Systems domain."""
    
    INTERACTION = "interaction"
    """Failure originated in Interaction contracts."""
    
    CORE = "core"
    """Failure originated in core infrastructure."""


# =============================================================================
# FAILURE ARTIFACT (Canonical Record)
# =============================================================================

@dataclass(frozen=True)
class FailureArtifact:
    """
    Immutable failure artifact with full provenance tracking.
    
    A failure is not merely an exception string. This artifact preserves:
        - Causal chain for root cause analysis
        - Classification results (category, severity)
        - Recovery eligibility and retryability
        - Affected entities and resources
        - Lifecycle state transitions
        - Provenance for audit and replay
        
    Design principles:
        - Immutable (frozen dataclass) for thread safety
        - Deterministic serialization for logging/diagnostics
        - Explicit unknown-outcome state
        - Stable failure identity via generated failure_id
        - Source and domain attribution
    """
    
    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------
    
    failure_id: str  # Unique identifier (UUID)
    
    runtime_id: Optional[str] = None  # Runtime instance identifier
    
    # Causation chain
    operation_id: Optional[str] = None       # What operation was being performed?
    correlation_id: Optional[str] = None     # User/request correlation
    causation_id: Optional[str] = None       # Root cause failure ID
    
    # ------------------------------------------------------------------
    # Classification (from classifier)
    # ------------------------------------------------------------------
    
    category: FailureCategory = FailureCategory.EXECUTION
    """Primary failure category."""
    
    severity: FailureSeverity = FailureSeverity.WARNING
    """Impact level of the failure."""
    
    lifecycle_state: FailureLifecycleState = FailureLifecycleState.DETECTED
    """Current state in lifecycle."""
    
    origin: FailureOrigin = FailureOrigin.CORE
    """Domain where failure originated."""
    
    # ------------------------------------------------------------------
    # Context information
    # ------------------------------------------------------------------
    
    source_component: str = ""
    """Component that detected/generated the failure."""
    
    affected_entity_ids: List[str] = field(default_factory=list)
    """IDs of entities directly affected."""
    
    affected_capability_ids: List[str] = field(default_factory=list)
    """IDs of capabilities affected."""
    
    resource_ids: List[str] = field(default_factory=list)
    """IDs of resources affected."""
    
    message: str = ""
    """Human-readable summary of the failure."""
    
    # ------------------------------------------------------------------
    # Execution context at time of failure
    # ------------------------------------------------------------------
    
    execution_context: Dict[str, Any] = field(default_factory=dict)
    """Execution context when failure occurred."""
    
    detected_at_utc: float = field(default_factory=time.time)
    """Timestamp of detection (UTC epoch seconds)."""
    
    logical_sequence: int = 0
    """Sequence number for ordering failures."""
    
    # ------------------------------------------------------------------
    # Recovery classification
    # ------------------------------------------------------------------
    
    retryability: Optional[bool] = None
    """True = safe to retry, False = unsafe, None = unknown."""
    
    rollback_eligibility: Optional[bool] = None
    """Can rollback to known prior state?"""
    
    recovery_eligibility: bool = True
    """Can attempt recovery from this failure?"""
    
    # ------------------------------------------------------------------
    # Propagation tracking
    # ------------------------------------------------------------------
    
    propagation_path: FailurePropagationPath = FailurePropagationPath.DIRECT
    """How failure propagated through the system."""
    
    propagation_timestamps: Dict[str, float] = field(default_factory=dict)
    """Timestamps for each propagation hop."""
    
    containment_scope: Set[str] = field(default_factory=set)
    """Entities/ids contained to prevent wider impact."""
    
    # ------------------------------------------------------------------
    # Recovery tracking
    # ------------------------------------------------------------------
    
    recovery_strategy: Optional[RecoveryStrategy] = None
    """Strategy selected for recovery."""
    
    recovered_at_utc: Optional[float] = None
    """Timestamp of successful recovery (if applicable)."""
    
    verified_at_utc: Optional[float] = None
    """Timestamp of verification success."""
    
    # ------------------------------------------------------------------
    # State at time of failure
    # ------------------------------------------------------------------
    
    integrity_impact: str = "unknown"  # none, degraded, corrupted
    security_impact: str = "none"      # none, suspected, confirmed
    
    unknown_outcome: bool = False
    """True if we cannot determine state after failure."""
    
    # ------------------------------------------------------------------
    # Provenance and metadata
    # ------------------------------------------------------------------
    
    provenance: Dict[str, str] = field(default_factory=dict)
    """Source tracking for audit trail."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional context-specific data."""
    
    diagnostic_data: List[str] = field(default_factory=list)
    """Diagnostic information collected."""
    
    # ------------------------------------------------------------------
    # Properties for quick inspection
    # ------------------------------------------------------------------
    
    @property
    def is_terminal(self) -> bool:
        """Check if failure is in a terminal state."""
        return self.lifecycle_state in (
            FailureLifecycleState.CLOSED,
            FailureLifecycleState.ESCALATED,
            FailureLifecycleState.ABORTED,
            FailureLifecycleState.UNRECOVERABLE,
        )
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this failure can potentially be recovered."""
        return (
            self.recovery_eligibility 
            and not (self.severity == FailureSeverity.FATAL)
            and not (self.category in (
                FailureCategory.CANCELLATION,
            ))
        )
    
    @property
    def is_retryable(self) -> bool:
        """Check if this failure can be retried."""
        return self.retryability is True
    
    @property
    def needs_escalation(self) -> bool:
        """Check if failure should be escalated to higher authority."""
        return (
            self.severity in (FailureSeverity.CRITICAL, FailureSeverity.FATAL)
            or not self.recovery_eligibility
        )
    
    @property
    def has_integrity_impact(self) -> bool:
        """Check if integrity may be affected."""
        return self.integrity_impact != "none"
    
    @property
    def lifecycle_duration_seconds(self) -> float:
        """Calculate total lifecycle duration from detection to current state."""
        now = time.time()
        return now - self.detected_at_utc
    
    # ------------------------------------------------------------------
    # State transition methods (immutable returns)
    # ------------------------------------------------------------------
    
    def with_state(self, new_state: FailureLifecycleState) -> "FailureArtifact":
        """Return copy with updated lifecycle state."""
        return dataclass_replace(self, lifecycle_state=new_state)
    
    def with_severity(self, new_severity: FailureSeverity) -> "FailureArtifact":
        """Return copy with updated severity."""
        return dataclass_replace(self, severity=new_severity)
    
    def with_recovery_strategy(
        self,
        strategy: RecoveryStrategy
    ) -> "FailureArtifact":
        """Return copy with recovery strategy set."""
        return dataclass_replace(
            self,
            recovery_strategy=strategy,
            lifecycle_state=FailureLifecycleState.RECOVERED,
            recovered_at_utc=time.time(),
        )
    
    def verify_recovery(self) -> "FailureArtifact":
        """Mark recovery as verified and close the lifecycle."""
        return dataclass_replace(
            self,
            lifecycle_state=FailureLifecycleState.VERIFIED,
            verified_at_utc=time.time(),
        ).with_state(FailureLifecycleState.CLOSED)
    
    def escalate(self) -> "FailureArtifact":
        """Escalate failure to higher authority."""
        return dataclass_replace(
            self,
            lifecycle_state=FailureLifecycleState.ESCALATED,
        )
    
    def abort(self) -> "FailureArtifact":
        """Abort the failure lifecycle."""
        return dataclass_replace(
            self,
            lifecycle_state=FailureLifecycleState.ABORTED,
        )
    
    def mark_unrecoverable(self) -> "FailureArtifact":
        """Mark failure as unrecoverable."""
        return dataclass_replace(
            self,
            recovery_eligibility=False,
            lifecycle_state=FailureLifecycleState.UNRECOVERABLE,
        )
    
    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    
    def to_dict(self) -> Dict[str, Any]:
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
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "severity": self.severity.value if hasattr(self.severity, 'value') else str(self.severity),
            "lifecycle_state": self.lifecycle_state.value if hasattr(self.lifecycle_state, 'value') else str(self.lifecycle_state),
            "origin": self.origin.value if hasattr(self.origin, 'value') else str(self.origin),
            "source_component": self.source_component,
            "affected_entity_ids": list(self.affected_entity_ids),
            "affected_capability_ids": list(self.affected_capability_ids),
            "resource_ids": list(self.resource_ids),
            "message": self.message,
            "execution_context": dict(self.execution_context),
            "detected_at_utc": self.detected_at_utc,
            "logical_sequence": self.logical_sequence,
            "retryability": self.retryability,
            "rollback_eligibility": self.rollback_eligibility,
            "recovery_eligibility": self.recovery_eligibility,
            "propagation_path": self.propagation_path.value if hasattr(self.propagation_path, 'value') else str(self.propagation_path),
            "propagation_timestamps": dict(self.propagation_timestamps),
            "containment_scope": list(self.containment_scope),
            "recovery_strategy": self.recovery_strategy.value if self.recovery_strategy and hasattr(self.recovery_strategy, 'value') else None,
            "recovered_at_utc": self.recovered_at_utc,
            "verified_at_utc": self.verified_at_utc,
            "integrity_impact": self.integrity_impact,
            "security_impact": self.security_impact,
            "unknown_outcome": self.unknown_outcome,
            "provenance": dict(self.provenance),
            "metadata": self._serialize_metadata(self.metadata),
            "diagnostic_data": list(self.diagnostic_data),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureArtifact":
        """Create FailureArtifact from serialized dictionary."""
        return cls(
            failure_id=data["failure_id"],
            runtime_id=data.get("runtime_id"),
            operation_id=data.get("operation_id"),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            category=cls._parse_enum(data.get("category"), FailureCategory, FailureCategory.EXECUTION),
            severity=cls._parse_enum(data.get("severity"), FailureSeverity, FailureSeverity.WARNING),
            lifecycle_state=cls._parse_enum(data.get("lifecycle_state"), FailureLifecycleState, FailureLifecycleState.DETECTED),
            origin=cls._parse_enum(data.get("origin"), FailureOrigin, FailureOrigin.CORE),
            source_component=data.get("source_component", ""),
            affected_entity_ids=data.get("affected_entity_ids", []),
            affected_capability_ids=data.get("affected_capability_ids", []),
            resource_ids=data.get("resource_ids", []),
            message=data.get("message", ""),
            execution_context=data.get("execution_context", {}),
            detected_at_utc=data.get("detected_at_utc", time.time()),
            logical_sequence=data.get("logical_sequence", 0),
            retryability=data.get("retryability"),
            rollback_eligibility=data.get("rollback_eligibility"),
            recovery_eligibility=data.get("recovery_eligibility", True),
            propagation_path=cls._parse_enum(data.get("propagation_path"), FailurePropagationPath, FailurePropagationPath.DIRECT),
            propagation_timestamps=data.get("propagation_timestamps", {}),
            containment_scope=set(data.get("containment_scope", [])),
            recovery_strategy=(
                cls._parse_enum(data.get("recovery_strategy"), RecoveryStrategy, None)
                if data.get("recovery_strategy") else None
            ),
            recovered_at_utc=data.get("recovered_at_utc"),
            verified_at_utc=data.get("verified_at_utc"),
            integrity_impact=data.get("integrity_impact", "unknown"),
            security_impact=data.get("security_impact", "none"),
            unknown_outcome=data.get("unknown_outcome", False),
            provenance=data.get("provenance", {}),
            metadata=cls._deserialize_metadata(data.get("metadata", {})),
            diagnostic_data=data.get("diagnostic_data", []),
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
            if isinstance(v, (Enum,)):
                result[k] = v.value if hasattr(v, 'value') else str(v)
            elif isinstance(v, (set,)):
                result[k] = list(v)
            else:
                result[k] = v
        return result
    
    @staticmethod
    def _deserialize_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize metadata from storage/transmission."""
        return dict(data)


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    This is a helper for immutable updates to FailureArtifact instances.
    """
    import copy
    new_instance = copy.copy(instance)
    for key, value in kwargs.items():
        object.__setattr__(new_instance, key, value)
    return new_instance


# =============================================================================
# FAILURE CLASSIFIER
# =============================================================================

class FailureClassifier:
    """
    Canonical failure classifier.
    
    Classifies failures into proper categories based on:
        - Exception type
        - Context information
        - Source component
        - Impact assessment
        
    Classification is idempotent and deterministic.
    """
    
    def __init__(self) -> None:
        """Initialize the classifier."""
        self._category_rules: Dict[str, FailureCategory] = {}
        self._severity_rules: Dict[str, FailureSeverity] = {}
        
        # Register default classification rules
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Register default failure classification rules."""
        # Validation failures
        self.register_category_rule(ValueError, FailureCategory.VALIDATION)
        self.register_category_rule(TypeError, FailureCategory.VALIDATION)
        
        # Execution failures
        self.register_category_rule(RuntimeError, FailureCategory.EXECUTION)
        self.register_category_rule(NotImplementedError, FailureCategory.EXECUTION)
        
        # Timeout failures
        self.register_category_rule(TimeoutError, FailureCategory.TIMEOUT)
        
        # Resource failures  
        self.register_category_rule(MemoryError, FailureCategory.RESOURCE)
        self.register_category_rule(PermissionError, FailureCategory.RESOURCE)
        self.register_category_rule(FileNotFoundError, FailureCategory.RESOURCE)
        
        # Security failures
        self.register_category_rule(SecurityError, FailureCategory.SECURITY)
        self.register_category_rule(AuthenticationError, FailureCategory.SECURITY)
        self.register_category_rule(AuthorizationError, FailureCategory.SECURITY)
    
    def register_category_rule(self, exception_type: type, category: FailureCategory) -> None:
        """Register a classification rule for an exception type."""
        self._category_rules[exception_type.__name__] = category
    
    def classify(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[FailureCategory, FailureSeverity]:
        """
        Classify an exception into category and severity.
        
        Args:
            exception: The exception to classify
            context: Additional context for classification
            
        Returns:
            Tuple of (category, severity)
        """
        # Check specific exception type first
        exc_name = type(exception).__name__
        if exc_name in self._category_rules:
            return self._category_rules[exc_name], self._determine_severity(exception, context)
        
        # Check base classes
        for base_class in type(exception).__mro__:
            base_name = base_class.__name__
            if base_name in self._category_rules:
                return self._category_rules[base_name], self._determine_severity(exception, context)
        
        # Default classification
        return FailureCategory.EXECUTION, self._determine_severity(exception, context)
    
    def _determine_severity(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> FailureSeverity:
        """Determine severity based on exception and context."""
        # Check for explicit severity in context
        if context and "severity" in context:
            try:
                return FailureSeverity(context["severity"])
            except ValueError:
                pass
        
        # Determine from exception type and message
        exc_name = type(exception).__name__
        
        if exc_name.endswith("FatalError"):
            return FailureSeverity.FATAL
        if exc_name.endswith("CriticalError") or "critical" in str(exception).lower():
            return FailureSeverity.CRITICAL
        if exc_name.endswith("SeriousError") or "serious" in str(exception).lower():
            return FailureSeverity.SERIOUS
        if exc_name.endswith("RecoverableError"):
            return FailureSeverity.RECOVERABLE
        if exc_name.endswith("WarningError"):
            return FailureSeverity.WARNING
        
        # Default to WARNING for unknown errors
        return FailureSeverity.WARNING
    
    def create_failure_artifact(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        origin: Optional[FailureOrigin] = None,
        source_component: str = "unknown"
    ) -> FailureArtifact:
        """
        Create a FailureArtifact from an exception.
        
        Args:
            exception: The exception that occurred
            context: Additional context information
            origin: Where the failure originated
            source_component: Component reporting the failure
            
        Returns:
            Fully populated FailureArtifact
        """
        category, severity = self.classify(exception, context)
        if origin is None:
            origin = FailureOrigin.CORE
        
        return FailureArtifact(
            failure_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            lifecycle_state=FailureLifecycleState.DETECTED,
            origin=origin,
            source_component=source_component,
            message=str(exception),
            execution_context=context or {},
            retryability=self._determine_retryability(exception),
            rollback_eligibility=self._determine_rollback_eligibility(exception, context),
        )
    
    def _determine_retryability(self, exception: Exception) -> Optional[bool]:
        """Determine if the failure is safe to retry."""
        exc_name = type(exception).__name__
        
        # Never retry terminal failures
        if exc_name.endswith(("FatalError", "CriticalError")):
            return False
        
        # Retry transient failures
        if exc_name in ("ConnectionError", "TimeoutError"):
            return True
            
        # Unknown errors - don't retry by default
        return None
    
    def _determine_rollback_eligibility(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[bool]:
        """Determine if rollback is a viable recovery option."""
        # If integrity is impacted, rollback may not help
        if context and "integrity_impact" in context:
            if context["integrity_impact"] == "corrupted":
                return False
        
        exc_name = type(exception).__name__
        
        # Some failures don't benefit from rollback
        if exc_name in ("TimeoutError",):
            return None  # Unknown - depends on context
            
        return True


# =============================================================================
# FAILURE CONTAINER (Integration Wrapper)
# =============================================================================

@dataclass(frozen=True)
class FailureContainer:
    """
    Container for failures that may occur during component operation.
    
    This provides a uniform interface for returning failures from
    operations without raising exceptions.
    """
    
    failure: Optional[FailureArtifact] = None
    """The failure artifact if operation failed, None on success."""
    
    result: Optional[Any] = None
    """Operation result if successful."""
    
    @property
    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self.failure is None
    
    @property
    def is_failure(self) -> bool:
        """Check if operation failed."""
        return self.failure is not None
    
    @classmethod
    def success(cls, result: Any = None) -> "FailureContainer":
        """Create a successful container."""
        return cls(failure=None, result=result)
    
    @classmethod
    def failure(cls, artifact: FailureArtifact) -> "FailureContainer":
        """Create a failed container."""
        return cls(failure=artifact, result=None)


# =============================================================================
# FAILURE PROPAGATOR
# =============================================================================

class FailurePropagator:
    """
    Canonical failure propagation coordinator.
    
    Manages how failures propagate through the system while preserving
    architectural ownership and authority boundaries.
    """
    
    def __init__(self) -> None:
        """Initialize the propagator."""
        self._handlers: Dict[FailureCategory, List[Any]] = {}
        self._propagation_history: List[Dict[str, Any]] = []
    
    def register_handler(
        self,
        category: FailureCategory,
        handler: Any
    ) -> None:
        """Register a propagation handler for a failure category."""
        if category not in self._handlers:
            self._handlers[category] = []
        self._handlers[category].append(handler)
    
    def propagate(
        self,
        artifact: FailureArtifact,
        target_origin: Optional[FailureOrigin] = None
    ) -> Tuple[FailureArtifact, bool]:
        """
        Propagate a failure to appropriate handlers.
        
        Args:
            artifact: The failure to propagate
            target_origin: Target domain for propagation
            
        Returns:
            Tuple of (updated artifact, propagated successfully)
        """
        # Update propagation path and timestamp
        updated = artifact.with_state(FailureLifecycleState.PROPAGATED)
        updated = dataclass_replace(
            updated,
            propagation_timestamps={
                **artifact.propagation_timestamps,
                f"propagated_to_{target_origin.value if target_origin else 'unknown'}": time.time(),
            },
        )
        
        # Find applicable handlers
        handlers = self._handlers.get(updated.category, [])
        propagated = False
        
        for handler in handlers:
            try:
                # Handler can modify the artifact
                result = handler(updated)
                if isinstance(result, FailureArtifact):
                    updated = result
                propagated = True
            except Exception as e:
                # Handler failure doesn't stop propagation
                pass
        
        self._propagation_history.append({
            "failure_id": updated.failure_id,
            "category": updated.category.value,
            "severity": updated.severity.value,
            "timestamp": time.time(),
        })
        
        return updated, propagated
    
    def get_propagation_history(self) -> List[Dict[str, Any]]:
        """Get history of all propagations."""
        return list(self._propagation_history)


# =============================================================================
# FAILURE CONTAINER (Local Scope)
# =============================================================================

class FailureContainmentScope:
    """
    Local containment scope for a failure.
    
    Ensures failures remain localized within their boundary while
    preserving the ability to escalate if needed.
    """
    
    def __init__(self, component_id: str):
        """Initialize containment scope."""
        self.component_id = component_id
        self._contained_entities: Set[str] = set()
        self._contained_resources: Set[str] = set()
    
    def contain_entity(self, entity_id: str) -> None:
        """Add an entity to the containment scope."""
        self._contained_entities.add(entity_id)
    
    def contain_resource(self, resource_id: str) -> None:
        """Add a resource to the containment scope."""
        self._contained_resources.add(resource_id)
    
    def contains_entity(self, entity_id: str) -> bool:
        """Check if entity is in containment scope."""
        return entity_id in self._contained_entities
    
    def get_scope_summary(self) -> Dict[str, Any]:
        """Get summary of current containment scope."""
        return {
            "component_id": self.component_id,
            "contained_entities": list(self._contained_entities),
            "contained_resources": list(self._contained_resources),
        }


# =============================================================================
# FAILURE ESCALATION POLICY
# =============================================================================

@dataclass(frozen=True)
class EscalationPolicy:
    """
    Policy for when and how failures are escalated.
    
    Escalation shall be deterministic and preserve provenance.
    Repeated escalation loops are prohibited.
    """
    
    max_escalation_level: int = 3
    """Maximum number of escalation levels."""
    
    escalate_on_severity: Set[FailureSeverity] = field(default_factory=lambda: {
        FailureSeverity.CRITICAL,
        FailureSeverity.FATAL,
    })
    """Severities that trigger automatic escalation."""
    
    escalate_on_recovery_failure: bool = True
    """Escalate when recovery attempts fail."""
    
    escalation_delay_seconds: float = 0.0
    """Delay before escalation (allows local recovery)."""
    
    def should_escalate(self, artifact: FailureArtifact) -> bool:
        """Check if failure should be escalated."""
        # Check severity-based escalation
        if artifact.severity in self.escalate_on_severity:
            return True
        
        # Check recovery failure escalation
        if self.escalate_on_recovery_failure and not artifact.recovery_eligibility:
            return True
        
        return False
    
    def get_escalation_path(self, current_level: int) -> List[str]:
        """Get the escalation path from current level."""
        return [f"level_{i}" for i in range(current_level + 1, self.max_escalation_level + 1)]


# =============================================================================
# RECOVERY PLANNER
# =============================================================================

class RecoveryPlanner:
    """
    Canonical recovery planner.
    
    Plans and orchestrates recovery actions while preserving architectural
    integrity and ownership boundaries.
    """
    
    def __init__(self) -> None:
        """Initialize the planner."""
        self._recovery_strategies: Dict[FailureCategory, List[RecoveryStrategy]] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self) -> None:
        """Register default recovery strategies by category."""
        # Validation failures - retry with corrected input
        self.register_strategy(FailureCategory.VALIDATION, RecoveryStrategy.RETRY)
        
        # Timeout failures - retry or failover
        self.register_strategy(FailureCategory.TIMEOUT, RecoveryStrategy.RETRY)
        self.register_strategy(FailureCategory.TIMEOUT, RecoveryStrategy.FAILOVER)
        
        # Resource failures - restore or allocate
        self.register_strategy(FailureCategory.RESOURCE, RecoveryStrategy.RESTART)
        self.register_strategy(FailureCategory.RESOURCE, RecoveryStrategy.REINITIALIZE)
        
        # Capability failures - restart capability
        self.register_strategy(FailureCategory.CAPABILITY, RecoveryStrategy.RESTART)
        
        # Stream failures - restore checkpoint
        self.register_strategy(FailureCategory.STREAM, RecoveryStrategy.RESTORE_CHECKPOINT)
        self.register_strategy(FailureCategory.STREAM, RecoveryStrategy.ROLLBACK)
    
    def register_strategy(
        self,
        category: FailureCategory,
        strategy: RecoveryStrategy
    ) -> None:
        """Register a recovery strategy for a failure category."""
        if category not in self._recovery_strategies:
            self._recovery_strategies[category] = []
        self._recovery_strategies[category].append(strategy)
    
    def plan_recovery(
        self,
        artifact: FailureArtifact
    ) -> Optional[List[RecoveryStrategy]]:
        """
        Plan recovery strategies for a failure.
        
        Args:
            artifact: The failure to plan recovery for
            
        Returns:
            Ordered list of recovery strategies to attempt, or None if no valid plan
        """
        # Check terminal conditions first
        if not artifact.recovery_eligibility:
            return None
        
        # Get strategies for this category
        strategies = self._recovery_strategies.get(artifact.category, [])
        
        if not strategies:
            return [RecoveryStrategy.GRACEFUL_SHUTDOWN]
        
        # Return ordered list of strategies to attempt
        return strategies
    
    def select_recovery_strategy(
        self,
        artifact: FailureArtifact
    ) -> Optional[RecoveryStrategy]:
        """Select best recovery strategy for failure."""
        plans = self.plan_recovery(artifact)
        return plans[0] if plans else None


# =============================================================================
# RECOVERY COORDINATOR
# =============================================================================

class RecoveryCoordinator:
    """
    Canonical recovery coordinator.
    
    Coordinates recovery actions across domains while ensuring:
        - Ownership boundaries are preserved
        - Authority constraints are respected
        - State integrity is maintained
    """
    
    def __init__(self) -> None:
        """Initialize the coordinator."""
        self._recovery_history: List[Dict[str, Any]] = []
    
    def execute_recovery(
        self,
        artifact: FailureArtifact,
        strategy: RecoveryStrategy,
        domain_owners: Dict[FailureOrigin, Any]
    ) -> Tuple[bool, Optional[FailureArtifact]]:
        """
        Execute recovery for a failure.
        
        Args:
            artifact: The failure to recover from
            strategy: The recovery strategy to use
            domain_owners: Dictionary of domain owners for coordination
            
        Returns:
            Tuple of (success, updated artifact)
        """
        # Validate ownership boundaries
        owner = domain_owners.get(artifact.origin)
        
        if owner is None:
            # No owner for this domain - escalate
            return False, artifact.escalate()
        
        # Execute recovery based on strategy
        try:
            success = self._execute_strategy(strategy, artifact, owner)
            
            if success:
                updated = artifact.verify_recovery()
                self._recovery_history.append({
                    "failure_id": artifact.failure_id,
                    "strategy": strategy.value,
                    "success": True,
                    "timestamp": time.time(),
                })
                return True, updated
            else:
                # Recovery failed - mark as such
                updated = artifact.mark_unrecoverable()
                self._recovery_history.append({
                    "failure_id": artifact.failure_id,
                    "strategy": strategy.value,
                    "success": False,
                    "timestamp": time.time(),
                })
                return False, updated
                
        except Exception as e:
            # Recovery threw an exception
            error_artifact = FailureArtifact(
                failure_id=str(uuid.uuid4()),
                category=FailureCategory.RECOVERY,
                severity=FailureSeverity.SERIOUS,
                lifecycle_state=FailureLifecycleState.ABORTED,
                origin=artifact.origin,
                source_component="recovery_coordinator",
                message=f"Recovery execution failed: {str(e)}",
            )
            self._recovery_history.append({
                "failure_id": artifact.failure_id,
                "strategy": strategy.value,
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            })
            return False, error_artifact
    
    def _execute_strategy(
        self,
        strategy: RecoveryStrategy,
        artifact: FailureArtifact,
        owner: Any
    ) -> bool:
        """Execute a specific recovery strategy."""
        # Each domain owner would implement their own recovery logic
        # This is a placeholder for the coordination interface
        
        strategies_that_dont_need_owner = {
            RecoveryStrategy.DEGRADE,  # Can be handled at current level
            RecoveryStrategy.GRACEFUL_SHUTDOWN,
            RecoveryStrategy.TERMINATE,
        }
        
        if strategy in strategies_that_dont_need_owner:
            return True  # Local decision
        
        # For other strategies, delegate to domain owner
        return hasattr(owner, 'recover') and callable(getattr(owner, 'recover'))
    
    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Get history of all recovery operations."""
        return list(self._recovery_history)


# =============================================================================
# OBSERVABILITY CONTRACTS
# =============================================================================

@dataclass(frozen=True)
class FailureObservabilityData:
    """
    Immutable observability data for failures and recoveries.
    
    Every failure and recovery activity shall expose immutable diagnostic
    metadata for audit and replay purposes.
    """
    
    # Core identifiers
    failure_id: str
    """Unique identifier for the failure."""
    
    recovery_id: Optional[str] = None
    """Identifier for the recovery operation (if any)."""
    
    # Classification data
    category: str
    severity: str
    
    # Lifecycle data
    lifecycle_state: str
    propagation_path: str
    
    # Timing data
    detected_at_utc: float
    recovered_at_utc: Optional[float] = None
    verified_at_utc: Optional[float] = None
    
    # Origin data
    originating_component: str
    origin_domain: str
    
    # Outcome data
    recovery_strategy: Optional[str] = None
    outcome: str  # recovered, escalated, aborted, unrecoverable
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for observability systems."""
        return {
            "failure_id": self.failure_id,
            "recovery_id": self.recovery_id,
            "category": self.category,
            "severity": self.severity,
            "lifecycle_state": self.lifecycle_state,
            "propagation_path": self.propagation_path,
            "detected_at_utc": self.detected_at_utc,
            "recovered_at_utc": self.recovered_at_utc,
            "verified_at_utc": self.verified_at_utc,
            "originating_component": self.originating_component,
            "origin_domain": self.origin_domain,
            "recovery_strategy": self.recovery_strategy,
            "outcome": self.outcome,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums (Classification)
    "FailureCategory",
    "FailureSeverity",
    "FailureLifecycleState",
    "FailurePropagationPath",
    
    # Recovery enums
    "RecoveryStrategy",
    "FailureOrigin",
    
    # Core types
    "FailureArtifact",
    "FailureClassifier",
    "FailureContainer",
    "FailurePropagator",
    "FailureContainmentScope",
    
    # Policy and planning
    "EscalationPolicy",
    "RecoveryPlanner",
    "RecoveryCoordinator",
    
    # Observability
    "FailureObservabilityData",
]