# Workspace Persistence Module
# ============================

"""
Canonical Persistence models for workspace states.

Persistence semantics define when and how workspace state records are eligible
for storage, what scope of data is persisted, and who has authority over persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class PersistenceEligibility:
    """
    Record of whether a workspace state is eligible for persistence.
    
    Persistence eligibility is determined by semantic criteria, not runtime factors.
    """
    
    # Eligibility status
    is_eligible: bool = False
    """Whether this state is eligible for persistence."""
    
    eligibility_kind: str = "full"
    """Kind of eligibility (full, partial, none)."""
    
    # Reasoning
    reason: str = ""
    """Human-readable explanation for eligibility decision."""
    
    # Criteria met
    criteria_met: Tuple[str, ...] = field(default_factory=tuple)
    """Criteria that made this state eligible."""
    
    criteria_not_met: Tuple[str, ...] = field(default_factory=tuple)
    """Criteria that were not satisfied."""
    
    # Validity period (semantic only, not runtime timing)
    valid_until_utc: float = 0.0
    """When eligibility expires (if applicable)."""
    
    @property
    def can_be_persisted(self) -> bool:
        """Check if this state can be persisted."""
        return self.is_eligible and len(self.criteria_met) > 0


@dataclass(frozen=True)
class PersistenceScope:
    """
    Scope of persistence for a workspace state.
    
    Defines what aspects of the state are persisted and what are excluded.
    """
    
    # Scope kind
    scope_kind: str = "complete"
    """Kind of scope (complete, minimal, metadata-only)."""
    
    # Included elements
    include_state_id: bool = True
    """Whether to persist the state ID."""
    
    include_revision: bool = True
    """Whether to persist the revision number."""
    
    include_snapshot: bool = True
    """Whether to persist the snapshot data."""
    
    include_delta_reference: bool = True
    """Whether to persist references to applied deltas."""
    
    include_transition_history: bool = False
    """Whether to persist transition history (may be large)."""
    
    include_evidence: bool = False
    """Whether to persist semantic evidence (may contain sensitive info)."""
    
    # Excluded elements
    exclude_runtime_data: bool = True
    """Runtime data is always excluded from persistence."""
    
    exclude_temporal_reference: bool = True
    """Runtime timestamps are excluded; use semantic references instead."""
    
    # Storage hints
    preferred_storage_medium: str = "immutable"
    """Preferred storage medium (immutable, mutable, cache)."""
    
    retention_policy: str = "long_term"
    """Retention policy for this persisted data."""


@dataclass(frozen=True)
class PersistenceAuthority:
    """
    Authority record for persistence operations.
    
    Captures who has permission to persist workspace states and under what conditions.
    """
    
    # Authority identity
    authority_id: str = ""
    """Unique identifier of the persistence authority."""
    
    authority_kind: str = "system"
    """Kind of authority (system, user, external)."""
    
    # Permissions
    can_persist: bool = True
    """Whether this authority can persist states."""
    
    can_delete_persistence: bool = False
    """Whether this authority can delete persisted records."""
    
    can_modify_persistence: bool = False
    """Whether this authority can modify existing persistence."""
    
    # Scope limitations
    max_retention_days: int = 365
    """Maximum retention period in days."""
    
    max_storage_size_bytes: int = 104857600  # 100MB default
    """Maximum storage size for persisted data."""
    
    # Audit
    last_audit_utc: float = 0.0
    """When authority was last audited."""
    
    audit_log_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of audit logs for this authority."""


@dataclass(frozen=True)
class PersistenceRecord:
    """
    Record of a persistence operation.
    
    Captures when and how workspace state data was persisted without embedding
    runtime dependencies.
    """
    
    # Record identity
    record_id: str = ""
    """Unique identifier for this persistence record."""
    
    # State reference
    state_id: str = ""
    """ID of the state that was persisted."""
    
    revision: int = 0
    """Revision of the state at persistence time."""
    
    # Persistence details
    timestamp_utc: float = 0.0
    """When persistence occurred (semantic reference)."""
    
    authority_id: str = ""
    """Authority that performed persistence."""
    
    storage_location: str = ""
    """Location/URI where state was persisted."""
    
    storage_hash: str = ""
    """Hash of persisted data for integrity verification."""
    
    # Metadata
    scope: PersistenceScope = field(default_factory=PersistenceScope)
    """Scope of what was persisted."""
    
    validity_class: str = "valid"
    """Classification of persistence validity."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "PersistenceEligibility",
    "PersistenceScope",
    "PersistenceAuthority",
    "PersistenceRecord",
)