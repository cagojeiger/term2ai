"""Integration tests for development tools."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestDevelopmentTools:
    """Test that development tools are properly configured and work."""

    def test_uv_commands_work(self):
        """Verify uv package manager commands work correctly."""
        # Test uv pip list
        result = subprocess.run(
            ["uv", "pip", "list"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"uv pip list failed: {result.stderr}"
        assert "term2ai" in result.stdout, "term2ai should be in installed packages"

    def test_pytest_runs(self):
        """Verify pytest can discover and run tests."""
        # Run pytest with --collect-only to just discover tests
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"pytest collection failed: {result.stderr}"
        # Should find at least this test
        assert "test_dev_tools.py" in result.stdout

    def test_mypy_configuration(self):
        """Verify mypy is properly configured."""
        # Test mypy on the simple hello module
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "src/term2ai/__init__.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"mypy failed: {result.stdout}"
        assert "Success" in result.stdout or result.stdout.strip() == ""

    def test_ruff_linting(self):
        """Verify ruff linting passes on source code."""
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "src/term2ai", "tests"],
            capture_output=True,
            text=True,
        )
        # Ruff returns 0 if no issues found
        assert result.returncode == 0, f"ruff found issues: {result.stdout}"

    def test_black_formatting(self):
        """Verify code is properly formatted with black."""
        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", "src/term2ai", "tests"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"black formatting issues: {result.stdout}"

    def test_hello_function_execution(self):
        """Test that the hello function can be executed via Python."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from term2ai import hello; print(hello())",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"hello execution failed: {result.stderr}"
        assert "Hello from term2ai!" in result.stdout
