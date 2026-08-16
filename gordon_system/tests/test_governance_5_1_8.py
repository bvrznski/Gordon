# Memory Governance Tests - Phase 5.1.8

"""
Tests for Memory Governance System.

This module tests:
    - Governance state transitions
    - Evidence creation and verification
    - Violation recording
    - Report generation
    - Session management
"""

from __future__ import annotations

import sys
sys.path.insert(0, 'src')

# Test imports work correctly
try:
    from agent.components.systems.memory.governance import (
        MemoryGovernance,
        MemoryGovernanceSession,
        GovernanceState,
        GovernanceViolationType,
        GovernanceSeverity,
        GovernanceEvidence,
        GovernanceViolation,
        GovernanceReport,
    )
    print("PASS: Core governance imports successful")
except ImportError as e:
    print(f"FAIL: Import error - {e}")
    sys.exit(1)

# TestGovernanceStates
def test_governance_states():
    """Test GovernanceState enum values."""
    states = [s.value for s in GovernanceState]
    expected = ['initial', 'observing', 'evaluating', 'certifying', 'reporting', 'complete', 'failed']
    
    if set(states) == set(expected):
        print("PASS: GovernanceState enum has correct values")
    else:
        print(f"FAIL: Expected {expected}, got {states}")
        return False
    return True


def test_governance_evidence():
    """Test GovernanceEvidence creation."""
    evidence = GovernanceEvidence.create(
        evaluation_type="test_check",
        result={"status": "pass", "check_count": 5},
    )
    
    if evidence.evidence_id.startswith("evidence:"):
        print("PASS: Evidence ID format correct")
    else:
        print("FAIL: Evidence ID format incorrect")
        return False
    
    if evidence.is_pass:
        print("PASS: Evidence is_pass property works")
    else:
        print("FAIL: Evidence is_pass property incorrect")
        return False
    
    dict_repr = evidence.to_dict()
    if dict_repr["evaluation_type"] == "test_check":
        print("PASS: Evidence to_dict() works")
    else:
        print("FAIL: Evidence to_dict() incorrect")
        return False
    
    return True


def test_governance_violation():
    """Test GovernanceViolation creation."""
    violation = GovernanceViolation(
        violation_id="violation:test1",
        violation_type=GovernanceViolationType.INTEGRITY_VIOLATION,
        location="test_module",
        rule_name="INTEGRITY-LAW-001",
        severity=GovernanceSeverity.WARNING,
        description="Test violation for testing purposes",
    )
    
    if not violation.is_critical:
        print("PASS: Violation is_critical property works")
    else:
        print("FAIL: Violation is_critical incorrect")
        return False
    
    dict_repr = violation.to_dict()
    if dict_repr["severity"] == "warning":
        print("PASS: Violation to_dict() works")
    else:
        print("FAIL: Violation to_dict() incorrect")
        return False
    
    return True


def test_governance_report():
    """Test GovernanceReport creation."""
    violations = (
        GovernanceViolation(
            violation_id="v1",
            violation_type=GovernanceViolationType.COMPLIANCE_VIOLATION,
            location="test",
            rule_name="COMPLIANCE-LAW-001",
            severity=GovernanceSeverity.WARNING,
            description="Test warning",
        ),
    )
    
    report = GovernanceReport.create(
        evaluation_scope="integrity_test",
        status=GovernanceState.COMPLETE,
        certification_status=None,  # Not certified due to violations
        violations=violations,
    )
    
    if not report.is_certified:
        print("PASS: Report is_certified correct when violations present")
    else:
        print("FAIL: Report is_certified should be False with violations")
        return False
    
    if report.has_violations:
        print("PASS: Report has_violations property works")
    else:
        print("FAIL: Report has_violations should be True")
        return False
    
    dict_repr = report.to_dict()
    if len(dict_repr["violations"]) == 1:
        print("PASS: Report to_dict() preserves violations")
    else:
        print("FAIL: Report to_dict() violation count incorrect")
        return False
    
    return True


def test_governance_session():
    """Test MemoryGovernanceSession state transitions."""
    session = MemoryGovernanceSession(evaluation_target="test_system")
    
    if session.state == GovernanceState.INITIAL:
        print("PASS: Session starts in INITIAL state")
    else:
        print(f"FAIL: Expected INITIAL, got {session.state}")
        return False
    
    session.transition_to_observing()
    if session.state == GovernanceState.OBSERVING:
        print("PASS: transition_to_observing() works")
    else:
        print(f"FAIL: State after observing should be OBSERVING, got {session.state}")
        return False
    
    session.transition_to_evaluating()
    if session.state == GovernanceState.EVALUATING:
        print("PASS: transition_to_evaluating() works")
    else:
        print(f"FAIL: State after evaluating should be EVALUATING, got {session.state}")
        return False
    
    return True


def test_governance_severity():
    """Test GovernanceSeverity enum values."""
    severities = [s.value for s in GovernanceSeverity]
    expected = ['debug', 'info', 'warning', 'error', 'critical']
    
    if set(severities) == set(expected):
        print("PASS: GovernanceSeverity enum has correct values")
    else:
        print(f"FAIL: Expected {expected}, got {severities}")
        return False
    
    return True


def test_governance_violation_types():
    """Test GovernanceViolationType enum values."""
    types = [t.value for t in GovernanceViolationType]
    expected = [
        'integrity_violation',
        'compliance_violation',
        'audit_violation',
        'certification_violation',
        'repair_violation',
        'evolution_violation',
        'migration_violation',
    ]
    
    if set(types) == set(expected):
        print("PASS: GovernanceViolationType enum has correct values")
    else:
        print(f"FAIL: Expected {expected}, got {types}")
        return False
    
    return True


# Run all tests
def run_all_tests():
    """Run all governance tests."""
    tests = [
        ("Governance States", test_governance_states),
        ("Evidence Creation", test_governance_evidence),
        ("Violation Recording", test_governance_violation),
        ("Report Generation", test_governance_report),
        ("Session Transitions", test_governance_session),
        ("Severity Enum", test_governance_severity),
        ("Violation Types", test_governance_violation_types),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  -> FAILED: {name}")
        except Exception as e:
            print(f"  -> ERROR in {name}: {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"Governance Tests Complete: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)