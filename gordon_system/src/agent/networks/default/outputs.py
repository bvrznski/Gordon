# Default Network Outputs
# =====================

"""
Semantic output proposals and assessments from the DefaultNetwork.

Outputs are proposals or assessments that other systems may consider.
They do NOT silently mutate other systems - they only propose.

PHASE 4.3.1: Output Proposals
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple
from datetime import datetime


# =============================================================================
# OUTPUT PROPOSAL (core output unit)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultOutput:
    """
    A single output from the DefaultNetwork.
    
    Represents a proposal or assessment that other systems may consider.
    Does NOT command execution - only proposes or assesses.
    """
    
    # Output identity
    output_id: str
    
    # Timestamp when output was created (not processed)
    timestamp_utc: datetime
    
    # Output type classification
    output_type: str  # e.g., "proposal", "assessment"
    
    # The actual proposal/assessment data (frozen, immutable content)
    content: dict  # Use dict for generic frozen content storage
    
    # Source information (for provenance)
    source_info: Optional[dict] = None


# =============================================================================
# PROPOSAL SET (canonical output format)
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultProposalSet:
    """
    A complete set of proposals from the DefaultNetwork.
    
    This is the canonical output format when multiple proposals are generated
    in a single assessment cycle.
    """
    
    # Assessment identity
    assessment_id: str
    
    # Timestamp
    timestamp_utc: datetime
    
    # All proposals (frozen tuple)
    proposals: Tuple[DefaultOutput, ...]
    
    # Overall network activation summary
    activation_summary: dict


# =============================================================================
# PROPOSAL TYPES (semantic categories)
# =============================================================================

class ProposalType:
    """
    Bounded proposal type classifications.
    
    Describes what kind of internally oriented processing is being proposed.
    """
    
    INTERNAL_ATTENTION = "internal_attention"
    ASSOCIATION = "association"
    MEMORY_REACTIVATION = "memory_reactivation"
    REFLECTION = "reflection"
    SIMULATION = "simulation"
    PROSPECTION = "prospection"
    NARRATIVE_INTEGRATION = "narrative_integration"
    UNRESOLVED_GOAL = "unresolved_goal"
    INCUBATION = "incubation"
    CONTEXT_REINTEGRATION = "context_reintegration"


# =============================================================================
# OUTPUT BOUNDS (for validation)
# =============================================================================

class OutputBounds:
    """
    Bounds for output values.
    
    Ensures no output can exceed acceptable semantic bounds.
    """
    
    # Maximum proposals per set (bounded)
    MAX_PROPOSAL_COUNT: int = 10
    
    # Confidence must be in [0.0, 1.0]
    MIN_CONFIDENCE: float = 0.0
    MAX_CONFIDENCE: float = 1.0
    
    # Priority estimates must be in [0.0, 1.0]
    MIN_PRIORITY_ESTIMATE: float = 0.0
    MAX_PRIORITY_ESTIMATE: float = 1.0


# =============================================================================
# OUTPUT VALIDATION HELPERS
# =============================================================================

def validate_proposal_content_type(content_type: str) -> bool:
    """
    Validate that a proposal content type is recognized.
    
    Args:
        content_type: The proposed content type
        
    Returns:
        True if valid, False otherwise
    """
    valid_types = {
        ProposalType.INTERNAL_ATTENTION,
        ProposalType.ASSOCIATION,
        ProposalType.MEMORY_REACTIVATION,
        ProposalType.REFLECTION,
        ProposalType.SIMULATION,
        ProposalType.PROSPECTION,
        ProposalType.NARRATIVE_INTEGRATION,
        ProposalType.UNRESOLVED_GOAL,
        ProposalType.INCUBATION,
        ProposalType.CONTEXT_REINTEGRATION,
    }
    return content_type in valid_types


def validate_proposal_count(count: int) -> bool:
    """
    Validate that proposal count is within bounds.
    
    Args:
        count: Number of proposals
        
    Returns:
        True if within bounds, False otherwise
    """
    return 0 <= count <= OutputBounds.MAX_PROPOSAL_COUNT