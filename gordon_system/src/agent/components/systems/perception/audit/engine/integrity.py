# Perception Audit Integrity Check - Phase 5.2.6
# ===============================================

"""
Integrity validation for Perception Audit subsystem.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional


def perception_audit_integrity_check() -> Tuple[bool, List[str]]:
    """
    Perform integrity check on the perception audit system.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues: List[str] = []
    
    try:
        from gordon_system.src.agent.components.systems.perception.audit.engine.engine import PerceptionAuditEngine
        engine_instance = PerceptionAuditEngine()
        if not hasattr(engine_instance, 'audit'):
            issues.append("PerceptionAuditEngine missing audit method")
    except ImportError as e:
        issues.append(f"Cannot import PerceptionAuditEngine: {e}")
    
    try:
        from gordon_system.src.agent.components.systems.perception.audit.models import (
            PerceptionSnapshot,
            AuditFinding,
            PerceptionAuditReport,
        )
        
        snapshot = PerceptionSnapshot.create()
        if not hasattr(snapshot, 'visual_confidence'):
            issues.append("PerceptionSnapshot missing visual_confidence")
    except ImportError as e:
        issues.append(f"Cannot import models: {e}")
    
    try:
        from gordon_system.src.agent.components.systems.perception.audit.constants import (
            AuditSeverity,
            FindingType,
            AuditStatus,
        )
        
        if not hasattr(AuditSeverity, 'CRITICAL'):
            issues.append("AuditSeverity missing CRITICAL value")
    except ImportError as e:
        issues.append(f"Cannot import constants: {e}")
    
    try:
        from gordon_system.src.agent.components.systems.perception.audit.findings.detector import FindingDetector
        detector = FindingDetector()
        if not hasattr(detector, 'detect'):
            issues.append("FindingDetector missing detect method")
    except ImportError as e:
        issues.append(f"Cannot import FindingDetector: {e}")
    
    required_files = [
        "gordon_system/src/agent/components/systems/perception/audit/__init__.py",
        "gordon_system/src/agent/components/systems/perception/audit/constants.py",
        "gordon_system/src/agent/components/systems/perception/audit/models.py",
        "gordon_system/src/agent/components/systems/perception/audit/engine/engine.py",
        "gordon_system/src/agent/components/systems/perception/audit/findings/__init__.py",
        "gordon_system/src/agent/components/systems/perception/audit/findings/detector.py",
    ]
    
    import os
    for filepath in required_files:
        if not os.path.exists(filepath):
            issues.append(f"Missing file: {filepath}")
    
    is_valid = len(issues) == 0
    
    return is_valid, issues


def verify_perception_audit_integrity() -> bool:
    """
    Verify integrity and raise exception if invalid.
    
    Returns:
        True if all checks pass
        
    Raises:
        RuntimeError: If any integrity check fails
    """
    is_valid, issues = perception_audit_integrity_check()
    
    if not is_valid:
        issue_summary = "; ".join(issues)
        raise RuntimeError(f"Perception Audit Integrity Check Failed: {issue_summary}")
    
    return True


__all__ = [
    "perception_audit_integrity_check",
    "verify_perception_audit_integrity",
]