# Core Failure Classification Model
# ================================

"""
Failure classification and management for runtime failures.

This module provides:
- Typed failure representation with causal chains
- Recoverability classification
- Occurrence tracking and deduplication
- Blast radius analysis
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from enum import Enum, auto
import time


# =============================================================================
# Failure Categories
# =============================================================================

class FailureCategory(Enum):
    """
    Generic failure categories for classification.
    
    Categories help determine appropriate recovery actions and
    aggregate related failures for reporting.
    """
    
    # Configuration
    CONFIGURATION = "configuration"  # Invalid or missing configuration
    
    # Dependency
    DEPENDENCY = "dependency"        # Dependency resolution failures
    
    # Lifecycle
    LIFECYCLE = "lifecycle"          # Lifecycle state violations
    
    # Registry
    REGISTRY = "registry"            # Registration errors
    
    # Context
    CONTEXT = "context"              # Runtime context errors
    
    # State
    STATE = "state"                  # State management errors
    
    # Bootstrap/Loading
    BOOTSTRAP = "bootstrap"          # Startup initialization failures
    PREFLIGHT = "preflight"          # Pre-startup validation failures
    LOADING = "loading"              # Module/component loading failures
    INITIALIZATION = "initialization"  # Component initialization failures
    
    # Execution
    EXECUTION = "execution"          # Task execution failures
    SCHEDULING = "scheduling"        # Scheduling errors
    CANCELLATION = "cancellation"    # Cancellation errors
    TIMEOUT = "timeout"              # Operation timeout
    
    # Resource
    RESOURCE = "resource"            # Resource management errors
    
    # Integrity/Health
    INTEGRITY = "integrity"          # Integrity validation failures
    HEALTH = "health"                # Health check failures
    
    # Security
    SECURITY = "security"            # Security-related failures
    
    # Shutdown
    SHUTDOWN = "shutdown"            # Shutdown errors
    
    # Unknown
    UNKNOWN = "unknown"              # Unspecified category


# =============================================================================
# Recoverability Classification
# =============================================================================

class Recoverability(Enum):
    """
    Recovery classification for failures.
    
    Determines whether and how a failure can be recovered:
        - RECOVERABLE: Can be handled through recovery actions
        - CONDITIONALLY_RECOVERABLE: Can recover with specific conditions met
        - NON_RECOVERABLE: Cannot be recovered, requires escalation
        - UNKNOWN: Unknown (needs evaluation)
    """
    
    RECOVERABLE = "recoverable"              # Recovery is possible
    CONDITIONALLY_RECOVERABLE = "conditionally_recoverable"  # Only under certain conditions
    NON_RECOVERABLE = "non_recoverable"      # Cannot recover, escalate needed
    UNKNOWN = "unknown"                      # Need to evaluate


# =============================================================================
# Failure Record
# =============================================================================

@dataclass(frozen=True)
class FailureRecord:
    """
    A structured failure record.
    
    A failure is not merely an exception string. It preserves:
    - Causal chain for root cause analysis
    - Recoverability classification
    - Occurrence tracking and deduplication
    - Context for appropriate recovery
    
    Usage:
        try:
            risky_operation()
        except Exception as e:
            failure = FailureRecord.from_exception(
                error=e,
                runtime_id=runtime_id,
                entity_id=entity_id,
                category=FailureCategory.EXECUTION
            )
            
            if failure.recoverability == Recoverability.RECOVERABLE:
                await initiate_recovery(failure)
    """
    
    # Identification
    failure_id: str  # Unique identifier for this failure occurrence
    
    # Classification
    category: FailureCategory  # What type of failure is this?
    
    severity: int = field(default=3)  # Severity level (0-7, matching EventSeverity)
    primary: bool = True  # Is this the primary failure or secondary effect?
    
    # Context
    runtime_id: Optional[str] = None  # Runtime instance identifier
    source_entity_id: Optional[str] = None  # Entity where failure occurred
    task_id: Optional[str] = None     # Task context (if any)
    
    # Lifecycle at time of failure
    lifecycle_state: str = ""         # Entity's lifecycle state
    execution_state: str = ""         # Execution state
    
    # Primary failure details
    primary_exception_type: str = ""  # Exception class name
    primary_exception_message: str = ""  # Exception message
    primary_exception_traceback: Optional[str] = None  # Full traceback if available
    
    # Causal chain (for root cause analysis)
    causal_chain: List["FailureRecord"] = field(default_factory=list)  # Causes
    
    # Occurrence tracking
    first_occurrence_utc: float = field(default_factory=time.time)
    latest_occurrence_utc: float = field(default_factory=time.time)
    occurrence_count: int = 1
    
    # Transient vs persistent
    is_transient: bool = False  # Temporary condition (might recover)
    is_persistent: bool = False  # Ongoing issue
    
    # Recovery classification
    recoverability: Recoverability = Recoverability.UNKNOWN
    
    # Blast radius analysis
    blast_radius: List[str] = field(default_factory=list)  # Affected entities
    affected_dependencies: List[str] = field(default_factory=list)
    affected_resources: List[str] = field(default_factory=list)
    
    # Diagnostic evidence
    diagnostic_evidence: Dict[str, Any] = field(default_factory=dict)
    
    # Recommended action
    recommended_action: str = ""  # Suggested recovery or escalation
    
    @property
    def is_recoverable(self) -> bool:
        """Check if this failure can be recovered."""
        return self.recoverability in (
            Recoverability.RECOVERABLE,
            Recoverability.CONDITIONALLY_RECOVERABLE
        )
    
    @property
    def duration_seconds(self) -> float:
        """Calculate time since first occurrence."""
        return time.time() - self.first_occurrence_utc
    
    def with_causal_chain(self, causes: List["FailureRecord"]) -> "FailureRecord":
        """Return a copy with additional causal failures."""
        new_chain = list(self.causal_chain)
        for cause in causes:
            if cause not in new_chain:
                new_chain.append(cause)
        
        return FailureRecord(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            causal_chain=new_chain,
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1,
            is_transient=self.is_transient,
            is_persistent=self.is_persistent,
            recoverability=self.recoverability,
            blast_radius=list(self.blast_radius),
            affected_dependencies=list(self.affected_dependencies),
            affected_resources=list(self.affected_resources),
            diagnostic_evidence=dict(self.diagnostic_evidence),
            recommended_action=self.recommended_action
        )
    
    def mark_transient(self) -> "FailureRecord":
        """Return a copy marked as transient."""
        return FailureRecord(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            causal_chain=list(self.causal_chain),
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1,
            is_transient=True,
            is_persistent=False,
            recoverability=self.recoverability,
            blast_radius=list(self.blast_radius),
            affected_dependencies=list(self.affected_dependencies),
            affected_resources=list(self.affected_resources),
            diagnostic_evidence=dict(self.diagnostic_evidence),
            recommended_action=self.recommended_action
        )
    
    def mark_persistent(self) -> "FailureRecord":
        """Return a copy marked as persistent."""
        return FailureRecord(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            causal_chain=list(self.causal_chain),
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1,
            is_transient=False,
            is_persistent=True,
            recoverability=Recoverability.NON_RECOVERABLE,
            blast_radius=list(self.blast_radius),
            affected_dependencies=list(self.affected_dependencies),
            affected_resources=list(self.affected_resources),
            diagnostic_evidence=dict(self.diagnostic_evidence),
            recommended_action="ESCALATE"
        )
    
    def classify_as_recoverable(self, action: str = "RETRY") -> "FailureRecord":
        """Return a copy classified as recoverable."""
        return FailureRecord(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            causal_chain=list(self.causal_chain),
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1,
            is_transient=self.is_transient,
            is_persistent=self.is_persistent,
            recoverability=Recoverability.RECOVERABLE,
            blast_radius=list(self.blast_radius),
            affected_dependencies=list(self.affected_dependencies),
            affected_resources=list(self.affected_resources),
            diagnostic_evidence=dict(self.diagnostic_evidence),
            recommended_action=action
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "failure_id": self.failure_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "severity": self.severity,
            "primary": self.primary,
            "runtime_id": self.runtime_id,
            "source_entity_id": self.source_entity_id,
            "task_id": self.task_id,
            "lifecycle_state": self.lifecycle_state,
            "execution_state": self.execution_state,
            "primary_exception_type": self.primary_exception_type,
            "primary_exception_message": self.primary_exception_message,
            "primary_exception_traceback": self.primary_exception_traceback,
            "causal_chain_count": len(self.causal_chain),
            "first_occurrence_utc": self.first_occurrence_utc,
            "latest_occurrence_utc": self.latest_occurrence_utc,
            "occurrence_count": self.occurrence_count,
            "is_transient": self.is_transient,
            "is_persistent": self.is_persistent,
            "recoverability": self.recoverability.value if hasattr(self.recoverability, 'value') else str(self.recoverability),
            "blast_radius": self.blast_radius,
            "affected_dependencies": self.affected_dependencies,
            "affected_resources": self.affected_resources,
            "diagnostic_evidence": self.diagnostic_evidence,
            "recommended_action": self.recommended_action
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureRecord":
        """Create a failure record from a dictionary."""
        return cls(
            failure_id=data["failure_id"],
            category=cls._parse_category(data.get("category")),
            severity=data.get("severity", 3),
            primary=data.get("primary", True),
            runtime_id=data.get("runtime_id"),
            source_entity_id=data.get("source_entity_id"),
            task_id=data.get("task_id"),
            lifecycle_state=data.get("lifecycle_state", ""),
            execution_state=data.get("execution_state", ""),
            primary_exception_type=data.get("primary_exception_type", ""),
            primary_exception_message=data.get("primary_exception_message", ""),
            primary_exception_traceback=data.get("primary_exception_traceback"),
            causal_chain=[],
            first_occurrence_utc=data.get("first_occurrence_utc", time.time()),
            latest_occurrence_utc=data.get("latest_occurrence_utc", time.time()),
            occurrence_count=data.get("occurrence_count", 1),
            is_transient=data.get("is_transient", False),
            is_persistent=data.get("is_persistent", False),
            recoverability=cls._parse_recoverability(data.get("recoverability")),
            blast_radius=data.get("blast_radius", []),
            affected_dependencies=data.get("affected_dependencies", []),
            affected_resources=data.get("affected_resources", []),
            diagnostic_evidence=data.get("diagnostic_evidence", {}),
            recommended_action=data.get("recommended_action", "")
        )
    
    @classmethod
    def create(
        cls,
        category: FailureCategory,
        primary_exception_type: str,
        primary_exception_message: str,
        runtime_id: Optional[str] = None,
        source_entity_id: Optional[str] = None,
        task_id: Optional[str] = None,
        lifecycle_state: str = "",
        execution_state: str = "",
        is_transient: bool = False,
        blast_radius: Optional[List[str]] = None,
        **diagnostic_evidence
    ) -> "FailureRecord":
        """
        Create a new failure record.
        
        Args:
            category: Failure category (determines recovery options)
            primary_exception_type: Exception class name
            primary_exception_message: Exception message
            runtime_id: Runtime instance identifier
            source_entity_id: Entity where failure occurred
            task_id: Task context
            lifecycle_state: Entity's lifecycle state at time of failure
            execution_state: Execution state at time of failure
            is_transient: Whether this is a temporary condition
            blast_radius: List of affected entities
            **diagnostic_evidence: Additional diagnostic information
            
        Returns:
            A new FailureRecord instance
        """
        return cls(
            failure_id=f"failure_{time.monotonic_ns()}",
            category=category,
            severity=3,  # INFO default
            primary=True,
            runtime_id=runtime_id,
            source_entity_id=source_entity_id,
            task_id=task_id,
            lifecycle_state=lifecycle_state,
            execution_state=execution_state,
            primary_exception_type=primary_exception_type,
            primary_exception_message=primary_exception_message,
            causal_chain=[],
            first_occurrence_utc=time.time(),
            latest_occurrence_utc=time.time(),
            occurrence_count=1,
            is_transient=is_transient,
            is_persistent=False,
            recoverability=(
                Recoverability.RECOVERABLE if is_transient
                else Recoverability.CONDITIONALLY_RECOVERABLE
            ),
            blast_radius=blast_radius or [],
            affected_dependencies=[],
            affected_resources=[],
            diagnostic_evidence=diagnostic_evidence,
            recommended_action="RETRY" if is_transient else "ESCALATE"
        )
    
    @staticmethod
    def _parse_category(category_value: Any) -> FailureCategory:
        """Parse a category value into a FailureCategory enum."""
        if isinstance(category_value, FailureCategory):
            return category_value
        
        if isinstance(category_value, str):
            try:
                return FailureCategory(category_value)
            except ValueError:
                pass
        
        return FailureCategory.UNKNOWN
    
    @staticmethod
    def _parse_recoverability(value: Any) -> Recoverability:
        """Parse a recoverability value into a Recoverability enum."""
        if isinstance(value, Recoverability):
            return value
        
        if isinstance(value, str):
            try:
                return Recoverability(value)
            except ValueError:
                pass
        
        return Recoverability.UNKNOWN


# =============================================================================
# Failure Deduplication
# =============================================================================

@dataclass
class FailureDeduplicator:
    """
    Deduplicate related failures for reporting.
    
    Groups identical or similar failures and tracks:
    - Total occurrence count
    - First and latest occurrence times
    - Affected tasks
    
    This does NOT merge unrelated failures - only groups repeated occurrences
    of the same failure condition.
    """
    
    _failures: Dict[str, FailureRecord] = field(default_factory=dict)
    
    def add(self, record: FailureRecord) -> None:
        """Add or update a failure record."""
        key = self._dedup_key(record)
        
        if key in self._failures:
            existing = self._failures[key]
            
            # Update occurrence count and timestamp
            self._failures[key] = FailureRecord(
                failure_id=existing.failure_id,
                category=record.category,
                severity=record.severity,
                primary=record.primary,
                runtime_id=record.runtime_id or existing.runtime_id,
                source_entity_id=record.source_entity_id or existing.source_entity_id,
                task_id=record.task_id or existing.task_id,
                lifecycle_state=record.lifecycle_state or existing.lifecycle_state,
                execution_state=record.execution_state or existing.execution_state,
                primary_exception_type=existing.primary_exception_type,
                primary_exception_message=existing.primary_exception_message,
                primary_exception_traceback=existing.primary_exception_traceback,
                causal_chain=list(existing.causal_chain),
                first_occurrence_utc=existing.first_occurrence_utc,
                latest_occurrence_utc=time.time(),
                occurrence_count=existing.occurrence_count + 1,
                is_transient=record.is_transient,
                is_persistent=record.is_persistent,
                recoverability=record.recoverability,
                blast_radius=list(record.blast_radius),
                affected_dependencies=list(record.affected_dependencies),
                affected_resources=list(record.affected_resources),
                diagnostic_evidence=dict(existing.diagnostic_evidence),
                recommended_action=record.recommended_action
            )
        else:
            self._failures[key] = record
    
    def get(self, key: str) -> Optional[FailureRecord]:
        """Get a deduplicated failure by key."""
        return self._failures.get(key)
    
    def get_all(self) -> List[FailureRecord]:
        """Get all deduplicated failures."""
        return list(self._failures.values())
    
    def remove(self, key: str) -> None:
        """Remove a failure from the deduplicator."""
        if key in self._failures:
            del self._failures[key]
    
    def clear(self) -> None:
        """Clear all failures."""
        self._failures.clear()
    
    def _dedup_key(self, record: FailureRecord) -> str:
        """
        Generate a deduplication key for a failure.
        
        Uses core attributes to identify if two failures are the same condition
        (not just the same exception type).
        """
        return (
            f"{record.category.value}"
            f"|{record.primary_exception_type}"
            f"|{record.source_entity_id or ''}"
            f"|{record.task_id or ''}"
        )


# =============================================================================
# Runtime Failure Model (Phase 3.7+)
# =============================================================================

@dataclass(frozen=True)
class RuntimeFailure:
    """
    A runtime-level failure that affects system operation.
    
    Extends FailureRecord with runtime-specific context:
        - Impact scope (which entities are affected)
        - Recovery strategy (automated vs manual)
        - Alerting configuration
        - Escalation path
    
    Usage:
        failure = RuntimeFailure.from_failure_record(
            record=my_failure,
            impact_scope=["service_a", "service_b"],
            recovery_strategy=RecoveryStrategy.AUTOMATED_RETRY,
            alert_level=AlertLevel.HIGH
        )
        
        if failure.should_alert:
            await send_alert(failure)
    """
    
    # Base failure info (from FailureRecord)
    failure_id: str
    
    category: FailureCategory
    severity: int
    primary: bool
    
    # Runtime-specific context
    runtime_id: Optional[str] = None
    source_entity_id: Optional[str] = None
    task_id: Optional[str] = None
    
    lifecycle_state: str = ""
    execution_state: str = ""
    
    primary_exception_type: str = ""
    primary_exception_message: str = ""
    primary_exception_traceback: Optional[str] = None
    
    # Runtime-specific fields
    impact_scope: List[str] = field(default_factory=list)  # Affected entities
    recovery_strategy: "RuntimeRecoveryStrategy" = None  # Default set below
    alert_level: "AlertLevel" = None  # Default set below
    
    # Alerting config
    should_alert: bool = True
    alert_channels: List[str] = field(default_factory=list)  # e.g., ["email", "slack"]
    
    # Escalation
    escalation_path: Optional[str] = None  # e.g., "team-oncall"
    escalate_after_attempts: int = 3
    
    # Timing
    first_occurrence_utc: float = field(default_factory=time.time)
    latest_occurrence_utc: float = field(default_factory=time.time)
    occurrence_count: int = 1
    
    @property
    def duration_seconds(self) -> float:
        """Calculate time since first occurrence."""
        return time.time() - self.first_occurrence_utc
    
    @property
    def should_escalate(self) -> bool:
        """Check if failure should be escalated."""
        return self.occurrence_count >= self.escalate_after_attempts
    
    def with_impact_scope(self, scope: List[str]) -> "RuntimeFailure":
        """Return a copy with updated impact scope."""
        return RuntimeFailure(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            impact_scope=scope,
            recovery_strategy=self.recovery_strategy,
            alert_level=self.alert_level,
            should_alert=self.should_alert,
            alert_channels=list(self.alert_channels),
            escalation_path=self.escalation_path,
            escalate_after_attempts=self.escalate_after_attempts,
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1
        )
    
    def mark_alerted(self) -> "RuntimeFailure":
        """Return a copy with alert flag cleared (already sent)."""
        return RuntimeFailure(
            failure_id=self.failure_id,
            category=self.category,
            severity=self.severity,
            primary=self.primary,
            runtime_id=self.runtime_id,
            source_entity_id=self.source_entity_id,
            task_id=self.task_id,
            lifecycle_state=self.lifecycle_state,
            execution_state=self.execution_state,
            primary_exception_type=self.primary_exception_type,
            primary_exception_message=self.primary_exception_message,
            primary_exception_traceback=self.primary_exception_traceback,
            impact_scope=list(self.impact_scope),
            recovery_strategy=self.recovery_strategy,
            alert_level=self.alert_level,
            should_alert=False,
            alert_channels=list(self.alert_channels),
            escalation_path=self.escalation_path,
            escalate_after_attempts=self.escalate_after_attempts,
            first_occurrence_utc=self.first_occurrence_utc,
            latest_occurrence_utc=time.time(),
            occurrence_count=self.occurrence_count + 1
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "failure_id": self.failure_id,
            "category": self.category.value if hasattr(self.category, 'value') else str(self.category),
            "severity": self.severity,
            "primary": self.primary,
            "runtime_id": self.runtime_id,
            "source_entity_id": self.source_entity_id,
            "task_id": self.task_id,
            "lifecycle_state": self.lifecycle_state,
            "execution_state": self.execution_state,
            "primary_exception_type": self.primary_exception_type,
            "primary_exception_message": self.primary_exception_message,
            "impact_scope": self.impact_scope,
            "recovery_strategy": str(self.recovery_strategy) if hasattr(self.recovery_strategy, 'value') else self.recovery_strategy,
            "alert_level": str(self.alert_level) if hasattr(self.alert_level, 'value') else self.alert_level,
            "should_alert": self.should_alert,
            "alert_channels": self.alert_channels,
            "escalation_path": self.escalation_path,
            "occurrence_count": self.occurrence_count,
            "duration_seconds": self.duration_seconds
        }
    
    @classmethod
    def from_failure_record(
        cls,
        record: FailureRecord,
        runtime_id: Optional[str] = None,
        impact_scope: Optional[List[str]] = None,
        recovery_strategy: "RuntimeRecoveryStrategy" = None,
        alert_level: "AlertLevel" = None
    ) -> "RuntimeFailure":
        """
        Create a RuntimeFailure from a FailureRecord.
        
        Args:
            record: The base failure record
            runtime_id: Runtime instance identifier
            impact_scope: List of affected entity IDs
            recovery_strategy: How to recover automatically
            alert_level: Alert priority
            
        Returns:
            A new RuntimeFailure instance
        """
        return cls(
            failure_id=record.failure_id,
            category=record.category,
            severity=record.severity,
            primary=record.primary,
            runtime_id=runtime_id or record.runtime_id,
            source_entity_id=record.source_entity_id,
            task_id=record.task_id,
            lifecycle_state=record.lifecycle_state,
            execution_state=record.execution_state,
            primary_exception_type=record.primary_exception_type,
            primary_exception_message=record.primary_exception_message,
            primary_exception_traceback=record.primary_exception_traceback,
            impact_scope=impact_scope or [],
            recovery_strategy=recovery_strategy or RuntimeRecoveryStrategy.AUTOMATED_RETRY,
            alert_level=alert_level or AlertLevel.INFO,
            should_alert=True,
            alert_channels=["log"],
            escalation_path=None,
            escalate_after_attempts=3,
            first_occurrence_utc=record.first_occurrence_utc,
            latest_occurrence_utc=record.latest_occurrence_utc,
            occurrence_count=record.occurrence_count
        )


class RuntimeRecoveryStrategy(Enum):
    """
    Strategies for automatic recovery from runtime failures.
    
    - AUTOMATED_RETRY: Retry the operation automatically
    - RESTART_SERVICE: Restart the affected service
    - ISOLATE_ENTITY: Isolate from other entities temporarily
    - ESCALATE_ONLY: Only escalate, no automated action
    - DISABLE_FEATURE: Temporarily disable affected feature
    """
    
    AUTOMATED_RETRY = "automated_retry"
    RESTART_SERVICE = "restart_service"
    ISOLATE_ENTITY = "isolate_entity"
    ESCALATE_ONLY = "escalate_only"
    DISABLE_FEATURE = "disable_feature"


class AlertLevel(Enum):
    """
    Alert priority levels for runtime failures.
    
    - INFO: Informational, no immediate action needed
    - LOW: Notable event, monitor closely
    - MEDIUM: Requires attention, may need intervention
    - HIGH: Urgent, requires immediate response
    - CRITICAL: System impact, immediate escalation required
    """
    
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuntimeFailureDeduplicator:
    """
    Deduplicate runtime failures for reporting.
    
    Groups related failures and tracks:
        - Total occurrence count
        - First and latest occurrence times
        - Impact scope expansion
    
    Usage:
        dedup = RuntimeFailureDeduplicator()
        
        failure = RuntimeFailure(...)
        dedup.add(failure)
        
        # Get deduplicated failures
        reports = dedup.get_all()
    """
    
    def __init__(self) -> None:
        self._failures: Dict[str, RuntimeFailure] = {}
        self._lock = __import__("threading").Lock()
    
    def add(self, failure: RuntimeFailure) -> None:
        """Add or update a runtime failure."""
        key = f"{failure.category.value}|{failure.source_entity_id or ''}"
        
        with self._lock:
            if key in self._failures:
                existing = self._failures[key]
                
                # Update occurrence and expand impact scope
                new_impact = list(set(existing.impact_scope) | set(failure.impact_scope))
                
                self._failures[key] = RuntimeFailure(
                    failure_id=existing.failure_id,
                    category=failure.category,
                    severity=max(existing.severity, failure.severity),
                    primary=existing.primary,
                    runtime_id=existing.runtime_id,
                    source_entity_id=existing.source_entity_id,
                    task_id=failure.task_id or existing.task_id,
                    lifecycle_state=failure.lifecycle_state or existing.lifecycle_state,
                    execution_state=failure.execution_state or existing.execution_state,
                    primary_exception_type=existing.primary_exception_type,
                    primary_exception_message=existing.primary_exception_message,
                    primary_exception_traceback=existing.primary_exception_traceback,
                    impact_scope=new_impact,
                    recovery_strategy=failure.recovery_strategy or existing.recovery_strategy,
                    alert_level=max_alert_level(existing.alert_level, failure.alert_level),
                    should_alert=True,
                    alert_channels=list(set(existing.alert_channels) | set(failure.alert_channels)),
                    escalation_path=existing.escalation_path,
                    escalate_after_attempts=existing.escalate_after_attempts,
                    first_occurrence_utc=existing.first_occurrence_utc,
                    latest_occurrence_utc=time.time(),
                    occurrence_count=existing.occurrence_count + 1
                )
            else:
                self._failures[key] = failure
    
    def get(self, key: str) -> Optional[RuntimeFailure]:
        """Get a deduplicated failure by key."""
        return self._failures.get(key)
    
    def get_all(self) -> List[RuntimeFailure]:
        """Get all deduplicated failures."""
        with self._lock:
            return list(self._failures.values())
    
    def remove(self, key: str) -> None:
        """Remove a failure from the deduplicator."""
        with self._lock:
            if key in self._failures:
                del self._failures[key]
    
    def clear(self) -> None:
        """Clear all failures."""
        with self._lock:
            self._failures.clear()


def max_alert_level(a: Optional[AlertLevel], b: Optional[AlertLevel]) -> AlertLevel:
    """
    Return the higher alert level between two.
    
    Returns CRITICAL > HIGH > MEDIUM > LOW > INFO
    """
    if a is None:
        return b or AlertLevel.INFO
    if b is None:
        return a
    
    priority = {
        AlertLevel.CRITICAL: 5,
        AlertLevel.HIGH: 4,
        AlertLevel.MEDIUM: 3,
        AlertLevel.LOW: 2,
        AlertLevel.INFO: 1
    }
    
    return max(a, b, key=lambda x: priority.get(x, 0))


__all__ = [
    # Categories
    "FailureCategory",
    
    # Recoverability
    "Recoverability",
    
    # Records
    "FailureRecord",
    "RuntimeFailure",
    
    # Recovery strategies
    "RuntimeRecoveryStrategy",
    
    # Alerting
    "AlertLevel",
    
    # Deduplication
    "FailureDeduplicator",
    "RuntimeFailureDeduplicator",
]
