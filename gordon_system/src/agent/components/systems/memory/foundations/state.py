# Memory State - Phase 5.1 Canonical Substrate Summary
# ====================================================

"""
Memory State: Summary of the entire memory substrate.

The Memory System exposes:
    - MemoryState (substrate summary)
    - MemoryHealth (architectural health)
    - MemoryStatistics (metrics and counts)

Never exposes:
    - The substrate itself (internal representation is private)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import time


# =============================================================================
# MEMORY HEALTH STATES
# =============================================================================


class MemoryHealth(Enum):
    """
    Health status of the memory substrate.
    
    | State           | Description                                        |
    |-----------------|---------------------------------------------------|
    | CONFIGURED      | Configured but not initialized                     |
    | INITIALIZED     | Initialized but not ready                          |
    | READY           | Ready for operations                               |
    | OPERATIONAL     | Fully operational                                  |
    | DEGRADED        | Some functionality unavailable                     |
    | MAINTENANCE     | In maintenance mode                                |
    | FAILED          | Infrastructure failure                             |
    """
    
    CONFIGURED = "configured"
    INITIALIZED = "initialized"
    READY = "ready"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


# =============================================================================
# MEMORY STATISTICS - Metrics and counts
# =============================================================================


@dataclass(frozen=True)
class MemoryStatistics:
    """
    Statistics about the memory substrate.
    
    These are observational metrics, NOT semantic authority. They summarize
    what's in the substrate but don't define it.
    
    Fields:
        artifact_count:      Total artifacts in substrate
        
        relation_count:      Total relations between artifacts
        cluster_count:       Number of clusters
        
        revision_count:      Total revisions tracked
        average_connectivity: Average relations per artifact
        
        integrity:           Integrity score (0.0-1.0)
        
        # Timeline stats
        first_artifact_time: Timestamp of oldest artifact
        last_artifact_time:  Timestamp of newest artifact
        
        # Storage stats (implementation detail, exposed for observability)
        storage_size_bytes:  Approximate storage size
    """
    
    artifact_count: int = 0
    
    relation_count: int = 0
    cluster_count: int = 0
    
    revision_count: int = 0
    average_connectivity: float = 0.0
    
    integrity: float = 1.0  # 0.0-1.0
    
    first_artifact_time: Optional[float] = None
    last_artifact_time: Optional[float] = None
    
    storage_size_bytes: int = 0


# =============================================================================
# MEMORY DIAGNOSTICS - Diagnostic findings
# =============================================================================


@dataclass(frozen=True)
class MemoryDiagnostic:
    """
    Diagnostic findings about the memory substrate.
    
    Diagnostics remain observational - they don't modify memory.
    
    Fields:
        diagnostic_id:       Unique ID for this diagnostic
        
        # Findings
        finding_type:        Type of finding (integrity, consistency, etc.)
        severity:            0.0-1.0 severity level
        description:         Detailed description
        
        affected_artifacts:  Artifact IDs affected by this finding
        
        recommendations:     Suggested actions
        confidence:          Belief in diagnostic accuracy
        
        timestamp_utc:       When diagnostic was generated
    """
    
    diagnostic_id: str
    
    finding_type: str           # integrity, consistency, orphan, etc.
    severity: float = 0.0       # 0.0-1.0
    description: Optional[str] = None
    
    affected_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0     # 0.0-1.0
    
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# MEMORY STATE - Substrate summary
# =============================================================================


@dataclass(frozen=True)
class MemoryState:
    """
    Summary of the memory substrate state.
    
    This provides a high-level view without exposing internal representation.
    
    Fields:
        substrate_revision:   Version of substrate schema
        
        # Counts (from statistics)
        artifact_count:       Total artifacts
        relation_count:       Total relations
        
        # Health
        health_status:        MemoryHealth status
        integrity:            Substrate integrity (0.0-1.0)
        
        # Statistics
        revision_count:       Total revisions tracked
        cluster_count:        Number of clusters
    """
    
    substrate_revision: int = 1
    
    # Counts
    artifact_count: int = 0
    relation_count: int = 0
    
    # Health
    health_status: MemoryHealth = MemoryHealth.CONFIGURED
    integrity: float = 1.0  # 0.0-1.0
    
    # Statistics
    revision_count: int = 0
    cluster_count: int = 0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace_state(instance: MemoryState, **kwargs) -> MemoryState:
    """Replace fields in a frozen MemoryState."""
    return MemoryState(
        substrate_revision=kwargs.get("substrate_revision", instance.substrate_revision),
        artifact_count=kwargs.get("artifact_count", instance.artifact_count),
        relation_count=kwargs.get("relation_count", instance.relation_count),
        health_status=kwargs.get("health_status", instance.health_status),
        integrity=kwargs.get("integrity", instance.integrity),
        revision_count=kwargs.get("revision_count", instance.revision_count),
        cluster_count=kwargs.get("cluster_count", instance.cluster_count),
    )


def dataclass_replace_stats(instance: MemoryStatistics, **kwargs) -> MemoryStatistics:
    """Replace fields in a frozen MemoryStatistics."""
    return MemoryStatistics(
        artifact_count=kwargs.get("artifact_count", instance.artifact_count),
        relation_count=kwargs.get("relation_count", instance.relation_count),
        cluster_count=kwargs.get("cluster_count", instance.cluster_count),
        revision_count=kwargs.get("revision_count", instance.revision_count),
        average_connectivity=kwargs.get("average_connectivity", instance.average_connectivity),
        integrity=kwargs.get("integrity", instance.integrity),
        first_artifact_time=kwargs.get("first_artifact_time", instance.first_artifact_time),
        last_artifact_time=kwargs.get("last_artifact_time", instance.last_artifact_time),
        storage_size_bytes=kwargs.get("storage_size_bytes", instance.storage_size_bytes),
    )


def dataclass_replace_diagnostics(instance: MemoryDiagnostic, **kwargs) -> MemoryDiagnostic:
    """Replace fields in a frozen MemoryDiagnostic."""
    return MemoryDiagnostic(
        diagnostic_id=instance.diagnostic_id,
        finding_type=kwargs.get("finding_type", instance.finding_type),
        severity=kwargs.get("severity", instance.severity),
        description=kwargs.get("description", instance.description),
        affected_artifacts=kwargs.get("affected_artifacts", instance.affected_artifacts),
        recommendations=kwargs.get("recommendations", instance.recommendations),
        confidence=kwargs.get("confidence", instance.confidence),
        timestamp_utc=kwargs.get("timestamp_utc", instance.timestamp_utc),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryState",
    "MemoryHealth",
    "MemoryStatistics",
    "MemoryDiagnostic",
    "dataclass_replace_state",
    "dataclass_replace_stats",
    "dataclass_replace_diagnostics",
]