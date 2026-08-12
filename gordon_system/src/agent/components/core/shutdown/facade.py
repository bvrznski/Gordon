# Core Shutdown Facade Protocol
# ==============================
"""
Production-grade shutdown infrastructure for Phase 3.7.9-I.

This module provides a protocol interface for the Coordinator to invoke
Core shutdown without implementing shutdown logic itself.
"""

from typing import Protocol, Dict, Any, Optional


class CoreShutdownFacade(Protocol):
    """
    Protocol defining the Core shutdown interface that must be implemented by Core.
    
    Architecture Boundary:
        The Agent Shutdown Coordinator delegates to this facade but does NOT implement it.
        This ensures clean ownership separation between entrypoint coordination and
        core runtime shutdown.
    
    Core MUST implement these methods:
        - graceful_shutdown(request) -> Dict[str, Any]
        - forced_shutdown(request) -> Dict[str, Any]
        - verify_terminal_state(request) -> bool
    
    Coordinator USES this facade to invoke shutdown but never implements it.
    """
    
    def graceful_shutdown(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a graceful shutdown through Core.
        
        Args:
            request: Shutdown request dictionary with runtime_id, timeout_seconds, etc.
            
        Returns:
            Result dictionary containing:
                - runtime_id: The runtime that was shut down
                - terminated: True if shutdown completed
                - success: True if successful
                - duration_seconds: How long shutdown took
                - terminal_state_evidence: Evidence of terminal state
        """
        ...
    
    def forced_shutdown(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a forced shutdown through Core (bypass graceful waiting).
        
        Args:
            request: Shutdown request dictionary
            
        Returns:
            Result dictionary with same structure as graceful_shutdown
        """
        ...
    
    def verify_terminal_state(self, request: Dict[str, Any]) -> bool:
        """
        Verify that the runtime has reached a terminal state.
        
        Args:
            request: Request containing runtime_id to verify
            
        Returns:
            True if runtime is in terminal state (TERMINATED or FAILED)
        """
        ...