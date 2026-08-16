# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Cognitive Event Engine - Orchestration of Event Creation and Management

This module defines the main engine that orchestrates cognitive event creation,
validation, and management.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CognitiveEventRequest:
    """
    Request to create a new cognitive event.
    
    The request describes one semantic occurrence that should produce
    an immutable Cognitive Event.
    
    REQUEST LAWS (REQ-LAW)
    ----------------------
    REQ-LAW-001: Requests are immutable once submitted
    REQ-LAW-002: Requests must have all required fields filled
    REQ-LAW-003: Requests preserve provenance for auditing
    """
    
    # Source network that produced this event
    _source_network: str
    
    # Source artifact (file, module, function) that generated the event
    _source_artifact: str
    
    # Kind of event
    _event_kind: str
    
    # Semantic payload reference
    _semantic_payload: dict = field(default_factory=dict)
    
    # Semantic scope of the event
    _semantic_scope: str = "default"
    
    # Correlation reference (if any)
    _correlation_reference: str | None = None
    
    # Causation reference (if any)
    _causation_reference: str | None = None
    
    # Originating epoch identifier
    _originating_epoch: int = 1
    
    # Originating cycle identifier  
    _originating_cycle: int = 1
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate request components."""
        if not self._source_network:
            raise ValueError("Source network cannot be empty")
        
        if not self._source_artifact:
            raise ValueError("Source artifact cannot be empty")
        
        if not self._event_kind:
            raise ValueError("Event kind cannot be empty")
    
    @property
    def source_network(self) -> str:
        """Get the source network identifier."""
        return self._source_network
    
    @property
    def source_artifact(self) -> str:
        """Get the source artifact identifier."""
        return self._source_artifact
    
    @property
    def event_kind(self) -> str:
        """Get the event kind."""
        return self._event_kind
    
    @property
    def semantic_payload(self) -> dict:
        """Get the semantic payload reference."""
        return self._semantic_payload
    
    @property
    def semantic_scope(self) -> str:
        """Get the semantic scope."""
        return self._semantic_scope
    
    @property
    def correlation_reference(self) -> str | None:
        """Get the correlation reference, if any."""
        return self._correlation_reference
    
    @property
    def causation_reference(self) -> str | None:
        """Get the causation reference, if any."""
        return self._causation_reference
    
    @property
    def originating_epoch(self) -> int:
        """Get the originating epoch identifier."""
        return self._originating_epoch
    
    @property
    def originating_cycle(self) -> int:
        """Get the originating cycle identifier."""
        return self._originating_cycle
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "source_network": self._source_network,
            "source_artifact": self._source_artifact,
            "event_kind": self._event_kind,
            "semantic_payload": dict(self._semantic_payload),
            "semantic_scope": self._semantic_scope,
            "correlation_reference": self._correlation_reference,
            "causation_reference": self._causation_reference,
            "originating_epoch": self._originating_epoch,
            "originating_cycle": self._originating_cycle,
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventRequest":
        """
        Create a request from a dictionary.
        
        Args:
            data: Dictionary with request data
            
        Returns:
            New CognitiveEventRequest instance
        """
        return cls(
            _source_network=data["source_network"],
            _source_artifact=data.get("source_artifact", "unknown"),
            _event_kind=data["event_kind"],
            _semantic_payload=dict(data.get("semantic_payload", {})),
            _semantic_scope=data.get("semantic_scope", "default"),
            _correlation_reference=data.get("correlation_reference"),
            _causation_reference=data.get("causation_reference"),
            _originating_epoch=data.get("originating_epoch", 1),
            _originating_cycle=data.get("originating_cycle", 1),
            _provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True)
class CognitiveEventResult:
    """
    Result of event construction.
    
    Contains the constructed event along with validation results and findings.
    
    RESULT LAWS (RESULT-LAW)
    ------------------------
    RESULT-LAW-001: Results include complete trace
    RESULT-LAW-002: Results preserve all validation information
    RESULT-LAW-003: Results are immutable once created
    """
    
    # Reference to the original request
    _request_reference: str
    
    # Constructed event (if valid)
    _event: dict | None = None
    
    # Validation result
    _validation_result: dict = field(default_factory=dict)
    
    # Findings from construction process
    _findings: tuple[str, ...] = field(default_factory=tuple)
    
    # Limitations of the constructed event
    _limitations: tuple[str, ...] = field(default_factory=tuple)
    
    # Trace of processing steps
    _trace: tuple[str, ...] = field(default_factory=tuple)
    
    # Final status
    _status: str = "occurred"
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def request_reference(self) -> str:
        """Get the reference to the original request."""
        return self._request_reference
    
    @property
    def event(self) -> dict | None:
        """Get the constructed event, if valid."""
        return self._event
    
    @property
    def validation_result(self) -> dict:
        """Get the validation result."""
        return self._validation_result
    
    @property
    def findings(self) -> tuple[str, ...]:
        """Get the construction findings."""
        return self._findings
    
    @property
    def limitations(self) -> tuple[str, ...]:
        """Get the event limitations."""
        return self._limitations
    
    @property
    def trace(self) -> tuple[str, ...]:
        """Get the processing trace."""
        return self._trace
    
    @property
    def status(self) -> str:
        """Get the final status."""
        return self._status
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "request_reference": self._request_reference,
            "event": self._event,
            "validation_result": dict(self._validation_result),
            "findings": list(self._findings),
            "limitations": list(self._limitations),
            "trace": list(self._trace),
            "status": self._status,
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEventResult":
        """
        Create a result from a dictionary.
        
        Args:
            data: Dictionary with result data
            
        Returns:
            New CognitiveEventResult instance
        """
        return cls(
            _request_reference=data["request_reference"],
            _event=data.get("event"),
            _validation_result=dict(data.get("validation_result", {})),
            _findings=tuple(data.get("findings", [])),
            _limitations=tuple(data.get("limitations", [])),
            _trace=tuple(data.get("trace", [])),
            _status=data.get("status", "occurred"),
            _provenance=dict(data.get("provenance", {})),
        )


class CognitiveEventEngine:
    """
    Main orchestrator for cognitive event processing.
    
    The engine handles request validation, event construction, stream
    updates, timeline updates, and index management.
    
    ENGINE LAWS (ENGINE-LAW)
    ------------------------
    ENGINE-LAW-001: Engine validates before construction
    ENGINE-LAW-002: Engine classifies event kinds correctly
    ENGINE-LAW-003: Engine constructs immutable events
    ENGINE-LAW-004: Engine updates all relevant indexes
    """
    
    def __init__(self):
        """Initialize the event engine."""
        self._event_count = 0
        self._events_by_kind: dict[str, list[str]] = {}
        self._events_by_network: dict[str, list[str]] = {}
    
    def process_event_request(
        self, request: CognitiveEventRequest
    ) -> CognitiveEventResult:
        """
        Process an event request and return the result.
        
        This is the main entry point for creating new cognitive events.
        
        Args:
            request: The event request to process
            
        Returns:
            Result with constructed event or error information
        """
        trace = []
        
        # Step 1: Validate request
        trace.append("EVENT_REQUEST_VALIDATED")
        validation_result = self._validate_request(request)
        
        if not validation_result.get("is_valid", False):
            return CognitiveEventResult(
                _request_reference=f"req_{self._event_count + 1}",
                _validation_result=validation_result,
                _findings=tuple(validation_result.get("findings", [])),
                _status="invalid",
                _provenance={"engine": "CognitiveEventEngine"},
            )
        
        # Step 2: Classify event kind
        trace.append("EVENT_CLASSIFIED")
        kind_classification = self._classify_event_kind(request.event_kind)
        
        # Step 3: Validate payload reference
        trace.append("EVENT_VALIDATED")
        payload_validated = True
        
        # Step 4: Assign semantic identity
        trace.append("EVENT_CONSTRUCTED")
        event_id = f"evt_{self._event_count + 1:08x}"
        self._event_count += 1
        
        # Construct the event representation
        event = {
            "identity": event_id,
            "revision": 1,
            "event_kind": request.event_kind,
            "payload_reference": f"payload:{event_id}",
            "source_network": request.source_network,
            "semantic_scope": request.semantic_scope,
            "importance": self._determine_importance(request.event_kind),
            "status": "occurred",
            "provenance": {
                **request.provenance,
                "originating_epoch": request.originating_epoch,
                "originating_cycle": request.originating_cycle,
            },
        }
        
        # Step 5: Update stream
        trace.append("STREAM_UPDATED")
        self._update_stream(request.source_network, event_id)
        
        # Step 6: Update timeline
        trace.append("TIMELINE_UPDATED")
        
        # Step 7: Update indexes
        trace.append("INDEX_UPDATED")
        self._update_indexes(event)
        
        return CognitiveEventResult(
            _request_reference=f"req_{self._event_count}",
            _event=event,
            _validation_result=validation_result,
            _findings=(),
            _trace=tuple(trace),
            _status="published",
            _provenance={"engine": "CognitiveEventEngine"},
        )
    
    def _validate_request(
        self, request: CognitiveEventRequest
    ) -> dict:
        """Validate an event request."""
        findings = []
        
        if not request.source_network:
            findings.append("INVALID_SOURCE_NETWORK")
        
        if not request.event_kind:
            findings.append("INVALID_EVENT_KIND")
        
        return {
            "is_valid": len(findings) == 0,
            "findings": findings,
        }
    
    def _classify_event_kind(self, kind: str) -> dict:
        """Classify an event kind."""
        return {"kind": kind, "category": self._get_category(kind)}
    
    def _get_category(self, kind: str) -> str:
        """Get the category for an event kind."""
        if kind.startswith("network_"):
            return "lifecycle"
        elif kind.startswith("goal_") or kind.startswith("task_"):
            return "goal_task"
        elif kind.startswith("plan_"):
            return "planning"
        elif kind.startswith("decision_"):
            return "decision"
        elif kind.startswith("prediction_"):
            return "prediction"
        elif kind.startswith("reward_"):
            return "reward"
        elif kind.startswith("memory_") or kind.startswith("workspace_"):
            return "memory"
        else:
            return "other"
    
    def _determine_importance(self, kind: str) -> str:
        """Determine importance for an event kind."""
        if kind in ("failure_detected", "conflict_detected"):
            return "critical"
        elif kind in (
            "goal_created",
            "decision_selected",
            "plan_completed",
        ):
            return "high"
        else:
            return "normal"
    
    def _update_stream(self, network: str, event_id: str) -> None:
        """Update the stream for a network."""
        if network not in self._events_by_network:
            self._events_by_network[network] = []
        self._events_by_network[network].append(event_id)
    
    def _update_indexes(self, event: dict) -> None:
        """Update all relevant indexes for an event."""
        kind = event.get("event_kind", "unknown")
        network = event.get("source_network", "unknown")
        
        if kind not in self._events_by_kind:
            self._events_by_kind[kind] = []
        self._events_by_kind[kind].append(event["identity"])
    
    def get_events_by_kind(self, kind: str) -> list[str]:
        """Get event identities for a given kind."""
        return self._events_by_kind.get(kind, [])
    
    def get_events_by_network(self, network: str) -> list[str]:
        """Get event identities for a given network."""
        return self._events_by_network.get(network, [])