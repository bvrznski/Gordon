# Knowledge Audit Sessions - Phase 6.10
# =====================================

"""
Session management for knowledge audit operations.

Sessions encapsulate the state and configuration of an audit operation,
tracking progress from initiation through completion.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.interfaces import (
    KnowledgeAuditSession,
    KnowledgeAuditRequest,
    KnowledgeAuditTarget,
    KnowledgeAuditFinding,
    KnowledgeAuditReport,
)
from gordon_system.src.agent.components.systems.knowledge.knowledge_audit.enums import AuditStatus


@dataclass
class ActiveSession:
    """
    Represents an active audit session with runtime state.
    
    Unlike KnowledgeAuditSession (immutable), this is mutable and tracks
    the actual execution progress of an audit.
    """
    
    # Session identity
    session_id: str
    
    # Runtime tracking
    started_at_utc: float = field(default_factory=time.time)
    last_update_utc: float = field(default_factory=time.time)
    
    # Progress tracking
    targets_total: int = 0
    targets_completed: int = 0
    engines_executed: List[str] = field(default_factory=list)
    
    # Findings accumulated during execution
    findings_by_target: Dict[str, List[KnowledgeAuditFinding]] = field(default_factory=dict)
    
    # Execution status
    is_running: bool = True
    error_message: Optional[str] = None
    
    def record_engine_execution(self, engine_name: str) -> None:
        """Record that an engine has been executed."""
        self.last_update_utc = time.time()
        if engine_name not in self.engines_executed:
            self.engines_executed.append(engine_name)
    
    def record_target_completion(self, target_id: str, findings: List[KnowledgeAuditFinding]) -> None:
        """Record completion of a target audit."""
        self.last_update_utc = time.time()
        self.targets_completed += 1
        if target_id not in self.findings_by_target:
            self.findings_by_target[target_id] = []
        self.findings_by_target[target_id].extend(findings)
    
    def mark_complete(self) -> None:
        """Mark the session as completed."""
        self.is_running = False
        self.last_update_utc = time.time()
    
    def mark_error(self, error_message: str) -> None:
        """Mark the session as having encountered an error."""
        self.is_running = False
        self.error_message = error_message
        self.last_update_utc = time.time()


class KnowledgeAuditSessionFactory:
    """
    Factory for creating and managing audit sessions.
    
    Creates initial sessions from requests and tracks their execution state.
    """
    
    def __init__(self):
        """Initialize the session factory."""
        self._active_sessions: Dict[str, ActiveSession] = {}
    
    @property
    def active_session_count(self) -> int:
        """Get count of currently active sessions."""
        return sum(1 for s in self._active_sessions.values() if s.is_running)
    
    def create_from_request(
        self,
        request: KnowledgeAuditRequest,
        target_ids: List[str],
        target_types: Dict[str, str],
    ) -> Tuple[KnowledgeAuditSession, ActiveSession]:
        """
        Create a new session from an audit request.
        
        Args:
            request: The audit request
            target_ids: List of artifact IDs to audit
            target_types: Mapping from ID to type
            
        Returns:
            Tuple of (immutable session, mutable active session)
        """
        immutable_session = KnowledgeAuditSession.create_pending(
            request=request,
            target_ids=target_ids,
            target_types=target_types,
        )
        
        active_session = ActiveSession(
            session_id=immutable_session.session_id,
            targets_total=len(target_ids),
        )
        
        self._active_sessions[immutable_session.session_id] = active_session
        
        return immutable_session, active_session
    
    def get_active(self, session_id: str) -> Optional[ActiveSession]:
        """Get an active session by ID."""
        return self._active_sessions.get(session_id)
    
    def remove_session(self, session_id: str) -> None:
        """Remove a session from tracking."""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
    
    def get_all_active(self) -> List[ActiveSession]:
        """Get all active sessions."""
        return [s for s in self._active_sessions.values() if s.is_running]
    
    def to_immutable_session(
        self,
        active: ActiveSession,
        report: Optional[KnowledgeAuditReport] = None,
    ) -> KnowledgeAuditSession:
        """
        Convert an active session to immutable form.
        
        Args:
            active: The active session
            report: Final report if completed
            
        Returns:
            Immutable session with final state
        """
        # Build findings dict from active session
        findings_dict: Dict[str, Tuple[KnowledgeAuditFinding, ...]] = {
            target_id: tuple(findings)
            for target_id, findings in active.findings_by_target.items()
        }
        
        return KnowledgeAuditSession(
            session_id=active.session_id,
            request_id="",  # Would need to be tracked separately
            audit_request=KnowledgeAuditRequest.create_all(),
            target_ids=tuple(active.findings_by_target.keys()),
            target_types={},
            status=AuditStatus.COMPLETED if report else AuditStatus.RUNNING,
            started_at_utc=active.started_at_utc,
            completed_at_utc=time.time() if not active.is_running else 0.0,
            findings=findings_dict,
            report=report,
        )


__all__ = [
    "ActiveSession",
    "KnowledgeAuditSessionFactory",
]