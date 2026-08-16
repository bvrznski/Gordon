# Salience Network Dynamic Validation Functions
# =============================================

"""
Canonical validation functions (Phase 4.8.7).

Validation ensures:
    - Requests are well-formed and complete
    - Candidates contain required fields
    - Policy references exist
"""

from __future__ import annotations

from typing import Tuple


def validate_request(request: dict) -> Tuple[bool, list[str]]:
    """
    Validate a DynamicUpdateRequest dictionary.
    
    Args:
        request: Request dictionary to validate
        
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    if not isinstance(request, dict):
        return False, ["Request must be a dictionary"]
    
    # Identity check
    identity = request.get("identity", "")
    if not isinstance(identity, str) or len(identity.strip()) == 0:
        errors.append("Request must have non-empty identity")
    
    # Candidate states check
    candidate_states = request.get("candidate_states", [])
    if not isinstance(candidate_states, (list, tuple)):
        errors.append("candidate_states must be a list or tuple")
    elif len(candidate_states) == 0:
        errors.append("At least one candidate state is required")
    
    # Semantic delta check
    semantic_delta = request.get("semantic_delta", {})
    if not isinstance(semantic_delta, dict):
        errors.append("semantic_delta must be a dictionary")
    
    # Policy reference check (optional but recommended)
    dynamic_policy = request.get("dynamic_policy", "")
    if not isinstance(dynamic_policy, str):
        errors.append("dynamic_policy must be a string")
    
    return len(errors) == 0, errors


def validate_candidates(candidates: Tuple[dict, ...]) -> Tuple[bool, list[str]]:
    """
    Validate Candidate State dictionaries.
    
    Args:
        candidates: Tuple of candidate dictionaries
        
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    if not isinstance(candidates, tuple):
        return False, ["Candidates must be a tuple"]
    
    for i, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"Candidate {i} must be a dictionary")
            continue
        
        # Check required candidate fields
        state_identity = candidate.get("state_identity", "")
        if not isinstance(state_identity, str) or len(state_identity.strip()) == 0:
            errors.append(f"Candidate {i}: missing or empty state_identity")
        
        overall_level = candidate.get("overall_level", "")
        if not isinstance(overall_level, str):
            errors.append(f"Candidate {i}: overall_level must be a string")
    
    return len(errors) == 0, errors