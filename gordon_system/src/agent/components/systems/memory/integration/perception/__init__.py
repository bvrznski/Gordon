# Perception Integration - Phase 5.1.7

"""
Perception Integration: Communication between Memory and Perception subsystem.

The Perception integration handles:
    - Observation exchange (percepts, signals, features)
    - Contextual projection retrieval
    - Semantic context for observations

Perception Contract:
    INPUT:
        - Percepts (observations, events, signals)
        - Features (detected characteristics)
        
    OUTPUT:
        - Relevant projections from Memory
        - Contextual information
        - Prior observations

Guarantees:
    - No direct storage in Perception
    - Projection-only communication
    - Deterministic retrieval
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# PERCEPTION REQUEST TYPES
# =============================================================================


class PerceptionRequestType:
    """Request types specific to perception integration."""
    
    OBSERVATION = "observation"
    FEATURE_QUERY = "feature_query"
    CONTEXT_PROJECTION = "context_projection"
    HISTORY_REQUEST = "history_request"


# =============================================================================
# PERCEPTION PROTOCOL
# =============================================================================


@dataclass(frozen=True)
class PerceptionProtocol:
    """
    Protocol for perception-memory communication.
    
    Provides methods for:
        - Submitting observations to Memory
        - Querying contextual projections
        - Requesting history for current context
    
    Usage:
        protocol = PerceptionProtocol()
        
        # Get projection for a feature set
        response = protocol.get_contextual_projection(feature_set)
    """
    
    consumer_id: str = "perception"
    
    def submit_observation(self, 
                           observation: Dict[str, Any],
                           context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Submit an observation to Memory.
        
        Args:
            observation: The observed data
            context: Additional context for the observation
            
        Returns:
            (success, message)
        """
        return (True, f"Observation submitted with source: {self.consumer_id}")
    
    def get_contextual_projection(self,
                                   feature_set: Tuple[str, ...],
                                   time_window_seconds: float = 60.0) -> Dict[str, Any]:
        """
        Get contextual projection based on current features.
        
        Args:
            feature_set: Current feature identifiers
            time_window: How far back to look (seconds)
            
        Returns:
            Contextual projection from Memory
        """
        return {
            "requester": self.consumer_id,
            "projections": [],  # Would be populated by actual Memory response
            "confidence": 1.0,
            "contextual_info": []
        }
    
    def get_history_for_context(self,
                                 context: Dict[str, Any],
                                 limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical observations matching current context.
        
        Args:
            context: Current context data
            limit: Maximum number of history items
            
        Returns:
            List of relevant historical observations
        """
        return []  # Would be populated by actual Memory response


# =============================================================================
# PERCEPTION INTEGRATION CONTRACT
# =============================================================================


def create_perception_contract(consumer_id: str = "perception") -> Dict[str, Any]:
    """
    Create a perception integration contract.
    
    Args:
        consumer_id: The ID of the consumer (perception subsystem)
        
    Returns:
        Contract definition with supported operations
    """
    return {
        "consumer": consumer_id,
        "integration_type": "perception",
        "supported_requests": [
            PerceptionRequestType.OBSERVATION,
            PerceptionRequestType.FEATURE_QUERY,
            PerceptionRequestType.CONTEXT_PROJECTION,
            PerceptionRequestType.HISTORY_REQUEST
        ],
        "supported_responses": ["context", "summary"],
        "guarantees": {
            "semantic_integrity": True,
            "determinism": True,
            "projection_only": True,
            "no_direct_storage": True
        }
    }