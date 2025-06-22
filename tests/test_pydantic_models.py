"""Test Pydantic models can be instantiated and work correctly."""

from datetime import datetime

from plan.models import (
    Checkpoint,
    CheckpointStatus,
    Deliverable,
    DependencyGroup,
    DevelopmentStatus,
    ProjectMetadata,
    TechnicalRequirement,
    TestCase,
    TestCaseType,
    TestResult,
    TestRun,
    TestStatus,
    TestSuite,
)


class TestCheckpointModels:
    """Test checkpoint-related models."""

    def test_checkpoint_model_creation(self):
        """Test creating a Checkpoint model instance."""
        checkpoint = Checkpoint(
            id="checkpoint-0",
            name="Project Setup",
            description="Initial project setup",
            priority="high",
            status=CheckpointStatus.COMPLETED,
            estimated_hours=2.0,
            actual_hours=1.5,
        )

        assert checkpoint.id == "checkpoint-0"
        assert checkpoint.name == "Project Setup"
        assert checkpoint.status == CheckpointStatus.COMPLETED
        assert checkpoint.estimated_hours == 2.0
        assert checkpoint.actual_hours == 1.5

    def test_test_case_model(self):
        """Test creating a TestCase model."""
        test_case = TestCase(
            name="test_project_structure_exists",
            description="Verify project directories exist",
            type=TestCaseType.UNIT,
        )

        assert test_case.name == "test_project_structure_exists"
        assert test_case.type == TestCaseType.UNIT
        assert test_case.status == "pending"  # default value

    def test_technical_requirement_model(self):
        """Test creating a TechnicalRequirement model."""
        requirement = TechnicalRequirement(
            name="Project Initialization",
            description="Initialize project with uv",
            acceptance_criteria=[
                "uv init --lib structure",
                "Git repository initialized",
            ],
            completed=True,
        )

        assert requirement.name == "Project Initialization"
        assert len(requirement.acceptance_criteria) == 2
        assert requirement.completed is True

    def test_deliverable_model(self):
        """Test creating a Deliverable model."""
        deliverable = Deliverable(
            name="Project Structure",
            status="completed",
            location="root directory",
            description="Complete project directory structure",
        )

        assert deliverable.name == "Project Structure"
        assert deliverable.status == "completed"


class TestProjectModels:
    """Test project metadata and configuration models."""

    def test_project_metadata_creation(self):
        """Test creating ProjectMetadata model."""
        metadata = ProjectMetadata(
            name="term2ai",
            version="0.1.0",
            description="Terminal wrapper with AI integration",
            author="term2ai Team",
            email="cagojeiger@naver.com",
            license="MIT",
            repository="https://github.com/yourusername/term2ai",
            python_version=">=3.11",
        )

        assert metadata.name == "term2ai"
        assert metadata.version == "0.1.0"
        assert metadata.development_status == DevelopmentStatus.ALPHA
        assert metadata.platform == "unix"

    def test_dependency_group_model(self):
        """Test creating DependencyGroup model."""
        dep_group = DependencyGroup(
            name="dev",
            description="Development dependencies",
            packages={"pytest": ">=8.4.1", "mypy": ">=1.16.1"},
            optional=True,
        )

        assert dep_group.name == "dev"
        assert len(dep_group.packages) == 2
        assert dep_group.optional is True


class TestTestTrackingModels:
    """Test test tracking and results models."""

    def test_test_result_creation(self):
        """Test creating TestResult model."""
        result = TestResult(
            test_name="tests.test_project_structure::test_source_directories_exist",
            status=TestStatus.PASSED,
            duration=0.123,
        )

        assert result.status == TestStatus.PASSED
        assert result.duration == 0.123
        assert result.error_message is None

    def test_test_suite_model(self):
        """Test creating TestSuite model."""
        suite = TestSuite(
            name="TestProjectStructure",
            module="tests.test_project_structure",
            tests=[
                "test_source_directories_exist",
                "test_documentation_structure_exists",
            ],
            markers=["unit"],
        )

        assert suite.name == "TestProjectStructure"
        assert len(suite.tests) == 2
        assert "unit" in suite.markers

    def test_test_run_model(self):
        """Test creating TestRun model."""
        run = TestRun(
            id="test-run-001",
            started_at=datetime.now(),
            python_version="3.11.0",
            platform="darwin",
            test_command="pytest -v",
            total_tests=10,
            passed=9,
            failed=1,
        )

        assert run.id == "test-run-001"
        assert run.total_tests == 10
        assert run.success_rate == 90.0

    def test_enum_values(self):
        """Test enum values are accessible."""
        assert CheckpointStatus.PENDING == "pending"
        assert CheckpointStatus.COMPLETED == "completed"
        assert TestCaseType.UNIT == "unit"
        assert TestCaseType.E2E == "e2e"
        assert TestStatus.PASSED == "passed"
        assert TestStatus.FAILED == "failed"
        assert DevelopmentStatus.ALPHA == "alpha"
