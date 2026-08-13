# Backpressure, Capacity & Fairness - Phase 3.11.5 Canonical Flow Control
# ========================================================================

"""
Phase 3.11.5: Canonical Flow Control Architecture for Gordon's Semantic Streams.

Canonical Model:
    Publisher → AdmissionControl → Backpressure → Commit → Capacity → Delivery → Subscriber

Responsibilities:
    - Admissions: Accept, wait, throttle, reject, drop, or escalate
    - Capacity: Bound record count, bytes, memory, generations, active subs, pending work
    - Backpressure: Propagate signals toward producers without modifying history
    - Fairness: Weighted, round-robin, priority-aware scheduling with starvation prevention

Constraints (NOT allowed):
    - Backpressure never reorders committed records
    - Backpressure never mutates committed records
    - Backpressure never rewrites history
    - Priorities must not violate canonical ordering contracts
"""

from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Set,
    Any,
    Protocol,
)
from enum import Enum
import time
import threading


# =============================================================================
# CAPACITY POLICY - Configuration for resource bounds
# =============================================================================

class CapacityDimension(Enum):
    """Dimensions of capacity that can be bounded."""
    RECORD_COUNT = "record_count"
    BYTE_SIZE = "byte_size"
    MEMORY_USAGE = "memory_usage"
    GENERATION_COUNT = "generation_count"
    ACTIVE_SUBSCRIBERS = "active_subscribers"
    REPLAY_REQUESTS = "replay_requests"
    PENDING_DELIVERIES = "pending_deliveries"
    PENDING_ACKNOWLEDGEMENTS = "pending_acknowledgements"


class CapacityStatus(Enum):
    """Capacity status levels of a stream."""
    UNDER_CAPACITY = "under_capacity"     # Well within limits (0-50%)
    WARNING_THRESHOLD = "warning"         # Approaching limits (50-80%)
    CRITICAL_THRESHOLD = "critical"       # Near maximum (80-100%)
    EXCEEDED = "exceeded"                 # Over capacity (>100%)


@dataclass(frozen=True)
class CapacityPolicy:
    """Policy configuration for stream capacity bounds."""
    dimension: CapacityDimension
    limit: int
    warning_threshold_percent: float = 50.0
    critical_threshold_percent: float = 80.0


@dataclass
class CapacityState:
    """Current capacity state for a stream."""
    policy: CapacityPolicy
    current_value: int = 0
    last_updated_utc: float = field(default_factory=time.time)
    
    @property
    def percent_used(self) -> float:
        if self.policy.limit == 0:
            return 100.0
        return (self.current_value / self.policy.limit) * 100.0
    
    @property
    def state_enum(self) -> CapacityStatus:
        percent = self.percent_used
        if percent < 50:
            return CapacityStatus.UNDER_CAPACITY
        elif percent < 80:
            return CapacityStatus.WARNING_THRESHOLD
        elif percent < 100:
            return CapacityStatus.CRITICAL_THRESHOLD
        return CapacityStatus.EXCEEDED
    
    def is_at_capacity(self) -> bool:
        return self.current_value >= self.policy.limit


@dataclass(frozen=True)
class CapacitySnapshot:
    """Immutable snapshot of capacity state."""
    stream_id: str
    policies: Dict[str, int]
    limits: Dict[str, int]
    states: Dict[str, str]
    last_updated_utc: float


@dataclass(frozen=True)
class CapacityMetrics:
    """Metrics for capacity observability."""
    record_count: int = 0
    byte_count: int = 0
    pending_commits: int = 0
    active_subscribers: int = 0
    pending_deliveries: int = 0
    pending_acks: int = 0
    publish_rate_1s: float = 0.0
    consume_rate_1s: float = 0.0
    max_capacity_percent: float = 0.0
    exceeded_dimensions: Tuple[str, ...] = field(default_factory=tuple)


# =============================================================================
# ADMISSION POLICY & DECISIONS
# =============================================================================

class AdmissionDecision(Enum):
    """Decisions made by admission control."""
    ACCEPT = "accept"
    WAIT = "wait"
    THROTTLE = "throttle"
    REJECT = "reject"
    DROP = "drop"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class AdmissionContext:
    """Context for making admission decisions."""
    stream_id: str
    stream_state: Optional[str] = None
    ownership: Optional[Dict] = None
    capacity_state: Dict[str, CapacityState] = field(default_factory=dict)
    publisher_id: str = ""
    record_size_bytes: int = 0
    priority: int = 0
    is_replay: bool = False
    is_duplicate: bool = False
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class AdmissionDecisionRecord:
    """Record of an admission decision."""
    decision: AdmissionDecision
    reason: str
    timestamp_utc: float = field(default_factory=time.time)
    stream_id: str = ""
    publisher_id: str = ""
    capacity_percent: float = 0.0
    queue_length: int = 0
    retry_after_seconds: Optional[float] = None


class AdmissionPolicy(Protocol):
    """Protocol for admission policies."""
    
    def evaluate(self, context: AdmissionContext) -> AdmissionDecisionRecord:
        ...


@dataclass
class SimpleAdmissionPolicy:
    """Default admission policy implementation."""
    max_queue_wait_seconds: float = 60.0
    drop_lowest_priority: bool = True
    strict_capacity_enforcement: bool = False
    
    def evaluate(self, context: AdmissionContext) -> AdmissionDecisionRecord:
        if context.stream_state == "CLOSED":
            return AdmissionDecisionRecord(
                decision=AdmissionDecision.REJECT,
                reason="Stream is closed",
                stream_id=context.stream_id,
                publisher_id=context.publisher_id,
            )
        
        if context.stream_state == "PAUSED":
            if context.priority >= 10:
                return AdmissionDecisionRecord(
                    decision=AdmissionDecision.ESCALATE,
                    reason="Paused stream but high priority request",
                    stream_id=context.stream_id,
                    publisher_id=context.publisher_id,
                )
            return AdmissionDecisionRecord(
                decision=AdmissionDecision.REJECT,
                reason="Stream is paused",
                stream_id=context.stream_id,
                publisher_id=context.publisher_id,
            )
        
        exceeded_capacity = False
        max_percent = 0.0
        
        for dimension, cap_state in context.capacity_state.items():
            max_percent = max(max_percent, cap_state.percent_used)
            if self.strict_capacity_enforcement:
                if cap_state.is_at_capacity():
                    exceeded_capacity = True
            else:
                if cap_state.state_enum == CapacityStatus.EXCEEDED:
                    exceeded_capacity = True
        
        if exceeded_capacity:
            if context.priority < 0:
                return AdmissionDecisionRecord(
                    decision=AdmissionDecision.DROP,
                    reason="Capacity exceeded - low priority record dropped",
                    stream_id=context.stream_id,
                    publisher_id=context.publisher_id,
                    capacity_percent=max_percent,
                )
            return AdmissionDecisionRecord(
                decision=AdmissionDecision.WAIT,
                reason="Capacity exceeded - queued for later processing",
                stream_id=context.stream_id,
                publisher_id=context.publisher_id,
                capacity_percent=max_percent,
                retry_after_seconds=self.max_queue_wait_seconds * 0.5,
            )
        
        return AdmissionDecisionRecord(
            decision=AdmissionDecision.ACCEPT,
            reason="Record admitted successfully",
            stream_id=context.stream_id,
            publisher_id=context.publisher_id,
            capacity_percent=max_percent,
        )


# =============================================================================
# BACKPRESSURE POLICY & SIGNALS
# =============================================================================

class BackpressureMode(Enum):
    """How backpressure is applied when limits are exceeded."""
    REJECT_NEW = "reject_new"
    DROP_OLDEST = "drop_oldest"
    THROTTLE_PUBLISHERS = "throttle_publishers"
    BLOCK_SUBSCRIBERS = "block_subscribers"
    DEGRADE_QUALITY = "degrade_quality"


@dataclass(frozen=True)
class BackpressurePolicy:
    """Policy for applying backpressure."""
    mode: BackpressureMode
    burst_allowance_percent: float = 10.0
    recovery_delay_seconds: float = 5.0
    throttle_decay_rate: float = 0.9


@dataclass(frozen=True)
class BackpressureSignal:
    """Signal indicating backpressure is active."""
    stream_id: str
    signal_type: str
    current_value: float
    limit_value: float
    threshold_percent: float = 80.0
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_severe(self) -> bool:
        return self.threshold_percent >= 95.0
    
    @property
    def severity_level(self) -> int:
        ratio = self.current_value / max(self.limit_value, 1)
        if ratio >= 2.0:
            return 3
        elif ratio >= 1.5:
            return 2
        return 1


@dataclass(frozen=True)
class BackpressureState:
    """Current backpressure state for a stream."""
    policy: BackpressurePolicy
    active_signals: List[BackpressureSignal] = field(default_factory=list)
    last_backpressure_utc: Optional[float] = None
    
    @property
    def is_under_backpressure(self) -> bool:
        return len(self.active_signals) > 0
    
    @property
    def max_severity(self) -> int:
        if not self.active_signals:
            return 0
        return max(s.severity_level for s in self.active_signals)
    
    def get_signal_by_type(self, signal_type: str) -> Optional[BackpressureSignal]:
        for signal in self.active_signals:
            if signal.signal_type == signal_type:
                return signal
        return None


# =============================================================================
# FAIRNESS POLICY & SCHEDULING
# =============================================================================

class FairnessPolicy(Enum):
    """Policies for fair resource distribution."""
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    PRIORITY_FIFO = "priority_fifo"
    PROPORTIONAL_SHARE = "proportional_share"
    STARVATION_PREVENTION = "starvation_prevention"


@dataclass(frozen=True)
class FairnessPolicyConfig:
    """Configuration for fairness policy."""
    policy: FairnessPolicy = FairnessPolicy.WEIGHTED_ROUND_ROBIN
    weights: Dict[str, int] = field(default_factory=dict)
    max_wait_seconds: float = 30.0


@dataclass(frozen=True)
class FairnessSnapshot:
    """Snapshot of fairness state for observability."""
    stream_id: str
    publisher_stats: Dict[str, Dict]
    total_records_delivered: int
    total_wait_time_seconds: float
    max_starvation_time: float = 0.0


@dataclass(frozen=True)
class ThrottlingDecision(Enum):
    """Decision about throttling."""
    ALLOW = "allow"
    SLOW_DOWN = "slow_down"
    SUSPEND = "suspend"
    REJECT_PERMANENTLY = "reject_permanently"


@dataclass(frozen=True)
class ThrottlingDecisionRecord:
    """Record of a throttling decision."""
    entity_id: str
    entity_type: str
    decision: ThrottlingDecision
    reason: str
    timestamp_utc: float = field(default_factory=time.time)
    rate_factor: Optional[float] = None
    duration_seconds: Optional[float] = None


@dataclass
class WeightedFairScheduler:
    """Weighted round-robin scheduler for fair distribution."""
    
    config: FairnessPolicyConfig
    _publishers: Dict[str, int] = field(default_factory=dict)
    _round_robin_order: List[str] = field(default_factory=list)
    _current_index: int = 0
    _publisher_state: Dict[str, Dict] = field(default_factory=dict)
    
    def __post_init__(self):
        self._lock = threading.RLock()
        
    def register_publisher(self, publisher_id: str, weight: int = 1) -> None:
        with self._lock:
            if publisher_id not in self._publishers:
                idx = 0
                for i, pid in enumerate(self._round_robin_order):
                    if self._publishers[pid] < weight:
                        idx = i
                        break
                    idx = i + 1
                self._round_robin_order.insert(idx, publisher_id)
            
            self._publishers[publisher_id] = weight
            
            if publisher_id not in self._publisher_state:
                self._publisher_state[publisher_id] = {
                    "records_delivered": 0,
                    "last_service_utc": time.time(),
                    "wait_since": None,
                }
    
    def unregister_publisher(self, publisher_id: str) -> bool:
        with self._lock:
            if publisher_id in self._publishers:
                del self._publishers[publisher_id]
                try:
                    self._round_robin_order.remove(publisher_id)
                except ValueError:
                    pass
                if publisher_id in self._publisher_state:
                    del self._publisher_state[publisher_id]
                if self._current_index >= len(self._round_robin_order):
                    self._current_index = 0
                return True
            return False
    
    def get_next_publisher(self) -> Optional[str]:
        with self._lock:
            if not self._round_robin_order:
                return None
            
            current_time = time.time()
            
            for pid in self._round_robin_order:
                state = self._publisher_state.get(pid, {})
                wait_start = state.get("wait_since")
                if wait_start and (current_time - wait_start) > self.config.max_wait_seconds:
                    return pid
            
            start_index = self._current_index
            attempts = 0
            
            while attempts < len(self._round_robin_order):
                idx = (self._current_index + attempts) % len(self._round_robin_order)
                publisher_id = self._round_robin_order[idx]
                
                weight = self._publishers.get(publisher_id, 1)
                if weight >= 1:
                    self._current_index = (idx + 1) % len(self._round_robin_order)
                    self._publisher_state[publisher_id]["last_service_utc"] = current_time
                    self._publisher_state[publisher_id]["wait_since"] = None
                    return publisher_id
                
                attempts += 1
            
            if self._round_robin_order:
                pid = self._round_robin_order[0]
                self._current_index = 1 % len(self._round_robin_order)
                self._publisher_state[pid]["last_service_utc"] = current_time
                self._publisher_state[pid]["wait_since"] = None
                return pid
            
            return None
    
    def record_delivery(self, publisher_id: str) -> None:
        with self._lock:
            if publisher_id in self._publisher_state:
                self._publisher_state[publisher_id]["records_delivered"] += 1
                self._publisher_state[publisher_id]["wait_since"] = None
    
    def record_wait(self, publisher_id: str) -> None:
        with self._lock:
            if publisher_id in self._publisher_state:
                state = self._publisher_state[publisher_id]
                if state.get("wait_since") is None:
                    state["wait_since"] = time.time()
    
    def get_statistics(self) -> Dict[str, Any]:
        with self._lock:
            current_time = time.time()
            max_wait = 0.0
            for pid, state in self._publisher_state.items():
                wait_start = state.get("wait_since")
                if wait_start:
                    max_wait = max(max_wait, current_time - wait_start)
            
            return {
                "total_publishers": len(self._publishers),
                "round_robin_order": list(self._round_robin_order),
                "current_index": self._current_index,
                "max_starvation_seconds": max_wait,
                "publisher_stats": self._publisher_state.copy(),
            }


# =============================================================================
# FLOW CONTROLLER - Central coordinator
# =============================================================================

class CongestionState(Enum):
    """Overall congestion state of a stream."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    SEVERE = "severe"


@dataclass(frozen=True)
class CongestionReport:
    """Report of current congestion state."""
    stream_id: str
    overall_state: CongestionState
    timestamp_utc: float = field(default_factory=time.time)
    capacity_states: Dict[str, str] = field(default_factory=dict)
    exceeded_dimensions: Tuple[str, ...] = field(default_factory=tuple)
    active_signals: Tuple[Dict, ...] = field(default_factory=tuple)
    records_per_second_in: float = 0.0
    records_per_second_out: float = 0.0
    publishers_active: int = 0
    subscribers_active: int = 0
    max_starvation_seconds: float = 0.0


@dataclass
class FlowControllerConfig:
    """Configuration for the flow controller."""
    capacity_policies: Dict[CapacityDimension, CapacityPolicy] = field(default_factory=dict)
    default_capacity_policy: Optional[CapacityPolicy] = None
    admission_policy: Optional[AdmissionPolicy] = None
    backpressure_policy: BackpressurePolicy = field(
        default_factory=lambda: BackpressurePolicy(mode=BackpressureMode.THROTTLE_PUBLISHERS)
    )
    fairness_config: FairnessPolicyConfig = field(
        default_factory=lambda: FairnessPolicyConfig(policy=FairnessPolicy.WEIGHTED_ROUND_ROBIN)
    )
    max_throttle_duration_seconds: float = 60.0
    throttle_decay_rate: float = 0.9


class FlowController:
    """Central coordinator for flow control decisions."""
    
    def __init__(self, config: Optional[FlowControllerConfig] = None):
        self._config = config or FlowControllerConfig()
        self._lock = threading.RLock()
        self._capacity_states: Dict[str, CapacityState] = {}
        self._backpressure_state: Optional[BackpressureState] = None
        self._fairness_scheduler: Optional[WeightedFairScheduler] = None
        self._records_in: int = 0
        self._records_out: int = 0
        self._last_metrics_update_utc: float = time.time()
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        with self._lock:
            for dim, policy in self._config.capacity_policies.items():
                self._capacity_states[dim.value] = CapacityState(policy=policy)
            
            if self._config.default_capacity_policy:
                self._capacity_states["default"] = CapacityState(
                    policy=self._config.default_capacity_policy
                )
            
            self._backpressure_state = BackpressureState(
                policy=self._config.backpressure_policy
            )
            
            if self._config.fairness_config:
                self._fairness_scheduler = WeightedFairScheduler(
                    config=self._config.fairness_config
                )
    
    def check_admission(self, context: AdmissionContext) -> AdmissionDecisionRecord:
        with self._lock:
            for dim, cap_state in context.capacity_state.items():
                self._capacity_states[dim] = cap_state
            
            policy = self._config.admission_policy or SimpleAdmissionPolicy()
            decision = policy.evaluate(context)
            
            if decision.decision == AdmissionDecision.ACCEPT:
                self._records_in += 1
            
            return decision
    
    def record_commit(self, publisher_id: str, size_bytes: int) -> Tuple[bool, Optional[BackpressureSignal]]:
        with self._lock:
            if "byte_size" in self._capacity_states:
                state = self._capacity_states["byte_size"]
                state.current_value += size_bytes
            
            if self._fairness_scheduler:
                self._fairness_scheduler.record_delivery(publisher_id)
            
            return self._check_backpressure()
    
    def record_delivery(
        self,
        subscriber_id: str,
        publisher_id: Optional[str] = None,
    ) -> Tuple[bool, Optional[BackpressureSignal]]:
        with self._lock:
            self._records_out += 1
            
            if publisher_id and self._fairness_scheduler:
                self._fairness_scheduler.record_delivery(publisher_id)
            
            return self._check_backpressure()
    
    def _check_backpressure(self) -> Tuple[bool, Optional[BackpressureSignal]]:
        for dim_name, state in self._capacity_states.items():
            if state.state_enum == CapacityStatus.EXCEEDED:
                signal = BackpressureSignal(
                    stream_id="stream",
                    signal_type=f"capacity_{dim_name}",
                    current_value=float(state.current_value),
                    limit_value=float(state.policy.limit),
                    threshold_percent=state.percent_used,
                )
                
                if self._backpressure_state:
                    self._backpressure_state.active_signals.append(signal)
                    self._backpressure_state.last_backpressure_utc = time.time()
                
                return False, signal
        
        if self._backpressure_state:
            self._backpressure_state.active_signals.clear()
        
        return True, None
    
    def get_capacity_snapshot(self) -> CapacitySnapshot:
        with self._lock:
            return CapacitySnapshot(
                stream_id="stream",
                policies={
                    dim: state.policy.limit
                    for dim, state in self._capacity_states.items()
                },
                limits={
                    dim: state.current_value
                    for dim, state in self._capacity_states.items()
                },
                states={
                    dim: state.state_enum.value
                    for dim, state in self._capacity_states.items()
                },
                last_updated_utc=time.time(),
            )
    
    def get_metrics(self) -> CapacityMetrics:
        with self._lock:
            elapsed = time.time() - self._last_metrics_update_utc
            
            return CapacityMetrics(
                record_count=sum(
                    s.current_value 
                    for s in self._capacity_states.values()
                    if "record" in s.policy.dimension.value
                ),
                byte_count=self._capacity_states.get("byte_size", CapacityState(CapacityPolicy(dimension=CapacityDimension.BYTE_SIZE, limit=0))).current_value,
                pending_commits=0,
                active_subscribers=len(self._fairness_scheduler._publishers) if self._fairness_scheduler else 0,
                pending_deliveries=self._records_in - self._records_out,
                pending_acks=0,
                publish_rate_1s=self._records_in / max(elapsed, 0.1),
                consume_rate_1s=self._records_out / max(elapsed, 0.1),
                max_capacity_percent=max(
                    s.percent_used for s in self._capacity_states.values()
                ) if self._capacity_states else 0,
                exceeded_dimensions=tuple(
                    dim for dim, state in self._capacity_states.items()
                    if state.state_enum == CapacityStatus.EXCEEDED
                ),
            )
    
    def get_congestion_report(self) -> CongestionReport:
        with self._lock:
            max_percent = max(
                s.percent_used for s in self._capacity_states.values()
            ) if self._capacity_states else 0.0
            
            if max_percent >= 95:
                state = CongestionState.SEVERE
            elif max_percent >= 80:
                state = CongestionState.CRITICAL
            elif max_percent >= 50:
                state = CongestionState.WARNING
            else:
                state = CongestionState.HEALTHY
            
            signals = []
            if self._backpressure_state:
                for sig in self._backpressure_state.active_signals:
                    signals.append({
                        "type": sig.signal_type,
                        "current": sig.current_value,
                        "limit": sig.limit_value,
                        "severity": sig.severity_level,
                    })
            
            fairness_stats = {}
            if self._fairness_scheduler:
                fairness_stats = self._fairness_scheduler.get_statistics()
            
            return CongestionReport(
                stream_id="stream",
                overall_state=state,
                capacity_states={
                    dim: state.state_enum.value
                    for dim, state in self._capacity_states.items()
                },
                exceeded_dimensions=tuple(
                    dim for dim, state in self._capacity_states.items()
                    if state.state_enum == CapacityStatus.EXCEEDED
                ),
                active_signals=tuple(signals),
                records_per_second_in=self._records_in / max(time.time() - self._last_metrics_update_utc, 0.1),
                records_per_second_out=self._records_out / max(time.time() - self._last_metrics_update_utc, 0.1),
                publishers_active=len(self._fairness_scheduler._publishers) if self._fairness_scheduler else 0,
                subscribers_active=0,
                max_starvation_seconds=fairness_stats.get("max_starvation_seconds", 0),
            )
    
    def get_throttling_decision(
        self,
        entity_id: str,
        entity_type: str,
        context: Dict[str, Any],
    ) -> ThrottlingDecisionRecord:
        with self._lock:
            if self._fairness_scheduler:
                return ThrottlingDecisionRecord(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    decision=ThrottlingDecision.ALLOW,
                    reason="Not throttled",
                )
            
            return ThrottlingDecisionRecord(
                entity_id=entity_id,
                entity_type=entity_type,
                decision=ThrottlingDecision.ALLOW,
                reason="No fairness policy configured",
            )


__all__ = [
    "CapacityDimension",
    "CapacityStatus",
    "CapacityPolicy",
    "CapacityState",
    "CapacitySnapshot",
    "CapacityMetrics",
    
    "AdmissionDecision",
    "AdmissionContext",
    "AdmissionDecisionRecord",
    "AdmissionPolicy",
    "SimpleAdmissionPolicy",
    
    "BackpressureMode",
    "BackpressurePolicy",
    "BackpressureSignal",
    "BackpressureState",
    
    "FairnessPolicy",
    "FairnessPolicyConfig",
    "FairnessSnapshot",
    "ThrottlingDecision",
    "ThrottlingDecisionRecord",
    "WeightedFairScheduler",
    
    "CongestionState",
    "CongestionReport",
    "FlowControllerConfig",
    "FlowController",
]