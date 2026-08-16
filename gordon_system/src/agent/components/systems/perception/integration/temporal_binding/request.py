# Temporal Binding Request - Phase 5.2.3
# ======================================

"""
Temporal Binding Request: Specification for temporal binding operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class TemporalBindingRequest:
    """
    Request for temporal binding.
    
    Fields:
        request_identity: Unique identifier
        candidate_artifacts: Artifact IDs to bind in time
        aligned_time_references: Time references already aligned
        binding_window: Time window for binding
        ordering_requirements: Ordering constraints
        latency_allowances: Permitted timing differences
        missing_interval_policy: How to handle gaps
    """
    
    request_identity: str
    
    candidate_artifacts: Tuple[str, ...]
    
    aligned_time_references: Dict[str, float] = field(default_factory=dict)  # artifact -> time
    binding_window: Dict[str, Any] = field(default_factory=dict)
    ordering_requirements: Dict[str, Any] = field(default_factory=dict)
    latency_allowances: Dict[str, float] = field(default_factory=dict)  # modality -> seconds
    missing_interval_policy: str = "record"  # record, infer, or reject
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        artifact_ids: List[str],
        time_window_seconds: float = 60.0,
        tolerance_seconds: float = 1.0,
        latency_allowances: Optional[Dict[str, float]] = None,
    ) -> "TemporalBindingRequest":
        """Create a temporal binding request."""
        return cls(
            request_identity=f"temporal_binding_request:{uuid.uuid4().hex[:16]}",
            candidate_artifacts=tuple(artifact_ids),
            binding_window={
                "start": time.time() - time_window_seconds,
                "end": time.time(),
                "tolerance": tolerance_seconds,
            },
            latency_allowances=latency_allowances or {},
            provenance={
                "origin": "system",
                "created_at_utc": time.time(),
            },
        )