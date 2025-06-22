"""Project metadata and tracking models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DevelopmentStatus(str, Enum):
    """Overall project development status."""

    PLANNING = "planning"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "rc"
    STABLE = "stable"


class ProjectMetadata(BaseModel):
    """Project metadata and configuration."""

    name: str = Field(..., description="Project name")
    version: str = Field(..., description="Current version")
    description: str = Field(..., description="Project description")
    author: str = Field(..., description="Author name")
    email: str = Field(..., description="Contact email")
    license: str = Field(..., description="License type")
    repository: str = Field(..., description="Repository URL")
    homepage: str | None = Field(None, description="Project homepage")
    documentation: str | None = Field(None, description="Documentation URL")
    keywords: list[str] = Field(default_factory=list, description="Project keywords")
    classifiers: list[str] = Field(default_factory=list, description="PyPI classifiers")
    python_version: str = Field(..., description="Required Python version")
    platform: str = Field(default="unix", description="Target platform")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Project creation date"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )
    development_status: DevelopmentStatus = Field(
        default=DevelopmentStatus.ALPHA, description="Development status"
    )


class DependencyGroup(BaseModel):
    """Group of related dependencies."""

    name: str = Field(..., description="Group name")
    description: str = Field(..., description="Group description")
    packages: dict[str, str] = Field(
        default_factory=dict, description="Package name to version mapping"
    )
    optional: bool = Field(default=True, description="Whether group is optional")


class ProjectConfiguration(BaseModel):
    """Project configuration and settings."""

    metadata: ProjectMetadata = Field(..., description="Project metadata")
    core_dependencies: dict[str, str] = Field(
        default_factory=dict, description="Core dependencies"
    )
    dependency_groups: list[DependencyGroup] = Field(
        default_factory=list, description="Optional dependency groups"
    )
    scripts: dict[str, str] = Field(
        default_factory=dict, description="Entry point scripts"
    )
    test_config: dict[str, Any] = Field(
        default_factory=dict, description="Test configuration"
    )
    linting_config: dict[str, Any] = Field(
        default_factory=dict, description="Linting configuration"
    )
    type_checking_config: dict[str, Any] = Field(
        default_factory=dict, description="Type checking configuration"
    )
