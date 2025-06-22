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
from term2ai import AsyncIOManager

async def async_terminal():
    # 비동기 context manager 사용
    async with AsyncIOManager() as io_manager:
        # 비동기 I/O 작업
        data = await io_manager.read_async(fd, 1024)
        await io_manager.write_async(fd, b"command\n")
        # 비동기 리소스가 자동으로 정리됨

asyncio.run(async_terminal())
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