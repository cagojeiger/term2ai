"""Test that all required dependencies can be imported."""


class TestDependencies:
    """Test that all core dependencies are properly installed and importable."""

    def test_core_dependencies_importable(self):
        """Verify all core dependencies can be imported."""
        # Core dependencies from pyproject.toml
        import aiofiles
        import pexpect
        import ptyprocess
        import pydantic
        import rich
        import typer

        # Basic checks that imports worked
        assert pexpect.__version__
        assert ptyprocess.__version__
        assert pydantic.__version__
        # rich doesn't expose __version__ directly
        assert rich
        # typer uses __version__ from typer.__version__
        assert typer
        assert aiofiles

    def test_dev_dependencies_importable(self):
        """Verify all development dependencies can be imported."""
        import black
        import mypy
        import pytest
        import pytest_asyncio
        import pytest_cov
        import ruff

        # Basic version checks
        assert black.__version__
        # mypy doesn't expose __version__ directly
        assert mypy
        assert pytest.__version__
        assert pytest_asyncio.__version__
        # pytest_cov doesn't expose __version__ directly
        assert pytest_cov
        # ruff doesn't expose __version__ in Python
        assert ruff

    def test_term2ai_importable(self):
        """Verify term2ai package can be imported."""
        from term2ai import hello

        # Test basic functionality
        assert hello() == "Hello from term2ai!"

    def test_term2ai_submodules_importable(self):
        """Verify term2ai submodules can be imported."""
        import term2ai.core
        import term2ai.models
        import term2ai.utils

        # Just checking imports work
        assert term2ai.core
        assert term2ai.models
        assert term2ai.utils
