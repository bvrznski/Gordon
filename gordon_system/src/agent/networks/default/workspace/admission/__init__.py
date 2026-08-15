# Workspace Admission Contracts Subpackage
# =========================================

"""
Admission decision contracts for workspace candidates.

ARCHITECTURAL PRINCIPLES:
    - All dataclasses are frozen (deeply immutable)
    - No runtime dependencies
    - Bounded by explicit limits
"""

from __future__ import annotations

# =============================================================================
# ADMISSION DECISION
# =============================================================================

from .decision import (
    WorkspaceAdmissionDecision,
    WorkspaceAdmissionDecisionKind,
)

# =============================================================================
# ACCEPTANCE
# =============================================================================

from .acceptance import (
    WorkspaceAdmissionAcceptance,
)

# =============================================================================
# REJECTION
# =============================================================================

from .rejection import (
    WorkspaceAdmissionRejection,
    RejectionReason,
)

# =============================================================================
# DEFERRAL
# =============================================================================

from .deferral import (
    WorkspaceAdmissionDeferral,
    DeferralReason,
)

# =============================================================================
# REASON
# =============================================================================

from .reason import (
    AdmissionReason,
)


__all__ = [
    # Decision
    "WorkspaceAdmissionDecision",
    "WorkspaceAdmissionDecisionKind",
    
    # Acceptance
    "WorkspaceAdmissionAcceptance",
    
    # Rejection
    "WorkspaceAdmissionRejection",
    "RejectionReason",
    
    # Deferral
    "WorkspaceAdmissionDeferral",
    "DeferralReason",
    
    # Reason
    "AdmissionReason",
]