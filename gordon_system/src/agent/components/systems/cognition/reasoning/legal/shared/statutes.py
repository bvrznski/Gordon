# Statute Management - Phase 7.47 Part 1
# =======================================

"""
Statute Management Contract.

Statutes are primary legal sources enacted by legislative bodies.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class Statute:
    """
    A statute (law) enacted by a legislative body.
    
    A statute includes:
        - Authority and source identification
        - Effective dates
        - Applicable provisions
        - Related regulations and precedents
    
    Statutes form the foundation of legal obligations.
    """
    
    # Identity
    statute_id: str                           # Unique identifier
    
    # Authority
    legislative_authority: str                # Who enacted this?
    enactment_date_utc: float                 # When was it enacted?
    
    # Scope
    subject_matter: Tuple[str, ...] = ()      # What topics does it cover?
    territorial_scope: Tuple[str, ...] = ()   # Where does it apply?
    
    # Content
    statute_text: str = ""                    # Full text of the statute
    sections: Tuple[str, ...] = ()            # Section identifiers
    
    # Status
    effective_from_utc: float = field(default_factory=time.time)
    effective_to_utc: Optional[float] = None  # When repealed/amended
    is_active: bool = True                    # Current status
    
    # Related provisions
    related_regulations: Tuple[str, ...] = () # Associated regulations
    related_precedents: Tuple[str, ...] = ()  # Related court decisions
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legislative_authority: str,
        statute_text: str,
        subject_matter: Optional[List[str]] = None,
        sections: Optional[List[str]] = None,
    ) -> Statute:
        """Create a new statute."""
        return cls(
            statute_id=f"statute:{uuid.uuid4().hex[:16]}",
            legislative_authority=legislative_authority,
            statute_text=statute_text,
            subject_matter=tuple(subject_matter or []),
            sections=tuple(sections or []),
            enactment_date_utc=time.time(),
        )


@dataclass(frozen=True)
class StatuteManager:
    """
    Manager for statutes.
    
    Handles statute discovery, selection, and
    relationship management across legal systems.
    """
    
    manager_id: str                           # Unique identifier
    
    # Known statutes
    statutes: Dict[str, Statute] = field(default_factory=dict)
    
    # Selection filters
    selected_jurisdiction_ids: Tuple[str, ...] = ()
    subject_matter_filters: Tuple[str, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        selected_jurisdiction_ids: Optional[List[str]] = None,
        subject_matter_filters: Optional[List[str]] = None,
    ) -> StatuteManager:
        """Create a new statute manager."""
        return cls(
            manager_id=f"statute_manager:{uuid.uuid4().hex[:16]}",
            selected_jurisdiction_ids=tuple(selected_jurisdiction_ids or []),
            subject_matter_filters=tuple(subject_matter_filters or []),
        )
    
    def add_statute(self, statute: Statute) -> StatuteManager:
        """Add a statute to the manager."""
        new_statutes = dict(self.statutes)
        new_statutes[statute.statute_id] = statute
        return dataclass_replace(
            self,
            statutes=new_statutes,
        )
    
    def get_active_statutes(
        self,
    ) -> Dict[str, Statute]:
        """Get all currently active statutes."""
        now = time.time()
        return {
            sid: s for sid, s in self.statutes.items()
            if (
                s.is_active
                and s.effective_from_utc <= now
                and (s.effective_to_utc is None or s.effective_to_utc >= now)
            )
        }


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "Statute",
    "StatuteManager",
]