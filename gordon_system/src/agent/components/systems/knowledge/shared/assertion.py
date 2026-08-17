# Knowledge Assertion - Phase 5.4
# ================================

"""
Knowledge Assertion: The smallest semantic claim in Gordon's knowledge system.

An assertion represents a semantic statement that may later become accepted,
rejected, revised, or remain unknown. Assertions are not automatically accepted;
they require justification and evidence to gain belief status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# ASSERTION STATES - Lifecycle of an assertion
# =============================================================================


class AssertionState(Enum):
    """
    States of assertion lifecycle.
    
    Every assertion shall have an explicit state indicating its current
    position in the knowledge organization pipeline.
    """
    
    PROPOSED = "proposed"           # New assertion, awaiting evaluation
    SUPPORTED = "supported"         # Has sufficient evidence and justification
    CHALLENGED = "challenged"       # Facing counter-evidence or criticism
    SUPERSEDED = "superseded"       # Replaced by newer assertion
    DEPRECATED = "deprecated"       # Should not be used, but not wrong
    UNKNOWN = "unknown"             # State indeterminate


# =============================================================================
# ASSERTION MODEL - Canonical assertion structure
# =============================================================================


@dataclass(frozen=True)
class KnowledgeAssertion:
    """
    Canonical representation of a semantic claim in Gordon's knowledge system.
    
    Every assertion shall possess an explicit semantic identity and preserve
    its provenance, confidence, uncertainty, and revision history.
    
    Fields:
        assertion_identity:    Unique identifier for this assertion
        statement:             The semantic content being claimed
        language:              Language of the statement (ISO 639-1)
        semantic_scope:        Domain context (e.g., "physical", "digital")
        source_evidence:       References to evidence supporting this claim
        confidence:            Semantic confidence in this assertion (0.0-1.0)
        uncertainty:           Semantic uncertainty about this assertion (0.0-1.0)
        revision:              Revision number for traceability
        provenance:            Origin tracking with timestamps and sources
        justification_chain:   References to justifications supporting this claim
        related_concepts:      Concepts referenced in this assertion
    """
    
    # Identity and metadata (required)
    assertion_identity: str           # Unique ID for this assertion
    
    # Semantic content (required)
    statement: str                    # The semantic claim being made
    language: str = "en"              # Statement language (ISO 639-1)
    semantic_scope: str = "general"   # Domain context
    
    # Evidence and justification
    source_evidence: Tuple[str, ...] = field(default_factory=tuple)  # Evidence references
    justification_chain: Tuple[str, ...] = field(default_factory=tuple)  # Justification refs
    
    # Quality metrics (required)
    confidence: float = 0.5           # Semantic confidence (0.0-1.0)
    uncertainty: float = 0.5          # Semantic uncertainty (0.0-1.0)
    
    # Lifecycle tracking
    revision: int = 1                 # Revision number for traceability
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    # Related knowledge artifacts
    related_concepts: Tuple[str, ...] = field(default_factory=tuple)
    related_beliefs: Tuple[str, ...] = field(default_factory=tuple)
    
    @property
    def is_valid(self) -> bool:
        """Check if assertion has minimal required data."""
        return (
            len(self.assertion_identity) > 0 and
            len(self.statement) > 0 and
            0.0 <= self.confidence <= 1.0 and
            0.0 <= self.uncertainty <= 1.0
        )
    
    @property
    def is_supported(self) -> bool:
        """Check if assertion has sufficient evidence."""
        return (
            len(self.source_evidence) > 0 or
            len(self.justification_chain) > 0
        )
    
    @classmethod
    def create(
        cls,
        statement: str,
        language: str = "en",
        semantic_scope: str = "general",
        source_evidence: Optional[List[str]] = None,
        justification_chain: Optional[List[str]] = None,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
        related_concepts: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> "KnowledgeAssertion":
        """
        Create a new assertion.
        
        Args:
            statement: The semantic claim being made
            language: Statement language (ISO 639-1)
            semantic_scope: Domain context
            source_evidence: Evidence references (optional)
            justification_chain: Justification references (optional)
            confidence: Semantic confidence (0.0-1.0)
            uncertainty: Semantic uncertainty (0.0-1.0)
            related_concepts: Related concept IDs (optional)
            provenance: Origin tracking data (optional)
        """
        return cls(
            assertion_identity=f"assertion:{uuid.uuid4().hex[:16]}",
            statement=statement,
            language=language,
            semantic_scope=semantic_scope,
            source_evidence=tuple(source_evidence or []),
            justification_chain=tuple(justification_chain or []),
            confidence=max(0.0, min(1.0, float(confidence))),
            uncertainty=max(0.0, min(1.0, float(uncertainty))),
            provenance={
                **(provenance or {}),
                "created_at_utc": time.time(),
                "revision": 1,
            },
            related_concepts=tuple(related_concepts or []),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assertion to dictionary for serialization."""
        return {
            "assertion_identity": self.assertion_identity,
            "statement": self.statement,
            "language": self.language,
            "semantic_scope": self.semantic_scope,
            "source_evidence": list(self.source_evidence),
            "justification_chain": list(self.justification_chain),
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "revision": self.revision,
            "provenance": dict(self.provenance),
            "related_concepts": list(self.related_concepts),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeAssertion":
        """Create assertion from dictionary."""
        return cls(
            assertion_identity=data.get("assertion_identity", str(uuid.uuid4())),
            statement=data.get("statement", ""),
            language=data.get("language", "en"),
            semantic_scope=data.get("semantic_scope", "general"),
            source_evidence=tuple(data.get("source_evidence", [])),
            justification_chain=tuple(data.get("justification_chain", [])),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.5)),
            revision=int(data.get("revision", 1)),
            provenance=dict(data.get("provenance", {})),
            related_concepts=tuple(data.get("related_concepts", [])),
        )
    
    def update_revision(
        self,
        new_statement: Optional[str] = None,
        new_evidence: Optional[List[str]] = None,
        confidence_delta: float = 0.0,
        uncertainty_delta: float = 0.0,
    ) -> "KnowledgeAssertion":
        """
        Create a revision of this assertion with updated content.
        
        Args:
            new_statement: Updated statement (optional)
            new_evidence: New evidence references (optional)
            confidence_delta: Confidence adjustment (-1.0 to +1.0)
            uncertainty_delta: Uncertainty adjustment (-1.0 to +1.0)
        """
        return KnowledgeAssertion(
            assertion_identity=self.assertion_identity,
            statement=new_statement or self.statement,
            language=self.language,
            semantic_scope=self.semantic_scope,
            source_evidence=tuple(new_evidence or self.source_evidence),
            justification_chain=self.justification_chain,
            confidence=max(0.0, min(1.0, self.confidence + confidence_delta)),
            uncertainty=max(0.0, min(1.0, self.uncertainty + uncertainty_delta)),
            revision=self.revision + 1,
            provenance={
                **self.provenance,
                "revised_at_utc": time.time(),
                "previous_revision": self.revision,
            },
            related_concepts=self.related_concepts,
        )


# =============================================================================
# ASSERTION VALIDATOR
# =============================================================================


class AssertionValidator:
    """
    Validates assertions for semantic integrity.
    
    Evaluates whether an assertion meets all requirements before becoming
    part of the knowledge graph.
    """
    
    def __init__(
        self,
        minimum_confidence: float = 0.3,
        maximum_uncertainty: float = 0.9,
    ):
        """
        Initialize the validator.
        
        Args:
            minimum_confidence: Minimum acceptable confidence (0.0-1.0)
            maximum_uncertainty: Maximum acceptable uncertainty (0.0-1.0)
        """
        self._minimum_confidence = minimum_confidence
        self._maximum_uncertainty = maximum_uncertainty
    
    @property
    def minimum_confidence(self) -> float:
        """Minimum acceptable confidence threshold."""
        return self._minimum_confidence
    
    @property
    def maximum_uncertainty(self) -> float:
        """Maximum acceptable uncertainty threshold."""
        return self._maximum_uncertainty
    
    def validate(
        self,
        assertion: KnowledgeAssertion,
    ) -> Tuple[bool, List[str]]:
        """
        Validate an assertion for semantic integrity.
        
        Args:
            assertion: The assertion to validate
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Rule 1: Must have identity
        if not assertion.assertion_identity or len(assertion.assertion_identity) == 0:
            issues.append("Missing assertion identity")
        
        # Rule 2: Statement must not be empty
        if not assertion.statement or len(assertion.statement.strip()) == 0:
            issues.append("Empty statement")
        
        # Rule 3: Confidence must be in valid range
        if not (0.0 <= assertion.confidence <= 1.0):
            issues.append(f"Invalid confidence: {assertion.confidence}")
        
        # Rule 4: Uncertainty must be in valid range
        if not (0.0 <= assertion.uncertainty <= 1.0):
            issues.append(f"Invalid uncertainty: {assertion.uncertainty}")
        
        # Rule 5: Confidence + uncertainty should sum to approximately 1.0
        total = assertion.confidence + assertion.uncertainty
        if not (0.8 <= total <= 1.2):  # Allow some flexibility
            issues.append(f"Confidence-uncertainty imbalance: {total:.2f}")
        
        # Rule 6: Confidence must meet minimum threshold
        if assertion.confidence < self._minimum_confidence:
            issues.append(f"Confidence below minimum: {assertion.confidence} < {self._minimum_confidence}")
        
        # Rule 7: Uncertainty must not exceed maximum
        if assertion.uncertainty > self._maximum_uncertainty:
            issues.append(f"Uncertainty above maximum: {assertion.uncertainty} > {self._maximum_uncertainty}")
        
        return len(issues) == 0, issues


__all__ = [
    "AssertionState",
    "KnowledgeAssertion",
    "AssertionValidator",
]