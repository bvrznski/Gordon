# Workspace Interface Module - Phase 5.2.5
# ==========================================

"""
Workspace Interface: Publishes bounded perceptual candidates to the Workspace Network.

Package:
    perception/interfaces/workspace/

The Workspace Interface publishes bounded perceptual candidates to the
Workspace Network and receives explicit Workspace requests.

Does NOT perform:
    - Workspace capacity allocation
    - global broadcasting
    - cognitive competition
    - global salience calculation
    - content eviction
    - executive prioritization
"""

__all__ = [
    "PerceptionWorkspaceInterface",
]