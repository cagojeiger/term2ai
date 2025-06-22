"""Tests for PTYWrapper class - TDD approach for Checkpoint 1."""

import os
import signal
import time
from unittest.mock import MagicMock, patch

import pytest
from blessed import Terminal
from term2ai.core.pty_wrapper import PTYWrapper


class TestPTYWrapperBasics:
    """Test basic PTY wrapper functionality."""

    def test_init_default_shell(self) -> None:
        """Test initialization with default shell."""
        wrapper = PTYWrapper()
        assert wrapper.command is not None
        assert wrapper.command in ["/bin/bash", "/bin/sh", "/bin/zsh", "/usr/bin/zsh"]
        assert wrapper.process is None
        assert wrapper.terminal is not None
        assert isinstance(wrapper.terminal, Terminal)

    def test_init_custom_shell(self) -> None:
        """Test initialization with custom shell."""
        wrapper = PTYWrapper(command="/bin/zsh")
        assert wrapper.command == "/bin/zsh"

    def test_init_with_args(self) -> None:
        """Test initialization with command arguments."""
        wrapper = PTYWrapper(command="/bin/bash", args=["-c", "echo test"])
        assert wrapper.command == "/bin/bash"
        assert wrapper.args == ["-c", "echo test"]

    def test_init_with_env(self) -> None:
        """Test initialization with custom environment."""
        custom_env = {"CUSTOM_VAR": "test_value"}
        wrapper = PTYWrapper(env=custom_env)
        assert "CUSTOM_VAR" in wrapper.env
        assert wrapper.env["CUSTOM_VAR"] == "test_value"

    def test_init_with_dimensions(self) -> None:
        """Test initialization with custom terminal dimensions."""
        wrapper = PTYWrapper(rows=40, cols=120)
        assert wrapper.rows == 40
        assert wrapper.cols == 120


class TestPTYWrapperProcessManagement:
    """Test process lifecycle management."""

    def test_start_process(self) -> None:
        """Test starting a PTY process."""
        wrapper = PTYWrapper(command="/bin/echo", args=["hello"])
        wrapper.start()

        assert wrapper.process is not None
        assert wrapper.is_alive()
        assert wrapper.pid > 0

        # Clean up
        wrapper.stop()

    def test_stop_process(self) -> None:
        """Test stopping a PTY process gracefully."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        pid = wrapper.pid
        assert wrapper.is_alive()

        wrapper.stop()
        assert not wrapper.is_alive()
        assert wrapper.process is None

        # Verify process is terminated
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)

    def test_force_stop_process(self) -> None:
        """Test force stopping a PTY process."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        pid = wrapper.pid
        wrapper.stop(force=True)

        assert not wrapper.is_alive()

        # Verify process is killed
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)

    def test_restart_process(self) -> None:
        """Test restarting a PTY process."""
        wrapper = PTYWrapper(command="/bin/echo", args=["test"])
        wrapper.start()

        first_pid = wrapper.pid
        wrapper.restart()

        assert wrapper.is_alive()
        assert wrapper.pid != first_pid

        wrapper.stop()

    def test_process_exit_detection(self) -> None:
        """Test detecting when process exits naturally."""
        wrapper = PTYWrapper(command="/bin/echo", args=["done"])
        wrapper.start()

        # Give process time to complete
        time.sleep(0.1)

        assert not wrapper.is_alive()
        assert wrapper.exit_status == 0


class TestPTYWrapperIO:
    """Test I/O operations."""

    def test_write_to_pty(self) -> None:
        """Test writing data to PTY."""
        wrapper = PTYWrapper(command="/bin/cat")
        wrapper.start()

        test_data = "Hello, PTY!\n"
        bytes_written = wrapper.write(test_data)

        assert bytes_written == len(test_data.encode())

        # Read back the echoed data
        output = wrapper.read(timeout=1.0)
        assert test_data in output

        wrapper.stop()

    def test_read_from_pty(self) -> None:
        """Test reading data from PTY."""
        wrapper = PTYWrapper(command="/bin/echo", args=["test output"])
        wrapper.start()

        output = wrapper.read(timeout=1.0)
        assert "test output" in output

        wrapper.stop()

    def test_read_nonblocking(self) -> None:
        """Test non-blocking read operation."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["1"])
        wrapper.start()

        # Non-blocking read should return empty string if no data
        output = wrapper.read_nonblocking()
        assert output == ""

        wrapper.stop()

    def test_read_with_timeout(self) -> None:
        """Test read with timeout."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        start_time = time.time()
        output = wrapper.read(timeout=0.5)
        elapsed = time.time() - start_time

        assert output == ""
        assert elapsed < 1.0  # Should timeout quickly

        wrapper.stop()

    def test_write_bytes(self) -> None:
        """Test writing raw bytes to PTY."""
        wrapper = PTYWrapper(command="/bin/cat")
        wrapper.start()

        test_bytes = b"\x01\x02\x03\x04"
        bytes_written = wrapper.write_bytes(test_bytes)

        assert bytes_written == len(test_bytes)

        wrapper.stop()

    def test_encoding_handling(self) -> None:
        """Test UTF-8 encoding handling."""
        wrapper = PTYWrapper(command="/bin/cat")
        wrapper.start()

        test_unicode = "Hello 世界! 🌍\n"
        wrapper.write(test_unicode)

        output = wrapper.read(timeout=1.0)
        assert "世界" in output
        assert "🌍" in output

        wrapper.stop()


class TestPTYWrapperContextManager:
    """Test context manager implementation."""

    def test_context_manager_basic(self) -> None:
        """Test basic context manager usage."""
        with PTYWrapper(command="/bin/echo", args=["test"]) as wrapper:
            assert wrapper.is_alive()
            output = wrapper.read(timeout=1.0)
            assert "test" in output

        # Process should be stopped after exiting context
        assert not wrapper.is_alive()

    def test_context_manager_exception_cleanup(self) -> None:
        """Test cleanup on exception in context manager."""
        wrapper = None
        try:
            with PTYWrapper(command="/bin/sleep", args=["10"]) as w:
                wrapper = w
                assert wrapper.is_alive()
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Process should still be cleaned up
        assert wrapper is not None
        assert not wrapper.is_alive()

    def test_context_manager_nested(self) -> None:
        """Test nested context managers."""
        with PTYWrapper(command="/bin/cat") as wrapper1:
            wrapper1.write("outer\n")
            output1 = wrapper1.read(timeout=0.5)

            with PTYWrapper(command="/bin/cat") as wrapper2:
                wrapper2.write("inner\n")
                output2 = wrapper2.read(timeout=0.5)

                assert "outer" in output1
                assert "inner" in output2
                assert wrapper1.is_alive()
                assert wrapper2.is_alive()

            assert wrapper1.is_alive()
            assert not wrapper2.is_alive()

        assert not wrapper1.is_alive()


class TestPTYWrapperBlessedIntegration:
    """Test blessed terminal integration."""

    def test_terminal_initialization(self) -> None:
        """Test blessed Terminal initialization."""
        wrapper = PTYWrapper()
        assert wrapper.terminal is not None
        assert isinstance(wrapper.terminal, Terminal)

    def test_terminal_dimensions_sync(self) -> None:
        """Test terminal dimensions synchronization."""
        wrapper = PTYWrapper(rows=30, cols=100)
        wrapper.start()

        # Terminal should report same dimensions
        assert wrapper.get_terminal_size() == (30, 100)

        wrapper.stop()

    def test_terminal_resize(self) -> None:
        """Test resizing terminal."""
        wrapper = PTYWrapper()
        wrapper.start()

        wrapper.resize(40, 120)
        rows, cols = wrapper.get_terminal_size()

        assert rows == 40
        assert cols == 120

        wrapper.stop()

    def test_terminal_capabilities(self) -> None:
        """Test accessing terminal capabilities."""
        wrapper = PTYWrapper()

        # Should have access to blessed terminal features
        assert hasattr(wrapper.terminal, "clear")
        assert hasattr(wrapper.terminal, "bold")
        assert hasattr(wrapper.terminal, "color")

    @patch("term2ai.core.pty_wrapper.Terminal")
    def test_terminal_fullscreen_mode(self, mock_terminal: MagicMock) -> None:
        """Test fullscreen mode support."""
        mock_term_instance = MagicMock()
        mock_terminal.return_value = mock_term_instance

        wrapper = PTYWrapper()
        wrapper.enter_fullscreen()

        # Verify fullscreen context was entered
        mock_term_instance.fullscreen.__enter__.assert_called_once()

        wrapper.exit_fullscreen()
        mock_term_instance.fullscreen.__exit__.assert_called_once()


class TestPTYWrapperErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_command(self) -> None:
        """Test handling invalid command."""
        wrapper = PTYWrapper(command="/nonexistent/command")

        with pytest.raises(OSError):
            wrapper.start()

    def test_double_start(self) -> None:
        """Test starting already started process."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        with pytest.raises(RuntimeError, match="Process already running"):
            wrapper.start()

        wrapper.stop()

    def test_stop_not_started(self) -> None:
        """Test stopping process that wasn't started."""
        wrapper = PTYWrapper()
        # Should not raise exception
        wrapper.stop()

    def test_write_to_stopped_process(self) -> None:
        """Test writing to stopped process."""
        wrapper = PTYWrapper(command="/bin/cat")

        with pytest.raises(RuntimeError, match="Process not running"):
            wrapper.write("test")

    def test_read_from_stopped_process(self) -> None:
        """Test reading from stopped process."""
        wrapper = PTYWrapper()

        with pytest.raises(RuntimeError, match="Process not running"):
            wrapper.read()


class TestPTYWrapperSignalHandling:
    """Test signal handling capabilities."""

    def test_send_signal(self) -> None:
        """Test sending signals to process."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        # Send interrupt signal
        wrapper.send_signal(signal.SIGINT)
        time.sleep(0.1)

        assert not wrapper.is_alive()

    def test_send_ctrl_c(self) -> None:
        """Test sending Ctrl+C to process."""
        wrapper = PTYWrapper(command="/bin/sleep", args=["10"])
        wrapper.start()

        wrapper.send_ctrl_c()
        time.sleep(0.1)

        assert not wrapper.is_alive()

    def test_send_ctrl_d(self) -> None:
        """Test sending Ctrl+D (EOF) to process."""
        wrapper = PTYWrapper(command="/bin/cat")
        wrapper.start()

        wrapper.send_ctrl_d()
        time.sleep(0.1)

        assert not wrapper.is_alive()


@pytest.mark.integration
class TestPTYWrapperIntegration:
    """Integration tests with real shell commands."""

    def test_interactive_shell_session(self) -> None:
        """Test interactive shell session."""
        with PTYWrapper(command="/bin/bash") as wrapper:
            # Send command
            wrapper.write("echo $USER\n")
            output = wrapper.read(timeout=1.0)

            # Should see the command and output
            assert "echo" in output
            assert os.environ.get("USER", "") in output

    def test_command_with_color_output(self) -> None:
        """Test handling ANSI color codes."""
        with PTYWrapper(command="/bin/ls", args=["--color=always", "/"]) as wrapper:
            output = wrapper.read(timeout=2.0)

            # Should contain ANSI escape sequences
            assert "\033[" in output or "\x1b[" in output

    def test_long_running_process(self) -> None:
        """Test managing long-running process."""
        with PTYWrapper(command="/bin/bash") as wrapper:
            # Start a background process
            wrapper.write("sleep 0.5 &\n")
            wrapper.write("echo started\n")

            output = wrapper.read(timeout=1.0)
            assert "started" in output

            # Check process is still alive
            assert wrapper.is_alive()

    def test_environment_variables(self) -> None:
        """Test custom environment variables."""
        env = {"CUSTOM_VAR": "test_value", "ANOTHER_VAR": "another_value"}

        with PTYWrapper(command="/bin/bash", env=env) as wrapper:
            wrapper.write("echo $CUSTOM_VAR\n")
            output = wrapper.read(timeout=1.0)
            assert "test_value" in output

            wrapper.write("echo $ANOTHER_VAR\n")
            output = wrapper.read(timeout=1.0)
            assert "another_value" in output


@pytest.mark.slow
class TestPTYWrapperPerformance:
    """Performance-related tests."""

    def test_high_throughput_io(self) -> None:
        """Test handling high-throughput I/O."""
        with PTYWrapper(command="/bin/cat") as wrapper:
            # Send large amount of data
            data = "x" * 1000 + "\n"
            for _ in range(100):
                wrapper.write(data)

            # Read it back
            total_output = ""
            start_time = time.time()
            while len(total_output) < 100000 and time.time() - start_time < 5:
                chunk = wrapper.read_nonblocking()
                total_output += chunk
                if not chunk:
                    time.sleep(0.01)

            assert len(total_output) >= 100000

    def test_many_small_writes(self) -> None:
        """Test many small write operations."""
        with PTYWrapper(command="/bin/cat") as wrapper:
            # Send many small chunks
            for i in range(1000):
                wrapper.write(f"{i}\n")

            # Should handle without issues
            output = wrapper.read(timeout=2.0)
            assert "999" in output
