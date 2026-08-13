# Phase 3.11.14 - Cross-Stream Correlation Replay Support
# =========================================================

"""
Replay Support Module for Cross-Stream Correlation & Causation Architecture.

Provides deterministic reconstruction of relationship graphs from stream history.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time
import hashlib


# =============================================================================
# REPLAY MODES
# =============================================================================


class CorrelationReplayMode(Enum):
    """Mode of correlation graph replay."""
    CONSTRUCTION = "construction"     # Build relationships from scratch
    RESTORATION = "restoration"       # Restore from snapshot
    VERIFICATION = "verification"     # Verify existing graph
    RECONSTRUCTION = "reconstruction" # Reconstruct with partial data


# =============================================================================
# RELATIONSHIP SNAPSHOT
# =============================================================================


@dataclass(frozen=True)
class CorrelationEdgeSnapshot:
    """
    Snapshot of one correlation edge for replay.
    
    Contains only the information needed to reconstruct the edge.
    """
    source_record_id: str
    target_record_id: str
    stream_id_source: str
    stream_id_target: str
    relationship_kind: str  # RelationshipKind.value
    correlation_id: Optional[str] = None
    metadata_json: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CausationEdgeSnapshot:
    """
    Snapshot of one causation edge for replay.
    
    Causation edges are reconstructed with original evidence references.
    """
    cause_record_id: str
    effect_record_id: str
    stream_id_cause: str
    stream_id_effect: str
    relationship_kind: str  # RelationshipKind.value
    evidence_references: Tuple[str, ...]
    metadata_json: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EpisodeMembershipSnapshot:
    """
    Snapshot of one episode membership for replay.
    """
    record_id: str
    stream_id: str
    episode_id: str
    role_in_episode: Optional[str] = None


# =============================================================================
# REPLAY STATE
# =============================================================================


@dataclass(frozen=True)
class RelationshipReplayState:
    """
    State tracking for relationship graph replay.
    
    Allows incremental construction of the relationship graph during replay.
    """
    replay_id: str
    replay_mode: CorrelationReplayMode
    
    # Progress
    edges_processed: int = 0
    edges_reconstructed: int = 0
    errors_encountered: int = 0
    
    # Timestamps
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Result summary
    correlation_edges_count: int = 0
    causation_edges_count: int = 0
    episode_memberships_count: int = 0


class RelationshipReplayResult:
    """
    Result of a relationship graph replay operation.
    
    Contains the reconstructed graph and any warnings/errors.
    """

    def __init__(
        self,
        replay_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        self.replay_id = replay_id
        self.success = success
        self.error_message = error_message
        
        # Graph state (populated during replay)
        self.correlation_edge_snapshots: List[CorrelationEdgeSnapshot] = []
        self.causation_edge_snapshots: List[CausationEdgeSnapshot] = []
        self.episode_membership_snapshots: List[EpisodeMembershipSnapshot] = []
        
        # Metadata
        self.start_time_utc = time.time()
        self.end_time_utc: Optional[float] = None
    
    def add_correlation_edge(self, snapshot: CorrelationEdgeSnapshot) -> None:
        """Add a correlation edge snapshot."""
        self.correlation_edge_snapshots.append(snapshot)
    
    def add_causation_edge(self, snapshot: CausationEdgeSnapshot) -> None:
        """Add a causation edge snapshot."""
        self.causation_edge_snapshots.append(snapshot)
    
    def add_episode_membership(self, snapshot: EpisodeMembershipSnapshot) -> None:
        """Add an episode membership snapshot."""
        self.episode_membership_snapshots.append(snapshot)
    
    def complete(self) -> RelationshipReplayState:
        """Mark replay as completed and return state."""
        self.end_time_utc = time.time()
        
        return RelationshipReplayState(
            replay_id=self.replay_id,
            replay_mode=CorrelationReplayMode.CONSTRUCTION,
            edges_processed=len(self.correlation_edge_snapshots) + 
                           len(self.causation_edge_snapshots) + 
                           len(self.episode_membership_snapshots),
            edges_reconstructed=len(self.correlation_edge_snapshots) +
                               len(self.causation_edge_snapshots) +
                               len(self.episode_membership_snapshots),
            correlation_edges_count=len(self.correlation_edge_snapshots),
            causation_edges_count=len(self.causation_edge_snapshots),
            episode_memberships_count=len(self.episode_membership_snapshots),
        )


class RelationshipReplayEngine:
    """
    Engine for replaying relationship graph construction from stream history.
    
    Key principle: Replay reconstructs relationships but NEVER computes new
    causal relationships. Causation must come from original stream records.
    """

    def __init__(
        self,
        max_edges: int = 1_000_000,
        allow_causation_reconstruction: bool = False,
    ):
        """
        Initialize replay engine.
        
        Args:
            max_edges: Maximum edges to process (safety limit)
            allow_causation_reconstruction: If True, may infer causation
                from stream order. Default: False (strict mode).
        """
        self.max_edges = max_edges
        self.allow_causation_reconstruction = allow_causation_reconstruction
    
    def replay_from_snapshots(
        self,
        correlation_edge_snapshots: List[CorrelationEdgeSnapshot],
        causation_edge_snapshots: List[CausationEdgeSnapshot],
        episode_membership_snapshots: List[EpisodeMembershipSnapshot],
    ) -> RelationshipReplayResult:
        """
        Replay relationship graph from pre-collected snapshots.
        
        This is the primary replay path - relationships are reconstructed
        exactly as they were originally recorded, no inference.
        """
        result = RelationshipReplayResult(
            replay_id=f"replay-{time.monotonic_ns()}"
        )
        
        # Process correlation edges
        for snapshot in correlation_edge_snapshots[:self.max_edges]:
            result.add_correlation_edge(snapshot)
        
        # Process causation edges (if allowed)
        if self.allow_causation_reconstruction:
            for snapshot in causation_edge_snapshots[:self.max_edges]:
                result.add_causation_edge(snapshot)
        elif causation_edge_snapshots:
            result.error_message = "Causation reconstruction disabled but causation snapshots present"
        
        # Process episode memberships
        for snapshot in episode_membership_snapshots[:self.max_edges]:
            result.add_episode_membership(snapshot)
        
        return result
    
    def verify_replay_integrity(
        self,
        correlation_edge_snapshots: List[CorrelationEdgeSnapshot],
        causation_edge_snapshots: List[CausationEdgeSnapshot],
        episode_membership_snapshots: List[EpisodeMembershipSnapshot],
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify replay integrity without reconstructing.
        
        Returns:
            (is_valid, error_message) tuple
        """
        total_edges = (
            len(correlation_edge_snapshots) +
            len(causation_edge_snapshots) +
            len(episode_membership_snapshots)
        )
        
        if total_edges > self.max_edges:
            return False, f"Edge count {total_edges} exceeds limit {self.max_edges}"
        
        # Verify no duplicates in correlation edges
        seen_correlation = set()
        for snapshot in correlation_edge_snapshots:
            key = (
                snapshot.source_record_id,
                snapshot.target_record_id,
                snapshot.relationship_kind,
            )
            if key in seen_correlation:
                return False, f"Duplicate correlation edge: {key}"
            seen_correlation.add(key)
        
        # Verify causation edges have evidence (if reconstruction enabled)
        if not self.allow_causation_reconstruction and causation_edge_snapshots:
            for snapshot in causation_edge_snapshots:
                if not snapshot.evidence_references:
                    return False, f"Causation edge missing evidence: {snapshot.cause_record_id} -> {snapshot.effect_record_id}"
        
        return True, None
    
    def reconstruct_graph(
        self,
        result: RelationshipReplayResult,
    ) -> Dict[str, Any]:
        """
        Reconstruct graph state from replay result.
        
        Returns a dictionary representation of the reconstructed graph
        (references only, no live objects).
        """
        return {
            "replay_id": result.replay_id,
            "success": result.success,
            "correlation_edges": [
                {
                    "source_record_id": s.source_record_id,
                    "target_record_id": s.target_record_id,
                    "stream_id_source": s.stream_id_source,
                    "stream_id_target": s.stream_id_target,
                    "relationship_kind": s.relationship_kind,
                }
                for s in result.correlation_edge_snapshots
            ],
            "causation_edges": [
                {
                    "cause_record_id": s.cause_record_id,
                    "effect_record_id": s.effect_record_id,
                    "stream_id_cause": s.stream_id_cause,
                    "stream_id_effect": s.stream_id_effect,
                    "relationship_kind": s.relationship_kind,
                    "evidence_count": len(s.evidence_references),
                }
                for s in result.causation_edge_snapshots
            ],
            "episode_memberships": [
                {
                    "record_id": s.record_id,
                    "stream_id": s.stream_id,
                    "episode_id": s.episode_id,
                }
                for s in result.episode_membership_snapshots
            ],
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Replay modes
    "CorrelationReplayMode",
    
    # Snapshots
    "CorrelationEdgeSnapshot",
    "CausationEdgeSnapshot",
    "EpisodeMembershipSnapshot",
    
    # Replay state and result
    "RelationshipReplayState",
    "RelationshipReplayResult",
    
    # Engine
    "RelationshipReplayEngine",
]