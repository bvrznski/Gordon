"""
Oriented Network Audit Exceptions

Defines exception classes used throughout the audit subsystem.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditError(Exception):
    """
    Base exception for all audit-related errors.
    
    This is a production-quality error that preserves context and provenance
    for debugging and auditing purposes.
    """
    
    message: str
    """Human-readable error message."""
    
    audit_context: Optional[Dict[str, Any]] = None
    """Contextual information about the audit when error occurred."""
    
    def __str__(self) -> str:
        base_msg = self.message
        if self.audit_context:
            context_str = ", ".join(
                f"{k}={v!r}" for k, v in self.audit_context.items()
            )
            return f"{base_msg} (context: {context_str})"
        return base_msg


@dataclass(frozen=True)
class AuditConfigError(AuditError):
    """
    Raised when audit configuration is invalid or incomplete.
    
    This indicates a problem with the audit setup rather than
    execution or graph analysis.
    """
    
    config_key: Optional[str] = None
    """The specific configuration key that caused the error."""
    
    def __post_init__(self) -> None:
        if self.config_key:
            if not self.message:
                object.__setattr__(
                    self,
                    "message",
                    f"Invalid audit configuration for '{self.config_key}'"
                )
            if self.audit_context is None:
                object.__setattr__(
                    self,
                    "audit_context",
                    {"config_key": self.config_key}
                )


@dataclass(frozen=True)
class AuditExecutionError(AuditError):
    """
    Raised when an audit operation fails during execution.
    
    This indicates a failure in the audit process itself, such as
    adapter errors or internal logic failures.
    """
    
    step: Optional[str] = None
    """The audit step during which the error occurred."""
    
    def __post_init__(self) -> None:
        if self.step:
            if not self.message:
                object.__setattr__(
                    self,
                    "message",
                    f"Audit execution failed at step '{self.step}'"
                )
            if self.audit_context is None:
                object.__setattr__(
                    self,
                    "audit_context",
                    {"step": self.step}
                )


@dataclass(frozen=True)
class AuditValidationError(AuditError):
    """
    Raised when validation of audit results fails.
    
    This indicates that the audit completed but produced invalid
    or inconsistent results.
    """
    
    validation_rule: Optional[str] = None
    """The validation rule that failed."""
    
    def __post_init__(self) -> None:
        if self.validation_rule:
            if not self.message:
                object.__setattr__(
                    self,
                    "message",
                    f"Validation failed for rule '{self.validation_rule}'"
                )
            if self.audit_context is None:
                object.__setattr__(
                    self,
                    "audit_context",
                    {"validation_rule": self.validation_rule}
                )


# =============================================================================
# AUDIT-SPECIFIC EXCEPTIONS
# =============================================================================


class GraphAdapterError(AuditExecutionError):
    """Raised when a graph adapter operation fails."""


class AdapterNotConnected(GraphAdapterError):
    """Raised when adapter operations are attempted without connection."""


class NodeNotFoundError(AuditValidationError):
    """
    Raised when an expected node is not found in the graph.
    
    This may indicate graph corruption or a race condition.
    """
    
    node_id: str
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(
            message=f"Node not found: {node_id}",
            audit_context={"node_id": node_id}
        )


class EdgeNotFoundError(AuditValidationError):
    """
    Raised when an expected edge is not found in the graph.
    
    This may indicate graph corruption or a race condition.
    """
    
    source_id: str
    target_id: str
    
    def __init__(self, source_id: str, target_id: str):
        self.source_id = source_id
        self.target_id = target_id
        super().__init__(
            message=f"Edge not found: {source_id} -> {target_id}",
            audit_context={"source_id": source_id, "target_id": target_id}
        )


class CycleDetectedError(AuditValidationError):
    """
    Raised when a cycle is detected where acyclicity is required.
    
    This indicates a violation of graph constraints.
    """
    
    cycle_nodes: tuple
    
    def __init__(self, cycle_nodes: tuple):
        self.cycle_nodes = cycle_nodes
        super().__init__(
            message=f"Cycle detected in nodes: {cycle_nodes}",
            audit_context={"cycle_nodes": list(cycle_nodes)}
        )


class InvalidGraphStateError(AuditValidationError):
    """
    Raised when the graph is in an invalid state for the requested operation.
    
    This may indicate structural corruption or constraint violations.
    """
    
    state_description: str
    
    def __init__(self, state_description: str):
        self.state_description = state_description
        super().__init__(
            message=f"Invalid graph state: {state_description}",
            audit_context={"state_description": state_description}
        )

__all__ = [
    "AuditError",
    "AuditConfigError",
    "AuditExecutionError",
    "AuditValidationError",
    "GraphAdapterError",
    "AdapterNotConnected",
    "NodeNotFoundError",
    "EdgeNotFoundError",
    "CycleDetectedError",
    "InvalidGraphStateError",
]