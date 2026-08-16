# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Cognitive Episode Models - Coherent Collections of Related Events

This module defines how events form coherent cognitive episodes such as
problem-solving sessions, dialogue, planning, etc.
"""

from dataclasses import dataclass, field
from enum import Enum, unique


@unique
class CognitiveEpisodeKind(Enum):
    """
    Kinds of cognitive episodes.
    
    EPISODE KIND LAWS (EP-KIND-LAW)
    -------------------------------
    EP-KIND-LAW-001: Each episode has exactly one kind
    EP-KIND-LAW-002: Episode kinds represent semantic experiences
    """
    
    PROBLEM_SOLVING = "problem_solving"
    """A problem-solving episode."""
    
    DIALOGUE = "dialogue"
    """A dialogue or conversation episode."""
    
    PLANNING = "planning"
    """A planning episode."""
    
    NAVIGATION = "navigation"
    """A navigation or movement episode."""
    
    LEARNING = "learning"
    """A learning episode."""
    
    REFLECTION = "reflection"
    """A reflection episode."""
    
    WORKFLOW = "workflow"
    """A standard workflow execution episode."""


@dataclass(frozen=True)
class CognitiveEpisodeIdentity:
    """
    Unique identity for a cognitive episode.
    """
    
    _identity: str
    _episode_kind: str
    
    @property
    def identity(self) -> str:
        """Get the episode identity."""
        return self._identity
    
    @property
    def episode_kind(self) -> str:
        """Get the episode kind."""
        return self._episode_kind


@dataclass(frozen=True)
class CognitiveEpisode:
    """
    A coherent collection of related cognitive events.
    
    Episodes represent meaningful units of cognition like problem-solving,
    dialogue, planning, etc. They group related events without duplicating them.
    
    EPISODE LAWS (EP-LAW)
    ---------------------
    EP-LAW-001: Episodes represent coherent cognitive experiences
    EP-LAW-002: Episode boundaries are explicit
    EP-LAW-003: Episodes preserve participating events
    EP-LAW-004: Episodes preserve participating networks
    """
    
    # Episode identity
    _episode_identity: str
    
    # Kind of episode
    _episode_kind: CognitiveEpisodeKind
    
    # Start event (first event in the episode)
    _start_event: str | None = None
    
    # End event (last event in the episode, if known)
    _end_event: str | None = None
    
    # Participating events (all events in this episode)
    _participating_events: tuple[str, ...] = field(default_factory=tuple)
    
    # Networks that participated
    _participating_networks: set[str] = field(default_factory=set)
    
    # Goals addressed by this episode
    _goals: tuple[str, ...] = field(default_factory=tuple)
    
    # Findings from the episode
    _findings: dict = field(default_factory=dict)
    
    # Limitations of the episode
    _limitations: dict = field(default_factory=dict)
    
    # Provenance information
    _provenance: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate episode components."""
        if not self._episode_identity:
            raise ValueError("Episode identity cannot be empty")
        
        if not self._episode_kind:
            raise ValueError("Episode kind cannot be empty")
    
    @property
    def episode_identity(self) -> str:
        """Get the episode's unique identity."""
        return self._episode_identity
    
    @property
    def episode_kind(self) -> CognitiveEpisodeKind:
        """Get the episode kind."""
        return self._episode_kind
    
    @property
    def start_event(self) -> str | None:
        """Get the start event, if any."""
        return self._start_event
    
    @property
    def end_event(self) -> str | None:
        """Get the end event, if known."""
        return self._end_event
    
    @property
    def participating_events(self) -> tuple[str, ...]:
        """Get all events participating in this episode."""
        return self._participating_events
    
    @property
    def participating_networks(self) -> set[str]:
        """Get networks that participated in this episode."""
        return self._participating_networks
    
    @property
    def goals(self) -> tuple[str, ...]:
        """Get the goals addressed by this episode."""
        return self._goals
    
    @property
    def findings(self) -> dict:
        """Get the findings from this episode."""
        return self._findings
    
    @property
    def limitations(self) -> dict:
        """Get the limitations of this episode."""
        return self._limitations
    
    @property
    def provenance(self) -> dict:
        """Get the provenance information."""
        return self._provenance
    
    def event_count(self) -> int:
        """Get the number of events in this episode."""
        return len(self._participating_events)
    
    def is_complete(self) -> bool:
        """Check if this episode has a known end."""
        return self._end_event is not None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "episode_identity": self._episode_identity,
            "episode_kind": self._episode_kind.value,
            "start_event": self._start_event,
            "end_event": self._end_event,
            "participating_events": list(self._participating_events),
            "participating_networks": list(self._participating_networks),
            "goals": list(self._goals),
            "findings": dict(self._findings),
            "limitations": dict(self._limitations),
            "provenance": dict(self._provenance),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CognitiveEpisode":
        """
        Create an episode from a dictionary.
        
        Args:
            data: Dictionary with episode data
            
        Returns:
            New CognitiveEpisode instance
        """
        return cls(
            _episode_identity=data["episode_identity"],
            _episode_kind=CognitiveEpisodeKind(data.get("episode_kind", "problem_solving")),
            _start_event=data.get("start_event"),
            _end_event=data.get("end_event"),
            _participating_events=tuple(data.get("participating_events", [])),
            _participating_networks=set(data.get("participating_networks", [])),
            _goals=tuple(data.get("goals", [])),
            _findings=dict(data.get("findings", {})),
            _limitations=dict(data.get("limitationss", {})),
            _provenance=dict(data.get("provenance", {})),
        )