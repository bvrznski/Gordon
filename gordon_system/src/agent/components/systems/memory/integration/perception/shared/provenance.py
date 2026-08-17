# Provenance - Cross-System Traceability
# ========================================

"""
Provenance: Complete traceability of cross-system operations.

Every artifact in Memory-Perception Integration shall preserve complete provenance
that permits bidirectional traversal:
    - From result back to source artifacts
    - From source artifacts through integration to results
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROVENANCE KINDS
# =============================================================================


class ProvenanceKind(Enum):
    """
    Kinds of provenance operations.
    
    Every cross-system operation shall have an explicit provenance kind that
    describes what transformation occurred.
    """
    
    # Source types
    PERCEPTION_SOURCE = "perception_source"           # Original perception artifact
    MEMORY_SOURCE = "memory_source"                   # Original memory artifact
    
    # Integration operations
    ADMISSION_PREPARATION = "admission_preparation"   # Prepared for Memory admission
    RECOGNITION_MATCHING = "recognition_matching"     # Recognition comparison
    RECOLLECTION_RETRIEVAL = "recollection_retrieval"  # Recollection query result
    CONTEXTUALIZATION = "contextualization"           # Context enrichment
    EXPECTATION_GENERATION = "expectation_generation"  # Generated expectation
    MISMATCH_CLASSIFICATION = "mismatch_classification"  # Classified mismatch
    CONTINUITY_ANALYSIS = "continuity_analysis"       # Continuity evaluation
    TEMPORAL_CORRESPONDENCE = "temporal_correspondence"  # Time alignment
    SPATIAL_CORRESPONDENCE = "spatial_correspondence"   # Space alignment
    IDENTITY_CORRESPONDENCE = "identity_correspondence"  # Identity match
    
    # Metadata operations
    VALIDATION = "validation"                         # Validation operation
    SYNCHRONIZATION = "synchronization"               # Revision sync


# =============================================================================
# PROVENANCE SOURCE - Where did something come from?
# =============================================================================


@dataclass(frozen=True)
class ProvenanceSource:
    """
    Source of information in a cross-system artifact.
    
    Every piece of data shall have an explicit source that can be traced
    back to its origin.
    """
    
    # Identity
    source_identity: str                    # Unique ID for this source
    
    # Type of source
    source_type: str                        # "perception", "memory", "inference"
    
    # Location
    source_location: Optional[str] = None   # Artifact ID or other reference
    
    # Trust metrics
    confidence: float = 1.0                 # Belief in this source
    uncertainty: float = 0.0                # Uncertainty about this source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_identity": self.source_identity,
            "source_type": self.source_type,
            "source_location": self.source_location,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
        }


# =============================================================================
# PROVENANCE TRANSFORMATION - What happened during integration?
# =============================================================================


@dataclass(frozen=True)
class ProvenanceTransformation:
    """
    A transformation step in the cross-system processing chain.
    
    Every integration operation shall record its transformations for auditability.
    """
    
    # Identity
    transformation_identity: str            # Unique ID
    
    # Operation details
    kind: ProvenanceKind                    # What kind of transformation?
    
    # Input references
    input_artifact_ids: Tuple[str, ...]     # Source artifacts
    
    # Output references  
    output_artifact_ids: Tuple[str, ...]    # Result artifacts
    
    # Timestamps
    start_time_utc: float                   # When operation started
    end_time_utc: Optional[float] = None    # When operation completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transformation_identity": self.transformation_identity,
            "kind": self.kind.value,
            "input_artifact_ids": list(self.input_artifact_ids),
            "output_artifact_ids": list(self.output_artifact_ids),
            "start_time_utc": self.start_time_utc,
            "end_time_utc": self.end_time_utc,
        }


# =============================================================================
# PROVENANCE CHAIN - Complete trace through integration
# =============================================================================


@dataclass(frozen=True)
class ProvenanceChain:
    """
    Complete provenance chain from source to result.
    
    Every cross-system artifact shall have a provenance chain that permits
    bidirectional traversal of the processing pipeline.
    """
    
    # Identity
    provenance_identity: str                # Unique ID for this provenance record
    
    # Source artifacts (original, before integration)
    source_artifact_ids: Tuple[str, ...]
    
    # Source types (perception vs memory)
    source_types: Tuple[str, ...]           # "perception" or "memory" per artifact
    
    # Integration operations
    transformations: Tuple[ProvenanceTransformation, ...]
    
    # Result artifacts (after integration)
    result_artifact_ids: Tuple[str, ...]
    
    # Processing metadata
    processing_identity: str                # Which integration engine?
    processing_version: str = "1.0.0"
    
    @property
    def source_chain(self) -> List[Dict[str, Any]]:
        """Return traceable path from sources to results."""
        chain = []
        
        for i, source_id in enumerate(self.source_artifact_ids):
            chain.append({
                "type": self.source_types[i],
                "artifact_id": source_id,
                "stage": "source",
            })
        
        for transformation in self.transformations:
            chain.append({
                "type": "transformation",
                "kind": transformation.kind.value,
                "input_artifacts": list(transformation.input_artifact_ids),
                "output_artifacts": list(transformation.output_artifact_ids),
                "stage": "integration",
            })
        
        for result_id in self.result_artifact_ids:
            chain.append({
                "type": "result",
                "artifact_id": result_id,
                "stage": "result",
            })
        
        return chain
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provenance_identity": self.provenance_identity,
            "source_artifact_ids": list(self.source_artifact_ids),
            "source_types": list(self.source_types),
            "transformations": [t.to_dict() for t in self.transformations],
            "result_artifact_ids": list(self.result_artifact_ids),
            "processing_identity": self.processing_identity,
            "processing_version": self.processing_version,
        }
    
    @classmethod
    def create_admission_provenance(
        cls,
        source_projection_id: str,
        candidate_id: str,
    ) -> "ProvenanceChain":
        """Create provenance for observation admission preparation."""
        now = time.time()
        
        transformation = ProvenanceTransformation(
            transformation_identity=f"transform:admission:{uuid.uuid4().hex[:16]}",
            kind=ProvenanceKind.ADMISSION_PREPARATION,
            input_artifact_ids=(source_projection_id,),
            output_artifact_ids=(candidate_id,),
            start_time_utc=now,
        )
        
        return cls(
            provenance_identity=f"provenance:admission:{uuid.uuid4().hex[:16]}",
            source_artifact_ids=(source_projection_id,),
            source_types=("perception",),
            transformations=(transformation,),
            result_artifact_ids=(candidate_id,),
            processing_identity="integration:admission",
        )
    
    @classmethod
    def create_recognition_provenance(
        cls,
        perception_artifact_id: str,
        memory_artifact_id: str,
        recognition_result_id: str,
    ) -> "ProvenanceChain":
        """Create provenance for recognition operation."""
        now = time.time()
        
        transformation = ProvenanceTransformation(
            transformation_identity=f"transform:recognition:{uuid.uuid4().hex[:16]}",
            kind=ProvenanceKind.RECOGNITION_MATCHING,
            input_artifact_ids=(perception_artifact_id, memory_artifact_id),
            output_artifact_ids=(recognition_result_id,),
            start_time_utc=now,
        )
        
        return cls(
            provenance_identity=f"provenance:recognition:{uuid.uuid4().hex[:16]}",
            source_artifact_ids=(perception_artifact_id, memory_artifact_id),
            source_types=("perception", "memory"),
            transformations=(transformation,),
            result_artifact_ids=(recognition_result_id,),
            processing_identity="integration:recognition",
        )
    
    @classmethod
    def create_recollection_provenance(
        cls,
        trigger_id: str,
        memory_artifact_ids: Tuple[str, ...],
        recollection_context_id: str,
    ) -> "ProvenanceChain":
        """Create provenance for recollection operation."""
        now = time.time()
        
        transformation = ProvenanceTransformation(
            transformation_identity=f"transform:recollection:{uuid.uuid4().hex[:16]}",
            kind=ProvenanceKind.RECOLLECTION_RETRIEVAL,
            input_artifact_ids=(trigger_id,) + memory_artifact_ids,
            output_artifact_ids=(recollection_context_id,),
            start_time_utc=now,
        )
        
        return cls(
            provenance_identity=f"provenance:recollection:{uuid.uuid4().hex[:16]}",
            source_artifact_ids=(trigger_id,) + memory_artifact_ids,
            source_types=("perception",) + ("memory",) * len(memory_artifact_ids),
            transformations=(transformation,),
            result_artifact_ids=(recollection_context_id,),
            processing_identity="integration:recollection",
        )


# =============================================================================
# PROVENANCE VALIDATOR
# =============================================================================


class ProvenanceValidator:
    """
    Validates provenance chains for integrity.
    
    Ensures that:
        - Every transformation has valid inputs and outputs
        - Source artifacts are properly labeled
        - Processing identity is preserved through all steps
        - No circular references exist in the chain
    """
    
    @staticmethod
    def validate_chain(chain: ProvenanceChain) -> Tuple[bool, List[str]]:
        """
        Validate a provenance chain.
        
        Args:
            chain: The provenance chain to validate
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Rule 1: At least one source artifact
        if len(chain.source_artifact_ids) == 0:
            errors.append("Provenance chain has no source artifacts")
        
        # Rule 2: Source types must match source count
        if len(chain.source_types) != len(chain.source_artifact_ids):
            errors.append(
                f"Source type count ({len(chain.source_types)}) doesn't match "
                f"source artifact count ({len(chain.source_artifact_ids)})"
            )
        
        # Rule 3: Every transformation must have inputs and outputs
        for i, t in enumerate(chain.transformations):
            if len(t.input_artifact_ids) == 0:
                errors.append(f"Transformation {i} has no input artifacts")
            if len(t.output_artifact_ids) == 0:
                errors.append(f"Transformation {i} has no output artifacts")
        
        # Rule 4: Check for circular references
        all_ids = set(chain.source_artifact_ids)
        seen_ids = set()
        for t in chain.transformations:
            for inp in t.input_artifact_ids:
                if inp in seen_ids and inp not in all_ids:
                    errors.append(f"Circular reference detected at {inp}")
                seen_ids.add(inp)
            for outp in t.output_artifact_ids:
                all_ids.add(outp)
        
        # Rule 5: Result artifacts must be from last transformation
        if len(chain.transformations) > 0:
            last_trans = chain.transformations[-1]
            result_set = set(chain.result_artifact_ids)
            output_set = set(last_trans.output_artifact_ids)
            
            if not result_set.issubset(output_set):
                errors.append("Result artifacts not produced by last transformation")
        
        return len(errors) == 0, errors


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_provenance_chain(
    source_artifacts: Tuple[str, ...],
    source_types: Tuple[str, ...],
    transformations: Tuple[ProvenanceTransformation, ...],
    result_artifacts: Tuple[str, ...],
) -> ProvenanceChain:
    """
    Create a provenance chain with validation.
    
    Args:
        source_artifacts: IDs of original artifacts
        source_types: Types ("perception" or "memory") for each source
        transformations: Processing steps
        result_artifacts: IDs of resulting artifacts
        
    Returns:
        Validated ProvenanceChain
        
    Raises:
        ValueError: If validation fails
    """
    chain = ProvenanceChain(
        provenance_identity=f"provenance:{uuid.uuid4().hex[:16]}",
        source_artifact_ids=source_artifacts,
        source_types=source_types,
        transformations=transformations,
        result_artifact_ids=result_artifacts,
        processing_identity="integration:generic",
    )
    
    is_valid, errors = ProvenanceValidator.validate_chain(chain)
    
    if not is_valid:
        raise ValueError(f"Invalid provenance chain: {errors}")
    
    return chain


__all__ = [
    "ProvenanceKind",
    "ProvenanceSource",
    "ProvenanceTransformation",
    "ProvenanceChain",
    "ProvenanceValidator",
    "create_provenance_chain",
]