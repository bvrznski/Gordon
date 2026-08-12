# Core Resource Reconciliation
# ============================
"""
Resource reconciliation between internal state and external reality.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import time


@dataclass(frozen=True)
class ReconciliationSource(Enum):
    """Sources for reconciliation verification."""
    INVENTORY = "inventory"           # Resource inventory
    OS = "os"                         # Operating system state
    DEVICE_ADAPTOR = "device_adaptor"
    PROCESS_TABLE = "process_table"
    NETWORK_STATE = "network_state"
    STORAGE_STATE = "storage_state"
    SERVICE_STATE = "service_state"


@dataclass(frozen=True)
class ResourceObservation:
    """
    Observation of external resource state.
    
    Used to compare against internal accounting records.
    """
    source: ReconciliationSource
    resource_id: str
    
    observed_exists: bool
    observed_state: Optional[str] = None
    observed_capacity: Optional[float] = None
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class ResourceDifference:
    """
    A difference between internal state and external observation.
    
    Indicates potential drift that needs reconciliation.
    """
    difference_id: str
    resource_id: str
    
    internal_state: Dict[str, Any]
    external_observation: Dict[str, Any]
    
    difference_type: str  # missing, extra, mismatch, stale
    
    severity: str = "warning"  # warning, critical


@dataclass(frozen=True)
class ResourceRepairAction(Enum):
    """Actions for resource reconciliation."""
    CREATE_MISSING = "create_missing"
    REMOVE_EXTRA = "remove_extra"
    UPDATE_STATE = "update_state"
    RESET_ACCOUNTING = "reset_accounting"
    QUARANTINE = "quarantine"


@dataclass(frozen=True)
class ResourceReconciliationRequest:
    """
    Request for resource reconciliation.
    
    Specifies which resources to reconcile.
    """
    runtime_id: str
    
    resource_ids: Optional[Tuple[str, ...]] = None  # If None, all resources
    sources: Tuple[ReconciliationSource, ...] = field(
        default_factory=lambda: tuple(ReconciliationSource)
    )


@dataclass(frozen=True)
class ResourceReconciliationResult:
    """
    Result of a reconciliation operation.
    
    Contains differences found and actions taken.
    """
    result_id: str
    timestamp_utc: float
    
    resources_checked: int
    differences_found: int
    actions_taken: int
    
    differences: Tuple[ResourceDifference, ...] = field(default_factory=tuple)
    actions: Tuple[str, ...] = field(default_factory=tuple)  # Action IDs
    
    success: bool = True
    partial_failure: bool = False


class ResourceReconciler:
    """
    Reconciles internal resource state with external reality.
    
    Compares inventory records against actual system state and identifies drift.
    """
    
    def __init__(self, runtime_id: str):
        self.runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Reconciliation history (bounded)
        self._history: List[ResourceReconciliationResult] = []
        self._max_history = 100
    
    def observe_external_state(
        self,
        source: ReconciliationSource,
        resource_ids: List[str]
    ) -> Dict[str, ResourceObservation]:
        """
        Observe external state for resources from a specific source.
        
        Returns mapping of resource_id to observation.
        """
        with self._lock:
            observations = {}
            
            # In real implementation, would query the external source
            for res_id in resource_ids:
                # Simulated observation - real impl would check actual system
                observations[res_id] = ResourceObservation(
                    source=source,
                    resource_id=res_id,
                    observed_exists=True,
                    observed_state="active",
                    observed_capacity=100.0,  # Example value
                    timestamp_utc=time.time(),
                )
            
            return observations
    
    def compare_with_internal(
        self,
        internal_records: Dict[str, Dict[str, Any]],
        external_observations: Dict[str, ResourceObservation]
    ) -> List[ResourceDifference]:
        """
        Compare internal records with external observations.
        
        Returns list of differences that need reconciliation.
        """
        with self._lock:
            differences = []
            
            for res_id, internal in internal_records.items():
                if res_id not in external_observations:
                    # Missing from external - could be error or deleted
                    differences.append(ResourceDifference(
                        difference_id=f"diff_{time.time():.0f}_{res_id[:8]}",
                        resource_id=res_id,
                        internal_state=internal,
                        external_observation={},
                        difference_type="missing",
                        severity="warning",
                    ))
                else:
                    # Compare states
                    external = external_observations[res_id]
                    
                    if internal.get("state") != external.observed_state:
                        differences.append(ResourceDifference(
                            difference_id=f"diff_{time.time():.0f}_{res_id[:8]}",
                            resource_id=res_id,
                            internal_state=internal,
                            external_observation={
                                "exists": external.observed_exists,
                                "state": external.observed_state,
                            },
                            difference_type="mismatch",
                            severity="critical" if external.observed_exists else "warning",
                        ))
            
            return differences
    
    def reconcile(
        self,
        resources_to_check: List[str]
    ) -> ResourceReconciliationResult:
        """
        Perform reconciliation for specified resources.
        
        Returns result with differences and any actions taken.
        """
        with self._lock:
            # Get external observations from multiple sources
            os_observations = self.observe_external_state(
                ReconciliationSource.OS,
                resources_to_check
            )
            
            inventory_observations = self.observe_external_state(
                ReconciliationSource.INVENTORY,
                resources_to_check
            )
            
            # Compare with internal records (simplified - would use actual ResourceManager)
            differences = self.compare_with_internal(
                {res_id: {"state": "active"} for res_id in resources_to_check},
                os_observations
            )
            
            # Take actions on critical differences
            actions_taken = []
            for diff in differences:
                if diff.severity == "critical":
                    actions_taken.append(f"quarantine_{diff.difference_id}")
            
            result = ResourceReconciliationResult(
                result_id=f"recon_{time.time():.0f}",
                timestamp_utc=time.time(),
                resources_checked=len(resources_to_check),
                differences_found=len(differences),
                actions_taken=len(actions_taken),
                differences=tuple(differences),
                actions=tuple(actions_taken),
                success=True,
            )
            
            self._history.append(result)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
            
            return result
    
    def get_last_reconciliation(self) -> Optional[ResourceReconciliationResult]:
        """Get the most recent reconciliation result."""
        with self._lock:
            if not self._history:
                return None
            return self._history[-1]


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "ReconciliationSource",
    "ResourceObservation",
    "ResourceDifference",
    "ResourceRepairAction",
    "ResourceReconciliationRequest",
    "ResourceReconciliationResult",
    "ResourceReconciler",
]