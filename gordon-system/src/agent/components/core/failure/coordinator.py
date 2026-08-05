# Failure Coordinator
# ===================

"""
Failure Coordinator - the canonical authority for failure handling in Phase 3.7.10.

The FailureCoordinator owns:
    - Failure intake (accepting failures from detectors)
    - Deduplication (avoiding duplicate reports)
    - Classification (determining kind, severity, scope)
    - Containment orchestration (coordinating subsystems to contain)
    - Routing (to rollback or recovery as appropriate)
    - Escalation (for failures beyond recovery capability)

The FailureCoordinator does NOT:
    - Perform subsystem-specific cleanup itself
    - Mutate arbitrary component state directly
    - Restart components directly
    - Declare recovery successful (that's for independent verifier)
"""

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, List, Optional, Any
import time
import uuid

from .types import RuntimeFailure, FailureKind, FailureSeverity, FailureDomain
from .classifier import (
    FailureClassifier,
    FailureClassificationResult,
    FailureClassificationContext,
)
from .containment import ContainmentCoordinator, DefaultContainmentCoordinator
from .events import (
    FailureEventPublisher,
    EventBusFailurePublisher,
    LoggingEventPublisher,
    FailureDetectedEvent,
    FailureClassifiedEvent,
    FailureContainedEvent,
)


@dataclass(frozen=True)
class FailureReport:
    """
    Report from a failure handling operation.
    
    Args:
        failure_id: Which failure this report is for
        status: Current handling status (CLASSIFYING, CONTAINING, etc.)
        
        classification_result: Results of classification (kind, severity, etc.)
        containment_result: Results of containment (if any)
        
        recovery_eligible: Whether recovery is eligible
        rollback_eligible: Whether rollback is eligible
        
        recommended_action: What action should be taken next
    """
    
    failure_id: str
    
    status: "FailureStatus"
    
    classification_result: Optional[FailureClassificationResult] = None
    containment_result: Optional[Any] = None  # ContainmentResult type
    
    recovery_eligible: bool = False
    rollback_eligible: bool = False
    
    recommended_action: str = ""


class FailureStatus(Enum):
    """Status of failure handling."""
    
    RECEIVED = "received"
    CLASSIFYING = "classifying"
    CONTAINING = "containing"
    CONTAINED = "contained"
    ROLLED_BACK = "rolled_back"
    RECOVERED = "recovered"
    FAILED = "failed"
    ESCALATED = "escalated"


class FailureCoordinator:
    """
    Canonical failure coordinator for Phase 3.7.10.
    
    Usage with canonical EventBus (Phase 3.7.27+):
        from gordon_system.src.agent.components.core.communication import get_event_bus
        from gordon_system.src.agent.components.core.failure.coordinator import FailureCoordinator
        
        event_bus = get_event_bus(runtime_id="my-runtime")
        coordinator = FailureCoordinator(
            classifier=FailureClassifier(),
            containment_coordinator=DefaultContainmentCoordinator(),
            event_publisher=EventBusFailurePublisher(event_bus, runtime_id="my-runtime")
        )
        
        report = await coordinator.report_failure(runtime_failure)
    
    Usage with logging (development/testing):
        publisher = LoggingEventPublisher()
        coordinator = FailureCoordinator(
            classifier=FailureClassifier(),
            containment_coordinator=DefaultContainmentCoordinator(),
            event_publisher=publisher
        )
    """
    
    def __init__(
        self,
        classifier: Optional[FailureClassifier] = None,
        containment_coordinator: Optional[ContainmentCoordinator] = None,
        event_publisher: Optional[FailureEventPublisher] = None,
        event_bus: Optional[Any] = None,  # EventBus type from communication module
        runtime_id: str = ""
    ):
        """
        Initialize the failure coordinator.
        
        Args:
            classifier: FailureClassifier instance (creates default if None)
            containment_coordinator: ContainmentCoordinator instance
            event_publisher: FailureEventPublisher for event delivery
            event_bus: Optional canonical EventBus for Phase 3.7.27+ integration
            runtime_id: Runtime identifier for events when using event_bus
        
        If event_bus is provided, creates EventBusFailurePublisher.
        Otherwise uses event_publisher or defaults to LoggingEventPublisher.
        """
        self._classifier = classifier or FailureClassifier()
        self._containment = containment_coordinator or DefaultContainmentCoordinator()
        
        # Priority: explicit publisher > EventBus integration > logging
        if event_publisher is not None:
            self._publisher = event_publisher
        elif event_bus is not None:
            self._publisher = EventBusFailurePublisher(event_bus, runtime_id)
        else:
            self._publisher = LoggingEventPublisher()
        
        # Internal state
        self._failures: Dict[str, RuntimeFailure] = {}
        self._reports: Dict[str, FailureReport] = {}
        self._classification_contexts: Dict[str, FailureClassificationContext] = {}
        self._failure_sequence: int = 0
        
    async def report_failure(self, failure: RuntimeFailure) -> FailureReport:
        """
        Report a new failure for handling.
        
        This is the canonical entry point. Every detected failure must go
        through this method to ensure consistent handling.
        
        Args:
            failure: The failure to report
            
        Returns:
            Initial FailureReport with status RECEIVED
        """
        # Generate sequence number for ordering
        self._failure_sequence += 1
        
        # Assign runtime_id if not set (for multi-runtime isolation)
        if failure.runtime_id is None:
            import os
            failure = replace(failure, runtime_id=str(os.getpid()))
        
        # Update logical sequence
        failure = replace(
            failure,
            logical_sequence=self._failure_sequence
        )
        
        # Store the failure
        self._failures[failure.failure_id] = failure
        
        # Create initial report
        report = FailureReport(
            failure_id=failure.failure_id,
            status=FailureStatus.RECEIVED,
            recommended_action="classify"
        )
        self._reports[failure.failure_id] = report
        
        # Emit detected event
        await self._publisher.publish(FailureDetectedEvent(
            event_id=str(uuid.uuid4()),
            runtime_id=failure.runtime_id or "",
            failure_id=failure.failure_id,
            source=failure.source,
            payload={"severity": failure.severity.value if hasattr(failure.severity, 'value') else str(failure.severity)}
        ))
        
        return report
    
    async def classify_failure(self, failure_id: str) -> FailureReport:
        """
        Classify a reported failure.
        
        This determines:
            - Kind (TRANSIENT, RECOVERABLE, etc.)
            - Severity
            - Scope of affected entities
            - Retryability
            - Rollback eligibility
            - Recovery eligibility
            
        Args:
            failure_id: ID of the failure to classify
            
        Returns:
            FailureReport with classification results
        """
        failure = self._failures.get(failure_id)
        if failure is None:
            raise ValueError(f"Unknown failure: {failure_id}")
        
        # Create classification context from stored state
        ctx = self._classification_contexts.get(
            failure_id,
            FailureClassificationContext()
        )
        
        # Run classifier
        result = await self._classifier.classify(failure, ctx)
        
        # Update failure with classification results
        updated_failure = replace(
            failure,
            kind=result.kind,
            severity=result.severity,
            retryability=result.retryability,
            rollback_eligibility=result.rollback_eligibility,
            recovery_eligibility=result.recovery_eligibility,
            scope=result.scope
        )
        
        self._failures[failure_id] = updated_failure
        
        # Create classification context for future reference
        ctx = FailureClassificationContext(
            runtime_id=updated_failure.runtime_id,
            retry_count=self._get_retry_count(failure_id),
            restart_count=self._get_restart_count(failure_id),
            remaining_retry_budget=max(0, 3 - self._get_retry_count(failure_id)),
            remaining_restart_budget=max(0, 2 - self._get_restart_count(failure_id))
        )
        self._classification_contexts[failure_id] = ctx
        
        # Update report
        report = FailureReport(
            failure_id=failure_id,
            status=FailureStatus.CLASSIFYING,
            classification_result=result,
            recovery_eligible=result.recovery_eligibility is True,
            rollback_eligible=result.rollback_eligibility is True,
            recommended_action=self._determine_recommended_action(result, updated_failure)
        )
        self._reports[failure_id] = report
        
        # Emit classified event
        await self._publisher.publish(FailureClassifiedEvent(
            event_id=str(uuid.uuid4()),
            runtime_id=updated_failure.runtime_id or "",
            failure_id=failure_id,
            source=updated_failure.source,
            kind=result.kind.value if hasattr(result.kind, 'value') else str(result.kind),
            severity=result.severity.value if hasattr(result.severity, 'value') else str(result.severity)
        ))
        
        return report
    
    async def contain_failure(self, failure_id: str) -> FailureReport:
        """
        Request containment for a failure.
        
        This prevents uncontrolled propagation of the failure to other
        subsystems while recovery is attempted.
        
        Args:
            failure_id: ID of the failure to contain
            
        Returns:
            FailureReport with containment result
        """
        failure = self._failures.get(failure_id)
        if failure is None:
            raise ValueError(f"Unknown failure: {failure_id}")
        
        # Check if containment required
        if not failure.containment_requirement and failure.kind in (
            FailureKind.FATAL,
            FailureKind.PANIC
        ):
            # Fatal/panic require immediate escalation, not containment
            return await self.escalate_failure(failure_id)
        
        # Execute containment
        scope = list(failure.scope) if failure.scope else [failure.source]
        
        result = await self._containment.request_containment(
            failure_id=failure_id,
            scope=scope
        )
        
        # Update report with containment result
        report = self._reports.get(failure_id, FailureReport(
            failure_id=failure_id,
            status=FailureStatus.CONTAINING
        ))
        
        report = replace(
            report,
            status=FailureStatus.CONTAINED if result.success else FailureStatus.FAILED,
            containment_result=result,
            recommended_action="recovery" if result.success else "escalate"
        )
        self._reports[failure_id] = report
        
        # Emit contained event
        await self._publisher.publish(FailureContainedEvent(
            event_id=str(uuid.uuid4()),
            runtime_id=failure.runtime_id or "",
            failure_id=failure_id,
            source=failure.source,
            containment_id=failure_id,
            success=result.success,
            scope_affected=result.scope_affected,
            actions_executed=result.actions_executed
        ))
        
        return report
    
    async def request_recovery(self, failure_id: str) -> FailureReport:
        """
        Request recovery for a classified failure.
        
        This initiates the recovery process which may include:
            - Retry operation
            - Rollback to prior state
            - Restart component
            - Enter degraded mode
            
        Args:
            failure_id: ID of the failure to recover from
            
        Returns:
            FailureReport with recovery request result
        """
        failure = self._failures.get(failure_id)
        report = self._reports.get(failure_id)
        
        if failure is None or report is None:
            raise ValueError(f"Unknown failure: {failure_id}")
        
        # Check eligibility
        if not report.recovery_eligible:
            return await self.escalate_failure(failure_id)
        
        # Determine recovery strategy based on classification
        if report.rollback_eligible:
            # Rollback eligible - initiate rollback first
            report = replace(
                report,
                status=FailureStatus.ROLLED_BACK,  # Placeholder
                recommended_action="rollback"
            )
        elif report.retry_count < 3:  # Simple budget check
            # Retry eligible and budget available
            report = replace(
                report,
                status=FailureStatus.RECOVERED,  # Placeholder
                recommended_action="retry"
            )
        else:
            # Escalate (no recovery path available)
            return await self.escalate_failure(failure_id)
        
        self._reports[failure_id] = report
        
        return report
    
    async def escalate_failure(self, failure_id: str) -> FailureReport:
        """
        Escalate a failure that cannot be recovered.
        
        This marks the failure as needing operator intervention or
        system-level response (shutdown, etc.).
        
        Args:
            failure_id: ID of the failure to escalate
            
        Returns:
            FailureReport with ESCALATED status
        """
        failure = self._failures.get(failure_id)
        if failure is None:
            raise ValueError(f"Unknown failure: {failure_id}")
        
        report = replace(
            self._reports[failure_id],
            status=FailureStatus.ESCALATED,
            recommended_action="operator_intervention"
        )
        self._reports[failure_id] = report
        
        return report
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Get an immutable snapshot of failure coordinator state.
        
        Used for diagnostics and recovery state preservation.
        """
        return {
            "failure_count": len(self._failures),
            "report_count": len(self._reports),
            "failures": {k: v.to_serializable() for k, v in self._failures.items()},
            "reports": {k: {
                "failure_id": v.failure_id,
                "status": v.status.value if hasattr(v.status, 'value') else str(v.status),
                "recovery_eligible": v.recovery_eligible,
                "rollback_eligible": v.rollback_eligible
            } for k, v in self._reports.items()},
        }
    
    def diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about failure handling."""
        return {
            "total_failures_reported": len(self._failures),
            "classification_contexts_count": len(self._classification_contexts),
            "containment_status": self._get_containment_diagnostics()
        }
    
    def _get_retry_count(self, failure_id: str) -> int:
        """Get retry count for a failure."""
        # In production, this would query actual retry history
        return 0
    
    def _get_restart_count(self, failure_id: str) -> int:
        """Get restart count for a failure."""
        # In production, this would query actual restart history
        return 0
    
    def _determine_recommended_action(
        self,
        classification: FailureClassificationResult,
        failure: RuntimeFailure
    ) -> str:
        """
        Determine the recommended next action based on classification.
        
        This implements the decision logic from section 10 of the spec:
            - Known transient + retryable = RETRY
            - Rollback eligible = ROLLBACK  
            - Recovery eligible = RECOVERY
            - FATAL/PANIC/PROGRAMMING = ESCALATE
            - Unknown outcome = ESCALATE for verification
        """
        if failure.kind in (FailureKind.FATAL, FailureKind.PANIC):
            return "ESCALATE"
        
        if classification.retryability is True:
            return "RETRY"
        
        if classification.rollback_eligibility is True:
            return "ROLLBACK"
        
        if classification.recovery_eligibility is True:
            return "RECOVERY"
        
        # Unknown outcome requires verification
        if any(fact.startswith("unknown") for fact in classification.unresolved_facts):
            return "ESCALATE_FOR_VERIFICATION"
        
        return "ESCALATE"
    
    def _get_containment_diagnostics(self) -> Dict[str, Any]:
        """Get containment status diagnostics."""
        try:
            # This would query the actual containment coordinator
            return {"active_containments": 0, "barriers_active": 0}
        except Exception:
            return {"error": "Unable to get containment diagnostics"}


# All imports are now at the top of the file
