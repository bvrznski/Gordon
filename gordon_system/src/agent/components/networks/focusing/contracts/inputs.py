# Focusing Network Input Contracts - Phase 4.2.8
# ===============================================

"""
Input contracts for the FocusingNetwork.

These define stable interfaces for providing focus candidates and context
to the network without exposing implementation details.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


class FocusModality:
    """Focus modality type."""
    VISUAL = "visual"
    COGNITIVE = "cognitive"
    WORKSPACE = "workspace"


# =============================================================================
# FOCUS CANDIDATE PROVIDER
# =============================================================================

class FocusCandidateProvider(ABC):
    """
    Provider of focus candidates.

    This interface defines how external systems can supply focus targets to
    the FocusingNetwork without exposing internal implementation details.

    The provider NEVER owns the candidates - it only provides access.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new candidate types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_candidates(self) -> Tuple[str, ...]:
        """
        Return the set of candidate target IDs.

        Returns:
            Tuple of unique candidate identifiers. Never None or empty unless
            no candidates are available.
        """

    @abstractmethod
    def get_modality(self, candidate_id: str) -> Optional[FocusModality]:
        """
        Return the modality for a given candidate.

        Args:
            candidate_id: The target ID to query

        Returns:
            FocusModality or None if unknown
        """


# =============================================================================
# FOCUS CONTEXT PROVIDER
# =============================================================================

class FocusContextProvider(ABC):
    """
    Provider of focus context information.

    Context includes current state from higher layers that may influence
    focus allocation decisions without being part of the candidates themselves.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new context types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_current_focus_strength(self) -> Optional[float]:
        """
        Return current overall focus strength (0.0 to 1.0).

        Returns:
            Current global focus intensity, or None if unavailable
        """

    @abstractmethod
    def get_active_targets(self) -> Tuple[str, ...]:
        """
        Return currently active focus target IDs.

        These are targets that have been allocated focus in the recent past
        and may continue to be maintained.
        """

    @abstractmethod
    def get_relevance_hint(self, candidate_id: str) -> Optional[float]:
        """
        Return a relevance hint from external systems.

        Args:
            candidate_id: The target ID to query

        Returns:
            Relevance score (0.0 to 1.0), or None if not available
        """


# =============================================================================
# FOCUS STATE PROVIDER
# =============================================================================

class FocusStateProvider(ABC):
    """
    Provider of current focus state information.

    This interface provides access to existing focus targets and their
    associated metadata without coupling to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new state keys via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_current_focus_targets(self) -> Tuple[str, ...]:
        """
        Get currently active focus target IDs.

        These are targets that are currently receiving sustained attention.

        Returns:
            Tuple of active target IDs
        """

    @abstractmethod
    def get_target_strength(self, target_id: str) -> float:
        """
        Get the current strength for a focus target.

        Args:
            target_id: The target to query

        Returns:
            Strength value (0.0 to 1.0)
        """


# =============================================================================
# OBJECTIVE PROVIDER
# =============================================================================

class ObjectiveProvider(ABC):
    """
    Provider of current objectives for focus allocation.

    This interface provides access to active goals and objectives that may
    influence focus decisions without coupling to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new objective types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_active_objectives(self) -> Tuple[str, ...]:
        """
        Get currently active objective IDs.

        Returns:
            Tuple of active objective identifiers
        """

    @abstractmethod
    def get_objective_priority(self, objective_id: str) -> Optional[float]:
        """
        Get priority for a specific objective.

        Args:
            objective_id: The objective ID to query

        Returns:
            Priority value (0.0 to 1.0), or None if not tracked
        """

    @abstractmethod
    def get_objective_deadline(self, objective_id: str) -> Optional[datetime]:
        """
        Get deadline for a specific objective.

        Args:
            objective_id: The objective ID to query

        Returns:
            Deadline datetime, or None if no deadline
        """


# =============================================================================
# WORKSPACE PROJECTION PROVIDER
# =============================================================================

class WorkspaceProjectionProvider(ABC):
    """
    Provider of workspace state projections.

    This interface provides access to current workspace state that may influence
    focus allocation without coupling to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new projection types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_workspace_state(self) -> Dict[str, Any]:
        """
        Get current workspace state as a dictionary.

        Returns:
            Workspace state dictionary
        """

    @abstractmethod
    def get_active_workspace_targets(self) -> Tuple[str, ...]:
        """
        Get currently active workspace target IDs.

        Returns:
            Tuple of active workspace target IDs
        """


# =============================================================================
# WORKING MEMORY PROJECTION PROVIDER
# =============================================================================

class WorkingMemoryProjectionProvider(ABC):
    """
    Provider of working memory state projections.

    This interface provides access to current working memory contents that may
    influence focus allocation without coupling to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new memory types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_working_memory_contents(self) -> Tuple[Dict[str, Any], ...]:
        """
        Get current working memory contents.

        Returns:
            Tuple of working memory item dictionaries
        """

    @abstractmethod
    def get_relevant_memories(
        self,
        candidate_id: str,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Get memories relevant to a specific candidate.

        Args:
            candidate_id: The candidate ID to query

        Returns:
            Tuple of relevant memory dictionaries
        """


# =============================================================================
# ALERTING ASSESSMENT PROVIDER
# =============================================================================

class AlertingAssessmentProvider(ABC):
    """
    Provider of alerting assessments that may influence focus allocation.

    This interface provides access to AlertingNetwork assessments without coupling
    to the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new alert types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_current_alerts(self) -> Tuple[Dict[str, Any], ...]:
        """
        Get current alert assessments.

        Returns:
            Tuple of alert assessment dictionaries
        """

    @abstractmethod
    def get_active_alert_targets(self) -> Tuple[str, ...]:
        """
        Get target IDs with active alerts.

        Returns:
            Tuple of target IDs with active alerts
        """


# =============================================================================
# POLICY PROJECTION PROVIDER
# =============================================================================

class PolicyProjectionProvider(ABC):
    """
    Provider of policy projections that constrain focus allocation.

    This interface provides access to policy constraints without coupling to
    the FocusingNetwork implementation.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new policy types via enum)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_policy_constraints(self) -> Tuple[Dict[str, Any], ...]:
        """
        Get current policy constraints.

        Returns:
            Tuple of policy constraint dictionaries
        """

    @abstractmethod
    def get_allowed_focus_types(self) -> Tuple[str, ...]:
        """
        Get allowed focus target types according to policy.

        Returns:
            Tuple of allowed focus type identifiers
        """


# =============================================================================
# CONFIGURATION PROVIDER
# =============================================================================

class ConfigurationProvider(ABC):
    """
    Provider of configuration for the FocusingNetwork.

    This interface provides runtime-independent configuration without coupling
    to the FocusingNetwork implementation. Configuration is read-only once loaded.
    
    VERSION: 1.0.0
    COMPATIBILITY: backward
    DEPRECATION: three_releases policy
    EXTENSION: additive_only (new config sections via nested objects)
    """

    @property
    def version(self) -> str:
        """Return the contract version string."""
        ...

    @abstractmethod
    def get_configuration(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration values.

        Args:
            section: Specific config section to retrieve. If None,
                     returns all configuration.

        Returns:
            Dictionary containing configuration values
        """

    @abstractmethod
    def get_threshold(self, threshold_name: str) -> Optional[float]:
        """Get a specific threshold value."""

    @abstractmethod
    def is_config_valid(self) -> bool:
        """Check if current configuration is valid."""


__all__ = [
    # Provider contracts (Network consumes)
    "FocusCandidateProvider",
    "FocusContextProvider",
    "FocusStateProvider",
    "ObjectiveProvider",
    "WorkspaceProjectionProvider",
    "WorkingMemoryProjectionProvider",
    "AlertingAssessmentProvider",
    "PolicyProjectionProvider",
    "ConfigurationProvider",
]