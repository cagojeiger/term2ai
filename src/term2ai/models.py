from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ShellType(str, Enum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    SH = "sh"


class ProcessState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"


class PTYConfig(BaseModel):
    """Immutable PTY configuration"""

    shell_command: str = Field(default="/bin/bash")
    shell_type: ShellType = Field(default=ShellType.BASH)
    env_vars: dict[str, str] = Field(default_factory=dict)
    working_directory: str | None = Field(default=None)
    timeout: float = Field(default=30.0)

    class Config:
        frozen = True


class PTYHandle(BaseModel):
    """Immutable PTY handle"""

    process_id: int
    fd: int
    created_at: datetime
    config: PTYConfig

    class Config:
        frozen = True


class ProcessEvent(BaseModel):
    """Immutable process event for event sourcing"""

    event_type: str
    timestamp: datetime
    data: dict[str, Any]
    process_id: int

    class Config:
        frozen = True


class ProcessStateData(BaseModel):
    """Immutable process state"""

    state: ProcessState
    process_id: int
    events: list[ProcessEvent]
    last_updated: datetime

    class Config:
        frozen = True


class IOError(Exception):
    """Custom IO error for PTY operations"""

    pass


class PTYError(Exception):
    """Base exception for PTY-related errors"""

    pass


class ConfigurationError(PTYError):
    """Exception for PTY configuration errors"""

    pass


class ProcessError(PTYError):
    """Exception for process-related errors"""

    pass
