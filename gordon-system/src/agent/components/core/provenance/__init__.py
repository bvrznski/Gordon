# Core Provenance System
# ======================
"""
Core runtime provenance tracking.

Provides:
- Artifact provenance chains (who created what, when)
- Transformation lineage for artifacts
- Source tracking and attribution

Phase 3.7: Runtime third-stage expansion - Provenance subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import time


# =============================================================================
# Artifact Types
# =============================================================================

class ArtifactType(Enum):
    """
    Types of artifacts tracked in the runtime.
    
    - ENTITY: Runtime entity instance
    - TASK: Task specification
    - DATA: Data produced/consumed by tasks
    - CONFIG: Configuration state
    - STATE: State snapshot
    - LOG: Log record
    - METRIC: Metric measurement
    """
    
    ENTITY = "entity"
    TASK = "task"
    DATA = "data"
    CONFIG = "config"
    STATE = "state"
    LOG = "log"
    METRIC = "metric"


# =============================================================================
# Provenance Record
# =============================================================================

@dataclass(frozen=True)
class ProvenanceRecord:
    """
    A provenance record for an artifact.
    
    Records who created/modified an artifact and when.
    
    Usage:
        record = ProvenanceRecord(
            artifact_id=artifact_id,
            artifact_type=ArtifactType.DATA,
            created_by=entity_id,
            timestamp=time.time()
        )
        
        # Track transformations
        transformed = record.add_transformation(
            by_entity=new_entity_id,
            transformation="aggregate",
            output_artifact=output_id
        )
    """
    
    record_id: str
    
    artifact_id: str  # The artifact being tracked
    artifact_type: ArtifactType
    
    created_by: Any  # Entity ID that created this
    timestamp: float = field(default_factory=time.time)
    
    # Transformation history (optional)
    transformation_name: Optional[str] = None  # If this is a transformed artifact
    source_artifact_ids: List[str] = field(default_factory=list)  # Original artifacts
    
    # Metadata
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_root(self) -> bool:
        """Check if this artifact was not derived from others."""
        return len(self.source_artifact_ids) == 0
    
    def add_transformation(
        self,
        by_entity: Any,
        transformation_name: str,
        output_artifact_id: str,
        timestamp: Optional[float] = None
    ) -> "ProvenanceRecord":
        """Return a new record for the transformed artifact."""
        return ProvenanceRecord(
            record_id=f"prov_{time.monotonic_ns()}",
            artifact_id=output_artifact_id,
            artifact_type=self.artifact_type,
            created_by=by_entity,
            timestamp=timestamp or time.time(),
            transformation_name=transformation_name,
            source_artifact_ids=list(self.source_artifact_ids) + [self.artifact_id],
            version=self.version + 1,
            metadata=dict(self.metadata)
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "record_id": self.record_id,
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type.value if hasattr(self.artifact_type, 'value') else str(self.artifact_type),
            "created_by": str(self.created_by) if hasattr(self.created_by, '__str__') else self.created_by,
            "timestamp": self.timestamp,
            "transformation_name": self.transformation_name,
            "source_artifact_count": len(self.source_artifact_ids),
            "version": self.version
        }


# =============================================================================
# Provenance Chain
# =============================================================================

class ProvenanceChain:
    """
    A chain of provenance records showing artifact lineage.
    
    Usage:
        chain = ProvenanceChain()
        
        # Add record
        chain.add_record(record)
        
        # Get lineage for an artifact
        lineage = chain.get_lineage(artifact_id)
        
        # Find all artifacts created by a source
        derived = chain.find_derived(source_artifact_id)
    """
    
    def __init__(self) -> None:
        self._records: Dict[str, ProvenanceRecord] = {}
        self._artifacts_by_source: Dict[str, List[str]] = {}  # source -> derived artifacts
        self._lock = __import__("threading").Lock()
    
    def add_record(self, record: ProvenanceRecord) -> None:
        """Add a provenance record."""
        with self._lock:
            self._records[record.artifact_id] = record
            
            for source_id in record.source_artifact_ids:
                if source_id not in self._artifacts_by_source:
                    self._artifacts_by_source[source_id] = []
                self._artifacts_by_source[source_id].append(record.artifact_id)
    
    def get_record(self, artifact_id: str) -> Optional[ProvenanceRecord]:
        """Get the provenance record for an artifact."""
        return self._records.get(artifact_id)
    
    def get_lineage(self, artifact_id: str) -> List[ProvenanceRecord]:
        """
        Get the full lineage of an artifact (back to root sources).
        
        Returns records from most recent back through all sources.
        """
        with self._lock:
            record = self._records.get(artifact_id)
            if not record:
                return []
            
            lineage = [record]
            
            # Recursively trace back
            def trace_back(src_id: str):
                src_record = self._records.get(src_id)
                if src_record and src_record.is_root:
                    lineage.insert(0, src_record)
                elif src_record:
                    lineage.insert(0, src_record)
                    for s in src_record.source_artifact_ids:
                        trace_back(s)
            
            for source_id in record.source_artifact_ids:
                trace_back(source_id)
            
            return lineage
    
    def find_derived(self, artifact_id: str) -> List[str]:
        """Find all artifacts derived from the given artifact."""
        with self._lock:
            result = []
            to_process = [artifact_id]
            
            while to_process:
                current = to_process.pop(0)
                
                for derived in self._artifacts_by_source.get(current, []):
                    if derived not in result:
                        result.append(derived)
                        to_process.append(derived)
            
            return result
    
    @property
    def artifact_count(self) -> int:
        """Return number of tracked artifacts."""
        with self._lock:
            return len(self._records)


# =============================================================================
# Provenance Context
# =============================================================================

@dataclass(frozen=True)
class ProvenanceContext:
    """
    Context for provenance tracking during operations.
    
    Usage:
        ctx = ProvenanceContext(
            operator_id=operator_entity_id,
            input_artifacts=input_ids
        )
        
        # Perform operation, record outputs
        output_record = ctx.record_output(
            artifact_type=ArtifactType.DATA,
            artifact_id=output_id
        )
    """
    
    operator_id: Any  # Entity performing the operation
    
    input_artifact_ids: List[str] = field(default_factory=list)
    
    timestamp: float = field(default_factory=time.time)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def record_output(
        self,
        artifact_id: str,
        artifact_type: ArtifactType
    ) -> ProvenanceRecord:
        """Create a provenance record for an output artifact."""
        return ProvenanceRecord(
            record_id=f"prov_{time.monotonic_ns()}",
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            created_by=self.operator_id,
            timestamp=self.timestamp,
            source_artifact_ids=list(self.input_artifact_ids),
            metadata=dict(self.metadata)
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "operator_id": str(self.operator_id) if hasattr(self.operator_id, '__str__') else self.operator_id,
            "input_artifact_count": len(self.input_artifact_ids),
            "timestamp": self.timestamp
        }


__all__ = [
    # Artifact types
    "ArtifactType",
    
    # Records and chains
    "ProvenanceRecord",
    "ProvenanceChain",
    
    # Context
    "ProvenanceContext",
]