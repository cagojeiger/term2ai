# 함수형 API 설계 문서

## 개요
term2ai의 API는 **함수형 프로그래밍 패러다임**을 기반으로 설계되어 순수 함수, 모나드, Effect 시스템을 통한 명확하고 합성 가능한 인터페이스를 제공합니다. 이 문서는 함수형 API 설계 원칙과 구체적인 함수 시그니처를 설명합니다.

## 함수형 API 설계 원칙

### 1. 순수성 (Purity)
- 모든 비즈니스 로직은 순수 함수로 구현
- 동일한 입력에 대해 항상 동일한 출력 보장
- 부작용은 Effect 시스템을 통해 명시적으로 분리

### 2. 타입 안전성 및 모나드 활용
- Result 모나드로 에러 처리
- Maybe 모나드로 null 안전성
- IOEffect 모나드로 부작용 관리
- 컴파일 타임 에러 감지

### 3. 합성성 (Composability)
- 작은 함수들의 합성으로 복잡한 기능 구현
- 파이프라인과 체이닝을 통한 데이터 변환
- 모나드 법칙을 통한 안전한 합성

### 4. 불변성 (Immutability)
- 모든 데이터 구조는 불변
- 상태 변경은 새로운 인스턴스 생성
- 동시성 안전성 자동 보장

### 5. 명시적 부작용 관리
- I/O 작업을 IOEffect로 캡슐화
- 순수 함수와 부작용 명확히 분리
- Effect 합성을 통한 복잡한 I/O 작업

## 함수형 API 모듈

### 1. PTY 처리 순수 함수 API

#### PTY 설정 및 생성 함수
```python
# 순수 함수: PTY 설정 생성
def create_pty_config(
    shell: str = "/bin/bash",
    env: dict[str, str] | None = None,
    working_dir: str | None = None
) -> PTYConfig:
    """
    PTY 설정을 생성하는 순수 함수

    Args:
        shell: 실행할 쉘 경로
        env: 환경 변수 딕셔너리
        working_dir: 작업 디렉토리

    Returns:
        불변 PTY 설정 객체
    """

# Effect: PTY 프로세스 생성
def spawn_pty_effect(config: PTYConfig) -> IOEffect[Result[PTYHandle, PTYError]]:
    """
    PTY 프로세스를 생성하는 Effect

    Args:
        config: PTY 설정

    Returns:
        PTY 핸들을 반환하는 Effect (성공/실패 포함)
    """

# 순수 함수: PTY 상태 검증
def validate_pty_handle(handle: PTYHandle) -> Result[PTYHandle, ValidationError]:
    """
    PTY 핸들의 유효성을 검증하는 순수 함수

    Args:
        handle: 검증할 PTY 핸들

    Returns:
        검증된 핸들 또는 에러
    """
```

#### PTY I/O 함수형 API
```python
# Effect: PTY 읽기
def read_pty_effect(handle: PTYHandle, size: int = 1024) -> IOEffect[Result[bytes, IOError]]:
    """
    PTY에서 데이터를 읽는 Effect

    Args:
        handle: PTY 핸들
        size: 읽을 바이트 수

    Returns:
        읽은 데이터 또는 에러를 포함하는 Effect
    """

# Effect: PTY 쓰기
def write_pty_effect(handle: PTYHandle, data: str) -> IOEffect[Result[int, IOError]]:
    """
    PTY에 데이터를 쓰는 Effect

    Args:
        handle: PTY 핸들
        data: 쓸 데이터

    Returns:
        쓰여진 바이트 수 또는 에러를 포함하는 Effect
    """

# 순수 함수: 데이터 변환
def decode_pty_data(data: bytes) -> Result[str, DecodeError]:
    """
    PTY 바이트 데이터를 문자열로 디코딩하는 순수 함수

    Args:
        data: 디코딩할 바이트 데이터

    Returns:
        디코딩된 문자열 또는 에러
    """

# Effect 합성을 통한 고수준 API
def read_and_decode_pty(handle: PTYHandle, size: int = 1024) -> IOEffect[Result[str, PTYError]]:
    """
    PTY 읽기와 디코딩을 합성한 Effect

    Returns:
        디코딩된 문자열 또는 에러
    """
    return (read_pty_effect(handle, size)
            .bind(lambda result:
                  result.bind(decode_pty_data)
                  .map_err(PTYError.from_decode_error)))
```

### 2. 이벤트 스트림 API

#### 비동기 스트림 생성 함수
```python
# 순수 함수: 스트림 설정 생성
def create_stream_config(
    buffer_size: int = 1024,
    timeout: float | None = None,
    backpressure_limit: int = 1000
) -> StreamConfig:
    """
    스트림 설정을 생성하는 순수 함수

    Args:
        buffer_size: 버퍼 크기
        timeout: 타임아웃 (초)
        backpressure_limit: 백프레셔 한계

    Returns:
        불변 스트림 설정 객체
    """

# Effect: 키보드 이벤트 스트림 생성
def create_keyboard_stream_effect() -> IOEffect[AsyncStream[KeyboardEvent]]:
    """
    키보드 이벤트 스트림을 생성하는 Effect

    Returns:
        키보드 이벤트 스트림을 반환하는 Effect
    """

# Effect: PTY 출력 스트림 생성
def create_pty_stream_effect(handle: PTYHandle, config: StreamConfig) -> IOEffect[AsyncStream[PTYEvent]]:
    """
    PTY 출력 스트림을 생성하는 Effect

    Args:
        handle: PTY 핸들
        config: 스트림 설정

    Returns:
        PTY 이벤트 스트림을 반환하는 Effect
    """
```

#### 스트림 변환 순수 함수
```python
# 순수 함수: 스트림 병합
def merge_streams[T](streams: list[AsyncStream[T]]) -> AsyncStream[T]:
    """
    여러 스트림을 하나로 병합하는 순수 함수

    Args:
        streams: 병합할 스트림 리스트

    Returns:
        병합된 통합 스트림
    """

# 순수 함수: 스트림 필터링
def filter_stream[T](
    stream: AsyncStream[T],
    predicate: Callable[[T], bool]
) -> AsyncStream[T]:
    """
    스트림을 필터링하는 순수 함수

    Args:
        stream: 원본 스트림
        predicate: 필터링 조건

    Returns:
        필터링된 스트림
    """

# 순수 함수: 스트림 변환
def map_stream[T, U](
    stream: AsyncStream[T],
    transform: Callable[[T], U]
) -> AsyncStream[U]:
    """
    스트림의 각 요소를 변환하는 순수 함수

    Args:
        stream: 원본 스트림
        transform: 변환 함수

    Returns:
        변환된 스트림
    """

# 순수 함수: 스트림 폴드 (상태 누적)
def scan_stream[T, S](
    stream: AsyncStream[T],
    initial_state: S,
    accumulator: Callable[[S, T], S]
) -> AsyncStream[S]:
    """
    스트림을 스캔하여 상태를 누적하는 순수 함수

    Args:
        stream: 원본 스트림
        initial_state: 초기 상태
        accumulator: 상태 누적 함수

    Returns:
        상태가 누적된 스트림
    """
```

#### 스트림 파이프라인 합성
```python
# 함수 합성을 통한 복잡한 스트림 처리
def create_terminal_event_pipeline(
    pty_handle: PTYHandle
) -> IOEffect[AsyncStream[ProcessedTerminalEvent]]:
    """
    터미널 이벤트 처리 파이프라인을 생성

    Args:
        pty_handle: PTY 핸들

    Returns:
        처리된 터미널 이벤트 스트림을 반환하는 Effect
    """
    return (create_pty_stream_effect(pty_handle, StreamConfig.default())
            .map(lambda pty_stream:
                 pty_stream
                 .filter(is_relevant_event)
                 .map(parse_terminal_data)
                 .map(validate_event)
                 .scan(ProcessedTerminalEvent.initial(), accumulate_state)))
```

### 3. 터미널 상태 관리 API

#### TerminalState 클래스
```python
class TerminalState:
    """터미널 상태 관리 클래스"""

    def __init__(self, fd: int) -> None:
        """
        터미널 상태 관리자 초기화

        Args:
            fd: 터미널 파일 디스크립터
        """

    def set_mode(self, mode: TerminalMode) -> None:
        """
        터미널 모드 설정

        Args:
            mode: 설정할 터미널 모드
        """

    def get_mode(self) -> TerminalMode:
        """현재 터미널 모드 반환"""

    def set_size(self, rows: int, cols: int) -> None:
        """
        터미널 크기 설정

        Args:
            rows: 행 수
            cols: 열 수
        """

    def get_size(self) -> Tuple[int, int]:
        """터미널 크기 반환 (행, 열)"""

    def get_cursor_position(self) -> Tuple[int, int]:
        """커서 위치 반환 (행, 열)"""
```

### 4. ANSI 파서 API

#### ANSIParser 클래스
```python
class ANSIParser:
    """ANSI 이스케이프 시퀀스 파서"""

    def parse(self, data: str) -> List[ANSISequence]:
        """
        ANSI 시퀀스 파싱

        Args:
            data: 파싱할 문자열

        Returns:
            파싱된 ANSI 시퀀스 목록
        """

    def parse_incremental(self, data: str) -> Iterator[ANSISequence]:
        """
        점진적 ANSI 시퀀스 파싱

        Args:
            data: 파싱할 문자열 조각

        Yields:
            파싱된 ANSI 시퀀스
        """

    def reset_state(self) -> None:
        """파서 상태 초기화"""
```

### 5. 세션 관리 API

#### SessionManager 클래스
```python
class SessionManager:
    """터미널 세션 관리자"""

    def create_session(self, config: SessionConfig) -> Session:
        """
        새 세션 생성

        Args:
            config: 세션 설정

        Returns:
            생성된 세션 객체
        """

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        세션 ID로 세션 조회

        Args:
            session_id: 조회할 세션 ID

        Returns:
            세션 객체 또는 None
        """

    def list_sessions(self) -> List[Session]:
        """모든 세션 목록 반환"""

    def delete_session(self, session_id: str) -> None:
        """
        세션 삭제

        Args:
            session_id: 삭제할 세션 ID
        """

    def session_context(self, config: SessionConfig) -> SessionContext:
        """
        세션 context manager 생성

        Args:
            config: 세션 설정

        Returns:
            세션 context manager
        """

class SessionContext:
    """세션 생명주기 관리를 위한 Context Manager"""

    def __init__(self, manager: SessionManager, config: SessionConfig):
        self.manager = manager
        self.config = config
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        """세션 생성 및 시작"""
        self.session = self.manager.create_session(self.config)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """세션 자동 정리 및 삭제"""
        if self.session:
            self.manager.delete_session(self.session.id)
```

### 6. 플러그인 시스템 API

#### PluginManager 클래스
```python
class PluginManager:
    """플러그인 관리자"""

    def load_plugin(self, plugin_path: str) -> Plugin:
        """
        플러그인 로드

        Args:
            plugin_path: 플러그인 경로

        Returns:
            로드된 플러그인 객체
        """

    def unload_plugin(self, plugin_id: str) -> None:
        """
        플러그인 언로드

        Args:
            plugin_id: 언로드할 플러그인 ID
        """

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        플러그인 조회

        Args:
            plugin_id: 조회할 플러그인 ID

        Returns:
            플러그인 객체 또는 None
        """
```

## 이벤트 및 콜백 API

### 1. 이벤트 시스템
```python
class EventManager:
    """이벤트 관리 시스템"""

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """이벤트 핸들러 등록"""

    def emit_event(self, event: Event) -> None:
        """이벤트 발생"""

    def remove_handler(self, event_type: str, handler: Callable) -> None:
        """이벤트 핸들러 제거"""
```

### 2. 훅 시스템
```python
class HookManager:
    """훅 관리 시스템"""

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """훅 콜백 등록"""

    def execute_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """훅 실행"""
```

## 설정 API

### ConfigManager 클래스
```python
class ConfigManager:
    """설정 관리자"""

    def load_config(self, config_path: str) -> Config:
        """설정 파일 로드"""

    def save_config(self, config: Config, config_path: str) -> None:
        """설정 파일 저장"""

    def get_setting(self, key: str) -> Any:
        """설정 값 조회"""

    def set_setting(self, key: str, value: Any) -> None:
        """설정 값 변경"""

    def temporary_config(self, **overrides) -> TempConfigContext:
        """
        임시 설정 오버라이드를 위한 context manager

        Args:
            **overrides: 임시로 설정할 키-값 쌍

        Returns:
            임시 설정 context manager
        """

class TempConfigContext:
    """임시 설정 관리를 위한 Context Manager"""

    def __init__(self, config_manager: ConfigManager, overrides: Dict[str, Any]):
        self.config_manager = config_manager
        self.overrides = overrides
        self.original_values: Dict[str, Any] = {}

    def __enter__(self) -> ConfigManager:
        """임시 설정 적용"""
        for key, value in self.overrides.items():
            self.original_values[key] = self.config_manager.get_setting(key)
            self.config_manager.set_setting(key, value)
        return self.config_manager

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """원래 설정 복원"""
        for key, original_value in self.original_values.items():
            self.config_manager.set_setting(key, original_value)
```

### 8. 완전 터미널 하이재킹 API

#### CompleteHijacker 클래스
```python
class CompleteHijacker:
    """모든 레벨의 터미널 하이재킹을 통합하는 메인 클래스"""

    def __init__(
        self,
        shell: str = "/bin/bash",
        enable_global_input: bool = True,
        enable_blessed_control: bool = True,
        **kwargs
    ) -> None:
        """
        완전 하이재킹 시스템 초기화

        Args:
            shell: 실행할 쉘 경로
            enable_global_input: 전역 입력 캡처 활성화 여부
            enable_blessed_control: blessed 터미널 제어 활성화 여부
            **kwargs: 추가 설정 옵션
        """

    async def __aenter__(self) -> 'CompleteHijacker':
        """
        비동기 context manager 진입점

        Returns:
            자기 자신 (CompleteHijacker 인스턴스)
        """
        await self.start_complete_hijacking()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        비동기 context manager 종료점, 모든 하이재킹 자동 정리

        Args:
            exc_type: 예외 타입
            exc_val: 예외 값
            exc_tb: 예외 트레이스백
        """
        await self.stop_complete_hijacking()
        await self._cleanup_all_resources()

    async def start_complete_hijacking(self) -> None:
        """모든 레벨의 하이재킹 동시 시작"""
        await self.start_pty_hijacking()      # Level 1: PTY 기반
        await self.start_global_hijacking()   # Level 2: 전역 입력
        await self.start_terminal_control()   # Level 3: 터미널 제어

    async def stop_complete_hijacking(self) -> None:
        """모든 레벨의 하이재킹 안전하게 중지"""
        await self.stop_terminal_control()    # Level 3 먼저 정리
        await self.stop_global_hijacking()    # Level 2 정리
        await self.stop_pty_hijacking()       # Level 1 마지막 정리

class GlobalInputHijacker:
    """전역 입력 하이재킹을 위한 클래스"""

    def __init__(self, capture_keyboard: bool = True, capture_mouse: bool = True):
        """
        전역 입력 하이재킹 초기화

        Args:
            capture_keyboard: 키보드 캡처 활성화
            capture_mouse: 마우스 캡처 활성화
        """

    async def start_keyboard_hijacking(self) -> None:
        """키보드 전역 캡처 시작"""
        from keyboard import Listener as KeyboardListener
        self.keyboard_listener = KeyboardListener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()

    async def start_mouse_hijacking(self) -> None:
        """마우스 전역 캡처 시작"""
        from pynput.mouse import Listener as MouseListener
        self.mouse_listener = MouseListener(
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()

    def _on_key_press(self, key) -> None:
        """키보드 입력 이벤트 핸들러"""
        # 키 입력 분석 및 로깅
        self.log_keyboard_event('press', key)
        self.analyze_input_pattern(key)

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """마우스 클릭 이벤트 핸들러"""
        # 마우스 이벤트 분석 및 로깅
        self.log_mouse_event('click', x, y, button, pressed)

class BlessedTerminalControl:
    """blessed 기반 고급 터미널 제어 클래스"""

    def __init__(self):
        """blessed 터미널 제어 초기화"""
        from blessed import Terminal
        self.terminal = Terminal()

    def __enter__(self) -> 'BlessedTerminalControl':
        """Context manager로 전체 화면 모드 진입"""
        self._fullscreen_context = self.terminal.fullscreen()
        self._cbreak_context = self.terminal.cbreak()

        self._fullscreen_context.__enter__()
        self._cbreak_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """전체 화면 모드 종료 및 터미널 복원"""
        if hasattr(self, '_cbreak_context'):
            self._cbreak_context.__exit__(exc_type, exc_val, exc_tb)
        if hasattr(self, '_fullscreen_context'):
            self._fullscreen_context.__exit__(exc_type, exc_val, exc_tb)

    def move_cursor(self, x: int, y: int) -> None:
        """커서를 지정된 위치로 이동"""
        print(self.terminal.move_xy(x, y), end='')

    def clear_screen(self) -> None:
        """화면 전체 지우기"""
        print(self.terminal.clear, end='')

    def set_colors(self, fg_color: str, bg_color: str = None) -> str:
        """색상 설정 문자열 반환"""
        color_str = getattr(self.terminal, fg_color, '')
        if bg_color:
            color_str += getattr(self.terminal, f'on_{bg_color}', '')
        return color_str

class HijackingEventHandler:
    """하이재킹된 이벤트 처리를 위한 기본 클래스"""

    async def on_keyboard_input(self, event: KeyboardEvent) -> None:
        """키보드 입력 이벤트 처리"""
        pass

    async def on_mouse_input(self, event: MouseEvent) -> None:
        """마우스 입력 이벤트 처리"""
        pass

    async def on_terminal_output(self, data: str) -> None:
        """터미널 출력 이벤트 처리"""
        pass

    async def on_ansi_sequence(self, sequence: ANSISequence) -> None:
        """ANSI 이스케이프 시퀀스 이벤트 처리"""
        pass
```

#### 사용 예제

##### 기본 완전 하이재킹 사용
```python
async def basic_complete_hijacking():
    """기본적인 완전 하이재킹 예제"""
    async with CompleteHijacker() as hijacker:
        # 모든 레벨의 하이재킹이 자동으로 시작됨
        # Level 1: PTY 기반 터미널 세션 제어
        # Level 2: 전역 키보드/마우스 입력 캡처
        # Level 3: blessed 기반 터미널 화면 제어

        # 하이재킹된 데이터에 대한 실시간 처리
        await hijacker.process_hijacked_data()
    # context manager 종료 시 모든 하이재킹 자동 정리
```

##### 선택적 하이재킹 기능
```python
async def selective_hijacking():
    """선택적 하이재킹 기능 예제"""
    hijacker = CompleteHijacker(
        enable_global_input=True,    # 전역 입력만 활성화
        enable_blessed_control=False # 터미널 제어는 비활성화
    )

    async with hijacker:
        # PTY + 전역 입력만 활성화된 상태
        await hijacker.analyze_input_patterns()
```

##### 커스텀 이벤트 핸들러
```python
class CustomHijackingHandler(HijackingEventHandler):
    """사용자 정의 하이재킹 이벤트 핸들러"""

    async def on_keyboard_input(self, event: KeyboardEvent) -> None:
        """특정 키 조합 감지 및 처리"""
        if event.key == 'ctrl+alt+h':
            print("하이재킹 모드 토글!")
            await self.toggle_hijacking_mode()

    async def on_terminal_output(self, data: str) -> None:
        """민감한 정보 필터링"""
        if 'password' in data.lower():
            # 비밀번호 출력 시 마스킹 처리
            filtered_data = self.mask_sensitive_data(data)
            await self.log_filtered_output(filtered_data)

async def custom_handler_example():
    """커스텀 핸들러 사용 예제"""
    handler = CustomHijackingHandler()

    async with CompleteHijacker() as hijacker:
        hijacker.set_event_handler(handler)
        await hijacker.start_monitoring()
```

## 오류 처리 API

### 예외 계층 구조
```python
class Term2AIError(Exception):
    """term2ai의 기본 예외 클래스"""

class PTYError(Term2AIError):
    """PTY 관련 오류"""

class IOError(Term2AIError):
    """I/O 관련 오류"""

class ParseError(Term2AIError):
    """파싱 관련 오류"""

class SessionError(Term2AIError):
    """세션 관련 오류"""

class PluginError(Term2AIError):
    """플러그인 관련 오류"""
```

## CLI API

### 함수형 CLI 인터페이스
Term2AI의 CLI는 함수형 프로그래밍 패러다임을 따라 모든 명령어를 순수 함수와 Effect로 구현합니다.

#### 기본 명령어 API
```python
import typer
from term2ai.monads import IOEffect, Result
from term2ai.cli.types import CLICommand, CLIOptions

app = typer.Typer()

# 메인 엔트리포인트
def cli_main(args: list[str]) -> IOEffect[int]:
    """함수형 CLI 메인 함수"""
    return (
        parse_cli_args_effect(args)
        .bind(validate_cli_command)
        .bind(execute_cli_command)
        .bind(format_cli_output)
        .map(lambda _: 0)
        .recover(handle_cli_error)
    )

@app.command()
def start(
    shell: str = typer.Option("/bin/bash", help="실행할 셸 경로"),
    config: Optional[str] = typer.Option(None, help="설정 파일 경로"),
    hijack_level: str = typer.Option("minimal", help="하이재킹 레벨"),
    filter_passwords: bool = typer.Option(False, help="비밀번호 필터링"),
    verbose: bool = typer.Option(False, help="상세 출력 모드")
) -> None:
    """터미널 세션 시작"""
    effect = start_terminal_session_effect(
        shell=shell,
        config_path=config,
        hijack_level=hijack_level,
        filters={"passwords": filter_passwords},
        verbose=verbose
    )
    run_effect(effect)

@app.command()
def stats(
    session_id: Optional[str] = typer.Option(None, help="세션 ID"),
    last: bool = typer.Option(False, help="마지막 세션 통계"),
    format: str = typer.Option("table", help="출력 형식"),
    metric: Optional[str] = typer.Option(None, help="특정 메트릭")
) -> None:
    """세션 통계 표시"""
    effect = show_session_stats_effect(
        session_id=session_id,
        last=last,
        output_format=format,
        metric_filter=metric
    )
    run_effect(effect)
```

#### 세션 관리 API
```python
# 세션 녹화
@app.command()
def record(
    output: str = typer.Argument(..., help="출력 파일 경로"),
    format: str = typer.Option("json", help="녹화 형식"),
    compress: bool = typer.Option(False, help="압축 활성화"),
    timestamp: bool = typer.Option(True, help="타임스탬프 포함")
) -> None:
    """세션 녹화"""
    effect = record_session_effect(
        output_path=output,
        format=RecordFormat[format.upper()],
        compression_enabled=compress,
        include_timestamps=timestamp
    )
    run_effect(effect)

# 세션 재생
@app.command()
def replay(
    input: str = typer.Argument(..., help="입력 파일 경로"),
    speed: float = typer.Option(1.0, help="재생 속도"),
    pause_on_output: bool = typer.Option(False, help="출력 시 일시정지"),
    skip_idle: Optional[float] = typer.Option(None, help="유휴 시간 건너뛰기")
) -> None:
    """세션 재생"""
    effect = replay_session_effect(
        input_path=input,
        playback_speed=speed,
        pause_on_output=pause_on_output,
        skip_idle_threshold=skip_idle
    )
    run_effect(effect)

# 세션 관리 서브커맨드
session_app = typer.Typer()
app.add_typer(session_app, name="session")

@session_app.command()
def list() -> None:
    """세션 목록 표시"""
    effect = list_sessions_effect()
    run_effect(effect)

@session_app.command()
def export(
    session_id: str = typer.Argument(..., help="세션 ID"),
    format: str = typer.Option("json", help="내보내기 형식"),
    output: Optional[str] = typer.Option(None, help="출력 파일")
) -> None:
    """세션 내보내기"""
    effect = export_session_effect(session_id, format, output)
    run_effect(effect)
```

#### 고급 기능 API
```python
# 분석 명령어
@app.command()
def analyze(
    pattern: str = typer.Option(None, help="분석할 패턴"),
    session_id: Optional[str] = typer.Option(None, help="세션 ID"),
    time_range: Optional[str] = typer.Option(None, help="시간 범위"),
    ai_model: Optional[str] = typer.Option(None, help="AI 모델 사용")
) -> None:
    """세션 분석"""
    effect = analyze_session_effect(
        pattern=pattern,
        session_id=session_id,
        time_range=parse_time_range(time_range),
        ai_model=ai_model
    )
    run_effect(effect)

# 벤치마크 명령어
@app.command()
def benchmark(
    metric: str = typer.Option("all", help="측정할 메트릭"),
    duration: int = typer.Option(60, help="테스트 시간(초)"),
    compare_with: Optional[str] = typer.Option(None, help="비교 기준"),
    output: Optional[str] = typer.Option(None, help="결과 저장")
) -> None:
    """성능 벤치마크"""
    effect = run_benchmark_effect(
        metric=BenchmarkMetric[metric.upper()],
        duration_seconds=duration,
        baseline=compare_with,
        output_path=output
    )
    run_effect(effect)

# 프로필 관리
profile_app = typer.Typer()
app.add_typer(profile_app, name="profile")

@profile_app.command()
def create(
    name: str = typer.Argument(..., help="프로필 이름"),
    base: str = typer.Option("default", help="기본 프로필")
) -> None:
    """프로필 생성"""
    effect = create_profile_effect(name, base)
    run_effect(effect)
```

### 대화형 모드 API
```python
# 대화형 CLI
@app.command()
def interactive() -> None:
    """대화형 모드 시작"""
    effect = start_interactive_mode_effect()
    run_effect(effect)

# 대화형 모드 스트림 API
def create_interactive_session() -> IOEffect[InteractiveSession]:
    """대화형 세션 생성"""
    return IOEffect(lambda: InteractiveSession(
        input_stream=create_stdin_stream(),
        output_stream=create_stdout_stream(),
        completion_engine=create_completion_engine()
    ))

def process_interactive_input(
    session: InteractiveSession
) -> IOEffect[AsyncStream[CommandResult]]:
    """대화형 입력 처리"""
    return session.input_stream.map(
        lambda stream: stream
        .map(parse_interactive_command)
        .filter(is_valid_interactive_command)
        .map(execute_interactive_command)
        .map(format_interactive_result)
    )
```

### 설정 관리 API
```python
# 설정 명령어
config_app = typer.Typer()
app.add_typer(config_app, name="config")

@config_app.command()
def show() -> None:
    """현재 설정 표시"""
    effect = show_config_effect()
    run_effect(effect)

@config_app.command()
def set(
    key: str = typer.Argument(..., help="설정 키"),
    value: str = typer.Argument(..., help="설정 값")
) -> None:
    """설정 값 변경"""
    effect = update_config_effect(key, value)
    run_effect(effect)

# 설정 관리 순수 함수
def parse_config_key(key: str) -> Result[ConfigKey, ConfigError]:
    """설정 키 파싱 및 검증"""
    parts = key.split('.')
    if not all(parts):
        return Err(ConfigError("Invalid config key"))
    return Ok(ConfigKey(parts))

def merge_config_values(
    base: Config,
    overrides: dict[str, Any]
) -> Config:
    """설정 값 병합 (순수 함수)"""
    return Config(
        **{**base.dict(), **overrides}
    )
```

### 플러그인 시스템 API
```python
# 플러그인 명령어
plugin_app = typer.Typer()
app.add_typer(plugin_app, name="plugin")

@plugin_app.command()
def install(
    name: str = typer.Argument(..., help="플러그인 이름"),
    source: Optional[str] = typer.Option(None, help="플러그인 소스")
) -> None:
    """플러그인 설치"""
    effect = install_plugin_effect(name, source)
    run_effect(effect)

@plugin_app.command()
def list() -> None:
    """설치된 플러그인 목록"""
    effect = list_plugins_effect()
    run_effect(effect)

# 플러그인 로더 API
def load_plugin_manifest(path: str) -> Result[PluginManifest, PluginError]:
    """플러그인 매니페스트 로드 (순수 함수)"""
    try:
        with open(path) as f:
            data = json.load(f)
        return Ok(PluginManifest(**data))
    except Exception as e:
        return Err(PluginError(str(e)))

def validate_plugin_compatibility(
    manifest: PluginManifest,
    system_version: Version
) -> Result[None, CompatibilityError]:
    """플러그인 호환성 검증 (순수 함수)"""
    if manifest.min_version > system_version:
        return Err(CompatibilityError("Plugin requires newer version"))
    return Ok(None)
```

### Effect 실행 시스템
```python
# Effect 실행 헬퍼
def run_effect[T](effect: IOEffect[T]) -> None:
    """Effect를 실행하고 결과 처리"""
    try:
        result = effect.run()
        if isinstance(result, Result):
            if result.is_err():
                handle_error(result.unwrap_err())
            else:
                handle_success(result.unwrap())
        else:
            handle_success(result)
    except Exception as e:
        handle_exception(e)

# 에러 처리
def handle_cli_error(error: CLIError) -> IOEffect[int]:
    """CLI 에러를 처리하고 종료 코드 반환"""
    return IOEffect(lambda: {
        console.print(f"[red]Error:[/red] {error}")
        return 1
    })

# 비동기 Effect 실행
async def run_async_effect[T](effect: IOEffect[T]) -> T:
    """비동기 Effect 실행"""
    if hasattr(effect, 'run_async'):
        return await effect.run_async()
    else:
        return await asyncio.to_thread(effect.run)
```

### CLI 테스트 API
```python
# 테스트 명령어
@app.command()
def test(
    scenario: Optional[str] = typer.Option(None, help="테스트 시나리오"),
    property_based: bool = typer.Option(False, help="Property-based 테스트"),
    coverage: bool = typer.Option(False, help="커버리지 측정")
) -> None:
    """통합 테스트 실행"""
    effect = run_tests_effect(
        scenario=scenario,
        use_property_based=property_based,
        measure_coverage=coverage
    )
    run_effect(effect)

# 테스트 헬퍼 함수
def create_test_cli_context() -> CLIContext:
    """테스트용 CLI 컨텍스트 생성"""
    return CLIContext(
        stdin=io.StringIO(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        config=Config.default()
    )

def assert_cli_output(
    context: CLIContext,
    expected: str
) -> None:
    """CLI 출력 검증"""
    actual = context.stdout.getvalue()
    assert actual.strip() == expected.strip()
```

## 네트워크 API

### NetworkServer 클래스
```python
class NetworkServer:
    """네트워크 터미널 서버"""

    def start_server(self, host: str, port: int) -> None:
        """서버 시작"""

    def stop_server(self) -> None:
        """서버 중지"""

    def handle_client(self, client_socket) -> None:
        """클라이언트 연결 처리"""
```

## 사용 예제

### 기본 사용법 (Context Manager 적용)
```python
from term2ai import PTYWrapper, SessionManager

# PTY 래퍼 사용 (자동 리소스 관리)
with PTYWrapper(shell="/bin/bash") as pty:
    # 명령 실행
    pty.write("echo 'Hello, World!'\n")
    output = pty.read()
    print(output)
    # pty.terminate()와 리소스 정리가 자동으로 수행됨

# 세션 관리 (자동 세션 정리)
session_manager = SessionManager()
with session_manager.session_context(SessionConfig()) as session:
    session.start_recording()
    # 작업 수행
    # 세션이 자동으로 정리됨

# 임시 설정 사용
config_manager = ConfigManager()
with config_manager.temporary_config(debug=True, verbose=True):
    # 임시 설정으로 작업 수행
    pass
    # 원래 설정이 자동으로 복원됨
```

### 비동기 사용법 (Async Context Manager 적용)
```python
import asyncio
import uvloop
from term2ai import AsyncIOManager
import aiofiles

# Unix 전용 성능 최적화
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
print("uvloop 성능 최적화 활성화")

async def async_terminal():
    # 비동기 context manager 사용
    async with AsyncIOManager() as io_manager:
        # 비동기 I/O 작업
        data = await io_manager.read_async(fd, 1024)
        await io_manager.write_async(fd, b"command\n")

        # aiofiles를 통한 세션 로깅
        async with aiofiles.open('session.log', 'a') as log_file:
            await log_file.write(f"Command executed: {data.decode()}\n")

        # 비동기 리소스가 자동으로 정리됨

# Unix 최적화된 고성능으로 실행
asyncio.run(async_terminal())
```

### 성능 최적화 사용법
```python
import uvloop
from term2ai import AsyncIOManager, PTYWrapper

# Unix 전용 고성능 비동기 터미널 래퍼
class HighPerformancePTY:
    def __init__(self):
        self.setup_unix_optimization()

    def setup_unix_optimization(self):
        """Unix 전용 최적화 설정"""
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.performance_mode = "uvloop_epoll"

    async def process_high_throughput(self, data_stream):
        """고처리량 데이터 처리 (목표: >300MB/s Unix)"""
        async with AsyncIOManager() as io_manager:
            async for chunk in data_stream:
                processed = await io_manager.process_chunk(chunk)
                yield processed

# 사용 예시
async def benchmark_performance():
    pty = HighPerformancePTY()
    print(f"성능 모드: {pty.performance_mode}")

    # 대용량 데이터 처리
    async for result in pty.process_high_throughput(data_generator()):
        # 결과 처리
        pass
```

### 플러그인 개발
```python
from term2ai.plugins import PluginBase

class MyPlugin(PluginBase):
    def on_input(self, data: str) -> str:
        """입력 데이터 처리"""
        return data.upper()  # 모든 입력을 대문자로

    def on_output(self, data: str) -> str:
        """출력 데이터 처리"""
        return f"[PLUGIN] {data}"
```

이 API 설계는 모듈화, 확장성, 사용 편의성을 고려하여 설계되었으며, 터미널 래퍼의 모든 기능에 대한 명확하고 일관된 인터페이스를 제공합니다.
