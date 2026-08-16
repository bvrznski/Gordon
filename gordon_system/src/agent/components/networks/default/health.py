# Default Network Health
# =====================

"""
Semantic health states for the DefaultNetwork.

Health describes the semantic computational component state, not runtime liveness
or readiness. Runtime health belongs elsewhere.

PHASE 4.3.1: Semantic Health States
"""

from __future__ import annotations

from typing import Tuple, Optional


# =============================================================================
# HEALTH STATES (semantic states only)
# =============================================================================

class HealthState:
    """
    Bounded health state for the DefaultNetwork.
    
    These describe semantic computational component states, NOT runtime liveness.
    """
    
    # Network is ready to process inputs
    READY = "ready"
    
    # Network is actively processing
    ACTIVE = "active"
    
    # Network is in degraded mode (some capabilities unavailable)
    DEGRADED = "degraded"
    
    # Insufficient context for meaningful assessment
    INSUFFICIENT_CONTEXT = "insufficient_context"
    
    # Required input type not available
    INPUT_UNAVAILABLE = "input_unavailable"
    
    # Validation failed for inputs/outputs
    VALIDATION_FAILED = "validation_failed"
    
    # Operation is capacity bounded (cannot process more)
    CAPACITY_BOUNDED = "capacity_bounded"
    
    # Network encountered an error state
    FAILED = "failed"


# =============================================================================
# HEALTH CHECK RESULT
# =============================================================================

class HealthCheckResult:
    """
    Result of a health check operation.
    
    Records whether the network is healthy and why.
    """
    
    def __init__(
        self,
        is_healthy: bool,
        state: str = HealthState.READY,
        reasons: Tuple[str, ...] = (),
    ) -> None:
        """
        Initialize a health check result.
        
        Args:
            is_healthy: Whether the network is healthy
            state: The current health state
            reasons: List of reasons supporting this assessment
        """
        self._is_healthy = is_healthy
        self._state = state
        self._reasons = tuple(reasons)
    
    @property
    def is_healthy(self) -> bool:
        """Return whether the network is healthy."""
        return self._is_healthy
    
    @property
    def state(self) -> str:
        """Return the current health state."""
        return self._state
    
    @property
    def reasons(self) -> Tuple[str, ...]:
        """Return reasons for this assessment."""
        return self._reasons


# =============================================================================
# HEALTH CHECK TYPES
# =============================================================================

class HealthCheckType:
    """
    Bounded health check type classifications.
    
    Describes what aspect of the network is being checked.
    """
    
    # Basic operational status
    OPERATIONAL = "operational"
    
    # Configuration validity
    CONFIGURATION = "configuration"
    
    # Input availability and bounds
    INPUT_AVAILABILITY = "input_availability"
    
    # Output generation capability
    OUTPUT_GENERATION = "output_generation"
    
    # State consistency
    STATE_CONSISTENCY = "state_consistency"


# =============================================================================
# HEALTH CHECKER (semantic, no runtime dependencies)
# =============================================================================

class HealthChecker:
    """
    Semantic health checker for the DefaultNetwork.
    
    This performs semantic checks only - it does NOT interact with runtime
    systems like thread management or resource allocation.
    """
    
    def __init__(self) -> None:
        """Initialize the health checker."""
        self._last_check_state: str = HealthState.READY
        self._last_check_reasons: list[str] = []
    
    @property
    def last_state(self) -> str:
        """Return the state from the last check."""
        return self._last_check_state
    
    @property
    def last_reasons(self) -> Tuple[str, ...]:
        """Return the reasons from the last check."""
        return tuple(self._last_check_reasons)
    
    def check_configuration(
        self,
        config_valid: bool,
        config_error: Optional[str] = None,
    ) -> HealthCheckResult:
        """
        Check configuration health.
        
        Args:
            config_valid: Whether configuration is valid
            config_error: Optional error message if invalid
            
        Returns:
            HealthCheckResult for this check
        """
        if config_valid:
            self._last_check_state = HealthState.READY
            self._last_check_reasons = ["configuration_valid"]
            return HealthCheckResult(
                is_healthy=True,
                state=HealthState.READY,
                reasons=("configuration_valid",),
            )
        
        self._last_check_state = HealthState.FAILED
        reason = f"configuration_invalid: {config_error}" if config_error else "configuration_invalid"
        self._last_check_reasons.append(reason)
        return HealthCheckResult(
            is_healthy=False,
            state=HealthState.FAILED,
            reasons=(reason,),
        )
    
    def check_input_availability(self, has_inputs: bool) -> HealthCheckResult:
        """
        Check if inputs are available.
        
        Args:
            has_inputs: Whether input data is available
            
        Returns:
            HealthCheckResult for this check
        """
        if has_inputs:
            self._last_check_state = HealthState.READY
            self._last_check_reasons = ["inputs_available"]
            return HealthCheckResult(
                is_healthy=True,
                state=HealthState.READY,
                reasons=("inputs_available",),
            )
        
        self._last_check_state = HealthState.INPUT_UNAVAILABLE
        self._last_check_reasons.append("inputs_unavailable")
        return HealthCheckResult(
            is_healthy=False,
            state=HealthState.INPUT_UNAVAILABLE,
            reasons=("inputs_unavailable",),
        )


# =============================================================================
# HEALTH METRICS (bounded)
# =============================================================================

class HealthMetrics:
    """
    Semantic health metric definitions.
    
    These define what can be measured about the DefaultNetwork's health,
    without specifying how measurements are collected or stored.
    """
    
    # Configuration health
    CONFIG_VALID = "config_valid"
    
    # Input health
    INPUTS_AVAILABLE = "inputs_available"
    INPUT_COUNT_WITHIN_BOUNDS = "input_count_within_bounds"
    
    # Output health
    OUTPUTS_GENERATED = "outputs_generated"
    OUTPUT_COUNT_WITHIN_BOUNDS = "output_count_within_bounds"
    
    # State health
    STATE_CONSISTENT = "state_consistent"


# =============================================================================
# HEALTH BOUNDS (for validation)
# =============================================================================

class HealthBounds:
    """
    Bounds for health-related values.
    
    Ensures no health value exceeds acceptable semantic bounds.
    """
    
    # Maximum reason count (bounded for bounded diagnostics)
    MAX_REASON_COUNT: int = 50