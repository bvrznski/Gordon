# Focusing Network Examples
# ==========================

"""
Examples demonstrating how the FocusingNetwork participates in Gordon's behavior
without owning it.

These examples show:

1. What enters the Focusing Network (immutable projections)
2. What the Focusing Network computes (FocusAssessment advisory output)
3. What it does NOT decide (authority remains with Executive/Attention)
4. How Execution receives semantic consequences
5. How Core performs runtime mechanics

ARCHITECTURAL INTEGRITY REQUIREMENTS:
====================================

Every example MUST follow this chain:

    Source systems → immutable projections → FocusingNetwork → 
    FocusAssessment → Authority decision → Execution consequence → Core runtime
    
The Focusing Network produces recommendations, not commands.

FORBIDDEN PATTERN (must NOT appear in examples):
    If assessment.primary_target:
        scheduler.run(assessment.primary_target)  # ❌ This is forbidden

CORRECT PATTERN (examples must show):
    Executive receives assessment
    Executive evaluates against objectives and policy  
    Executive decides to accept, modify, defer, or reject
    Execution interprets the accepted decision
    Core performs runtime mechanics

EXAMPLES:
=========

- conversation_focus.py      : Focus during conversation
- task_focus.py              : Focus during task execution
- planning_focus.py          : Focus during planning
- monitoring_focus.py        : Focus for monitoring
- reflection_focus.py        : Focus during reflection
- alert_reorientation.py     : Alert-driven reorientation
- divided_focus.py           : Multiple targets
- focus_release.py           : Releasing current focus
- stale_assessment.py        : Stale assessment rejection
- resource_pressure.py       : Resource pressure adaptation

See also:
    - docs/architecture/networks/focusing/reference_flows.md
    - docs/architecture/networks/focusing/behavioral_examples.md
    - docs/architecture/networks/focusing/example_antipatterns.md
"""

__all__ = []