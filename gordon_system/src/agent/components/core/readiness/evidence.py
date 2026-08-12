# Readiness Evidence Collection and Aggregation
# ===============================================

"""
Evidence collection and aggregation for readiness evaluation.

This module provides:
- Evidence collection from subsystems (health, integrity, resources)
- Deterministic evidence aggregation
- Evidence freshness validation
- Evidence provenance tracking

Readiness evidence is contributed by subsystems but does NOT determine readiness.
The ReadinessController aggregates evidence and makes the final decision.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
import time


# =============================================================================
# EVIDENCE SOURCE TYPES
# =============================================================================

class EvidenceSource(Enum):
    """Sources of readiness evidence."""
    HEALTH = "health"                 # Health check results
    INTEGRITY = "integrity"           # Integrity validation results
    CONFIGURATION = "configuration"   # Configuration state
    RESOURCES = "resources"           # Resource availability
    CAPABILITIES = "capabilities"     # Capability availability
    DEPENDENCIES = "dependencies"     # Dependency status
    ACTIVATION = "activation"         # Activation state


# =============================================================================
# EVIDENCE COLLECTOR
# =============================================================================

@dataclass(frozen=True)
class EvidenceCollectorConfig:
    """Configuration for evidence collection."""
    max_evidence_age_seconds: float = 30.0
    required_evidence_sources: Tuple[str, ...] = field(default_factory=tuple)
    optional_evidence_sources: Tuple[str, ...] = field(default_factory=tuple)


class EvidenceCollector:
    """
    Collects and validates evidence from subsystems.
    
    This is a contribution module - it does NOT determine readiness!
    It only collects, validates, and reports evidence to the ReadinessController.
    """
    
    def __init__(self, config: Optional[EvidenceCollectorConfig] = None):
        self._config = config or EvidenceCollectorConfig()
        self._evidence_store: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = time.monotonic  # Placeholder for actual locking
    
    def add_health_evidence(
        self,
        subsystem_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add health evidence from a subsystem."""
        evidence = {
            "source": EvidenceSource.HEALTH.value,
            "subsystem_id": subsystem_id,
            "status": status,
            "details": details or {},
            "collected_at_utc": time.time(),
            "monotonic_time": time.monotonic()
        }
        
        if EvidenceSource.HEALTH.value not in self._evidence_store:
            self._evidence_store[EvidenceSource.HEALTH.value] = []
        self._evidence_store[EvidenceSource.HEALTH.value].append(evidence)
    
    def add_integrity_evidence(
        self,
        subsystem_id: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add integrity evidence from a subsystem."""
        evidence = {
            "source": EvidenceSource.INTEGRITY.value,
            "subsystem_id": subsystem_id,
            "status": status,
            "details": details or {},
            "collected_at_utc": time.time(),
            "monotonic_time": time.monotonic()
        }
        
        if EvidenceSource.INTEGRITY.value not in self._evidence_store:
            self._evidence_store[EvidenceSource.INTEGRITY.value] = []
        self._evidence_store[EvidenceSource.INTEGRITY.value].append(evidence)
    
    def add_resource_evidence(
        self,
        resource_id: str,
        available: bool,
        quantity: Optional[float] = None
    ) -> None:
        """Add resource evidence."""
        evidence = {
            "source": EvidenceSource.RESOURCES.value,
            "resource_id": resource_id,
            "available": available,
            "quantity": quantity,
            "collected_at_utc": time.time(),
            "monotonic_time": time.monotonic()
        }
        
        if EvidenceSource.RESOURCES.value not in self._evidence_store:
            self._evidence_store[EvidenceSource.RESOURCES.value] = []
        self._evidence_store[EvidenceSource.RESOURCES.value].append(evidence)
    
    def is_evidence_valid(self, evidence_item: Dict[str, Any]) -> bool:
        """Check if an evidence item is still fresh."""
        age = time.monotonic() - evidence_item.get("monotonic_time", 0)
        return age <= self._config.max_evidence_age_seconds
    
    def get_all_evidence(
        self,
        source_filter: Optional[EvidenceSource] = None
    ) -> List[Dict[str, Any]]:
        """Get all collected evidence."""
        result = []
        for source_name, items in self._evidence_store.items():
            if source_filter is None or EvidenceSource(source_name) == source_filter:
                result.extend(items)
        return result
    
    def get_health_summary(self) -> Dict[str, str]:
        """Get summary of health evidence."""
        health_items = self._evidence_store.get(EvidenceSource.HEALTH.value, [])
        
        statuses: Dict[str, int] = {}
        for item in health_items:
            if self.is_evidence_valid(item):
                status = item.get("status", "unknown")
                statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_checked": len(health_items),
            "by_status": statuses,
        }
    
    def clear(self) -> None:
        """Clear all collected evidence."""
        self._evidence_store.clear()