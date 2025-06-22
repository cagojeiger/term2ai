"""PTY (Pseudo-Terminal) wrapper with blessed integration for terminal control."""

import os
import signal
import time
from pathlib import Path
from typing import Any

import ptyprocess
from blessed import Terminal
from ptyprocess import PtyProcess


class PTYWrapper:
    """Wrapper for pseudo-terminal operations with blessed integration.

    This class provides a high-level interface for creating and managing
    pseudo-terminal processes with advanced terminal control capabilities
    through blessed integration.

    Attributes:
        command: Command to execute in the PTY
        args: Arguments for the command
        env: Environment variables for the process
        rows: Terminal height in rows
        cols: Terminal width in columns
        terminal: Blessed Terminal instance for advanced control
        process: The underlying PTY process
    """

    def __init__(
        self,
        command: str | None = None,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        rows: int = 24,
        cols: int = 80,
    ) -> None:
        """Initialize PTY wrapper.

        Args:
            command: Command to execute (defaults to user's shell)
            args: Command arguments
            env: Environment variables (inherits current env by default)
            rows: Terminal height in rows
            cols: Terminal width in columns
        """
        self.command = command or self._get_default_shell()
        self.args = args or []
        self.rows = rows
        self.cols = cols

        # Set up environment
        self.env: dict[str, str] = dict(os.environ)
        if env:
            self.env.update(env)

        # Initialize blessed Terminal
        self.terminal = Terminal()

        # Process management
        self.process: PtyProcess | None = None
        self._in_fullscreen = False
        self._fullscreen_context: Any | None = None

    def _get_default_shell(self) -> str:
        """Get the default shell for the current user."""
        # Try common shell paths
        shells = ["/bin/bash", "/usr/bin/zsh", "/bin/zsh", "/bin/sh"]

        # Check SHELL environment variable first
        user_shell = os.environ.get("SHELL")
        if user_shell and Path(user_shell).exists():
            return user_shell

        # Fall back to checking common shells
        for shell in shells:
            if Path(shell).exists():
                return shell

        # Last resort
        return "/bin/sh"

    def start(self) -> None:
        """Start the PTY process.

        Raises:
            RuntimeError: If process is already running
            OSError: If command cannot be executed
        """
        if self.process is not None and self.is_alive():
            raise RuntimeError("Process already running")

        # Prepare command line
        cmd = [self.command] + self.args if self.args else [self.command]

        # Spawn the process
        self.process = PtyProcess.spawn(
            cmd,
            env=self.env,
            dimensions=(self.rows, self.cols),
        )

    def stop(self, force: bool = False) -> None:
        """Stop the PTY process.

        Args:
            force: If True, forcefully kill the process
        """
        if self.process is None:
            return

        if not self.is_alive():
            self.process = None
            return

        try:
            if force:
                self.process.kill(signal.SIGKILL)
            else:
                # Try graceful termination first
                self.process.terminate()

                # Wait a bit for process to exit
                for _ in range(10):
                    if not self.is_alive():
                        break
                    time.sleep(0.1)

                # Force kill if still alive
                if self.is_alive():
                    self.process.kill(signal.SIGKILL)
        except ProcessLookupError:
            # Process already dead
            pass
        finally:
            self.process = None

    def restart(self) -> None:
        """Restart the PTY process."""
        self.stop()
        self.start()

    def is_alive(self) -> bool:
        """Check if the process is still running.

        Returns:
            True if process is alive, False otherwise
        """
        if self.process is None:
            return False
        return bool(self.process.isalive())

    @property
    def pid(self) -> int:
        """Get the process ID.

        Returns:
            Process ID or -1 if no process
        """
        if self.process is None:
            return -1
        return int(self.process.pid)

    @property
    def exit_status(self) -> int | None:
        """Get the exit status of the process.

        Returns:
            Exit status or None if process hasn't exited
        """
        if self.process is None:
            return None

        if self.is_alive():
            return None

        exitstatus = self.process.exitstatus
        return int(exitstatus) if exitstatus is not None else None

    def write(self, data: str) -> int:
        """Write string data to the PTY.

        Args:
            data: String data to write

        Returns:
            Number of bytes written

        Raises:
            RuntimeError: If process is not running
        """
        if self.process is None or not self.is_alive():
            raise RuntimeError("Process not running")

        encoded = data.encode("utf-8")
        self.process.write(encoded)
        return len(encoded)

    def write_bytes(self, data: bytes) -> int:
        """Write raw bytes to the PTY.

        Args:
            data: Bytes to write

        Returns:
            Number of bytes written

        Raises:
            RuntimeError: If process is not running
        """
        if self.process is None or not self.is_alive():
            raise RuntimeError("Process not running")

        self.process.write(data)
        return len(data)

    def read(self, size: int = 4096, timeout: float | None = None) -> str:
        """Read data from the PTY with optional timeout.

        Args:
            size: Maximum number of bytes to read
            timeout: Timeout in seconds (None for blocking)

        Returns:
            String data read from PTY

        Raises:
            RuntimeError: If process is not running
        """
        if self.process is None:
            raise RuntimeError("Process not running")

        try:
            if timeout is not None:
                # Use read_nonblocking with timeout
                data = self.process.read_nonblocking(size, timeout)
            else:
                # Blocking read
                data = self.process.read(size)

            return str(data.decode("utf-8", errors="replace"))
        except ptyprocess.TIMEOUT:
            return ""
        except ptyprocess.EOF:
            return ""

    def read_nonblocking(self, size: int = 4096) -> str:
        """Read available data without blocking.

        Args:
            size: Maximum number of bytes to read

        Returns:
            String data read from PTY (empty if no data available)

        Raises:
            RuntimeError: If process is not running
        """
        if self.process is None:
            raise RuntimeError("Process not running")

        try:
            data = self.process.read_nonblocking(size, timeout=0)
            return str(data.decode("utf-8", errors="replace"))
        except ptyprocess.TIMEOUT:
            return ""
        except ptyprocess.EOF:
            return ""

    def send_signal(self, sig: int) -> None:
        """Send a signal to the process.

        Args:
            sig: Signal number to send
        """
        if self.process is not None and self.is_alive():
            self.process.kill(sig)

    def send_ctrl_c(self) -> None:
        """Send Ctrl+C (SIGINT) to the process."""
        if self.process is not None and self.is_alive():
            self.process.sendcontrol("c")

    def send_ctrl_d(self) -> None:
        """Send Ctrl+D (EOF) to the process."""
        if self.process is not None and self.is_alive():
            self.process.sendeof()

    def get_terminal_size(self) -> tuple[int, int]:
        """Get current terminal size.

        Returns:
            Tuple of (rows, cols)
        """
        if self.process is not None:
            size = self.process.getwinsize()
            return (int(size[0]), int(size[1]))
        return (self.rows, self.cols)

    def resize(self, rows: int, cols: int) -> None:
        """Resize the terminal.

        Args:
            rows: New number of rows
            cols: New number of columns
        """
        self.rows = rows
        self.cols = cols

        if self.process is not None and self.is_alive():
            self.process.setwinsize(rows, cols)

    def enter_fullscreen(self) -> None:
        """Enter fullscreen mode using blessed."""
        if not self._in_fullscreen:
            self._fullscreen_context = self.terminal.fullscreen()
            self._fullscreen_context.__enter__()
            self._in_fullscreen = True

    def exit_fullscreen(self) -> None:
        """Exit fullscreen mode."""
        if self._in_fullscreen and self._fullscreen_context:
            self._fullscreen_context.__exit__(None, None, None)
            self._in_fullscreen = False
            self._fullscreen_context = None

    def __enter__(self) -> "PTYWrapper":
        """Enter context manager."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit context manager and clean up resources."""
        # Exit fullscreen if active
        if self._in_fullscreen:
            self.exit_fullscreen()

        # Stop the process
        self.stop()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        # Ensure process is stopped
        if hasattr(self, "process") and self.process is not None:
            self.stop(force=True)

        # Ensure fullscreen is exited
        if hasattr(self, "_in_fullscreen") and self._in_fullscreen:
            self.exit_fullscreen()
