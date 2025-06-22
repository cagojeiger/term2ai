# 체크포인트 2: 모나드 기반 I/O 시스템

## 개요
**함수형 프로그래밍 패러다임**을 사용하여 IOEffect 모나드 합성을 통한 복잡한 I/O 파이프라인과 비동기 스트림의 함수형 변환을 구현합니다. 모든 I/O 작업을 순수한 Effect 합성으로 처리하여 예측 가능하고 테스트 가능한 I/O 시스템을 구축합니다.

## 상태
- **우선순위**: 높음
- **상태**: 📋 대기
- **예상 시간**: 6시간 (Effect 합성 + 스트림 처리)
- **의존성**: 체크포인트 1 (순수 함수 기반 PTY 처리)

## 함수형 기술 요구사항

### 1. IOEffect 모나드 합성 시스템
- **설명**: IOEffect의 bind, map, flatMap을 통한 복잡한 I/O 파이프라인 구현
- **승인 기준**:
  - IOEffect 모나드의 완전한 구현 (`bind`, `map`, `flatMap`, `sequence`)
  - 순수 함수로 Effect 합성 체인 구현 (`compose_effects`)
  - Result와 IOEffect의 중첩 모나드 처리 (`IOEffect[Result[T, E]]`)
  - 에러 전파 및 복구를 위한 Effect 변환 (`map_err`, `recover`)
  - 타입 안전한 Effect 합성 검증

### 2. 함수형 비동기 스트림 시스템
- **설명**: AsyncStream의 함수형 변환과 스트림 병합 구현
- **승인 기준**:
  - 순수 함수로 스트림 변환 (`map_stream`, `filter_stream`, `scan_stream`)
  - 스트림 병합 및 분할을 위한 순수 함수 (`merge_streams`, `split_stream`)
  - 백프레셔 처리를 위한 함수형 메커니즘 (`throttle_stream`)
  - 스트림 파이프라인 합성 (`compose_stream_pipeline`)
  - 함수형 스트림 에러 처리 (`catch_stream_errors`)

### 3. Maybe 모나드 기반 Null 안전성
- **설명**: null 값 처리를 위한 Maybe 모나드 완전 구현
- **승인 기준**:
  - Maybe 모나드 구현 (`Some`, `Nothing`, `bind`, `map`)
  - 순수 함수로 옵션 값 변환 (`maybe_to_result`, `result_to_maybe`)
  - Maybe와 IOEffect 합성 (`lift_maybe_to_effect`)
  - 체이닝을 통한 안전한 값 접근 (`safe_get`, `unwrap_or`)
  - Maybe 컬렉션 처리 (`traverse_maybe`, `sequence_maybe`)

### 4. 스트림 병합 및 파이프라인 합성
- **설명**: 여러 입력 스트림을 하나의 처리 파이프라인으로 합성
- **승인 기준**:
  - 키보드, 마우스, PTY 스트림의 통합 (`merge_input_streams`)
  - 이벤트 타입별 스트림 분기 (`partition_by_event_type`)
  - 스트림 우선순위 처리 (`prioritize_streams`)
  - 타임윈도우 기반 스트림 집계 (`window_stream`)
  - 스트림 상태 누적 (`fold_stream_state`)

### 5. 함수형 동시성 및 병렬 처리
- **설명**: Effect와 스트림의 안전한 동시 실행
- **승인 기준**:
  - 여러 Effect의 병렬 실행 (`parallel_effects`)
  - 스트림의 병렬 처리 (`parallel_map_stream`)
  - 함수형 세마포어 및 동시성 제어 (`concurrent_limit`)
  - 불변 데이터를 통한 동시성 안전성 보장
  - Effect 취소 및 타임아웃 처리 (`timeout_effect`)

## 함수형 테스트 케이스

### Property-Based 모나드 테스트

#### test_ioeffect_monad_composition_properties
- **설명**: IOEffect 합성의 결합법칙 및 항등원 속성 테스트
- **테스트 타입**: Property-based 모나드
- **예상 동작**: `(a.bind(f)).bind(g) == a.bind(x => f(x).bind(g))` 항상 성립

#### test_stream_transformation_properties
- **설명**: 스트림 변환의 수학적 속성 테스트
- **테스트 타입**: Property-based 스트림
- **예상 동작**: `map(f).map(g) == map(compose(g, f))` 항상 성립

#### test_maybe_functor_laws
- **설명**: Maybe 모나드의 Functor 법칙 테스트
- **테스트 타입**: Property-based 모나드
- **예상 동작**: `map(id) == id`, `map(compose(f, g)) == map(f).map(g)` 성립

### Effect 합성 시스템 테스트

#### test_complex_io_pipeline_composition
- **설명**: 실제 PTY I/O 파이프라인의 Effect 합성 테스트
- **테스트 타입**: Effect 통합
- **예상 동작**: 전체 파이프라인이 순수한 함수 합성으로 표현되고 실행됨

#### test_stream_error_propagation
- **설명**: 스트림 처리 중 에러 전파 테스트
- **테스트 타입**: 에러 처리 통합
- **예상 동작**: 스트림의 에러가 Result 모나드로 안전하게 전파됨

#### test_concurrent_stream_processing
- **설명**: 동시 스트림 처리의 안전성 테스트
- **테스트 타입**: 동시성 통합
- **예상 동작**: 여러 스트림 동시 처리 시 데이터 일관성 보장

### 성능 및 메모리 테스트

#### test_stream_memory_efficiency
- **설명**: 대용량 스트림 처리의 메모리 효율성 테스트
- **테스트 타입**: 성능 테스트
- **예상 동작**: 스트림 크기에 관계없이 일정한 메모리 사용량

#### test_effect_composition_performance
- **설명**: Effect 합성 체인의 성능 테스트
- **테스트 타입**: 성능 테스트
- **예상 동작**: Effect 체인 길이와 무관하게 선형 성능

## 함수형 결과물

### 1. IOEffect 모나드 시스템
- **위치**: src/term2ai/monads/io_effect.py
- **설명**: 완전한 IOEffect 모나드 구현
- **핵심 함수들**:
  ```python
  # IOEffect 모나드 핵심
  def bind[T, U](effect: IOEffect[T], f: Callable[[T], IOEffect[U]]) -> IOEffect[U]
  def map[T, U](effect: IOEffect[T], f: Callable[[T], U]) -> IOEffect[U]
  def sequence[T](effects: list[IOEffect[T]]) -> IOEffect[list[T]]
  def parallel[T](effects: list[IOEffect[T]]) -> IOEffect[list[T]]

  # Effect 합성 유틸리티
  def compose_effects[T, U, V](
      f: Callable[[T], IOEffect[U]],
      g: Callable[[U], IOEffect[V]]
  ) -> Callable[[T], IOEffect[V]]
  ```

### 2. 함수형 스트림 시스템
- **위치**: src/term2ai/streams/async_stream.py
- **설명**: 함수형 비동기 스트림 구현
- **핵심 함수들**:
  ```python
  # 스트림 변환 순수 함수들
  def map_stream[T, U](stream: AsyncStream[T], f: Callable[[T], U]) -> AsyncStream[U]
  def filter_stream[T](stream: AsyncStream[T], predicate: Callable[[T], bool]) -> AsyncStream[T]
  def scan_stream[T, S](stream: AsyncStream[T], initial: S, f: Callable[[S, T], S]) -> AsyncStream[S]
  def merge_streams[T](streams: list[AsyncStream[T]]) -> AsyncStream[T]

  # 스트림 파이프라인 합성
  def compose_stream_pipeline[T, U](
      transformations: list[Callable[[AsyncStream], AsyncStream]]
  ) -> Callable[[AsyncStream[T]], AsyncStream[U]]
  ```

### 3. Maybe 모나드 시스템
- **위치**: src/term2ai/monads/maybe.py
- **설명**: Null 안전성을 위한 Maybe 모나드
- **구현**:
  ```python
  @dataclass(frozen=True)
  class Maybe[T]:
      value: T | None

      def bind[U](self, f: Callable[[T], Maybe[U]]) -> Maybe[U]
      def map[U](self, f: Callable[[T], U]) -> Maybe[U]
      def unwrap_or(self, default: T) -> T
      def is_some(self) -> bool
      def is_nothing(self) -> bool
  ```

### 4. 통합 I/O 파이프라인
- **위치**: src/term2ai/pipelines/io_pipeline.py
- **설명**: PTY, 키보드, 마우스 입력의 통합 처리 파이프라인
- **파이프라인**:
  ```python
  # 전체 I/O 파이프라인 합성
  def create_terminal_io_pipeline(
      pty_handle: PTYHandle
  ) -> IOEffect[AsyncStream[TerminalEvent]]:
      return (
          parallel([
              create_pty_stream_effect(pty_handle),
              create_keyboard_stream_effect(),
              create_mouse_stream_effect()
          ])
          .map(merge_streams)
          .map(lambda stream:
               stream
               .filter(is_valid_event)
               .map(normalize_event)
               .scan(initial_state, fold_event))
      )
  ```

### 5. Property-Based 테스트 스위트
- **위치**: tests/test_checkpoint_02_monad_io/
- **설명**: 모나드 법칙 및 스트림 속성을 검증하는 테스트
- **파일**:
  - `test_monad_laws.py`: 모든 모나드의 수학적 법칙 검증
  - `test_stream_properties.py`: 스트림 변환의 속성 테스트
  - `test_effect_composition.py`: Effect 합성 테스트
  - `test_concurrent_streams.py`: 동시성 스트림 테스트
  - `conftest.py`: 함수형 테스트 픽스처

## 함수형 구현 참고사항

### 함수형 핵심 의존성
- **asyncio**: 비동기 스트림 기반 (함수형 래핑)
- **typing**: 고급 타입 힌트 (모나드 타입)
- **hypothesis**: Property-based testing 확장
- **pytest-asyncio**: 비동기 함수 테스트

### 함수형 설계 결정
1. **모나드 우선**: 모든 계산을 모나드 체인으로 표현
2. **스트림 합성**: 모든 I/O를 스트림의 함수형 변환으로 처리
3. **에러 투명성**: 모든 에러가 타입 시스템에 명시됨
4. **동시성 안전성**: 불변 데이터로 race condition 원천 차단
5. **테스트 가능성**: 모든 I/O가 모킹 가능한 Effect로 캡슐화

### 함수형 성능 고려사항
- **지연 평가**: 스트림 변환의 지연 실행으로 메모리 효율성
- **스트림 퓨전**: 연속된 변환의 단일 패스 최적화
- **Effect 캐싱**: 동일한 Effect 재실행 방지
- **백프레셔**: 함수형 백프레셔로 메모리 사용량 제어

## 함수형 승인 기준
- [ ] 모든 모나드가 수학적 모나드 법칙 만족 (Property-based 테스트)
- [ ] IOEffect 합성 체인이 순수 함수 합성으로 표현됨
- [ ] 스트림 변환의 Functor/Monad 법칙 준수
- [ ] Maybe 모나드로 모든 null 참조 제거
- [ ] 동시 스트림 처리에서 데이터 race 없음 (불변성 보장)
- [ ] 전체 I/O 파이프라인이 순수한 함수 합성으로 구성됨
- [ ] Property-based 테스트로 스트림 변환 속성 검증
- [ ] Effect 모킹으로 모든 I/O 테스트 가능
- [ ] 메모리 효율적인 스트림 처리 (일정한 메모리 사용량)

## 다음 체크포인트
모나드 기반 I/O 시스템이 구현되고 테스트되면 [체크포인트 3: 함수형 CLI 인터페이스](03_functional_cli.md)로 진행합니다.
