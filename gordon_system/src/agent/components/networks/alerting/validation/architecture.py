# Alerting Network Architecture Validation
# =========================================

"""
Architectural invariants for AlertingNetwork.

These invariants enforce the core architectural principles:
- No fabrication of assessments
- Clear separation from FocusingNetwork, Executive, and other components
- Bounded state ownership
- Advisory-only output authority
"""

from __future__ import annotations


ALERTING_INVARIANTS = {
    # Core authority invariants
    "ALERT-INV-001": "AlertingNetwork produces advisory assessments only.",
    "ALERT-INV-002": "AlertingNetwork never authorizes interruption.",
    "ALERT-INV-003": "AlertingNetwork never schedules execution.",
    "ALERT-INV-004": "AlertingNetwork never maintains endogenous focus.",
    "ALERT-INV-005": "AlertingNetwork state is bounded computational state.",
    
    # Input/output invariants
    "ALERT-INV-006": "AlertingNetwork accepts immutable projected input.",
    "ALERT-INV-007": "AlertingNetwork returns immutable assessment output.",
    "ALERT-INV-008": "Unknown modality is never silently converted.",
    
    # Dependency invariants
    "ALERT-INV-009": "AlertingNetwork has no production dependency on legacy code.",
    "ALERT-INV-010": "AlertingNetwork has no direct dependency on concrete sibling Networks.",
    
    # Separation of concerns invariants
    "ALERT-INV-011": "Alerting and Focusing remain separate authorities.",
    "ALERT-INV-012": "Attention demand and behavioral authority remain separate.",
    
    # Package behavior invariants
    "ALERT-INV-013": "Package import performs no computation or runtime activation.",
    "ALERT-INV-014": "No state structure may grow without an explicit bound.",
    "ALERT-INV-015": "No fabricated assessment may represent unfinished computation as success.",
}


class AlertingArchitecturalValidator:
    """
    Validator for architectural invariants.
    
    This class checks that implementations adhere to the core architectural
    principles. It does NOT perform runtime behavior validation - only
    structural and contract-level validation.
    """

    @staticmethod
    def validate_network_name(name: str) -> bool:
        """Validate that the network uses the canonical AlertingNetwork name."""
        return name == "AlertingNetwork"
    
    @staticmethod
    def validate_role(role: str) -> bool:
        """
        Validate that the role is exogenous-attention coordination.
        
        The AlertingNetwork MUST be described as performing exogenous attention
        demand coordination. It must NOT describe itself as endogenous focus,
        execution authority, or arbitrary event routing.
        """
        return "exogenous" in role.lower() and "attention" in role.lower()