import os
from datetime import datetime
from typing import Any

import ptyprocess

from .models import (
    IOError,
    PTYConfig,
    PTYHandle,
)
from .monads import IOEffect, Result
from .pure_functions import decode_pty_data, encode_pty_data, validate_pty_config


def create_pty_effect(config: PTYConfig) -> IOEffect[Result[PTYHandle, IOError]]:
    """IOEffect to create a PTY process"""

    def create_pty() -> Result[PTYHandle, IOError]:
        try:
            validation_result = validate_pty_config(config)
            if not validation_result._is_success:
                return Result.failure(IOError(validation_result._value))

            process = ptyprocess.PtyProcess.spawn(
                [config.shell_command],
                env=dict(os.environ, **config.env_vars),
                cwd=config.working_directory,
            )

            handle = PTYHandle(
                process_id=process.pid,
                fd=process.fd,
                created_at=datetime.now(),
                config=config,
            )

            return Result.success(handle)

        except Exception as e:
            return Result.failure(IOError(f"Failed to create PTY: {e}"))

    return IOEffect(create_pty)


def read_pty_effect(handle: PTYHandle) -> IOEffect[Result[bytes, IOError]]:
    """IOEffect to read from PTY"""

    def read_pty() -> Result[bytes, IOError]:
        try:
            data = os.read(handle.fd, 4096)
            return Result.success(data)
        except Exception as e:
            return Result.failure(IOError(f"Failed to read from PTY: {e}"))

    return IOEffect(read_pty)


def write_pty_effect(handle: PTYHandle, data: str) -> IOEffect[Result[int, IOError]]:
    """IOEffect to write to PTY"""

    def write_pty() -> Result[int, IOError]:
        try:
            encode_result = encode_pty_data(data)
            if not encode_result._is_success:
                return Result.failure(IOError(encode_result._value))

            bytes_data = encode_result.unwrap()
            bytes_written = os.write(handle.fd, bytes_data)
            return Result.success(bytes_written)
        except Exception as e:
            return Result.failure(IOError(f"Failed to write to PTY: {e}"))

    return IOEffect(write_pty)


def close_pty_effect(handle: PTYHandle) -> IOEffect[Result[None, IOError]]:
    """IOEffect to close PTY"""

    def close_pty() -> Result[None, IOError]:
        try:
            os.close(handle.fd)
            return Result.success(None)
        except Exception as e:
            return Result.failure(IOError(f"Failed to close PTY: {e}"))

    return IOEffect(close_pty)


def init_terminal_effect() -> IOEffect[Result[dict, IOError]]:
    """IOEffect to initialize terminal"""

    def init_terminal() -> Result[dict, IOError]:
        try:
            from .pure_functions import analyze_terminal_capabilities

            capabilities = analyze_terminal_capabilities()
            return Result.success(capabilities)
        except Exception as e:
            return Result.failure(IOError(f"Failed to initialize terminal: {e}"))

    return IOEffect(init_terminal)


def apply_terminal_changes_effect(changes: dict) -> IOEffect[Result[None, IOError]]:
    """IOEffect to apply terminal changes"""

    def apply_changes() -> Result[None, IOError]:
        try:
            if not isinstance(changes, dict):
                return Result.failure(IOError("Changes must be a dictionary"))  # type: ignore[unreachable]
            return Result.success(None)
        except Exception as e:
            return Result.failure(IOError(f"Failed to apply terminal changes: {e}"))

    return IOEffect(apply_changes)


class PTYWrapper:
    """Context manager for PTY operations using functional programming patterns"""

    def __init__(self, config: PTYConfig):
        self.config = config
        self.handle: PTYHandle | None = None

    def __enter__(self) -> "PTYWrapper":
        """Enter context manager - create PTY"""
        create_effect = create_pty_effect(self.config)
        result = create_effect.run()

        if result._is_success:
            self.handle = result.unwrap()
            return self
        raise Exception(str(result._value))

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - close PTY"""
        if self.handle:
            close_effect = close_pty_effect(self.handle)
            close_result = close_effect.run()
            if not close_result._is_success:
                print(f"Warning: Failed to close PTY: {close_result._value}")

    def read(self) -> Result[str, IOError]:
        """Read decoded data from PTY"""
        if not self.handle:
            return Result.failure(IOError("PTY not initialized"))

        read_effect = read_pty_effect(self.handle)
        read_result = read_effect.run()

        if read_result._is_success:
            bytes_data = read_result.unwrap()
            decode_result = decode_pty_data(bytes_data)
            if decode_result._is_success:
                return Result.success(decode_result._value)
            return Result.failure(IOError(decode_result._value))
        error = read_result.unwrap_err()
        return Result.failure(error)

    def write(self, data: str) -> Result[int, IOError]:
        """Write data to PTY"""
        if not self.handle:
            return Result.failure(IOError("PTY not initialized"))

        write_effect = write_pty_effect(self.handle, data)
        return write_effect.run()

    def get_handle(self) -> PTYHandle | None:
        """Get the current PTY handle"""
        return self.handle

    def is_active(self) -> bool:
        """Check if PTY is active"""
        return self.handle is not None


def sequence_pty_effects(
    effects: list[IOEffect[Result[Any, IOError]]],
) -> IOEffect[Result[list, IOError]]:
    """Sequence multiple PTY effects"""

    def run_sequence() -> Result[list, IOError]:
        results = []
        for effect in effects:
            result = effect.run()
            if result._is_success:
                results.append(result._value)
            else:
                return Result.failure(result._value)
        return Result.success(results)

    return IOEffect(run_sequence)


def chain_pty_operations(*operations: Any) -> IOEffect[Result[Any, IOError]]:
    """Chain multiple PTY operations"""

    def run_chain() -> Result[Any, IOError]:
        result: Any = None
        for operation in operations:
            if callable(operation):
                effect_result = operation()
                if hasattr(effect_result, "run"):
                    result = effect_result.run()
                    if not result._is_success:
                        return result  # type: ignore[no-any-return]
                else:
                    result = effect_result
            else:
                result = operation
        return Result.success(result) if result is not None else Result.success(None)

    return IOEffect(run_chain)
