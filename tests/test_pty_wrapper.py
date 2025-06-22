from unittest.mock import MagicMock, patch

from term2ai.models import ShellType
from term2ai.pty_wrapper import (
    PTYWrapper,
    create_pty_effect,
    read_pty_effect,
    write_pty_effect,
)
from term2ai.pure_functions import create_pty_config


class TestPTYWrapper:
    """Integration tests for PTY wrapper"""

    def test_pty_config_creation(self):
        """Test PTY configuration creation"""
        config = create_pty_config(
            shell_command="/bin/bash", shell_type=ShellType.BASH, timeout=30.0
        )

        assert config.shell_command == "/bin/bash"
        assert config.shell_type == ShellType.BASH
        assert config.timeout == 30.0

    @patch("ptyprocess.PtyProcess.spawn")
    def test_pty_creation_effect(self, mock_spawn):
        """Test PTY creation with mocked ptyprocess"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.fd = 3
        mock_spawn.return_value = mock_process

        config = create_pty_config()
        create_effect = create_pty_effect(config)
        result = create_effect.run()

        assert result._is_success
        assert result._value.process_id == 12345
        assert result._value.fd == 3

    @patch("os.read")
    def test_pty_read_effect(self, mock_read):
        """Test PTY reading with mocked os.read"""
        mock_read.return_value = b"test output"

        config = create_pty_config()
        from datetime import datetime

        from term2ai.models import PTYHandle

        handle = PTYHandle(
            process_id=12345, fd=3, created_at=datetime.now(), config=config
        )

        read_effect = read_pty_effect(handle)
        result = read_effect.run()

        assert result._is_success
        assert result._value == b"test output"

    @patch("os.write")
    def test_pty_write_effect(self, mock_write):
        """Test PTY writing with mocked os.write"""
        mock_write.return_value = 11  # bytes written

        config = create_pty_config()
        from datetime import datetime

        from term2ai.models import PTYHandle

        handle = PTYHandle(
            process_id=12345, fd=3, created_at=datetime.now(), config=config
        )

        write_effect = write_pty_effect(handle, "test input\n")
        result = write_effect.run()

        assert result._is_success
        assert result._value == 11

    @patch("ptyprocess.PtyProcess.spawn")
    @patch("os.close")
    def test_pty_wrapper_context_manager(self, mock_close, mock_spawn):
        """Test PTY wrapper as context manager"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.fd = 3
        mock_spawn.return_value = mock_process

        config = create_pty_config()

        with PTYWrapper(config) as pty:
            assert pty.handle is not None
            assert pty.handle.process_id == 12345
            assert pty.is_active()

        mock_close.assert_called_once_with(3)

    @patch("ptyprocess.PtyProcess.spawn")
    @patch("os.read")
    def test_pty_wrapper_read(self, mock_read, mock_spawn):
        """Test PTY wrapper read method"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.fd = 3
        mock_spawn.return_value = mock_process
        mock_read.return_value = b"hello world"

        config = create_pty_config()

        with PTYWrapper(config) as pty:
            result = pty.read()
            assert result._is_success
            assert result._value == "hello world"

    @patch("ptyprocess.PtyProcess.spawn")
    @patch("os.write")
    def test_pty_wrapper_write(self, mock_write, mock_spawn):
        """Test PTY wrapper write method"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.fd = 3
        mock_spawn.return_value = mock_process
        mock_write.return_value = 11

        config = create_pty_config()

        with PTYWrapper(config) as pty:
            result = pty.write("test input\n")
            assert result._is_success
            assert result._value == 11

    def test_pty_wrapper_not_initialized(self):
        """Test PTY wrapper methods when not initialized"""
        config = create_pty_config()
        pty = PTYWrapper(config)

        result = pty.read()
        assert not result._is_success
        assert "PTY not initialized" in str(result._value)

        result = pty.write("test")
        assert not result._is_success
        assert "PTY not initialized" in str(result._value)


class TestPTYEffectChaining:
    """Test PTY effect chaining and composition"""

    @patch("ptyprocess.PtyProcess.spawn")
    @patch("os.write")
    @patch("os.read")
    def test_effect_chaining(self, mock_read, mock_write, mock_spawn):
        """Test chaining multiple PTY effects"""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.fd = 3
        mock_spawn.return_value = mock_process
        mock_write.return_value = 5
        mock_read.return_value = b"echo"

        config = create_pty_config()

        create_effect = create_pty_effect(config)

        def write_then_read(handle):
            write_effect = write_pty_effect(handle, "echo\n")
            return write_effect.bind(lambda _: read_pty_effect(handle))

        create_result = create_effect.run()
        assert create_result._is_success

        handle = create_result._value
        final_result = write_then_read(handle).run()
        assert final_result._is_success
        assert final_result._value == b"echo"


class TestErrorHandling:
    """Test error handling in PTY operations"""

    @patch("ptyprocess.PtyProcess.spawn")
    def test_pty_creation_failure(self, mock_spawn):
        """Test PTY creation failure handling"""
        mock_spawn.side_effect = Exception("Failed to spawn process")

        config = create_pty_config()
        create_effect = create_pty_effect(config)
        result = create_effect.run()

        assert not result._is_success
        assert "Failed to create PTY" in str(result._value)

    @patch("os.read")
    def test_pty_read_failure(self, mock_read):
        """Test PTY read failure handling"""
        mock_read.side_effect = OSError("Read failed")

        config = create_pty_config()
        from datetime import datetime

        from term2ai.models import PTYHandle

        handle = PTYHandle(
            process_id=12345, fd=3, created_at=datetime.now(), config=config
        )

        read_effect = read_pty_effect(handle)
        result = read_effect.run()

        assert not result._is_success
        assert "Failed to read from PTY" in str(result._value)

    @patch("os.write")
    def test_pty_write_failure(self, mock_write):
        """Test PTY write failure handling"""
        mock_write.side_effect = OSError("Write failed")

        config = create_pty_config()
        from datetime import datetime

        from term2ai.models import PTYHandle

        handle = PTYHandle(
            process_id=12345, fd=3, created_at=datetime.now(), config=config
        )

        write_effect = write_pty_effect(handle, "test")
        result = write_effect.run()

        assert not result._is_success
        assert "Failed to write to PTY" in str(result._value)
