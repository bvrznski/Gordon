# Gordon Phase 5.7.1-I: Consciousness Exceptions
# ===============================================================================

"""
Canonical exception hierarchy for the Consciousness capability.

All exceptions inherit from ConsciousnessError and provide typed failure
information with retryability, underlying causes, and partial commit status.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# BASE EXCEPTION CLASSES
# =============================================================================

class ConsciousnessError(Exception):
    """
    Base exception for all Consciousness capability errors.
    
    All Consciousness exceptions inherit from this base class, providing
    a single catch point for capability-related failures.
    """
    pass


class ConsciousnessUnavailable(ConsciousnessError):
    """
    Raised when Consciousness is not available for operations.
    
    This may occur during:
        - Capability shutdown (STOPPING/STOPPED state)
        - Failed recovery (FAILED state)
        - Permanent unavailability
    
    Action: Retry after capability becomes available, or abort operation.
    """
    
    def __init__(self, message: str = "Consciousness is unavailable"):
        super().__init__(message)


class ConsciousnessNotReady(ConsciousnessError):
    """
    Raised when Consciousness is not ready for the requested operation.
    
    This may occur during:
        - INITIALIZING state (still setting up)
        - PAUSED state (temporarily suspended)
        - DRAINING state (shutting down, accepting no new work)
    
    Action: Wait for capability to enter ACTIVE or READY state.
    """
    
    def __init__(self, message: str = "Consciousness is not ready"):
        super().__init__(message)


class InvalidContribution(ConsciousnessError):
    """
    Raised when a contribution submission is invalid.
    
    This may occur due to:
        - Malformed contribution envelope
        - Invalid source identity
        - Expired freshness timestamp
        - Missing required fields
    
    Action: Validate and resubmit with correct structure.
    """
    
    def __init__(
        self,
        message: str = "Invalid contribution",
        contribution_id: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        self.contribution_id = contribution_id
        self.reason = reason
        full_message = f"{message}"
        if contribution_id:
            full_message += f" (contribution_id={contribution_id})"
        if reason:
            full_message += f": {reason}"
        super().__init__(full_message)


class InvalidProjection(ConsciousnessError):
    """
    Raised when a projection submission is invalid.
    
    This may occur due to:
        - Malformed projection envelope
        - Invalid source identity
        - Invalid extension reference
        - Missing required fields
    
    Action: Validate and resubmit with correct structure.
    """
    
    def __init__(
        self,
        message: str = "Invalid projection",
        projection_id: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        self.projection_id = projection_id
        self.reason = reason
        full_message = f"{message}"
        if projection_id:
            full_message += f" (projection_id={projection_id})"
        if reason:
            full_message += f": {reason}"
        super().__init__(full_message)


class UnknownSource(ConsciousnessError):
    """
    Raised when referencing an unknown source identity.
    
    This may occur during:
        - Contribution submission with unregistered source
        - Projection submission with unregistered source
        - Query with source filter for unregistered source
    
    Action: Register the source before submitting contributions or projections.
    """
    
    def __init__(
        self,
        message: str = "Unknown source identity",
        source_id: Optional[str] = None,
    ):
        self.source_id = source_id
        full_message = f"{message}"
        if source_id:
            full_message += f" (source_id={source_id})"
        super().__init__(full_message)


class DuplicateSource(ConsciousnessError):
    """
    Raised when attempting to register a duplicate source identity.
    
    Sources must have unique, stable identities. Attempting to re-register
    an existing source without proper lifecycle management triggers this error.
    
    Action: Use the existing registration or unregister and re-register.
    """
    
    def __init__(
        self,
        message: str = "Duplicate source identity",
        source_id: Optional[str] = None,
    ):
        self.source_id = source_id
        full_message = f"{message}"
        if source_id:
            full_message += f" (source_id={source_id})"
        super().__init__(full_message)


class UnknownExtension(ConsciousnessError):
    """
    Raised when referencing an unknown extension identity.
    
    This may occur during:
        - Transition request with unregistered extension
        - Query referencing unregistered extension snapshot
    
    Action: Register the extension before using it in transitions or queries.
    """
    
    def __init__(
        self,
        message: str = "Unknown extension identity",
        extension_id: Optional[str] = None,
    ):
        self.extension_id = extension_id
        full_message = f"{message}"
        if extension_id:
            full_message += f" (extension_id={extension_id})"
        super().__init__(full_message)


class DuplicateExtension(ConsciousnessError):
    """
    Raised when attempting to register a duplicate extension identity.
    
    Extensions must have unique, stable identities. Attempting to re-register
    an existing extension without proper lifecycle management triggers this error.
    
    Action: Use the existing registration or unregister and re-register.
    """
    
    def __init__(
        self,
        message: str = "Duplicate extension identity",
        extension_id: Optional[str] = None,
    ):
        self.extension_id = extension_id
        full_message = f"{message}"
        if extension_id:
            full_message += f" (extension_id={extension_id})"
        super().__init__(full_message)


class ExtensionDependencyCycle(ConsciousnessError):
    """
    Raised when extension dependencies form a cycle.
    
    Extensions must have acyclic dependency graphs. This error indicates
    circular dependencies that would prevent deterministic ordering.
    
    Action: Break the dependency cycle by removing or reordering dependencies.
    """
    
    def __init__(
        self,
        message: str = "Extension dependency cycle detected",
        cycle_path: Optional[list[str]] = None,
    ):
        self.cycle_path = cycle_path
        full_message = f"{message}"
        if cycle_path:
            full_message += f" ({' -> '.join(cycle_path)})"
        super().__init__(full_message)


class SourceGenerationMismatch(ConsciousnessError):
    """
    Raised when source generation in a contribution doesn't match expected.
    
    Each source maintains its own generation counter. Contributions must
    use the correct generation to prevent out-of-order or stale submissions.
    
    Action: Use the current generation for this source.
    """
    
    def __init__(
        self,
        message: str = "Source generation mismatch",
        source_id: Optional[str] = None,
        expected_generation: int = 0,
        actual_generation: int = 0,
    ):
        self.source_id = source_id
        self.expected_generation = expected_generation
        self.actual_generation = actual_generation
        full_message = f"{message}"
        if source_id:
            full_message += f" (source_id={source_id})"
        full_message += f", expected={expected_generation}, actual={actual_generation}"
        super().__init__(full_message)


class ContextTransitionConflict(ConsciousnessError):
    """
    Raised when concurrent transition attempts conflict.
    
    Only one transition may be committed at a time. This error indicates
    a race condition where multiple transitions were proposed simultaneously.
    
    Action: Retry the transition with current context generation.
    """
    
    def __init__(
        self,
        message: str = "Context transition conflict",
        context_id: Optional[str] = None,
        previous_generation: int = 0,
        attempt_generation: int = 0,
    ):
        self.context_id = context_id
        self.previous_generation = previous_generation
        self.attempt_generation = attempt_generation
        full_message = f"{message}"
        if context_id:
            full_message += f" (context_id={context_id})"
        full_message += f", prev_gen={previous_generation}, attempt_gen={attempt_generation}"
        super().__init__(full_message)


class ContextPublicationFailure(ConsciousnessError):
    """
    Raised when atomic publication of a new context generation fails.
    
    This may occur due to:
        - I/O failure during persistence
        - Concurrent modification conflict
        - Invalid state after transition
    
    Action: The previous valid snapshot is preserved. Retry with current state.
    """
    
    def __init__(
        self,
        message: str = "Context publication failed",
        context_id: Optional[str] = None,
        generation: int = 0,
        underlying_error: Optional[Exception] = None,
    ):
        self.context_id = context_id
        self.generation = generation
        self.underlying_error = underlying_error
        full_message = f"{message}"
        if context_id:
            full_message += f" (context_id={context_id})"
        if generation > 0:
            full_message += f", gen={generation}"
        super().__init__(full_message)


# =============================================================================
# UTILITY EXCEPTIONS
# =============================================================================

class ExtensionUnavailable(ConsciousnessError):
    """
    Raised when an extension is unavailable for transition.
    
    This may occur during:
        - Required extension not ready
        - Optional extension failure in degraded mode
        - Extension timeout
    
    Action: Wait for extension to become available or accept degraded mode.
    """
    
    def __init__(
        self,
        message: str = "Extension unavailable",
        extension_id: Optional[str] = None,
    ):
        self.extension_id = extension_id
        full_message = f"{message}"
        if extension_id:
            full_message += f" (extension_id={extension_id})"
        super().__init__(full_message)


class ExtensionIncompatible(ConsciousnessError):
    """
    Raised when an extension is incompatible with current context.
    
    This may occur due to:
        - Schema version mismatch
        - Contract version incompatibility
        - Dependency unmet
    
    Action: Update extension or use compatible version.
    """
    
    def __init__(
        self,
        message: str = "Extension incompatible",
        extension_id: Optional[str] = None,
        required_version: Optional[str] = None,
        actual_version: Optional[str] = None,
    ):
        self.extension_id = extension_id
        self.required_version = required_version
        self.actual_version = actual_version
        full_message = f"{message}"
        if extension_id:
            full_message += f" (extension_id={extension_id})"
        super().__init__(full_message)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    # Base classes
    "ConsciousnessError",
    "ConsciousnessUnavailable",
    "ConsciousnessNotReady",
    # Validation exceptions
    "InvalidContribution",
    "InvalidProjection",
    "UnknownSource",
    "DuplicateSource",
    "UnknownExtension",
    "DuplicateExtension",
    # Dependency exceptions
    "ExtensionDependencyCycle",
    # Generation exceptions
    "SourceGenerationMismatch",
    # Transition exceptions
    "ContextTransitionConflict",
    "ContextPublicationFailure",
    # Utility exceptions
    "ExtensionUnavailable",
    "ExtensionIncompatible",
)