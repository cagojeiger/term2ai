import os
import shlex
from pathlib import Path
from typing import Any

from .models import ProcessEvent, ProcessState, ProcessStateData, PTYConfig, ShellType
from .monads import Result


def create_pty_config(
    shell_command: str = "/bin/bash",
    shell_type: ShellType = ShellType.BASH,
    env_vars: dict[str, str] | None = None,
    working_directory: str | None = None,
    timeout: float = 30.0,
) -> PTYConfig:
    """Pure function to create PTY configuration"""
    return PTYConfig(
        shell_command=shell_command,
        shell_type=shell_type,
        env_vars=env_vars or {},
        working_directory=working_directory,
        timeout=timeout,
    )


def validate_pty_config(config: PTYConfig) -> Result[PTYConfig, str]:
    """Pure function to validate PTY configuration"""
    if not config.shell_command:
        return Result.failure("Shell command cannot be empty")

    if config.timeout <= 0:
        return Result.failure("Timeout must be positive")

    if config.working_directory and not Path(config.working_directory).exists():
        return Result.failure(
            f"Working directory does not exist: {config.working_directory}"
        )

    return Result.success(config)


def validate_shell_command(command: str) -> Result[str, str]:
    """Pure function to validate shell command"""
    if not command.strip():
        return Result.failure("Command cannot be empty")

    try:
        shlex.split(command)
        return Result.success(command)
    except ValueError as e:
        return Result.failure(f"Invalid shell command: {e}")


def decode_pty_data(data: bytes) -> Result[str, str]:
    """Pure function to decode PTY data"""
    try:
        return Result.success(data.decode("utf-8", errors="replace"))
    except Exception as e:
        return Result.failure(f"Failed to decode data: {e}")


def encode_pty_data(text: str) -> Result[bytes, str]:
    """Pure function to encode PTY data"""
    try:
        return Result.success(text.encode("utf-8"))
    except Exception as e:
        return Result.failure(f"Failed to encode text: {e}")


def update_process_state(
    current_state: ProcessStateData, event: ProcessEvent
) -> ProcessStateData:
    """Pure function to update process state"""
    new_events = current_state.events + [event]

    new_state = current_state.state
    if event.event_type == "process_started":
        new_state = ProcessState.RUNNING
    elif event.event_type == "process_stopped":
        new_state = ProcessState.STOPPED
    elif event.event_type == "process_terminated":
        new_state = ProcessState.TERMINATED

    return ProcessStateData(
        state=new_state,
        process_id=current_state.process_id,
        events=new_events,
        last_updated=event.timestamp,
    )


def fold_process_events(
    events: list[ProcessEvent], initial_state: ProcessState
) -> ProcessState:
    """Pure function to reconstruct state from events"""
    current_state = initial_state

    for event in sorted(events, key=lambda e: e.timestamp):
        if event.event_type == "process_started":
            current_state = ProcessState.RUNNING
        elif event.event_type == "process_stopped":
            current_state = ProcessState.STOPPED
        elif event.event_type == "process_terminated":
            current_state = ProcessState.TERMINATED

    return current_state


def validate_process_state(state: ProcessStateData) -> Result[ProcessStateData, str]:
    """Pure function to validate process state"""
    if not state.events:
        return Result.failure("Process state must have at least one event")

    sorted_events = sorted(state.events, key=lambda e: e.timestamp)
    if sorted_events != state.events:
        return Result.failure("Events are not in chronological order")

    return Result.success(state)


def analyze_terminal_capabilities() -> dict[str, Any]:
    """Pure function to analyze terminal capabilities"""
    return {
        "colors": os.getenv("TERM", "").find("color") != -1,
        "unicode": os.getenv("LANG", "").find("UTF") != -1,
        "term_type": os.getenv("TERM", "unknown"),
        "columns": int(os.getenv("COLUMNS", "80")),
        "lines": int(os.getenv("LINES", "24")),
    }


def generate_ansi_sequence(command: str, *args: Any) -> str:
    """Pure function to generate ANSI escape sequences"""
    sequences: dict[str, Any] = {
        "clear": "\033[2J\033[H",
        "cursor_up": lambda n: f"\033[{n}A",
        "cursor_down": lambda n: f"\033[{n}B",
        "cursor_right": lambda n: f"\033[{n}C",
        "cursor_left": lambda n: f"\033[{n}D",
        "cursor_position": lambda row, col: f"\033[{row};{col}H",
        "erase_line": "\033[K",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "underline": "\033[4m",
        "blink": "\033[5m",
        "reverse": "\033[7m",
        "hidden": "\033[8m",
    }

    if command not in sequences:
        return ""

    sequence = sequences[command]
    if callable(sequence):
        return str(sequence(*args))
    return str(sequence)


def create_cursor_commands(row: int, col: int) -> list[str]:
    """Pure function to create cursor control commands"""
    commands = []

    if row > 0:
        commands.append(generate_ansi_sequence("cursor_down", row))
    elif row < 0:
        commands.append(generate_ansi_sequence("cursor_up", abs(row)))

    if col > 0:
        commands.append(generate_ansi_sequence("cursor_right", col))
    elif col < 0:
        commands.append(generate_ansi_sequence("cursor_left", abs(col)))

    return commands


def recover_from_error(
    error: str, recovery_strategy: str = "default"
) -> Result[str, str]:
    """Pure function for error recovery strategies"""
    strategies = {
        "default": "Attempting default recovery",
        "retry": "Preparing for retry operation",
        "fallback": "Using fallback configuration",
        "abort": "Aborting operation safely",
    }

    if recovery_strategy not in strategies:
        return Result.failure(f"Unknown recovery strategy: {recovery_strategy}")

    recovery_message = strategies[recovery_strategy]
    return Result.success(f"{recovery_message} for error: {error}")


def validate_environment_variables(
    env_vars: dict[str, str],
) -> Result[dict[str, str], str]:
    """Pure function to validate environment variables"""
    if not isinstance(env_vars, dict):
        return Result.failure("Environment variables must be a dictionary")  # type: ignore[unreachable]

    for key, value in env_vars.items():
        if not isinstance(key, str) or not isinstance(value, str):
            return Result.failure(  # type: ignore[unreachable]
                f"Environment variable key and value must be strings: {key}={value}"
            )
        if not key:
            return Result.failure("Environment variable key cannot be empty")

    return Result.success(env_vars)


def merge_configurations(
    base_config: PTYConfig, override_config: dict[str, Any]
) -> Result[PTYConfig, str]:
    """Pure function to merge PTY configurations"""
    try:
        config_dict = base_config.dict()

        for key, value in override_config.items():
            if key not in config_dict:
                return Result.failure(f"Unknown configuration key: {key}")
            config_dict[key] = value

        new_config = PTYConfig(**config_dict)
        return Result.success(new_config)
    except Exception as e:
        return Result.failure(f"Failed to merge configurations: {e}")
