# 기술적 결정사항 문서

## 개요
이 문서는 term2ai 프로젝트에서 내린 주요 기술적 결정사항들과 그 근거를 설명합니다. 각 결정의 배경, 고려사항, 그리고 트레이드오프를 상세히 기록합니다.

## 핵심 기술 선택

### 1. PTY 라이브러리 선택: ptyprocess vs subprocess

#### 결정: ptyprocess 사용
**근거:**
- **의사 터미널 지원**: subprocess는 파이프만 제공하지만, ptyprocess는 실제 터미널처럼 동작하는 의사 터미널 제공
- **인터랙티브 애플리케이션 호환성**: vim, htop, ssh 등의 프로그램이 정상 동작
- **ANSI 이스케이프 시퀀스**: 터미널 애플리케이션이 색상과 커서 제어 코드를 올바르게 출력
- **터미널 크기 감지**: 애플리케이션이 터미널 크기를 인식하고 적절히 반응

**트레이드오프:**
- **복잡성 증가**: subprocess보다 복잡한 설정과 오류 처리 필요
- **Unix 전용 특화**: Unix/Linux 계열 전용으로 최적화되어 최대 성능 달성
- **성능 최적화**: 의사 터미널 최적화로 Unix 네이티브 성능 활용

#### 대안 고려사항
- **subprocess**: 단순한 명령 실행에는 충분하지만 터미널 기능 제한적
- **pexpect**: ptyprocess 기반으로 구축되어 더 높은 수준의 추상화 제공하지만 무거움

### 2. 동기 vs 비동기 I/O 아키텍처

#### 결정: 하이브리드 접근 (동기 + 비동기)
**근거:**
- **기본 동기 인터페이스**: 단순한 사용 사례를 위한 직관적인 API
- **비동기 옵션**: 고성능 요구사항과 다중 세션 지원을 위한 async/await
- **점진적 복잡성**: 사용자가 필요에 따라 복잡성 수준 선택 가능

**구현 전략:**
```python
# 동기 인터페이스 (기본)
pty = PTYWrapper()
output = pty.read()

# 비동기 인터페이스 (고성능)
async def async_operation():
    async_pty = AsyncPTYWrapper()
    output = await async_pty.read_async()
```

**트레이드오프:**
- **코드 복잡성**: 두 가지 인터페이스 유지 관리
- **성능 최적화**: 상황에 맞는 최적의 성능 제공
- **학습 곡선**: 개발자가 두 패러다임 모두 이해 필요

### 3. 데이터 검증: Pydantic vs dataclasses

#### 결정: Pydantic 사용
**근거:**
- **런타임 검증**: 설정과 데이터의 실시간 검증으로 버그 조기 발견
- **자동 직렬화**: JSON/YAML 설정 파일과의 원활한 통합
- **타입 변환**: 자동 타입 변환으로 사용자 편의성 향상
- **문서화**: 스키마 자동 생성으로 API 문서화 개선

**트레이드오프:**
- **성능 오버헤드**: dataclasses보다 느린 객체 생성
- **의존성 추가**: 외부 라이브러리 의존성 증가
- **메모리 사용량**: 추가 메타데이터로 인한 메모리 사용량 증가

### 4. UI 프레임워크: Rich vs Click

#### 결정: Rich + Typer (Click 기반)
**근거:**
- **Rich의 장점**: 아름다운 터미널 출력, 색상, 테이블, 진행률 표시
- **Typer의 장점**: 타입 힌트 기반 CLI, 자동 도움말 생성
- **상호 보완성**: Rich는 출력, Typer는 명령줄 파싱 담당

**사용 예시:**
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def start(verbose: bool = False):
    if verbose:
        console.print("[green]터미널 래퍼 시작[/green]")
```

### 5. 리소스 관리: 수동 정리 vs Context Manager

#### 결정: Context Manager 패턴 (RAII) 채택
**근거:**
- **자동 리소스 정리**: with 문을 사용하면 예외 발생 시에도 리소스가 자동으로 정리됨
- **Python다운 코드**: Python의 표준 관용구로 코드 가독성 향상
- **예외 안전성**: try/finally 블록이 자동으로 처리되어 버그 가능성 감소
- **RAII 패턴**: Resource Acquisition Is Initialization 원칙으로 견고한 설계

**구현 전략:**
```python
# 기존 방식 (위험)
pty = PTYWrapper()
try:
    pty.spawn()
    # 작업 수행
finally:
    pty.terminate()  # 실수로 누락될 수 있음

# Context Manager 방식 (안전)
with PTYWrapper() as pty:
    # 작업 수행
    pass  # 자동으로 정리됨
```

**트레이드오프:**
- **구현 복잡성**: `__enter__`와 `__exit__` 메서드 구현 필요
- **성능 향상**: 리소스 누수 방지로 장기적 성능 향상
- **디버깅 용이성**: 리소스 관련 버그 대폭 감소

### 6. 설정 관리: TOML vs YAML vs JSON

#### 결정: TOML (주) + JSON (보조)
**근거:**
- **TOML**: 사람이 읽기 쉽고 주석 지원, Python 생태계 표준
- **JSON**: API 통신과 플러그인 설정에 적합
- **YAML 제외**: 보안 문제와 복잡한 문법으로 인한 오류 가능성

**설정 계층 구조:**
```
1. pyproject.toml (프로젝트 설정)
2. ~/.config/term2ai/config.toml (사용자 설정)
3. 환경 변수 (런타임 오버라이드)
4. CLI 인수 (실행시 오버라이드)
```

### 7. 비동기 I/O 라이브러리 선택

#### 결정: aiofiles + uvloop + aiosignal 조합 (Unix 전용)
**근거:**
- **aiofiles**: 비동기 파일 I/O의 표준 라이브러리로 세션 로깅과 설정 파일 처리에 필수
- **uvloop**: asyncio 기본 구현 대비 3-5배 성능 향상으로 <3ms 지연시간 목표 달성
- **aiosignal**: 비동기 환경에서 Unix 시그널 처리와 I/O 멀티플렉싱 통합

**트레이드오프:**
- **Unix 전용 최적화**: Unix 계열에만 특화되어 최대 성능 달성 (3-5배 향상)
- **고성능 의존성**: Unix 전용 고성능 라이브러리로 최적 성능 보장
- **성능 우선**: Unix 네이티브 성능 활용을 위한 필수 선택

#### 대안 고려사항
- **표준 asyncio만 사용**: 단순하지만 성능 목표(>300MB/s) 달성 어려움
- **trio**: 우수한 비동기 라이브러리이지만 Unix 전용 최적화 부족
- **anyio**: 호환성 레이어이지만 성능 오버헤드 존재

### 8. 의존성 그룹 전략

#### 결정: Unix 전용 최적화 의존성 관리
**구조:**
- **핵심 의존성**: 모든 Unix 사용자에게 필수 (aiofiles 포함)
- **성능 그룹**: 최적 성능을 위한 필수 (uvloop, aiosignal)
- **하이재킹 그룹**: 완전한 터미널 하이재킹 기능 (keyboard, pynput, blessed)
- **개발 그룹**: 개발 및 테스트 도구

**설치 전략:**
```bash
# 기본 설치
uv sync

# 최적 성능 (권장)
uv sync --group performance

# 완전 하이재킹 기능
uv sync --group hijacking

# 모든 기능 포함
uv sync --all-groups
```

**근거:**
- **최적화**: Unix 계열 전용 최적화로 최대 성능 달성
- **단순성**: 플랫폼 분기 제거로 복잡성 감소
- **성능 우선**: 고성능 터미널 래퍼를 위한 의존성 선택
- **하이재킹**: 완전한 터미널 I/O 제어를 위한 전문 라이브러리

### 9. 터미널 하이재킹 아키텍처 선택

#### 결정: 다층 하이재킹 아키텍처
**근거:**
- **PTY 기반 하이재킹**: ptyprocess로 터미널 세션 내부 완전 제어
- **전역 입력 하이재킹**: keyboard + pynput으로 시스템 레벨 입력 캡처
- **고급 터미널 제어**: blessed로 터미널 기능 완전 활용

**아키텍처 계층:**
```
Level 3: GUI 터미널 하이재킹 (blessed)
         ↓
Level 2: 전역 입력 하이재킹 (keyboard + pynput)  
         ↓
Level 1: PTY 기반 하이재킹 (ptyprocess + pexpect)
         ↓
Level 0: 운영 체제 (Unix)
```

**구현 전략:**
```python
class CompleteTerminalHijacker:
    def __init__(self):
        # Level 1: PTY 하이재킹
        self.pty = pexpect.spawn('/bin/bash')
        
        # Level 2: 전역 입력 하이재킹  
        self.keyboard_listener = keyboard.Listener(on_press=self.capture_key)
        self.mouse_listener = mouse.Listener(on_click=self.capture_mouse)
        
        # Level 3: 터미널 제어
        self.terminal = Terminal()
        
    async def start_complete_hijacking(self):
        # 모든 레벨의 하이재킹 동시 시작
        async with self:
            # PTY + 전역 입력 + 터미널 제어 = 100% 커버리지
            pass
```

**트레이드오프:**
- **복잡성 증가**: 다층 아키텍처로 인한 복잡도 상승
- **완전한 제어**: 터미널 I/O의 100% 하이재킹 달성
- **성능 영향**: 전역 입력 캡처로 인한 소량의 성능 오버헤드
- **보안 고려**: 시스템 레벨 접근으로 인한 권한 관리 필요

#### 대안 고려사항
- **PTY만 사용**: 단순하지만 터미널 외부 입력 캡처 불가
- **pyautogui 사용**: GUI 자동화 가능하지만 신뢰성 문제
- **저수준 Hook**: 플랫폼별 구현 필요로 복잡성 증가

### 10. 전역 입력 캡처 라이브러리 비교

#### 결정: keyboard + pynput 조합 사용
**keyboard 선택 근거:**
- **전역 키보드 Hook**: 모든 키보드 입력을 시스템 레벨에서 캡처
- **실시간 처리**: 낮은 지연시간으로 실시간 키 이벤트 처리
- **Unix 최적화**: Linux/macOS에서 최적의 성능

**pynput 선택 근거:**
- **마우스 + 키보드**: 통합된 입력 장치 제어
- **크로스 플랫폼**: Unix 계열에서 일관된 API 제공
- **이벤트 리스너**: 비침투적인 백그라운드 모니터링

**조합 사용 이유:**
```python
# keyboard: 전역 키보드 Hook (빠른 응답)
import keyboard
keyboard.on_press(lambda key: capture_keyboard_event(key))

# pynput: 마우스 + 정교한 키보드 제어
from pynput import mouse, keyboard as pynput_keyboard
mouse_listener = mouse.Listener(on_click=capture_mouse_event)
kb_listener = pynput_keyboard.Listener(on_press=capture_detailed_key_event)
```

**트레이드오프:**
- **라이브러리 중복**: 두 라이브러리 동시 사용으로 메모리 사용량 증가
- **기능 보완**: keyboard의 속도 + pynput의 정교함 = 완벽한 하이재킹
- **유지보수**: 두 라이브러리 모두 관리 필요

#### 대안 고려사항
- **keyboard만 사용**: 마우스 이벤트 캡처 불가
- **pynput만 사용**: 전역 Hook 성능이 keyboard보다 느림
- **pyautogui**: GUI 자동화는 가능하지만 안정성 문제

### 11. GUI vs PTY 기반 터미널 제어

#### 결정: blessed 기반 고급 터미널 제어
**blessed 선택 근거:**
- **풀스크린 모드**: 터미널 전체 화면 완전 제어
- **고급 커서 제어**: 정밀한 커서 위치 및 모양 제어  
- **터미널 기능 감지**: 터미널별 기능 자동 감지 및 활용
- **ANSI 최적화**: 효율적인 ANSI 시퀀스 생성

**구현 전략:**
```python
from blessed import Terminal

class AdvancedTerminalControl:
    def __init__(self):
        self.terminal = Terminal()
        
    def enter_fullscreen_mode(self):
        with self.terminal.fullscreen():
            # 전체 화면 모드에서 완전 제어
            with self.terminal.cbreak():
                # 키보드 입력 즉시 처리
                self.handle_terminal_interaction()
                
    def precise_cursor_control(self, x: int, y: int):
        # 정확한 커서 위치 제어
        print(self.terminal.move_xy(x, y), end='')
```

**트레이드오프:**
- **터미널 의존성**: 터미널 기능에 따른 제약 존재
- **완전한 제어**: PTY + blessed 조합으로 모든 터미널 기능 활용
- **성능 최적화**: 효율적인 ANSI 시퀀스로 빠른 화면 업데이트

#### 대안 고려사항
- **curses**: Python 내장이지만 기능 제한적
- **rich**: 아름다운 출력이지만 실시간 제어 부족
- **직접 ANSI**: 구현 복잡도 높고 호환성 문제

## 성능 관련 결정사항

### 1. 버퍼링 전략

#### 결정: 계층적 버퍼링
**구조:**
- **커널 버퍼**: OS 수준 버퍼링
- **애플리케이션 버퍼**: term2ai 내부 버퍼 (기본 8KB)
- **사용자 버퍼**: 플러그인과 필터를 위한 버퍼

**근거:**
- **성능**: 시스템 콜 횟수 최소화
- **메모리 효율성**: 적응적 버퍼 크기 조정
- **응답성**: 작은 데이터도 즉시 처리 가능

### 2. 리소스 수명 관리

#### 결정: Context Manager 기반 자동 관리
**전략:**
- **PTY 리소스**: Context manager로 파일 디스크립터 자동 정리
- **비동기 리소스**: Async context manager로 비동기 리소스 관리
- **세션 관리**: 세션별 context manager로 생명주기 관리
- **설정 관리**: 임시 설정을 위한 context manager

**구현:**
```python
class PTYWrapper:
    def __enter__(self) -> 'PTYWrapper':
        self.spawn()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.terminate()
        self._cleanup_resources()

class AsyncIOManager:
    async def __aenter__(self) -> 'AsyncIOManager':
        await self._initialize_async_resources()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._cleanup_async_resources()
```

### 3. 메모리 관리

#### 결정: 객체 풀링 + 가비지 컬렉션 최적화
**전략:**
- **버퍼 풀**: 자주 사용되는 버퍼 객체 재사용
- **문자열 인터닝**: 반복되는 ANSI 시퀀스 메모리 절약
- **약한 참조**: 순환 참조 방지로 메모리 누수 예방

**구현:**
```python
class BufferPool:
    def __init__(self):
        self._pool = collections.deque(maxlen=100)
    
    def get_buffer(self, size: int) -> bytearray:
        if self._pool:
            buffer = self._pool.popleft()
            if len(buffer) >= size:
                return buffer
        return bytearray(size)
```

### 3. ANSI 파싱 최적화

#### 결정: 상태 기계 + 사전 컴파일된 정규식
**근거:**
- **상태 기계**: 메모리 효율적이고 빠른 파싱
- **정규식**: 복잡한 시퀀스 패턴 매칭
- **캐싱**: 자주 사용되는 시퀀스 결과 캐싱

**성능 목표:**
- 100MB/s 이상의 파싱 속도
- 메모리 사용량 50MB 이하
- 지연시간 1ms 미만

## 보안 관련 결정사항

### 1. 플러그인 샌드박싱

#### 결정: 제한적 실행 환경
**구현 방법:**
- **import 제한**: 허용된 모듈만 import 가능
- **파일 시스템 접근 제한**: 지정된 디렉토리만 접근
- **네트워크 접근 제어**: 화이트리스트 기반 네트워크 접근
- **CPU/메모리 제한**: 리소스 사용량 모니터링

**보안 계층:**
```python
class PluginSandbox:
    def __init__(self):
        self.allowed_modules = {'os', 'sys', 'json', 'term2ai.api'}
        self.max_memory = 100 * 1024 * 1024  # 100MB
        self.max_cpu_time = 5.0  # 5초
```

### 2. 세션 데이터 보호

#### 결정: 선택적 암호화
**전략:**
- **기본값**: 평문 저장 (성능 우선)
- **민감 데이터**: AES-256 암호화 (보안 우선)
- **사용자 선택**: 보안 수준 설정 가능

**구현:**
```python
class SessionStorage:
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_enabled = encryption_key is not None
        self.cipher = AES.new(encryption_key) if encryption_key else None
```

### 3. 네트워크 보안

#### 결정: TLS 1.3 + 인증서 기반 인증
**요구사항:**
- **암호화**: 모든 네트워크 통신 TLS 암호화
- **인증**: 클라이언트 인증서 또는 토큰 기반
- **권한**: 역할 기반 접근 제어 (RBAC)

## 호환성 결정사항

### 1. Python 버전 지원

#### 결정: Python 3.11+
**근거:**
- **최신 기능**: 향상된 오류 메시지, 성능 개선
- **타입 힌트**: 최신 타입 힌트 기능 활용
- **생태계**: 대부분의 라이브러리가 3.11 지원
- **유지보수**: 지원 버전 수 최소화

**마이그레이션 경로:**
- Python 3.10: 호환성 유지하되 기능 제한
- Python 3.9 이하: 지원 중단

### 2. 운영체제 지원

#### 결정: Unix 계열 전용 지원
**지원 플랫폼:**
1. **Linux**: 주요 타겟 플랫폼 (최적 성능)
2. **macOS**: 전체 기능 지원 (개발자 친화적)

**근거:**
- **PTY 완전 지원**: Unix 계열에서 PTY 기능 완전 활용
- **성능 최적화**: Unix 전용 라이브러리로 최대 성능 달성
- **유지보수 효율성**: 단일 플랫폼 지원으로 코드 복잡성 감소
- **타겟 사용자**: 고급 터미널 사용자는 대부분 Unix 계열 선호

### 3. Unix 전용 성능 최적화

#### 결정: Unix 전용 고성능 라이브러리 사용
**전략:**
- **uvloop**: libuv 기반 고성능 이벤트 루프
- **aiosignal**: Unix 시그널 처리 최적화
- **epoll/kqueue**: 플랫폼별 최적 I/O 멀티플렉싱

**구현 방법:**
```python
# Unix 전용 최적화 설정
import uvloop
import aiosignal

# 고성능 이벤트 루프 설정
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Unix 전용 시그널 처리 활성화
aiosignal.setup_unix_signals()
```

**성능 영향:**
- **I/O 성능**: 기본 asyncio 대비 3-5배 향상
- **지연시간**: <3ms 달성
- **처리량**: >300MB/s 달성

### 3. 터미널 에뮬레이터 호환성

#### 결정: VT100/ANSI 표준 준수
**지원 우선순위:**
1. **xterm**: 가장 널리 사용되는 표준
2. **gnome-terminal, konsole**: 주요 Linux 터미널
3. **iTerm2, Terminal.app**: macOS 터미널
4. **기타**: 표준 준수 터미널들

**호환성 전략:**
```python
class TerminalCapabilities:
    def detect_terminal(self) -> str:
        """터미널 타입 감지"""
        term_type = os.environ.get('TERM', 'unknown')
        return self.normalize_terminal_type(term_type)
    
    def get_capabilities(self, terminal_type: str) -> Dict[str, bool]:
        """터미널별 기능 반환"""
        return self.capability_database.get(terminal_type, self.default_caps)
```

## 확장성 결정사항

### 1. 플러그인 아키텍처

#### 결정: 이벤트 기반 훅 시스템
**구조:**
- **이벤트 버스**: 중앙집중식 이벤트 처리
- **훅 포인트**: 코어 기능의 확장 지점
- **플러그인 라이프사이클**: 로드/언로드/재로드 지원

**예시:**
```python
@plugin.hook('on_input')
def transform_input(data: str) -> str:
    return data.upper()

@plugin.hook('on_output')
def log_output(data: str) -> None:
    logger.info(f"Output: {data}")
```

### 2. 설정 시스템

#### 결정: 계층적 설정 + 런타임 변경
**특징:**
- **상속**: 기본 설정 → 사용자 설정 → 세션 설정
- **검증**: Pydantic을 통한 실시간 검증
- **알림**: 설정 변경 시 이벤트 발생

### 3. API 버전 관리

#### 결정: 시맨틱 버전 + 하위 호환성
**정책:**
- **Major**: 호환성 깨는 변경
- **Minor**: 새 기능 추가 (호환성 유지)
- **Patch**: 버그 수정

**마이그레이션:**
```python
@deprecated_api("2.0.0", "사용 중단됨. new_method() 사용")
def old_method(self):
    return self.new_method()
```

## 테스트 전략 결정사항

### 1. 테스트 프레임워크

#### 결정: pytest + 전용 픽스처
**구성:**
- **단위 테스트**: 개별 함수/클래스 테스트
- **통합 테스트**: 컴포넌트 간 상호작용 테스트
- **E2E 테스트**: 실제 터미널 애플리케이션 테스트

### 2. 모킹 전략

#### 결정: 계층별 모킹
**수준:**
- **시스템 콜**: PTY 생성/제어 모킹
- **네트워크**: 소켓 통신 모킹
- **파일 시스템**: 설정/로그 파일 모킹

### 3. 성능 테스트

#### 결정: 벤치마크 + 회귀 테스트
**메트릭:**
- **처리량**: MB/s
- **지연시간**: 밀리초
- **메모리**: MB
- **CPU**: 사용률

이러한 기술적 결정사항들은 term2ai가 안정적이고 확장 가능하며 고성능인 터미널 래퍼가 되도록 하는 기반을 제공합니다.