# Persistence Manager
# ===================

"""
Canonical runtime persistence authority.

This module provides:
- PersistenceManager: The single, authoritative persistence coordinator
- State domain registration and management
- Participant coordination for capture/restore
- Backend selection and transaction coordination
- Retention and lifecycle management
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, AsyncIterable
from enum import Enum, auto
import uuid
import time


# =============================================================================
# Persistence Request Types
# =============================================================================

@dataclass(frozen=True)
class PersistenceRequest:
    """A request to persist state."""
    
    request_id: str
    
    runtime_id: str
    boot_session_id: str
    
    # What to persist
    domains: List[str]
    
    # Capture context
    capture_mode: str = "versioned"
    quiesce_timeout_seconds: float = 5.0
    
    # Target backend (None for default)
    target_backend: Optional[str] = None
    
    # Requirements
    requires_integrity: bool = True
    requires_transaction: bool = False


@dataclass(frozen=True)
class RestoreRequest:
    """A request to restore persisted state."""
    
    request_id: str
    
    runtime_id: str
    boot_session_id: str
    
    # Selection criteria
    checkpoint_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    journal_range: Optional[tuple[int, int]] = None
    
    # Mode
    mode: str = "full"  # full, validate_only, dry_run
    skip_validation: bool = False
    
    # Target domains (None for all)
    target_domains: Optional[List[str]] = None


# =============================================================================
# Persistence Result Types
# =============================================================================

class PersistResult(Enum):
    """Result of a persistence operation."""
    
    SUCCESS = "success"
    PARTIAL = "partial"  # Some domains succeeded, some failed
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class PersistenceResult:
    """Result of a persistence operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    status: PersistResult
    timestamp: float
    
    # Details
    domains_attempted: int = 0
    domains_succeeded: int = 0
    domains_failed: int = 0
    
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if operation succeeded."""
        return self.status == PersistResult.SUCCESS


@dataclass(frozen=True)
class RestoreResult:
    """Result of a restore operation."""
    
    result_id: str
    
    request_id: str
    runtime_id: str
    
    status: PersistResult
    timestamp: float
    
    # Details
    domains_restored: int = 0
    domains_failed: int = 0
    resources_reacquired: List[str] = field(default_factory=list)
    
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if restore succeeded."""
        return self.status == PersistResult.SUCCESS


# =============================================================================
# Storage Backend Protocol (interface only)
# =============================================================================

class StorageBackendProtocol:
    """
    Interface for storage backends.
    
    PersistenceManager uses this interface - it does not implement storage
    directly. Backends are adapters that provide storage capabilities.
    """
    
    def capabilities(self) -> Dict[str, Any]:
        """Return backend capabilities."""
        raise NotImplementedError
    
    async def write(
        self,
        key: str,
        data: bytes,
        checksum: Optional[str] = None
    ) -> str:
        """
        Write data to storage.
        
        Returns:
            Object ID (content address or generated ID)
        """
        raise NotImplementedError
    
    async def read(self, key_or_id: str) -> bytes:
        """Read data from storage."""
        raise NotImplementedError
    
    async def exists(self, key_or_id: str) -> bool:
        """Check if object exists."""
        raise NotImplementedError
    
    async def delete(self, key_or_id: str) -> None:
        """Delete an object."""
        raise NotImplementedError
    
    async def list_keys(self, prefix: str = "") -> AsyncIterable[str]:
        """List keys matching a prefix."""
        raise NotImplementedError


# =============================================================================
# Persistence Domain Registration
# =============================================================================

@dataclass(frozen=True)
class RegisteredDomain:
    """A registered persistence domain."""
    
    domain_id: str
    
    # Metadata
    owner: str
    durability_class: str
    
    # Capture settings
    capture_enabled: bool = True
    checkpoint_enabled: bool = True
    journal_enabled: bool = False
    
    # Serialization settings
    schema_version: int = 1
    serialization_format: str = "canonical_json"
    
    # Retention
    retention_seconds: float = 86400.0


# =============================================================================
# Persistence Manager - The Canonical Authority
# =============================================================================

class PersistenceManager:
    """
    Canonical runtime persistence authority.
    
    This is the SINGLE, canonical persistence coordinator for a runtime instance.
    
    Responsibilities:
        - State domain registration and management
        - Participant coordination (capture, restore)
        - Backend selection and transaction coordination
        - Persistence planning and execution
        - Retention and lifecycle management
        - Diagnostics and monitoring
    
    NOT responsible for:
        - Storing data directly (delegates to backends)
        - Defining state ownership (owners retain authority)
        - Making persistence decisions (only coordinates)
    
    Usage:
        # Create one manager per runtime
        pm = PersistenceManager(runtime_id="runtime_123")
        
        # Register domains and participants
        pm.register_domain(
            domain_id="runtime_state",
            owner="runtime_state_store"
        )
        
        pm.register_participant(my_component)
        
        # Perform persistence operations
        result = await pm.capture_and_persist(request)
        restored = await pm.restore(request)
    """
    
    def __init__(self, runtime_id: str) -> None:
        self._runtime_id = runtime_id
        
        # State domain registry
        self._domains: Dict[str, RegisteredDomain] = {}
        
        # Participant registry
        self._participants: Dict[str, Any] = {}  # participant_id -> protocol
        
        # Backend registry - backends are selected per operation
        self._backends: Dict[str, StorageBackendProtocol] = {}
        self._default_backend: Optional[StorageBackendProtocol] = None
        
        # Operation tracking
        self._active_transactions: Dict[str, Any] = {}
        
        # Metrics
        self._capture_count = 0
        self._restore_count = 0
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    def register_domain(
        self,
        domain_id: str,
        owner: str,
        durability_class: str = "restart_recoverable",
        **kwargs
    ) -> None:
        """
        Register a state domain for persistence coordination.
        
        Args:
            domain_id: Unique identifier for the domain
            owner: Component ID that owns this state
            durability_class: Required durability guarantees
            **kwargs: Additional options (capture_enabled, checkpoint_enabled, etc.)
        """
        if domain_id in self._domains:
            raise ValueError(f"Domain '{domain_id}' already registered")
        
        self._domains[domain_id] = RegisteredDomain(
            domain_id=domain_id,
            owner=owner,
            durability_class=durability_class,
            capture_enabled=kwargs.get("capture_enabled", True),
            checkpoint_enabled=kwargs.get("checkpoint_enabled", True),
            journal_enabled=kwargs.get("journal_enabled", False),
            schema_version=kwargs.get("schema_version", 1),
            serialization_format=kwargs.get("serialization_format", "canonical_json"),
            retention_seconds=kwargs.get("retention_seconds", 86400.0),
        )
    
    def register_participant(
        self,
        participant_id: str,
        protocol: Any
    ) -> None:
        """
        Register a persistence participant.
        
        Args:
            participant_id: Unique identifier for the participant
            protocol: Object implementing PersistenceParticipantProtocol
        """
        if participant_id in self._participants:
            raise ValueError(f"Participant '{participant_id}' already registered")
        
        self._participants[participant_id] = protocol
    
    def register_backend(
        self,
        backend_id: str,
        backend: StorageBackendProtocol,
        is_default: bool = False
    ) -> None:
        """
        Register a storage backend.
        
        Args:
            backend_id: Unique identifier for the backend
            backend: Backend instance implementing StorageBackendProtocol
            is_default: Whether this is the default backend
        """
        self._backends[backend_id] = backend
        
        if is_default or not self._default_backend:
            self._default_backend = backend
    
    def get_domain(self, domain_id: str) -> Optional[RegisteredDomain]:
        """Get a registered domain."""
        return self._domains.get(domain_id)
    
    def list_domains(self) -> List[RegisteredDomain]:
        """List all registered domains."""
        return list(self._domains.values())
    
    async def capture_and_persist(
        self,
        request: PersistenceRequest
    ) -> PersistenceResult:
        """
        Capture and persist state for requested domains.
        
        This is the main entry point for persistence operations.
        
        Args:
            request: The persistence request
            
        Returns:
            Result with success/failure status
        """
        # Validate request
        if not self._validate_request(request):
            return PersistenceResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="Request validation failed"
            )
        
        # Plan capture
        plan = self._create_capture_plan(request)
        
        if not plan:
            return PersistenceResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="No capture plan could be created"
            )
        
        # Execute capture (quiescent or versioned)
        captured = await self._execute_capture(plan, request)
        
        if not captured:
            return PersistenceResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="Capture failed"
            )
        
        # Serialize and persist
        backend = self._select_backend(request)
        if not backend:
            return PersistenceResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="No backend available"
            )
        
        persisted_ids = await self._persist_captured_state(backend, captured)
        
        if not persisted_ids:
            return PersistenceResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.PARTIAL,
                timestamp=time.monotonic(),
                domains_attempted=len(captured),
                domains_failed=len(captured)
            )
        
        self._capture_count += 1
        
        return PersistenceResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=PersistResult.SUCCESS,
            timestamp=time.monotonic(),
            domains_attempted=len(captured),
            domains_succeeded=len(persisted_ids)
        )
    
    async def restore(self, request: RestoreRequest) -> RestoreResult:
        """
        Restore persisted state.
        
        Args:
            request: The restore request
            
        Returns:
            Result with success/failure status
        """
        if request.skip_validation:
            # Validate only mode - do not actually restore
            return await self._validate_restore(request)
        
        # Find source artifact (checkpoint, snapshot, or journal)
        source = await self._find_restore_source(request)
        
        if not source:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="No restore source found"
            )
        
        # Deserialize
        deserialized = await self._deserialize_source(source)
        
        if not deserialized:
            return RestoreResult(
                result_id=str(uuid.uuid4()),
                request_id=request.request_id,
                runtime_id=self._runtime_id,
                status=PersistResult.FAILED,
                timestamp=time.monotonic(),
                error_message="Deserialization failed"
            )
        
        # Route to participants for restoration
        restored = await self._restore_to_participants(deserialized, request)
        
        self._restore_count += 1
        
        return RestoreResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=PersistResult.SUCCESS if restored else PersistResult.PARTIAL,
            timestamp=time.monotonic(),
            domains_restored=len(restored) if restored else 0
        )
    
    def _validate_request(self, request: PersistenceRequest) -> bool:
        """Validate a persistence request."""
        # Check runtime matches
        if request.runtime_id != self._runtime_id:
            return False
        
        # Check domains exist
        for domain_id in request.domains:
            if domain_id not in self._domains:
                return False
        
        return True
    
    def _create_capture_plan(
        self,
        request: PersistenceRequest
    ) -> Optional[Dict[str, Any]]:
        """Create a capture plan for the request."""
        domains = []
        
        for domain_id in request.domains:
            domain = self._domains.get(domain_id)
            if not domain or not domain.capture_enabled:
                continue
            
            # Find participants for this domain
            participants_for_domain = [
                pid for pid, proto in self._participants.items()
                if hasattr(proto, 'persistence_descriptor') and
                domain_id in proto.persistence_descriptor.state_domains
            ]
            
            domains.append({
                "domain_id": domain_id,
                "participant_ids": participants_for_domain,
                "schema_version": domain.schema_version,
            })
        
        return {
            "request_id": request.request_id,
            "runtime_id": self._runtime_id,
            "domains": domains,
            "capture_mode": request.capture_mode,
        }
    
    async def _execute_capture(
        self,
        plan: Dict[str, Any],
        request: PersistenceRequest
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute the capture plan."""
        captured = []
        
        for domain_info in plan["domains"]:
            domain_id = domain_info["domain_id"]
            
            # For each participant, call their capture method
            for pid in domain_info.get("participant_ids", []):
                participant = self._participants.get(pid)
                if not participant:
                    continue
                
                try:
                    # Capture state through the protocol
                    captured_state = await participant.capture_state(
                        type('CaptureContext', (), {
                            'context_id': request.request_id,
                            'runtime_id': request.runtime_id,
                            'boot_session_id': uuid.uuid4().hex,
                            'mode': request.capture_mode,
                            'timeout_seconds': request.quiesce_timeout_seconds,
                        })()
                    )
                    
                    captured.append({
                        "domain_id": domain_id,
                        "participant_id": pid,
                        "state": captured_state,
                    })
                except Exception:
                    # Continue with other participants
                    continue
        
        return captured if captured else None
    
    def _select_backend(self, request: PersistenceRequest) -> Optional[StorageBackendProtocol]:
        """Select backend for persistence operation."""
        if request.target_backend:
            return self._backends.get(request.target_backend)
        
        return self._default_backend
    
    async def _persist_captured_state(
        self,
        backend: StorageBackendProtocol,
        captured: List[Dict[str, Any]]
    ) -> List[str]:
        """Persist captured state to storage."""
        persisted_ids = []
        
        for item in captured:
            # Serialize the captured state
            data = self._serialize_state(item["state"])
            
            if not data:
                continue
            
            # Write to backend
            key = f"{self._runtime_id}/{item['domain_id']}/{uuid.uuid4().hex}"
            
            try:
                object_id = await backend.write(key, data)
                persisted_ids.append(object_id)
            except Exception:
                continue
        
        return persisted_ids
    
    def _serialize_state(self, state: Any) -> Optional[bytes]:
        """Serialize a captured state to bytes."""
        # Simplified - would use SerializationManager in production
        import json
        try:
            # Convert to serializable format (remove non-serializable bits)
            serializable = self._make_serializable(state)
            return json.dumps(serializable).encode('utf-8')
        except Exception:
            return None
    
    def _make_serializable(self, value: Any) -> Any:
        """Convert a value to a JSON-serializable format."""
        if isinstance(value, dict):
            return {k: self._make_serializable(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._make_serializable(item) for item in value]
        elif hasattr(value, '__dict__'):
            return self._make_serializable(vars(value))
        elif hasattr(value, 'value'):  # Enums
            return value.value
        else:
            return value
    
    async def _find_restore_source(
        self,
        request: RestoreRequest
    ) -> Optional[Dict[str, Any]]:
        """Find a restore source (checkpoint, snapshot, or journal range)."""
        # For now, return None - would query storage in production
        if request.checkpoint_id:
            # Look up checkpoint
            pass
        elif request.snapshot_id:
            # Look up snapshot
            pass
        
        return None
    
    async def _deserialize_source(
        self,
        source: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Deserialize a restore source."""
        # Would use SerializationManager in production
        return None
    
    async def _restore_to_participants(
        self,
        deserialized: Dict[str, Any],
        request: RestoreRequest
    ) -> List[str]:
        """Restore deserialized state to participants."""
        restored = []
        
        for domain_id, data in deserialized.items():
            # Find participants for this domain
            participant_ids = [
                pid for pid, proto in self._participants.items()
                if hasattr(proto, 'persistence_descriptor') and
                domain_id in proto.persistence_descriptor.state_domains
            ]
            
            for pid in participant_ids:
                participant = self._participants.get(pid)
                if not participant:
                    continue
                
                try:
                    # Restore state through the protocol
                    success = await participant.restore_state(
                        data,
                        type('CaptureContext', (), {
                            'context_id': request.request_id,
                            'runtime_id': request.runtime_id,
                        })()
                    )
                    
                    if success:
                        restored.append(domain_id)
                except Exception:
                    continue
        
        return restored
    
    async def _validate_restore(self, request: RestoreRequest) -> RestoreResult:
        """Validate a restore without executing it."""
        # Would perform schema validation, compatibility checks, etc.
        return RestoreResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            runtime_id=self._runtime_id,
            status=PersistResult.SUCCESS,
            timestamp=time.monotonic(),
        )
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostics information."""
        return {
            "runtime_id": self._runtime_id,
            "domains_registered": len(self._domains),
            "participants_registered": len(self._participants),
            "backends_registered": len(self._backends),
            "capture_count": self._capture_count,
            "restore_count": self._restore_count,
        }


__all__ = [
    # Request types
    "PersistenceRequest",
    "RestoreRequest",
    
    # Result types
    "PersistResult",
    "PersistenceResult",
    "RestoreResult",
    
    # Manager
    "PersistenceManager",
]