# Workspace Integration - Phase 5.1.7

"""
Workspace Integration: Communication between Memory and Workspace subsystem.

The Workspace integration handles:
    - Active artifacts requests
    - Context and summary retrieval
    - Temporary projections for working memory

Workspace Contract:
    INPUT:
        - Current task context
        - Attention focus
        - Execution context
        
    OUTPUT:
        - Working projections from Memory
        - Relevant summaries
        - Context bundles

Guarantees:
    - Workspace never owns Memory
    - Projection-only communication
    - Working memory only (no long-term storage)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class WorkspaceProtocol:
    """
    Protocol for workspace-memory communication.
    
    Provides methods for:
        - Requesting active artifacts
        - Getting context summaries
        - Creating temporary projections
    
    Usage:
        protocol = WorkspaceProtocol()
        
        # Get working memory projection
        response = protocol.get_working_projection(task_context)
    """
    
    consumer_id: str = "workspace"
    
    def get_working_projection(self,
                                task_context: Dict[str, Any],
                                window_seconds: float = 30.0) -> Dict[str, Any]:
        """
        Get working memory projection for current task context.
        
        Args:
            task_context: Current task information
            window_seconds: Time window for relevant memories
            
        Returns:
            Working projection with active artifacts
        """
        return {
            "requester": self.consumer_id,
            "projections": [],
            "working_memory": [],
            "context_bundles": []
        }
    
    def get_context_summary(self, 
                            focus_items: Tuple[str, ...]) -> Dict[str, Any]:
        """
        Get summary of context for focused items.
        
        Args:
            focus_items: Items currently in attention focus
            
        Returns:
            Summary projection
        """
        return {
            "summary": {},
            "focus_context": {}
        }
    
    def create_temporary_projection(self,
                                     item_ids: Tuple[str, ...]) -> Dict[str, Any]:
        """
        Create a temporary (non-persistent) projection.
        
        Args:
            item_ids: Items to include in projection
            
        Returns:
            Temporary projection data
        """
        return {
            "projection_id": f"temp_{self.consumer_id}_{id(item_ids)}",
            "items": list(item_ids),
            "is_persistent": False,
            "ttl_seconds": 300  # 5 minutes
        }


def create_workspace_contract(consumer_id: str = "workspace") -> Dict[str, Any]:
    """Create a workspace integration contract."""
    return {
        "consumer": consumer_id,
        "integration_type": "workspace",
        "supported_requests": [
            "working_projection",
            "context_summary",
            "temporary_projection"
        ],
        "supported_responses": ["projection", "summary"],
        "guarantees": {
            "semantic_integrity": True,
            "determinism": True,
            "non_persistent_only": True
        }
    }