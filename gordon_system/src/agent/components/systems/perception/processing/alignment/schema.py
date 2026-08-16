# Perceptual Schema Alignment - Phase 5.2.2
# ==========================================

"""
Schema Alignment: Aligns structurally different evidence into compatible fields.

Schema alignment maps between different data schemas to enable cross-source
processing without altering semantic meaning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# PERCEPTUAL SCHEMA ALIGNMENT - Schema structure mapping
# =============================================================================


@dataclass(frozen=True)
class PerceptualSchemaAlignment:
    """
    Mapping between source and target schema structures.
    
    Fields:
        alignment_identity:      Unique identifier for this alignment
        source_schema:           Source schema description
        target_schema:           Target (canonical) schema description
        field_mappings:          Field-by-field mapping rules
        value_mappings:          Value-level mappings (enums, units, etc.)
        omitted_fields:          Fields that don't have a mapping
        derived_fields:          New fields created through alignment
        unsupported_fields:      Fields that can't be mapped
        ambiguity:               Ambiguities in the alignment
        information_loss:        Information lost during alignment
        confidence:              Confidence in this schema mapping
    """
    
    alignment_identity: str             # Unique ID
    
    source_schema: str                  # e.g., "linux_process", "windows_process"
    target_schema: str = ""            # e.g., "canonical_process"
    
    field_mappings: Dict[str, str] = field(default_factory=dict)  # source_field -> target_field
    value_mappings: Dict[str, Any] = field(default_factory=dict)   # value -> mapped_value
    
    omitted_fields: Tuple[str, ...] = field(default_factory=tuple)
    derived_fields: Tuple[str, ...] = field(default_factory=tuple)
    unsupported_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    ambiguity: str = ""                 # Description of any ambiguities
    
    information_loss: str = ""         # What was lost?
    
    confidence: float = 0.5           # Alignment confidence (0.0-1.0)
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Alignment history
    
    @property
    def is_valid(self) -> bool:
        """Check if schema alignment has a target schema."""
        return len(self.target_schema) > 0 and self.confidence >= 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alignment to dictionary."""
        return {
            "alignment_identity": self.alignment_identity,
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "field_mappings": dict(self.field_mappings),
            "value_mappings": dict(self.value_mappings),
            "omitted_fields": list(self.omitted_fields),
            "derived_fields": list(self.derived_fields),
            "unsupported_fields": list(self.unsupported_fields),
            "ambiguity": self.ambiguity,
            "information_loss": self.information_loss,
            "confidence": self.confidence,
        }
    
    @classmethod
    def create(
        cls,
        source_schema: str,
        target_schema: str = "",
        field_mappings: Optional[Dict[str, str]] = None,
        value_mappings: Optional[Dict[str, Any]] = None,
    ) -> "PerceptualSchemaAlignment":
        """Create a new schema alignment."""
        return cls(
            alignment_identity=f"schema:{uuid.uuid4().hex[:16]}",
            source_schema=source_schema,
            target_schema=target_schema or f"canonical_{source_schema}",
            field_mappings=field_mappings or {},
            value_mappings=value_mappings or {},
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerceptualSchemaAlignment":
        """Create alignment from dictionary."""
        return cls(
            alignment_identity=data.get("alignment_identity", str(uuid.uuid4())),
            source_schema=data.get("source_schema", ""),
            target_schema=data.get("target_schema", ""),
            field_mappings=dict(data.get("field_mappings", {})),
            value_mappings=dict(data.get("value_mappings", {})),
            omitted_fields=tuple(data.get("omitted_fields", [])),
            derived_fields=tuple(data.get("derived_fields", [])),
            unsupported_fields=tuple(data.get("unsupported_fields", [])),
            ambiguity=data.get("ambiguity", ""),
            information_loss=data.get("information_loss", ""),
            confidence=float(data.get("confidence", 0.5)),
        )