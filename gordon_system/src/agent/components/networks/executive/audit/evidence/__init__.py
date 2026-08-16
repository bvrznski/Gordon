# Evidence Package - Gordon Executive Network Audit Subsystem
# ============================================================

"""
Evidence collection and validation module.

This package handles gathering raw data from executive components,
extracting relevant observations, and validating evidence before analysis.
"""

from gordon_system.src.agent.networks.executive.audit.evidence.collector import (
    EvidenceCollector,
    EvidenceCollectionAdapter,
)

__all__ = [
    "EvidenceCollector",
    "EvidenceCollectionAdapter",
]