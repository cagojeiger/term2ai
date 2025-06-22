"""Checkpoint tracking models for project development."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CheckpointStatus(str, Enum):
    """Status of a checkpoint in the development process."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TestCaseType(str, Enum):
    """Type of test case."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


class TestCase(BaseModel):
    """Model for tracking individual test cases."""

    name: str = Field(..., description="Name of the test case")
    description: str = Field(..., description="Description of what the test verifies")
    type: TestCaseType = Field(..., description="Type of test case")
    status: str = Field(default="pending", description="Test implementation status")
    file_path: str | None = Field(None, description="Path to test file")


class TechnicalRequirement(BaseModel):
    """Technical requirement for a checkpoint."""

    name: str = Field(..., description="Name of the requirement")
    description: str = Field(..., description="Detailed description")
    acceptance_criteria: list[str] = Field(
        default_factory=list, description="List of acceptance criteria"
    )
    completed: bool = Field(default=False, description="Whether requirement is met")


class Deliverable(BaseModel):
    """Deliverable item for a checkpoint."""

    name: str = Field(..., description="Name of the deliverable")
    status: str = Field(..., description="Status of the deliverable")
    location: str = Field(..., description="File or directory location")
    description: str = Field(..., description="Description of the deliverable")


class Checkpoint(BaseModel):
    """Model for tracking project checkpoints."""

    id: str = Field(..., description="Unique identifier for the checkpoint")
    name: str = Field(..., description="Name of the checkpoint")
    description: str = Field(..., description="Overview of the checkpoint")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    status: CheckpointStatus = Field(
        default=CheckpointStatus.PENDING, description="Current status"
    )
    estimated_hours: float = Field(..., description="Estimated hours to complete")
    actual_hours: float | None = Field(None, description="Actual hours taken")
    dependencies: list[str] = Field(
        default_factory=list, description="List of dependent checkpoint IDs"
    )
    technical_requirements: list[TechnicalRequirement] = Field(
        default_factory=list, description="Technical requirements"
    )
    test_cases: list[TestCase] = Field(
        default_factory=list, description="Test cases for this checkpoint"
    )
    deliverables: list[Deliverable] = Field(
        default_factory=list, description="Deliverable items"
    )
    started_at: datetime | None = Field(None, description="When work started")
    completed_at: datetime | None = Field(None, description="When work completed")
    notes: str | None = Field(None, description="Additional notes")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
