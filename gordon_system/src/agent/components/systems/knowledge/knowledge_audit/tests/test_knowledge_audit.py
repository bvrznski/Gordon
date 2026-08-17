# Knowledge Audit Tests - Phase 6.10
# ====================================

"""
Test suite for the Knowledge Audit subsystem.
"""

from __future__ import annotations

import pytest
import time
import uuid
from typing import Dict, List, Optional

from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.interfaces import (
    KnowledgeAuditEngine,
    KnowledgeAuditSession,
    KnowledgeAuditRequest,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
    KnowledgeAuditRecommendation,
    KnowledgeAuditReport,
    AuditDimension,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.enums import (
    FindingType,
    RecommendationType,
    AuditStatus,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.exceptions import (
    InvalidAuditRequest,
    AuditRequestTimeout,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.pipeline import (
    KnowledgeAuditPipeline,
    PipelineContext,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.sessions import (
    ActiveSession,
    KnowledgeAuditSessionFactory,
)

from gordon_system.src.agent.components.systems.knowledge.shared.assertion import KnowledgeAssertion, AssertionState
from gordon_system.src.agent.components.systems.knowledge.shared.belief import KnowledgeBelief, BeliefState


# =============================================================================
# TEST FIXTURES
# =============================================================================

class MockKnowledgeArtifactProvider:
    """Mock provider for testing audit engines."""
    
    def __init__(self):
        self._assertions: Dict[str, KnowledgeAssertion] = {}
        self._beliefs: Dict[str, KnowledgeBelief] = {}
    
    def get_assertion(self, assertion_id: str) -> Optional[KnowledgeAssertion]:
        return self._assertions.get(assertion_id)
    
    def get_belief(self, belief_id: str) -> Optional[KnowledgeBelief]:
        return self._beliefs.get(belief_id)
    
    def add_assertion(self, assertion: KnowledgeAssertion) -> None:
        self._assertions[assertion.assertion_identity] = assertion
    
    def add_belief(self, belief: KnowledgeBelief) -> None:
        self._beliefs[belief.belief_identity] = belief


class TestAuditEngine(KnowledgeAuditEngine):
    """Test audit engine for verification."""
    
    dimension: str = "test"
    
    def audit(self, target: KnowledgeAuditTarget) -> List[KnowledgeAuditFinding]:
        return []
    
    def batch_audit(
        self,
        targets: List[KnowledgeAuditTarget],
    ) -> Dict[str, List[KnowledgeAuditFinding]]:
        return {t.target_id: [] for t in targets}


# =============================================================================
# TEST CASES
# =============================================================================

class TestKnowledgeAuditRequest:
    """Test KnowledgeAuditRequest model."""
    
    def test_create_all(self):
        """Test creating a request to audit all knowledge."""
        req = KnowledgeAuditRequest.create_all()
        
        assert req.request_id.startswith("request:")
        assert len(req.target_ids) == 0
        assert len(req.dimensions) == 0
    
    def test_create_for_targets(self):
        """Test creating a request for specific targets."""
        target_ids = ["assertion:1", "belief:2"]
        dimensions = [AuditDimension.CONSISTENCY]
        
        req = KnowledgeAuditRequest.create_for_targets(target_ids, dimensions)
        
        assert len(req.target_ids) == 2
        assert AuditDimension.CONSISTENCY in req.dimensions
    
    def test_invalid_timeout(self):
        """Test that invalid timeout raises error."""
        with pytest.raises(InvalidAuditRequest):
            KnowledgeAuditRequest(
                request_id="test",
                target_ids=(),
                timeout_seconds=0,
            )


class TestKnowledgeAuditEngine:
    """Test audit engine interface and base implementation."""
    
    def test_engine_creation(self):
        """Test engine can be instantiated."""
        provider = MockKnowledgeArtifactProvider()
        engine = TestAuditEngine(artifact_provider=provider)
        
        assert engine.engine_id.startswith("engine:")
        assert engine.artifact_provider is provider
    
    def test_config_access(self):
        """Test configuration access methods."""
        config = {"test_param": 42}
        engine = TestAuditEngine(configuration=config)
        
        assert engine.get_config("test_param") == 42
        engine.set_config("new_key", "value")
        assert engine.get_config("new_key") == "value"


class TestKnowledgeAuditFinding:
    """Test KnowledgeAuditFinding model."""
    
    def test_finding_severity_levels(self):
        """Test severity level classifications."""
        finding = KnowledgeAuditFinding(
            finding_id="finding:1",
            target_id="artifact:1",
            target_type="test",
            finding_type=FindingType.UNSUPPORTED,
            severity=0.85,  # Critical
        )
        
        assert finding.is_critical is True
        assert finding.is_warning is False
        assert finding.is_info is False
    
    def test_finding_to_dict(self):
        """Test finding serialization."""
        rec = KnowledgeAuditRecommendation(
            recommendation_id="rec:1",
            recommendation_type=RecommendationType.VERIFY,
            rationale="Test reason",
            priority=0.5,
        )
        
        finding = KnowledgeAuditFinding(
            finding_id="finding:1",
            target_id="artifact:1",
            target_type="test",
            finding_type=FindingType.UNSUPPORTED,
            recommendation=rec,
        )
        
        data = finding.to_dict()
        
        assert data["finding_id"] == "finding:1"
        assert data["target_id"] == "artifact:1"
        assert data["recommendation"]["rationale"] == "Test reason"


class TestKnowledgeAuditPipeline:
    """Test KnowledgeAuditPipeline orchestration."""
    
    def test_pipeline_creation(self):
        """Test pipeline can be created with engines."""
        engine = TestAuditEngine()
        pipeline = KnowledgeAuditPipeline(
            engines={AuditDimension.TEST: engine},
        )
        
        assert len(pipeline.engines) == 1
    
    def test_session_creation(self):
        """Test creating an audit session from factory."""
        provider = MockKnowledgeArtifactProvider()
        factory = KnowledgeAuditSessionFactory()
        
        request = KnowledgeAuditRequest.create_all()
        
        immutable, active = factory.create_from_request(
            request=request,
            target_ids=["artifact:1"],
            target_types={"artifact:1": "test"},
        )
        
        assert immutable.status == AuditStatus.PENDING
        assert active.is_running is True


class TestKnowledgeAuditSession:
    """Test KnowledgeAuditSession model."""
    
    def test_session_state_transitions(self):
        """Test session state properties."""
        request = KnowledgeAuditRequest.create_all()
        
        session = KnowledgeAuditSession.create_pending(
            request=request,
            target_ids=["artifact:1"],
            target_types={"artifact:1": "test"},
        )
        
        assert session.is_active is False
        assert session.status == AuditStatus.PENDING
    
    def test_session_report(self):
        """Test session with report."""
        request = KnowledgeAuditRequest.create_all()
        
        report = KnowledgeAuditReport(
            report_id="report:1",
            session_id="session:1",
            created_at_utc=time.time(),
            audit_dimensions=("consistency",),
            total_targets=1,
            all_findings=(),
            health_metrics=None,
            summary={},
        )
        
        findings_dict: Dict[str, tuple] = {}
        
        session = KnowledgeAuditSession(
            session_id="session:1",
            request_id=request.request_id,
            audit_request=request,
            target_ids=tuple(request.target_ids),
            target_types={},
            status=AuditStatus.COMPLETED,
            started_at_utc=time.time(),
            completed_at_utc=time.time(),
            findings=findings_dict,
            report=report,
        )
        
        assert session.is_completed is True

# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])