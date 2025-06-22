# Term2AI 함수형 패턴 가이드

## 개요

이 문서는 Term2AI에서 사용하는 함수형 프로그래밍 패턴과 모범 사례를 설명합니다. Term2AI는 순수 함수, 모나드, Effect 시스템을 통해 예측 가능하고 테스트 가능한 코드를 구현합니다.

## 핵심 원칙

### 1. 순수성 (Purity)
모든 비즈니스 로직은 순수 함수로 구현합니다. 순수 함수는:
- 동일한 입력에 대해 항상 동일한 출력 생성
- 부작용(side effects) 없음
- 외부 상태에 의존하지 않음

```python
# 순수 함수 예시
def parse_ansi_sequence(data: str) -> ANSISequence:
    """ANSI 시퀀스를 파싱하는 순수 함수"""
    # 외부 상태나 I/O 없이 순수하게 변환만 수행
    if data.startswith('\x1b['):
        return ANSISequence(type='escape', content=data)
    return ANSISequence(type='text', content=data)

# 비순수 함수 (피해야 할 패턴)
def bad_parse_ansi(data: str) -> ANSISequence:
    print(f"Parsing: {data}")  # 부작용!
    global counter
    counter += 1  # 외부 상태 변경!
    return ANSISequence(...)
```

### 2. 불변성 (Immutability)
모든 데이터 구조는 불변으로 설계합니다:

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class TerminalState:
    cursor_position: tuple[int, int]
    buffer_content: str
    window_size: tuple[int, int]

# 상태 변경은 새 객체 생성으로
def move_cursor(state: TerminalState, new_pos: tuple[int, int]) -> TerminalState:
    """커서 이동 (새 상태 생성)"""
    return replace(state, cursor_position=new_pos)

# 잘못된 패턴 (피해야 함)
def bad_move_cursor(state: TerminalState, new_pos: tuple[int, int]) -> None:
    state.cursor_position = new_pos  # 에러! frozen=True
```

### 3. 합성성 (Composability)
작은 함수들을 합성하여 복잡한 기능을 구현합니다:

```python
from functools import compose

# 작은 순수 함수들
def trim_whitespace(s: str) -> str:
    return s.strip()

def to_uppercase(s: str) -> str:
    return s.upper()

def add_prefix(prefix: str) -> Callable[[str], str]:
    return lambda s: f"{prefix}{s}"

# 함수 합성
process_command = compose(
    add_prefix("CMD: "),
    to_uppercase,
    trim_whitespace
)

# 사용
result = process_command("  hello world  ")  # "CMD: HELLO WORLD"
```

## 모나드 시스템

### Result 모나드
에러 처리를 타입 안전하게 수행합니다:

```python
from typing import TypeVar, Generic, Callable
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def bind(self, f: Callable[[T], 'Result[T, E]']) -> 'Result[T, E]':
        return f(self.value)

    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        return Ok(f(self.value))

    def is_ok(self) -> bool:
        return True

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def bind(self, f: Callable[[T], 'Result[T, E]']) -> 'Result[T, E]':
        return self

    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        return self

    def is_err(self) -> bool:
        return True

Result = Ok[T] | Err[E]

# 사용 예시
def parse_int(s: str) -> Result[int, str]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"'{s}' is not a valid integer")

def double(n: int) -> Result[int, str]:
    return Ok(n * 2)

# Result 체이닝
result = (
    parse_int("42")
    .bind(double)
    .bind(double)
)  # Ok(168)

# 에러 전파
error_result = (
    parse_int("not a number")
    .bind(double)
    .bind(double)
)  # Err("'not a number' is not a valid integer")
```

### Maybe 모나드
null 안전성을 보장합니다:

```python
@dataclass(frozen=True)
class Some(Generic[T]):
    value: T

    def bind(self, f: Callable[[T], 'Maybe[T]']) -> 'Maybe[T]':
        return f(self.value)

    def unwrap_or(self, default: T) -> T:
        return self.value

@dataclass(frozen=True)
class Nothing:
    def bind(self, f: Callable[[T], 'Maybe[T]']) -> 'Maybe[T]':
        return self

    def unwrap_or(self, default: T) -> T:
        return default

Maybe = Some[T] | Nothing

# 사용 예시
def find_config(key: str) -> Maybe[str]:
    config = {"shell": "/bin/bash", "theme": "dark"}
    return Some(config[key]) if key in config else Nothing()

# 안전한 체이닝
shell = (
    find_config("shell")
    .bind(lambda s: Some(s.upper()) if s else Nothing())
    .unwrap_or("/bin/sh")
)
```

### IOEffect 모나드
모든 I/O 작업을 캡슐화합니다:

```python
@dataclass(frozen=True)
class IOEffect(Generic[T]):
    effect: Callable[[], T]

    def run(self) -> T:
        """Effect 실행 (부작용 발생)"""
        return self.effect()

    def bind(self, f: Callable[[T], 'IOEffect[T]']) -> 'IOEffect[T]':
        def chained_effect():
            result = self.run()
            return f(result).run()
        return IOEffect(chained_effect)

    def map(self, f: Callable[[T], T]) -> 'IOEffect[T]':
        return IOEffect(lambda: f(self.run()))

# 순수 함수로 Effect 생성
def read_file_effect(path: str) -> IOEffect[str]:
    return IOEffect(lambda: open(path).read())

def write_file_effect(path: str, content: str) -> IOEffect[None]:
    return IOEffect(lambda: open(path, 'w').write(content))

# Effect 합성
def process_file_effect(input_path: str, output_path: str) -> IOEffect[None]:
    return (
        read_file_effect(input_path)
        .map(str.upper)
        .bind(lambda content: write_file_effect(output_path, content))
    )

# 실행은 최상위 레벨에서만
if __name__ == "__main__":
    process_file_effect("input.txt", "output.txt").run()
```

## CLI에서의 함수형 패턴

### 명령어 파싱
모든 CLI 파싱은 순수 함수로 구현합니다:

```python
from typing import NamedTuple

class CLICommand(NamedTuple):
    name: str
    options: dict[str, Any]
    args: list[str]

def parse_cli_args(args: list[str]) -> Result[CLICommand, str]:
    """CLI 인자를 파싱하는 순수 함수"""
    if not args:
        return Err("No command provided")

    command_name = args[0]
    options = {}
    positional = []

    i = 1
    while i < len(args):
        if args[i].startswith('--'):
            key = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                options[key] = args[i + 1]
                i += 2
            else:
                options[key] = True
                i += 1
        else:
            positional.append(args[i])
            i += 1

    return Ok(CLICommand(command_name, options, positional))
```

### Effect 기반 명령어 실행
모든 명령어 실행은 Effect로 래핑합니다:

```python
def execute_command(command: CLICommand) -> IOEffect[Result[str, str]]:
    """명령어를 실행하는 Effect"""

    def start_session_effect() -> IOEffect[Result[str, str]]:
        return IOEffect(lambda: Ok(f"Session started with {command.options}"))

    def show_stats_effect() -> IOEffect[Result[str, str]]:
        return IOEffect(lambda: Ok("Statistics displayed"))

    # 명령어 디스패치
    effect_map = {
        'start': start_session_effect,
        'stats': show_stats_effect,
    }

    if command.name in effect_map:
        return effect_map[command.name]()
    else:
        return IOEffect(lambda: Err(f"Unknown command: {command.name}"))

# CLI 메인 함수
def cli_main(args: list[str]) -> IOEffect[int]:
    """함수형 CLI 메인"""
    return (
        IOEffect(lambda: parse_cli_args(args))
        .bind(lambda parse_result:
            execute_command(parse_result.value) if parse_result.is_ok()
            else IOEffect(lambda: Err(parse_result.error))
        )
        .map(lambda result:
            0 if result.is_ok() else 1
        )
    )
```

### 스트림 처리
대화형 입력을 함수형 스트림으로 처리합니다:

```python
from typing import AsyncIterator, TypeVar

T = TypeVar('T')

class AsyncStream(Generic[T]):
    def __init__(self, source: AsyncIterator[T]):
        self.source = source

    async def map(self, f: Callable[[T], T]) -> 'AsyncStream[T]':
        async def mapped():
            async for item in self.source:
                yield f(item)
        return AsyncStream(mapped())

    async def filter(self, predicate: Callable[[T], bool]) -> 'AsyncStream[T]':
        async def filtered():
            async for item in self.source:
                if predicate(item):
                    yield item
        return AsyncStream(filtered())

    async def fold(self, initial: S, f: Callable[[S, T], S]) -> S:
        state = initial
        async for item in self.source:
            state = f(state, item)
        return state

# 사용 예시
async def process_user_input(input_stream: AsyncStream[str]) -> None:
    # 함수형 파이프라인
    processed = await (
        input_stream
        .map(str.strip)
        .filter(lambda s: len(s) > 0)
        .map(parse_command)
        .filter(lambda cmd: cmd.is_valid())
        .fold([], lambda acc, cmd: acc + [cmd])
    )
```

## 이벤트 소싱 패턴

상태 변경을 이벤트로 기록하고 재구성합니다:

```python
from enum import Enum
from datetime import datetime

class EventType(Enum):
    SESSION_STARTED = "session_started"
    COMMAND_EXECUTED = "command_executed"
    OUTPUT_RECEIVED = "output_received"
    SESSION_ENDED = "session_ended"

@dataclass(frozen=True)
class Event:
    type: EventType
    timestamp: datetime
    data: dict[str, Any]

@dataclass(frozen=True)
class SessionState:
    session_id: str
    started_at: datetime
    commands: tuple[str, ...]
    output_lines: tuple[str, ...]
    ended_at: datetime | None = None

def apply_event(state: SessionState, event: Event) -> SessionState:
    """이벤트를 적용하여 새 상태 생성"""
    match event.type:
        case EventType.SESSION_STARTED:
            return replace(
                state,
                session_id=event.data['session_id'],
                started_at=event.timestamp
            )
        case EventType.COMMAND_EXECUTED:
            return replace(
                state,
                commands=state.commands + (event.data['command'],)
            )
        case EventType.OUTPUT_RECEIVED:
            return replace(
                state,
                output_lines=state.output_lines + (event.data['output'],)
            )
        case EventType.SESSION_ENDED:
            return replace(state, ended_at=event.timestamp)
        case _:
            return state

def reconstruct_state(events: list[Event]) -> SessionState:
    """이벤트 목록에서 상태 재구성"""
    initial_state = SessionState(
        session_id="",
        started_at=datetime.now(),
        commands=(),
        output_lines=()
    )

    return reduce(apply_event, events, initial_state)
```

## Property-Based Testing

함수의 수학적 속성을 검증합니다:

```python
from hypothesis import given, strategies as st

# 순수 함수의 속성 테스트
@given(st.text())
def test_parse_format_inverse(text: str):
    """파싱과 포맷팅이 역함수 관계"""
    parsed = parse_ansi_sequence(text)
    formatted = format_ansi_sequence(parsed)
    assert formatted == text or is_equivalent(formatted, text)

# 모나드 법칙 테스트
@given(st.integers())
def test_result_monad_left_identity(value: int):
    """Left Identity: return a >>= f ≡ f a"""
    f = lambda x: Ok(x * 2)
    assert Ok(value).bind(f) == f(value)

@given(st.integers())
def test_result_monad_right_identity(value: int):
    """Right Identity: m >>= return ≡ m"""
    m = Ok(value)
    assert m.bind(Ok) == m

# 설정 병합의 결합법칙
@given(st.dictionaries(st.text(), st.text()))
def test_config_merge_associative(a: dict, b: dict, c: dict):
    """(a + b) + c = a + (b + c)"""
    assert merge_configs(merge_configs(a, b), c) == merge_configs(a, merge_configs(b, c))
```

## 함수형 에러 처리

에러를 값으로 다루어 명시적으로 처리합니다:

```python
def safe_terminal_operation(command: str) -> Result[str, TerminalError]:
    """안전한 터미널 작업"""
    return (
        validate_command(command)
        .bind(parse_command)
        .bind(check_permissions)
        .bind(execute_safely)
        .map(format_output)
    )

# 에러 복구
def with_fallback(primary: Callable[[], Result[T, E]],
                  fallback: Callable[[], Result[T, E]]) -> Result[T, E]:
    """실패 시 대체 함수 실행"""
    result = primary()
    if result.is_err():
        return fallback()
    return result

# 사용
result = with_fallback(
    lambda: connect_to_primary_server(),
    lambda: connect_to_backup_server()
)
```

## 함수형 성능 최적화

### 메모이제이션
순수 함수의 결과를 캐싱합니다:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_parse(data: str) -> ANSISequence:
    """비용이 큰 파싱 작업 (캐시됨)"""
    # 복잡한 파싱 로직
    return parsed_result

# 재귀 함수 최적화
@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 지연 평가
필요할 때까지 계산을 미룹니다:

```python
from typing import Iterator

def lazy_filter(predicate: Callable[[T], bool],
                items: Iterator[T]) -> Iterator[T]:
    """지연 필터링"""
    for item in items:
        if predicate(item):
            yield item

def lazy_map(f: Callable[[T], U], items: Iterator[T]) -> Iterator[U]:
    """지연 매핑"""
    for item in items:
        yield f(item)

# 대용량 데이터 처리
large_dataset = range(1_000_000)
result = lazy_map(
    lambda x: x * 2,
    lazy_filter(
        lambda x: x % 2 == 0,
        large_dataset
    )
)
# 아직 계산되지 않음, 필요할 때만 계산
```

## 모범 사례

### 1. 순수성 유지
- 모든 비즈니스 로직은 순수 함수로
- I/O는 Effect로 격리
- 전역 상태 사용 금지

### 2. 타입 안전성
- Result/Maybe로 에러와 null 처리
- 명시적 타입 힌트 사용
- mypy로 타입 검증

### 3. 테스트 용이성
- Property-based testing 우선
- Effect 모킹으로 I/O 테스트
- 순수 함수는 단위 테스트 용이

### 4. 합성 우선
- 작은 함수들의 합성으로 기능 구현
- 파이프라인 스타일 선호
- 함수형 도구 활용 (map, filter, reduce)

### 5. 불변성 보장
- 모든 데이터 구조 frozen=True
- 상태 변경은 새 객체 생성
- 컬렉션은 튜플 사용

## 결론

함수형 프로그래밍 패턴을 따르면:
- 예측 가능한 코드
- 테스트 용이성
- 동시성 안전성
- 버그 감소
- 유지보수성 향상

Term2AI는 이러한 패턴들을 일관되게 적용하여 견고하고 확장 가능한 터미널 래퍼를 구현합니다.
