# Internal Access Engine - Phase 5.1.3 Canonical Internal Memory Access

"""
Internal Access Engine: Provides internal architecture with safe memory access.

This engine:
    - Processes requests through the canonical pipeline
    - Applies authorization, visibility, and publication filters
    - Returns projections only (never exposes substrate directly)

Internal consumers include:
    - Reasoning
    - Planning
    - Knowledge
    - Learning
    - Identity
    - Coordination
    - Governance

The engine is stateless and deterministic.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

# Local imports (using module paths relative to access package root)
from gordon_system.src.agent.components.systems.memory.access.session import (
    MemoryAccessSession,
    AccessPermission,
)
from gordon_system.src.agent.components.systems.memory.access.request import (
    MemoryAccessRequest,
    ProjectionType,
)
from gordon_system.src.agent.components.systems.memory.access.response import (
    MemoryAccessResponse,
    AuthorizationOutcome,
)
from gordon_system.src.agent.components.systems.memory.access.authorization import (
    AuthorizationPolicy,
    PolicyRule,
    PolicyAction,
    MemoryAuthorizer,
    AuthorizationDecision,
)
from gordon_system.src.agent.components.systems.memory.access.visibility import (
    VisibilityFilter,
    VisibilityPolicy,
    MemoryVisibilityEngine,
)
from gordon_system.src.agent.components.systems.memory.access.publication import (
    PublicationFormat,
    PublicationResult,
    MemoryPublisher,
)


class InternalAccessEngine:
    """
    Access engine for internal Gordon architecture.
    
    Processes requests through the canonical pipeline:
        1. Parse request and session context
        2. Authorize (check permissions, apply policy)
        3. Evaluate visibility (apply filters)
        4. Generate projection (format results)
        5. Return response
        
    The engine never modifies Memory - it only exposes projections.
    """
    
    def __init__(
        self,
        authorizer: Optional[MemoryAuthorizer] = None,
        visibility_engine: Optional[MemoryVisibilityEngine] = None,
        publisher: Optional[MemoryPublisher] = None,
    ):
        """
        Initialize the internal access engine.
        
        Args:
            authorizer: Authorization engine (creates default if None)
            visibility_engine: Visibility engine (creates default if None)
            publisher: Publication engine (creates default if None)
        """
        self._authorizer = authorizer or MemoryAuthorizer()
        self._visibility = visibility_engine or MemoryVisibilityEngine()
        self._publisher = publisher or MemoryPublisher()
        
        # Register default internal policy
        self._register_default_policy()
    
    def _register_default_policy(self) -> None:
        """Register a default internal access policy."""
        policy = AuthorizationPolicy(
            policy_id="internal-default",
            name="Internal Default Policy",
            description="Default policy for internal architecture access",
            rules=(
                # Reasoning can read and query
                PolicyRule(
                    rule_id="reasoning-read-query",
                    subject_match={"requester_type": "reasoning"},
                    action=PolicyAction.READ,
                    effect="allow",
                    priority=100,
                ),
                PolicyRule(
                    rule_id="reasoning-project",
                    subject_match={"requester_type": "reasoning"},
                    action=PolicyAction.PROJECT,
                    effect="allow",
                    priority=100,
                ),
                # Planning can read, query, and project
                PolicyRule(
                    rule_id="planning-all",
                    subject_match={"requester_type": "planning"},
                    action=PolicyAction.READ,
                    effect="allow",
                    priority=100,
                ),
                PolicyRule(
                    rule_id="planning-project",
                    subject_match={"requester_type": "planning"},
                    action=PolicyAction.PROJECT,
                    effect="allow",
                    priority=100,
                ),
                # Knowledge can read
                PolicyRule(
                    rule_id="knowledge-read",
                    subject_match={"requester_type": "knowledge"},
                    action=PolicyAction.READ,
                    effect="allow",
                    priority=100,
                ),
            ),
        )
        
        self._authorizer.register_policy(policy)
    
    def process_request(
        self,
        session: MemoryAccessSession,
        request: MemoryAccessRequest,
    ) -> Tuple[MemoryAccessResponse, Optional[PublicationResult]]:
        """
        Process a memory access request.
        
        Args:
            session: Access session making the request
            request: Request to process
            
        Returns:
            (response, publication) tuple where:
                - response contains authorization result and projection
                - publication is the formatted output (if allowed)
                
        The processing follows the canonical pipeline:
            Request -> Authorization -> Visibility -> Projection -> Response
        """
        # Record the request in session statistics
        session = session.record_request()
        
        # Step 1: Evaluate authorization
        auth_decision = self._authorizer.evaluate(session, request)
        
        if not auth_decision.is_allowed:
            # Build denial response
            return (
                MemoryAccessResponse(
                    response_id=str(request.request_id),
                    outcome=AuthorizationOutcome.DENY,
                    authorization_notes=auth_decision.notes or "Authorization denied",
                ),
                None,
            )
        
        # Step 2: Get artifacts (simulated - in real implementation, this would
        # query the memory substrate through MemoryRetrieval)
        # For now, return empty projection
        artifacts = self._get_artifacts_for_request(request)
        
        # Step 3: Apply visibility filtering
        filtered_artifacts, _ = self._visibility.evaluate_projection(
            artifacts=artifacts,
            policy_id=None,  # Use default visibility
        )
        
        # Step 4: Determine projection type from request
        format_ = self._projection_type_to_format(request.projection_type)
        
        # Step 5: Build response with allowed outcome
        response = MemoryAccessResponse(
            response_id=str(request.request_id),
            outcome=AuthorizationOutcome.ALLOW,
            projection=filtered_artifacts,
            total_count=len(artifacts),
            filtered_count=len(artifacts) - len(filtered_artifacts),
            confidence=self._calculate_confidence(auth_decision, request),
            limitations=auth_decision.matched_rules + (f"limit:{request.limit}",),
        )
        
        # Step 6: Generate publication if allowed
        publication = None
        if auth_decision.is_allowed and filtered_artifacts:
            publication = self._publisher.publish_projection(
                artifacts=filtered_artifacts,
                format=format_,
                summary=self._build_summary(filtered_artifacts),
                limitations=request.filter_conditions.keys(),
                generated_by="internal-access-engine",
            )
        
        return response, publication
    
    def _get_artifacts_for_request(self, request: MemoryAccessRequest) -> Tuple[Any, ...]:
        """
        Get artifacts matching the request.
        
        In a real implementation, this would query the memory substrate
        through MemoryRetrieval. For now, returns empty tuple as placeholder.
        """
        # TODO: Integrate with actual Memory Retrieval system
        return ()
    
    def _projection_type_to_format(
        self,
        projection_type: ProjectionType,
    ) -> PublicationFormat:
        """Convert projection type to publication format."""
        mapping = {
            ProjectionType.FULL: PublicationFormat.FULL,
            ProjectionType.SUMMARY: PublicationFormat.SUMMARY,
            ProjectionType.IDENTIFIERS: PublicationFormat.IDENTIFIERS,
            ProjectionType.METADATA: PublicationFormat.METADATA,
            ProjectionType.RELATIONSHIP: PublicationFormat.RELATIONSHIP,
        }
        return mapping.get(projection_type, PublicationFormat.FULL)
    
    def _calculate_confidence(
        self,
        auth_decision: AuthorizationDecision,
        request: MemoryAccessRequest,
    ) -> float:
        """Calculate confidence level for the response."""
        # Base confidence
        confidence = 1.0
        
        # Reduce if there were limitations
        if auth_decision.is_limited:
            confidence *= 0.9
        
        # Reduce if results were filtered by visibility
        if request.filter_conditions:
            confidence *= 0.95
        
        return max(0.0, min(1.0, confidence))
    
    def _build_summary(self, artifacts: Tuple[Any, ...]) -> Optional[Dict[str, Any]]:
        """Build summary statistics for the projection."""
        if not artifacts:
            return None
        
        kind_counts: Dict[str, int] = {}
        
        for artifact in artifacts:
            kind = getattr(artifact, "artifact_kind", None)
            if kind is not None:
                kind_str = str(kind) if isinstance(kind, (str, Enum)) else type(kind).__name__
                kind_counts[kind_str] = kind_counts.get(kind_str, 0) + 1
        
        return {
            "artifact_count": len(artifacts),
            "by_kind": kind_counts,
        }
    
    @property
    def authorizer(self) -> MemoryAuthorizer:
        """Get the authorization engine."""
        return self._authorizer
    
    @property
    def visibility_engine(self) -> MemoryVisibilityEngine:
        """Get the visibility engine."""
        return self._visibility
    
    @property
    def publisher(self) -> MemoryPublisher:
        """Get the publication engine."""
        return self._publisher