# Identity Integration Exceptions
# ===============================

"""
Exception types for identity integration coordination.
"""

from __future__ import annotations


class InvalidIdentityIntegrationRequest(Exception):
    """Raised when an identity integration request is invalid."""


class InvalidIdentityPurpose(Exception):
    """Raised when the identity purpose is not recognized or valid."""


class InvalidIdentitySubject(Exception):
    """Raised when the identity subject is not recognized or valid."""


class InvalidIdentityScope(Exception):
    """Raised when the identity scope exceeds bounds or is invalid."""


class IdentityContextMismatch(Exception):
    """Raised when context binding cannot be established."""


class MissingIdentityProjection(Exception):
    """Raised when an identity projection is required but not available."""


class IdentityProjectionRevisionConflict(Exception):
    """Raised when identity projection revision conflicts with current state."""


class InvalidIdentitySource(Exception):
    """Raised when an identity source reference is invalid."""


class IdentityAuthorityViolation(Exception):
    """Raised when authority constraints are violated."""


class IdentityFactualityViolation(Exception):
    """Raised when factuality classification is inconsistent or invalid."""


class IdentityPrivacyViolation(Exception):
    """Raised when privacy restrictions would be violated."""


class InvalidIdentityPlan(Exception):
    """Raised when a coordination plan is invalid."""


class IdentityCapabilityUnavailable(Exception):
    """Raised when Identity Capability is not available."""


class IdentityCapabilityFailure(Exception):
    """Raised when Identity Capability operation fails."""


class InvalidIdentityAspect(Exception):
    """Raised when an identity aspect is invalid or inconsistent."""


class InvalidIdentityRole(Exception):
    """Raised when a role specification is invalid or inconsistent."""


class InvalidIdentityValueProjection(Exception):
    """Raised when a value projection is invalid or inconsistent."""


class InvalidIdentityCommitmentProjection(Exception):
    """Raised when a commitment projection is invalid or inconsistent."""


class UnsupportedIdentityClaim(Exception):
    """Raised when an identity claim is unsupported or cannot be evaluated."""


class IdentityContinuityFailure(Exception):
    """Raised when continuity assessment fails."""


class IdentityConsistencyFailure(Exception):
    """Raised when consistency assessment reveals irreconcilable issues."""


class IdentityCoherenceFailure(Exception):
    """Raised when coherence assessment fails."""


class IdentityRevisionConflict(Exception):
    """Raised when revision conflicts with existing identity state."""


class IdentityRecursionLimitExceeded(Exception):
    """Raised when recursive self-analysis depth is exceeded."""


class IdentityOutcomeInvalid(Exception):
    """Raised when an outcome does not meet validation requirements."""


class IdentityCapacityExceeded(Exception):
    """Raised when bounded capacity limits are exceeded."""


class IdentityInvariantViolation(Exception):
    """Raised when architectural invariants are violated."""