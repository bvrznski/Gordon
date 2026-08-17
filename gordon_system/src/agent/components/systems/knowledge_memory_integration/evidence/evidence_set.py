# Knowledge-Memory Evidence Set
# ==============================

"""
Evidence Set: Grouped eligible evidence for semantic operations.

This module defines the EvidenceSet model that organizes retrieved and
eligible memory artifacts for semantic construction operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


@dataclass(frozen=True)
class KnowledgeMemoryEvidenceSet:
    """
    A set of eligible evidence artifacts for one semantic operation.
    
    Groups retained evidence that has been retrieved and filtered for eligibility
    before semantic extraction or grounding operations.
    
    Fields:
        evidence_set_identity:   Unique ID for this evidence set
        request_reference:       Reference to the originating request
        
        # Evidence categories
        eligible_artifacts:          Artifacts fully eligible for use
        conditionally_eligible_artifacts: Artifacts eligible with constraints
        rejected_artifacts:          Artifacts not eligible
        
        # Evidence roles in semantic context
        supporting_artifacts:        Artifacts supporting current understanding
        contradicting_artifacts:     Artifacts contradicting current understanding
        unresolved_artifacts:        Artifacts requiring further analysis
        
        # Scope information
        semantic_scope:              Semantic domain covered
        temporal_extent:             Time period covered (start_utc, end_utc)
        
        # Quality metrics
        confidence:                  Confidence in evidence set completeness
        uncertainty:                 Uncertainty about evidence quality
        
        # Limitations and provenance
        limitations:                 Known issues with this set
        provenance:                  How was this set constructed?
    """
    
    # Identity and request reference (required)
    evidence_set_identity: str              # Unique ID for this evidence set
    request_reference: str                  # Request this evidence supports
    
    # Evidence artifacts by eligibility status
    eligible_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Fully eligible
    conditionally_eligible_artifacts: Tuple[Tuple[str, Tuple[str, ...]], ...] = field(
        default_factory=tuple  # (artifact_id, conditions)
    )
    rejected_artifacts: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)  # (id, reason)
    
    # Evidence roles
    supporting_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Support current view
    contradicting_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Contradict current view
    unresolved_artifacts: Tuple[str, ...] = field(default_factory=tuple)  # Need more analysis
    
    # Scope information
    semantic_scope: str = ""                # Semantic domain (e.g., "python_concepts")
    temporal_extent_start_utc: Optional[float] = None
    temporal_extent_end_utc: Optional[float] = None
    
    # Quality metrics
    confidence: float = 1.0                 # Confidence in completeness
    uncertainty: float = 0.0                # Uncertainty about evidence
    
    # Limitations and diagnostics
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance tracking (required)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_evidence_response(
        cls,
        evidence_response,
        request_reference: str,
        confidence_threshold: float = 0.5,
    ) -> "KnowledgeMemoryEvidenceSet":
        """
        Create an EvidenceSet from an EvidenceResponse.
        
        Args:
            evidence_response: The response to process
            request_reference: Reference to the original request
            confidence_threshold: Minimum confidence for inclusion
        """
        eligible_ids = []
        rejected_ids = []
        
        # Process memory artifacts and their eligibility
        for i, artifact_id in enumerate(evidence_response.memory_artifacts):
            # Check if this artifact passes the confidence threshold
            if hasattr(evidence_response, 'confidence_bounds'):
                conf = evidence_response.confidence_bounds.resulting_confidence
                if conf >= confidence_threshold:
                    eligible_ids.append(artifact_id)
                else:
                    rejected_ids.append((artifact_id, "below_confidence_threshold"))
            
            # Check supersession state
            if hasattr(evidence_response, 'supersession_states'):
                states = dict(evidence_response.supersession_states)
                if artifact_id in states:
                    state = states[artifact_id]
                    if state.value == "historical_only":
                        rejected_ids.append((artifact_id, "historical_only"))
        
        return cls(
            evidence_set_identity=f"evidence_set:{uuid.uuid4().hex[:16]}",
            request_reference=request_reference,
            eligible_artifacts=tuple(eligible_ids),
            rejected_artifacts=tuple(rejected_ids),
            provenance={
                "origin": "evidence_response_processing",
                "created_at_utc": evidence_response.provenance.get("created_at_utc", 0),
                "artifact_count": len(evidence_response.memory_artifacts),
            },
        )
    
    @property
    def total_eligible_count(self) -> int:
        """Count of all eligible artifacts (including conditional)."""
        return len(self.eligible_artifacts) + len(self.conditionally_eligible_artifacts)
    
    @property
    def is_empty(self) -> bool:
        """Check if this evidence set has no eligible artifacts."""
        return self.total_eligible_count == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence set to dictionary for serialization."""
        return {
            "evidence_set_identity": self.evidence_set_identity,
            "request_reference": self.request_reference,
            "eligible_artifacts": list(self.eligible_artifacts),
            "conditionally_eligible_artifacts": [
                {"artifact_id": aid, "conditions": list(conds)}
                for aid, conds in self.conditionally_eligible_artifacts
            ],
            "rejected_artifacts": [{"artifact_id": aid, "reason": reason} for aid, reason in self.rejected_artifacts],
            "supporting_artifacts": list(self.supporting_artifacts),
            "contradicting_artifacts": list(self.contradicting_artifacts),
            "unresolved_artifacts": list(self.unresolved_artifacts),
            "semantic_scope": self.semantic_scope,
            "temporal_extent_start_utc": self.temporal_extent_start_utc,
            "temporal_extent_end_utc": self.temporal_extent_end_utc,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "diagnostics": list(self.diagnostics),
            "provenance": dict(self.provenance),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeMemoryEvidenceSet":
        """Create evidence set from dictionary."""
        return cls(
            evidence_set_identity=data.get("evidence_set_identity", str(id(data))),
            request_reference=data.get("request_reference", ""),
            eligible_artifacts=tuple(data.get("eligible_artifacts", [])),
            conditionally_eligible_artifacts=tuple(
                (item["artifact_id"], tuple(item.get("conditions", [])))
                for item in data.get("conditionally_eligible_artifacts", [])
            ),
            rejected_artifacts=tuple(
                (item["artifact_id"], item.get("reason", "unknown"))
                for item in data.get("rejected_artifacts", [])
            ),
            supporting_artifacts=tuple(data.get("supporting_artifacts", [])),
            contradicting_artifacts=tuple(data.get("contradicting_artifacts", [])),
            unresolved_artifacts=tuple(data.get("unresolved_artifacts", [])),
            semantic_scope=data.get("semantic_scope", ""),
            temporal_extent_start_utc=data.get("temporal_extent_start_utc"),
            temporal_extent_end_utc=data.get("temporal_extent_end_utc"),
            confidence=float(data.get("confidence", 1.0)),
            uncertainty=float(data.get("uncertainty", 0.0)),
            limitations=tuple(data.get("limitations", [])),
            diagnostics=tuple(data.get("diagnostics", [])),
            provenance=dict(data.get("provenance", {})),
        )


__all__ = ["KnowledgeMemoryEvidenceSet"]