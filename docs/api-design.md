# API 설계 문서

## 개요
term2ai의 API는 모듈화된 구조로 설계되어 각 기능별로 명확한 인터페이스를 제공합니다. 이 문서는 각 모듈의 API 설계 원칙과 구체적인 인터페이스를 설명합니다.

## API 설계 원칙

### 1. 타입 안전성
- 모든 API는 타입 힌트를 포함
- Pydantic 모델을 통한 데이터 검증
- mypy를 통한 정적 타입 검사

### 2. 직관적인 인터페이스
- 명확하고 일관된 메서드 명명
- 예측 가능한 매개변수 구조
- 표준 Python 관례 따름

### 3. 확장성
- 플러그인 시스템을 통한 기능 확장
- 훅과 콜백을 통한 커스터마이징
- 설정 가능한 모든 동작

### 4. 오류 처리
- 명확한 예외 계층 구조
- 구체적인 오류 메시지
- 복구 가능한 오류와 불가능한 오류 구분

## 핵심 API 모듈

### 1. PTY 래퍼 코어 API

#### PTYWrapper 클래스
```python
class PTYWrapper:
    """의사 터미널 래퍼의 핵심 클래스"""
    
    def __init__(self, shell: str = "/bin/bash", **kwargs) -> None:
        """
        PTY 래퍼 초기화
        
        Args:
            shell: 실행할 쉘 경로
            **kwargs: 추가 설정 옵션
        """
    
    def __enter__(self) -> 'PTYWrapper':
        """
        Context manager 진입점
        
        Returns:
            자기 자신 (PTYWrapper 인스턴스)
        """
        self.spawn()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager 종료점, 리소스 자동 정리
        
        Args:
            exc_type: 예외 타입
            exc_val: 예외 값
            exc_tb: 예외 트레이스백
        """
        self.terminate()
        self._cleanup_resources()
    
    def spawn(self) -> None:
        """프로세스를 의사 터미널에서 실행"""
    
    def write(self, data: str) -> int:
        """
        PTY에 데이터 쓰기
        
        Args:
            data: 전송할 문자열
            
        Returns:
            실제로 쓰여진 바이트 수
        """
    
    def read(self, size: int = 1024) -> str:
        """
        PTY에서 데이터 읽기
        
        Args:
            size: 읽을 최대 바이트 수
            
        Returns:
            읽은 문자열
        """
    
    def is_alive(self) -> bool:
        """프로세스가 살아있는지 확인"""
    
    def terminate(self) -> None:
        """프로세스 종료"""
    
    def get_exit_code(self) -> Optional[int]:
        """프로세스 종료 코드 반환"""
    
    def _cleanup_resources(self) -> None:
        """내부 리소스 정리 (파일 디스크립터, 버퍼 등)"""
```

### 2. 비동기 I/O 관리 API

#### AsyncIOManager 클래스
```python
class AsyncIOManager:
    """비동기 I/O 작업 관리자"""
    
    async def __aenter__(self) -> 'AsyncIOManager':
        """
        비동기 context manager 진입점
        
        Returns:
            자기 자신 (AsyncIOManager 인스턴스)
        """
        await self._initialize_async_resources()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        비동기 context manager 종료점, 비동기 리소스 정리
        
        Args:
            exc_type: 예외 타입
            exc_val: 예외 값
            exc_tb: 예외 트레이스백
        """
        await self._cleanup_async_resources()
    
    async def read_async(self, fd: int, size: int = 1024) -> bytes:
        """
        비동기 읽기 작업
        
        Args:
            fd: 파일 디스크립터
            size: 읽을 바이트 수
            
        Returns:
            읽은 데이터
        """
    
    async def write_async(self, fd: int, data: bytes) -> int:
        """
        비동기 쓰기 작업
        
        Args:
            fd: 파일 디스크립터
            data: 쓸 데이터
            
        Returns:
            쓰여진 바이트 수
        """
    
    async def read_with_timeout(self, fd: int, timeout: float) -> bytes:
        """
        타임아웃이 있는 읽기 작업
        
        Args:
            fd: 파일 디스크립터
            timeout: 타임아웃 시간(초)
            
        Returns:
            읽은 데이터
            
        Raises:
            asyncio.TimeoutError: 타임아웃 발생 시
        """
    
    async def _initialize_async_resources(self) -> None:
        """비동기 리소스 초기화"""
    
    async def _cleanup_async_resources(self) -> None:
        """비동기 리소스 정리"""
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

### 명령줄 인터페이스
```python
import typer

app = typer.Typer()

@app.command()
def start(
    shell: str = "/bin/bash",
    config: Optional[str] = None,
    verbose: bool = False
) -> None:
    """터미널 래퍼 시작"""

@app.command()
def record(
    output_file: str,
    shell: str = "/bin/bash"
) -> None:
    """세션 기록"""

@app.command()
def replay(
    input_file: str,
    speed: float = 1.0
) -> None:
    """세션 재생"""
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