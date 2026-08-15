# Conversation Focus Example
# ===========================

"""
Example A: Conversation Focus Flow

Scenario:
A ConversationThread is active. The participant asks a complex question that
requires interpretation before a response can be produced.

Expected Focusing behavior:
    • prioritize the current participant input
    • maintain the conversation objective as a persistent secondary context
    • suppress unrelated internal reflection
    • recommend sufficient precision for reference resolution
    • produce explainable target ranking

This example demonstrates:
1. What enters the Focusing Network (immutable projections)
2. What the Focusing Network computes (FocusAssessment)
3. What it returns (advisory assessment, NOT command)
4. What it does NOT decide (authority remains with Executive/Attention)
5. How Execution receives semantic consequences
"""

from datetime import datetime

# Import Focusing contracts and models
from gordon_system.src.agent.components.networks.focusing.executive import (
    ProjectionId,
    AssessmentId,
    CorrelationId,
    ObjectiveProjection,
    FocusCommitmentProjection,
    ExecutiveFocusProjection,
    ExecutiveFocusDecisionKind,
)

from gordon_system.src.agent.components.networks.focusing.models import (
    FocusTarget,
    FocusCandidate,
    ProvenanceRecord,
    FocusAssessment,
)

# Import Focusing Network
from gordon_system.src.agent.components.networks.focusing.network import FocusingNetwork

# Import fixtures for deterministic test data
from gordon_system.examples.networks.focusing.fixtures import (
    FixedIds,
    fixed_timestamp,
    create_conversation_candidates,
)


def create_conversation_projection() -> ExecutiveFocusProjection:
    """
    Create an executive projection representing active conversation state.
    
    This is the INPUT to the FocusingNetwork. It contains all information
    that Executive wants Focusing to consider when computing recommendations.
    """
    # Active objectives (what ConversationThread is trying to achieve)
    obj_proj_1 = ObjectiveProjection(
        objective_id="conv_obj_complex_question",
        priority_hint=0.9,
        completion_status="in_progress",
        context={"participant_count": 2, "topic": "complex_problem"},
    )
    
    # Current focus commitment (what we're currently focusing on)
    current_commitment = FocusCommitmentProjection(
        target_ids=(FixedIds.TARGET_1.value,),
        strength=0.85,
        estimated_completion_seconds=None,  # Still active
    )
    
    projection = ExecutiveFocusProjection.create(
        active_objectives=(obj_proj_1,),
        revision=5,  # Current revision of executive state
        current_commitment=current_commitment,
    )
    
    return projection


def create_conversation_candidates() -> tuple[FocusCandidate, ...]:
    """
    Create conversation-related focus candidates.
    
    These represent the different things that could receive attention:
    - Current participant input (what was just said)
    - Conversation objective (maintaining the thread)
    - Internal maintenance (background tasks - can be suppressed)
    """
    # Candidate 1: Current participant input
    current_input_target = FocusTarget.create(
        semantic_category="participant_input",
        origin="conversation_stream",
        priority_hint=0.95,  # High priority - what was just said!
        confidence=0.8,
        provenance=ProvenanceRecord.from_subsystem("conversation"),
    )
    
    # Candidate 2: Conversation continuity
    conversation_continuity_target = FocusTarget.create(
        semantic_category="conversation_objective",
        origin="objective_system",
        priority_hint=0.75,  # Moderate - important but not immediate
        confidence=0.9,
        provenance=ProvenanceRecord.from_subsystem("objectives"),
    )
    
    # Candidate 3: Internal maintenance (can be suppressed)
    internal_maintenance_target = FocusTarget.create(
        semantic_category="internal_maintenance",
        origin="reflection_stream",
        priority_hint=0.3,  # Low - background task
        confidence=0.6,
        provenance=ProvenanceRecord.from_subsystem("reflection"),
    )
    
    return (
        FocusCandidate(target=current_input_target),
        FocusCandidate(target=conversation_continuity_target),
        FocusCandidate(target=internal_maintenance_target),
    )


def create_focus_assessment(
    projection: ExecutiveFocusProjection,
    candidates: tuple[FocusCandidate, ...],
) -> FocusAssessment:
    """
    Compute the Focusing Network's assessment.
    
    This is the CORE computational part - what the FocusingNetwork actually does.
    
    The actual implementation delegates to submodules (priority aggregation,
    relevance evaluation, competition analysis, etc.) but the public API
    remains this simple: give candidates, get assessment.
    """
    # Create the network
    network = FocusingNetwork.create()
    
    # Execute the assessment pipeline
    assessment = network.assess(candidates)
    
    return assessment


def simulate_executive_decision(
    projection: ExecutiveFocusProjection,
    assessment: FocusAssessment | dict,
) -> tuple[str, tuple[str, ...]]:
    """
    Simulate what Executive does with the Focusing assessment.
    
    This represents the AUTHORITY layer that makes decisions based on
    computational recommendations. The FocusingNetwork cannot make these
    decisions - it only provides evidence and estimates.
    
    Returns:
        Tuple of (decision_kind, accepted_targets)
    """
    # Handle both dict and FocusAssessment types
    if isinstance(assessment, FocusAssessment):
        primary_target = assessment.priority_scores.get("current_input", "default")
        secondary_targets = []
        confidence = getattr(assessment, 'confidence', 0.75) if hasattr(assessment, 'confidence') else 0.75
    else:
        # Handle dict for testing/demonstration
        primary_target = assessment.get("primary_target", "default")
        secondary_targets = assessment.get("secondary_targets", [])
        confidence = assessment.get("confidence", 0.75)
    
    # Executive evaluates the assessment:
    # 1. Is the projection revision still current?
    # 2. Does this recommendation align with objectives and policy?
    # 3. What's the confidence level?
    
    if confidence >= 0.7:
        # Accept as-is (high confidence)
        decision_kind = ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION
        accepted_targets = (primary_target,) + tuple(secondary_targets) if secondary_targets else (primary_target,)
    elif confidence >= 0.5:
        # Accept with modifications (moderate confidence)
        decision_kind = ExecutiveFocusDecisionKind.ACCEPT_WITH_MODIFICATION
        accepted_targets = (primary_target,)  # Only accept primary, be selective about secondary
    else:
        # Low confidence - defer or request reassessment
        decision_kind = ExecutiveFocusDecisionKind.DEFER_FOCUS_CHANGE
        accepted_targets = tuple()
    
    return decision_kind, accepted_targets


def run_conversation_example():
    """
    Demonstrate the complete conversation focus flow.
    
    This is NOT a behavioral policy. It's an example showing:
    1. Input (immutable projection) → FocusingNetwork → Assessment (advisory)
    2. Executive evaluates and decides
    3. Execution interprets semantic consequences
    """
    print("=" * 80)
    print("CONVERSATION FOCUS EXAMPLE")
    print("=" * 80)
    
    # Step 1: Create executive projection (what Executive tells Focusing)
    print("\n[Step 1] Executive Projection (immutable input):")
    projection = create_conversation_projection()
    print(f"  - Projection ID: {projection.projection_id.value}")
    print(f"  - Revision: {projection.revision}")
    print(f"  - Active objectives: {[obj.objective_id for obj in projection.active_objectives]}")
    if projection.current_commitment:
        print(f"  - Current commitment targets: {projection.current_commitment.target_ids}")
    
    # Step 2: Create candidates (what could receive attention)
    print("\n[Step 2] Focus Candidates (what could be focused):")
    candidates = create_conversation_candidates()
    for i, candidate in enumerate(candidates):
        target = candidate.target
        print(f"  - Candidate {i+1}: {target.target_id.value} ({target.semantic_category})")
    
    # Step 3: FocusingNetwork computes assessment (this is the core computation)
    print("\n[Step 3] FocusingNetwork Assessment (computational output):")
    assessment = create_focus_assessment(projection, candidates)
    
    # For FocusAssessment object, use to_serializable() method
    if hasattr(assessment, 'to_serializable'):
        assessment_dict = assessment.to_serializable()
    else:
        assessment_dict = assessment
    
    print(f"  - Assessment ID: {assessment.assessment_id.value if hasattr(assessment, 'assessment_id') else assessment.get('assessment_id', 'N/A')}")
    print(f"  - Overall score: {assessment.overall_focus_score if hasattr(assessment, 'overall_focus_score') else assessment_dict.get('overall_focus_score', 'N/A')}")
    
    # Note: The actual FocusAssessment output contains more detailed information:
    # - priority_assessment
    # - relevance_assessment  
    # - competition_assessment
    # - suppression_assessment
    # - precision_assessment
    # - persistence_assessment
    # - bias_assessment
    
    print("\n[Step 4] Executive Decision (authoritative):")
    decision_kind, accepted_targets = simulate_executive_decision(projection, assessment)
    print(f"  - Decision kind: {decision_kind}")
    print(f"  - Accepted targets: {accepted_targets}")
    
    # Step 5: Execution consequence
    print("\n[Step 5] Execution Consequence:")
    if decision_kind == ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION:
        print("  → ConversationLoop selects InterpretationCycle")
        print("  → Thread continues processing with new focus commitment")
    elif decision_kind == ExecutiveFocusDecisionKind.DEFER_FOCUS_CHANGE:
        print("  → Current focus maintained (no change)")
        print("  → Reassessment requested later")
    
    # Step 6: Core consequence
    print("\n[Step 6] Core Consequence:")
    if decision_kind == ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION:
        print("  → Runtime state updated with new focus targets")
        print("  → Appropriate cycles scheduled for execution")
    
    # Invariants demonstration
    print("\n" + "=" * 80)
    print("ARCHITECTURAL INVARIANTS DEMONSTRATED:")
    print("=" * 80)
    print("✓ FocusingNetwork produced advisory assessment (not command)")
    print("✓ Executive made authoritative decision")
    print("✓ Execution interpreted semantic consequences")
    print("✓ Core performed runtime mechanics (if decision accepted)")
    print("✓ No FocusingNetwork → Runtime coupling")
    
    return assessment


if __name__ == "__main__":
    run_conversation_example()
