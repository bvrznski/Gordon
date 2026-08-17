# Knowledge Transfer Pipeline - Phase 7.4
# =======================================

"""
Canonical Transfer Pipeline Contract.

Transfer applies mapped knowledge to the target problem.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class KnowledgeTransfer:
    """
    A knowledge transfer from source case to target problem.
    
    Transfer may include:
        - Relations (how elements relate)
        - Constraints (what must hold)
        - Causal mechanisms (why things happen)
        - Strategies (how to solve problems)
        - Procedures (step-by-step methods)
    
    Transfer remains provisional; it must be validated before use.
    """
    
    # Identity
    transfer_id: str                          # Unique identifier
    
    # Source of transfer
    originating_mapping_id: str               # Which mapping enabled this?
    source_case_id: str                       # Where did knowledge come from?
    
    # Transferred elements
    transferred_elements: Tuple[str, ...] = ()  # What was transferred?
    
    # Expected validity in target domain
    expected_validity: float = 0.0            # How valid is this transfer?
    adaptation_rules: Tuple[str, ...] = ()    # How must it be adapted?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def element_count(self) -> int:
        """Number of elements transferred."""
        return len(self.transferred_elements)
    
    @classmethod
    def create(
        cls,
        originating_mapping_id: str,
        source_case_id: str,
        transferred_elements: Optional[List[str]] = None,
        expected_validity: float = 0.5,
    ) -> KnowledgeTransfer:
        """Create a new knowledge transfer."""
        return cls(
            transfer_id=f"knowledge_transfer:{uuid.uuid4().hex[:16]}",
            originating_mapping_id=originating_mapping_id,
            source_case_id=source_case_id,
            transferred_elements=tuple(transferred_elements or []),
            expected_validity=expected_validity,
        )
    
    def add_element(self, element: str) -> KnowledgeTransfer:
        """Return a new transfer with the element added."""
        return dataclass_replace(
            self,
            transferred_elements=self.transferred_elements + (element,),
        )


@dataclass(frozen=True)
class TransferPipeline:
    """
    A knowledge transfer pipeline result.
    
    Pipeline flow:
        Validated Mapping
              ↓
        Transfer Candidates
              ↓
        Constraint Adaptation
              ↓
        Conflict Detection
              ↓
        Transfer Validation
              ↓
        Reasoning Output
    
    Transferred knowledge remains provisional until validated.
    """
    
    # Identity
    pipeline_id: str                          # Unique identifier
    
    # Pipeline components
    source_mapping_id: str                    # Which mapping is being transferred?
    
    # Transfer results
    transfer_candidates: Tuple[KnowledgeTransfer, ...] = ()
    
    # Adaptation and validation
    conflicts_detected: Tuple[str, ...] = ()  # Any issues with transfer?
    adaptation_applied: Tuple[str, ...] = ()  # How was knowledge adapted?
    
    # Overall assessment
    is_transferable: bool = False             # Can knowledge be safely transferred?
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def candidate_count(self) -> int:
        """Number of transfer candidates."""
        return len(self.transfer_candidates)
    
    @classmethod
    def create(
        cls,
        source_mapping_id: str,
    ) -> TransferPipeline:
        """Create a new transfer pipeline result."""
        return cls(
            pipeline_id=f"transfer_pipeline:{uuid.uuid4().hex[:16]}",
            source_mapping_id=source_mapping_id,
        )
    
    def add_candidate(self, candidate: KnowledgeTransfer) -> TransferPipeline:
        """Add a transfer candidate."""
        return dataclass_replace(
            self,
            transfer_candidates=self.transfer_candidates + (candidate,),
        )
    
    def detect_conflict(self, conflict_description: str) -> TransferPipeline:
        """Record a detected conflict."""
        return dataclass_replace(
            self,
            conflicts_detected=self.conflicts_detected + (conflict_description,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "KnowledgeTransfer",
    "TransferPipeline",
]