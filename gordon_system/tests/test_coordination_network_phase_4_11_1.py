# Gordon Cognitive Architecture - Phase 4.11.1
# ===========================================

"""
Coordination Network Test Suite
================================

Tests for the Coordination Network implementation.
All tests verify deterministic, immutable behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from agent.components.networks.coordinator import (
    CoordinatedNetworkKind,
    NetworkIdentity,
    CoordinationMembership,
    NetworkProjection,
    CoordinationRequestIdentity,
    CoordinationCycleIdentity,
    CoordinationStateIdentity,
)

# =============================================================================
# TEST: COORDINATED NETWORK KIND ENUM
# =============================================================================


class TestCoordinatedNetworkKind:
    """Tests for the CoordinatedNetworkKind enumeration."""
    
    def test_has_all_ten_networks(self) -> None:
        """Verify all ten canonical networks are present."""
        kinds = list(CoordinatedNetworkKind)
        assert len(kinds) == 10
    
    def test_all_kinds_method(self) -> None:
        """Test the all_kinds() class method."""
        kinds = CoordinatedNetworkKind.all_kinds()
        assert len(kinds) == 10
        assert isinstance(kinds, tuple)
    
    def test_from_string_valid(self) -> None:
        """Test from_string with valid network kind names."""
        assert CoordinatedNetworkKind.from_string("alerting") == CoordinatedNetworkKind.ALERTING
        assert CoordinatedNetworkKind.from_string("default") == CoordinatedNetworkKind.DEFAULT
        assert CoordinatedNetworkKind.from_string("executive") == CoordinatedNetworkKind.EXECUTIVE
    
    def test_from_string_invalid(self) -> None:
        """Test from_string with invalid network kind names."""
        with pytest.raises(ValueError):
            CoordinatedNetworkKind.from_string("unknown_network")


# =============================================================================
# TEST: NETWORK IDENTITY
# =============================================================================


class TestNetworkIdentity:
    """Tests for NetworkIdentity model."""
    
    def test_create_identity(self) -> None:
        """Test creating a basic identity."""
        identity = NetworkIdentity(
            network_kind="ALERTING",
            semantic_name="Alerting Network",
        )
        assert identity.network_kind == "ALERTING"
        assert identity.semantic_name == "Alerting Network"
    
    def test_identity_is_frozen(self) -> None:
        """Test that identity is immutable."""
        identity = NetworkIdentity(
            network_kind="DEFAULT",
            semantic_name="Default Network",
        )
        with pytest.raises((AttributeError, TypeError)):
            identity.network_kind = "EXECUTIVE"


# =============================================================================
# TEST: COORDINATION MEMBERSHIP
# =============================================================================


class TestCoordinationMembership:
    """Tests for CoordinationMembership model."""
    
    def test_core_membership(self) -> None:
        """Test creating core membership with all ten networks."""
        membership = CoordinationMembership.core_membership()
        
        assert membership.membership_identity == "core:1.0.0"
        assert len(membership.required_network_kinds) == 10
        
        # Verify all network kinds are present
        for kind in CoordinatedNetworkKind:
            assert kind.name in membership.required_network_kinds


# =============================================================================
# TEST: PROJECTION IDENTITY
# =============================================================================


class TestProjectionIdentity:
    """Tests for projection identity models."""
    
    def test_request_identity(self) -> None:
        """Test CoordinationRequestIdentity."""
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        assert "coord-request:cycle-001:0" in str(identity)
    
    def test_cycle_identity(self) -> None:
        """Test CoordinationCycleIdentity."""
        identity = CoordinationCycleIdentity.from_epoch("epoch-001")
        assert "coord-cycle:epoch-001:0" in str(identity)
    
    def test_state_identity_from_cycle(self) -> None:
        """Test CoordinationStateIdentity.from_cycle()."""
        cycle_id = CoordinationCycleIdentity(cycle_id="cycle-001", sequence_index=0)
        state_id = CoordinationStateIdentity.from_cycle(cycle_id)
        
        assert "state-cycle-001" in state_id.state_id
        assert str(cycle_id) == state_id.cycle_ref


# =============================================================================
# TEST: NETWORK PROJECTION
# =============================================================================


class TestNetworkProjection:
    """Tests for NetworkProjection base contract."""
    
    def test_create_base_projection(self) -> None:
        """Test creating a base projection."""
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="ALERTING",
            semantic_name="Alerting Network",
        )
        
        projection = NetworkProjection(
            identity=identity,
            network_identity=network_identity,
            projection_revision=1,
        )
        
        assert projection.identity.cycle_id == "cycle-001"
        assert projection.network_identity.network_kind == "ALERTING"
        assert projection.projection_revision == 1
    
    def test_projection_is_frozen(self) -> None:
        """Test that projection is immutable."""
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="DEFAULT",
            semantic_name="Default Network",
        )
        
        projection = NetworkProjection(
            identity=identity,
            network_identity=network_identity,
        )
        
        with pytest.raises((AttributeError, TypeError)):
            projection.status = "blocked"


# =============================================================================
# TEST: NETWORK-SPECIFIC PROJECTIONS
# =============================================================================


class TestNetworkSpecificProjections:
    """Tests for network-specific projections."""
    
    def test_alerting_projection(self) -> None:
        """Test AlertingNetworkProjection."""
        from agent.components.networks.coordinator import (
            AlertingNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="ALERTING",
            semantic_name="Alerting Network",
        )
        
        projection = AlertingNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            alert_level=5,
            interruption_status="active",
        )
        
        assert projection.alert_level == 5
        assert projection.interruption_status == "active"
    
    def test_default_projection(self) -> None:
        """Test DefaultNetworkProjection."""
        from agent.components.networks.coordinator import (
            DefaultNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="DEFAULT",
            semantic_name="Default Network",
        )
        
        projection = DefaultNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            mode_transition_status="stable",
        )
        
        assert projection.mode_transition_status == "stable"
    
    def test_executive_projection(self) -> None:
        """Test ExecutiveNetworkProjection."""
        from agent.components.networks.coordinator import (
            ExecutiveNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="EXECUTIVE",
            semantic_name="Executive Network",
        )
        
        projection = ExecutiveNetworkProjection(
            identity=identity,
            network_identity=network_identity,
        )
        
        assert len(projection.directive_references) == 0
    
    def test_focusing_projection(self) -> None:
        """Test FocusingNetworkProjection."""
        from agent.components.networks.coordinator import (
            FocusingNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="FOCUSING",
            semantic_name="Focusing Network",
        )
        
        projection = FocusingNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            focus_capacity=0.8,
        )
        
        assert projection.focus_capacity == 0.8
    
    def test_oriented_projection(self) -> None:
        """Test OrientedNetworkProjection."""
        from agent.components.networks.coordinator import (
            OrientedNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="ORIENTED",
            semantic_name="Oriented Network",
        )
        
        projection = OrientedNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            orientation_transition_status="stable",
        )
        
        assert projection.orientation_transition_status == "stable"
    
    def test_predictive_projection(self) -> None:
        """Test PredictiveNetworkProjection."""
        from agent.components.networks.coordinator import (
            PredictiveNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="PREDICTIVE",
            semantic_name="Predictive Network",
        )
        
        projection = PredictiveNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            predictive_completion_status="partial",
        )
        
        assert projection.predictive_completion_status == "partial"
    
    def test_reward_projection(self) -> None:
        """Test RewardNetworkProjection."""
        from agent.components.networks.coordinator import (
            RewardNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="REWARD",
            semantic_name="Reward Network",
        )
        
        projection = RewardNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            evaluation_status="pending",
        )
        
        assert projection.evaluation_status == "pending"
    
    def test_salience_projection(self) -> None:
        """Test SalienceNetworkProjection."""
        from agent.components.networks.coordinator import (
            SalienceNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="SALIENCE",
            semantic_name="Salience Network",
        )
        
        projection = SalienceNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            urgency_summary="normal",
        )
        
        assert projection.urgency_summary == "normal"
    
    def test_sensorimotor_projection(self) -> None:
        """Test SensorimotorNetworkProjection."""
        from agent.components.networks.coordinator import (
            SensorimotorNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="SENSORIMOTOR",
            semantic_name="Sensorimotor Network",
        )
        
        projection = SensorimotorNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            execution_readiness="unknown",
        )
        
        assert projection.execution_readiness == "unknown"
    
    def test_workspace_projection(self) -> None:
        """Test WorkspaceNetworkProjection."""
        from agent.components.networks.coordinator import (
            WorkspaceNetworkProjection,
        )
        
        identity = CoordinationRequestIdentity(cycle_id="cycle-001", sequence_index=0)
        network_identity = NetworkIdentity(
            network_kind="WORKSPACE",
            semantic_name="Workspace Network",
        )
        
        projection = WorkspaceNetworkProjection(
            identity=identity,
            network_identity=network_identity,
            capacity_state=0.9,
        )
        
        assert projection.capacity_state == 0.9


# =============================================================================
# TEST: GET PROJECTION FOR KIND
# =============================================================================


class TestGetProjectionForKind:
    """Tests for get_projection_for_kind() function."""
    
    def test_get_alerting_projection(self) -> None:
        """Test getting AlertingNetworkProjection class."""
        from agent.components.networks.coordinator import (
            get_projection_for_kind,
        )
        
        projection_class = get_projection_for_kind("ALERTING")
        assert projection_class.__name__ == "AlertingNetworkProjection"
    
    def test_get_unknown_kind(self) -> None:
        """Test getting an unknown network kind."""
        from agent.components.networks.coordinator import (
            get_projection_for_kind,
        )
        
        with pytest.raises(ValueError):
            get_projection_for_kind("UNKNOWN_NETWORK")


# =============================================================================
# END OF TEST SUITE
# =============================================================================