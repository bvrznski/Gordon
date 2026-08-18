# Diagnostic Descriptor - Phase 7.39
# ==================================

"""
Canonical Diagnostic Descriptor.

A diagnostic descriptor exposes diagnostic metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class DiagnosticMode(Enum):
    """Diagnostic reasoning modes."""
    
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"  # Identify root cause
    FAILURE_EXPLANATION = "failure_explanation"   # Explain observed failure
    ANOMALY_CLASSIFICATION = "anomaly_classification"  # Classify anomaly type
    RECOVERY_HYPOTHESIS = "recovery_hypothesis"   # Generate recovery options
    PROPAGATION_ANALYSIS = "propagation_analysis"  # Analyze failure spread


class DiagnosticLifecycle(Enum):
    """Diagnostic session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    LOCALIZING = "localizing"
    EXPLAINING = "explaining"
    VALIDATING = "validating"
    RANKING = "ranking"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class DiagnosticSessionIdentity:
    """
    Immutable identity for a diagnostic session.
    
    Provides persistent semantic identity across multiple runs.
    """
    
    # Primary identifiers
    session_id: str              # Unique session instance ID
    semantic_identity: str       # Stable semantic identity (same diagnosis = same identity)
    
    # Context
    context_hash: str           # Hash of observation context for replay verification
    diagnostic_mode: DiagnosticMode
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        diagnostic_mode: DiagnosticMode,
        context_hash: Optional[str] = None,
    ) -> DiagnosticSessionIdentity:
        """Create a new diagnostic session identity."""
        return cls(
            session_id=f"session:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            context_hash=context_hash or uuid.uuid4().hex[:16],
            diagnostic_mode=diagnostic_mode,
        )


@dataclass(frozen=True)
class DiagnosticDescriptor:
    """
    Descriptor exposing diagnostic metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Diagnostic mode and reasoning strategy
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what diagnostics occurred without
    needing to execute the full diagnostic process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Diagnostic classification
    diagnostic_mode: DiagnosticMode         # What kind of diagnostic?
    reasoning_strategy: Optional[str] = None  # Strategy details
    
    # Lifecycle state
    lifecycle_state: DiagnosticLifecycle = DiagnosticLifecycle.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Constraints and scope
    system_scope: str = "global"            # Scope of diagnostic
    observation_constraints: List[str] = field(default_factory=list)  # Constraints on observations
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did diagnostic originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if diagnostic completed."""
        return self.lifecycle_state == DiagnosticLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if diagnostic failed."""
        return self.lifecycle_state == DiagnosticLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        diagnostic_mode: DiagnosticMode,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        system_scope: str = "global",
        reasoning_strategy: Optional[str] = None,
    ) -> DiagnosticDescriptor:
        """Create a new diagnostic descriptor."""
        return cls(
            descriptor_id=f"descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            diagnostic_mode=diagnostic_mode,
            reasoning_strategy=reasoning_strategy,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            system_scope=system_scope,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: DiagnosticLifecycle) -> DiagnosticDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == DiagnosticLifecycle.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DiagnosticDescriptor",
    "DiagnosticSessionIdentity",
    "DiagnosticMode",
    "DiagnosticLifecycle",
]