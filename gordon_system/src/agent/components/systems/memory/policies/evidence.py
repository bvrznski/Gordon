# Memory Policy Evidence - Phase 5.1.5 Canonical Evidence Model
# ================================================================
"""
Memory Policy Evidence: Supporting data for policy decisions.

Evidence is what policies use to make decisions.
Evidence is never created by policies; it is observed and referenced.

Evidence Kinds:
    ARTIFACT       : Reference to a memory artifact
    RULE           : Applied policy rule or constraint
    STATISTIC      : Statistical observation about the system
    CONTEXT        : Contextual information for evaluation
    HISTORY        : Historical state of artifacts
    PROVENANCE     : Origin and processing history

Evidence Laws:
    EVIDENCE-LAW-001: Every recommendation references supporting evidence
    EVIDENCE-LAW-002: Evidence is explicit and inspectable
    EVIDENCE-LAW-003: Evidence preserves provenance
    EVIDENCE-LAW-004: Evidence remains immutable after publication
    EVIDENCE-LAW-005: Evidence shall never be fabricated
    EVIDENCE-LAW-006: Evidence evaluation is deterministic

Policy Contract:
    Operation Proposal
         ↓
    Policy Evaluation (uses evidence)
         ↓
    Decision (references evidence)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# EVIDENCE KINDS - What types of evidence exist?
# =============================================================================


class EvidenceKind(Enum):
    """
    Kinds of evidence policies can reference.
    
    | Kind         | Description                                    |
    |--------------|------------------------------------------------|
    | ARTIFACT     : Reference to a memory artifact
    | RULE         : Applied policy rule or constraint
    | STATISTIC    : Statistical observation about the system
    | CONTEXT      : Contextual information for evaluation
    | HISTORY      : Historical state of artifacts
    | PROVENANCE   : Origin and processing history
    """
    
    ARTIFACT = "artifact"       # Reference to memory artifact
    RULE = "rule"             # Applied policy rule
    STATISTIC = "statistic"   # Statistical observation
    CONTEXT = "context"       # Contextual information
    HISTORY = "history"       # Historical state
    PROVENANCE = "provenance" # Origin and history


# =============================================================================
# EVIDENCE RECORD - Reference to supporting evidence
# =============================================================================


@dataclass(frozen=True)
class PolicyEvidence:
    """
    Immutable reference to supporting evidence for a policy decision.
    
    Evidence is what policies observe and reference.
    Policies never create or modify evidence; they only use it.
    
    Fields:
        evidence_id:     Unique ID for this evidence record
        kind_:           What kind of evidence is this?
        
        # Content references
        source_type:     Type of the evidence source
        source_id:       ID of the source (artifact, rule, etc.)
        
        # Evidence content (can be minimal reference)
        description:     Human-readable description of evidence
        value:           The actual evidence value (if small)
        
        # Provenance
        timestamp_utc:   When was this evidence created/observed?
        provenance:      Where did this evidence come from?
        
        # Quality metrics
        confidence:      Confidence in the evidence (0.0-1.0)
        reliability:     How reliable is this source? (0.0-1.0)
    """
    
    evidence_id: str                            # Unique ID for this evidence record
    
    kind_: EvidenceKind                         # What kind of evidence?
    
    # Source references
    source_type: str                            # Type of source (artifact, rule, etc.)
    source_id: str                              # ID of the source
    
    # Content
    description: str = ""                       # Description of what this evidence shows
    value: Optional[Any] = None                 # The actual evidence value
    
    # Provenance
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    # Quality metrics
    confidence: float = 1.0                     # Confidence in this evidence (0.0-1.0)
    reliability: float = 1.0                    # How reliable is the source? (0.0-1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary representation."""
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind_.value,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "description": self.description,
            "value": str(self.value) if self.value is not None else None,
            "timestamp_utc": self.timestamp_utc,
            "provenance": dict(self.provenance),
            "confidence": self.confidence,
            "reliability": self.reliability,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PolicyEvidence:
        """Create evidence from dictionary representation."""
        return cls(
            evidence_id=data["evidence_id"],
            kind_=EvidenceKind(data["kind"]),
            source_type=data["source_type"],
            source_id=data["source_id"],
            description=data.get("description", ""),
            value=data.get("value"),
            timestamp_utc=data.get("timestamp_utc", time.time()),
            provenance=dict(data.get("provenance", {})),
            confidence=data.get("confidence", 1.0),
            reliability=data.get("reliability", 1.0),
        )
    
    def explain(self) -> str:
        """Generate human-readable explanation of this evidence."""
        parts = [
            f"Evidence: {self.kind_.value.upper()}",
            f"Source: {self.source_type} ({self.source_id})",
            f"Confidence: {self.confidence:.2%}",
            f"Reliability: {self.reliability:.2%}",
        ]
        
        if self.description:
            parts.append(f"{self.description}")
        
        return " | ".join(parts)


# =============================================================================
# EVIDENCE BUILDER - Mutable builder for evidence records
# =============================================================================


class PolicyEvidenceBuilder:
    """
    Mutable builder for constructing policy evidence records.
    
    Allows step-by-step construction before producing an immutable record.
    """
    
    def __init__(
        self,
        kind_: EvidenceKind,
        source_type: str,
        source_id: str,
    ):
        """Initialize the builder."""
        self._kind_ = kind_
        self._source_type = source_type
        self._source_id = source_id
        
        self._description = ""
        self._value: Optional[Any] = None
        self._provenance: Dict[str, Any] = {"origin": "system"}
        self._confidence = 1.0
        self._reliability = 1.0
    
    def set_description(self, description: str) -> "PolicyEvidenceBuilder":
        """Set the human-readable description of this evidence."""
        self._description = description
        return self
    
    def set_value(self, value: Any) -> "PolicyEvidenceBuilder":
        """Set the actual evidence value."""
        self._value = value
        return self
    
    def set_provenance(self, provenance: Dict[str, Any]) -> "PolicyEvidenceBuilder":
        """Set the provenance information."""
        self._provenance = dict(provenance)
        return self
    
    def set_confidence(self, confidence: float) -> "PolicyEvidenceBuilder":
        """Set confidence in this evidence (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_reliability(self, reliability: float) -> "PolicyEvidenceBuilder":
        """Set reliability of this source (0.0-1.0)."""
        if not 0.0 <= reliability <= 1.0:
            raise ValueError(f"Reliability must be 0.0-1.0, got {reliability}")
        self._reliability = reliability
        return self
    
    def build(self) -> PolicyEvidence:
        """
        Build an immutable PolicyEvidence record.
        
        Returns:
            New PolicyEvidence with all settings applied
        """
        import uuid
        evidence_id = f"evidence:{uuid.uuid4().hex[:12]}"
        
        return PolicyEvidence(
            evidence_id=evidence_id,
            kind_=self._kind_,
            source_type=self._source_type,
            source_id=self._source_id,
            description=self._description,
            value=self._value,
            provenance=dict(self._provenance),
            confidence=self._confidence,
            reliability=self._reliability,
        )


# =============================================================================
# EVIDENCE COLLECTION - Group of related evidence
# =============================================================================


@dataclass(frozen=True)
class EvidenceCollection:
    """
    Immutable collection of policy evidence records.
    
    Collections group related evidence for a single decision evaluation.
    
    Fields:
        collection_id:   Unique ID for this collection
        evidence_records: Tuple of individual evidence records
        created_at_utc:  When was the collection created?
        metadata:        Additional collection metadata
    """
    
    collection_id: str                          # Unique ID for this collection
    
    evidence_records: Tuple[PolicyEvidence, ...] = field(default_factory=tuple)
    
    created_at_utc: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_by_kind(self, kind_: EvidenceKind) -> Tuple[PolicyEvidence, ...]:
        """Get all evidence records of a specific kind."""
        return tuple(e for e in self.evidence_records if e.kind_ == kind_)
    
    def get_by_source_type(self, source_type: str) -> Tuple[PolicyEvidence, ...]:
        """Get all evidence from sources of a specific type."""
        return tuple(e for e in self.evidence_records if e.source_type == source_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert collection to dictionary representation."""
        return {
            "collection_id": self.collection_id,
            "evidence_records": [e.to_dict() for e in self.evidence_records],
            "created_at_utc": self.created_at_utc,
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidenceCollection:
        """Create evidence collection from dictionary representation."""
        records = []
        for rec_data in data.get("evidence_records", []):
            try:
                records.append(PolicyEvidence.from_dict(rec_data))
            except Exception:
                continue
        return cls(
            collection_id=data["collection_id"],
            evidence_records=tuple(records),
            created_at_utc=data.get("created_at_utc", time.time()),
            metadata=dict(data.get("metadata", {})),
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_artifact_evidence(
    artifact: Any,
    description: str = "",
    confidence: float = 1.0,
) -> PolicyEvidence:
    """
    Create evidence referencing a memory artifact.
    
    Args:
        artifact: The memory artifact to reference
        description: Description of what this evidence shows
        confidence: Confidence in the evidence
        
    Returns:
        New PolicyEvidence record for this artifact
    """
    import uuid
    
    # Get artifact ID
    artifact_id = getattr(artifact, "identity", None)
    if hasattr(artifact_id, "artifact_id"):
        source_id = artifact_id.artifact_id
    elif isinstance(artifact_id, str):
        source_id = artifact_id
    else:
        source_id = str(hash(artifact))
    
    return PolicyEvidence(
        evidence_id=f"evidence:{uuid.uuid4().hex[:12]}",
        kind_=EvidenceKind.ARTIFACT,
        source_type="memory_artifact",
        source_id=source_id,
        description=description,
        value=str(artifact)[:100] if artifact else None,  # Truncate for brevity
        confidence=confidence,
        reliability=1.0,
    )


def create_rule_evidence(
    rule_name: str,
    rule_description: str = "",
    confidence: float = 1.0,
) -> PolicyEvidence:
    """
    Create evidence referencing an applied policy rule.
    
    Args:
        rule_name: Name of the applied rule
        rule_description: Description of what the rule specifies
        confidence: Confidence in rule application
        
    Returns:
        New PolicyEvidence record for this rule
    """
    import uuid
    
    return PolicyEvidence(
        evidence_id=f"evidence:{uuid.uuid4().hex[:12]}",
        kind_=EvidenceKind.RULE,
        source_type="policy_rule",
        source_id=rule_name,
        description=rule_description or f"Applied rule: {rule_name}",
        value={"rule": rule_name},
        confidence=confidence,
        reliability=1.0,
    )


def create_statistic_evidence(
    statistic_name: str,
    value: Any,
    description: str = "",
    reliability: float = 1.0,
) -> PolicyEvidence:
    """
    Create evidence referencing a statistical observation.
    
    Args:
        statistic_name: Name of the observed statistic
        value: The observed value
        description: Description of what this shows
        reliability: How reliable is this statistic?
        
    Returns:
        New PolicyEvidence record for this statistic
    """
    import uuid
    
    return PolicyEvidence(
        evidence_id=f"evidence:{uuid.uuid4().hex[:12]}",
        kind_=EvidenceKind.STATISTIC,
        source_type="system_statistics",
        source_id=statistic_name,
        description=description or f"Observed: {statistic_name} = {value}",
        value=value,
        confidence=0.95,  # Statistics are generally reliable
        reliability=reliability,
    )


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Evidence kinds
    "EvidenceKind",
    
    # Evidence record
    "PolicyEvidence",
    
    # Builder
    "PolicyEvidenceBuilder",
    
    # Collection
    "EvidenceCollection",
    
    # Utility functions
    "create_artifact_evidence",
    "create_rule_evidence",
    "create_statistic_evidence",
]