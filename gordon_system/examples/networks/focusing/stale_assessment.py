# Stale Assessment Rejection Example
# ====================================

"""
Example Z: Stale Focus Assessment

Scenario:
The Focusing Network evaluates projection revision 10.

The Executive objective state advances to revision 11 before the assessment is used.

Expected sequence:

    old projection (revision 10)
        ↓ FocusingNetwork computes assessment
    assessment references revision 10
        
    new executive projection (revision 11)
        ↓ assessment application attempted
    rejection as stale
        ↓
    assessment retained as historical evidence
        ↓
    new assessment requested

This example demonstrates:
- Stale assessment detection and rejection
- Revision tracking between projections and assessments
- Historical preservation without affecting current state
"""

from gordon_system.src.agent.components.networks.focusing.executive import (
    ProjectionId,
    AssessmentId,
    ObjectiveProjection,
    FocusCommitmentProjection,
    ExecutiveFocusProjection,
    FocusAssessmentApplicationResult,
)


def create_projection_at_revision(revision: int) -> ExecutiveFocusProjection:
    """Create an executive projection at a specific revision."""
    obj_proj = ObjectiveProjection(
        objective_id="stale_test_obj",
        priority_hint=0.8,
    )
    
    commitment = FocusCommitmentProjection(target_ids=("target_1",), strength=0.7)
    
    return ExecutiveFocusProjection.create(
        active_objectives=(obj_proj,),
        revision=revision,
        current_commitment=commitment,
    )


def compute_assessment_for_projection(projection: ExecutiveFocusProjection) -> dict:
    """
    Simulate computing a focus assessment for the given projection.
    
    In reality, this would involve FocusingNetwork.assess() with candidates
    and produce a FocusAssessment object.
    """
    return {
        "assessment_id": f"assess_{projection.projection_id.value[-8:]}",
        "revision_referenced": projection.revision,
        "timestamp_utc": projection.timestamp_utc.isoformat(),
        "recommended_targets": ("target_1",),
        "confidence": 0.85,
    }


def check_assessment_staleness(
    assessment: dict,
    current_projection: ExecutiveFocusProjection,
) -> FocusAssessmentApplicationResult:
    """
    Check if the assessment is stale relative to current projection state.
    
    This is what Executive does when applying a Focusing Network assessment:
    1. Extract the revision from the assessment
    2. Compare with current projection revision
    3. Return appropriate result (valid or stale)
    """
    # Extract the revision that was referenced in the assessment
    assessment_revision = assessment.get("revision_referenced", 0)
    
    if assessment_revision != current_projection.revision:
        # Assessment is stale - projection has advanced since assessment was computed
        return FocusAssessmentApplicationResult.stale(
            expected_revision=current_projection.revision,
            actual_revision=assessment_revision,
            reason=(
                f"Projection state advanced during assessment. "
                f"Expected revision {current_projection.revision}, "
                f"but assessment used revision {assessment_revision}."
            ),
        )
    
    # Assessment is fresh - can be applied
    new_commitment = FocusCommitmentProjection(
        target_ids=assessment.get("recommended_targets", ()),
        strength=current_projection.current_commitment.strength if current_projection.current_commitment else 0.5,
    )
    
    return FocusAssessmentApplicationResult.valid_and_applied(new_commitment)


def main():
    """
    Demonstrate the stale assessment rejection flow.
    """
    print("=" * 80)
    print("STALE ASSESSMENT REJECTION EXAMPLE")
    print("=" * 80)
    
    # Step 1: Create initial projection at revision 10
    print("\n[Step 1] Initial Executive Projection (revision 10):")
    projection_v10 = create_projection_at_revision(10)
    print(f"  - Projection ID: {projection_v10.projection_id.value}")
    print(f"  - Revision: {projection_v10.revision}")
    
    # Step 2: Focusing Network computes assessment for this projection
    print("\n[Step 2] FocusingNetwork Assessment:")
    assessment = compute_assessment_for_projection(projection_v10)
    print(f"  - Assessment references revision: {assessment['revision_referenced']}")
    print(f"  - Recommended targets: {assessment['recommended_targets']}")
    
    # Step 3: Meanwhile, Executive state advances to revision 11
    print("\n[Step 3] Executive State Advances:")
    projection_v11 = create_projection_at_revision(11)
    print(f"  - New projection revision: {projection_v11.revision}")
    print("  (This represents new objectives, changed commitment, etc.)")
    
    # Step 4: Attempt to apply stale assessment
    print("\n[Step 4] Apply Assessment to Current State:")
    result = check_assessment_staleness(assessment, projection_v11)
    
    print(f"  - Is Valid: {result.is_valid}")
    print(f"  - Is Stale: {result.is_stale}")
    print(f"  - Action Taken: {result.action_taken}")
    
    if result.validation_errors:
        print("\n[Step 5] Validation Errors:")
        for error in result.validation_errors:
            print(f"  - {error}")
    
    # Step 6: Show outcome
    print("\n[Step 6] Outcome:")
    if result.is_stale:
        print("  → Assessment REJECTED as stale")
        print("  → Assessment retained as HISTORICAL EVIDENCE (not applied)")
        print("  → NEW assessment REQUESTED with current projection revision")
    else:
        print("  → Assessment ACCEPTED and APPLIED")
    
    # Invariants demonstrated
    print("\n" + "=" * 80)
    print("ARCHITECTURAL INVARIANTS DEMONSTRATED:")
    print("=" * 80)
    print("✓ Focusing assessment is tied to specific projection revision")
    print("✓ Executive validates revision before applying assessment")
    print("✓ Stale assessments do not affect current state")
    print("✓ Assessment history preserved without affecting Execution")
    
    return result


if __name__ == "__main__":
    main()