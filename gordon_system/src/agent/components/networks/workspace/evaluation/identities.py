# Workspace Evaluation Identities
# ===============================

"""
Canonical evaluation identities for immutable references.

ARCHITECTURAL PRINCIPLES:
    - Immutable types (str aliases)
    - No runtime dependencies
    - External identity providers only
    - Deterministic derivation from inputs
"""

from __future__ import annotations


# =============================================================================
# EVALUATION IDENTITY TYPES
# =============================================================================

WorkspaceEvaluationIdentity = str
"""
Unique identifier for an evaluation request instance.

Must be:
    - Deterministically derived or externally supplied
    - Replayable (same input produces same output)
    - Never generated internally (no UUIDs, timestamps)

Examples: Content hash with prefix, source system ID with context.
"""


WorkspaceEvaluationRevision = int
"""
Monotonically increasing revision number for evaluations.

Revision rules:
    - Revision 1 is initial creation
    - Each semantic change requires a new revision
    - Identity + Revision = unique artifact reference

No in-place mutation allowed. Create new revision instead.
"""


WorkspaceEvaluationReference = str
"""
Immutable reference to Workspace Evaluation.

Format: "identity@revision"
Examples:
    "evaluation_def123@1"
    "candidate_analysis_abc@3"

Used for linking without ownership.
"""