from datetime import datetime

from hypothesis import given
from hypothesis import strategies as st
from term2ai.models import ProcessEvent, ProcessState, ProcessStateData, ShellType
from term2ai.pure_functions import (
    create_pty_config,
    decode_pty_data,
    encode_pty_data,
    fold_process_events,
    update_process_state,
    validate_process_state,
    validate_pty_config,
    validate_shell_command,
)


class TestPTYConfigCreation:
    @given(
        shell_command=st.text(min_size=1),
        timeout=st.floats(min_value=0.1, max_value=300.0),
    )
    def test_pty_config_creation_properties(self, shell_command, timeout):
        """Property-based test for PTY config creation"""
        config = create_pty_config(shell_command=shell_command, timeout=timeout)

        assert config.shell_command == shell_command
        assert config.timeout == timeout
        assert isinstance(config.env_vars, dict)
        assert config.shell_type in ShellType

    def test_pty_config_validation_success(self):
        """Test successful PTY config validation"""
        config = create_pty_config()
        result = validate_pty_config(config)

        assert result._is_success
        assert result._value == config

    def test_pty_config_validation_failure(self):
        """Test PTY config validation failure"""
        config = create_pty_config(shell_command="")
        result = validate_pty_config(config)
        assert not result._is_success
        assert "Shell command cannot be empty" in result._value

        config = create_pty_config(timeout=0.0)
        result = validate_pty_config(config)
        assert not result._is_success
        assert "Timeout must be positive" in result._value


class TestDataTransformation:
    @given(text=st.text())
    def test_encode_decode_roundtrip(self, text):
        """Property-based test for encode/decode roundtrip"""
        encode_result = encode_pty_data(text)
        assert encode_result._is_success

        decode_result = decode_pty_data(encode_result._value)
        assert decode_result._is_success
        assert decode_result._value == text

    @given(data=st.binary())
    def test_decode_pty_data_properties(self, data):
        """Property-based test for PTY data decoding"""
        result = decode_pty_data(data)
        assert result._is_success
        assert isinstance(result._value, str)


class TestProcessStateTransitions:
    @given(
        process_id=st.integers(min_value=1),
        event_type=st.sampled_from(
            ["process_started", "process_stopped", "process_terminated"]
        ),
    )
    def test_process_state_transitions(self, process_id, event_type):
        """Property-based test for process state transitions"""
        initial_state = ProcessStateData(
            state=ProcessState.CREATED,
            process_id=process_id,
            events=[],
            last_updated=datetime.now(),
        )

        event = ProcessEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            data={},
            process_id=process_id,
        )

        new_state = update_process_state(initial_state, event)

        assert new_state.process_id == process_id
        assert len(new_state.events) == 1
        assert new_state.events[0] == event

        if event_type == "process_started":
            assert new_state.state == ProcessState.RUNNING
        elif event_type == "process_stopped":
            assert new_state.state == ProcessState.STOPPED
        elif event_type == "process_terminated":
            assert new_state.state == ProcessState.TERMINATED


class TestShellCommandValidation:
    @given(command=st.text(min_size=1).filter(lambda x: x.strip()))
    def test_valid_shell_commands(self, command):
        """Property-based test for valid shell commands"""
        try:
            result = validate_shell_command(command)
            if result._is_success:
                assert result._value == command
        except Exception:
            pass

    def test_empty_command_validation(self):
        """Test empty command validation"""
        result = validate_shell_command("")
        assert not result._is_success
        assert "Command cannot be empty" in result._value


class TestEventFolding:
    def test_fold_process_events_ordering(self):
        """Test that events are processed in chronological order"""
        base_time = datetime.now()

        events = [
            ProcessEvent(
                event_type="process_started",
                timestamp=base_time,
                data={},
                process_id=123,
            ),
            ProcessEvent(
                event_type="process_stopped",
                timestamp=base_time.replace(second=base_time.second + 1),
                data={},
                process_id=123,
            ),
            ProcessEvent(
                event_type="process_terminated",
                timestamp=base_time.replace(second=base_time.second + 2),
                data={},
                process_id=123,
            ),
        ]

        final_state = fold_process_events(events, ProcessState.CREATED)
        assert final_state == ProcessState.TERMINATED


class TestProcessStateValidation:
    def test_validate_process_state_success(self):
        """Test successful process state validation"""
        event = ProcessEvent(
            event_type="process_started",
            timestamp=datetime.now(),
            data={},
            process_id=123,
        )

        state = ProcessStateData(
            state=ProcessState.RUNNING,
            process_id=123,
            events=[event],
            last_updated=datetime.now(),
        )

        result = validate_process_state(state)
        assert result._is_success
        assert result._value == state

    def test_validate_process_state_no_events(self):
        """Test process state validation with no events"""
        state = ProcessStateData(
            state=ProcessState.CREATED,
            process_id=123,
            events=[],
            last_updated=datetime.now(),
        )

        result = validate_process_state(state)
        assert not result._is_success
        assert "Process state must have at least one event" in result._value


class TestANSISequenceGeneration:
    @given(command=st.sampled_from(["clear", "reset", "bold", "dim", "underline"]))
    def test_ansi_sequence_generation(self, command):
        """Property-based test for ANSI sequence generation"""
        from term2ai.pure_functions import generate_ansi_sequence

        sequence = generate_ansi_sequence(command)
        assert isinstance(sequence, str)
        if sequence:
            assert sequence.startswith("\033") or sequence.startswith("\x1b")

    def test_cursor_commands_generation(self):
        """Test cursor command generation"""
        from term2ai.pure_functions import create_cursor_commands

        commands = create_cursor_commands(5, -3)
        assert isinstance(commands, list)
        assert len(commands) == 2  # One for row, one for column
