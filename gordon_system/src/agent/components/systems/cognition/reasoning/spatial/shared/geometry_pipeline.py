# Geometry Pipeline - Phase 7.9
# =============================

"""
Canonical Geometric Reasoning Pipeline.

Canonical geometry pipeline:
    Entities -> Coordinate Normalization -> Property Computation ->
    Constraint Evaluation -> Consistency Validation -> Publication
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GeometricMeasurement:
    """
    Computed geometric measurement on an entity.
    
    Measurements remain explicit and reproducible.
    """
    
    # Identity
    measurement_id: str                     # Unique identifier
    
    # Entity targeted
    target_entity_id: str                   # Which entity was measured?
    
    # Measurement type
    measurement_type: str                   # e.g., "distance", "angle", "area"
    
    # Value - explicit representation
    value: float                            # Numeric result
    unit: str = "meters"                    # Unit of measurement
    
    # Uncertainty (explicit)
    confidence: float = 1.0                 # 0.0 to 1.0
    error_margin: Optional[float] = None    # Absolute error if known
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def is_reliable(self) -> bool:
        """Check if measurement is reliable based on confidence."""
        return self.confidence >= 0.8


@dataclass(frozen=True)
class PropertyComputation:
    """
    Computed property on an entity.
    
    Properties remain explicit and reproducible.
    """
    
    # Identity
    property_id: str                        # Unique identifier
    
    # Entity targeted
    target_entity_id: str                   # Which entity was analyzed?
    
    # Property type
    property_type: str                      # e.g., "volume", "surface_area", "centroid"
    
    # Computed value(s)
    computed_value: Any                     # Can be scalar, vector, matrix, etc.
    
    # Metadata
    computation_method: Optional[str] = None  # Algorithm used if known
    precision_digits: int = 6               # Decimal precision
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary for serialization."""
        return {
            "property_id": self.property_id,
            "target_entity_id": self.target_entity_id,
            "property_type": self.property_type,
            "computed_value": repr(self.computed_value),
            "computation_method": self.computation_method,
            "precision_digits": self.precision_digits,
        }


@dataclass(frozen=True)
class GeometryPipeline:
    """
    Result of geometric reasoning pipeline execution.
    
    Pipeline stages:
        Entities -> Coordinate Normalization -> Property Computation ->
        Constraint Evaluation -> Consistency Validation -> Publication
    """
    
    # Identity
    pipeline_id: str                        # Unique identifier
    
    # Input - participating geometry
    participating_entities: Tuple[str, ...] = ()  # Entity IDs processed
    
    # Computed measurements
    measurements: Tuple[GeometricMeasurement, ...] = ()
    
    # Computed properties
    properties: Tuple[PropertyComputation, ...] = ()
    
    # Diagnostics - pipeline execution info
    coordinate_transformations_applied: int = 0
    constraints_evaluated: int = 0
    validation_passed: bool = True
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    source_descriptor_id: str = ""
    
    @property
    def measurement_count(self) -> int:
        """Return number of measurements computed."""
        return len(self.measurements)
    
    @property
    def property_count(self) -> int:
        """Return number of properties computed."""
        return len(self.properties)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        entity_ids: List[str],
    ) -> GeometryPipeline:
        """Create a new geometry pipeline result."""
        return cls(
            pipeline_id=f"geometry:{uuid.uuid4().hex[:16]}",
            participating_entities=tuple(entity_ids),
            created_at_utc=time.time(),
            source_descriptor_id=semantic_identity,
        )
    
    def add_measurement(self, measurement: GeometricMeasurement) -> GeometryPipeline:
        """Return new pipeline with additional measurement."""
        return dataclass_replace(
            self,
            measurements=self.measurements + (measurement,),
        )
    
    def add_property(self, property_comp: PropertyComputation) -> GeometryPipeline:
        """Return new pipeline with additional property."""
        return dataclass_replace(
            self,
            properties=self.properties + (property_comp,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GeometryPipeline",
    "GeometricMeasurement", 
    "PropertyComputation",
]