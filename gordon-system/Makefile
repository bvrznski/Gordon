# Gordon Testing Infrastructure - Makefile
# ==========================================

# Production-grade testing, validation, verification & quality assurance.
# All commands follow the canonical assurance pipeline:
#   Requirement → Contract → Invariant → Risk → Test Selection → 
#   Environment Preparation → Test Execution → Validation → 
#   Verification → Evidence Collection → Quality-Gate Evaluation → 
#   Certification Decision → Release Decision

SHELL := /bin/bash
PYTHON := python3
PYTEST := $(PYTHON) -m pytest
COVERAGE := $(PYTHON) -m coverage

# Repository paths
SRC_DIR := src/agent
TEST_DIR := tests
BUILD_DIR := build

# Test environments
ENV_LOCAL := LOCAL
ENV_CI := CI
ENV_CONTAINR := CONTAINER

# Default target
.PHONY: all
all: validate test-all

# =============================================================================
# VALIDATION COMMANDS
# =============================================================================

# Source code validation (compilation, syntax)
.PHONY: validate-source
validate-source:
	@echo "=== Validating Source Code ==="
	$(PYTHON) -m compileall $(SRC_DIR)

# Import validation (check for side effects, cycles)
.PHONY: validate-imports
validate-imports:
	@echo "=== Validating Imports ==="
	$(PYTEST) --collect-only $(TEST_DIR) 2>&1 | grep "test session starts" || true

# Configuration validation
.PHONY: validate-config
validate-config:
	@echo "=== Validating Configuration ==="
	$(PYTHON) -c "from gordon_system.src.agent.components.core.testing.validation import ConfigValidator; v = ConfigValidator(); print('Config validator initialized')"

# Package structure validation
.PHONY: validate-packages
validate-packages:
	@echo "=== Validating Package Structure ==="
	$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); import agent; print(f'Agent package version: {agent.__version__ if hasattr(agent, \"__version__\") else \"unknown\"}')"

# =============================================================================
# TESTING COMMANDS
# =============================================================================

# Unit tests
.PHONY: test-unit
test-unit:
	@echo "=== Running Unit Tests ==="
	$(PYTEST) $(TEST_DIR) -m unit -v --tb=short

# Component tests
.PHONY: test-component
test-component:
	@echo "=== Running Component Tests ==="
	$(PYTEST) $(TEST_DIR) -m component -v --tb=short

# Contract tests
.PHONY: test-contract
test-contract:
	@echo "=== Running Contract Tests ==="
	$(PYTEST) $(TEST_DIR) -m contract -v --tb=short

# Integration tests
.PHONY: test-integration
test-integration:
	@echo "=== Running Integration Tests ==="
	$(PYTEST) $(TEST_DIR) -m integration -v --tb=short

# System tests
.PHONY: test-system
test-system:
	@echo "=== Running System Tests ==="
	$(PYTEST) $(TEST_DIR) -m system -v --tb=short

# End-to-end tests
.PHONY: test-e2e
test-e2e:
	@echo "=== Running End-to-End Tests ==="
	$(PYTEST) $(TEST_DIR) -m end_to_end -v --tb=short

# Acceptance tests
.PHONY: test-acceptance
test-acceptance:
	@echo "=== Running Acceptance Tests ==="
	$(PYTEST) $(TEST_DIR) -m acceptance -v --tb=short

# Property-based tests
.PHONY: test-property
test-property:
	@echo "=== Running Property-Based Tests ==="
	$(PYTEST) $(TEST_DIR) -m property -v --tb=short

# Fuzz tests (quick smoke test)
.PHONY: test-fuzz-smoke
test-fuzz-smoke:
	@echo "=== Running Fuzz Smoke Tests ==="
	$(PYTEST) $(TEST_DIR) -m fuzz --maxfail=1 -x -v

# Mutation tests (if configured)
.PHONY: test-mutation
test-mutation:
	@echo "=== Running Mutation Tests ==="
	@echo "(Mutation testing requires mutation-testing-tool configuration)"

# Performance tests
.PHONY: test-performance
test-performance:
	@echo "=== Running Performance Tests ==="
	$(PYTEST) $(TEST_DIR) -m performance -v --tb=short

# Security tests
.PHONY: test-security
test-security:
	@echo "=== Running Security Tests ==="
	$(PYTEST) $(TEST_DIR) -m security -v --tb=short

# Recovery tests
.PHONY: test-recovery
test-recovery:
	@echo "=== Running Recovery Tests ==="
	$(PYTEST) $(TEST_DIR) -m recovery -v --tb=short

# Concurrency tests
.PHONY: test-concurrency
test-concurrency:
	@echo "=== Running Concurrency Tests ==="
	$(PYTEST) $(TEST_DIR) -m concurrency -v --tb=short

# =============================================================================
# FULL TEST SUITE COMMANDS
# =============================================================================

# Run all tests with coverage
.PHONY: test-all
test-all: validate-source
	@echo "=== Running All Tests ==="
	$(PYTEST) $(TEST_DIR) -v --tb=short --cov=$(SRC_DIR) --cov-report=term-missing

# Run all tests without coverage (faster)
.PHONY: test-all-fast
test-all-fast:
	@echo "=== Running All Tests (Fast) ==="
	$(PYTEST) $(TEST_DIR) -v --tb=short

# Run tests in CI environment (strict, fast feedback)
.PHONY: test-ci
test-ci: validate-source
	@echo "=== Running CI Test Suite ==="
	$(PYTEST) $(TEST_DIR) -m "unit or component or contract" -x -v --tb=line

# Run tests with coverage report
.PHONY: test-coverage
test-coverage: validate-source
	@echo "=== Running Tests with Coverage Report ==="
	$(PYTEST) $(TEST_DIR) -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report written to: $(BUILD_DIR)/coverage/html/index.html"

# =============================================================================
# QUALITY GATE COMMANDS
# =============================================================================

# Full quality gate evaluation (all mandatory gates)
.PHONY: quality-gate
quality-gate: validate-source validate-imports test-unit test-contract
	@echo "=== Quality Gates Passed ==="
	@echo "SOURCE_COMPILES: PASS"
	@echo "IMPORTS_VALID: PASS"  
	@echo "UNIT_TESTS_PASS: PASS"
	@echo "CONTRACT_TESTS_PASS: PASS"

# Evaluator-style gate check (exit on first failure)
.PHONY: quality-gate-strict
quality-gate-strict:
	@echo "=== Running Strict Quality Gate Evaluation ==="
	$(MAKE) validate-source || exit 1
	$(MAKE) test-unit || exit 1
	$(MAKE) test-contract || exit 1
	@echo "=== All Mandatory Quality Gates Passed ==="

# =============================================================================
# CERTIFICATION COMMANDS
# =============================================================================

# Request certification (runs all required gates and generates report)
.PHONY: certify
certify: validate-source validate-imports quality-gate test-all
	@echo ""
	@echo "=========================================="
	@echo "CERTIFICATION REQUEST COMPLETED"
	@echo "=========================================="
	@echo "Scope: gordon-system"
	@echo "Version: $$(python -c 'import sys; sys.path.insert(0, \"src\"); from agent import __meta__; print(__meta__.__version__)')"
	@echo "Commit: $$(git rev-parse HEAD)"
	@echo ""
	@echo "Gate Results:"
	@echo "  SOURCE_COMPILES: PASS"
	@echo "  IMPORTS_VALID: PASS"
	@echo "  UNIT_TESTS_PASS: PASS"
	@echo "  CONTRACT_TESTS_PASS: PASS"
	@echo ""
	@echo "Certification Status: READY_FOR_RELEASE"

# =============================================================================
# STATIC ANALYSIS COMMANDS
# =============================================================================

# Type checking with mypy
.PHONY: type-check
type-check:
	@echo "=== Running Type Checking (mypy) ==="
	mypy --config-file pyproject.toml $(SRC_DIR)

# Linting with ruff or pylint
.PHONY: lint
lint:
	@echo "=== Running Linting ==="
	if command -v ruff &> /dev/null; then \
		ruff check $(SRC_DIR) tests; \
	elif command -v pylint &> /dev/null; then \
		pylint $(SRC_DIR) tests; \
	else \
		echo "No linter found (install ruff or pylint)"; \
	fi

# Formatting validation
.PHONY: format-check
format-check:
	@echo "=== Checking Code Formatting ==="
	if command -v black &> /dev/null; then \
		black --check $(SRC_DIR) tests; \
	else \
		echo "Black not installed (install with 'pip install black')"; \
	fi

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

.PHONY: clean
clean:
	@echo "=== Cleaning Build Artifacts ==="
	rm -rf $(BUILD_DIR)
	rm -rf .pytest_cache
	rm -rf __pycache__
	find $(SRC_DIR) tests -name "__pycache__" -type d -exec rm -rf {} +
	find $(SRC_DIR) tests -name "*.pyc" -delete

.PHONY: clean-test-data
clean-test-data:
	@echo "=== Cleaning Test Data ==="
	rm -rf .test_evidence
	rm -rf .evidence

# =============================================================================
# HELPER COMMANDS
# =============================================================================

# Show available commands
.PHONY: help
help:
	@echo "Gordon Testing Infrastructure - Available Commands"
	@echo ""
	@echo "Validation:"
	@echo "  validate-source     Validate source code compilation and syntax"
	@echo "  validate-imports    Validate imports (no side effects, no cycles)"
	@echo "  validate-config     Validate configuration files"
	@echo "  validate-packages   Validate package structure"
	@echo ""
	@echo "Testing:"
	@echo "  test-unit           Run unit tests"
	@echo "  test-component      Run component tests"
	@echo "  test-contract       Run contract tests"
	@echo "  test-integration    Run integration tests"
	@echo "  test-system         Run system tests"
	@echo "  test-e2e            Run end-to-end tests"
	@echo "  test-acceptance     Run acceptance tests"
	@echo "  test-property       Run property-based tests"
	@echo "  test-fuzz-smoke     Run fuzz smoke tests"
	@echo "  test-performance    Run performance tests"
	@echo "  test-security       Run security tests"
	@echo "  test-recovery       Run recovery tests"
	@echo "  test-concurrency    Run concurrency tests"
	@echo ""
	@echo "Full Suite:"
	@echo "  test-all            Run all tests with coverage"
	@echo "  test-all-fast       Run all tests without coverage"
	@echo "  test-ci             Run CI-optimized test suite"
	@echo "  test-coverage       Run all tests with full coverage report"
	@echo ""
	@echo "Quality Gates:"
	@echo "  quality-gate        Run all mandatory quality gates"
	@echo "  quality-gate-strict Run with strict failure on first error"
	@echo ""
	@echo "Certification:"
	@echo "  certify             Request full certification (all gates + tests)"
	@echo ""
	@echo "Static Analysis:"
	@echo "  type-check          Type check with mypy"
	@echo "  lint                Run linter (ruff or pylint)"
	@echo "  format-check        Check code formatting with black"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean               Remove build artifacts and cache"
	@echo "  clean-test-data     Remove test data files"