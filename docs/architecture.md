# 실용적 아키텍처 개요

## 시스템 아키텍처

term2ai 터미널 래퍼는 **실용적 함수형 프로그래밍 접근법**을 기반으로 설계된 터미널 제어 시스템입니다. 핵심 비즈니스 로직은 순수 함수로 구현하되, 과도한 추상화를 피하고 실제 필요한 기능에 집중합니다. 기존 터미널 애플리케이션과의 호환성을 유지하면서 점진적으로 개선 가능한 구조를 제공합니다.

### 함수형 아키텍처 레이어

```
┌─────────────────────────────────────────────────────────────┐
│            Application Layer (합성된 Effect들)                │
├─────────────────────────────────────────────────────────────┤
│  Event Streams    │  Function Pipelines │  UI Renderers     │
│  (비동기 스트림)     │  (순수 함수 합성)      │  (블레스드 제어)     │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer (순수 함수들)                           │
│  • ANSI 파싱      • 데이터 변환      • 입력 검증             │
│  • 출력 포맷팅    • 패턴 분석       • 상태 변환              │
├─────────────────────────────────────────────────────────────┤
│  Effect Management Layer (모나드 시스템)                      │
│  • IOEffect      • Result          • Maybe                 │
│  • State         • Reader          • Writer                │
├─────────────────────────────────────────────────────────────┤
│  Event Sourcing Layer (이벤트 저장소)                        │
│  • 이벤트 스트림  • 상태 재구성     • 시간 여행 디버깅         │
├─────────────────────────────────────────────────────────────┤
│  System Interface Layer (Unix I/O Effects)                │
│  • PTY Effects   • 파일 Effects    • 네트워크 Effects       │
├─────────────────────────────────────────────────────────────┤
│                   운영 체제 (Unix)                            │
└─────────────────────────────────────────────────────────────┘
```

### 실용적 터미널 제어 접근법

term2ai는 **단계적이고 실용적인 접근**을 통해 터미널 I/O 제어를 구현합니다:

```
Phase 1: 기본 PTY 제어 (현재 구현)
┌─────────────────────────────────────────────────────┐
│ PTY Process     →    Basic I/O    →    Terminal    │
│ (ptyprocess)         (read/write)      (stdout)     │
└─────────────────────────────────────────────────────┘

Phase 2: 핵심 로직 함수형 전환 (계획)
┌─────────────────────────────────────────────────────┐
│ PTY Wrapper  →  Pure Functions  →  Simple Effects  │
│ (OOP 기반)      (데이터 변환)        (I/O 래핑)       │
└─────────────────────────────────────────────────────┘

Phase 3: 고급 기능 선택적 추가 (선택사항)
┌─────────────────────────────────────────────────────┐
│ • blessed (필요시)                                   │
│ • keyboard hooks (특정 기능 요구시)                   │
│ • Event sourcing (감사 추적 필요시)                   │
└─────────────────────────────────────────────────────┘
```

**실용적 설계 원칙:**
- 필요한 기능만 구현 (YAGNI 원칙)
- 검증된 라이브러리 활용
- 점진적 복잡도 증가
- 실제 사용 사례 기반 설계

### 함수형 레이어 설명

#### Application Layer (애플리케이션 계층)
- **목적**: 최종 사용자 기능의 함수형 합성
- **구성요소**: Effect 합성, 스트림 처리, UI 렌더링
- **특징**: 모든 기능이 순수 함수와 Effect의 합성으로 구현
- **예시**: `terminal_session = pipe(create_pty_stream, filter_ansi, render_ui)`

#### Business Logic Layer (비즈니스 로직 계층)
- **목적**: 도메인 로직의 순수 함수 구현
- **구성요소**:
  - `parse_ansi_sequence: str -> ANSISequence`
  - `transform_input: KeyEvent -> Maybe[Action]`
  - `validate_terminal_state: TerminalState -> Result[TerminalState, ValidationError]`
- **특징**: 완전히 순수하고 테스트 가능한 함수들
- **부작용**: 없음 (순수 함수만)

#### Effect Management Layer (Effect 관리 계층)
- **목적**: 부작용의 명시적 관리 및 합성
- **구성요소**:
  - `IOEffect[T]`: I/O 작업 캡슐화
  - `Result[T, E]`: 성공/실패 타입 안전 처리
  - `Maybe[T]`: null 안전성
  - `State[S, A]`: 상태 변경 함수형 관리
- **특징**: 모나드 법칙을 만족하는 타입 안전한 합성
- **예시**: `read_pty_effect.bind(parse_data).bind(update_state)`

#### Event Sourcing Layer (이벤트 소싱 계층)
- **목적**: 모든 상태 변경을 이벤트로 기록하고 재생
- **구성요소**:
  - `Event`: 불변 이벤트 타입
  - `EventStore`: 이벤트 컬렉션
  - `fold_events: [Event] -> ApplicationState`
- **특징**: 상태는 이벤트의 fold 결과로만 존재
- **장점**: 시간 여행 디버깅, 완벽한 감사 추적

#### System Interface Layer (시스템 인터페이스 계층)
- **목적**: Unix 시스템 호출을 Effect로 래핑
- **구성요소**:
  - `pty_read_effect: PTYHandle -> IOEffect[bytes]`
  - `file_write_effect: FilePath -> Content -> IOEffect[Unit]`
  - `signal_handler_effect: Signal -> IOEffect[Unit]`
- **특징**: 모든 부작용이 명시적으로 Effect 타입에 표현됨
- **Unix 최적화**: epoll/kqueue 기반 고성능 비동기 I/O

## 함수형 데이터 흐름

### 입력 이벤트 스트림 처리
```
KeyboardEvent | MouseEvent | PTYEvent
              ↓
        async_stream_merge
              ↓
   filter_relevant_events: Event -> Maybe[Event]
              ↓
   parse_event_data: Event -> Result[ParsedEvent, ParseError]
              ↓
   validate_event: ParsedEvent -> Result[ValidEvent, ValidationError]
              ↓
   transform_to_action: ValidEvent -> Maybe[Action]
              ↓
   append_to_event_store: Action -> IOEffect[EventStore]
```

### 상태 재구성 파이프라인
```
EventStore
    ↓
fold_events: (State, Event) -> State
    ↓
current_terminal_state: TerminalState
    ↓
derive_ui_model: TerminalState -> UIModel
    ↓
render_ui: UIModel -> IOEffect[Unit]
```

### Effect 합성 체인
```
read_pty_effect: IOEffect[bytes]
    ↓ (bind)
decode_utf8: bytes -> Result[str, UnicodeError]
    ↓ (bind)
parse_ansi: str -> Result[ANSISequence[], ParseError]
    ↓ (bind)
update_terminal_state: ANSISequence[] -> State[TerminalState, Unit]
    ↓ (bind)
emit_ui_update: TerminalState -> IOEffect[Unit]
```

## 실용적 함수형 설계 원칙

### 1. 선택적 순수성 (Selective Purity)
- **핵심 비즈니스 로직**만 순수 함수로 구현
- 데이터 변환, 파싱, 검증 등에 집중
- I/O는 기존 방식 유지, 필요시 래핑
- 80/20 원칙: 20%의 순수 함수로 80%의 이익

### 2. 실용적 불변성 (Pragmatic Immutability)
- Pydantic 모델로 타입 안전성 확보
- 성능이 중요한 부분은 가변 허용
- 불변성은 도구이지 목적이 아님
- 필요한 곳에만 선택적 적용

### 3. 단순한 합성 (Simple Composition)
- 복잡한 모나드 체인 대신 단순 함수 호출
- 표준 Python 기능 우선 활용
- 가독성을 해치지 않는 선에서 합성
- 디버깅 가능한 코드 유지

### 4. 명확한 에러 처리
- 기본 Exception 활용, 필요시 Result 타입
- 과도한 타입 래핑 지양
- Python의 관용적 에러 처리 존중
- 실용적인 에러 메시지

### 5. 점진적 개선
- 작동하는 코드부터 시작
- 필요에 따라 함수형 개념 도입
- 리팩토링을 통한 점진적 개선
- 실제 문제 해결에 집중

### 6. 필요시 고급 기능
- Event sourcing은 감사 추적 필요시만
- 모나드는 복잡한 에러 처리시만
- Effect 시스템은 테스트 격리 필요시만
- YAGNI (You Aren't Gonna Need It) 원칙

## 함수형 구성요소 상호작용

### 순수 함수 모듈들
```python
# 데이터 변환 순수 함수들
parse_ansi_sequence: str -> ANSISequence
decode_keyboard_event: RawInput -> KeyboardEvent
validate_terminal_state: TerminalState -> Result[TerminalState, ValidationError]
format_output: Content -> Style -> StyledOutput
analyze_input_pattern: [Event] -> PatternAnalysis
```

### Effect 기반 I/O 시스템
```python
# 모든 I/O가 Effect로 래핑됨
pty_read_effect: PTYHandle -> IOEffect[bytes]
file_write_effect: Path -> Content -> IOEffect[Unit]
keyboard_listen_effect: () -> IOEffect[AsyncStream[KeyEvent]]
terminal_render_effect: UIModel -> IOEffect[Unit]

# Effect 합성을 통한 복잡한 I/O 작업
session_logging_effect =
    read_pty_effect
    .bind(parse_ansi)
    .bind(filter_sensitive_data)
    .bind(append_to_log_file)
```

### 이벤트 스트림 처리
```python
# 비동기 스트림들의 합성
keyboard_stream: AsyncStream[KeyboardEvent]
mouse_stream: AsyncStream[MouseEvent]
pty_stream: AsyncStream[PTYEvent]

# 스트림 변환 파이프라인
unified_stream = merge_streams([keyboard_stream, mouse_stream, pty_stream])
    .map(normalize_event)
    .filter(is_relevant_event)
    .scan(fold_to_state, initial_state)
```

### 상태 관리 (이벤트 소싱)
```python
# 불변 이벤트 저장소
@dataclass(frozen=True)
class EventStore:
    events: tuple[Event, ...]

# 상태 재구성 함수
def fold_events(events: tuple[Event, ...]) -> ApplicationState:
    return functools.reduce(apply_event, events, ApplicationState.initial())

# 상태 업데이트 (새 이벤트 추가)
def append_event(store: EventStore, event: Event) -> EventStore:
    return EventStore(events=store.events + (event,))
```

### 모나드 기반 에러 처리
```python
# 연쇄적 연산에서 안전한 에러 처리
def safe_terminal_operation(input_data: str) -> Result[TerminalState, Error]:
    return (
        Result.ok(input_data)
        .bind(validate_input)
        .bind(parse_commands)
        .bind(execute_commands)
        .bind(update_terminal_state)
    )

# Maybe를 통한 null 안전성
def find_active_session(session_id: str) -> Maybe[Session]:
    session = session_store.get(session_id)
    return Some(session) if session else Nothing()
```

### 플러그인 시스템 (함수형 확장)
```python
# 플러그인은 순수 함수로 정의
PluginFunction = Callable[[Event], Maybe[Event]]

# 플러그인 합성
def apply_plugins(plugins: list[PluginFunction], event: Event) -> Event:
    return functools.reduce(
        lambda e, plugin: plugin(e).unwrap_or(e),
        plugins,
        event
    )
```

## 설정 아키텍처

### 설정 소스
1. **기본 설정**: 내장 기본값
2. **시스템 설정**: 시스템 전체 설정
3. **사용자 설정**: 사용자별 설정
4. **환경 변수**: 런타임 오버라이드
5. **명령줄 인수**: 실행시 오버라이드

### 설정 계층구조
```
명령줄 인수 > 환경변수 > 사용자 설정 > 시스템 설정 > 기본값
```

## 오류 처리 전략

### 오류 범주
1. **시스템 오류**: OS 수준 실패 (권한, 리소스)
2. **프로토콜 오류**: 터미널 프로토콜 위반
3. **설정 오류**: 잘못된 설정 또는 매개변수
4. **플러그인 오류**: 플러그인 로딩 또는 실행 실패
5. **네트워크 오류**: 네트워크 관련 실패

### 오류 처리 패턴
- **우아한 성능 저하**: 기능 축소로 작업 계속
- **재시도 로직**: 일시적 실패에 대한 자동 재시도
- **사용자 알림**: 명확한 오류 메시지 및 복구 안내
- **로깅**: 디버깅을 위한 포괄적인 오류 로깅
- **예외 안전성**: Context manager를 통한 예외 발생 시 리소스 보장 정리
- **RAII 패턴**: 리소스 획득과 동시에 해제 보장

## 보안 고려사항

### 입력 검증
- 모든 사용자 입력의 검증 및 살균
- 인젝션 공격 방지를 위한 ANSI 시퀀스 검증
- 설정 매개변수 검증

### 프로세스 격리
- 자식 프로세스는 적절한 권한으로 실행
- 플러그인 기능 제한을 위한 플러그인 샌드박싱
- 리소스 고갈 방지를 위한 리소스 제한

### 데이터 보호
- 세션 기록에서 민감한 데이터 암호화
- 인증 자격 증명의 안전한 처리
- 개인정보 보호를 고려한 AI 통합 옵션

## 성능 특성

### 예상 성능

#### 성능 목표 (Unix 전용)
- **I/O 지연시간**: < 3ms (uvloop + epoll/kqueue 최적화)
- **처리량**: > 300MB/s (기본 asyncio 대비 3-5배 향상)
- **메모리 사용량**: < 60MB (Unix 메모리 관리 최적화)
- **CPU 사용량**: < 2% (네이티브 Unix I/O 성능)

### 최적화 전략

#### 비동기 I/O 최적화
- **uvloop 활용**: libuv 기반 고성능 이벤트 루프
- **aiofiles 통합**: 비동기 파일 I/O로 블로킹 방지
- **최적화 라이브러리**: Unix 전용 고성능 라이브러리 활용

#### 메모리 및 버퍼 최적화
- **계층적 버퍼링**: 커널 → 애플리케이션 → 사용자 버퍼
- **객체 풀링**: 자주 사용되는 버퍼 객체 재사용
- **적응적 크기**: 워크로드에 따른 동적 버퍼 크기 조정

#### 시그널 및 동시성 최적화
- **aiosignal 통합**: 비동기 시그널 처리로 I/O 블로킹 방지
- **epoll 활용**: Linux/Unix 최적화된 다중 스트림 처리
- **Context manager 최적화**: RAII 패턴으로 리소스 관리 오버헤드 최소화

## 실용적 테스트 전략

### 테스트 우선순위
1. **단위 테스트 우선**: 기본 pytest로 핵심 로직 테스트
2. **통합 테스트**: 실제 PTY 동작 검증
3. **E2E 테스트**: 사용자 시나리오 기반
4. **Property-based (선택)**: 복잡한 로직에만 적용
5. **성능 테스트**: 실제 병목 현상 발생시

### 실용적 테스트 기법
```python
# 기본 단위 테스트
def test_parse_ansi_sequence():
    """간단하고 명확한 테스트"""
    result = parse_ansi_sequence("\x1b[31m")
    assert result.color == "red"
    assert result.type == "color"

# 통합 테스트
def test_pty_basic_io():
    """실제 PTY 동작 테스트"""
    with PTYWrapper() as pty:
        pty.write("echo hello\n")
        output = pty.read()
        assert "hello" in output

# Property-based는 필요시만
@given(st.text())
def test_data_encoding_safety(text: str):
    """인코딩 안전성 검증"""
    try:
        encoded = encode_for_pty(text)
        decoded = decode_from_pty(encoded)
        assert isinstance(decoded, str)
    except UnicodeError:
        # 예상된 에러는 통과
        pass
```

## 지원 플랫폼

### Unix 계열 전용 지원

| 플랫폼 | aiofiles | uvloop | aiosignal | 예상 성능 | 권장 설치 |
|--------|----------|---------|-----------|-----------|-----------|
| **Linux** | ✅ | ✅ | ✅ | 최고 (< 3ms, > 300MB/s) | `uv sync --group performance` |
| **macOS** | ✅ | ✅ | ✅ | 최고 (< 3ms, > 300MB/s) | `uv sync --group performance` |

### Unix 계열 설치 가이드

#### Linux/macOS 전용 설치
```bash
# 전체 성능 최적화 설치
uv sync --group performance

# 환경 확인
python -c "
import sys, uvloop, aiosignal
print(f'플랫폼: {sys.platform}')
print(f'uvloop: {uvloop.__version__}')
print(f'aiosignal: {aiosignal.__version__}')
print('✅ Unix 최적 성능 구성 완료')
"
```

### Unix 전용 최적화 설정

```python
import asyncio
import uvloop

# Unix 전용 최적화 설정
def setup_unix_optimization():
    """비동기 이벤트 루프 최적화 설정"""
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def get_expected_performance() -> dict:
    """고성능 Unix 예상 성능 지표"""
    return {
        'latency': '<3ms',
        'throughput': '>300MB/s',
        'memory': '<60MB',
        'cpu': '<2%'
    }

# 사용 예시
setup_unix_optimization()
print(f"예상 성능: {get_expected_performance()}")
```

### 개발 환경 권장사항

#### CI/CD 환경
- **GitHub Actions**: Linux runner에서 `uv sync --group performance`
- **GitLab CI**: Docker 이미지에 uvloop 사전 설치
- **Travis CI**: Linux/macOS 환경에서 테스트

#### 개발자 환경
- **Linux 개발자**: 성능 그룹 필수 설치
- **macOS 개발자**: 성능 그룹 필수 설치
- **Unix 전용 테스트**: 의존성 그룹별 테스트 자동화

## CLI 아키텍처

### CLI 명령어 처리 파이프라인

Term2AI의 CLI는 함수형 프로그래밍 패러다임을 따라 모든 명령어 처리를 순수 함수와 Effect 시스템으로 구현합니다:

```
사용자 입력 (CLI 명령어)
        ↓
┌─────────────────────────────────────────────────────┐
│          순수 함수 명령어 파싱 레이어                  │
│  • parse_cli_args: list[str] -> Result[Command]    │
│  • validate_options: Options -> Result[Options]    │
│  • generate_help: Command -> str                   │
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│            Effect 명령어 실행 레이어                  │
│  • start_session_effect: Config -> IOEffect[Session]│
│  • show_stats_effect: ID -> IOEffect[Stats]        │
│  • manage_config_effect: Action -> IOEffect[Config]│
└─────────────────┬───────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────┐
│          출력 포맷팅 및 렌더링 레이어                 │
│  • format_output: Result -> str (순수 함수)        │
│  • render_table: Data -> Table (Rich 통합)         │
│  • apply_colors: Text -> StyledText                │
└─────────────────────────────────────────────────────┘
```

### CLI 모듈 구조

```
src/term2ai/cli/
├── main.py           # Typer 앱 엔트리포인트
├── commands/         # 명령어 구현
│   ├── start.py      # 세션 시작 명령어
│   ├── stats.py      # 통계 명령어
│   ├── config.py     # 설정 관리 명령어
│   ├── doctor.py     # 시스템 진단 명령어
│   ├── interactive.py # 대화형 모드
│   ├── record.py     # 세션 녹화
│   ├── replay.py     # 세션 재생
│   ├── analyze.py    # 세션 분석
│   ├── benchmark.py  # 성능 측정
│   └── profile.py    # 프로필 관리
├── parsers/          # 순수 함수 파서
│   ├── args.py       # 인자 파싱
│   ├── options.py    # 옵션 검증
│   └── config.py     # 설정 파싱
├── effects/          # Effect 시스템
│   ├── session.py    # 세션 관련 Effect
│   ├── io.py         # I/O Effect
│   └── config.py     # 설정 Effect
├── formatters/       # 출력 포맷터
│   ├── table.py      # 테이블 포맷
│   ├── json.py       # JSON 포맷
│   └── progress.py   # 진행률 표시
└── interactive/      # 대화형 모드
    ├── stream.py     # 입력 스트림 처리
    ├── completion.py # 자동완성
    └── prompt.py     # 프롬프트 관리
```

### 함수형 CLI 설계 패턴

#### 1. 명령어 파싱 (순수 함수)
```python
# 모든 파싱은 부작용 없는 순수 함수
def parse_cli_args(args: list[str]) -> Result[CLICommand, ParseError]:
    """CLI 인자를 파싱하여 명령어 객체 생성"""
    if not args:
        return Err(ParseError("No command provided"))

    command_name = args[0]
    options = parse_options(args[1:])

    return Ok(CLICommand(name=command_name, options=options))

def validate_cli_options(command: CLICommand) -> Result[CLICommand, ValidationError]:
    """명령어 옵션의 유효성 검증"""
    validators = get_validators_for_command(command.name)

    for validator in validators:
        result = validator(command.options)
        if result.is_err():
            return result

    return Ok(command)
```

#### 2. Effect 기반 명령어 실행
```python
# 모든 부작용은 IOEffect로 캡슐화
def execute_command(command: CLICommand) -> IOEffect[CommandResult]:
    """명령어를 실행하는 Effect 생성"""

    # Effect 딕셔너리에서 적절한 Effect 선택
    effect_map = {
        'start': start_terminal_session_effect,
        'stats': show_session_stats_effect,
        'config': manage_config_effect,
        'doctor': run_diagnostics_effect,
    }

    effect_fn = effect_map.get(command.name, unknown_command_effect)
    return effect_fn(command.options)

# Effect 합성을 통한 복잡한 명령어
def start_terminal_session_effect(options: CLIOptions) -> IOEffect[Session]:
    """터미널 세션을 시작하는 Effect 체인"""
    return (
        validate_environment_effect()
        .bind(lambda _: load_config_effect(options.config_path))
        .bind(lambda config: create_pty_effect(config))
        .bind(lambda pty: setup_hijacking_effect(pty, options.hijack_level))
        .bind(lambda hijacker: create_session_effect(hijacker))
        .map(lambda session: log_session_start(session))
    )
```

#### 3. 대화형 모드 스트림 처리
```python
# 사용자 입력을 함수형 스트림으로 처리
def create_interactive_stream() -> IOEffect[AsyncStream[UserInput]]:
    """대화형 모드의 입력 스트림 생성"""
    return IOEffect(lambda: create_async_input_stream())

def process_interactive_commands(
    stream: AsyncStream[UserInput]
) -> AsyncStream[CommandResult]:
    """입력 스트림을 명령어 결과 스트림으로 변환"""
    return (
        stream
        .map(parse_interactive_input)      # 순수 함수
        .filter(is_valid_command)          # 순수 함수
        .map(create_command_effect)        # Effect 생성
        .map(execute_effect_async)         # Effect 실행
        .map(format_command_result)        # 순수 함수
    )
```

#### 4. 설정 관리 시스템
```python
# 불변 설정 객체와 순수 함수 조작
@dataclass(frozen=True)
class CLIConfig:
    shell: str = "/bin/bash"
    hijack_level: str = "minimal"
    filters: tuple[str, ...] = ()
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

def merge_configs(base: CLIConfig, override: CLIConfig) -> CLIConfig:
    """두 설정을 병합하는 순수 함수"""
    return CLIConfig(
        shell=override.shell or base.shell,
        hijack_level=override.hijack_level or base.hijack_level,
        filters=base.filters + override.filters,
        performance=merge_performance_configs(base.performance, override.performance)
    )

def apply_cli_overrides(config: CLIConfig, options: CLIOptions) -> CLIConfig:
    """CLI 옵션으로 설정을 오버라이드"""
    overrides = CLIConfig(
        shell=options.shell,
        hijack_level=options.hijack_level,
        filters=tuple(options.filters or [])
    )
    return merge_configs(config, overrides)
```

#### 5. 세션 녹화 시스템
```python
# 이벤트 소싱 기반 세션 녹화
@dataclass(frozen=True)
class SessionEvent:
    timestamp: datetime
    event_type: str
    data: dict

def record_session_events(session: Session) -> IOEffect[AsyncStream[SessionEvent]]:
    """세션 이벤트를 기록하는 스트림 생성"""
    return (
        create_event_stream_effect(session)
        .map(lambda stream:
            stream
            .map(create_session_event)     # 순수 함수
            .scan(EventStore.empty(), append_event)  # 이벤트 누적
        )
    )

def replay_session_events(events: list[SessionEvent]) -> IOEffect[None]:
    """녹화된 세션을 재생"""
    return sequence_effects([
        replay_event_effect(event, calculate_delay(event, next_event))
        for event, next_event in zip(events, events[1:] + [None])
    ])
```

### CLI 하이재킹 레벨 아키텍처

```
하이재킹 레벨 설정:
┌─────────────────────────────────────────────────────┐
│ minimal:  PTY만 사용                                │
│           └─> PTYWrapper + 기본 I/O                 │
├─────────────────────────────────────────────────────┤
│ standard: PTY + 키보드 캡처                         │
│           └─> PTYWrapper + keyboard 라이브러리      │
├─────────────────────────────────────────────────────┤
│ complete: PTY + 키보드 + 마우스 + blessed           │
│           └─> 완전한 터미널 제어                    │
└─────────────────────────────────────────────────────┘
```

### CLI 성능 최적화

#### 1. 명령어 파싱 최적화
- 파서 결과 캐싱
- 정규식 사전 컴파일
- 지연 평가 활용

#### 2. Effect 실행 최적화
- Effect 배치 처리
- 병렬 Effect 실행
- 리소스 풀링

#### 3. 출력 렌더링 최적화
- 증분 렌더링
- 버퍼링된 출력
- 비동기 렌더링

### CLI 테스트 전략

#### 1. Property-Based CLI 테스트
```python
@given(st.lists(st.text()))
def test_cli_parsing_properties(args: list[str]):
    """CLI 파싱의 수학적 속성 검증"""
    result = parse_cli_args(args)

    # 속성 1: 파싱은 결정적이다
    assert parse_cli_args(args) == result

    # 속성 2: 유효한 명령어는 항상 파싱 가능
    if result.is_ok():
        formatted = format_command(result.unwrap())
        reparsed = parse_cli_args(formatted.split())
        assert reparsed.is_ok()
```

#### 2. Effect 모킹 테스트
```python
def test_command_effects_with_mocking():
    """Effect를 모킹하여 명령어 로직 테스트"""
    mock_pty_effect = IOEffect.pure(MockPTYHandle())
    mock_config_effect = IOEffect.pure(MockConfig())

    # Effect 주입을 통한 테스트
    result = run_command_with_effects(
        command="start",
        pty_effect=mock_pty_effect,
        config_effect=mock_config_effect
    )

    assert result.is_ok()
```

이 아키텍처는 Unix 계열 전용 최적화를 통해 최대 성능을 달성하며 견고하고 확장 가능한 터미널 래퍼를 구축하기 위한 견고한 기반을 제공합니다.

## 실용적 개선 노트 (2025-06-22 업데이트)

### 현재 상태
- Phase 1 (기본 PTY 래퍼) 구현 완료
- 과도한 함수형 설계를 실용적 접근으로 전환 중
- 핵심 기능 동작 확인, 점진적 개선 진행

### 권장 개발 방향
1. **작동하는 MVP 우선**: 기본 터미널 기능부터 완성
2. **점진적 함수형 도입**: 필요한 부분만 순수 함수로 추출
3. **실제 사용 피드백**: 사용자 요구사항 기반 기능 추가
4. **성능 측정 후 최적화**: 실제 병목 지점만 개선

### 피해야 할 것들
- 모든 것을 모나드로 래핑
- 과도한 타입 추상화
- 불필요한 함수형 라이브러리 도입
- Property-based testing 강제
- 3중 하이재킹 시스템

### 집중해야 할 것들
- 안정적인 PTY 처리
- 명확한 에러 메시지
- 간단한 CLI 인터페이스
- 실용적인 테스트
- 점진적 개선
