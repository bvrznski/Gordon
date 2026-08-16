# Gordon Workspace Network Audit Models
# =====================================

"""
Core data model types for the Workspace Audit subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List
import time


@dataclass(frozen=True)
class AuditFinding:
    """
    A single finding from an audit session.
    
    Each finding represents a specific issue or anomaly detected during
    the validation process. Findings include severity, category, affected
    objects, and supporting evidence.
    """
    
    finding_id: str
    """Unique identifier for this finding."""
    
    timestamp_utc: float
    """Unix timestamp when finding was recorded."""
    
    category: str
    """Category of the finding (from FindingKind)."""
    
    severity: str
    """Severity level (critical/high/medium/low/info)."""
    
    description: str
    """Human-readable description of the issue."""
    
    affected_objects: Tuple[str, ...]
    """IDs of objects affected by this finding."""
    
    validator_name: Optional[str] = None
    """Name of the validator that produced this finding."""
    
