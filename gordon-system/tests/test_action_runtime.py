# Action Runtime Tests
# =====================

"""
Tests for Phase 3.7.26-R: Tool Execution, Effector, and Action Runtime.

This test suite validates:
    - Action request contracts
    - Tool/effector registration
    - Execution dispatch and result normalization
    - Side effect reporting
"""

import pytest
import asyncio
from dataclasses import field

# Import action runtime components
from src.agent.components.core.action import (
    ActionId,
    InvocationId,
    ToolId,
    EffectorId,
    ActionState,
    ActionRequest,
    ToolContract,
    EffectorContract,
    ExecutionResult,
    ExecutionStatus,
    ActionExecutor,
    DefaultActionExecutor,
)


# =============================================================================
# IDENTITY TESTS
# =============================================================================


class TestIdentifiers:
    """Test identifier generation and comparison."""
    
    def test_action_id_generation(self):
        """ActionIds should be unique UUIDs."""
        id1 = ActionId.generate()
        id2 = ActionId.generate()
        
        assert str(id1) != str(id2)
        assert len(str(id1)) > 0
    
    def test_invocation_id_generation(self):
        """InvocationIds should include timestamp for uniqueness."""
        id1 = InvocationId.generate()
        id2 = InvocationId.generate()
        
        # Should be different due to nanosecond timestamp
        assert str(id1) != str(id2)
    
    def test_tool_id_from_name(self):
        """ToolId should normalize names correctly."""
        tool_id = ToolId.from_name("My Test Tool")
        
        assert tool_id.value == "my_test_tool"
    
    def test_effector_id_from_name(self):
        """EffectorId should normalize names correctly."""
        effector_id = EffectorId.from_name("File System Effector")
        
        assert effector_id.value == "file_system_effector"


# =============================================================================
# ACTION REQUEST CONTRACT TESTS
# =============================================================================


class TestActionRequest:
    """Test ActionRequest contract structure."""
    
    def test_action_request_creation(self):
        """ActionRequest should require required fields."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        request = ActionRequest(
            action_id=action_id,
            invocation_id=invocation_id,
            arguments={"test": "value"},
        )
        
        assert request.action_id == action_id
        assert request.invocation_id == invocation_id
        assert request.arguments["test"] == "value"
    
    def test_action_request_defaults(self):
        """ActionRequest should have sensible defaults."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        request = ActionRequest(
            action_id=action_id,
            invocation_id=invocation_id,
        )
        
        assert request.arguments == {}
        assert request.priority.value == 2  # NORMAL
        assert request.risk_level == "low"
    
    def test_action_request_freeze(self):
        """ActionRequest should be frozen (immutable)."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        request = ActionRequest(
            action_id=action_id,
            invocation_id=invocation_id,
        )
        
        # Should not allow modification
        with pytest.raises((AttributeError, TypeError)):
            request.arguments["new"] = "value"


# =============================================================================
# TOOL AND EFFECTOR CONTRACT TESTS
# =============================================================================


class TestToolContract:
    """Test ToolContract structure."""
    
    def test_tool_contract_creation(self):
        """ToolContract should require all fields."""
        tool_id = ToolId.from_name("test_tool")
        
        contract = ToolContract(
            tool_id=tool_id,
            name="Test Tool",
            supported_operations=("read", "write"),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        
        assert contract.tool_id == tool_id
        assert contract.name == "Test Tool"
        assert "read" in contract.supported_operations
        assert contract.side_effect_class == "none"


class TestEffectorContract:
    """Test EffectorContract structure."""
    
    def test_effector_contract_creation(self):
        """EffectorContract should require all fields."""
        effector_id = EffectorId.from_name("test_effector")
        
        contract = EffectorContract(
            effector_id=effector_id,
            name="Test Effector",
            target_domain="filesystem",
            side_effect_class="write",
        )
        
        assert contract.effector_id == effector_id
        assert contract.target_domain == "filesystem"
        assert contract.side_effect_class == "write"


# =============================================================================
# EXECUTION RESULT CONTRACT TESTS
# =============================================================================


class TestExecutionResult:
    """Test ExecutionResult structure."""
    
    def test_success_result(self):
        """Success result should have proper status and value."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        result = ExecutionResult(
            action_id=action_id,
            invocation_id=invocation_id,
            status=ExecutionStatus.SUCCEEDED,
            value="test result",
        )
        
        assert result.status == ExecutionStatus.SUCCEEDED
        assert result.value == "test result"
    
    def test_failure_result(self):
        """Failure result should have proper status and error."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        result = ExecutionResult(
            action_id=action_id,
            invocation_id=invocation_id,
            status=ExecutionStatus.FAILED,
            error="Something went wrong",
        )
        
        assert result.status == ExecutionStatus.FAILED
        assert "Something went wrong" in result.error
    
    def test_result_timing(self):
        """Result should track timing."""
        action_id = ActionId.generate()
        invocation_id = InvocationId.generate()
        
        import time
        
        start = time.monotonic()
        result = ExecutionResult(
            action_id=action_id,
            invocation_id=invocation_id,
            status=ExecutionStatus.SUCCEEDED,
            value="test",
            started_at=start,
        )
        
        assert result.started_at >= start
        # completed_at defaults to started_at if not provided


# =============================================================================
# ACTION EXECUTOR TESTS
# =============================================================================


class TestActionExecutor:
    """Test ActionExecutor canonical authority."""
    
    @pytest.fixture
    def executor(self):
        """Create an action executor for testing."""
        return DefaultActionExecutor("test-runtime-123")
    
    async def test_register_tool(self, executor):
        """Should be able to register a tool contract."""
        tool_id = ToolId.from_name("test_tool")
        
        contract = ToolContract(
            tool_id=tool_id,
            name="Test Tool",
            supported_operations=("run",),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        
        await executor.register_tool(contract)
        
        retrieved = executor.get_tool_contract(tool_id)
        assert retrieved is not None
        assert retrieved.tool_id == tool_id
    
    async def test_duplicate_tool_registration_fails(self, executor):
        """Registering duplicate tool should fail."""
        tool_id = ToolId.from_name("test_tool")
        
        contract1 = ToolContract(
            tool_id=tool_id,
            name="Test Tool",
            supported_operations=("run",),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        
        await executor.register_tool(contract1)
        
        # Try to register same tool again
        result = await executor.register_tool(contract1)
        assert result is False  # Returns False for duplicate
    
    async def test_register_effector(self, executor):
        """Should be able to register an effector contract."""
        effector_id = EffectorId.from_name("test_effector")
        
        contract = EffectorContract(
            effector_id=effector_id,
            name="Test Effector",
            target_domain="filesystem",
            side_effect_class="write",
        )
        
        await executor.register_effector(contract)
        
        retrieved = executor.get_effector_contract(effector_id)
        assert retrieved is not None
        assert retrieved.effector_id == effector_id
    
    def test_state_snapshot(self, executor):
        """Executor should provide state snapshot."""
        snapshot = executor.get_state_snapshot()
        
        assert "runtime_id" in snapshot
        assert "tool_count" in snapshot
        assert "effector_count" in snapshot


# =============================================================================
# ASYNC EXECUTION TESTS
# =============================================================================


class TestAsyncExecution:
    """Test async execution patterns."""
    
    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Should be able to register tools asynchronously."""
        executor = DefaultActionExecutor("test-runtime")
        
        tool_id = ToolId.from_name("async_test_tool")
        
        contract = ToolContract(
            tool_id=tool_id,
            name="Async Test Tool",
            supported_operations=("execute",),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        
        result = await executor.register_tool(contract)
        
        assert result is True
        assert executor.get_tool_contract(tool_id) is not None
    
    @pytest.mark.asyncio
    async def test_effector_registration(self):
        """Should be able to register effectors asynchronously."""
        executor = DefaultActionExecutor("test-runtime")
        
        effector_id = EffectorId.from_name("async_test_effector")
        
        contract = EffectorContract(
            effector_id=effector_id,
            name="Async Test Effector",
            target_domain="filesystem",
            side_effect_class="read",
        )
        
        result = await executor.register_effector(contract)
        
        assert result is True
        assert executor.get_effector_contract(effector_id) is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])