# Integration Session - Phase 5.1.7 Session Management System
# ============================================================

"""
Memory Integration Session: Manages sessions for integration interactions.

Session responsibilities:
    - Track request/response history
    - Maintain consumer state
    - Support session recovery
    - Ensure determinism

Session Laws:
    SESSION-LAW-001: Every interaction belongs to exactly one session
    SESSION-LAW-002: Sessions preserve identity and history
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SESSION STATES
# =============================================================================


class SessionState(Enum):
    """
    States of a session.
    
    | State       | Description                                    |
    |-------------|------------------------------------------------|
    | ACTIVE      | Currently active                               |
    | SUSPENDED   | Temporarily suspended                          |
    | TERMINATED  | Terminated normally                            |
    | ERROR       | Terminated due to error                        |
    """
    
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"


# =============================================================================
# SESSION METADATA
# =============================================================================


@dataclass(frozen=True)
class SessionMetadata:
    """
    Metadata about a session.
    
    Fields:
        session_id:      Unique session identifier
        
        # Identity
        consumer_id:     Which consumer is this for?
        integration_type: Which integration?
        
        # Timing
        started_at_utc:  When was the session created?
        last_activity:   When was the last activity?
        
        # Counters
        request_count:   Number of requests in this session
        response_count:  Number of responses in this session
    """
    
    session_id: str                         # Unique identifier
    
    consumer_id: str                        # Consumer identity
    integration_type: str                   # e.g., "perception", "workspace"
    
    started_at_utc: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    request_count: int = 0
    response_count: int = 0


# =============================================================================
# SESSION HISTORY
# =============================================================================


@dataclass(frozen=True)
class SessionHistory:
    """
    History of interactions in a session.
    
    Fields:
        entries:         List of interaction records
        
        first_entry:     When was the first interaction?
        last_entry:      When was the last interaction?
        
        # Summary
        total_requests:  Total requests
        total_responses: Total responses
    """
    
    entries: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    first_entry: float = field(default_factory=time.time)
    last_entry: float = field(default_factory=time.time)
    
    total_requests: int = 0
    total_responses: int = 0


# =============================================================================
# SESSION RECORD
# =============================================================================


@dataclass(frozen=True)
class SessionRecord:
    """
    Complete record of a session.
    
    Fields:
        metadata:        Session metadata
        
        state:           Current session state
        terminated_at:   When was it terminated? (if terminated)
        
        # History
        history:         Interaction history
        
        # Diagnostics
        error_message:   Error message (if any)
        diagnostics:     Additional diagnostic information
    """
    
    metadata: SessionMetadata
    
    state: SessionState = SessionState.ACTIVE
    terminated_at: Optional[float] = None
    
    history: SessionHistory = field(default_factory=SessionHistory)
    
    error_message: Optional[str] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# SESSION MANAGER
# =============================================================================


class SessionManager:
    """
    Manager for integration sessions.
    
    Creates, manages, and tracks all integration sessions.
    
    Usage:
        manager = SessionManager()
        
        # Create a session
        session_id = manager.create_session("perception", "consumer-1")
        
        # Record an interaction
        manager.record_request(session_id, request_data)
        
        # Get session status
        record = manager.get_record(session_id)
    """
    
    def __init__(self):
        self._sessions: Dict[str, SessionRecord] = {}
        self._session_index: Dict[Tuple[str, str], List[str]] = {}  # consumer, integration -> session IDs
    
    def create_session(self, integration_type: str,
                       consumer_id: str) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        
        metadata = SessionMetadata(
            session_id=session_id,
            consumer_id=consumer_id,
            integration_type=integration_type
        )
        
        record = SessionRecord(metadata=metadata)
        self._sessions[session_id] = record
        
        # Index by consumer and integration
        key = (consumer_id, integration_type)
        if key not in self._session_index:
            self._session_index[key] = []
        self._session_index[key].append(session_id)
        
        return session_id
    
    def terminate_session(self, session_id: str,
                          state: SessionState = SessionState.TERMINATED,
                          error_message: Optional[str] = None) -> None:
        """Terminate a session."""
        if session_id in self._sessions:
            record = self._sessions[session_id]
            new_record = dataclass_replace(record,
                                           state=state,
                                           terminated_at=time.time(),
                                           error_message=error_message)
            self._sessions[session_id] = new_record
    
    def suspend_session(self, session_id: str) -> None:
        """Suspend a session (can be resumed)."""
        if session_id in self._sessions:
            record = self._sessions[session_id]
            self._sessions[session_id] = dataclass_replace(record,
                                                           state=SessionState.SUSPENDED)
    
    def resume_session(self, session_id: str) -> None:
        """Resume a suspended session."""
        if session_id in self._sessions:
            record = self._sessions[session_id]
            if record.state == SessionState.SUSPENDED:
                self._sessions[session_id] = dataclass_replace(record,
                                                               state=SessionState.ACTIVE)
    
    def record_request(self, session_id: str,
                       request_data: Dict[str, Any]) -> None:
        """Record a request in session history."""
        if session_id not in self._sessions:
            return
        
        record = self._sessions[session_id]
        now = time.time()
        
        # Update history
        new_entries = list(record.history.entries) + [request_data]
        new_record = dataclass_replace(record,
                                       last_activity=now,
                                       history=SessionHistory(
                                           entries=tuple(new_entries),
                                           first_entry=min(now, record.history.first_entry),
                                           last_entry=now,
                                           total_requests=record.history.total_requests + 1
                                       ))
        
        self._sessions[session_id] = new_record
    
    def record_response(self, session_id: str,
                        response_data: Dict[str, Any]) -> None:
        """Record a response in session history."""
        if session_id not in self._sessions:
            return
        
        record = self._sessions[session_id]
        now = time.time()
        
        # Update history
        new_entries = list(record.history.entries) + [response_data]
        new_record = dataclass_replace(record,
                                       last_activity=now,
                                       history=SessionHistory(
                                           entries=tuple(new_entries),
                                           first_entry=min(now, record.history.first_entry),
                                           last_entry=now,
                                           total_responses=record.history.total_responses + 1
                                       ))
        
        self._sessions[session_id] = new_record
    
    def get_record(self, session_id: str) -> Optional[SessionRecord]:
        """Get the complete record for a session."""
        return self._sessions.get(session_id)
    
    def get_records_for_consumer(self, consumer_id: str,
                                 integration_type: Optional[str] = None
                                 ) -> Tuple[SessionRecord, ...]:
        """Get all sessions for a consumer (optionally filtered by integration)."""
        if integration_type:
            key = (consumer_id, integration_type)
            session_ids = self._session_index.get(key, [])
        else:
            # Get all session IDs for this consumer
            session_ids = []
            for (cid, _), sids in self._session_index.items():
                if cid == consumer_id:
                    session_ids.extend(sids)
        
        return tuple(self._sessions[sid] for sid in session_ids if sid in self._sessions)
    
    def list_sessions(self) -> Dict[str, SessionRecord]:
        """List all active sessions."""
        return {sid: r for sid, r in self._sessions.items() 
                if r.state == SessionState.ACTIVE}


def dataclass_replace(instance: Any, **kwargs) -> Any:
    """Replacement for dataclasses.replace (Python 3.7 compatible)."""
    fields = instance.__dataclass_fields__
    return type(instance)(
        **{f.name: kwargs.get(f.name, getattr(instance, f.name)) 
           for f in fields.values()}
    )