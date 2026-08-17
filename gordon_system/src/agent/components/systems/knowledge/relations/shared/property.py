# Knowledge Relation Property - Phase 6.5
# ======================================

"""
Relation Property: Attributes and metrics for Relations.

Relations may possess various properties that describe their characteristics.
These properties are independent from the relation's semantic endpoints.

Examples of relation properties:
    - confidence:      Semantic certainty in the relation (0.0-1.0)
    - strength:        Strength of the relationship (0.0-1.0)
    - weight:          Numerical weight for graph algorithms
    - priority:        Priority level for reasoning
    - stability:       Stability metric over time
    - scope:           Applicability domain
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# PROPERTY KINDS - Types of relation properties
# =============================================================================


class RelationPropertyKind(Enum):
    """
    Kinds of properties that can be attached to Relations.
    
    Defines the categories of relation attributes:
        METRIC      -> Numerical metrics (confidence, strength, weight)
        QUALITY     -> Quality assessment (certainty, stability, priority)
        SEMANTIC    -> Semantic boundaries and scope
        LIFECYCLE   -> Lifecycle state tracking
        PROVENANCE  -> Provenance metadata
        CONSTRAINT  -> Constraint definitions
    """
    
    METRIC = "metric"         # Numerical metrics
    QUALITY = "quality"       # Quality assessments
    SEMANTIC = "semantic"     # Semantic properties
    LIFECYCLE = "lifecycle"   # Lifecycle state
    PROVENANCE = "provenance" # Provenance tracking
    CONSTRAINT = "constraint" # Constraint definitions


# =============================================================================
# PROPERTY VALUE TYPES - Type categorization for property values
# =============================================================================


class RelationPropertyValueKind(Enum):
    """
    Kinds of value types for relation properties.
    
    Defines the data type of a property's value:
        NUMERIC     -> Float or integer values
        BOOLEAN     -> True/false values
        STRING      -> Text values
        ENUMERATION -> Enum value from known set
        COMPLEX     -> Structured object value
    """
    
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    STRING = "string"
    ENUMERATION = "enumeration"
    COMPLEX = "complex"


# =============================================================================
# RELATION PROPERTY - Canonical property structure
# =============================================================================


@dataclass(frozen=True)
class RelationProperty:
    """
    Property attached to a semantic relation in Gordon's knowledge system.
    
    Properties describe the relation itself, independent of its endpoints.
    Every property has:
        - Unique identity
        - Reference to the relation it belongs to
        - Kind (category)
        - Value (the actual data)
        - Constraints (validation rules)
        - Provenance (origin tracking)
    
    Fields:
        property_identity:   Unique identifier for this property
        relation_reference:  Identity of the relation this property attaches to
        property_kind:       Category of this property
        value:               Property value
        constraints:         Validation constraints on the value
        confidence:          Confidence in this property (0.0-1.0)
        provenance:          Origin tracking records
    """
    
    # Identity and reference (required)
    property_identity: str                  # Unique ID for this property
    relation_reference: str                 # Relation this property belongs to
    
    # Property metadata (required)
    property_kind: RelationPropertyKind     # Category of the property
    value_kind: RelationPropertyValueKind   # Data type of the value
    
    # Value storage (required - stored as Any for flexibility)
    value: Any                              # The actual property value
    
    # Constraints and quality (optional with defaults)
    constraints: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0                 # Confidence in this property
    
    # Provenance
    provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if property has valid foundational data."""
        return (
            len(self.property_identity) > 0 and
            len(self.relation_reference) > 0 and
            self.property_kind is not None and
            self.value is not None
        )
    
    @property
    def name(self) -> str:
        """Get a human-readable property name from identity."""
        if self.property_identity.startswith("prop:"):
            return self.property_identity[5:]
        return self.property_identity
    
    @classmethod
    def create(
        cls,
        relation_id: str,
        property_kind: RelationPropertyKind,
        value: Any,
        constraints: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "RelationProperty":
        """
        Create a new relation property.
        
        Args:
            relation_id: ID of the relation this property belongs to
            property_kind: Category of the property
            value: Property value
            constraints: Validation constraints (optional)
            confidence: Confidence in this property (0.0-1.0)
            provenance_context: Initial provenance context (optional)
            
        Returns:
            New RelationProperty instance
        """
        initial_provenance = (
            {
                "provenance_identity": f"prop-prov:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "originating_revision": 1,
                "property_reference": f"prop:{uuid.uuid4().hex[:16]}",
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            property_identity=f"prop:{uuid.uuid4().hex[:16]}",
            relation_reference=relation_id,
            property_kind=property_kind,
            value_kind=_infer_value_kind(value),
            value=value,
            constraints=constraints or {},
            confidence=max(0.0, min(1.0, float(confidence))),
            provenance=initial_provenance,
        )
    
    def with_revision(
        self,
        new_value: Any,
        change_reason: Optional[str] = None,
    ) -> "RelationProperty":
        """
        Create a revised version of this property.
        
        Args:
            new_value: The updated value
            change_reason: Reason for the revision (optional)
            
        Returns:
            New property instance with updated value
        """
        new_provenance = tuple(list(self.provenance) + [{
            "provenance_identity": f"prop-prov:{uuid.uuid4().hex[:16]}",
            "originating_request": change_reason or "Property revision",
            "originating_system": self.provenance[0].get("originating_system", "system") if self.provenance else "system",
            "originating_revision": len(self.provenance),
            "property_reference": self.property_identity,
            "previous_value": self.value,
            "timestamp_utc": time.time(),
        }])
        
        return RelationProperty(
            property_identity=self.property_identity,
            relation_reference=self.relation_reference,
            property_kind=self.property_kind,
            value_kind=_infer_value_kind(new_value),
            value=new_value,
            constraints=self.constraints,
            confidence=self.confidence,
            provenance=new_provenance,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert property to dictionary for serialization."""
        return {
            "property_identity": self.property_identity,
            "relation_reference": self.relation_reference,
            "property_kind": self.property_kind.value,
            "value_kind": self.value_kind.value,
            "value": _serialize_value(self.value),
            "constraints": dict(self.constraints),
            "confidence": self.confidence,
            "provenance": [p for p in self.provenance],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelationProperty":
        """Create property from dictionary."""
        provenance = []
        for p_data in data.get("provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        try:
            property_kind = RelationPropertyKind(data.get("property_kind", "metric"))
        except ValueError:
            property_kind = RelationPropertyKind.METRIC
        
        try:
            value_kind = RelationPropertyValueKind(data.get("value_kind", "numeric"))
        except ValueError:
            value_kind = RelationPropertyValueKind.NUMERIC
        
        return cls(
            property_identity=data.get("property_identity", str(uuid.uuid4())),
            relation_reference=data.get("relation_reference", ""),
            property_kind=property_kind,
            value_kind=value_kind,
            value=_deserialize_value(data.get("value")),
            constraints=dict(data.get("constraints", {})),
            confidence=float(data.get("confidence", 1.0)),
            provenance=tuple(provenance),
        )


def _infer_value_kind(value: Any) -> RelationPropertyValueKind:
    """Infer the value kind from a Python value."""
    if value is None:
        return RelationPropertyValueKind.STRING
    elif isinstance(value, (int, float)):
        return RelationPropertyValueKind.NUMERIC
    elif isinstance(value, bool):
        return RelationPropertyValueKind.BOOLEAN
    elif isinstance(value, str):
        return RelationPropertyValueKind.STRING
    elif isinstance(value, Enum):
        return RelationPropertyValueKind.ENUMERATION
    else:
        return RelationPropertyValueKind.COMPLEX


def _serialize_value(value: Any) -> Any:
    """Serialize a value for storage."""
    if isinstance(value, Enum):
        return {"__enum__": True, "type": type(value).__name__, "value": value.value}
    elif isinstance(value, (dict, list, tuple)):
        return value
    else:
        return str(value) if value is not None else None


def _deserialize_value(data: Any) -> Any:
    """Deserialize a value from storage."""
    if isinstance(data, dict) and data.get("__enum__"):
        # In practice, would map back to actual enum classes
        return data.get("value")
    return data


__all__ = [
    # Property kinds
    "RelationPropertyKind",
    # Value kinds
    "RelationPropertyValueKind",
    # Property
    "RelationProperty",
]