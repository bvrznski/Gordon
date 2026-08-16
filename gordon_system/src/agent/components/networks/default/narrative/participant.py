# Narrative Participant Models
# ============================

"""
Immutable models for narrative participants.

ARCHITECTURAL PRINCIPLES:
    - Participants are referenced, not duplicated identities
    - No live objects in participant records
    - Confidence and provenance preserved
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# NARRATIVE PARTICIPANT - Entity involved in narrative
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativeParticipant:
    """
    Immutable representation of a participant in a narrative.
    
    A participant may be:
        - Gordon (the agent)
        - A user or external person
        - An organization or group
        - A subsystem or service
        - An abstract entity
        
    Participants are referenced by ID, not duplicated identities.
    """
    
    # Identity
    participant_id: str
    """Unique identifier for this participant."""
    
    source_identity_reference: Optional[str] = None
    """Reference to authoritative identity record (if applicable)."""
    
    role_in_narrative: str = ""
    """Role played in this narrative (e.g., 'actor', 'observer', 'affected_party')."""
    
    # Perspective availability
    perspective_available: bool = True
    """Whether perspective information is available for this participant."""
    
    perspective_kind: Optional[str] = None
    """Perspective kind if known (agent_first_person, external_observer, etc.)."""
    
    # Relevant context
    relevant_objectives: Tuple[str, ...] = field(default_factory=tuple)
    """Objectives relevant to this participant in the narrative."""
    
    relevant_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """Commitments held by or about this participant."""
    
    # Quality metrics
    confidence: float = 0.5
    """Confidence in participant identity and role (0.0 to 1.0)."""
    
    provenance: str = "canonical"
    """Provenance reference for this participant record."""
    
    @classmethod
    def agent_participant(cls) -> NarrativeParticipant:
        """Create a participant representing Gordon (the agent)."""
        return cls(
            participant_id="agent",
            source_identity_reference=None,
            role_in_narrative="actor",
            perspective_available=True,
            perspective_kind="agent_first_person",
            confidence=1.0,
        )
    
    @classmethod
    def user_participant(
        cls,
        user_id: str,
        confidence: float = 0.8,
    ) -> NarrativeParticipant:
        """Create a participant representing the user."""
        return cls(
            participant_id=f"user_{user_id}",
            source_identity_reference=None,
            role_in_narrative="participant",
            perspective_available=True,
            perspective_kind="external_observer",
            confidence=confidence,
        )
    
    @classmethod
    def external_entity(
        cls,
        entity_id: str,
        role: str = "",
        confidence: float = 0.6,
    ) -> NarrativeParticipant:
        """Create a participant for an external entity."""
        return cls(
            participant_id=entity_id,
            source_identity_reference=None,
            role_in_narrative=role,
            perspective_available=False,
            perspective_kind="unknown",
            confidence=confidence,
        )