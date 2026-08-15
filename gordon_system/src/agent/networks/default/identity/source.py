# Identity Source Reference Model
# ===============================

"""
Immutable identity source reference model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IdentitySourceReference:
    """
    Immutable representation of an identity source reference.
    
    PROPERTIES:
        • source_id: Unique identifier for this source
        • source_owner: Who owns the source system
        • source_revision: Source revision at capture time
        • source_kind: What type of source (IdentitySourceKind.*)
        • factuality: Factuality classification (FactualityClassification.*)
        • authority: Authority level that validated this source
        • captured_at_utc: When this source was captured
        • relevance: Relevance to identity integration (0.0 to 1.0)
        • confidence: Confidence in source reliability (0.0 to 1.0)
        • provenance: Provenance tracking reference
    """
    
    source_id: str = ""
    """Unique identifier for this identity source."""
    
    source_owner: str = ""
    """Who owns the source system (Identity, Memory, etc.)."""
    
    source_revision: int = 1
    """Source revision number at capture time."""
    
    source_kind: str = "identity_record"
    """What type of source (IdentitySourceKind.*)."""
    
    factuality: str = "recorded"
    """Factuality classification (FactualityClassification.*)."""
    
    authority: str = "identity_authority"
    """Authority level that validated this source."""
    
    captured_at_utc: datetime = field(default_factory=datetime.utcnow)
    """When this source was captured."""
    
    relevance: float = 1.0
    """Relevance to identity integration (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in source reliability (0.0 to 1.0)."""
    
    provenance: str = "canonical"
    """Provenance tracking reference."""