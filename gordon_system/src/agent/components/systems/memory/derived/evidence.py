# Derived Memory Evidence Contract - Phase 5.1.6 Canonical Implementation
# ========================================================================
"""
Evidence: The contract for derivation evidence aggregation and validation.

Purpose:
    Define how evidence is collected, validated, and attributed to derivations.
    
Evidence Laws:
    EVIDENCE-LAW-001: Every derivation references supporting memory artifacts
    EVIDENCE-LAW-002: Evidence remains inspectable
    EVIDENCE-LAW-003: Evidence preserves provenance
    EVIDENCE-LAW-004: Evidence preserves revision lineage
    EVIDENCE-LAW-005: Evidence shall never be fabricated
    EVIDENCE-LAW-006: Evidence revisions remain versioned
    EVIDENCE-LAW-007: Evidence remains immutable after publication
    EVIDENCE-LAW-008: Evidence evaluation remains deterministic

Evidence Aggregation:
    1. Collect supporting artifacts from source memory
    2. Validate evidence completeness
    3. Calculate confidence based on evidence quality
    4. Record provenance of each piece of evidence
    
Evidence Validation:
    - All source artifacts must exist
    - All relations used must be valid
    - Evidence must support the derivation conclusion
    - No contradictions in supporting evidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# EVIDENCE KINDS - What kind of evidence?
# =============================================================================


class EvidenceKind(Enum):
    """
    Kinds of evidence in derivations.
    
    | Kind            | Description                                       |
    |-----------------|---------------------------------------------------|
    | OBSERVATION     : Direct observation or perception
    | INFERENCE       : Derived through logical reasoning
    | AUTHORITY       : Attributed to trusted source
    | CONSISTENCY     : Consistent with known facts
    | VERIFICATION    : Independently verified fact
    | ANALOGY         : Based on similar cases
    | CAUSAL_EVIDENCE : Evidence of causal relationship
    
    All evidence kinds must preserve provenance and be inspectable.
    """
    
    OBSERVATION = "observation"
    INFERENCE = "inference"
    AUTHORITY = "authority"
    CONSISTENCY = "consistency"
    VERIFICATION = "verification"
    ANALOGY = "analogy"
    CAUSAL_EVIDENCE = "causal_evidence"


# =============================================================================
# EVIDENCE ITEM - A single piece of evidence
# =============================================================================


@dataclass(frozen=True)
class EvidenceItem:
    """
    A single piece of supporting evidence for a derivation.
    
    Fields:
        evidence_id:         Unique identifier for this item
        kind_:               What kind of evidence?
        
        # Content
        source_artifact_ids: IDs of artifacts that form this evidence
        description:         Human-readable explanation
        
        # Quality metrics
        confidence:          Trust in this piece of evidence (0.0-1.0)
        uncertainty:         Uncertainty about this evidence (0.0-1.0)
        
        # Provenance
        origin_system:       Which system collected this?
        timestamp_utc:       When was this evidence item created?
        
    Evidence Laws:
        EVIDENCE-LAW-002: Evidence remains inspectable
        EVIDENCE-LAW-003: Evidence preserves provenance
        EVIDENCE-LAW-008: Evidence evaluation is deterministic
    """
    
    evidence_id: str                        # Unique ID for this evidence item
    kind_: EvidenceKind                     # Kind of evidence
    
    # Content
    source_artifact_ids: Tuple[str, ...]    # Which artifacts support this?
    description: Optional[str] = None       # Human-readable explanation
    
    # Quality metrics
    confidence: float = 1.0                 # Trust in this evidence (0.0-1.0)
    uncertainty: float = 0.0                # Uncertainty about this evidence (0.0-1.0)
    
    # Provenance
    origin_system: str = "system"           # System that collected this
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# EVIDENCE COLLECTION - A collection of evidence items
# =============================================================================


@dataclass(frozen=True)
class EvidenceCollection:
    """
    A collection of evidence items for a derivation.
    
    Fields:
        collection_id:       Unique identifier for this collection
        derivation_id:       Which derivation does this support?
        
        # Evidence content
        items:               Individual pieces of evidence
        relations_used:      Relations between supporting artifacts
        
        # Aggregation metrics
        total_confidence:    Aggregate confidence across all evidence
        total_uncertainty:   Aggregate uncertainty across all evidence
        
        # Provenance
        collected_at_utc:    When was this collection created?
        
    Evidence Laws:
        EVIDENCE-LAW-001: Every derivation references supporting memory artifacts
        EVIDENCE-LAW-006: Evidence revisions remain versioned
    """
    
    collection_id: str                      # Unique ID for this collection
    derivation_id: str                      # Supporting which derivation?
    
    # Evidence content
    items: Tuple[EvidenceItem, ...]         # Individual evidence items
    relations_used: Tuple[str, ...] = field(default_factory=tuple)  # Relations used
    
    # Aggregation metrics
    total_confidence: float = 1.0           # Aggregate confidence (0.0-1.0)
    total_uncertainty: float = 0.0          # Aggregate uncertainty (0.0-1.0)
    
    # Provenance
    collected_at_utc: float = field(default_factory=time.time)


# =============================================================================
# EVIDENCE VALIDATOR - Validates evidence collections
# =============================================================================


class EvidenceValidator:
    """
    Validator for evidence collections.
    
    Verifies that evidence collections follow all contracts before derivations
    can be published.
    
    Validation Laws:
        VALIDATION-LAW-001: Every derivation must have supporting evidence
        VALIDATION-LAW-002: Evidence completeness is verified
        VALIDATION-LAW-003: Evidence logical consistency is checked
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._validation_count = 0
    
    def validate_collection(
        self, collection: EvidenceCollection
    ) -> Tuple[bool, Optional[str], Dict[str, float]]:
        """
        Validate an evidence collection.
        
        Args:
            collection: The evidence collection to validate
            
        Returns:
            Tuple of (is_valid, reason, metrics)
            
        Validation Checks:
            - At least one evidence item exists
            - All confidence values are in valid range
            - No contradictory evidence items
            - Total confidence is within bounds
        """
        self._validation_count += 1
        
        # Must have at least one evidence item
        if len(collection.items) == 0:
            return False, "No evidence items provided", {"count": 0}
        
        # Validate each item and aggregate metrics
        total_confidence = 0.0
        total_uncertainty = 0.0
        
        for i, item in enumerate(collection.items):
            if not 0.0 <= item.confidence <= 1.0:
                return False, f"Invalid confidence in item {i}: {item.confidence}", {"count": len(collection.items)}
            
            if not 0.0 <= item.uncertainty <= 1.0:
                return False, f"Invalid uncertainty in item {i}: {item.uncertainty}", {"count": len(collection.items)}
            
            total_confidence += item.confidence
            total_uncertainty += item.uncertainty
        
        # Calculate aggregate metrics
        avg_confidence = total_confidence / len(collection.items)
        
        # Check for contradictions (items that contradict each other)
        if self._detect_contradictions(collection):
            return False, "Contradictory evidence items detected", {
                "count": len(collection.items),
                "avg_confidence": avg_confidence,
            }
        
        # All checks passed
        metrics = {
            "count": len(collection.items),
            "avg_confidence": avg_confidence,
            "total_uncertainty": total_uncertainty / len(collection.items),
        }
        
        return True, "Evidence collection valid", metrics
    
    def _detect_contradictions(
        self, collection: EvidenceCollection
    ) -> bool:
        """
        Detect contradictory evidence items.
        
        This is a simplified implementation - actual contradiction detection
        would need to analyze the semantic content of supporting artifacts.
        
        Returns:
            True if contradictions found, False otherwise
        """
        # Simplified: in real implementation, this would compare artifact contents
        return False
    
    def calculate_aggregate_metrics(
        self, items: Tuple[EvidenceItem, ...]
    ) -> Dict[str, float]:
        """
        Calculate aggregate metrics from a set of evidence items.
        
        Args:
            items: Evidence items to aggregate
            
        Returns:
            Dictionary with total_confidence and total_uncertainty
        """
        if len(items) == 0:
            return {"total_confidence": 0.0, "total_uncertainty": 1.0}
        
        total_confidence = sum(item.confidence for item in items)
        total_uncertainty = sum(item.uncertainty for item in items)
        
        return {
            "total_confidence": total_confidence / len(items),
            "total_uncertainty": total_uncertainty / len(items),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "validation_count": self._validation_count,
        }


# =============================================================================
# EVIDENCE BUILDER - Mutable builder for evidence collections
# =============================================================================


class EvidenceBuilder:
    """
    Mutable builder for constructing evidence collections.
    
    Allows step-by-step construction before producing an immutable collection.
    """
    
    def __init__(self, derivation_id: str):
        """Initialize the builder."""
        self._derivation_id = derivation_id
        
        # Identity
        self._collection_id = f"evidence:{uuid.uuid4().hex[:12]}"
        
        # Items
        self._items: List[EvidenceItem] = []
        
        # Relations
        self._relations_used: List[str] = []
        
        # Provenance
        self._collected_at_utc = time.time()
    
    def add_item(
        self,
        kind_: EvidenceKind,
        source_artifact_ids: Tuple[str, ...],
        description: Optional[str] = None,
        confidence: float = 1.0,
        uncertainty: float = 0.0,
    ) -> "EvidenceBuilder":
        """Add an evidence item."""
        item = EvidenceItem(
            evidence_id=f"item:{uuid.uuid4().hex[:8]}",
            kind_=kind_,
            source_artifact_ids=source_artifact_ids,
            description=description,
            confidence=confidence,
            uncertainty=uncertainty,
            origin_system="builder",
        )
        self._items.append(item)
        return self
    
    def add_relation(self, relation_id: str) -> "EvidenceBuilder":
        """Add a relation used in this evidence."""
        self._relations_used.append(relation_id)
        return self
    
    def set_collection_id(self, collection_id: str) -> "EvidenceBuilder":
        """Set the collection ID."""
        self._collection_id = collection_id
        return self
    
    def build(self) -> EvidenceCollection:
        """
        Build an immutable EvidenceCollection from this builder.
        
        Returns:
            New EvidenceCollection with all settings applied
        """
        # Calculate aggregate metrics
        if len(self._items) > 0:
            total_confidence = sum(item.confidence for item in self._items)
            total_uncertainty = sum(item.uncertainty for item in self._items)
            
            avg_confidence = total_confidence / len(self._items)
            avg_uncertainty = total_uncertainty / len(self._items)
        else:
            avg_confidence = 0.0
            avg_uncertainty = 1.0
        
        return EvidenceCollection(
            collection_id=self._collection_id,
            derivation_id=self._derivation_id,
            items=tuple(self._items),
            relations_used=tuple(self._relations_used),
            total_confidence=avg_confidence,
            total_uncertainty=avg_uncertainty,
            collected_at_utc=time.time(),
        )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Kinds
    "EvidenceKind",
    
    # Item
    "EvidenceItem",
    
    # Collection
    "EvidenceCollection",
    
    # Validator
    "EvidenceValidator",
    
    # Builder
    "EvidenceBuilder",
]