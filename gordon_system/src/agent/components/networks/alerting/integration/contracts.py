# Alerting Network Integration Contracts - Phase 4.1.6
# ======================================================
#
# Canonical integration contracts separating the Alerting Network from
# all downstream Gordon subsystems.
#
# This module defines ALL contracts through which the Alerting Network may
# interact with other systems. The Network depends ONLY on these contracts,
# never on implementations.

"""
Integration Contracts for AlertingNetwork - Phase 4.1.6

ARCHITECTURE:
=============

The Alerting Network is computationally complete and independent.
It interacts with Gordon subsystems through explicit, typed contracts:

INPUT CONTRACTS (Network consumes):
+-------------------------------+
| AlertingSignalProvider        |
|   Provides: Normalized signals|
+-------------------------------+

+-------------------------------+
| AlertingContextProvider       |
|   Provides: Context modifiers |
|   - active_focus              |
|   - task_criticality          |
|   - execution_pressure        |
+-------------------------------+

+-------------------------------+
| AlertingStateProvider         |
|   Provides: Computational     |
|   state for continuity        |
+-------------------------------+

OUTPUT CONTRACTS (Network provides):
+-------------------------------+
| AlertingAssessmentConsumer    |
|   Consumes: Completed         |
|   assessments                 |
+-------------------------------+

+-------------------------------+
| AlertingDiagnosticsSink       |
|   Receives: Traces, events,   |
|   diagnostic data             |
+-------------------------------+

CONFIGURATION:
+-------------------------------+
| AlertingConfigurationProvider |
|   Supports: Runtime-independent|
|   configuration               |
+-------------------------------+

VALIDATION:
+-------------------------------+
| AlertingValidationContract    |
|   Defines: Validation         |
|   expectations                |
+-------------------------------+

DEPENDENCY DIRECTION:
=====================

    Capability/Executive System
        ↓ (provides context, consumes assessment)
    Alerting Contract Layer
        ↓ (consumes input, provides output)
    Alerting Network
        ↓ (computational implementation)
    Computational Pipeline

The Network NEVER depends on implementations. Only contracts.

OWNERSHIP RULES:
================

1. Context Ownership: The Provider owns context. Network only consumes it.
2. Assessment Ownership: Network produces assessments but never decides what happens next.
3. State Ownership: The StateProvider owns state. Network may read/write through contract.
4. Diagnostics Ownership: The Sink owns diagnostic storage. Network sends to it.

VERSIONING POLICY:
==================

Every public contract shall expose:
- version: String identifier
- compatibility_policy: "strict" | "backward" | "forward" | "full"
- deprecation_policy: When/如何 deprecated items are removed
- extension_strategy: How new functionality is added

EXTENSION POINTS:
=================

All contracts are designed for extension without breaking existing consumers:

1. SignalProvider: May add signal types via enum
2. ContextProvider: May add context fields with defaults
3. StateProvider: May add state keys with versioned serialization
4. AssessmentConsumer: May add assessment variants via type tag
5. DiagnosticsSink: May add event types via enum
6. ConfigurationProvider: May add config sections via nested objects
7. ValidationContract: May add validation rules via predicate functions

EXCEPTIONS:
===========

The Network MUST NOT:

1. Depend on Executive implementations
2. Depend on Thread implementations  
3. Depend on Loop implementations
4. Depend on Cycle implementations
5. Depend on Capability implementations
6. Decide core scheduling or future consumers
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Protocol,
    runtime_checkable,
)
from datetime import datetime
from enum import Enum, auto
import uuid


# =============================================================================
# VERSIONING CONSTANTS - Phase 4.1.6
# =============================================================================

ALERTING_CONTRACTS_VERSION = "1.0.0"
COMPATIBILITY_POLICY = "backward"  # Backward compatible with future consumers
DEPRECATION_POLICY = "three_releases"  # Deprecated items removed after 3 releases
EXTENSION_STRATEGY = "additive_only"  # New functionality added without breaking


# =============================================================================
# IDENTITY TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class AlertingContractId:
    """Unique identifier for an integration contract instance."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "AlertingContractId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True, slots=True)
class AssessmentDeliveryId:
    """Unique identifier for an assessment delivery."""
    
    value: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @classmethod
    def generate(cls) -> "AssessmentDeliveryId":
        return cls(value=str(uuid.uuid4()))


# =============================================================================
# INPUT CONTRACTS - Network consumes these
# =============================================================================

@runtime_checkable
class AlertingSignalProvider(Protocol):
    """
    Provides normalized signals to the AlertingNetwork.
    
    The Network depends on this contract but NEVER owns it.
    Signal ownership remains with the Provider.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add signal types)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new signal types via enum)
    
    OWNERSHIP:
        - Signals are owned by the Provider
        - Network consumes signals but never modifies them
        - Network does not store signals after processing
    
    DEPENDENCIES:
        - AlertingSignalProvider is the only dependency on signal data
        - No direct access to perception implementations
    
    USE BY:
        - AlertingNetwork.assess() calls this provider for current signals
        
    EXAMPLE CONSUMERS:
        - SignalRegistry (provides signals from various sources)
        - StreamSubscriber (receives signals from streams)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_current_signal(
        self,
        signal_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the current normalized signal.
        
        Args:
            signal_id: Optional specific signal to retrieve. If None,
                       returns the most recent/primary signal.
                       
        Returns:
            Dictionary containing normalized signal data with keys:
            - intensity: float in [0.0, 1.0]
            - source: str identifying origin
            - modality: str for routing classification
            - timestamp: ISO format datetime string
            
        Note:
            The returned dict is a snapshot. Network must not modify it.
        """
        ...
    
    @abstractmethod
    def get_signal_batch(
        self,
        count: int = 10,
        before_timestamp: Optional[datetime] = None,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Get a batch of recent signals for history-based assessment.
        
        Args:
            count: Number of signals to retrieve (bounded)
            before_timestamp: Retrieve signals before this time
            
        Returns:
            Tuple of signal dictionaries in chronological order
            (oldest first, newest last).
            
        Note:
            The batch is bounded - no unbounded memory access.
        """
        ...
    
    @abstractmethod
    def has_pending_signals(self) -> bool:
        """Return True if there are signals waiting for processing."""
        ...


@runtime_checkable
class AlertingContextProvider(Protocol):
    """
    Provides contextual modifiers to the AlertingNetwork.
    
    The Network consumes context but NEVER owns it. Context ownership
    remains with the Provider system (Executive, Workspace, etc.).
    
    CONTEXT FIELDS:
        - active_focus: Current focus strength [0.0, 1.0]
        - task_criticality: Task importance level [0.0, 1.0]  
        - execution_pressure: Current time/resource pressure [0.0, 1.0]
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add context fields)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new context types via enum)
    
    OWNERSHIP:
        - Context is owned by the Provider system
        - Network only reads context, never writes it
        - Context changes are made by the owning system
        
    DEPENDENCIES:
        - AlertingContextProvider is the only dependency on context data
        - No direct access to Executive or Workspace implementations
    
    USE BY:
        - AlertingNetwork uses context to modulate demand scores
        - Context affects: focus modulation, task criticality effects,
                          resource pressure adjustments
        
    EXAMPLE CONSUMERS:
        - Executive (provides active_focus and task_criticality)
        - ResourceMonitor (provides execution_pressure)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_context_snapshot(
        self,
    ) -> Dict[str, Optional[float]]:
        """
        Get current context values as a snapshot.
        
        Returns:
            Dictionary with context field names as keys and float values
            in [0.0, 1.0] range, or None if not available.
            
            Expected fields:
                - active_focus: Current focus strength (0.0-1.0)
                - task_criticality: Task importance level (0.0-1.0)
                - execution_pressure: Time/resource pressure (0.0-1.0)
                
        Note:
            The snapshot is immutable. Network must not modify it.
        """
        ...
    
    @abstractmethod
    def get_focus_strength(self) -> Optional[float]:
        """Get the active focus strength, if available."""
        ...
    
    @abstractmethod
    def get_task_criticality(self) -> Optional[float]:
        """Get the current task criticality level, if available."""
        ...
    
    @abstractmethod
    def get_execution_pressure(self) -> Optional[float]:
        """Get the current execution pressure level, if available."""
        ...
    
    @abstractmethod
    def has_context_changed_since(
        self,
        last_check: datetime,
    ) -> bool:
        """
        Check if context has changed since the given time.
        
        Args:
            last_check: Last time context was checked
            
        Returns:
            True if any context field has been modified since last_check
        """
        ...


@runtime_checkable
class AlertingStateProvider(Protocol):
    """
    Provides computational state to the AlertingNetwork.
    
    The Network may read/write state through this contract but ownership
    remains with the Provider. State provides continuity across assessments.
    
    STATE TYPES:
        - Temporal baseline statistics
        - Habituation counters  
        - Refractory period tracking
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add state keys)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new state types via enum)
    
    OWNERSHIP:
        - State is owned by the Provider system
        - Network may read/write through contract interface
        - No direct access to internal state structures
        
    DEPENDENCIES:
        - AlertingStateProvider is the only dependency on state management
        - No direct access to persistent storage implementations
    
    USE BY:
        - AlertingNetwork reads state for habituation/refractory effects
        - AlertingNetwork writes state updates after each assessment
        
    EXAMPLE CONSUMERS:
        - MemoryStore (provides bounded state persistence)
        - SessionState (manages runtime state)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_state(
        self,
        state_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get current state for a specific key.
        
        Args:
            state_key: State identifier (e.g., "habituation", "refractory")
            
        Returns:
            Dictionary containing state data, or None if not found
            
        Example keys:
            - "baseline": Temporal baseline statistics
            - "habituation": Habituation level and counters
            - "refractory": Refractory period tracking
        """
        ...
    
    @abstractmethod
    def set_state(
        self,
        state_key: str,
        state_data: Dict[str, Any],
    ) -> None:
        """
        Set state for a specific key.
        
        Args:
            state_key: State identifier
            state_data: New state data to store
            
        Note:
            This is the only write interface. No direct state mutation.
        """
        ...
    
    @abstractmethod
    def has_state(self, state_key: str) -> bool:
        """Check if state exists for a given key."""
        ...
    
    @abstractmethod
    def delete_state(self, state_key: str) -> None:
        """
        Delete state for a specific key.
        
        Args:
            state_key: State identifier to remove
        """
        ...


# =============================================================================
# OUTPUT CONTRACTS - Network provides these
# =============================================================================

@runtime_checkable
class AlertingAssessmentConsumer(Protocol):
    """
    Consumes completed assessments from the AlertingNetwork.
    
    The Network produces assessments but NEVER decides what happens next.
    Assessment ownership transfers to the Consumer upon delivery.
    
    ASSESSMENT FLOW:
        1. Network computes assessment (deterministic)
        2. Network delivers via this contract
        3. Consumer decides: route, log, act, or discard
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may handle new assessment fields)
    DEPRECATION: three_releases policy  
    EXTENSION: additive_only (new assessment types via enum)
    
    OWNERSHIP:
        - Network owns computation only
        - Consumer owns the delivered assessment
        - No shared state or references after delivery
        
    DEPENDENCIES:
        - AlertingAssessmentConsumer is the only output dependency
        - No direct access to downstream systems
    
    USE BY:
        - AlertingNetwork calls this contract after each assessment
        - Consumer handles routing, logging, and action decisions
        
    EXAMPLE CONSUMERS:
        - Executive (decides attention allocation)
        - AttentionCapability (modulates focus)
        - MonitoringLoop (tracks alert history)
        
    NOTIFICATIONS TO:
        - Executive Capability (may override based on policy)
        - Attention Capability (adjusts focus strength)
        - Arbitration (handles conflicts between demands)
        - ExecutionLoop (may trigger interruption)
        - MonitoringLoop (records for analysis)
        - WorkingMemory (stores recent assessments)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def consume_assessment(
        self,
        assessment: Dict[str, Any],
    ) -> None:
        """
        Consume a completed assessment.
        
        Args:
            assessment: Assessment dictionary with required fields:
                - demand_score: float [0.0, 1.0]
                - confidence: float [0.0, 1.0]  
                - level: str (NEGLIGIBLE|LOW|MODERATE|HIGH|CRITICAL)
                - recommendation: str
                - features: dict with computed feature values
                - reasons: tuple of reason strings
                - provenance: dict with source information
                
        Note:
            The Network delivers the assessment. Consumer decides what to do.
        """
        ...
    
    @abstractmethod
    def consume_assessment_batch(
        self,
        assessments: Tuple[Dict[str, Any], ...],
    ) -> None:
        """
        Consume a batch of assessments (for efficiency).
        
        Args:
            assessments: Tuple of assessment dictionaries
            
        Note:
            This is optional - may be implemented by high-throughput consumers
        """
        ...
    
    @abstractmethod
    def get_consumption_count(self) -> int:
        """Return total number of assessments consumed."""
        ...


@runtime_checkable
class AlertingDiagnosticsSink(Protocol):
    """
    Receives diagnostic traces and events from the AlertingNetwork.
    
    The Network sends diagnostics but never owns the storage. Ownership
    remains with the Sink system (Observability, Monitoring, etc.).
    
    DIAGNOSTIC TYPES:
        - Trace events: Processing steps
        - Metric events: Counters and gauges
        - Error events: Exceptions and warnings
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add event types)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new event types via enum)
    
    OWNERSHIP:
        - Diagnostics are owned by the Sink system
        - Network only writes events to it
        - No access to stored diagnostic data
        
    DEPENDENCIES:
        - AlertingDiagnosticsSink is the only output dependency for diagnostics
        - No direct access to storage or logging implementations
    
    USE BY:
        - AlertingNetwork sends trace events during assessment
        - Sink handles storage, aggregation, and display
        
    EXAMPLE CONSUMERS:
        - ObservabilityService (stores and displays traces)
        - MonitoringLoop (collects metrics for alerting)
        - DebugConsole (shows real-time diagnostics)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def send_trace_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Send a trace event to the diagnostics sink.
        
        Args:
            event_type: Event category (e.g., "assessment_start", 
                       "signal_processed", "assessment_complete")
            data: Event-specific payload
            timestamp: Event time (defaults to current time)
            
        Example events:
            - "assessment_start": {signal_id, timestamp}
            - "feature_extracted": {name, value}
            - "modulation_applied": {factor, magnitude}
            - "assessment_complete": {demand_score, level, assessment_id}
        """
        ...
    
    @abstractmethod
    def send_metric_event(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Send a metric event to the diagnostics sink.
        
        Args:
            metric_name: Metric identifier (e.g., "assessments_per_minute")
            value: Numeric value
            labels: Optional key-value pairs for filtering
            
        Example metrics:
            - "total_assessments": count of all assessments
            - "high_demand_alerts": count of high/critical alerts
            - "average_demand_score": mean demand score
            - "assessment_latency_ms": processing time in milliseconds
        """
        ...
    
    @abstractmethod
    def send_error_event(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send an error/warning event to the diagnostics sink.
        
        Args:
            error_type: Category (e.g., "validation", "state_error")
            message: Human-readable description
            context: Optional additional data
            
        Example errors:
            - "signal_missing": intensity field not provided
            - "context_invalid": context values out of range
            - "state_corruption": state data inconsistent
        """
        ...
    
    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered diagnostics to storage."""
        ...


# =============================================================================
# CONFIGURATION CONTRACT
# =============================================================================

@runtime_checkable
class AlertingConfigurationProvider(Protocol):
    """
    Provides runtime-independent configuration to the AlertingNetwork.
    
    Configuration is immutable once loaded. The Network may read but never
    modify it. Configuration ownership remains with the Provider.
    
    CONFIGURATION TYPES:
        - Thresholds: Decision boundaries (e.g., demand thresholds)
        - Weights: Feature weight multipliers
        - Limits: Capacity and boundedness constraints
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add config sections)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new config keys via nested objects)
    
    OWNERSHIP:
        - Configuration is owned by the Provider system
        - Network only reads configuration
        - No runtime modification capability
        
    DEPENDENCIES:
        - AlertingConfigurationProvider is the only dependency on config
        - No direct access to file/system configuration implementations
    
    USE BY:
        - AlertingNetwork reads thresholds during assessment
        - Configuration affects: classification, feature weights,
                                state bounds, and limits
        
    EXAMPLE CONSUMERS:
        - ConfigManager (loads from files/environment)
        - RuntimeConfig (runtime-adjustable config with validation)
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def get_config(
        self,
        section: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get configuration values.
        
        Args:
            section: Specific config section to retrieve. If None,
                     returns all configuration.
                     
        Returns:
            Dictionary containing configuration values
            
        Example sections:
            - "thresholds": Decision boundaries
            - "weights": Feature weighting multipliers
            - "limits": Capacity constraints
            - "classification": Alert level definitions
        """
        ...
    
    @abstractmethod
    def get_threshold(
        self,
        threshold_name: str,
    ) -> Optional[float]:
        """Get a specific threshold value."""
        ...
    
    @abstractmethod
    def get_weight(
        self,
        weight_name: str,
    ) -> Optional[float]:
        """Get a specific feature weight value."""
        ...
    
    @abstractmethod
    def is_section_available(self, section: str) -> bool:
        """Check if a configuration section exists."""
        ...


# =============================================================================
# VALIDATION CONTRACT
# =============================================================================

@runtime_checkable
class AlertingValidationContract(Protocol):
    """
    Defines validation expectations for the AlertingNetwork.
    
    This contract specifies what inputs are valid, what state transitions
    are allowed, and what assessment properties must hold.
    
    VALIDATION RULES:
        - Input validity: What fields are required
        - State validity: Which transitions are permitted  
        - Assessment validity: What properties assessments must satisfy
        
    VERSION: 1.0.0
    COMPATIBILITY: backward (future consumers may add validation rules)
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new validation predicates via enum)
    
    OWNERSHIP:
        - Validation rules are owned by this contract definition
        - Network follows these rules but doesn't define them
        
    DEPENDENCIES:
        - AlertingValidationContract defines the rules
        - Network implements validation against them
        
    USE BY:
        - Network validates inputs against expectations
        - Consumer may validate outputs before processing
    """
    
    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...
    
    @property
    def compatibility_policy(self) -> str:
        """Return the compatibility policy string."""
        ...
    
    @abstractmethod
    def is_valid_input(
        self,
        input_data: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an input for the AlertingNetwork.
        
        Args:
            input_data: Input dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
            
        Validates:
            - Required fields present
            - Field types correct
            - Values in valid ranges
            - No conflicting fields
        """
        ...
    
    @abstractmethod
    def is_valid_state_transition(
        self,
        from_state: Dict[str, Any],
        to_state: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a state transition.
        
        Args:
            from_state: Current state dictionary
            to_state: Proposed new state dictionary
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
            
        Validates:
            - State keys match expected schema
            - Only allowed transitions occur
            - State bounds are maintained
        """
        ...
    
    @abstractmethod
    def is_valid_assessment(
        self,
        assessment: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an output assessment.
        
        Args:
            assessment: Assessment dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
            
        Validates:
            - Required fields present
            - Values in valid ranges [0.0, 1.0]
            - Level/recommendation consistency
            - No implementation leakage
        """
        ...
    
    @abstractmethod
    def get_validation_rules(self) -> Tuple[str, ...]:
        """Return all validation rule identifiers."""
        ...


# =============================================================================
# HELPER TYPES FOR CONSUMER IMPLEMENTATIONS
# =============================================================================

class AssessmentDeliveryMode(Enum):
    """Mode of assessment delivery to consumers."""
    
    IMMEDIATE = "immediate"     # Deliver as soon as ready
    BATCHED = "batched"         # Batch multiple assessments
    DEFERRED = "deferred"       # Defer for later processing
    DROPPABLE = "droppable"     # May be dropped if consumer overloaded


@dataclass(frozen=True, slots=True)
class AssessmentDelivery:
    """Complete assessment delivery record."""
    
    delivery_id: AssessmentDeliveryId
    assessment: Dict[str, Any]
    timestamp: datetime
    mode: AssessmentDeliveryMode
    consumer_id: Optional[str] = None  # If targeting specific consumer
    
    @property
    def is_droppable(self) -> bool:
        return self.mode == AssessmentDeliveryMode.DROPPABLE


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    """Immutable snapshot of alerting context."""
    
    active_focus: Optional[float] = None
    task_criticality: Optional[float] = None
    execution_pressure: Optional[float] = None
    
    def is_empty(self) -> bool:
        return all(v is None for v in [self.active_focus, self.task_criticality, self.execution_pressure])
    
    def to_dict(self) -> Dict[str, Optional[float]]:
        return {
            "active_focus": self.active_focus,
            "task_criticality": self.task_criticality,
            "execution_pressure": self.execution_pressure,
        }


@dataclass(frozen=True, slots=True)
class SignalBatch:
    """Batch of signals for history-based assessment."""
    
    signals: Tuple[Dict[str, Any], ...]
    before_timestamp: Optional[datetime] = None
    count: int = field(default=0, init=False)
    
    def __post_init__(self):
        object.__setattr__(self, "count", len(self.signals))
    
    @property
    def is_empty(self) -> bool:
        return self.count == 0
    
    @property
    def oldest_timestamp(self) -> Optional[datetime]:
        if not self.signals:
            return None
        first = self.signals[0]
        ts_str = first.get("timestamp")
        return datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else None
    
    @property
    def newest_timestamp(self) -> Optional[datetime]:
        if not self.signals or len(self.signals) < 2:
            return self.oldest_timestamp
        last = self.signals[-1]
        ts_str = last.get("timestamp")
        return datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else None


@dataclass(frozen=True, slots=True)
class TracingEvent:
    """Trace event for diagnostics."""
    
    event_type: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp),
            "data": dict(self.data),
            "trace_id": self.trace_id,
        }