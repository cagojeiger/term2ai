"""Test tracking and results models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TestStatus(str, Enum):
    """Status of a test execution."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    XFAIL = "xfail"  # Expected failure
    XPASS = "xpass"  # Unexpected pass


class TestResult(BaseModel):
    """Result of a single test execution."""

    test_name: str = Field(..., description="Full test name including module")
    status: TestStatus = Field(..., description="Test execution status")
    duration: float = Field(..., description="Test duration in seconds")
    error_message: str | None = Field(None, description="Error message if failed")
    stdout: str | None = Field(None, description="Captured stdout")
    stderr: str | None = Field(None, description="Captured stderr")
    traceback: str | None = Field(None, description="Full traceback if error")


class TestSuite(BaseModel):
    """Collection of related tests."""

    name: str = Field(..., description="Test suite name")
    module: str = Field(..., description="Python module containing tests")
    tests: list[str] = Field(default_factory=list, description="List of test names")
    markers: list[str] = Field(
        default_factory=list, description="Pytest markers applied"
    )
    setup_fixtures: list[str] = Field(
        default_factory=list, description="Required fixtures"
    )


class CoverageReport(BaseModel):
    """Code coverage report."""

    total_lines: int = Field(..., description="Total lines of code")
    covered_lines: int = Field(..., description="Lines covered by tests")
    coverage_percentage: float = Field(..., description="Coverage percentage")
    uncovered_lines: dict[str, list[int]] = Field(
        default_factory=dict, description="File to uncovered line numbers"
    )
    branch_coverage: float | None = Field(
        None, description="Branch coverage percentage"
    )


class TestRun(BaseModel):
    """Complete test run with results and metadata."""

    id: str = Field(..., description="Unique test run identifier")
    checkpoint_id: str | None = Field(None, description="Associated checkpoint if any")
    started_at: datetime = Field(..., description="Test run start time")
    completed_at: datetime | None = Field(None, description="Test run end time")
    duration: float | None = Field(None, description="Total duration in seconds")
    python_version: str = Field(..., description="Python version used")
    platform: str = Field(..., description="Platform (e.g., darwin, linux)")
    test_command: str = Field(..., description="Command used to run tests")
    total_tests: int = Field(default=0, description="Total number of tests")
    passed: int = Field(default=0, description="Number of passed tests")
    failed: int = Field(default=0, description="Number of failed tests")
    skipped: int = Field(default=0, description="Number of skipped tests")
    errors: int = Field(default=0, description="Number of test errors")
    results: list[TestResult] = Field(
        default_factory=list, description="Individual test results"
    )
    coverage: CoverageReport | None = Field(None, description="Coverage report")
    exit_code: int | None = Field(None, description="pytest exit code")
    summary: str | None = Field(None, description="Test run summary")

    @property
    def success_rate(self) -> float:
        """Calculate test success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
