# Security Incident Management - Production Implementation
# ==========================================================

"""
Canonical incident management authority for Phase 3.7.20-I.

This module implements:
- IncidentManager: Detection, classification, and response to security incidents
- Immutable incident records with evidence chains
- Incident lifecycle management
- Integration with recovery systems
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Set
from enum import Enum
import time
import uuid
import hashlib


# Import security primitives
from . import (
    SecurityEventType,
    AuditRecord,
)


class IncidentSeverity(Enum):
    """Severity levels for security incidents."""
    CRITICAL = "critical"       # Immediate system compromise, data breach
    HIGH = "high"              # Significant security event requiring immediate response
    MEDIUM = "medium"          # Moderate security concern needing investigation
    LOW = "low"                # Minor security event for monitoring
    INFO = "info"              # Informational security events


class IncidentStatus(Enum):
    """Status of an incident during its lifecycle."""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass(frozen=True)
class IncidentEvidence:
    """
    Evidence supporting a security incident.
    
    This is immutable and forms part of the audit trail. Evidence can be
    linked to create chains for complex incident analysis.
    """
    evidence_id: str
    type_: str  # e.g., "log_entry", "alert", "observation"
    source: str  # What generated this evidence (provider ID, plugin name, etc.)
    data_summary: Dict[str, Any]
    
    # Optional fields with defaults (must come after required fields)
    previous_evidence_id: Optional[str] = None
    timestamp: float = field(default_factory=time.monotonic)
    
    def hash(self) -> str:
        """Compute hash of this evidence for integrity verification."""
        content = f"{self.timestamp}:{self.source}:{hashlib.md5(str(self.data_summary).encode()).hexdigest()}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True)
class SecurityIncident:
    """
    A security incident with full lifecycle tracking.
    
    Incidents are immutable artifacts. They progress through a lifecycle
    but never modify historical records.
    """
    incident_id: str
    severity: IncidentSeverity
    title: str
    
    # Optional fields with defaults (must come after required fields)
    status: IncidentStatus = IncidentStatus.DETECTED
    timestamp: float = field(default_factory=time.monotonic)
    description: str = ""
    principal_id: Optional[str] = None
    affected_resources: Tuple[str, ...] = field(default_factory=tuple)
    evidence: Tuple[IncidentEvidence, ...] = field(default_factory=tuple)
    
    # Lifecycle tracking (optional with defaults)
    detected_at: float = field(default_factory=time.monotonic)
    analyzed_at: Optional[float] = None
    contained_at: Optional[float] = None
    eradicated_at: Optional[float] = None
    recovered_at: Optional[float] = None
    resolved_at: Optional[float] = None
    
    # Response information (optional with defaults)
    assigned_to: Optional[str] = None
    priority: int = 100  # Lower = higher priority
    
    def progress_status(self, new_status: IncidentStatus) -> "SecurityIncident":
        """Create a new incident with updated status (immutable progression)."""
        update_map = {
            IncidentStatus.ANALYZING: {"analyzed_at": time.monotonic()},
            IncidentStatus.CONTAINING: {"contained_at": time.monotonic()},
            IncidentStatus.ERADICATING: {"eradicated_at": time.monotonic()},
            IncidentStatus.RECOVERING: {"recovered_at": time.monotonic()},
            IncidentStatus.RESOLVED: {"resolved_at": time.monotonic()},
        }
        
        kwargs = self.__dict__.copy()
        kwargs.pop("_fields", None)  # Remove dataclass field marker
        
        if new_status in update_map:
            kwargs.update(update_map[new_status])
        
        kwargs["status"] = new_status
        
        return SecurityIncident(**kwargs)
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this incident in seconds."""
        return time.monotonic() - self.detected_at
    
    @property
    def is_critical(self) -> bool:
        """Check if this is a critical severity incident."""
        return self.severity == IncidentSeverity.CRITICAL


class IncidentManager:
    """
    Canonical security incident authority.
    
    Manages the full lifecycle of security incidents from detection through
    resolution and recovery. Integrates with the Recovery subsystem for
    automated recovery actions.
    
    Invariants:
    - Exactly one instance per runtime
    - All incidents are immutable once created
    - Evidence chains are preserved for forensic analysis
    - Integration with Recovery for containment and recovery
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        
        # Incident storage
        self._incidents: Dict[str, SecurityIncident] = {}  # incident_id -> incident
        self._incident_index: List[Tuple[str, float]] = []  # (id, priority) sorted
        
        # Evidence storage for chain verification
        self._evidence_index: Dict[str, str] = {}  # evidence_id -> incident_id
        
        # Lock for thread safety
        self._lock = __import__("threading").Lock()
        
        # Recovery integration reference (set during runtime initialization)
        self._recovery_system: Optional[Any] = None
    
    @property
    def runtime_id(self) -> str:
        return self._runtime_id
    
    def register_recovery_system(self, recovery_system: Any) -> None:
        """Register the recovery system for incident response."""
        self._recovery_system = recovery_system
    
    async def create_incident(
        self,
        severity: IncidentSeverity,
        title: str,
        description: str,
        principal_id: Optional[str] = None,
        affected_resources: Tuple[str, ...] = tuple(),
        priority: int = 100
    ) -> SecurityIncident:
        """
        Create a new security incident.
        
        This creates the initial DETECTED state. Further status progression
        must be explicit via progress_status().
        """
        incident_id = str(uuid.uuid4())
        
        incident = SecurityIncident(
            incident_id=incident_id,
            severity=severity,
            title=title,
            description=description,
            principal_id=principal_id,
            affected_resources=affected_resources,
            priority=priority
        )
        
        with self._lock:
            self._incidents[incident_id] = incident
            self._incident_index.append((incident_id, priority))
            # Sort by priority (lower first), then by timestamp (earlier first)
            self._incident_index.sort(key=lambda x: (x[1], -self._incidents[x[0]].timestamp))
        
        return incident
    
    async def add_evidence(
        self,
        incident_id: str,
        evidence_type: str,
        source: str,
        data_summary: Dict[str, Any],
        previous_evidence_id: Optional[str] = None
    ) -> IncidentEvidence:
        """
        Add evidence to an existing incident.
        
        Creates a new evidence record and links it to the incident.
        """
        with self._lock:
            if incident_id not in self._incidents:
                raise ValueError(f"Unknown incident: {incident_id}")
            
            evidence_id = str(uuid.uuid4())
            
            evidence = IncidentEvidence(
                evidence_id=evidence_id,
                type_=evidence_type,
                source=source,
                data_summary=data_summary,
                previous_evidence_id=previous_evidence_id
            )
            
            # Update incident with new evidence (immutable update)
            old_incident = self._incidents[incident_id]
            new_evidence_tuple = old_incident.evidence + (evidence,)
            
            kwargs = old_incident.__dict__.copy()
            kwargs.pop("_fields", None)
            kwargs["evidence"] = new_evidence_tuple
            
            self._incidents[incident_id] = SecurityIncident(**kwargs)
            self._evidence_index[evidence_id] = incident_id
        
        return evidence
    
    async def progress_incident(
        self,
        incident_id: str,
        new_status: IncidentStatus
    ) -> SecurityIncident:
        """
        Progress an incident to a new status.
        
        This is the primary method for lifecycle transitions. Each status
        progression creates a new immutable incident record with updated
        timestamps.
        """
        with self._lock:
            if incident_id not in self._incidents:
                raise ValueError(f"Unknown incident: {incident_id}")
            
            old_incident = self._incidents[incident_id]
            new_incident = old_incident.progress_status(new_status)
            
            self._incidents[incident_id] = new_incident
            
            return new_incident
    
    async def resolve_incident(
        self,
        incident_id: str,
        resolution_notes: Optional[str] = None
    ) -> SecurityIncident:
        """
        Mark an incident as resolved.
        
        This transitions the incident to RESOLVED status and triggers
        recovery actions via the registered Recovery system.
        """
        with self._lock:
            if incident_id not in self._incidents:
                raise ValueError(f"Unknown incident: {incident_id}")
            
            incident = self._incidents[incident_id]
            
            # Progress to resolved
            resolved = await self.progress_incident(incident_id, IncidentStatus.RESOLVED)
            
            # If recovery system is registered, trigger recovery actions
            if self._recovery_system and incident.is_critical:
                try:
                    await self._trigger_recovery(resolved)
                except Exception as e:
                    # Log but don't fail the resolution
                    pass
            
            return resolved
    
    async def _trigger_recovery(self, incident: SecurityIncident) -> None:
        """Trigger recovery actions for a critical incident."""
        if self._recovery_system is None:
            return
        
        try:
            # Create recovery action based on incident type
            recovery_action = {
                "incident_id": incident.incident_id,
                "type": "security_containment",
                "priority": "high" if incident.severity == IncidentSeverity.CRITICAL else "medium",
                "affected_resources": list(incident.affected_resources),
                "timestamp": time.monotonic()
            }
            
            # The recovery system handles the actual containment/recovery
            await self._recovery_system.execute_action(recovery_action)
        except Exception:
            pass  # Recovery failures don't affect incident status
    
    async def close_incident(self, incident_id: str) -> SecurityIncident:
        """Close a resolved incident permanently."""
        with self._lock:
            if incident_id not in self._incidents:
                raise ValueError(f"Unknown incident: {incident_id}")
            
            return await self.progress_incident(incident_id, IncidentStatus.CLOSED)
    
    async def get_incident(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get a specific incident by ID."""
        with self._lock:
            return self._incidents.get(incident_id)
    
    async def get_active_incidents(
        self,
        severity_filter: Optional[IncidentSeverity] = None
    ) -> Tuple[SecurityIncident, ...]:
        """Get all active (non-closed) incidents, optionally filtered by severity."""
        with self._lock:
            result = []
            
            for incident_id, _ in self._incident_index:
                incident = self._incidents.get(incident_id)
                
                if incident is None:
                    continue
                
                # Skip closed incidents
                if incident.status == IncidentStatus.CLOSED:
                    continue
                
                # Apply severity filter if specified
                if severity_filter and incident.severity != severity_filter:
                    continue
                
                result.append(incident)
            
            return tuple(result)
    
    async def get_incidents_by_principal(
        self,
        principal_id: str
    ) -> Tuple[SecurityIncident, ...]:
        """Get all incidents associated with a principal."""
        with self._lock:
            result = []
            
            for incident_id, _ in self._incident_index:
                incident = self._incidents.get(incident_id)
                
                if incident and incident.principal_id == principal_id:
                    result.append(incident)
            
            return tuple(result)
    
    async def get_incidents_by_status(
        self,
        status: IncidentStatus
    ) -> Tuple[SecurityIncident, ...]:
        """Get all incidents with a specific status."""
        with self._lock:
            result = []
            
            for incident_id, _ in self._incident_index:
                incident = self._incidents.get(incident_id)
                
                if incident and incident.status == status:
                    result.append(incident)
            
            return tuple(result)
    
    def get_incident_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of incident state (for diagnostics).
        
        This never includes sensitive evidence data - only summary information.
        """
        with self._lock:
            severity_counts: Dict[str, int] = {s.value: 0 for s in IncidentSeverity}
            status_counts: Dict[str, int] = {s.value: 0 for s in IncidentStatus}
            
            total_evidence = 0
            
            for incident in self._incidents.values():
                severity_counts[incident.severity.value] += 1
                status_counts[incident.status.value] += 1
                total_evidence += len(incident.evidence)
            
            return {
                "runtime_id": self._runtime_id,
                "total_incidents": len(self._incidents),
                "active_incidents": sum(
                    1 for i in self._incidents.values()
                    if i.status != IncidentStatus.CLOSED
                ),
                "severity_counts": severity_counts,
                "status_counts": status_counts,
                "total_evidence_records": total_evidence,
                "critical_count": severity_counts.get(IncidentSeverity.CRITICAL.value, 0)
            }
    
    def verify_evidence_chain(self) -> bool:
        """
        Verify the integrity of all evidence chains.
        
        Returns True if all chains are intact (no broken links).
        """
        with self._lock:
            for incident in self._incidents.values():
                # Check each evidence chain within this incident
                current: Optional[IncidentEvidence] = None
                
                for evidence in incident.evidence:
                    if current and evidence.previous_evidence_id != current.evidence_id:
                        return False  # Broken chain
                    
                    current = evidence
            
            return True


@dataclass(frozen=True)
class IncidentReport:
    """
    A formal incident report with all relevant details.
    
    This is typically generated when an incident is closed for postmortem
    analysis and compliance purposes.
    """
    report_id: str
    incident_id: str
    severity: IncidentSeverity
    status_at_close: IncidentStatus
    
    # Timeline (all required fields first)
    detected_at: float
    resolved_at: float
    title: str
    description: str
    
    # Optional fields with defaults (must come after required fields)
    timestamp: float = field(default_factory=time.monotonic)
    analyzed_at: Optional[float] = None
    contained_at: Optional[float] = None
    root_cause: Optional[str] = None
    remediation_steps: Tuple[str, ...] = field(default_factory=tuple)
    lessons_learned: Tuple[str, ...] = field(default_factory=tuple)


class SecurityIncidentDetector:
    """
    Detects security incidents from security events.
    
    This is a passive component that monitors security events and
    creates incidents when suspicious patterns are detected.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._incident_manager: Optional[IncidentManager] = None
    
    def register_incident_manager(self, manager: IncidentManager) -> None:
        """Register the incident manager for creating incidents."""
        self._incident_manager = manager
    
    async def detect_from_event(
        self,
        event_type: SecurityEventType,
        principal_id: str,
        resource: Optional[str] = None
    ) -> Optional[SecurityIncident]:
        """
        Detect if a security event indicates an incident.
        
        Returns an incident if detection threshold is exceeded, None otherwise.
        """
        # Define suspicious patterns
        critical_patterns = {
            SecurityEventType.SANDBOX_VIOLATION,
            SecurityEventType.PRIVILEGE_ESCALATION_ATTEMPT,
            SecurityEventType.POLICY_VIOLATION,
        }
        
        high_patterns = {
            SecurityEventType.AUTH_FAILED,  # Multiple failures indicate attack
        }
        
        if event_type in critical_patterns:
            return await self._create_incident_from_event(
                IncidentSeverity.CRITICAL,
                f"Security {event_type.value.replace(':', ' ').title()}",
                f"Critical security event detected: {event_type.value}",
                principal_id,
                resource
            )
        
        elif event_type in high_patterns:
            # For auth failures, check if multiple (simplified here to single)
            return await self._create_incident_from_event(
                IncidentSeverity.HIGH,
                "Authentication Failure",
                f"Authentication failure detected for principal: {principal_id}",
                principal_id,
                resource
            )
        
        return None
    
    async def _create_incident_from_event(
        self,
        severity: IncidentSeverity,
        title: str,
        description: str,
        principal_id: Optional[str],
        resource: Optional[str]
    ) -> Optional[SecurityIncident]:
        """Create an incident from event details."""
        if self._incident_manager is None:
            return None
        
        return await self._incident_manager.create_incident(
            severity=severity,
            title=title,
            description=description,
            principal_id=principal_id,
            affected_resources=tuple([resource] if resource else [])
        )


__all__ = [
    "IncidentSeverity",
    "IncidentStatus",
    "IncidentEvidence",
    "SecurityIncident",
    "IncidentManager",
    "IncidentReport",
    "SecurityIncidentDetector",
]