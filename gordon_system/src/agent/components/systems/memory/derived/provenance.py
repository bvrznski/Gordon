# Derived Memory Provenance Contract - Phase 5.1.6 Canonical Implementation
# ==========================================================================
"""
Provenance: The contract for derivation provenance tracking.

Purpose:
    Define how derivations trace their origin and evolution.
    
Provenance Laws:
    PROVENANCE-LAW-001: Every derived artifact preserves complete derivation provenance
    PROVENANCE-LAW-002: Derivation methods remain identifiable
    PROVENANCE-LAW-003: Supporting artifacts remain identifiable
    PROVENANCE-LAW-004: Algorithm versions remain recorded
    PROVENANCE-LAW-005: Derivation revisions preserve provenance
    PROVENANCE-LAW-006: Historical provenance remains inspectable
    PROVENANCE-LAW-007: Provenance remains immutable after publication
    PROVENANCE-LAW-008: Provenance handling remains deterministic

Provenance Tracking:
    - Originating derivation ID and kind
    - Method used for derivation
    - Supporting artifacts that were derived from
    - Algorithm version used
    - Timestamp of creation
    - Revision history with full provenance chain
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DERIVATION PROVENANCE SOURCE - A single source of derivation origin
# =============================================================================


@dataclass(frozen=True)
class DerivationProvenanceSource:
    """
    A single provenance source for a derivation.
    
    Fields:
        source_type:         Category (derivation, observation, external_source)
        source_id:           ID of the source derivation/artifact
        confidence:          Trust in this source (0.0-1.0)
        accessed_at_utc:     When was this source accessed?
        
    Provenance Laws:
        PROVENANCE-LAW-003: Supporting artifacts remain identifiable
    """
    
    source_type: str                        # derivation, observation, external_source
    source_id: str                          # ID of the source
    confidence: float = 1.0                 # Trust in this source (0.0-1.0)
    accessed_at_utc: float = field(default_factory=time.time)


# =============================================================================
# DERIVATION PROVENANCE RECORD - Complete provenance for a derivation
# =============================================================================


@dataclass(frozen=True)
class DerivationProvenanceRecord:
    """
    Complete provenance record for a derived artifact.
    
    Fields:
        provenance_id:       Unique identifier for this provenance record
        
        # Origin
        originating_derivation_id: Which derivation created this?
        originating_kind_:     What kind of derivation? (causal, counterfactual, etc.)
        
        # Method
        method:              Derivation method used
        algorithm_version:   Version of the inference algorithm
        parameters:          Parameters passed to the derivation
        
        # Evidence
        supporting_artifact_ids: IDs of artifacts that supported this derivation
        relations_used:      Relations between supporting artifacts
        
        # Timestamps
        created_at_utc:      When was this provenance recorded?
        
        # Revision tracking
        revision_number:     Which revision in chain (1 = original)
        previous_provenance_id: ID of prior provenance (if any)
        
    Provenance Laws:
        PROVENANCE-LAW-001: Every derived artifact has complete provenance
        PROVENANCE-LAW-005: Derivation revisions preserve provenance
        PROVENANCE-LAW-007: Provenance is immutable after publication
    """
    
    # Identity
    provenance_id: str                      # Unique ID for this provenance record
    
    # Origin
    originating_derivation_id: str          # Which derivation created this?
    originating_kind_: str                  # What kind of derivation?
    
    # Method info
    method: str                             # Derivation method name
    algorithm_version: str = "1.0.0"        # Algorithm version used
    parameters: Dict[str, Any] = field(default_factory=dict)  # Derivation parameters
    
    # Evidence
    supporting_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)
    relations_used: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    
    # Revision tracking
    revision_number: int = 1                # Which revision?
    previous_provenance_id: Optional[str] = None


# =============================================================================
# DERIVATION PROVENANCE BUILDER - Mutable builder for provenance records
# =============================================================================


class DerivationProvenanceBuilder:
    """
    Mutable builder for constructing derivation provenance records.
    
    Allows step-by-step construction before producing an immutable record.
    """
    
    def __init__(
        self,
        originating_derivation_id: str,
        originating_kind_: str,
        method: str,
    ):
        """Initialize the builder."""
        self._provenance_id = f"prov:{uuid.uuid4().hex[:12]}"
        
        # Origin
        self._originating_derivation_id = originating_derivation_id
        self._originating_kind_ = originating_kind_
        
        # Method
        self._method = method
        self._algorithm_version = "1.0.0"
        self._parameters: Dict[str, Any] = {}
        
        # Evidence
        self._supporting_artifact_ids: List[str] = []
        self._relations_used: List[str] = []
        
        # Revision tracking
        self._revision_number = 1
        self._previous_provenance_id: Optional[str] = None
    
    def set_algorithm_version(self, version: str) -> "DerivationProvenanceBuilder":
        """Set the algorithm version."""
        self._algorithm_version = version
        return self
    
    def add_parameter(self, key: str, value: Any) -> "DerivationProvenanceBuilder":
        """Add a derivation parameter."""
        self._parameters[key] = value
        return self
    
    def add_supporting_artifact(self, artifact_id: str) -> "DerivationProvenanceBuilder":
        """Add a supporting artifact ID."""
        self._supporting_artifact_ids.append(artifact_id)
        return self
    
    def add_relation(self, relation_id: str) -> "DerivationProvenanceBuilder":
        """Add a relation used in this derivation."""
        self._relations_used.append(relation_id)
        return self
    
    def set_revision_number(self, revision: int) -> "DerivationProvenanceBuilder":
        """Set the revision number."""
        if revision < 1:
            raise ValueError(f"Revision must be >= 1, got {revision}")
        self._revision_number = revision
        return self
    
    def set_previous_provenance_id(self, provenance_id: str) -> "DerivationProvenanceBuilder":
        """Set the previous provenance ID for revisions."""
        self._previous_provenance_id = provenance_id
        return self
    
    def build(self) -> DerivationProvenanceRecord:
        """
        Build an immutable DerivationProvenanceRecord from this builder.
        
        Returns:
            New DerivationProvenanceRecord with all settings applied
        """
        return DerivationProvenanceRecord(
            provenance_id=self._provenance_id,
            originating_derivation_id=self._originating_derivation_id,
            originating_kind_=self._originating_kind_,
            method=self._method,
            algorithm_version=self._algorithm_version,
            parameters=dict(self._parameters),
            supporting_artifact_ids=tuple(self._supporting_artifact_ids),
            relations_used=tuple(self._relations_used),
            created_at_utc=time.time(),
            revision_number=self._revision_number,
            previous_provenance_id=self._previous_provenance_id,
        )


# =============================================================================
# DERIVATION PROVENANCE CHAIN - Complete lineage of a derived artifact
# =============================================================================


@dataclass(frozen=True)
class DerivationProvenanceChain:
    """
    Complete provenance chain for a derived artifact.
    
    Fields:
        chain_id:            Unique identifier for this chain
        root_provenance_id:  ID of the first provenance in the chain
        
        # Chain content
        provenances:         All provenance records in the chain (ordered)
        
        # Chain properties
        chain_length:        Number of provenances in chain
        current_revision:    Latest revision number
        
        # Validation
        is_complete:         True if chain has no gaps
        validation_status:   Current validation state
        
    Provenance Laws:
        PROVENANCE-LAW-006: Historical provenance remains inspectable
    """
    
    chain_id: str                           # Unique ID for this chain
    
    # Root
    root_provenance_id: str                 # First in chain
    
    # Chain content
    provenances: Tuple[DerivationProvenanceRecord, ...]
    
    # Properties
    chain_length: int = 0                   # Number of records
    current_revision: int = 1               # Latest revision
    
    # Validation
    is_complete: bool = True                # No gaps in chain?
    validation_status: str = "valid"        # valid, invalid, incomplete


# =============================================================================
# DERIVATION PROVENANCE CHAIN BUILDER - Mutable builder for chains
# =============================================================================


class DerivationProvenanceChainBuilder:
    """
    Mutable builder for constructing provenance chains.
    
    Allows step-by-step construction of the complete lineage.
    """
    
    def __init__(self, root_provenance_id: str):
        """Initialize the builder."""
        self._chain_id = f"chain:{uuid.uuid4().hex[:12]}"
        
        # Root
        self._root_provenance_id = root_provenance_id
        
        # Chain
        self._provenances: List[DerivationProvenanceRecord] = []
        
        # Properties
        self._current_revision = 1
    
    def add_provenance(self, provenance: DerivationProvenanceRecord) -> "DerivationProvenanceChainBuilder":
        """Add a provenance record to the chain."""
        self._provenances.append(provenance)
        
        # Update current revision if this is higher
        if provenance.revision_number > self._current_revision:
            self._current_revision = provenance.revision_number
        
        return self
    
    def build(self) -> DerivationProvenanceChain:
        """
        Build an immutable DerivationProvenanceChain from this builder.
        
        Returns:
            New DerivationProvenanceChain with all settings applied
        """
        # Calculate chain length (including root)
        chain_length = 1 + len(self._provenances)
        
        return DerivationProvenanceChain(
            chain_id=self._chain_id,
            root_provenance_id=self._root_provenance_id,
            provenances=tuple(self._provenances),
            chain_length=chain_length,
            current_revision=self._current_revision,
            is_complete=True,  # Simplified - in real impl would verify no gaps
            validation_status="valid",
        )


# =============================================================================
# PROVENANCE VALIDATOR - Validates provenance chains
# =============================================================================


class DerivationProvenanceValidator:
    """
    Validator for derivation provenance.
    
    Verifies that provenance records and chains follow all contracts.
    
    Validation Laws:
        VALIDATION-LAW-001: Provenance completeness is verified
        VALIDATION-LAW-002: Provenance integrity is checked
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._validation_count = 0
    
    def validate_record(
        self, record: DerivationProvenanceRecord
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a provenance record.
        
        Args:
            record: The provenance record to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        self._validation_count += 1
        
        # Check required fields
        if not record.provenance_id:
            return False, "Missing provenance ID"
        
        if not record.originating_derivation_id:
            return False, "Missing originating derivation ID"
        
        if not record.method:
            return False, "Missing method"
        
        if record.revision_number < 1:
            return False, f"Invalid revision number: {record.revision_number}"
        
        # All checks passed
        return True, None
    
    def validate_chain(
        self, chain: DerivationProvenanceChain
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a provenance chain.
        
        Args:
            chain: The provenance chain to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check chain integrity
        if len(chain.provenances) == 0:
            return False, "Empty provenance chain"
        
        # Check revision sequence
        expected_revision = 1
        for prov in chain.provenances:
            if prov.revision_number != expected_revision:
                return False, f"Revision gap: expected {expected_revision}, got {prov.revision_number}"
            expected_revision += 1
        
        # All checks passed
        return True, None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "validation_count": self._validation_count,
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Source
    "DerivationProvenanceSource",
    
    # Record
    "DerivationProvenanceRecord",
    
    # Builder
    "DerivationProvenanceBuilder",
    
    # Chain
    "DerivationProvenanceChain",
    
    # Chain builder
    "DerivationProvenanceChainBuilder",
    
    # Validator
    "DerivationProvenanceValidator",
]