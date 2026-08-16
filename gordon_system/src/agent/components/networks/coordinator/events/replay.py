# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Replay Models - Semantic History Reconstruction

This module defines how the cognitive event history can be replayed to
reconstruct what happened, independent of runtime execution.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class ReplayScope(Enum):
    """
    Scopes for event replay.
    
    REPLAY SCOPE LAWS (REPLAY-SCOPE-LAW)
    ------------------------------------
    REPLAY-SCOPE-LAW-001: Each replay has exactly one scope
    REPLAY-SCOPE-LAW-002: Scope determines which events are included
    """
    
    GLOBAL = "global"
    """Replay all events across all networks."""
    
    NETWORK = "network"
    """Replay events from a specific network."""
    
    GOAL = "goal"
    """Replay events related to a specific goal."""
    
    TASK = "task"
    """Replay events related to a specific task."""
    
    DOMAIN = "domain"
    """Replay domain-specific events."""
    
    EPISODE = "episode"
    """Replay events from a specific episode."""
    
    INTERACTION = "interaction"
    """Replay events from a specific interaction."""
    
    REFLECTION = "reflection"
    """Replay reflection session events."""


@dataclass(frozen=True)
class CognitiveReplayRequest:
    """
    Request for semantic event replay.
    
    Replay reconstructs what happened, not how the runtime executed.
    
    REPLAY REQUEST LAWS (REPLAY-REQ-LAW)
    ------------------------------------
    REPLAY-REQ-LAW-001: Replay requests specify timeline reference
    REPLAY-REQ-LAW-002: Event range can be specified or all events
    REPLAY-REQ-LAW-003: Filtering policy determines which events to include
    """
    
    # Reference to the timeline to replay
    _timeline_reference: str
    
    # Event range (start and end event identities)
    _event_range: tuple[str | None, str | None] = field(
        default_factory=lambda: (None, None)
    )
    
    # Scope of replay
    _replay_scope: ReplayScope = ReplayScope.GLOBAL
    
    # Filtering policy
    _filtering_policy: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def timeline_reference(self) -> str:
        """Get the timeline reference."""
        return self._timeline_reference
    
    @property
    def start_event(self) -> str | None:
        """Get the starting event identity, if any."""
        return self._event_range[0]
    
    @property
    def end_event(self) -> str | None:
        """Get the ending event identity, if any."""
        return self._event_range[1]
    
    @property
    def replay_scope(self) -> ReplayScope:
        """Get the replay scope."""
        return self._replay_scope
    
    @property
    def filtering_policy(self) -> dict:
        """Get the filtering policy."""
        return self._filtering_policy
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "timeline_reference": self._timeline_reference,
            "start_event": self._event_range[0],
            "end_event": self._event_range[1],
            "replay_scope": self._replay_scope.value,
            "filtering_policy": dict(self._filtering_policy),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveReplayRequest":
        """
        Create a replay request from a dictionary.
        
        Args:
            data: Dictionary with replay request data
            
        Returns:
            New CognitiveReplayRequest instance
        """
        scope_value = data.get("replay_scope", "global")
        try:
            scope = ReplayScope(scope_value)
        except ValueError:
            scope = ReplayScope.GLOBAL
        
        return cls(
            _timeline_reference=data["timeline_reference"],
            _event_range=(data.get("start_event"), data.get("end_event")),
            _replay_scope=scope,
            _filtering_policy=dict(data.get("filtering_policy", {})),
            _provenance=dict(data.get("provenance", {})),
        )


@dataclass(frozen=True)
class CognitiveReplayResult:
    """
    Result of a semantic replay operation.
    
    REPLAY RESULT LAWS (REPLAY-RESULT-LAW)
    --------------------------------------
    REPLAY-RESULT-LAW-001: Replay reconstructs semantic history
    REPLAY-RESULT-LAW-002: Replay never invokes runtime execution
    REPLAY-RESULT-LAW-003: Replay preserves ordering
    """
    
    # Replayed events (by identity)
    _replayed_events: tuple[str, ...] = field(default_factory=tuple)
    
    # Reconstructed timelines from replay
    _reconstructed_timelines: dict[str, list[str]] = field(
        default_factory=dict
    )
    
    # Reconstructed episodes from replay
    _reconstructed_episodes: dict[str, list[str]] = field(
        default_factory=dict
    )
    
    # Findings from replay
    _findings: dict = field(default_factory=dict)
    
    # Limitations of the replay
    _limitations: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    @property
    def replayed_events(self) -> tuple[str, ...]:
        """Get the identities of replayed events."""
        return self._replayed_events
    
    @property
    def reconstructed_timelines(self) -> dict[str, list[str]]:
        """Get reconstructed timelines from replay."""
        return self._reconstructed_timelines
    
    @property
    def reconstructed_episodes(self) -> dict[str, list[str]]:
        """Get reconstructed episodes from replay."""
        return self._reconstructed_episodes
    
    @property
    def findings(self) -> dict:
        """Get the findings from replay."""
        return self._findings
    
    @property
    def limitations(self) -> dict:
        """Get the limitations of the replay."""
        return self._limitations
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of replayed events."""
        return len(self._replayed_events)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "replayed_events": list(self._replayed_events),
            "reconstructed_timelines": self._reconstructed_timelines,
            "reconstructed_episodes": self._reconstructed_episodes,
            "findings": dict(self._findings),
            "limitations": dict(self._limitations),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveReplayResult":
        """
        Create a replay result from a dictionary.
        
        Args:
            data: Dictionary with replay result data
            
        Returns:
            New CognitiveReplayResult instance
        """
        return cls(
            _replayed_events=tuple(data.get("replayed_events", [])),
            _reconstructed_timelines=dict(data.get("reconstructed_timelines", {})),
            _reconstructed_episodes=dict(data.get("reconstructed_episodes", {})),
            _findings=dict(data.get("findings", {})),
            _limitations=dict(data.get("limitations", {})),
            _provenance=dict(data.get("provenance", {})),
        )