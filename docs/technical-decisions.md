# 함수형 프로그래밍 기반 기술적 결정사항

## 개요
이 문서는 term2ai 프로젝트를 **함수형 프로그래밍 패러다임**으로 재설계하면서 내린 주요 기술적 결정사항들과 그 근거를 설명합니다. 순수성, 불변성, 합성성을 중심으로 한 설계 철학과 각 결정의 배경, 고려사항, 트레이드오프를 상세히 기록합니다.

## 함수형 프로그래밍 패러다임 선택

### 0. 프로그래밍 패러다임: 함수형 vs 객체지향

#### 결정: 함수형 프로그래밍 패러다임 채택
**근거:**
- **예측 가능성**: 순수 함수는 동일한 입력에 대해 항상 동일한 출력을 보장하여 버그 예측과 추적이 용이
- **테스트 용이성**: 부작용이 없는 순수 함수는 격리된 테스트가 가능하고 property-based testing 적용 가능
- **동시성 안전성**: 불변 데이터 구조는 동시성 문제를 원천적으로 방지
- **합성성**: 작은 함수들의 합성으로 복잡한 로직 구현 가능
- **부작용 관리**: Effect 시스템으로 I/O와 순수 로직을 명확히 분리

**구현 전략:**
```python
# 순수 함수 우선
def parse_ansi_sequence(data: str) -> ANSISequence:
    # 부작용 없는 순수 변환
    pass

# Effect로 부작용 캡슐화
def read_pty_effect(handle: PTYHandle) -> IOEffect[bytes]:
    return IOEffect(lambda: os.read(handle.fd, 1024))

# 모나드를 통한 안전한 합성
result = (read_pty_effect(handle)
          .bind(decode_utf8)
          .bind(parse_ansi_sequence)
          .bind(update_terminal_state))
```

**트레이드오프:**
- **학습 곡선**: 함수형 프로그래밍 개념 학습 필요
- **성능 고려**: 불변 데이터 구조의 메모리 오버헤드
- **라이브러리 호환성**: 기존 Python 라이브러리들이 주로 OOP 기반
- **장기적 이익**: 버그 감소, 유지보수성 향상, 테스트 커버리지 증가

## 핵심 기술 선택

### 1. PTY 라이브러리 선택: ptyprocess vs subprocess (함수형 관점에서 재검토)

#### 결정: ptyprocess 사용 (함수형 래핑)
**근거:**
- **의사 터미널 지원**: subprocess는 파이프만 제공하지만, ptyprocess는 실제 터미널처럼 동작하는 의사 터미널 제공
- **Effect 시스템 호환**: PTY 작업을 IOEffect로 래핑하여 순수 함수와 분리 가능
- **함수형 인터페이스**: 모든 PTY 작업을 순수 함수 + Effect 조합으로 표현

**함수형 접근법:**
```python
# 순수 함수로 PTY 설정 생성
def create_pty_config(shell: str, env: dict) -> PTYConfig:
    return PTYConfig(shell=shell, env=env)

# Effect로 PTY 생성
def spawn_pty_effect(config: PTYConfig) -> IOEffect[PTYHandle]:
    return IOEffect(lambda: ptyprocess.PtyProcess.spawn(config.shell))

# 순수 함수로 읽기 결과 파싱
def parse_pty_output(data: bytes) -> Result[str, DecodeError]:
    try:
        return Ok(data.decode('utf-8'))
    except UnicodeDecodeError as e:
        return Err(DecodeError(str(e)))
```

**함수형 장점:**
- **테스트 용이성**: PTY 작업을 모킹하여 순수 함수만 테스트
- **합성성**: 여러 PTY 작업을 함수 합성으로 연결
- **에러 처리**: Result 모나드로 PTY 에러를 타입 안전하게 처리

#### 대안 고려사항
- **subprocess**: 단순한 명령 실행에는 충분하지만 터미널 기능 제한적
- **pexpect**: ptyprocess 기반으로 구축되어 더 높은 수준의 추상화 제공하지만 무거움

### 2. 모나드 시스템: 자체 구현 vs 외부 라이브러리

#### 결정: 자체 구현한 경량 모나드 시스템 사용
**근거:**
- **터미널 도메인 특화**: PTY, ANSI 파싱 등 터미널 특화 요구사항에 최적화
- **의존성 최소화**: 복잡한 함수형 라이브러리 의존성 없이 핵심 모나드만 구현
- **학습 곡선 완화**: 프로젝트에 필요한 최소한의 함수형 개념만 도입
- **성능 최적화**: 터미널 I/O에 특화된 Effect 시스템

**구현된 모나드들:**
```python
# Result 모나드: 에러 처리
def parse_ansi_safe(data: str) -> Result[ANSISequence, ParseError]:
    pass

# Maybe 모나드: null 안전성
def find_session(id: str) -> Maybe[Session]:
    pass

# IOEffect 모나드: 부작용 관리
def read_pty_effect(handle: PTYHandle) -> IOEffect[bytes]:
    pass

# State 모나드: 상태 변경 함수형 관리
def update_cursor_position(new_pos: Position) -> State[TerminalState, Unit]:
    pass
```

**트레이드오프:**
- **기능 제한**: 완전한 함수형 라이브러리 대비 기능 제한
- **유지보수**: 자체 구현 모나드의 버그 수정 및 최적화 필요
- **장점**: 프로젝트 요구사항에 맞춘 최적화, 학습 용이성

### 3. 상태 관리: 이벤트 소싱 vs 전통적 상태 관리

#### 결정: 이벤트 소싱 패턴 채택
**근거:**
- **불변성**: 모든 이벤트가 불변이므로 동시성 문제 원천 차단
- **시간 여행 디버깅**: 과거 상태로 되돌아가서 버그 재현 가능
- **감사 추적**: 모든 상태 변경이 이벤트로 기록되어 완벽한 추적 가능
- **함수형 호환**: 상태는 이벤트들의 fold 결과로만 존재

**구현 전략:**
```python
# 불변 이벤트
@dataclass(frozen=True)
class KeyboardEvent:
    timestamp: datetime
    key: str
    modifiers: frozenset[str]

# 이벤트 저장소
@dataclass(frozen=True)
class EventStore:
    events: tuple[Event, ...]

# 상태 재구성
def fold_events(events: tuple[Event, ...]) -> TerminalState:
    return functools.reduce(apply_event, events, TerminalState.initial())
```

**트레이드오프:**
- **메모리 사용량**: 모든 이벤트 저장으로 메모리 사용량 증가
- **복잡성**: 이벤트 설계와 상태 재구성 로직 복잡
- **장점**: 버그 추적 용이성, 완벽한 상태 재현, 동시성 안전성

### 4. 불변 데이터 구조: Pydantic + dataclasses vs 순수 dataclasses

#### 결정: Pydantic 기반 불변 모델 사용
**근거:**
- **불변성 강제**: `frozen=True`와 Pydantic의 불변 설정으로 함수형 원칙 준수
- **타입 안전성**: 런타임 타입 검증으로 순수 함수의 입력 보장
- **함수형 호환**: 불변 객체는 순수 함수의 인자와 반환값으로 안전하게 사용
- **직렬화 지원**: 이벤트 소싱에서 이벤트 직렬화/역직렬화 지원

**함수형 활용:**
```python
@dataclass(frozen=True)
class TerminalState:
    cursor_position: tuple[int, int]
    buffer_content: bytes
    window_size: tuple[int, int]

    @classmethod
    def initial(cls) -> 'TerminalState':
        return cls(
            cursor_position=(0, 0),
            buffer_content=b'',
            window_size=(80, 24)
        )

# 상태 변경은 새 인스턴스 생성
def move_cursor(state: TerminalState, new_pos: tuple[int, int]) -> TerminalState:
    return dataclasses.replace(state, cursor_position=new_pos)
```

**트레이드오프:**
- **메모리 오버헤드**: 상태 변경 시마다 새 객체 생성
- **성능 고려**: 불변 객체 생성 비용 vs 동시성 안전성
- **장점**: 함수형 원칙 준수, 버그 감소, 동시성 안전성

### 5. 테스트 전략: Property-Based Testing vs Unit Testing

#### 결정: Property-Based Testing 우선, Unit Testing 보완
**근거:**
- **순수 함수 검증**: 순수 함수는 속성 기반 테스트로 완벽하게 검증 가능
- **경계 조건 자동 발견**: Hypothesis가 자동으로 엣지 케이스 생성
- **모나드 법칙 검증**: 수학적 법칙을 테스트로 검증하여 정확성 보장
- **회귀 방지**: 속성이 깨지면 즉시 감지 가능

**구현 전략:**
```python
from hypothesis import given, strategies as st

# 순수 함수의 속성 테스트
@given(st.text())
def test_ansi_parsing_idempotent(text: str):
    parsed = parse_ansi_sequence(text)
    reconstructed = reconstruct_ansi_sequence(parsed)
    assert reconstructed == text

# 모나드 법칙 테스트
@given(st.integers())
def test_result_monad_left_identity(value: int):
    f = lambda x: Result.ok(x * 2)
    assert Result.ok(value).bind(f) == f(value)

# Effect 테스트 (모킹)
def test_pty_read_effect():
    mock_effect = IOEffect(lambda: b"test_data")
    result = pty_pipeline(mock_effect)
    assert result.unwrap() == expected_result
```

**트레이드오프:**
- **학습 곡선**: Property-based testing 개념 학습 필요
- **테스트 작성 시간**: 초기 속성 정의 시간 vs 장기적 유지보수 비용
- **장점**: 더 많은 버그 발견, 자동화된 테스트 케이스 생성

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

## CLI 관련 결정사항

### 1. CLI 프레임워크: Typer vs Click vs argparse

#### 결정: Typer (Click 기반) + Rich
**근거:**
- **타입 힌트 기반**: Python 타입 힌트를 사용한 자동 CLI 생성
- **함수형 친화적**: 데코레이터 기반으로 순수 함수와 잘 통합
- **Rich 통합**: 아름다운 터미널 출력과 자연스럽게 결합
- **자동 도움말**: 타입 정보에서 자동으로 도움말 생성
- **서브커맨드**: 복잡한 CLI 구조를 깔끔하게 지원

**구현 전략:**
```python
# Typer를 함수형으로 래핑
@app.command()
def start(...) -> None:
    """명령어 자체는 thin wrapper"""
    effect = create_start_effect(...)  # 실제 로직은 Effect로
    run_effect(effect)  # Effect 실행
```

**트레이드오프:**
- **의존성 추가**: Click과 Typer 모두 필요
- **함수형 래핑**: 명령어 함수를 Effect로 변환하는 추가 작업
- **장점**: 타입 안전성, 자동 문서화, 사용자 친화적 인터페이스

### 2. 세션 녹화 형식: 커스텀 vs 표준

#### 결정: 다중 형식 지원 (JSON 네이티브 + Asciinema + Script)
**근거:**
- **JSON 네이티브**: 이벤트 소싱과 자연스럽게 통합, AI 분석 용이
- **Asciinema**: 널리 사용되는 표준, 웹 재생 지원
- **Script**: Unix 표준 도구와 호환성

**형식별 특징:**
```python
# JSON 네이티브 형식 (기본)
{
    "version": "1.0",
    "metadata": {...},
    "events": [
        {"timestamp": 0.0, "type": "output", "data": "..."},
        {"timestamp": 0.5, "type": "input", "data": "..."}
    ]
}

# Asciinema v2 형식
{
    "version": 2,
    "width": 80,
    "height": 24,
    "timestamp": 1234567890,
    "env": {"SHELL": "/bin/bash"},
    "stdout": [[0.0, "o", "data"], ...]
}
```

**트레이드오프:**
- **복잡성**: 여러 형식 지원으로 코드 복잡도 증가
- **유연성**: 사용자가 필요에 따라 형식 선택 가능
- **호환성**: 기존 도구들과 원활한 통합

### 3. 하이재킹 레벨 설계

#### 결정: 3단계 하이재킹 레벨 시스템
**구조:**
```
minimal:  PTY만 (기본값)
standard: PTY + 키보드
complete: PTY + 키보드 + 마우스 + blessed
```

**근거:**
- **점진적 제어**: 사용자가 필요한 만큼만 제어 수준 선택
- **성능 최적화**: 불필요한 하이재킹으로 인한 오버헤드 방지
- **보안 고려**: 높은 레벨일수록 더 많은 권한 필요

**구현:**
```python
@dataclass(frozen=True)
class HijackingLevel:
    pty: bool = True  # 항상 활성화
    keyboard: bool = False
    mouse: bool = False
    blessed: bool = False

    @classmethod
    def from_string(cls, level: str) -> 'HijackingLevel':
        return {
            'minimal': cls(pty=True),
            'standard': cls(pty=True, keyboard=True),
            'complete': cls(pty=True, keyboard=True, mouse=True, blessed=True)
        }[level]
```

### 4. 프로필 시스템 설계

#### 결정: 계층적 프로필 상속
**구조:**
```
default (내장)
  ├── development (사용자 정의)
  │   └── debug (파생)
  └── production (사용자 정의)
      └── secure (파생)
```

**근거:**
- **재사용성**: 기본 프로필에서 파생하여 중복 최소화
- **유연성**: 환경별 설정을 쉽게 전환
- **일관성**: 모든 프로필이 동일한 구조 따름

**프로필 병합 전략:**
```python
def merge_profiles(base: Profile, override: Profile) -> Profile:
    """프로필 병합 (순수 함수)"""
    return Profile(
        name=override.name,
        parent=base.name,
        settings=merge_settings(base.settings, override.settings)
    )
```

### 5. 실시간 필터링 아키텍처

#### 결정: 파이프라인 기반 필터 체인
**구조:**
```
입력 스트림 → 필터1 → 필터2 → ... → 출력 스트림
```

**필터 타입:**
- **정규식 필터**: 패턴 매칭 기반 필터링
- **의미론적 필터**: 비밀번호, 토큰 등 자동 감지
- **변환 필터**: 대소문자 변환, 색상화 등

**구현:**
```python
# 필터는 순수 함수
Filter = Callable[[str], Maybe[str]]

def compose_filters(filters: list[Filter]) -> Filter:
    """필터 합성 (순수 함수)"""
    def composed(data: str) -> Maybe[str]:
        result = Some(data)
        for filter_fn in filters:
            if result.is_nothing():
                break
            result = result.bind(filter_fn)
        return result
    return composed
```

### 6. 벤치마크 메트릭 선택

#### 결정: 4대 핵심 메트릭 + 비교 기준
**메트릭:**
1. **처리량 (Throughput)**: MB/s 단위, 대량 데이터 처리 능력
2. **지연시간 (Latency)**: ms 단위, 입력-출력 반응 시간
3. **메모리 사용량**: MB 단위, 피크 및 평균
4. **CPU 사용률**: %, 유휴 시간 포함

**비교 기준:**
- `native`: 순수 터미널 (bash)
- `screen`: GNU Screen
- `tmux`: tmux 세션

**측정 방법:**
```python
@dataclass(frozen=True)
class BenchmarkResult:
    metric: str
    value: float
    unit: str
    baseline_ratio: float  # 기준 대비 비율

def run_throughput_benchmark() -> IOEffect[BenchmarkResult]:
    """처리량 벤치마크 (Effect)"""
    return (
        create_test_data_effect(size_mb=100)
        .bind(lambda data: measure_throughput_effect(data))
        .map(calculate_mb_per_second)
        .map(lambda mbps: BenchmarkResult(
            metric="throughput",
            value=mbps,
            unit="MB/s",
            baseline_ratio=mbps / NATIVE_BASELINE
        ))
    )
```

### 7. 대화형 모드 설계

#### 결정: 스트림 기반 REPL with 자동완성
**구조:**
```
입력 스트림 → 파서 → 검증 → 실행 → 포맷팅 → 출력 스트림
     ↑                                            ↓
     └──────────── 자동완성 엔진 ←─────────────────┘
```

**기능:**
- **실시간 자동완성**: 명령어, 옵션, 파일명
- **히스토리**: 화살표 키로 이전 명령어
- **인라인 도움말**: 입력 중 도움말 표시
- **상태 표시**: 현재 세션 정보 상단 표시

**구현:**
```python
def create_interactive_pipeline() -> IOEffect[AsyncStream[CommandResult]]:
    """대화형 파이프라인 생성"""
    return (
        create_input_stream_effect()
        .map(lambda stream:
            stream
            .map(enrich_with_completions)
            .map(parse_interactive_command)
            .filter(is_valid_command)
            .map(execute_command_effect)
            .map(format_result_with_colors)
        )
    )
```

### 8. 플러그인 보안 모델

#### 결정: 샌드박스 + 권한 기반 시스템
**보안 레벨:**
1. **읽기 전용**: 데이터 읽기만 가능
2. **필터링**: 데이터 변환 가능
3. **전체 제어**: 모든 기능 접근 (신뢰된 플러그인만)

**샌드박스 구현:**
```python
@dataclass(frozen=True)
class PluginPermissions:
    read_session: bool = True
    modify_output: bool = False
    access_network: bool = False
    access_filesystem: bool = False

def create_plugin_sandbox(permissions: PluginPermissions) -> PluginSandbox:
    """플러그인 샌드박스 생성"""
    return PluginSandbox(
        allowed_modules=get_allowed_modules(permissions),
        resource_limits=get_resource_limits(permissions),
        capability_filter=create_capability_filter(permissions)
    )
```

이러한 기술적 결정사항들은 term2ai가 안정적이고 확장 가능하며 고성능인 터미널 래퍼가 되도록 하는 기반을 제공합니다.

## 실용적 개선 방향 (2025-06-22 업데이트)

### 1. 복잡성 감소
- **자체 모나드 시스템 → 검증된 라이브러리 또는 간단한 Result 타입**
  - 초기: 간단한 Result/Maybe 타입만 사용
  - 필요시: `returns` 같은 검증된 라이브러리 도입
  - 목표: 버그 위험 감소, 유지보수성 향상

- **다층 하이재킹 → 기본 PTY + 선택적 blessed**
  - 초기: PTY만으로 기본 기능 구현
  - 필요시: blessed만 추가하여 터미널 제어
  - 제외: keyboard/pynput은 특수 요구사항이 있을 때만

- **Property-Based Testing 우선 → Unit Testing 우선**
  - 기본: 모든 코드에 단위 테스트
  - 선택적: 핵심 순수 함수에만 Property-Based Testing
  - 목표: 빠른 개발과 즉각적인 피드백

### 2. 점진적 개발 전략
1. **Phase 1: 기본 구현 (OOP)**
   - 전통적인 Python 패턴으로 기본 기능 구현
   - Context Manager로 리소스 관리
   - 기본적인 PTY 래퍼 완성

2. **Phase 2: 실용적 함수형 전환**
   - 핵심 로직만 순수 함수로 분리
   - 간단한 Result 타입으로 에러 처리
   - 기존 코드와 공존하는 하이브리드 접근

3. **Phase 3: 선택적 고급 기능**
   - 성능 요구시 uvloop 적용
   - 복잡한 기능 요구시 이벤트 소싱
   - 필요시에만 고급 패턴 도입

### 3. 80/20 원칙 적용
- **80% 실용성**: 기존 Python 패턴과 라이브러리 활용
- **20% 함수형**: 핵심 비즈니스 로직만 순수 함수로
- **목표**: 실제로 작동하는 제품을 빠르게 출시

### 4. 기술 부채 관리
- **문서화**: 모든 타협점과 향후 개선 방향 명시
- **리팩토링 계획**: 점진적 개선을 위한 로드맵
- **테스트 커버리지**: 최소 80% 유지하며 품질 보장
