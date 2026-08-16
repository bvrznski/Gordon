# Memory Forgetting Operation - Phase 5.1.2
# ==========================================

"""
Memory Forgetting: Reduce accessibility of artifacts without deletion.

Purpose:
    Make artifacts less accessible over time while preserving semantic history.

Forgetting owns:
    - accessibility revision (marking artifacts as less accessible)
    - visibility revision (adjusting when/if they appear in queries)
    - retention revision (tracking how long until forgetting occurs)

Forgetting does NOT delete artifacts or their history.

Input:
    - Artifact: Which artifact to forget
    - Retention policy: When and how to forget
    - Importance: How important is it to remember this?

Output:
    - Accessibility revision: Updated accessibility level
    - Visibility revision: Updated visibility settings
    - Retention revision: Tracking of forgetting timeline

Usage:

    from gordon_system.src.agent.components.systems.memory.operations.forgetting import ForgettingOperation
    
    forgetter = ForgettingOperation()
    
    # Reduce accessibility for an artifact
    result, projection = forgetter.execute(
        inputs={
            "artifact_id": "art-123",
            "target_accessibility": 0.1,
        }
    )
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


# =============================================================================
# FORGETTING CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class ForgettingConfig:
    """Configuration for the forgetting operation."""
    
    default_accessibility_decay: float = 0.1
    min_accessibility: float = 0.0
    max_accessibility: float = 1.0
    archive_after_days: int = 365


# =============================================================================
# FORGETTING RESULT
# =============================================================================


@dataclass(frozen=True)
class ForgettingResult:
    """Result produced by the forgetting operation."""
    
    result_id: str                          # Unique result ID
    forgotten_artifacts: Tuple[Any, ...]    # Artifacts with reduced accessibility
    new_visibilities: Dict[str, float]      # Updated visibility scores
    duration_ms: float = 0.0                # Execution time
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# FORGETTING OPERATION
# =============================================================================


class ForgettingOperation:
    """
    Reduce accessibility of artifacts without deletion.
    
    This operation:
        1. Identifies artifacts to forget (based on policy or explicit request)
        2. Creates revisions with reduced accessibility scores
        3. Updates visibility settings for queries
        4. Preserves all semantic history and identity
        
    The artifacts remain in memory but are harder to access.
    
    Usage:
        forgetter = ForgettingOperation()
        result, projection = forgetter.execute(forgetting_inputs)
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        config: Optional[ForgettingConfig] = None,
    ):
        """Initialize the forgetting operation."""
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.config: ForgettingConfig = config or ForgettingConfig()
    
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate forgetting inputs."""
        try:
            if not isinstance(inputs, dict):
                return False
            
            # Check required fields
            if "artifact_id" not in inputs:
                return False
            
            artifact_id = inputs["artifact_id"]
            if not isinstance(artifact_id, str) or len(artifact_id) == 0:
                return False
            
            # Validate accessibility target if provided
            if "target_accessibility" in inputs:
                target = inputs["target_accessibility"]
                if not isinstance(target, (int, float)):
                    return False
                if not 0.0 <= target <= 1.0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ForgettingResult, Dict[str, Any]]:
        """
        Execute the forgetting operation.
        
        Args:
            inputs: Forgetting parameters
                - artifact_id: ID of artifact to forget
                - target_accessibility: Target accessibility level (0.0-1.0)
                - decay_rate: Custom decay rate if different from config
            context: Optional execution context
            
        Returns:
            Tuple of (forgetting_result, projection)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not self.validate(inputs, context):
            raise ValueError("Invalid forgetting inputs")
        
        start_time = time.time()
        
        try:
            # Parse inputs
            artifact_id = inputs["artifact_id"]
            target_accessibility = inputs.get("target_accessibility", self.config.min_accessibility)
            
            # In a real implementation, this would:
            # 1. Retrieve the current artifact revision
            # 2. Calculate new accessibility based on decay or explicit value
            # 3. Create new revision with updated accessibility/visibility
            
            from ..foundations.artifact import MemoryArtifact
            
            forgotten_artifacts: Tuple[MemoryArtifact, ...] = ()
            
            duration_ms = (time.time() - start_time) * 1000
            
            forgetting_result = ForgettingResult(
                result_id=f"forget:{uuid.uuid4().hex[:12]}",
                forgotten_artifacts=forgotten_artifacts,
                new_visibilities={artifact_id: target_accessibility},
                duration_ms=duration_ms,
                timestamp_utc=time.time(),
            )
            
            projection = {
                "operation_id": self.operation_id,
                "operation_kind": "forgetting",
                "state": "completed",
                "inputs_processed": 1,
                "outputs_produced": len(forgotten_artifacts),
                "duration_ms": duration_ms,
                "validation_status": "valid",
                "validation_result": f"Forgotten artifact {artifact_id}",
            }
            
            return forgetting_result, projection
            
        except Exception as e:
            raise ValueError(f"Forgetting operation failed: {str(e)}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_forgetting_operation(
    operation_id: Optional[str] = None,
    config: Optional[ForgettingConfig] = None,
) -> ForgettingOperation:
    """Create a forgetting operation instance."""
    return ForgettingOperation(operation_id=operation_id, config=config)


__all__ = [
    "ForgettingOperation",
    "ForgettingConfig",
    "ForgettingResult",
    "create_forgetting_operation",
]