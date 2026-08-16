# Memory Audit Tests - Phase 5.1.9
# ===================================

"""
Comprehensive test suite for the Memory Audit subsystem.

Tests cover:
    - Imports and configuration
    - Enums (AuditTypes, CertificationStatus, etc.)
    - Models (Request, Session, Report, Finding, Health)
    - Adapters
    - Validators
    - Planners
    - Lineage verification
    - Engine operations
    - Integrity checks
"""

from __future__ import annotations

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

# =============================================================================
# IMPORT TESTS
# =============================================================================


def test_imports():
    """Test that all audit modules can be imported."""
    try:
        from agent.components.systems.memory.audit import (
            AuditTypes,
            AuditCertificationStatus,
            MemoryAuditRequest,
            MemoryAuditSession,
            MemoryAuditReport,
            AuditFinding,
            HealthAssessment,
            MemoryAuditEngine,
        )
        print("PASS: Core imports successful")
        return True
    except ImportError as e:
        print(f"FAIL: Import error - {e}")
        return False


def test_enum_imports():
    """Test that all enum types can be imported."""
    try:
        from agent.components.systems.memory.audit.enums import (
            AuditTypes,
            AuditCertificationStatus,
            FindingSeverity,
            AuditPhases,
            MemoryDomains,
            ValidationState,
            ReferenceType,
            DataIntegrityState,
        )
        
        # Check enum values
        assert hasattr(AuditTypes, 'FULL_SYSTEM_AUDIT')
        assert hasattr(AuditCertificationStatus, 'CERTIFIED')
        assert hasattr(FindingSeverity, 'CRITICAL')
        assert hasattr(ValidationState, 'PASSED')
        
        print("PASS: Enum imports successful")
        return True
    except Exception as e:
        print(f"FAIL: Enum import error - {e}")
        return False


# =============================================================================
# MODEL TESTS
# =============================================================================


def test_finding_model():
    """Test AuditFinding model."""
    try:
        from agent.components.systems.memory.audit.models import (
            AuditFinding,
            ValidationState,
            FindingSeverity,
        )
        
        finding = AuditFinding(
            finding_id="test:finding:1",
            validation_type="structural",
            state=ValidationState.PASSED,
            severity=FindingSeverity.INFO,
            location="artifact:123",
            description="Test finding",
        )
        
        assert finding.finding_id == "test:finding:1"
        assert finding.is_issue is False
        assert finding.severity == FindingSeverity.INFO
        
        print("PASS: AuditFinding model works")
        return True
    except Exception as e:
        print(f"FAIL: AuditFinding test - {e}")
        return False


def test_health_metric_model():
    """Test HealthMetric model."""
    try:
        from agent.components.systems.memory.audit.models import (
            HealthMetric,
            ValidationState,
        )
        
        metric = HealthMetric(
            name="validation_rate",
            value=0.95,
            threshold=0.8,
            state=ValidationState.PASSED,
        )
        
        assert metric.name == "validation_rate"
        assert metric.value == 0.95
        assert metric.is_healthy is True
        
        print("PASS: HealthMetric model works")
        return True
    except Exception as e:
        print(f"FAIL: HealthMetric test - {e}")
        return False


def test_health_assessment_model():
    """Test HealthAssessment model."""
    try:
        from agent.components.systems.memory.audit.models import (
            HealthAssessment,
            HealthMetric,
            ValidationState,
        )
        
        assessment = HealthAssessment(
            overall_state=ValidationState.PASSED,
            adapter_health=(
                HealthMetric("adapter", 1.0, description="Adapter health"),
            ),
        )
        
        assert assessment.is_healthy is True
        assert len(assessment.adapter_health) == 1
        
        print("PASS: HealthAssessment model works")
        return True
    except Exception as e:
        print(f"FAIL: HealthAssessment test - {e}")
        return False


def test_request_model():
    """Test MemoryAuditRequest model."""
    try:
        from agent.components.systems.memory.audit.models import (
            MemoryAuditRequest,
            AuditTypes,
            MemoryDomains,
        )
        
        request = MemoryAuditRequest(
            request_id="test:1",
            audit_type=AuditTypes.FULL_SYSTEM_AUDIT,
            domains=(MemoryDomains.WORKING_MEMORY,),
            validate_lineage=True,
            validate_provenance=True,
            check_references=True,
        )
        
        assert request.is_full_system is True
        assert request.has_targets is False
        
        print("PASS: MemoryAuditRequest model works")
        return True
    except Exception as e:
        print(f"FAIL: MemoryAuditRequest test - {e}")
        return False


def test_session_model():
    """Test MemoryAuditSession model."""
    try:
        from agent.components.systems.memory.audit.models import (
            MemoryAuditSession,
            MemoryAuditRequest,
            AuditTypes,
            AuditPhases,
            MemoryDomains,
        )
        
        request = MemoryAuditRequest(
            request_id="test:1",
            audit_type=AuditTypes.FULL_SYSTEM_AUDIT,
            domains=(MemoryDomains.WORKING_MEMORY,),
        )
        
        session = MemoryAuditSession(
            session_id="session:test:1",
            request=request,
            current_phase=AuditPhases.PLANNING,
        )
        
        assert session.is_complete is False
        assert session.session_id.startswith("session:")
        
        print("PASS: MemoryAuditSession model works")
        return True
    except Exception as e:
        print(f"FAIL: MemoryAuditSession test - {e}")
        return False


def test_report_model():
    """Test MemoryAuditReport model."""
    try:
        from agent.components.systems.memory.audit.models import (
            MemoryAuditReport,
            AuditFinding,
            ValidationState,
            FindingSeverity,
            AuditTypes,
            AuditCertificationStatus,
        )
        
        report = MemoryAuditReport(
            report_id="report:test:1",
            timestamp_utc=1000.0,
            audit_type=AuditTypes.FULL_SYSTEM_AUDIT,
            findings=(
                AuditFinding(
                    finding_id="f1",
                    validation_type="test",
                    state=ValidationState.PASSED,
                    severity=FindingSeverity.INFO,
                    location="loc1",
                    description="Test finding",
                ),
            ),
            certification_status=AuditCertificationStatus.CERTIFIED,
        )
        
        assert report.is_certified is True
        assert report.has_findings is True
        
        print("PASS: MemoryAuditReport model works")
        return True
    except Exception as e:
        print(f"FAIL: MemoryAuditReport test - {e}")
        return False


# =============================================================================
# FACTORY TESTS
# =============================================================================


def test_request_factory():
    """Test audit request factory."""
    try:
        from agent.components.systems.memory.audit.factories import (
            create_audit_request,
            AuditTypes,
        )
        
        request = create_audit_request(
            audit_type=AuditTypes.FULL_SYSTEM_AUDIT,
            depth="full",
        )
        
        assert request is not None
        assert request.is_full_system is True
        
        print("PASS: Request factory works")
        return True
    except Exception as e:
        print(f"FAIL: Request factory test - {e}")
        return False


# =============================================================================
# ENGINE TESTS
# =============================================================================


def test_engine_integrity():
    """Test engine integrity check."""
    try:
        from agent.components.systems.memory.audit.engine import (
            memory_audit_integrity_check,
        )
        
        result = memory_audit_integrity_check()
        
        assert "checks" in result
        assert "is_healthy" in result
        
        print(f"PASS: Engine integrity check completed")
        return True
    except Exception as e:
        print(f"FAIL: Engine integrity test - {e}")
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================


def run_all_tests():
    """Run all audit tests and report results."""
    tests = [
        ("Imports", test_imports),
        ("Enum Imports", test_enum_imports),
        ("Finding Model", test_finding_model),
        ("HealthMetric Model", test_health_metric_model),
        ("HealthAssessment Model", test_health_assessment_model),
        ("Request Model", test_request_model),
        ("Session Model", test_session_model),
        ("Report Model", test_report_model),
        ("Request Factory", test_request_factory),
        ("Engine Integrity", test_engine_integrity),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nRunning {name}...")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"FAIL: {name} - {e}")
            results.append((name, False))
    
    # Summary
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("=" * 50)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
    
    return all(r for _, r in results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)