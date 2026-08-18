# Experimental Reasoning - Shared Components
# ============================================

"""
Shared canonical contracts for Experimental Reasoning.

This module implements:
- Descriptors and metadata
- Experiment sets
- Intervention analysis
- Measurement planning
- Control conditions
- Information gain estimation
- Refinement tracking
- Validation results
- Failure handling
- Governance evaluation
- Health metrics
- Diagnostics
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto

# Re-export common types from parent modules for convenience
from ...shared.descriptor import ReasoningDescriptor, ReasoningKind, ReasoningState

__all__ = [
    # Base shared components (defined here)
    "dataclass_replace",
]
