# Identity Subject Model
# ======================

"""
Immutable identity subject model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdentitySubject:
    """
    Immutable representation of an identity integration subject.
    
    PROPERTIES:
        • subject_id: Unique identifier for this subject
        • kind: What kind of subject (IdentitySubjectKind.*)
        • reference: Reference to the identity element
        • scope: How broad or narrow is this subject
    """
    
    subject_id: str = ""
    """Unique identifier for this identity subject."""
    
    kind: str = "whole_agent"
    """What kind of subject (IdentitySubjectKind.*)."""
    
    reference: str = ""
    """Reference to the identity element being integrated."""
    
    scope: str = "broad"
    """How broad or narrow is this subject (narrow, moderate, broad)."""