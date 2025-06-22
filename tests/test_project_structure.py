"""Test project structure exists as required by Checkpoint 0."""

from pathlib import Path


class TestProjectStructure:
    """Test that all required directories and files exist."""

    def test_source_directories_exist(self):
        """Verify source code directories are properly created."""
        base_path = Path("src/term2ai")
        assert base_path.exists(), "Source directory should exist"
        assert base_path.is_dir(), "Source path should be a directory"

        # Check subdirectories
        subdirs = ["core", "models", "utils"]
        for subdir in subdirs:
            path = base_path / subdir
            assert path.exists(), f"{subdir} directory should exist"
            assert path.is_dir(), f"{subdir} should be a directory"
            assert (path / "__init__.py").exists(), f"{subdir} should have __init__.py"

    def test_documentation_structure_exists(self):
        """Verify documentation directories exist."""
        docs_path = Path("docs")
        assert docs_path.exists(), "docs directory should exist"
        assert docs_path.is_dir(), "docs should be a directory"

        # Check key documentation files
        doc_files = ["api-design.md", "architecture.md", "technical-decisions.md"]
        for doc_file in doc_files:
            assert (docs_path / doc_file).exists(), f"{doc_file} should exist"

    def test_plan_structure_exists(self):
        """Verify planning directories and checkpoint files exist."""
        plan_path = Path("plan")
        assert plan_path.exists(), "plan directory should exist"
        assert plan_path.is_dir(), "plan should be a directory"

        # Check checkpoints directory
        checkpoints_path = plan_path / "checkpoints"
        assert checkpoints_path.exists(), "checkpoints directory should exist"
        assert checkpoints_path.is_dir(), "checkpoints should be a directory"

        # Check roadmap exists
        assert (plan_path / "roadmap.md").exists(), "roadmap.md should exist"

        # Check models directory now exists
        models_path = plan_path / "models"
        assert models_path.exists(), "models directory should exist"
        assert models_path.is_dir(), "models should be a directory"
        assert (models_path / "__init__.py").exists(), "models should have __init__.py"

    def test_test_directory_exists(self):
        """Verify test directory structure."""
        tests_path = Path("tests")
        assert tests_path.exists(), "tests directory should exist"
        assert tests_path.is_dir(), "tests should be a directory"
        assert (tests_path / "__init__.py").exists(), "tests should have __init__.py"
        assert (tests_path / "conftest.py").exists(), "conftest.py should exist"

    def test_configuration_files_exist(self):
        """Verify all configuration files are present."""
        config_files = [
            "pyproject.toml",
            "pytest.ini",
            ".gitignore",
            "README.md",
            "CLAUDE.md",
            "LICENSE",
        ]

        for config_file in config_files:
            path = Path(config_file)
            assert path.exists(), f"{config_file} should exist"
            assert path.is_file(), f"{config_file} should be a file"

    def test_py_typed_marker_exists(self):
        """Verify py.typed file exists for type hint support."""
        py_typed = Path("src/term2ai/py.typed")
        assert py_typed.exists(), "py.typed file should exist"
        assert py_typed.is_file(), "py.typed should be a file"
