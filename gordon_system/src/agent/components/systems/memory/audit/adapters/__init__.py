# Memory Audit Adapters - Phase 5.1.9
# ======================================

"""
Adapter implementations for memory access.

These adapters provide read-only access to various memory storage systems
for auditing purposes.
"""

from __future__ import annotations


# =============================================================================
# BASE ADAPTER - Abstract base class for all adapters
# =============================================================================


class BaseAuditAdapter:
    """
    Abstract base class for audit adapters.
    
    Adapters must be read-only and never modify memory.
    All retrieval operations must be deterministic.
    
    Anti-Patterns Rejected:
        - Mutating memory through adapters
        - Non-deterministic retrieval
        - Hidden side effects during retrieval
    """
    
    name: str = "base_adapter"
    
    def __init__(self):
        """Initialize the adapter."""
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if adapter has been initialized."""
        return self._initialized
    
    def initialize(self):
        """Initialize adapter connection to memory system."""
        self._initialized = True
    
    def shutdown(self):
        """Shutdown adapter connection."""
        self._initialized = False
    
    def get_health(self) -> bool:
        """
        Check if adapter can access memory.
        
        Returns:
            True if memory is accessible, False otherwise
        """
        return self._initialized


# =============================================================================
# IN-MEMORY ADAPTER - For testing and in-memory audits
# =============================================================================


class InMemoryAuditAdapter(BaseAuditAdapter):
    """
    In-memory adapter for testing audit components.
    
    This adapter stores artifacts in a dictionary and provides
    read-only access to them. It's primarily useful for testing.
    """
    
    name: str = "in_memory"
    
    def __init__(self, artifacts=None):
        """
        Initialize the in-memory adapter.
        
        Args:
            artifacts: Optional initial artifacts (dict of id -> artifact)
        """
        super().__init__()
        self._artifacts: dict = artifacts or {}
    
    @property
    def artifact_count(self) -> int:
        """Get count of stored artifacts."""
        return len(self._artifacts)
    
    def get_memory_artifacts(
        self,
        limit: int = 1000,
        offset: int = 0,
    ):
        """
        Retrieve memory artifacts from storage.
        
        Args:
            limit: Maximum number of artifacts to return
            offset: Number of artifacts to skip
            
        Returns:
            List of memory artifacts
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")
        
        artifact_list = list(self._artifacts.values())
        return artifact_list[offset : offset + limit]
    
    def get_memory_artifact_by_id(self, artifact_id: str):
        """
        Retrieve a specific artifact by ID.
        
        Args:
            artifact_id: Unique identifier of the artifact
            
        Returns:
            The requested artifact
            
        Raises:
            MemoryAuditNotFoundError: If artifact doesn't exist
        """
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")
        
        if artifact_id not in self._artifacts:
            from ..exceptions import MemoryAuditNotFoundError
            raise MemoryAuditNotFoundError("artifact_id", artifact_id)
        
        return self._artifacts[artifact_id]
    
    def get_references_for_artifact(
        self,
        artifact_id: str,
        reference_type=None,
    ):
        """
        Retrieve references for an artifact.
        
        This is a placeholder that returns empty for in-memory adapter.
        Real adapters would extract this from artifacts.
        
        Args:
            artifact_id: ID of the artifact
            reference_type: Filter by type (optional)
            
        Returns:
            Empty tuple (in-memory adapter doesn't track references)
        """
        return ()
    
    def add_artifact(self, artifact):
        """Add an artifact to storage (test helper)."""
        if hasattr(artifact, 'identity') and hasattr(artifact.identity, 'artifact_id'):
            self._artifacts[artifact.identity.artifact_id] = artifact
        else:
            self._artifacts[str(id(artifact))] = artifact
    
    def clear(self):
        """Clear all stored artifacts (test helper)."""
        self._artifacts.clear()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BaseAuditAdapter",
    "InMemoryAuditAdapter",
]