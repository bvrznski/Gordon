# Capacity Planner
# ================

"""
Capacity planning authority for Gordon runtime Phase 3.7.18-I.

This module provides the canonical capacity-planning authority:

CANONICAL AUTHORITY:
    - CapacityPlanner: Capacity forecasting and planning
    
The planner analyzes current state, historical trends, and projected workload
to produce capacity recommendations. It does NOT directly resize resources -
that responsibility belongs to ResourceManager and autoscaling authorities.

PRINCIPLES:
    - Proactive (forecast before saturation)
    - Conservative (recommend headroom, not maximum utilization)
    - Bounded (respects explicit limits)
    - Observable (transparent about assumptions)

Usage:
    from gordon.components.core.performance import CapacityPlanner
    
    planner = CapacityPlanner(runtime_id="runtime_1")
    
    # Get capacity forecast
    forecast = planner.get_forecast(
        current_state=state,
        historical_data=history,
        projected_workload=workload_projection
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import uuid
import time


# =============================================================================
# CAPACITY PROJECTIONS
# =============================================================================

@dataclass(frozen=True)
class CapacityProjection:
    """
    Projected capacity usage over time.
    
    For a single resource domain.
    """
    
    domain: str
    
    # Timeline of projections (timestamps and projected usage)
    timestamps_utc: Tuple[float, ...]
    projected_usage: Tuple[float, ...]  # Values like utilization percent, bytes, etc.
    
    @property
    def max_projection(self) -> float:
        """Get maximum projected value."""
        return max(self.projected_usage) if self.projected_usage else 0.0
    
    @property
    def min_projection(self) -> float:
        """Get minimum projected value."""
        return min(self.projected_usage) if self.projected_usage else 0.0


@dataclass(frozen=True)
class CapacityRequirement:
    """
    Required capacity for a specific period.
    
    Used to check if current resources can handle expected load.
    """
    
    requirement_id: str
    runtime_id: str
    
    domain: str  # e.g., "memory", "cpu", "queue_capacity"
    required_value: float
    time_window_seconds: float = 3600.0  # Default 1 hour
    
    confidence_percent: float = 95.0  # How confident are we in this requirement?
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class CapacityGap:
    """
    Gap between current capacity and required capacity.
    
    Used to identify when scaling is needed.
    """
    
    gap_id: str
    runtime_id: str
    
    domain: str
    current_capacity: float
    required_capacity: float
    
    gap_amount: float  # Required - Current
    
    priority: str = "medium"  # low, medium, high, critical
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def needed(self) -> bool:
        """Check if capacity gap exists."""
        return self.gap_amount > 0


# =============================================================================
# CAPACITY PLANNER (CANONICAL AUTHORITY)
# =============================================================================

class CapacityPlanner:
    """
    Canonical capacity-planning authority.
    
    This is THE ONE source of capacity recommendations. It analyzes current
    state, historical trends, and projected workload to produce forecasts.
    
    What it does NOT do:
        - Does not resize pools or allocate resources
        - Does not directly trigger scaling actions
        
    What it DOES own:
        - Capacity forecasting algorithms
        - Gap analysis (current vs required)
        - Headroom recommendations
        - Failure reserve calculations
        - Scale recommendations with justification
    
    Usage:
        planner = CapacityPlanner(runtime_id="runtime_1")
        
        # Get capacity forecast
        forecast = planner.get_forecast(
            current_state=state,
            historical_data=history,
            projected_workload=workload_projection
        )
        
        # Check for capacity gaps
        gap = planner.analyze_gap(current_capacity, required_capacity)
    """
    
    def __init__(self, runtime_id: str):
        """
        Initialize the capacity planner.
        
        Args:
            runtime_id: Unique identifier for this runtime instance
        """
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Configuration
        self._forecast_window_seconds: float = 3600.0  # 1 hour default
        self._safety_margin_percent: float = 20.0      # Add 20% headroom
        
        # Historical data storage (bounded)
        self._capacity_snapshots: List[Dict[str, Any]] = []
        self._max_snapshots = 1000
        
        # Request history (bounded)
        self._request_history: List[Dict[str, Any]] = []
        self._max_requests = 500
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID this planner serves."""
        return self._runtime_id
    
    @property
    def forecast_window_seconds(self) -> float:
        """Get the current forecast window in seconds."""
        return self._forecast_window_seconds
    
    def set_forecast_window(self, seconds: float) -> None:
        """Set the forecast window (e.g., 30 minutes, 1 hour)."""
        if seconds <= 0:
            raise ValueError("Forecast window must be positive")
        with self._lock:
            self._forecast_window_seconds = seconds
    
    def set_safety_margin(self, percent: float) -> None:
        """Set the safety margin (headroom) to add to forecasts."""
        if not 0 <= percent <= 50:
            raise ValueError("Safety margin must be between 0% and 50%")
        with self._lock:
            self._safety_margin_percent = percent
    
    # -------------------------------------------------------------------------
    # Capacity Forecasting
    # -------------------------------------------------------------------------
    
    def get_forecast(
        self,
        current_state: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        projected_workload: Optional[Dict[str, float]] = None,
    ) -> "CapacityForecast":
        """
        Get a capacity forecast for the runtime.
        
        Args:
            current_state: Current capacity measurements (utilization, usage, etc.)
            historical_data: Historical snapshots for trend analysis
            projected_workload: Expected workload (tasks per second, etc.)
            
        Returns:
            CapacityForecast with projections and recommendations
        """
        with self._lock:
            # Start with current state as the baseline
            timestamps = [time.time()]
            projections: Dict[str, List[float]] = {}
            
            for domain, value in current_state.items():
                if isinstance(value, (int, float)):
                    projections[domain] = [float(value)]
            
            # Apply trend analysis if historical data available
            if historical_data and len(historical_data) >= 3:
                # Calculate simple linear trend for each domain
                for domain in projections.keys():
                    values = []
                    for snapshot in historical_data[-10:]:  # Last 10 snapshots
                        if domain in snapshot.get("measurements", {}):
                            values.append(snapshot["measurements"][domain])
                    
                    if len(values) >= 2:
                        # Simple linear trend (first order)
                        delta = values[-1] - values[0]
                        trend_rate = delta / len(values)  # per snapshot
                        
                        # Project forward
                        for i in range(1, 6):  # 5 forecast points
                            next_val = values[-1] + trend_rate * i
                            projections.setdefault(domain, []).append(next_val)
            
            # Apply workload projection if available
            if projected_workload:
                for domain, workload in projected_workload.items():
                    current = projections.get(domain, [0])[-1]
                    # Simple linear scaling based on workload
                    scaled = current * (1 + workload / 100)  # workload is percent change
                    projections.setdefault(domain, []).append(scaled)
            
            # Add safety margin to all projections
            for domain in projections:
                current_val = projections[domain][-1]
                projected_val = current_val * (1 + self._safety_margin_percent / 100)
                projections[domain].append(projected_val)
            
            # Build projection objects
            domain_projections: Dict[str, CapacityProjection] = {}
            for domain, values in projections.items():
                if len(values) > 1:
                    timestamps_utc = tuple(timestamps[:len(values)])
                    projected_usage = tuple(values)
                    domain_projections[domain] = CapacityProjection(
                        domain=domain,
                        timestamps_utc=timestamps_utc,
                        projected_usage=projected_usage,
                    )
            
            # Determine peak projection
            peak_domain = None
            peak_value = 0.0
            for domain, proj in domain_projections.items():
                max_val = proj.max_projection
                if max_val > peak_value:
                    peak_value = max_val
                    peak_domain = domain
            
            return CapacityForecast(
                forecast_id=f"cap_forecast_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                window_start_utc=timestamps[0],
                window_end_utc=timestamps[0] + self._forecast_window_seconds,
                projections=domain_projections,
                peak_domain=peak_domain,
                peak_value=peak_value,
            )
    
    def analyze_gap(
        self,
        current_capacity: float,
        required_capacity: float,
        domain: str,
    ) -> CapacityGap:
        """
        Analyze if there's a capacity gap.
        
        Args:
            current_capacity: Current available capacity
            required_capacity: Required capacity for the workload
            domain: The resource domain (memory, cpu, queue, etc.)
            
        Returns:
            Gap analysis with priority and recommendations
        """
        gap_amount = required_capacity - current_capacity
        
        # Determine priority based on severity
        if gap_amount <= 0:
            priority = "none"
        elif gap_amount / max(current_capacity, 1) < 0.2:  # < 20% gap
            priority = "low"
        elif gap_amount / max(current_capacity, 1) < 0.5:  # < 50% gap
            priority = "medium"
        else:
            priority = "critical"
        
        return CapacityGap(
            gap_id=f"cap_gap_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            domain=domain,
            current_capacity=current_capacity,
            required_capacity=required_capacity,
            gap_amount=gap_amount,
            priority=priority,
        )
    
    def calculate_headroom(
        self,
        total_capacity: float,
        current_usage: float,
    ) -> "CapacityHeadroom":
        """
        Calculate available headroom.
        
        Args:
            total_capacity: Total available capacity
            current_usage: Currently consumed capacity
            
        Returns:
            Headroom calculation with percentages
        """
        free = max(0.0, total_capacity - current_usage)
        utilization = (current_usage / max(total_capacity, 1)) * 100
        
        return CapacityHeadroom(
            headroom_id=f"headroom_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            total_capacity=total_capacity,
            current_usage=current_usage,
            free_capacity=free,
            utilization_percent=utilization,
        )
    
    def calculate_failure_reserve(
        self,
        current_capacity: float,
        reserve_percentage: float = 15.0,
    ) -> "CapacityReserve":
        """
        Calculate failure reserve (capacity reserved for recovery).
        
        Args:
            current_capacity: Current total capacity
            reserve_percentage: Percentage to reserve (default 15%)
            
        Returns:
            Reserve calculation with availability information
        """
        reserve_amount = current_capacity * (reserve_percentage / 100)
        available = current_capacity - reserve_amount
        
        return CapacityReserve(
            reserve_id=f"fail_reserve_{uuid.uuid4().hex[:12]}",
            runtime_id=self._runtime_id,
            total_capacity=current_capacity,
            reserve_amount=reserve_amount,
            available_capacity=available,
            reserve_percent=reserve_percentage,
        )
    
    def get_recommendations(
        self,
        current_state: Dict[str, Any],
        forecast: Optional["CapacityForecast"] = None,
        gaps: Optional[List[CapacityGap]] = None,
    ) -> "CapacityRecommendation":
        """
        Get capacity recommendations based on analysis.
        
        Args:
            current_state: Current measurements
            forecast: Capacity forecast (if available)
            gaps: Known capacity gaps
            
        Returns:
            Recommendations with actions and justification
        """
        with self._lock:
            recommendations = []
            
            # Check for saturation
            for domain, utilization in current_state.items():
                if isinstance(utilization, (int, float)):
                    if utilization > 85:
                        recommendations.append({
                            "type": "scale_out",
                            "domain": domain,
                            "reason": f"High utilization: {utilization:.1f}%",
                            "confidence": "high" if utilization > 90 else "medium",
                        })
            
            # Add gap-based recommendations
            if gaps:
                for gap in sorted(gaps, key=lambda g: {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(g.priority, 0), reverse=True):
                    recommendations.append({
                        "type": "capacity_increase",
                        "domain": gap.domain,
                        "amount": gap.gap_amount,
                        "reason": f"Required: {gap.required_capacity}, Available: {gap.current_capacity}",
                        "priority": gap.priority,
                    })
            
            # If no specific issues, recommend routine monitoring
            if not recommendations:
                recommendations.append({
                    "type": "monitor",
                    "domain": "all",
                    "reason": "Capacity within acceptable limits",
                    "confidence": "low",
                })
            
            recommendation_id = f"cap_rec_{uuid.uuid4().hex[:12]}"
            
            self._record_request("recommendation", {
                "recommendation_id": recommendation_id,
                "count": len(recommendations),
                "domains": [r.get("domain") for r in recommendations],
            })
            
            return CapacityRecommendation(
                recommendation_id=recommendation_id,
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                recommendations=tuple(recommendations),
            )
    
    # -------------------------------------------------------------------------
    # History and Diagnostics
    # -------------------------------------------------------------------------
    
    def record_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Record a capacity snapshot for historical analysis."""
        with self._lock:
            self._capacity_snapshots.append(snapshot)
            
            if len(self._capacity_snapshots) > self._max_snapshots:
                self._capacity_snapshots = self._capacity_snapshots[-self._max_snapshots:]
    
    def get_snapshot_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent capacity snapshots."""
        with self._lock:
            return list(self._capacity_snapshots[-limit:])
    
    def get_request_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent requests (for diagnostics)."""
        with self._lock:
            return list(self._request_history[-limit:])
    
    def _record_request(self, request_type: str, payload: Dict[str, Any]) -> None:
        """Record a request for audit trail."""
        self._request_history.append({
            "timestamp_utc": time.time(),
            "request_type": request_type,
            "payload": dict(payload),
        })
        
        if len(self._request_history) > self._max_requests:
            self._request_history = self._request_history[-self._max_requests:]
    
    def get_snapshot(self) -> "CapacityPlannerSnapshot":
        """Get an immutable snapshot of planner state."""
        with self._lock:
            return CapacityPlannerSnapshot(
                snapshot_id=f"cp_snap_{uuid.uuid4().hex[:12]}",
                runtime_id=self._runtime_id,
                timestamp_utc=time.time(),
                forecast_window_seconds=self._forecast_window_seconds,
                safety_margin_percent=self._safety_margin_percent,
                snapshot_count=len(self._capacity_snapshots),
            )


# =============================================================================
# CAPACITY ARTIFACTS
# =============================================================================

@dataclass(frozen=True)
class CapacityForecast:
    """
    Forecast of future capacity needs.
    
    Based on historical trends and projected workload.
    """
    
    forecast_id: str
    runtime_id: str
    
    # Time horizon
    window_start_utc: float
    window_end_utc: float
    
    # Forecasts per domain
    projections: Dict[str, CapacityProjection] = field(default_factory=dict)
    
    peak_domain: Optional[str] = None
    peak_value: float = 0.0


@dataclass(frozen=True)
class CapacityHeadroom:
    """
    Available headroom before saturation.
    
    Headroom = free capacity / total capacity
    """
    
    headroom_id: str
    runtime_id: str
    
    total_capacity: float
    current_usage: float
    
    @property
    def free_capacity(self) -> float:
        return max(0.0, self.total_capacity - self.current_usage)
    
    @property
    def utilization_percent(self) -> float:
        if self.total_capacity <= 0:
            return 0.0
        return (self.current_usage / self.total_capacity) * 100
    
    @property
    def headroom_percent(self) -> float:
        """Get headroom as percentage of total."""
        if self.total_capacity <= 0:
            return 100.0
        return (self.free_capacity / self.total_capacity) * 100


@dataclass(frozen=True)
class CapacityReserve:
    """
    Reserved capacity for failure recovery.
    
    Ensures some capacity is always available for critical recovery operations.
    """
    
    reserve_id: str
    runtime_id: str
    
    total_capacity: float
    reserve_amount: float  # Amount reserved for failures
    available_capacity: float  # Total - Reserve
    
    reserve_percent: float = 15.0


@dataclass(frozen=True)
class CapacityRecommendation:
    """
    Recommendations based on capacity analysis.
    
    Contains actionable recommendations with justification.
    """
    
    recommendation_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    recommendations: Tuple[Dict[str, Any], ...]
    
    @property
    def scale_out_needed(self) -> bool:
        """Check if scaling out is recommended."""
        return any(r.get("type") == "scale_out" for r in self.recommendations)


@dataclass(frozen=True)
class CapacityPlannerSnapshot:
    """
    Immutable snapshot of capacity planner state.
    
    Used for diagnostics and historical analysis.
    """
    
    snapshot_id: str
    runtime_id: str
    
    timestamp_utc: float
    
    forecast_window_seconds: float
    safety_margin_percent: float
    
    snapshot_count: int = 0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Projections and requirements
    "CapacityProjection",
    "CapacityRequirement",
    
    # Gap analysis
    "CapacityGap",
    
    # Planner (canonical authority)
    "CapacityPlanner",
    
    # Artifacts
    "CapacityForecast",
    "CapacityHeadroom",
    "CapacityReserve",
    "CapacityRecommendation",
    "CapacityPlannerSnapshot",
]