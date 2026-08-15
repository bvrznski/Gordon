# Engine Package - Gordon Executive Network Audit Subsystem
# ===========================================================

"""
Audit engine and session management module.

This package provides the core audit engine that orchestrates evidence
collection, analysis, finding generation, and report creation.
"""

from gordon_system.src.agent.networks.executive.audit.engine.audit_engine import (
    DefaultExecutiveAuditEngine,
)

__all__ = ["DefaultExecutiveAuditEngine"]
