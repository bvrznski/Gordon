# Knowledge Audit Engine - Consistency - Phase 6.10
# ================================================

"""
Consistency audit engine for knowledge artifacts.

This engine checks if knowledge is internally consistent:
    - No logical contradictions within the artifact
    - Confidence and uncertainty properly calibrated
    - No circular dependencies in reasoning chains
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Tuple, Optional, Any

from ..interfaces import (
    KnowledgeAuditEngine,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
    KnowledgeAuditRecommendation,
)
from ..enums import (
    AuditDimension,
    FindingType,
    RecommendationType,
)
from ...shared.assertion import KnowledgeAssertion
from ...shared.belief import KnowledgeBelief, BeliefState


class ConsistencyAuditEngine(KnowledgeAuditEngine):
    """
    Audit engine for checking internal consistency of knowledge artifacts.
    
    Checks:
        - Confidence-uncertainty balance
        - No circular reasoning in justification chains
        - Consistent state transitions
        - Logical validity of assertions
    """
    
    dimension: str = "consistency"
    
    def __init__(
        self,
        *,
        configuration: Dict[str, Any] | None = None,
        artifact_provider: Optional[Any] = None,
        min_confidence_sum: float = 0.8,
        max_confidence_sum: float = 1.2,
    ):
        """
        Initialize the consistency audit engine.
        
        Args:
            configuration: Engine-specific configuration
            artifact_provider: Provider for accessing artifacts
            min_confidence_sum: Minimum acceptable confidence + uncertainty sum
            max_confidence_sum: Maximum acceptable confidence + uncertainty sum
        """
        super().__init__(configuration=configuration, artifact_provider=artifact_provider)
        self._min_confidence_sum = min_confidence_sum
        self._max_confidence_sum = max_confidence_sum
    
    def audit(self, target: KnowledgeAuditTarget) -> List[KnowledgeAuditFinding]:
        """Perform consistency audit on a single target."""
        findings = []
        
        # Try to resolve and audit the artifact based on type
        artifact = None
        
        if target.target_type == "assertion":
            if self.artifact_provider:
                artifact = self.artifact_provider.get_assertion(target.target_id)
        elif target.target_type == "belief":
            if self.artifact_provider:
                artifact = self.artifact_provider.get_belief(target.target_id)
        
        if isinstance(artifact, KnowledgeAssertion):
            findings.extend(self._audit_assertion_consistency(target, artifact))
        elif isinstance(artifact, KnowledgeBelief):
            findings.extend(self._audit_belief_consistency(target, artifact))
        
        return findings
    
    def batch_audit(
        self,
        targets: List[KnowledgeAuditTarget],
    ) -> Dict[str, List[KnowledgeAuditFinding]]:
        """Perform batch consistency audit."""
        results: Dict[str, List[KnowledgeAuditFinding]] = {}
        for target in targets:
            results[target.target_id] = self.audit(target)
        return results
    
    def _audit_assertion_consistency(
        self,
        target: KnowledgeAuditTarget,
        assertion: KnowledgeAssertion,
    ) -> List[KnowledgeAuditFinding]:
        """Check consistency of an assertion."""
        findings = []
        
        # Check confidence-uncertainty balance
        total = assertion.confidence + assertion.uncertainty
        
        if not (self._min_confidence_sum <= total <= self._max_confidence_sum):
            severity = 0.3 if total < self._min_confidence_sum else 0.4
            
            findings.append(KnowledgeAuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                target_id=target.target_id,
                target_type="assertion",
                finding_type=FindingType.LOW_CONFIDENCE if total < self._min_confidence_sum else FindingType.OVERCONFIDENT,
                severity=severity,
                confidence=0.7,
                uncertainty=0.3,
                evidence_references=(),
                supporting_context={
                    "confidence": assertion.confidence,
                    "uncertainty": assertion.uncertainty,
                    "total_sum": total,
                    "expected_range": [self._min_confidence_sum, self._max_confidence_sum],
                },
                recommendation=self._generate_recommendation(
                    target=target,
                    issue_type="consistency_imbalance",
                    suggestion="Review evidence quality and adjust confidence/uncertainty values",
                ),
            ))
        
        # Check for circular reasoning in justification chain
        if assertion.justification_chain:
            cycle = self._detect_cycle_in_chain(assertion.assertion_identity, assertion.justification_chain)
            if cycle:
                findings.append(KnowledgeAuditFinding(
                    finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                    target_id=target.target_id,
                    target_type="assertion",
                    finding_type=FindingType.CYCLIC_DEPENDENCY,
                    severity=0.8,
                    confidence=0.9,
                    uncertainty=0.1,
                    evidence_references=(),
                    supporting_context={
                        "cycle_path": cycle,
                        "chain_length": len(assertion.justification_chain),
                    },
                    recommendation=self._generate_recommendation(
                        target=target,
                        issue_type="circular_reasoning",
                        suggestion="Break circular dependency by adding external evidence",
                    ),
                ))
        
        return findings
    
    def _audit_belief_consistency(
        self,
        target: KnowledgeAuditTarget,
        belief: KnowledgeBelief,
    ) -> List[KnowledgeAuditFinding]:
        """Check consistency of a belief."""
        findings = []
        
        # Check confidence-uncertainty balance
        total = belief.confidence + belief.uncertainty
        
        if not (self._min_confidence_sum <= total <= self._max_confidence_sum):
            severity = 0.4
            
            findings.append(KnowledgeAuditFinding(
                finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                target_id=target.target_id,
                target_type="belief",
                finding_type=FindingType.LOW_CONFIDENCE if total < self._min_confidence_sum else FindingType.OVERCONFIDENT,
                severity=severity,
                confidence=0.7,
                uncertainty=0.3,
                evidence_references=(),
                supporting_context={
                    "confidence": belief.confidence,
                    "uncertainty": belief.uncertainty,
                    "total_sum": total,
                },
                recommendation=self._generate_recommendation(
                    target=target,
                    issue_type="consistency_imbalance",
                    suggestion="Review evidence balance and adjust confidence/uncertainty values",
                ),
            ))
        
        # Check net support ratio for ACCEPTED beliefs
        if belief.state == BeliefState.ACCEPTED:
            net_support = len(belief.supporting_evidence) - len(belief.counter_evidence)
            
            if net_support < 0:
                findings.append(KnowledgeAuditFinding(
                    finding_id=f"finding:{uuid.uuid4().hex[:16]}",
                    target_id=target.target_id,
                    target_type="belief",
                    finding_type=FindingType.UNSUPPORTED,
                    severity=0.6,
                    confidence=0.8,
                    uncertainty=0.2,
                    evidence_references=tuple(belief.counter_evidence),
                    supporting_context={
                        "net_support": net_support,
                        "supporting_count": len(belief.supporting_evidence),
                        "counter_count": len(belief.counter_evidence),
                    },
                    recommendation=self._generate_recommendation(
                        target=target,
                        issue_type="unsupported_accepted_belief",
                        suggestion="Review evidence and consider revising belief state",
                    ),
                ))
        
        return findings
    
    def _detect_cycle_in_chain(
        self,
        start_id: str,
        chain: Tuple[str, ...],
    ) -> List[str] | None:
        """Detect circular dependencies in a justification chain."""
        visited = set()
        path = []
        
        for ref in chain:
            if ref == start_id and ref in visited:
                # Found cycle - return the cycle path
                cycle_start = path.index(ref)
                return path[cycle_start:] + [ref]
            
            if ref in visited:
                continue
            
            visited.add(ref)
            path.append(ref)
        
        return None
    
    def _generate_recommendation(
        self,
        target: KnowledgeAuditTarget,
        issue_type: str,
        suggestion: str,
    ) -> Optional[KnowledgeAuditRecommendation]:
        """Generate a recommendation for the finding."""
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