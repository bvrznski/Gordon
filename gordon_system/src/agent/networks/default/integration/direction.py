# Port Direction Enumeration (Phase 4.3.13)
# ===========================================

"""
Port direction enumeration for integration contracts.

All ports must have exactly one direction.
"""

from __future__ import annotations

from enum import Enum


class PortDirection(Enum):
    """Direction of an integration port."""
    
    INBOUND = "INBOUND"
    """
    Inbound ports receive data from external systems into the Default Network.
    Examples: execution invocation, projection supply, result delivery.
    """
    
    OUTBOUND = "OUTBOUND"
    """
    Outbound ports send requests or proposals from the Default Network to external systems.
    Examples: capability request, proposal submission.
    """
    
    BIDIRECTIONAL = "BIDIRECTIONAL"
    """
    Bidirectional ports support both inbound and outbound operations.
    Must still define independent request and result contracts.
    """


# =============================================================================
# CONSTANTS (Phase 4.3.13)
# =============================================================================

INBOUND = PortDirection.INBOUND
"""Alias for INBOUND direction."""

OUTBOUND = PortDirection.OUTBOUND
"""Alias for OUTBOUND direction."""

BIDIRECTIONAL = PortDirection.BIDIRECTIONAL
"""Alias for BIDIRECTIONAL direction."""