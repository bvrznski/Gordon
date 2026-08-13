# Tests for Integration Between Authorities
# ==========================================

"""
Tests for the integration layer between readiness, admission, and operational state.

Tests cover:
- State synchronization
- Revocation propagation (readiness → admission)
- Operational transition validation
"""

import pytest
import asyncio
from typing import List, Dict, Tuple, Optional


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def runtime_id() -> str:
    """Generate a unique runtime ID for testing."""
    import uuid
    return f"test_runtime_{uuid.uuid4().hex[:8]}"


class MockReadinessController:
    """Mock readiness controller for testing integration."""
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._status = None
    
    def get_status(self):
        return self._status
    
    def get_snapshot(self):
        class Snapshot:
            state_version = 100
        return Snapshot()


class MockAdmissionController:
    """Mock admission controller for testing integration."""
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._status = None
    
    def get_snapshot(self):
        class Snapshot:
            state_version = 100
        return Snapshot()
    
    def close_admission(self, reason: str):
        pass
    
    def revoke_admission(self, reason: str):
        pass


class MockOperationalAuthority:
    """Mock operational authority for testing integration."""
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self.state = None


# =============================================================================
# TEST: State Synchronization
# =============================================================================

class TestStateSynchronization:
    """Tests for state synchronization between authorities."""
    
    async def test_sync_state_with_mocked_authorities(self, runtime_id: str):
        """Test state synchronization with mock authorities."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController,
                StateSyncResult
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController,
                StateSyncResult
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        # Set up mock authorities
        controller.set_readiness_controller(MockReadinessController(runtime_id))
        controller.set_admission_controller(MockAdmissionController(runtime_id))
        controller.set_operational_authority(MockOperationalAuthority(runtime_id))
        
        result = await controller.sync_state()
        
        assert isinstance(result, StateSyncResult)
    
    async def test_detects_state_drift(self, runtime_id: str):
        """Test that state drift is detected."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController,
                StateSyncResult
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController,
                StateSyncResult
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        # Set up authorities with different version numbers
        class DriftReadiness:
            def get_snapshot(self):
                class Snapshot:
                    state_version = 100
                return Snapshot()
        
        class DriftAdmission:
            def get_snapshot(self):
                class Snapshot:
                    state_version = 500  # Different!
                return Snapshot()
        
        controller.set_readiness_controller(DriftReadiness())
        controller.set_admission_controller(DriftAdmission())
        
        result = await controller.sync_state()
        
        assert isinstance(result, StateSyncResult)


# =============================================================================
# TEST: Revocation Propagation
# =============================================================================

class TestRevocationPropagation:
    """Tests for revocation propagation across authorities."""
    
    async def test_readiness_revocation_closes_admission(self, runtime_id: str):
        """Test that readiness revocation closes admission."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        close_called = []
        
        class ClosedAdmission:
            def close_admission(self, reason: str):
                close_called.append(reason)
            
            def revoke_admission(self, reason: str):
                pass
            
            def get_snapshot(self):
                class Snapshot:
                    state_version = 100
                return Snapshot()
        
        controller.set_readiness_controller(MockReadinessController(runtime_id))
        controller.set_admission_controller(ClosedAdmission())
        
        # Trigger readiness revocation
        await controller.handle_readiness_revoked("Health check failed")
        
        assert len(close_called) > 0
    
    async def test_non_critical_revocation_restricts_not_closes(self, runtime_id: str):
        """Test that non-critical revocation restricts rather than closes."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        revoke_called = []
        
        class RestrictedAdmission:
            def close_admission(self, reason: str):
                pass
            
            def revoke_admission(self, reason: str):
                revoke_called.append(reason)
            
            def get_snapshot(self):
                class Snapshot:
                    state_version = 100
                return Snapshot()
        
        controller.set_readiness_controller(MockReadinessController(runtime_id))
        controller.set_admission_controller(RestrictedAdmission())
        
        # Trigger non-critical readiness revocation (degraded)
        await controller.handle_readiness_revoked("Some features degraded")
        
        assert len(revoke_called) > 0


# =============================================================================
# TEST: Operational Transition Validation
# =============================================================================

class TestOperationalTransition:
    """Tests for operational state transitions."""
    
    async def test_transition_requires_both_conditions(self, runtime_id: str):
        """Test that transition to operational requires both readiness and admission."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        # Both conditions must be true
        allowed, blockers = await controller.validate_transition_to_operational(
            readiness_ready=True,
            admission_open=True
        )
        
        assert allowed is True
        assert len(blockers) == 0
    
    async def test_blocked_without_readiness(self, runtime_id: str):
        """Test that transition is blocked without readiness."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        # Readiness is false
        allowed, blockers = await controller.validate_transition_to_operational(
            readiness_ready=False,
            admission_open=True
        )
        
        assert allowed is False
        assert "Readiness not satisfied" in blockers
    
    async def test_blocked_without_admission(self, runtime_id: str):
        """Test that transition is blocked without admission."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController(runtime_id)
        
        # Admission is false
        allowed, blockers = await controller.validate_transition_to_operational(
            readiness_ready=True,
            admission_open=False
        )
        
        assert allowed is False
        assert "Admission not open" in blockers


# =============================================================================
# TEST: Multi-Runtime Isolation
# =============================================================================

class TestIntegrationMultiRuntime:
    """Tests for multi-runtime isolation in integration."""
    
    def test_integration_snapshots_contain_correct_runtime(self, runtime_id: str):
        """Test that integration snapshots contain correct runtime ID."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller = RuntimeIntegrationController("my_runtime")
        
        snapshot = controller.get_integration_snapshot()
        
        assert snapshot["runtime_id"] == "my_runtime"
    
    def test_different_runtimes_have_independent_state(self):
        """Test that different runtimes have independent integration state."""
        try:
            from agent.components.core.integration import (
                RuntimeIntegrationController
            )
        except ImportError:
            from agent.components.core.integration.__init__ import (
                RuntimeIntegrationController
            )
        
        controller_a = RuntimeIntegrationController("runtime_a")
        controller_b = RuntimeIntegrationController("runtime_b")
        
        # Get snapshots - should be independent
        snap_a = controller_a.get_integration_snapshot()
        snap_b = controller_b.get_integration_snapshot()
        
        assert snap_a["runtime_id"] != snap_b["runtime_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])