# Default Network - Workspace Integration

Workspace Integration layer for the Gordon cognitive architecture.

## Overview

The Workspace Integration layer implements runtime-neutral coordination of workspace candidates - semantic proposals that may deserve evaluation for admission to a shared cognitive workspace.

## Key Architectural Principles

1. **Distinct from Workspace Ownership**: The Default Network prepares and proposes candidates but does not own or mutate the shared workspace state.
2. **Immutable Contracts**: All data structures are deeply immutable with no runtime dependencies.
3. **Bounded Scope**: Every integration is bounded by explicit limits on resources, evidence, and candidates.
4. **Semantic Content Only**: No live objects or runtime handles in domain models.

## Architectural Invariants

- DEFAULT-WS-INV-001: The Default Network does not own the shared workspace
- DEFAULT-WS-INV-002: Every Workspace Integration belongs to exactly one InternalEpisode
- DEFAULT-WS-INV-003: Every Workspace Integration has explicit purpose, subject, scope
- DEFAULT-WS-INV-004: Every Workspace Integration binds to one InternalContext revision
- DEFAULT-WS-INV-005: Every candidate preserves source ownership, factuality, provenance
- DEFAULT-WS-INV-006: A workspace candidate is distinct from admitted workspace content
- DEFAULT-WS-INV-007: Admission is distinct from broadcast
- DEFAULT-WS-INV-008: Broadcast is distinct from consumption

## Architecture Boundaries

Workspace Integration does NOT:
- Own or mutate shared workspace state
- Perform direct broadcast
- Invoke Executive, Alerting, or Focusing
- Schedule execution or allocate resources
- Own runtime progression (ExecutionLoop does that)

## Key Models

### Core Models
- `WorkspaceIntegrationRequest`: Request for a bounded integration episode
- `WorkspaceIntegrationPurpose`: Purpose of the integration
- `WorkspaceIntegrationSubject`: What is being integrated
- `WorkspaceIntegrationScope`: Bounded constraints on the integration
- `WorkspaceSourceProductReference`: Reference to source products used

### Candidate Models
- `WorkspaceCandidate`: Immutable workspace candidate proposal
- `WorkspaceCandidateContent`: Semantic content of the candidate
- `WorkspaceCandidateOrigin`: Origin information for traceability
- `WorkspaceAudienceRecommendation`: Advisory audience recommendation

### Assessment Models
- `WorkspaceCandidateValue`: Value assessment (advisory)
- `WorkspaceCandidateRelevance`: Relevance assessment
- `WorkspaceCandidateUrgency`: Urgency assessment
- `WorkspaceCandidateImportance`: Importance assessment
- `WorkspaceCandidateNovelty`: Novelty assessment
- `WorkspaceCandidateConfidence`: Confidence assessment
- `WorkspaceCandidateRisk`: Risk assessment

### Proposals
- `WorkspaceSubmissionProposal`: Proposal to submit a candidate for admission
- `WorkspaceCandidateRevisionProposal`: Proposal to revise an existing candidate
- `WorkspaceCandidateWithdrawalProposal`: Proposal to withdraw a candidate

### Admission Contracts
- `WorkspaceAdmissionDecision`: Decision from external authority (accept/reject/defer)
- `WorkspaceAdmissionAcceptance`: Acceptance record
- `WorkspaceAdmissionRejection`: Rejection record with reason
- `WorkspaceAdmissionDeferral`: Deferral record

## Usage Pattern

```
Internal Product → Workspace Integration Request
                 → Prepare Candidate
                 → Assess Value/Relevance/Urgency/Importance/Novelty/Confidence/Risk
                 → Determine Audience/Access/Disclosure/Lifetime
                 → Detect Duplicates/Conflicts
                 → Prepare Submission Proposal
                 → External Admission Decision
                 → Process Feedback (accept/reject/defer/revision)
```

## Implementation Status

### Completed Models
- Core models: request, purpose, subject, scope
- Source product references
- Candidate models: content, origin, audience recommendations
- Assessment models: value, relevance, urgency, importance, novelty, confidence, risk
- Conflict and duplicate models
- Submission proposals: candidate submission, revision, withdrawal
- Admission contracts: decision, acceptance, rejection, deferral

### Pending Components
The following components should be implemented according to the phase specification:

1. **Episode Specialization** (`episode.py`)
   - `WorkspaceIntegrationEpisode` reusing InternalEpisode

2. **Plan Templates** (`plan.py`)
   - `WorkspaceIntegrationPlan`
   - Coordination step kinds and steps

3. **Products and Outcomes**
   - `WorkspaceIntegrationProduct`
   - `WorkspaceIntegrationOutcome`
   - `WorkspaceIntegrationContinuation`

4. **State and History**
   - `WorkspaceIntegrationState`
   - Snapshots, transitions, history

5. **Validation Module**
   - Request validation
   - Scope validation
   - Candidate validation
   - Admission validation
   - Architecture boundary verification

6. **Contracts Module**
   - `WorkspaceAdmissionContract`
   - `WorkspaceFeedbackContract`

7. **Feedback Contracts** (`feedback/` subpackage)
   - Broadcast result
   - Consumption feedback
   - Expiration feedback
   - Eviction feedback
   - Feedback projection

8. **Additional Assessment Models**
   - Competition projection
   - Capacity cost

9. **Configuration and Exceptions**
   - `WorkspaceIntegrationConfig`
   - Exception types

10. **Tests and Documentation**
    - Unit tests for each module
    - Integration tests
    - Architecture tests
    - Reference flows documentation

## Next Steps

To complete Phase 4.3.11, implement the remaining components following the established patterns:

1. Create episode specialization that reuses InternalEpisode machinery
2. Implement declarative plan templates with coordination step vocabulary
3. Add product and outcome models with continuation recommendations
4. Build state tracking with bounded history
5. Implement comprehensive validation for all contracts
6. Define admission and feedback contracts as protocols
7. Add configuration models with explicit bounds
8. Create exception hierarchy for error handling
9. Write tests covering all specified scenarios
10. Document the architecture and reference flows

## References

- Phase 4.3.11 Specification (this directory)
- InternalEpisode contracts (gordon_system/src/agent/networks/default/internal_episode/)
- Reflection Coordination (gordon_system/src/agent/networks/default/reflection/)