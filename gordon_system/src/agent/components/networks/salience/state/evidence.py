# Salience Network Evidence State
# ===============================
#
# Canonical implementation of evidence composition (Phase 4.8.4).
#

"""
Evidence state representation for Salience State.

Evidence State composes immutable Content references from Phase 4.8.3.
It preserves:
    - Supporting observations and evidence
    - Contradicting evidence
    - Cues and hypotheses
    - Evidence completeness

Do NOT create a second evidence model; reference canonical Content objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class SalienceEvidence:
    """
    Canonical salience evidence representation referencing immutable Content.
    
    Evidence represents semantic support for significance assessment without
    duplicating Content structures. Each evidence item has a role.
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-EVIDENCE-INV-001: Evidence references Content, never duplicates it
        - SALIENCE-EVIDENCE-INV-002: Evidence roles are explicit and distinct
        - SALIENCE-EVIDENCE-INV-003: Duplicate evidence across roles is invalid
    
    EVIDENCE ROLES:
        - SUPPORTING: Supports the salience assessment
        - CONTRADICTING: Contradicts the salience assessment
        - UNRESOLVED: Present but not yet classified
        - CONTEXTUAL: Provides background context
    """
    
    content_identity: str = field(default="")
    """Identity of the referenced Content object."""
    
    evidence_role: str = field(default="supporting")
    """
    Semantic role of this evidence:
        - supporting: Supports the assessment
        - contradicting: Contradicts the assessment
        - unresolved: Not yet classified
        - contextual: Provides background context
    """
    
    authority_id: str = field(default="")
    """Authority that vouches for this evidence."""
    
    confidence: str = field(default="unknown")
    """Semantic confidence in this evidence."""
    
    @property
    def is_supporting(self) -> bool:
        """Indicates whether this evidence supports the assessment."""
        return self.evidence_role == "supporting"
    
    @property
    def is_contradicting(self) -> bool:
        """Indicates whether this evidence contradicts the assessment."""
        return self.evidence_role == "contradicting"


@dataclass(frozen=True)
class SalienceEvidenceState:
    """
    Canonical composition of salience-related evidence.
    
    Evidence State preserves the distinctions among:
        - Supporting evidence: Semantic support for significance
        - Contradicting evidence: Mutually incompatible evidence
        - Unresolved evidence: Present but not yet classified
        - Cues: Indications that may become evidence
        - Hypotheses: Possible interpretations pending validation
    
    ARCHITECTURAL INVARIANTS:
        - SALIENCE-EVIDENCE-STATE-INV-001: Duplicate content identities are invalid
        - SALIENCE-EVIDENCE-STATE-INV-002: Same evidence cannot be both supporting and contradicting
        - SALIENCE-EVIDENCE-STATE-INV-003: Cues are not promoted to evidence silently
    
    EVIDENCE LAWS:
        - SALIENCE-EVIDENCE-STATE-LAW-001: Supporting and contradicting must coexist where applicable
        - SALIENCE-EVIDENCE-STATE-LAW-002: Hypotheses are not conclusions
        - SALIENCE-EVIDENCE-STATE-LAW-003: Evidence completeness is explicit
    """
    
    supporting: Tuple[SalienceEvidence, ...] = field(default_factory=tuple)
    """Evidence that supports the current assessment."""
    
    contradicting: Tuple[SalienceEvidence, ...] = field(default_factory=tuple)
    """Evidence that contradicts the current assessment."""
    
    unresolved: Tuple[SalienceEvidence, ...] = field(default_factory=tuple)
    """Evidence present but not yet classified."""
    
    cues: Tuple[str, ...] = field(default_factory=tuple)
    """
    Ids of cues (potential evidence):
        - Cues are indications that may become evidence
        - Cues are not promoted to evidence without validation
    """
    
    hypotheses: Tuple[str, ...] = field(default_factory=tuple)
    """
    Ids of hypotheses (possible interpretations):
        - Hypotheses are pending validation
        - Hypotheses are not conclusions until validated
    """
    
    completeness: str = field(default="unknown")
    """Semantic assessment of evidence completeness."""
    
    authority_id: str = field(default="")
    """Authority responsible for evidence composition."""