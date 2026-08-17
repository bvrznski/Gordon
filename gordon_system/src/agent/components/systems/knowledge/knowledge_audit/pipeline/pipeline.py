# Knowledge Audit Pipeline - Phase 6.10
# =====================================

"""
Knowledge Audit Pipeline implementation.

The pipeline orchestrates the complete audit process:
    1. Knowledge Selection
    2. Artifact Loading
    3. Dependency Resolution
    4. Evidence Collection
    5. Consistency Audit
    6. Contradiction Audit
    7. Confidence Audit
    8. Freshness Audit
    9. Coverage Audit
    10. Dependency Audit
    11. Usage Audit
    12. Applicability Audit
    13. Finding Generation
    14. Recommendation Generation
    15. Audit Report

Each step is independently executable and produces findings.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.interfaces import (
    KnowledgeAuditEngine,
    KnowledgeAuditSession,
    KnowledgeAuditRequest,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
    KnowledgeAuditRecommendation,
    KnowledgeAuditReport,
    AuditReportGenerator,
    KnowledgeHealth,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.enums import (
    AuditDimension,
    FindingType,
    RecommendationType,
)


@dataclass
class PipelineContext:
    """Context passed through the audit pipeline."""
    
    request_id: str
    session_id: str
    timestamp_utc: float = field(default_factory=time.time)
    findings: Dict[str, List[KnowledgeAuditFinding]] = field(default_factory=dict)
    recommendations: Dict[str, List[KnowledgeAuditRecommendation]] = field(default_factory=dict)
    health_metrics: KnowledgeHealth | None = None
    
    def add_findings(self, target_id: str, findings: List[KnowledgeAuditFinding]) -> "PipelineContext":
        """Add findings for a target."""
        if target_id not in self.findings:
            self.findings[target_id] = []
        self.findings[target_id].extend(findings)
        return self
    
    def add_recommendations(self, target_id: str, recommendations: List[KnowledgeAuditRecommendation]) -> "PipelineContext":
        """Add recommendations for a target."""
        if target_id not in self.recommendations:
            self.recommendations[target_id] = []
        self.recommendations[target_id].extend(recommendations)
        return self


class KnowledgeAuditPipeline:
    """
    Orchestrates the complete knowledge audit process.
    
    The pipeline executes all configured audit engines and aggregates results
    into a comprehensive audit report with health metrics and recommendations.
    """
    
    def __init__(
        self,
        engines: Dict[AuditDimension, KnowledgeAuditEngine],
        *,
        report_generator: Optional[AuditReportGenerator] = None,
        max_workers: int = 4,
    ):
        """
        Initialize the audit pipeline.
        
        Args:
            engines: Mapping from dimension to audit engine
            report_generator: Generator for final reports (optional)
            max_workers: Maximum concurrent workers for batch audits
        """
        self._engines = dict(engines)
        self._report_generator = report_generator
        self._max_workers = max_workers
    
    @property
    def engines(self) -> Dict[AuditDimension, KnowledgeAuditEngine]:
        """Get all audit engines."""
        return dict(self._engines)
    
    def execute(
        self,
        session: KnowledgeAuditSession,
    ) -> Tuple[KnowledgeHealth, Dict[str, List[KnowledgeAuditFinding]], Optional[KnowledgeAuditReport]]:
        """
        Execute the audit pipeline for a session.
        
        Args:
            session: The audit session to execute
            
        Returns:
            Tuple of (health_metrics, all_findings, optional_report)
        """
        context = PipelineContext(
            request_id=session.request_id,
            session_id=session.session_id,
        )
        
        # Step 1-4: Pre-processing
        context = self._pre_process(session, context)
        
        # Step 5-12: Execute audit engines
        context = self._execute_engines(session, context)
        
        # Steps 13-14: Generate findings and recommendations
        context = self._generate_findings_and_recommendations(context)
        
        # Step 15: Generate report
        report = None
        if session.audit_request.generate_report:
            report = self._generate_final_report(session, context)
        
        return context.health_metrics or KnowledgeHealth.empty(), context.findings, report
    
    def _pre_process(
        self,
        session: KnowledgeAuditSession,
        context: PipelineContext,
    ) -> PipelineContext:
        """Pre-processing step: artifact loading and dependency resolution."""
        # In a real implementation, this would load artifacts and resolve dependencies
        return context
    
    def _execute_engines(
        self,
        session: KnowledgeAuditSession,
        context: PipelineContext,
    ) -> PipelineContext:
        """Execute all configured audit engines on targets."""
        
        # Get targets for the session
        targets = []
        for target_id in session.target_ids:
            target_type = session.target_types.get(target_id, "unknown")
            targets.append(KnowledgeAuditTarget(
                target_id=target_id,
                target_type=target_type,
            ))
        
        # Execute engines concurrently if configured
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_engine: Dict[Any, Tuple[AuditDimension, KnowledgeAuditEngine]] = {}
            
            for dimension, engine in self._engines.items():
                if not session.audit_request.dimensions or dimension in session.audit_request.dimensions:
                    # Check if this dimension is specified
                    futures: List[Any] = []
                    
                    if len(targets) > 1:
                        future = executor.submit(engine.batch_audit, targets)
                        futures.append(future)
                    elif targets:
                        findings = engine.audit(targets[0])
                        context.add_findings(targets[0].target_id, findings)
                        continue
                    
                    for future in futures:
                        try:
                            results = future.result()
                            for target_id, findings in results.items():
                                context.add_findings(target_id, findings)
                        except Exception as e:
                            # Log error but continue with other engines
                            pass
        
        return context
    
    def _generate_findings_and_recommendations(
        self,
        context: PipelineContext,
    ) -> PipelineContext:
        """Generate recommendations based on findings."""
        
        for target_id, findings in context.findings.items():
            for finding in findings:
                if not finding.recommendation and finding.finding_type != FindingType.SUPPORTED:
                    # Generate a default recommendation
                    rec = self._generate_default_recommendation(finding)
                    if rec:
                        context.add_recommendations(target_id, [rec])
        
        return context
    
    def _generate_default_recommendation(
        self,
        finding: KnowledgeAuditFinding,
    ) -> Optional[KnowledgeAuditRecommendation]:
        """Generate a default recommendation for a finding."""
        
        if finding.finding_type in (
            FindingType.UNSUPPORTED,
            FindingType.LOW_CONFIDENCE,
            FindingType.WEAK_EVIDENCE,
        ):
            return KnowledgeAuditRecommendation(
                recommendation_id=f"rec:{uuid.uuid4().hex[:16]}",
                recommendation_type=RecommendationType.VERIFY,
                rationale="Audit identified insufficient support for this knowledge artifact",
                priority=0.5,
                required_context={
                    "finding_type": finding.finding_type.value,
                    "target_id": finding.target_id,
                },
            )
        
        elif finding.finding_type in (
            FindingType.CONTRADICTED,
            FindingType.CYCLIC_DEPENDENCY,
            FindingType.BROKEN_DEPENDENCY,
        ):
            return KnowledgeAuditRecommendation(
                recommendation_id=f"rec:{uuid.uuid4().hex[:16]}",
                recommendation_type=RecommendationType.RELEARN,
                rationale="Audit identified contradiction that requires re-evaluation",
                priority=0.8,
                required_context={
                    "finding_type": finding.finding_type.value,
                    "target_id": finding.target_id,
                },
            )
        
        elif finding.finding_type in (
            FindingType.OBSOLETE,
            FindingType.SUPERSEDED,
        ):
            return KnowledgeAuditRecommendation(
                recommendation_id=f"rec:{uuid.uuid4().hex[:16]}",
                recommendation_type=RecommendationType.ARCHIVE,
                rationale="Knowledge artifact may be outdated and should be reviewed for archival",
                priority=0.3,
                required_context={
                    "finding_type": finding.finding_type.value,
                    "target_id": finding.target_id,
                },
            )
        
        return None
    
    def _generate_final_report(
        self,
        session: KnowledgeAuditSession,
        context: PipelineContext,
    ) -> KnowledgeAuditReport:
        """Generate the final audit report."""
        
        all_findings = []
        for findings in context.findings.values():
            all_findings.extend(findings)
        
        # Compute health metrics
        critical_count = sum(1 for f in all_findings if f.is_critical)
        warning_count = sum(1 for f in all_findings if f.is_warning)
        info_count = sum(1 for f in all_findings if f.is_info)
        
        overall_score = 1.0 - (critical_count * 0.2 + warning_count * 0.1) / max(len(all_findings), 1)
        overall_score = max(0.0, min(1.0, overall_score))
        
        health_metrics = KnowledgeHealth(
            health_id=f"health:{uuid.uuid4().hex[:16]}",
            timestamp_utc=context.timestamp_utc,
            overall_score=overall_score,
            coverage_score=0.5,
            consistency_score=0.5,
            evidence_score=0.5,
            total_findings=len(all_findings),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
        )
        
        # Create report
        report = KnowledgeAuditReport(
            report_id=f"report:{uuid.uuid4().hex[:16]}",
            session_id=session.session_id,
            created_at_utc=context.timestamp_utc,
            audit_dimensions=tuple(d.value for d in self._engines.keys()),
            total_targets=len(session.target_ids),
            all_findings=tuple(all_findings),
            health_metrics=health_metrics,
            summary={
                "dimensions_audited": len(self._engines),
                "targets_audited": len(session.target_ids),
                "critical_findings": critical_count,
                "warning_findings": warning_count,
                "info_findings": info_count,
                "overall_health_score": overall_score,
            },
        )
        
        return report


__all__ = [
    "KnowledgeAuditPipeline",
    "PipelineContext",
]