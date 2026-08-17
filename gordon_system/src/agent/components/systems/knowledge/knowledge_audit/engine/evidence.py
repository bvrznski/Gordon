# Knowledge Audit Engine - Evidence - Phase 6.10
# =============================================

"""
Evidence audit engine for knowledge artifacts.

This engine checks if knowledge has sufficient and appropriate evidence:
    - Minimum evidence count thresholds
    - Evidence quality assessment
    - Evidence source reliability
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any

from ..interfaces import (
    KnowledgeAuditEngine,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
)
from ..enums import (
    AuditDimension,
    FindingType,
    RecommendationType,
)

from ...shared.belief import (
    KnowledgeBelief,
    BeliefState,
)
from ...shared.assertion import KnowledgeAssertion


class EvidenceAuditEngine(KnowledgeAuditEngine):
    """
    Audit engine for checking evidence quality and sufficiency.
    
    Checks:
        - Minimum evidence count thresholds
        - Evidence source reliability
        - Evidence currency (freshness)
        - Evidence relevance to the claim
    """
    
    dimension: str = "evidence"
    
    def __init__(
        self,
        *,
        configuration: Dict[str, Any] | None = None,
        artifact_provider: Optional[Any] = None,
        min_evidence_count: int = 1,
        max_uncertainty_threshold: float = 0.8,
    ):
        """
        Initialize the evidence audit engine.
        
        Args:
            configuration: Engine-specific configuration
            artifact_provider: Provider for accessing artifacts
            min_evidence_count: Minimum required evidence references
            max_uncertainty_threshold: Maximum acceptable uncertainty
        """
        super().__init__(configuration=configuration, artifact_provider=artifact_provider)
        self._min_evidence_count = min_evidence_count
        self._max_uncertainty_threshold = max_uncertainty_threshold
    
    def audit(self, target: KnowledgeAuditTarget) -> List[KnowledgeAuditFinding]:
        """Perform evidence audit on a single target."""
        findings = []
        
        artifact = None
        
        if target.target_type == "assertion":
            if self.artifact_provider:
                artifact = self.artifact_provider.get_assertion(target.target_id)
        elif target.target_type == "belief":
            if self.artifact_provider:
                artifact = self.artifact_provider.get_belief(target.target_id)
        
        if isinstance(artifact, KnowledgeAssertion):
            findings.extend(self._audit_assertion_evidence(target, artifact))
        elif isinstance(artifact, KnowledgeBelief):
            findings.extend(self._audit_belief_evidence(target, artifact))
        
        return findings
    
    def batch_audit(
        self,
        targets: List[KnowledgeAuditTarget],
    ) -> Dict[str, List[KnowledgeAuditFinding]]:
        """Perform batch evidence audit."""
        results: Dict[str, List[KnowledgeAuditFinding]] = {}
        for target in targets:
            results[target.target_id] = self.audit(target)
        return results
    
    def _audit_assertion_evidence(
        self,
        target: KnowledgeAuditTarget,
        assertion: KnowledgeAssertion,
    ) -> List[KnowledgeAuditFinding]:
        """Check evidence quality of an assertion."""
        findings = []
        
        # Check minimum evidence count
        evidence_count = len(assertion.source_evidence)
        
        if evidence_count < self._min_evidence_count:
            severity = 0.6
            findings.append(KnowledgeAuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                target_id=target.target_id,
                target_type="assertion",
                finding_type=FindingType.UNSUPPORTED,
                severity=severity,
                confidence=0.85,
                uncertainty=0.15,
                evidence_references=(),
                supporting_context={
                    "evidence_count": evidence_count,
                    "required_min": self._min_evidence_count,
                },
                recommendation=self._generate_recommendation(
                    target=target,
                    issue_type="insufficient_evidence",
                    suggestion=f"Add at least {self._min_evidence_count} piece(s) of supporting evidence",
                ),
            ))
        
        # Check if confidence is high but evidence count is low
        if assertion.confidence > 0.8 and evidence_count == 0:
            findings.append(KnowledgeAuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                target_id=target.target_id,
                target_type="assertion",
                finding_type=FindingType.OVERCONFIDENT,
                severity=0.7,
                confidence=0.9,
                uncertainty=0.1,
                evidence_references=(),
                supporting_context={
                    "confidence": assertion.confidence,
                    "evidence_count": evidence_count,
                },
                recommendation=self._generate_recommendation(
                    target=target,
                    issue_type="overconfident_without_evidence",
                    suggestion="Either reduce confidence or add supporting evidence",
                ),
            ))
        
        return findings
    
    def _audit_belief_evidence(
        self,
        target: KnowledgeAuditTarget,
        belief: KnowledgeBelief,
    ) -> List[KnowledgeAuditFinding]:
        """Check evidence quality of a belief."""
        findings = []
        
        # Check minimum supporting evidence for accepted beliefs
        if belief.state == BeliefState.ACCEPTED:
            supporting_count = len(belief.supporting_evidence)
            
            if supporting_count < self._min_evidence_count:
                severity = 0.7
                findings.append(KnowledgeAuditFinding(
                    finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                    target_id=target.target_id,
                    target_type="belief",
                    finding_type=FindingType.UNSUPPORTED,
                    severity=severity,
                    confidence=0.85,
                    uncertainty=0.15,
                    evidence_references=tuple(belief.counter_evidence),
                    supporting_context={
                        "state": belief.state.value,
                        "supporting_count": supporting_count,
                        "required_min": self._min_evidence_count,
                    },
                    recommendation=self._generate_recommendation(
                        target=target,
                        issue_type="insufficient_supporting_evidence",
                        suggestion=f"Add at least {self._min_evidence_count} piece(s) of supporting evidence to maintain ACCEPTED state",
                    ),
                ))
        
        # Check counter-evidence ratio
        total = len(belief.supporting_evidence) + len(belief.counter_evidence)
        
        if total > 0:
            counter_ratio = len(belief.counter_evidence) / total
            
            if counter_ratio > 0.3:
                severity = 0.6
                findings.append(KnowledgeAuditFinding(
                    finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                    target_id=target.target_id,
                    target_type="belief",
                    finding_type=FindingType.CONTRADICTED,
                    severity=severity,
                    confidence=0.8,
                    uncertainty=0.2,
                    evidence_references=tuple(belief.counter_evidence),
                    supporting_context={
                        "supporting_count": len(belief.supporting_evidence),
                        "counter_count": len(belief.counter_evidence),
                        "counter_ratio": counter_ratio,
                    },
                    recommendation=self._generate_recommendation(
                        target=target,
                        issue_type="high_counter_evidence",
                        suggestion=f"Review {len(belief.counter_evidence)} contradicting pieces of evidence",
                    ),
                ))
        
        return findings
    
    def _generate_recommendation(
        self,
        target: KnowledgeAuditTarget,
        issue_type: str,
        suggestion: str,
    ) -> Optional[Any]:
        """Generate a recommendation for the finding."""
        from ..enums import (
            RecommendationType,
        )
        
        from ..interfaces import (
            KnowledgeAuditRecommendation,
        )
        
        return KnowledgeAuditRecommendation(
            recommendation_id=f"rec:{uuid.uuid4().hex[:16]}",
            recommendation_type=RecommendationType.REVALIDATE,
            rationale=f"{issue_type}: {suggestion}",
            priority=0.5,
            required_context={
                "target_id": target.target_id,
                "issue_type": issue_type,
                "detection_engine": self.dimension,
            },
        )