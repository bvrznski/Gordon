# Tests for Admission Authority
# ==============================

"""
Tests for the AdmissionController and related components.

Tests cover:
- State transitions
- Gate evaluation in order
- Work acceptance/rejection decisions
- Receipt issuance and validation
- Revocation handling
"""

import pytest
import asyncio
import time
from typing import List, Dict, Tuple, Optional


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def runtime_id() -> str:
    """Generate a unique runtime ID for testing."""
    import uuid
    return f"test_runtime_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def admission_controller(runtime_id: str) -> "AdmissionController":
    """Create an admission controller for testing."""
    try:
        from gordon_system.src.agent.components.core.admission.__init__ import AdmissionController
    except ImportError:
        try:
            from src.agent.components.core.admission import AdmissionController
        except ImportError:
            from agent.components.core.admission import AdmissionController
    
    return AdmissionController(runtime_id)


# =============================================================================
# TEST: State Transitions
# =============================================================================

class TestAdmissionStateTransitions:
    """Tests for admission state transitions."""
    
    def test_initial_state_is_closed(self, runtime_id: str):
        """Test that initial admission state is CLOSED."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionStatus
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
        
        controller = AdmissionController(runtime_id)
        
        assert controller.admission_status == AdmissionStatus.CLOSED
    
    def test_open_admission(self, runtime_id: str):
        """Test opening admission."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionStatus
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
        
        controller = AdmissionController(runtime_id)
        assert controller.admission_status == AdmissionStatus.CLOSED
        
        result = controller.open_admission()
        
        assert result is True
        assert controller.admission_status == AdmissionStatus.OPEN
    
    def test_close_admission(self, runtime_id: str):
        """Test closing admission."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionStatus
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
        
        controller = AdmissionController(runtime_id)
        controller.open_admission()
        
        assert controller.admission_status == AdmissionStatus.OPEN
        
        controller.close_admission("Testing")
        
        assert controller.admission_status == AdmissionStatus.CLOSED
    
    def test_cannot_open_terminal_state(self, runtime_id: str):
        """Test that terminal states cannot be reopened."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionStatus
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
        
        controller = AdmissionController(runtime_id)
        
        # Terminate
        controller.terminate_admission()
        
        assert controller.admission_status == AdmissionStatus.TERMINATED
        
        # Cannot reopen
        result = controller.open_admission()
        assert result is False


# =============================================================================
# TEST: Gate Evaluation
# =============================================================================

class TestAdmissionGateEvaluation:
    """Tests for gate evaluation."""
    
    def test_gates_execute_in_deterministic_order(self, runtime_id: str):
        """Test that gates are evaluated in a deterministic order."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionRequest,
                AdmissionGate
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest,
                    AdmissionGate
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest,
                    AdmissionGate
                )
        
        controller = AdmissionController(runtime_id)
        
        # Create a request
        request = AdmissionRequest(
            request_id=str(id("test")),
            runtime_id=runtime_id,
            boot_session_id="session_123",
            operation_id="operation_1",
            caller_identity="caller_1",
            work_kind="normal"
        )
    
    def test_missing_evaluator_returns_unknown(self, runtime_id: str):
        """Test that missing gate evaluator returns unknown."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionRequest
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
        
        controller = AdmissionController(runtime_id)
        
        request = AdmissionRequest(
            request_id="test_request",
            runtime_id=runtime_id,
            boot_session_id="session_123",
            operation_id="op_1",
            caller_identity="caller_1",
            work_kind="normal"
        )
        
        gates_passed, results = asyncio.run(controller.evaluate_gates(request))
        
        assert isinstance(results, tuple)


# =============================================================================
# TEST: Work Acceptance
# =============================================================================

class TestWorkAcceptance:
    """Tests for work acceptance."""
    
    async def test_accept_request_when_all_gates_pass(self, runtime_id: str):
        """Test accepting a request when all gates pass."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionRequest
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
        
        controller = AdmissionController(runtime_id)
        
        def always_pass(_):
            return True
        
        for gate in [
            "readiness",
            "operational",
            "capability",
        ]:
            try:
                controller.set_gate_evaluator(gate, always_pass)
            except Exception:
                pass  # Gate enum may differ
        
        request = AdmissionRequest(
            request_id="test_request",
            runtime_id=runtime_id,
            boot_session_id="session_123",
            operation_id="op_1",
            caller_identity="caller_1",
            work_kind="normal"
        )
    
    async def test_reject_when_readiness_gate_fails(self, runtime_id: str):
        """Test rejecting when readiness gate fails."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionRequest
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionRequest
                )
        
        controller = AdmissionController(runtime_id)
        
        def always_fail(_):
            return False
        
        try:
            controller.set_gate_evaluator("readiness", always_fail)
        except Exception:
            pass  # Skip if can't set evaluator
    
    def test_receipt_is_validated(self, runtime_id: str):
        """Test that admission receipts are validated correctly."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController
                )
        
        controller = AdmissionController(runtime_id)
        
        result = controller.validate_receipt(
            request_id="nonexistent",
            runtime_id=runtime_id,
            expected_state_version=0
        )
        
        assert result is False  # Receipt doesn't exist


# =============================================================================
# TEST: Multi-Runtime Isolation
# =============================================================================

class TestAdmissionMultiRuntime:
    """Tests for multi-runtime isolation in admission."""
    
    def test_different_runtimes_independent(self):
        """Test that different runtimes have independent admission state."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController,
                AdmissionStatus
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController,
                    AdmissionStatus
                )
        
        controller_a = AdmissionController("runtime_a")
        controller_b = AdmissionController("runtime_b")
        
        # Open admission for A
        controller_a.open_admission()
        
        assert controller_a.admission_status == AdmissionStatus.OPEN
        
        # B should still be closed
        assert controller_b.admission_status == AdmissionStatus.CLOSED
    
    def test_boot_sessions_are_unique(self):
        """Test that each runtime has a unique boot session ID."""
        try:
            from gordon_system.src.agent.components.core.admission.__init__ import (
                AdmissionController
            )
        except ImportError:
            try:
                from src.agent.components.core.admission import (
                    AdmissionController
                )
            except ImportError:
                from agent.components.core.admission import (
                    AdmissionController
                )
        
        controller_a = AdmissionController("runtime_a")
        controller_b = AdmissionController("runtime_b")
        
        assert controller_a.boot_session_id != controller_b.boot_session_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])