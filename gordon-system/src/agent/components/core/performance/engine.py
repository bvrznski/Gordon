# Performance Policy Engine
# =========================

"""
Performance policy evaluation engine for Gordon runtime Phase 3.7.18-I.

This module provides the canonical performance-policy authority:

CANONICAL AUTHORITY:
    - PerformancePolicyEngine: Evaluates policies and produces decisions
    
The engine evaluates policies against current measurements and produces
immutable decisions that are then enforced by other authorities (ResourceManager,
AdmissionController, Scheduler).

PRINCIPLES:
    - Decisions are immutable artifacts, not side-effecting operations
    - No policy can bypass canonical Core authorities
    - All bounds are explicit and enforceable
    - Deterministic evaluation for reproducibility

Usage:
    from gordon.components.core.performance import PerformanceManager
    from gordon.components.core.performance.engine import PerformancePolicyEngine
    
    manager = PerformanceManager(runtime_id="runtime_1")
    engine = PerformancePolicyEngine(runtime_id=manager.runtime_id)
    
    # Evaluate policies and get decisions
    decision = engine.evaluate_overload(
        measurements=measurements,
        budgets=budgets,
        capacity=capacity
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# DECISION TYPES
# =============================================================================

class PolicyDecisionType(Enum):
    """Types of decisions the policy engine can produce."""
    OVERLOAD_DETECTED = "overload_detected"           # Overload state detected
    LOAD_SHEDDING_RECOMMENDED = "load_shedding_recommended"
    BACKPRESSURE_APPLY = "backpressure_apply"
    SCALE_OUT_RECOMMENDED = "scale_out_recommended"
    SCALE_IN_RECOMMENDED = "scale_in_recommended"
    DEGRADATION_ENTER = "degradation_enter"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    LATENCY_BUDGET_EXCEEDED = "latency_budget_exceeded"
    THROUGHPUT_TARGET_MISSED = "throughput_target_missed"
    NO_ACTION_NEEDED = "no_action_needed"


# =============================================================================
# POLICY DECISION ARTIFACTS
# =============================================================================

@dataclass(frozen=True)
class PolicyDecision:
    """
    Immutable decision produced by policy evaluation.
    
    This is the OUTPUT of policy evaluation - an immutable record that says:
    "Given current measurements and policies, I recommend [action]."
    
    Other authorities (ResourceManager, AdmissionController, Scheduler) 
    receive this decision and decide how to enforce it.
    """
    
    decision_id: str
    runtime_id: str
    
    # Decision metadata
    decision_type: PolicyDecisionType
    timestamp_utc: float = field(default_factory=time.time)
    
    # Context
    evaluation_window_start_utc: float
    evaluation_window_end_utc: float
    measurement_count: int = 0
    
    # Recommended action(s)
    recommended_actions: Tuple[str, ...] = field(default_factory=tuple)
    
    # Severity/urgency
    severity: str = "info"  # info, warning, critical, emergency
    
    # Evidence for the decision
    evidence: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def should_execute(self) -> bool:
        """Check if this decision requires action (non-info level)."""
        return self.severity != "info"


@dataclass(frozen=True)
class OverloadDecision:
    """Decision about overload state."""
    decision_id: str
    runtime_id: str
    
    current_state: str  # NORMAL, BUSY, SATURATED, OVERLOADED, CRITICAL
    recommended_state: Optional[str] = None  # State to transition to
    
    triggers: Tuple[str, ...] = field(default_factory=tuple)
    
    actions: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class BackpressureDecision:
    """Decision about backpressure application."""
    decision_id: str
    runtime_id: str
    
    domain: str
    current_level: str  # NONE, LOW, MODERATE, HIGH, CRITICAL, SATURATED
    recommended_level: str
    
    threshold_percent: float
    utilization_percent: float
    
    actions: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class LoadSheddingDecision:
    """Decision about load shedding."""
    decision_id: str
    runtime_id: str
    
    work_classes_eligible: Tuple[str, ...]
    
    selected_for_shedding: Tuple[str, ...] = field(default_factory=tuple)
    
    reason: str
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ScalingDecision:
    """Decision about scaling resources."""
    decision_id: str
    runtime_id: str
    
    action: str  # scale_out, scale_in, noop
    current_capacity: int
    target_capacity: int
    
    reason: str
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# PERFORMANCE POLICY ENGINE (CANONICAL AUTHORITY)
# =============================================================================

class PerformancePolicyEngine:
    """
    Canonical performance-policy evaluation authority.
    
    This is THE ONE source of policy decisions. It evaluates all policies
    against current measurements and produces immutable decision artifacts.
    
    What it does NOT do:
        - Does not directly resize pools or shed work
        - Does not modify runtime state
        - Does not schedule tasks
        
    What it DOES own:
        - Policy definitions (evaluation rules, thresholds)
        - Decision production (immutable artifacts)
        - Evidence tracking for decisions
        - Audit trail of policy evaluations
    
    Usage:
        engine = PerformancePolicyEngine(runtime_id="runtime_1")
        
        # Evaluate policies
        decision = engine.evaluate_overload(
            measurements=measurements,
            budgets=budgets,
            capacity=capacity,
            objectives=objectives
        )
        
        # Other authorities receive and act on the decision
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the policy engine.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Policy storage (immutable once set)
        self._backpressure_policies: Dict[str, "BackpressurePolicy"] = {}
        self._autoscaling_policies: Dict[str, "AutoscalingPolicy"] = {}
        self._load_shedding_policies: Dict[str, "LoadSheddingPolicy"] = {}
        self._batching_policies: Dict[str, "BatchingPolicy"] = {}
        
        # History of decisions (bounded)
        self._decision_history: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this engine serves."""
        return self._runtime_id
    
    # -------------------------------------------------------------------------
    # Policy Registration (for configuration)
    # -------------------------------------------------------------------------
    
    def register_backpressure_policy(
        self,
        domain: str,
        policy: "BackpressurePolicy"
    ) -> None:
        """Register a backpressure policy for a domain."""
        with self._lock:
            self._backpressure_policies[domain] = policy
            self._record_event("backpressure_policy_registered", {
                "domain": domain,
                "policy_id": policy.policy_id,
            })
    
    def register_autoscaling_policy(
        self,
        scope: str,
        policy: "AutoscalingPolicy"
    ) -> None:
        """Register an autoscaling policy for a scope."""
        with self._lock:
            self._autoscaling_policies[scope] = policy
            self._record_event("autoscaling_policy_registered", {
                "scope": scope,
                "policy_id": policy.policy_id,
            })
    
    def register_load_shedding_policy(
        self,
        domain: str,
        policy: "LoadSheddingPolicy"
    ) -> None:
        """Register a load shedding policy for a domain."""
        with self._lock:
            self._load_shedding_policies[domain] = policy
            self._record_event("load_shedding_policy_registered", {
                "domain": domain,
                "policy_id": policy.policy_id,
            })
    
    def register_batching_policy(
        self,
        domain: str,
        policy: "BatchingPolicy"
    ) -> None:
        """Register a batching policy for a domain."""
        with self._lock:
            self._batching_policies[domain] = policy
            self._record_event("batching_policy_registered", {
                "domain": domain,
                "policy_id": policy.policy_id,
            })
    
    # -------------------------------------------------------------------------
    # Policy Evaluation Methods
    # -------------------------------------------------------------------------
    
    def evaluate_overload(
        self,
        measurements: Dict[str, float],
        budgets: Optional[Dict[str, Any]] = None,
        capacity: Optional[Dict[str, Any]] = None,
        objectives: Optional[Dict[str, Any]] = None,
    ) -> OverloadDecision:
        """
        Evaluate all overload policies and produce a decision.
        
        Args:
            measurements: Current measurements (utilization percentages, etc.)
            budgets: Budget consumption states
            capacity: Capacity limits
            objectives: Performance objectives
            
        Returns:
            Decision with recommended state and actions
        """
        with self._lock:
            # Default to NORMAL if no data
            current_state = "NORMAL"
            
            # Check measurements for overload triggers
            triggers = []
            
            # Check CPU/memory/network utilization
            if measurements.get("cpu_utilization_percent", 0) > 95:
                triggers.append("cpu_saturation")
                current_state = "CRITICAL"
            elif measurements.get("cpu_utilization_percent", 0) > 85:
                triggers.append("high_cpu_utilization")
                current_state = "OVERLOADED"
            
            if measurements.get("memory_utilization_percent", 0) > 95:
                triggers.append("memory_pressure")
                current_state = max(current_state, "CRITICAL", key=lambda x: 
                    ["NORMAL", "BUSY", "SATURATED", "OVERLOADED", "CRITICAL"].index(x))
            elif measurements.get("memory_utilization_percent", 0) > 85:
                triggers.append("high_memory_utilization")
                current_state = max(current_state, "OVERLOADED", key=lambda x: 
                    ["NORMAL", "BUSY", "SATURATED", "OVERLOADED", "CRITICAL"].index(x))
            
            # Check budgets
            if budgets:
                for budget_id, budget in budgets.items():
                    status = getattr(budget, 'get_status', None)
                    if status and status() == "exceeded":
                        triggers.append(f"budget_exceeded:{budget_id}")
                        current_state = max(current_state, "OVERLOADED", key=lambda x: 
                            ["NORMAL", "BUSY", "SATURATED", "OVERLOADED", "CRITICAL"].index(x))
            
            # Check capacity
            if capacity:
                for domain, cap_info in capacity.items():
                    utilization = cap_info.get("utilization_percent", 0)
                    if utilization > 95:
                        triggers.append(f"capacity_exceeded:{domain}")
                        current_state = max(current_state, "CRITICAL", key=lambda x: 
                            ["NORMAL", "BUSY", "SATURATED", "OVERLOADED", "CRITICAL"].index(x))
            
            # Build actions based on state
            if current_state == "CRITICAL":
                actions = ("reduce_concurrency", "reject_retryable", "activate_backup_systems")
            elif current_state == "OVERLOADED":
                actions = ("reduce_batch_size", "throttle_background_work", "propagate_backpressure")
            elif current_state == "SATURATED":
                actions = ("reduce_concurrency", "apply_backpressure", "scale_out_recommendation")
            else:
                actions = tuple()
            
            decision_id = f"ol_dec_{uuid.uuid4().hex[:12]}"
            
            self._record_decision(decision_id, {
                "type": "overload",
                "state": current_state,
                "triggers": triggers,
                "actions": actions,
            })
            
            return OverloadDecision(
                decision_id=decision_id,
                runtime_id=self._runtime_id,
                current_state=current_state,
                recommended_state="NORMAL" if not triggers else None,
                triggers=tuple(triggers),
                actions=tuple(actions),
            )
    
    def evaluate_backpressure(
        self,
        domain: str,
        utilization_percent: float,
        queue_depth: Optional[int] = None,
        queue_capacity: Optional[int] = None,
    ) -> BackpressureDecision:
        """
        Evaluate backpressure policy for a specific domain.
        
        Args:
            domain: The domain to evaluate (e.g., "task_queue", "model_inference")
            utilization_percent: Current utilization percentage
            queue_depth: Current queue occupancy (if applicable)
            queue_capacity: Queue capacity limit (if applicable)
            
        Returns:
            Decision with recommended backpressure level and actions
        """
        with self._lock:
            policy = self._backpressure_policies.get(domain)
            
            if not policy:
                # Use default thresholds if no specific policy
                moderate_threshold = 70.0
                high_threshold = 85.0
                critical_threshold = 95.0
            else:
                moderate_threshold = policy.moderate_threshold_percent
                high_threshold = policy.high_threshold_percent
                critical_threshold = policy.critical_threshold_percent
            
            # Determine recommended level
            if utilization_percent >= critical_threshold:
                recommended_level = "SATURATED"
                actions = ("reject_new_work", "propagate_upstream")
            elif utilization_percent >= high_threshold:
                recommended_level = "CRITICAL"
                actions = policy.critical_actions if policy else ("reduce_concurrency",)
            elif utilization_percent >= moderate_threshold:
                recommended_level = "MODERATE"
                actions = policy.moderate_actions if policy else ("throttle",)
            else:
                recommended_level = "NONE"
                actions = tuple()
            
            decision_id = f"bp_dec_{uuid.uuid4().hex[:12]}"
            
            self._record_decision(decision_id, {
                "type": "backpressure",
                "domain": domain,
                "current_utilization": utilization_percent,
                "recommended_level": recommended_level,
                "actions": actions,
            })
            
            return BackpressureDecision(
                decision_id=decision_id,
                runtime_id=self._runtime_id,
                domain=domain,
                current_level="NONE" if utilization_percent < moderate_threshold else (
                    "MODERATE" if utilization_percent < high_threshold else (
                        "CRITICAL" if utilization_percent < critical_threshold else "SATURATED"
                    )
                ),
                recommended_level=recommended_level,
                threshold_percent=moderate_threshold,
                utilization_percent=utilization_percent,
                actions=tuple(actions),
            )
    
    def evaluate_scale_decision(
        self,
        scope: str,
        current_capacity: int,
        utilization_percent: float,
        demand_forecast: Optional[float] = None,
    ) -> ScalingDecision:
        """
        Evaluate autoscaling policy and produce a scaling decision.
        
        Args:
            scope: The scope to scale (e.g., "worker_pool", "runtime")
            current_capacity: Current number of workers/instances
            utilization_percent: Current utilization percentage
            demand_forecast: Forecasted demand (if available)
            
        Returns:
            Scaling decision with recommended action
        """
        with self._lock:
            policy = self._autoscaling_policies.get(scope)
            
            if not policy:
                scale_out_threshold = 80.0
                scale_in_threshold = 30.0
                min_capacity = 1
                max_capacity = 64
            else:
                scale_out_threshold = policy.scale_out_threshold_percent
                scale_in_threshold = policy.scale_in_threshold_percent
                min_capacity = policy.min_capacity
                max_capacity = policy.max_capacity
            
            # Determine action based on utilization and hysteresis
            upper_bound = scale_out_threshold + (policy.hysteresis_percent if policy else 10.0)
            lower_bound = max(0.0, scale_in_threshold - (policy.hysteresis_percent if policy else 10.0))
            
            if utilization_percent >= upper_bound and current_capacity < max_capacity:
                # Scale out
                target = min(current_capacity + max(1, int(current_capacity * 0.25)), max_capacity)
                action = "scale_out"
                reason = f"High utilization ({utilization_percent:.1f}%) exceeds scale-out threshold"
            elif utilization_percent <= lower_bound and current_capacity > min_capacity:
                # Scale in
                target = max(min_capacity, current_capacity - 1)
                action = "scale_in"
                reason = f"Low utilization ({utilization_percent:.1f}%) below scale-in threshold"
            else:
                action = "noop"
                target = current_capacity
                reason = "Utilization within hysteresis bounds"
            
            decision_id = f"scale_dec_{uuid.uuid4().hex[:12]}"
            
            self._record_decision(decision_id, {
                "type": "scaling",
                "scope": scope,
                "action": action,
                "current_capacity": current_capacity,
                "target_capacity": target,
            })
            
            return ScalingDecision(
                decision_id=decision_id,
                runtime_id=self._runtime_id,
                action=action,
                current_capacity=current_capacity,
                target_capacity=target,
                reason=reason,
            )
    
    def evaluate_load_shedding(
        self,
        domain: str,
        overload_state: str,
        queue_depth: int,
        queue_capacity: int,
        eligible_work_classes: Optional[Tuple[str, ...]] = None,
    ) -> LoadSheddingDecision:
        """
        Evaluate load shedding policy and produce a decision.
        
        Args:
            domain: The domain to evaluate
            overload_state: Current runtime overload state
            queue_depth: Current queue occupancy
            queue_capacity: Queue capacity limit
            eligible_work_classes: Work classes that may be shed
            
        Returns:
            Decision with recommended shedding actions
        """
        with self._lock:
            policy = self._load_shedding_policies.get(domain)
            
            # Determine if shedding is needed
            should_shed = overload_state in ("OVERLOADED", "CRITICAL", "COLLAPSING")
            should_shed = should_shed or (queue_depth / max(queue_capacity, 1)) > 0.95
            
            selected_for_shedding = []
            
            if should_shed:
                # Select work classes for shedding
                if policy:
                    eligible = policy.eligible_classes
                else:
                    eligible = ("background", "optional")
                
                if eligible_work_classes:
                    selected_for_shedding = [c for c in eligible if c in eligible_work_classes]
                else:
                    selected_for_shedding = list(eligible)
            
            decision_id = f"shed_dec_{uuid.uuid4().hex[:12]}"
            
            self._record_decision(decision_id, {
                "type": "load_shedding",
                "should_shed": should_shed,
                "selected_classes": selected_for_shedding,
                "reason": "Overload state or queue pressure" if should_shed else "Within capacity",
            })
            
            return LoadSheddingDecision(
                decision_id=decision_id,
                runtime_id=self._runtime_id,
                work_classes_eligible=tuple(eligible if should_shed else ()),
                selected_for_shedding=tuple(selected_for_shedding),
                reason="Overload state or queue pressure" if should_shed else "Within capacity",
            )
    
    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------
    
    def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent decisions (for diagnostics)."""
        with self._lock:
            return list(self._decision_history[-limit:])
    
    def get_snapshot(self) -> "PolicyEngineSnapshot":
        """Get an immutable snapshot of engine state."""
        with self._lock:
            return PolicyEngineSnapshot(
                snapshot_id=f"pe_snap_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                backpressure_policy_count=len(self._backpressure_policies),
                autoscaling_policy_count=len(self._autoscaling_policies),
                load_shedding_policy_count=len(self._load_shedding_policies),
                batching_policy_count=len(self._batching_policies),
            )
    
    def _record_decision(self, decision_id: str, payload: Dict[str, Any]) -> None:
        """Record a decision for audit trail."""
        self._decision_history.append({
            "timestamp_utc": time.time(),
            "decision_id": decision_id,
            "payload": dict(payload),
        })
        
        if len(self._decision_history) > self._max_history:
            self._decision_history = self._decision_history[-self._max_history:]
    
    def _record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Record an internal event (bounded)."""
        self._decision_history.append({
            "timestamp_utc": time.time(),
            "event_type": event_type,
            "payload": dict(payload),
        })
        
        if len(self._decision_history) > self._max_history:
            self._decision_history = self._decision_history[-self._max_history:]


@dataclass(frozen=True)
class PolicyEngineSnapshot:
    """Immutable snapshot of policy engine state."""
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    backpressure_policy_count: int = 0
    autoscaling_policy_count: int = 0
    load_shedding_policy_count: int = 0
    batching_policy_count: int = 0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Decision types
    "PolicyDecisionType",
    
    # Decision artifacts
    "PolicyDecision",
    "OverloadDecision",
    "BackpressureDecision",
    "LoadSheddingDecision",
    "ScalingDecision",
    
    # Canonical authority
    "PerformancePolicyEngine",
    "PolicyEngineSnapshot",
]