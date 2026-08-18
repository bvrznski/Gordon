# Execution Reasoning Governance - Phase 7.21
# ===========================================

"""
Canonical Execution Governance for Phase 7.21.

Execution Governance evaluates execution correctness, authorization integrity,
resource synchronization, rollback safety, policy compliance, and diagnostics.
Governance remains observational and never modifies execution artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class GovernanceFindingKind(Enum):
    """Kinds of governance findings."""
    
    AUTHORIZATION_INTEGRITY = "authorization_integrity"       # Authorization state is invalid
    SYNCHRONIZATION_VIOLATION = "synchronization_violation"     # Synchronization violated
    NONDETERMINISTIC_EXECUTION = "nondeterministic_execution"   # Non-deterministic behavior detected
    POLICY_VIOLATION = "policy_violation"                       # Policy constraint not satisfied


@dataclass(frozen=True)
class ExecutionGovernance:
    """
    Execution Governance provides observational evaluation.
    
    Governance evaluates:
        - Execution correctness
        - Authorization integrity
        - Resource synchronization
        - Rollback safety
        - Policy compliance
        - Diagnostics
    
    Governance remains observational and does not modify execution artifacts.
    """
    
    # Identity
    governance_identity: str                    # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...]         # IDs of sessions governed
    
    # Findings
    findings: Tuple[GovernanceFinding, ...] = ()
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: Tuple[str, ...],
        findings: Tuple[GovernanceFinding, ...] = (),
    ) -> ExecutionGovernance:
        """Create a new execution governance instance."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=evaluated_sessions,
            findings=findings,
        )
    
    @property
    def total_findings(self) -> int:
        """Total number of findings."""
        return len(self.findings)
    
    @property
    def has_violations(self) -> bool:
        """Check if any violations found."""
        return self.total_findings > 0


@dataclass(frozen=True)
class GovernanceFinding:
    """
    A single governance finding.
    
    Each finding includes kind, description, and diagnostic information.
    """
    
    # Identity
    finding_identity: str                       # Unique finding identifier
    
    # Finding details
    finding_kind: GovernanceFindingKind         # What type of issue?
    description: str                            # Human-readable description
    
    @classmethod
    def create(
        cls,
        finding_kind: GovernanceFindingKind,
        description: str,
    ) -> GovernanceFinding:
        """Create a new governance finding."""
        return cls(
            finding_identity=f"gov_finding:{uuid.uuid4().hex[:16]}",
            finding_kind=finding_kind,
            description=description,
        )


@dataclass(frozen=True)
class ExecutionSessionGovernance:
    """
    Governance evaluation for an execution session.
    
    Tracks governance state throughout a session's lifecycle.
    """
    
    # Identity
    governance_session_identity: str
    
    # Session being governed
    governed_session_id: str                    # ID of the session being governed
    
    # Evaluation history
    evaluations: Tuple[ExecutionGovernance, ...]
    
    @classmethod
    def create(
        cls,
        governed_session_id: str,
        evaluations: Tuple[ExecutionGovernance, ...] = (),
    ) -> ExecutionSessionGovernance:
        """Create a new session governance instance."""
        return cls(
            governance_session_identity=f"gov_session:{uuid.uuid4().hex[:16]}",
            governed_session_id=governed_session_id,
            evaluations=evaluations,
        )
    
    def add_evaluation(self, evaluation: ExecutionGovernance) -> ExecutionSessionGovernance:
        """Return a new instance with the evaluation added."""
        return dataclass_replace(
            self,
            evaluations=self.evaluations + (evaluation,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionGovernance",
    "GovernanceFindingKind",
    "GovernanceFinding",
    "ExecutionSessionGovernance",
]