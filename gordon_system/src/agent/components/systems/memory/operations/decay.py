# Memory Decay Operation - Phase 5.1.2
# =====================================

"""
Memory Decay: Model gradual weakening of activation/accessibility over time.

Purpose:
    Simulate natural forgetting through temporal decay of activation levels.

Decay owns:
    - activation revision (decreasing activation over time)
    - priority revision (adjusting retrieval priority)
    - accessibility revision (reducing likelihood of recall)

Decay preserves identity and semantic history at all times.

Input:
    - Artifact: Which artifact to apply decay to
    - Activation history: Historical activation levels
    - Time model: How time affects decay

Output:
    - Activation revision: New, lower activation level
    - Priority revision: Updated priority for retrieval
    - Accessibility revision: Lower recall probability

Usage:

    from gordon_system.src.agent.components.systems.memory.operations.decay import DecayOperation
    
    decayer = DecayOperation()
    
    # Apply decay to an artifact based on time elapsed
    result, projection = decayer.execute(
        inputs={
            "artifact_id": "art-123",
            "current_activation": 0.8,
            "time_elapsed_seconds": 86400,  # 24 hours
        }
    )
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# DECAY CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class DecayConfig:
    """Configuration for the decay operation."""
    
    half_life_seconds: float = 86400.0  # Activation halves every 24 hours
    min_activation: float = 0.01      # Floor for activation levels
    decay_rate_per_second: float = 0.000007  # Alternative parametrization


# =============================================================================
# DECAY RESULT
# =============================================================================


@dataclass(frozen=True)
class DecayResult:
    """Result produced by the decay operation."""
    
    result_id: str                          # Unique result ID
    artifacts_affected: Tuple[str, ...]     # IDs of affected artifacts
    activation_before: Dict[str, float]
    activation_after: Dict[str, float]
    duration_ms: float = 0.0                # Execution time
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# DECAY OPERATION
# =============================================================================


class DecayOperation:
    """
    Model gradual weakening of activation/accessibility over time.
    
    This operation implements temporal decay as a natural forgetting mechanism:
        - Activation decreases exponentially over time
        - Half-life determines the rate of decay
        - Lower activation means lower retrieval probability
        
    The artifact identity and semantic content remain unchanged.
    
    Usage:
        decayer = DecayOperation()
        result, projection = decayer.execute(decay_inputs)
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        config: Optional[DecayConfig] = None,
    ):
        """Initialize the decay operation."""
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.config: DecayConfig = config or DecayConfig()
    
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate decay inputs."""
        try:
            if not isinstance(inputs, dict):
                return False
            
            # Check required fields
            if "artifact_id" not in inputs or "current_activation" not in inputs:
                return False
            
            artifact_id = inputs["artifact_id"]
            if not isinstance(artifact_id, str) or len(artifact_id) == 0:
                return False
            
            current_activation = inputs["current_activation"]
            if not isinstance(current_activation, (int, float)):
                return False
            if not 0.0 <= current_activation <= 1.0:
                return False
            
            # Validate time elapsed if provided
            if "time_elapsed_seconds" in inputs:
                elapsed = inputs["time_elapsed_seconds"]
                if not isinstance(elapsed, (int, float)) or elapsed < 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[DecayResult, Dict[str, Any]]:
        """
        Execute the decay operation.
        
        Args:
            inputs: Decay parameters
                - artifact_id: ID of artifact to decay
                - current_activation: Current activation level (0.0-1.0)
                - time_elapsed_seconds: Time since last activation (optional)
            context: Optional execution context
            
        Returns:
            Tuple of (decay_result, projection)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not self.validate(inputs, context):
            raise ValueError("Invalid decay inputs")
        
        start_time = time.time()
        
        try:
            # Parse inputs
            artifact_id = inputs["artifact_id"]
            current_activation = float(inputs["current_activation"])
            
            # Calculate elapsed time (use system time if not provided)
            elapsed_seconds = float(inputs.get("time_elapsed_seconds", 0.0))
            
            # Apply exponential decay: A_new = A_current * e^(-lambda * t)
            # where lambda is the decay rate
            decay_factor = self.config.decay_rate_per_second
            
            activation_after_decay = current_activation * (
                2 ** (-elapsed_seconds / self.config.half_life_seconds)
            )
            
            # Ensure minimum activation floor
            activation_after_decay = max(
                self.config.min_activation,
                activation_after_decay
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            decay_result = DecayResult(
                result_id=f"decay:{uuid.uuid4().hex[:12]}",
                artifacts_affected=(artifact_id,),
                activation_before={artifact_id: current_activation},
                activation_after={artifact_id: activation_after_decay},
                duration_ms=duration_ms,
                timestamp_utc=time.time(),
            )
            
            projection = {
                "operation_id": self.operation_id,
                "operation_kind": "decay",
                "state": "completed",
                "inputs_processed": 1,
                "outputs_produced": 1,
                "duration_ms": duration_ms,
                "validation_status": "valid",
                "validation_result": f"Decayed activation from {current_activation:.4f} to {activation_after_decay:.4f}",
            }
            
            return decay_result, projection
            
        except Exception as e:
            raise ValueError(f"Decay operation failed: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_decay_operation(
    operation_id: Optional[str] = None,
    config: Optional[DecayConfig] = None,
) -> DecayOperation:
    """Create a decay operation instance."""
    return DecayOperation(operation_id=operation_id, config=config)


__all__ = [
    "DecayOperation",
    "DecayConfig",
    "DecayResult",
    "create_decay_operation",
]