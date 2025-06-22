# term2ai - 함수형 프로그래밍 기반 터미널 래퍼
"""
순수 함수, 모나드 시스템, Effect 관리를 통한 예측 가능하고
테스트 가능한 터미널 래퍼 라이브러리
"""

__version__ = "0.1.0"

from .models import (
    ProcessEvent,
    ProcessState,
    ProcessStateData,
    PTYConfig,
    PTYHandle,
    ShellType,
)
from .monads import IOEffect, Maybe, Result
from .pty_wrapper import (
    PTYWrapper,
    create_pty_effect,
    read_pty_effect,
    write_pty_effect,
)
from .pure_functions import (
    create_pty_config,
    decode_pty_data,
    encode_pty_data,
    fold_process_events,
    update_process_state,
    validate_process_state,
    validate_pty_config,
    validate_shell_command,
)

__all__ = [
    "PTYWrapper",
    "create_pty_effect",
    "read_pty_effect",
    "write_pty_effect",
    "create_pty_config",
    "validate_pty_config",
    "validate_shell_command",
    "decode_pty_data",
    "encode_pty_data",
    "update_process_state",
    "fold_process_events",
    "validate_process_state",
    "PTYConfig",
    "PTYHandle",
    "ProcessEvent",
    "ProcessStateData",
    "ShellType",
    "ProcessState",
    "Result",
    "IOEffect",
    "Maybe",
]
