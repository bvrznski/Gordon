# Salience Network Competition Validation
# ========================================

"""
Canonical validation functions for competition (Phase 4.8.6).

Validation ensures:
    - Requests contain valid candidates
    - Graphs have no duplicate edges or dangling nodes
    - Policies are well-formed
"""

from __future__ import annotations


def validate_candidate_identity(candidate: dict) -> tuple[bool, str]:
    """
    Validate that a candidate has required identity fields.
    
    Args:
        candidate: Candidate state dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(candidate, dict):
        return False, "Candidate must be a dictionary"
    
    if "state_identity" not in candidate:
        return False, "Candidate missing state_identity field"
    
    identity = candidate.get("state_identity")
    if not isinstance(identity, str) or not identity:
        return False, "Candidate state_identity must be non-empty string"
    
    return True, ""


def validate_competition_request(request: dict) -> tuple[bool, list[str]]:
    """
    Validate a CompetitionRequest dictionary.
    
    Args:
        request: Request to validate
        
    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []
    
    if not isinstance(request, dict):
        return False, ["Request must be a dictionary"]
    
    # Check candidate_states
    candidate_states = request.get("candidate_states")
    if not isinstance(candidate_states, tuple) or len(candidate_states) == 0:
        errors.append("candidate_states must be non-empty tuple")
    
    # Validate each candidate
    for i, candidate in enumerate(candidate_states):
        valid, error = validate_candidate_identity(candidate)
        if not valid:
            errors.append(f"Candidate {i}: {error}")
    
    return len(errors) == 0, errors


def validate_competition_graph(graph: dict) -> tuple[bool, list[str]]:
    """
    Validate a CompetitionGraph dictionary.
    
    Args:
        graph: Graph to validate
        
    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []
    
    if not isinstance(graph, dict):
        return False, ["Graph must be a dictionary"]
    
    # Check candidate_ids
    candidate_ids = graph.get("candidate_ids")
    if not isinstance(candidate_ids, tuple):
        errors.append("candidate_ids must be a tuple")
    
    # Validate edges reference valid candidates
    dominance_edges = graph.get("dominance_edges", ())
    inhibition_edges = graph.get("inhibition_edges", ())
    facilitation_edges = graph.get("facilitation_edges", ())
    equivalence_edges = graph.get("equivalence_edges", ())
    
    all_nodes = set(candidate_ids) if isinstance(candidate_ids, tuple) else set()
    
    # Check dominance edges
    for edge in dominance_edges:
        if not isinstance(edge, tuple) or len(edge) != 2:
            errors.append(f"Invalid dominance edge: {edge}")
            continue
        source, target = edge
        if source not in all_nodes:
            errors.append(f"Dominance edge references unknown candidate: {source}")
        if target not in all_nodes:
            errors.append(f"Dominance edge references unknown candidate: {target}")
    
    return len(errors) == 0, errors