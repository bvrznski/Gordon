# Core Observability Governance Layer
# ====================================

"""
Observability governance, orchestration, and runtime integration.

This module provides:
- Telemetry policy enforcement
- Runtime lifecycle integration
- Telemetry orchestration
- Observability governance framework
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum, auto
import time
import uuid
import threading


# =============================================================================
# TELEMETRY POLICY
# =============================================================================

class PolicyScope(Enum):
    """Scopes for telemetry policies."""
    
    GLOBAL = "global"          # Apply to all runtime
    SERVICE = "service"        # Per-service scope
    COMPONENT = "component"    # Specific component
    RUNTIME = "runtime"        # Runtime-scoped only


@dataclass(frozen=True)
class TelemetryPolicy:
    """
    A telemetry policy definition.
    
    Specifies rules for sampling, retention, export, and other behaviors.
    """
    
    # Required fields (no defaults) - must come first
    name: str  # Human-readable policy name
    description: str  # Policy description
    scope: PolicyScope  # Scope of this policy
    
    # Optional fields with defaults - must come after required fields
    policy_id: str = field(default_factory=lambda: f"policy_{uuid.uuid4().hex[:8]}")  # Policy identifier
    scope_id: Optional[str] = None  # Service or component ID if scoped
    sample_rate: float = 1.0  # 0.0 - 1.0
    sampling_strategy: str = "probabilistic"  # always, never, probabilistic
    retention_seconds: int = 3600  # Default 1 hour
    export_enabled: bool = True
    export_format: str = "json"
    min_severity: str = "TRACE"  # TRACE, DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL
    
    @property
    def is_active(self) -> bool:
        """Check if this policy is currently active."""
        return self.sample_rate > 0 and self.export_enabled


# =============================================================================
# GOVERNANCE ENFORCEMENT
# =============================================================================

class GovernanceRule(ABC):
    """Abstract base class for governance rules."""
    
    @abstractmethod
    def check(self, event: Dict[str, Any]) -> bool:
        """
        Check if an event complies with the rule.
        
        Args:
            event: Event to check
            
        Returns:
            True if compliant, False otherwise
        """
        ...
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Get rule identifier."""
        ...


class SamplingRule(GovernanceRule):
    """Rule for sampling decisions."""
    
    def __init__(
        self,
        policy: TelemetryPolicy,
        runtime_state: "RuntimeObservabilityState",
    ) -> None:
        self._policy = policy
        self._runtime_state = runtime_state
    
    def check(self, event: Dict[str, Any]) -> bool:
        """Check if the event should be sampled."""
        import random
        
        # Always sample CRITICAL events
        severity = event.get("severity", "INFO")
        if severity in ("CRITICAL", "FATAL"):
            return True
        
        # Apply policy sampling rate
        if self._policy.sampling_strategy == "probabilistic":
            return random.random() < self._policy.sample_rate
        
        if self._policy.sampling_strategy == "always":
            return True
        
        return False
    
    @property
    def rule_id(self) -> str:
        """Get rule identifier."""
        return f"sampling:{self._policy.policy_id}"


class RetentionRule(GovernanceRule):
    """Rule for data retention."""
    
    def __init__(self, max_age_seconds: int = 3600) -> None:
        self._max_age = max_age_seconds
    
    def check(self, event: Dict[str, Any]) -> bool:
        """Check if event is within retention window."""
        timestamp = event.get("timestamp_utc", 0)
        age = time.time() - timestamp
        return age <= self._max_age
    
    @property
    def rule_id(self) -> str:
        """Get rule identifier."""
        return "retention:age_check"


# =============================================================================
# RUNTIME OBSERVABILITY STATE
# =============================================================================

class RuntimeObservabilityState:
    """
    State container for observability across runtime lifecycle.
    
    Tracks active sessions, policies, and configuration.
    """
    
    def __init__(
        self,
        runtime_id: str,
    ) -> None:
        self._runtime_id = runtime_id
        
        # Active telemetry policies
        self._policies: Dict[str, TelemetryPolicy] = {}
        
        # Runtime lifecycle state
        self._lifecycle_state: Optional[str] = None
        
        # Statistics
        self._total_events_emitted = 0
        self._total_events_dropped = 0
        
        # Lock for thread safety
        self._lock = threading.RLock()
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def set_lifecycle_state(self, state: str) -> None:
        """Update the runtime lifecycle state."""
        with self._lock:
            old_state = self._lifecycle_state
            self._lifecycle_state = state
            
            # Emit lifecycle event (this is observability tracking)
    
    def get_lifecycle_state(self) -> Optional[str]:
        """Get current runtime lifecycle state."""
        return self._lifecycle_state
    
    def register_policy(self, policy: TelemetryPolicy) -> "RuntimeObservabilityState":
        """Register a telemetry policy."""
        with self._lock:
            self._policies[policy.policy_id] = policy
        return self
    
    def unregister_policy(self, policy_id: str) -> "RuntimeObservabilityState":
        """Unregister a telemetry policy."""
        with self._lock:
            self._policies.pop(policy_id, None)
        return self
    
    def get_active_policies(self) -> List[TelemetryPolicy]:
        """Get all active policies."""
        with self._lock:
            return list(self._policies.values())
    
    def record_event(
        self,
        emitted: bool = True,
        dropped_reason: Optional[str] = None,
    ) -> None:
        """Record an event emission or drop."""
        with self._lock:
            if emitted:
                self._total_events_emitted += 1
            else:
                self._total_events_dropped += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get observability statistics."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "lifecycle_state": self._lifecycle_state,
                "policies_count": len(self._policies),
                "events_emitted_total": self._total_events_emitted,
                "events_dropped_total": self._total_events_dropped,
            }


# =============================================================================
# TELEMETRY ORCHESTRATOR
# =============================================================================

class TelemetryOrchestrator:
    """
    Orchestrates telemetry collection across the runtime.
    
    Coordinates logging, metrics, tracing, and analytics with proper
    lifecycle management and policy enforcement.
    """
    
    def __init__(
        self,
        runtime_id: Optional[str] = None,
    ) -> None:
        import uuid
        
        self._runtime_id = runtime_id or str(uuid.uuid4())
        self._state = RuntimeObservabilityState(self._runtime_id)
        
        # Components
        self._logging_manager: Any = None  # Will be set during integration
        self._metrics_manager: Any = None
        self._tracing_manager: Any = None
        self._analytics_pipeline: Any = None
        
        # Orchestration state
        self._is_running = False
        self._shutdown_requested = False
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime identifier."""
        return self._runtime_id
    
    def set_logging_manager(self, manager: Any) -> "TelemetryOrchestrator":
        """Set the logging manager for integration."""
        self._logging_manager = manager
        return self
    
    def set_metrics_manager(self, manager: Any) -> "TelemetryOrchestrator":
        """Set the metrics manager for integration."""
        self._metrics_manager = manager
        return self
    
    def set_tracing_manager(self, manager: Any) -> "TelemetryOrchestrator":
        """Set the tracing manager for integration."""
        self._tracing_manager = manager
        return self
    
    def set_analytics_pipeline(self, pipeline: Any) -> "TelemetryOrchestrator":
        """Set the analytics pipeline for integration."""
        self._analytics_pipeline = pipeline
        return self
    
    def start(self) -> None:
        """Start telemetry orchestration."""
        self._is_running = True
        self._state.set_lifecycle_state("STARTED")
    
    def stop(self) -> None:
        """Stop telemetry orchestration and flush data."""
        self._shutdown_requested = True
        
        # Flush any pending telemetry
        if self._logging_manager:
            pass  # Would call flush() on manager
        
        self._is_running = False
        self._state.set_lifecycle_state("STOPPED")
    
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._is_running
    
    def emit_log(
        self,
        level: str,
        message: str,
        **context
    ) -> None:
        """
        Emit a log through the orchestration layer.
        
        Applies policies before emitting.
        """
        if not self._is_running:
            return
        
        event = {
            "level": level,
            "message": message,
            "timestamp_utc": time.time(),
            **context
        }
        
        # Check policy
        if not self._apply_policies(event):
            self._state.record_event(emitted=False, dropped_reason="policy")
            return
        
        # Emit to logging manager
        if self._logging_manager:
            pass  # Would call the appropriate method
    
    def _apply_policies(self, event: Dict[str, Any]) -> bool:
        """
        Apply governance policies to an event.
        
        Args:
            event: Event to evaluate
            
        Returns:
            True if event passes all policy checks
        """
        for policy in self._state.get_active_policies():
            # Check sampling
            import random
            if policy.sampling_strategy == "probabilistic":
                if random.random() >= policy.sample_rate:
                    return False
        
        return True


# =============================================================================
# OBSERVABILITY LIFECYCLE HOOKS
# =============================================================================

class LifecycleEvent(Enum):
    """Events in the observability lifecycle."""
    
    INITIALIZED = "initialized"         # System initialized
    STARTED = "started"                 # Runtime started
    STOPPING = "stopping"               # Shutdown initiated
    STOPPED = "stopped"                 # All systems stopped


class ObservabilityLifecycleHooks:
    """
    Hooks for observability lifecycle events.
    
    Allows components to register callbacks for lifecycle transitions.
    """
    
    def __init__(self) -> None:
        self._callbacks: Dict[LifecycleEvent, List[Callable]] = {}
        self._lock = threading.RLock()
    
    def register(
        self,
        event: LifecycleEvent,
        callback: Callable[[Dict[str, Any]], None],
    ) -> "ObservabilityLifecycleHooks":
        """Register a lifecycle hook."""
        with self._lock:
            if event not in self._callbacks:
                self._callbacks[event] = []
            
            self._callbacks[event].append(callback)
        
        return self
    
    def emit(self, event: LifecycleEvent, context: Dict[str, Any]) -> None:
        """Emit a lifecycle event to all registered hooks."""
        with self._lock:
            callbacks = list(self._callbacks.get(event, []))
        
        for callback in callbacks:
            try:
                callback(context)
            except Exception:
                # Don't let one hook failure affect others
                continue


# =============================================================================
# OBSERVABILITY GOVERNANCE ENGINE
# =============================================================================

class ObservabilityGovernanceEngine:
    """
    Core governance engine for observability.
    
    Enforces policies, tracks violations, and generates compliance reports.
    """
    
    def __init__(
        self,
        runtime_id: str,
    ) -> None:
        self._runtime_id = runtime_id
        
        # Registered policies
        self._policies: Dict[str, TelemetryPolicy] = {}
        
        # Policy violations
        self._violations: List[Dict[str, Any]] = []
        
        # Statistics
        self._total_policy_evaluations = 0
    
    def register_policy(self, policy: TelemetryPolicy) -> None:
        """Register a new telemetry policy."""
        self._policies[policy.policy_id] = policy
    
    def unregister_policy(self, policy_id: str) -> None:
        """Unregister a policy."""
        self._policies.pop(policy_id, None)
    
    def evaluate_event(
        self,
        event: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate an event against all policies.
        
        Args:
            event: Event to evaluate
            
        Returns:
            Evaluation result with policy decisions
        """
        self._total_policy_evaluations += 1
        
        results = {
            "policy_id": None,
            "compliant": True,
            "reason": None,
        }
        
        for policy in self._policies.values():
            # Check sampling
            import random
            if policy.sampling_strategy == "probabilistic":
                if random.random() >= policy.sample_rate:
                    results["policy_id"] = policy.policy_id
                    results["compliant"] = False
                    results["reason"] = f"sampled_out (rate={policy.sample_rate})"
                    self._record_violation(event, policy, results)
                    break
        
        return results
    
    def _record_violation(
        self,
        event: Dict[str, Any],
        policy: TelemetryPolicy,
        result: Dict[str, Any],
    ) -> None:
        """Record a policy violation."""
        self._violations.append({
            "timestamp_utc": time.time(),
            "event_hash": hash(str(event)),
            "policy_id": policy.policy_id,
            "violation_type": result.get("reason", "unknown"),
        })
    
    def get_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violations."""
        return self._violations[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get governance statistics."""
        return {
            "runtime_id": self._runtime_id,
            "policies_count": len(self._policies),
            "total_evaluations": self._total_policy_evaluations,
            "violation_count": len(self._violations),
        }


__all__ = [
    # Policies
    "PolicyScope",
    "TelemetryPolicy",
    
    # Governance rules
    "GovernanceRule",
    "SamplingRule",
    "RetentionRule",
    
    # State and orchestration
    "RuntimeObservabilityState",
    "TelemetryOrchestrator",
    
    # Lifecycle hooks
    "LifecycleEvent",
    "ObservabilityLifecycleHooks",
    
    # Governance engine
    "ObservabilityGovernanceEngine",
]