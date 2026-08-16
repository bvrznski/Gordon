# Integration Statistics - Phase 5.1.7 Communication Statistics
# =============================================================

"""
Memory Integration Statistics: Tracks communication patterns and metrics.

Statistics provide:
    - Request/response counts
    - Throughput measurements
    - Consumer behavior analysis
    - Pattern detection for optimization

Statistics Laws:
    STATISTICS-LAW-001: All requests must be measurable
    STATISTICS-LAW-002: All responses must be measurable
    STATISTICS-LAW-003: Statistics must be deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# STATISTIC TYPES
# =============================================================================


class StatisticType(Enum):
    """
    Types of statistics that can be collected.
    
    | Type        | Description                                      |
    |-------------|--------------------------------------------------|
    | REQUEST     | Request count and patterns                       |
    | RESPONSE    | Response count and patterns                      |
    | LATENCY     | Latency distribution                             |
    | ERROR       | Error counts and types                           |
    | THROUGHPUT  | Requests per time unit                           |
    """
    
    REQUEST = "request"
    RESPONSE = "response"
    LATENCY = "latency"
    ERROR = "error"
    THROUGHPUT = "throughput"


# =============================================================================
# REQUEST STATISTICS
# =============================================================================


@dataclass(frozen=True)
class RequestStatistics:
    """
    Statistics about requests made.
    
    Fields:
        total_requests:  Total number of requests
        successful:      Number of successful requests
        failed:          Number of failed requests
        
        by_consumer:     Requests broken down by consumer
        by_type:         Requests by request type
        
        first_request:   When was the first request?
        last_request:    When was the last request?
    """
    
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    
    by_consumer: Dict[str, int] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)
    
    first_request: float = field(default_factory=time.time)
    last_request: float = field(default_factory=time.time)


# =============================================================================
# RESPONSE STATISTICS
# =============================================================================


@dataclass(frozen=True)
class ResponseStatistics:
    """
    Statistics about responses received.
    
    Fields:
        total_responses: Total number of responses
        by_outcome:      Responses broken down by outcome
        
        avg_confidence:  Average confidence across responses
        min_confidence:  Minimum confidence seen
        max_confidence:  Maximum confidence seen
        
        first_response:  When was the first response?
        last_response:   When was the last response?
    """
    
    total_responses: int = 0
    by_outcome: Dict[str, int] = field(default_factory=dict)
    
    avg_confidence: float = 1.0
    min_confidence: float = 1.0
    max_confidence: float = 0.0
    
    first_response: float = field(default_factory=time.time)
    last_response: float = field(default_factory=time.time)


# =============================================================================
# LATENCY STATISTICS
# =============================================================================


@dataclass(frozen=True)
class LatencyStatistics:
    """
    Statistics about request latency.
    
    Fields:
        p50_ms:       50th percentile (median) latency
        p95_ms:       95th percentile latency
        p99_ms:       99th percentile latency
        
        min_ms:       Minimum observed latency
        max_ms:       Maximum observed latency
        avg_ms:       Average latency
        
        total_samples: Number of samples collected
    """
    
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    
    total_samples: int = 0


# =============================================================================
# THROUGHPUT STATISTICS
# =============================================================================


@dataclass(frozen=True)
class ThroughputStatistics:
    """
    Statistics about request throughput.
    
    Fields:
        requests_per_second: Average RPS over window
        
        window_start:     When did the current window start?
        total_in_window:  Total requests in current window
        
        peak_rps:         Highest observed RPS
        average_rps:      Overall average RPS
    """
    
    requests_per_second: float = 0.0
    
    window_start: float = field(default_factory=time.time)
    total_in_window: int = 0
    
    peak_rps: float = 0.0
    average_rps: float = 0.0


# =============================================================================
# INTEGRATION STATISTICS
# =============================================================================


@dataclass(frozen=True)
class IntegrationStatistics:
    """
    Complete statistics for an integration.
    
    Fields:
        integration_type: Which integration is this?
        
        requests:         Request statistics
        responses:        Response statistics
        latency:          Latency statistics
        throughput:       Throughput statistics
        
        # Time window
        window_start:     When did this window start?
    """
    
    integration_type: str                   # e.g., "perception", "workspace"
    
    requests: RequestStatistics = field(default_factory=RequestStatistics)
    responses: ResponseStatistics = field(default_factory=ResponseStatistics)
    latency: LatencyStatistics = field(default_factory=LatencyStatistics)
    throughput: ThroughputStatistics = field(default_factory=ThroughputStatistics)
    
    window_start: float = field(default_factory=time.time)


# =============================================================================
# STATISTICS COLLECTOR
# =============================================================================


class IntegrationStatisticsCollector:
    """
    Collector for integration statistics.
    
    Tracks all communication metrics and provides
    aggregated statistics for monitoring and analysis.
    
    Usage:
        collector = IntegrationStatisticsCollector()
        
        # Record operations
        collector.record_request("perception", "query")
        collector.record_response("perception", success=True, latency_ms=50.0)
        
        # Get statistics
        stats = collector.get_statistics("perception")
    """
    
    def __init__(self, window_size_seconds: int = 3600):
        self._stats: Dict[str, IntegrationStatistics] = {}
        self.window_size_seconds = window_size_seconds
    
    def record_request(self, integration_type: str, 
                       consumer: Optional[str] = None,
                       request_type: Optional[str] = None) -> None:
        """Record a request."""
        if integration_type not in self._stats:
            self._init_stats(integration_type)
        
        stats = self._stats[integration_type]
        req_stats = stats.requests
        
        # Update counters
        new_req_stats = dataclass_replace(req_stats,
                                          total_requests=req_stats.total_requests + 1,
                                          last_request=time.time())
        
        if consumer:
            by_consumer = dict(new_req_stats.by_consumer)
            by_consumer[consumer] = by_consumer.get(consumer, 0) + 1
            new_req_stats = dataclass_replace(new_req_stats, by_consumer=by_consumer)
        
        if request_type:
            by_type = dict(new_req_stats.by_type)
            by_type[request_type] = by_type.get(request_type, 0) + 1
            new_req_stats = dataclass_replace(new_req_stats, by_type=by_type)
        
        self._stats[integration_type] = dataclass_replace(stats, requests=new_req_stats)
    
    def record_response(self, integration_type: str,
                        success: bool = True,
                        latency_ms: float = 0.0,
                        confidence: float = 1.0) -> None:
        """Record a response."""
        if integration_type not in self._stats:
            self._init_stats(integration_type)
        
        stats = self._stats[integration_type]
        resp_stats = stats.responses
        lat_stats = stats.latency
        
        # Update response counters
        outcome = "success" if success else "failed"
        by_outcome = dict(resp_stats.by_outcome)
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
        
        new_resp_stats = dataclass_replace(resp_stats,
                                           total_responses=resp_stats.total_responses + 1,
                                           by_outcome=by_outcome,
                                           last_response=time.time())
        
        # Update confidence
        n = resp_stats.total_responses + 1
        new_avg_conf = ((resp_stats.avg_confidence * (n - 1)) + confidence) / n
        new_resp_stats = dataclass_replace(new_resp_stats,
                                           avg_confidence=new_avg_conf,
                                           min_confidence=min(resp_stats.min_confidence, confidence),
                                           max_confidence=max(resp_stats.max_confidence, confidence))
        
        # Update latency statistics
        samples = lat_stats.total_samples + 1
        new_lat_stats = self._update_latency(lat_stats, latency_ms, samples)
        
        self._stats[integration_type] = dataclass_replace(stats,
                                                          responses=new_resp_stats,
                                                          latency=new_lat_stats)
    
    def get_statistics(self, integration_type: str) -> Optional[IntegrationStatistics]:
        """Get statistics for an integration."""
        return self._stats.get(integration_type)
    
    def get_all_statistics(self) -> Dict[str, IntegrationStatistics]:
        """Get all statistics."""
        return dict(self._stats)
    
    def _init_stats(self, integration_type: str) -> None:
        """Initialize statistics for a new integration."""
        self._stats[integration_type] = IntegrationStatistics(
            integration_type=integration_type,
            window_start=time.time()
        )
    
    def _update_latency(self, current: LatencyStatistics, 
                        new_value: float, n: int) -> LatencyStatistics:
        """Update latency statistics with a new value."""
        # Simple incremental update
        min_val = min(current.min_ms, new_value) if current.total_samples > 0 else new_value
        max_val = max(current.max_ms, new_value) if current.total_samples > 0 else new_value
        
        # For median/percentiles, we'd need to store all values
        # This is a simplified version that tracks min/max/avg
        total_sum = (current.avg_ms * current.total_samples) + new_value
        avg_val = total_sum / n if n > 0 else new_value
        
        return dataclass_replace(current,
                                 p50_ms=avg_val,  # Simplified: use average as proxy
                                 p95_ms=max_val,  # Simplified: use max as proxy
                                 p99_ms=max_val,  # Simplified
                                 min_ms=min_val,
                                 max_ms=max_val,
                                 avg_ms=avg_val,
                                 total_samples=n)


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
    )