# Verification Subpackage - Testing Infrastructure
# ==========================================

"""
Verification subpackage for contracts, invariants, and requirements verification.

This module provides verification authorities:
- VerificationManager: Coordinates all verification activities
- ContractVerifier: Verifies implementations satisfy protocols
- InvariantVerifier: Verifies invariants are maintained
"""

from .manager import (
    VerificationManager,
)
from .contracts import (
    ContractVerifier,
    verify_contract,
    check_protocol_compliance,
)
from .invariants import (
    InvariantVerifier,
    verify_invariant,
    check_state_preservation,
)
from .requirements import (
    RequirementVerifier,
    trace_requirement,
    verify_requirements,
)

__all__ = [
    # Main verification manager
    "VerificationManager",
    
    # Contract verification
    "ContractVerifier",
    "verify_contract",
    "check_protocol_compliance",
    
    # Invariant verification  
    "InvariantVerifier",
    "verify_invariant",
    "check_state_preservation",
    
    # Requirements verification
    "RequirementVerifier",
    "trace_requirement",
    "verify_requirements",
]