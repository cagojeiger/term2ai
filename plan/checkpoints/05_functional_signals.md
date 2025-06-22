# 체크포인트 5: 함수형 시그널 처리

## 개요
Unix 시그널을 **함수형 이벤트 스트림**으로 변환하여 처리합니다. 모든 시그널 핸들러를 순수 함수로 구현하고, IOEffect를 통해 시그널 처리의 부작용을 명시적으로 관리합니다. 이를 통해 예측 가능하고 테스트 가능한 시그널 처리 시스템을 구축합니다.

## 상태
- **우선순위**: 중간
- **상태**: 📋 대기
- **예상 시간**: 5시간 (Effect 기반 시그널 처리)
- **의존성**: 체크포인트 2 (모나드 기반 I/O 시스템), 체크포인트 4 (이벤트 소싱)

## 함수형 기술 요구사항

### 1. 시그널 이벤트 모델링
- **설명**: Unix 시그널을 불변 이벤트로 표현
- **승인 기준**:
  - 시그널 이벤트 타입 정의 (`SignalEvent` ADT)
  - 시그널 번호와 이름 매핑 순수 함수 (`signal_to_name`)
  - 시그널 정보 파싱 순수 함수 (`parse_signal_info`)
  - 시그널 우선순위 계산 순수 함수 (`signal_priority`)
  - 시그널 카테고리 분류 순수 함수 (`categorize_signal`)

### 2. 함수형 시그널 핸들러
- **설명**: 시그널 처리를 순수 함수와 Effect로 분리
- **승인 기준**:
  - 시그널 처리 전략 순수 함수 (`decide_signal_action`)
  - 시그널 상태 변환 순수 함수 (`apply_signal_to_state`)
  - 시그널 핸들러 등록 Effect (`register_signal_handler_effect`)
  - 시그널 핸들러 해제 Effect (`unregister_signal_handler_effect`)
  - 시그널 마스킹 Effect (`mask_signals_effect`)

### 3. 시그널 이벤트 스트림
- **설명**: 시그널을 비동기 이벤트 스트림으로 처리
- **승인 기준**:
  - 시그널 스트림 생성 Effect (`create_signal_stream_effect`)
  - 시그널 필터링 순수 함수 (`filter_signals`)
  - 시그널 변환 순수 함수 (`transform_signal_event`)
  - 시그널 배치 처리 순수 함수 (`batch_signals`)
  - 시그널 스트림 병합 (`merge_signal_streams`)

### 4. 시그널 전파 체인
- **설명**: 자식 프로세스로의 시그널 전파를 함수형으로 구현
- **승인 기준**:
  - 전파 대상 결정 순수 함수 (`should_propagate_signal`)
  - 시그널 변환 규칙 순수 함수 (`transform_signal_for_child`)
  - 시그널 전송 Effect (`send_signal_effect`)
  - 전파 결과 수집 Effect (`collect_propagation_results_effect`)
  - 전파 실패 처리 순수 함수 (`handle_propagation_failure`)

### 5. 시그널 안전성 보장
- **설명**: 시그널 처리의 원자성과 재진입 안전성 보장
- **승인 기준**:
  - 시그널 큐잉 시스템 (`SignalQueue` 불변 구조)
  - 중복 시그널 처리 순수 함수 (`deduplicate_signals`)
  - 시그널 처리 순서 보장 (`order_signals_by_priority`)
  - 크리티컬 섹션 보호 Effect (`with_signal_safety_effect`)
  - 시그널 처리 타임아웃 Effect (`timeout_signal_handler_effect`)

## 함수형 테스트 케이스

### Property-Based 시그널 테스트

#### test_signal_event_properties
- **설명**: 시그널 이벤트의 불변성과 순서 속성 테스트
- **테스트 타입**: Property-based 시그널
- **예상 동작**: 시그널 이벤트가 타임스탬프 순서 유지

#### test_signal_handler_determinism
- **설명**: 동일한 시그널에 대해 항상 동일한 처리 결정
- **테스트 타입**: Property-based 결정성
- **예상 동작**: `decide_signal_action(signal, state)`가 결정적

#### test_signal_propagation_rules
- **설명**: 시그널 전파 규칙의 일관성 테스트
- **테스트 타입**: Property-based 전파
- **예상 동작**: 전파 규칙이 추이적 일관성 유지

### 시그널 스트림 테스트

#### test_signal_stream_ordering
- **설명**: 시그널 스트림의 순서 보장 테스트
- **테스트 타입**: 스트림 순서
- **예상 동작**: 우선순위와 타임스탬프에 따른 정렬

#### test_signal_filtering_consistency
- **설명**: 시그널 필터링의 일관성 테스트
- **테스트 타입**: 필터링 테스트
- **예상 동작**: 필터 조합의 교환법칙 성립

#### test_concurrent_signal_handling
- **설명**: 동시 시그널 처리의 안전성 테스트
- **테스트 타입**: 동시성 테스트
- **예상 동작**: 여러 시그널 동시 발생 시 데이터 일관성

### 시그널 안전성 테스트

#### test_signal_atomicity
- **설명**: 시그널 처리의 원자성 테스트
- **테스트 타입**: 원자성 테스트
- **예상 동작**: 시그널 처리 중 다른 시그널 차단

#### test_signal_reentrancy_safety
- **설명**: 재진입 안전성 테스트
- **테스트 타입**: 재진입 테스트
- **예상 동작**: 중첩된 시그널 호출에서도 상태 일관성 유지

## 함수형 결과물

### 1. 시그널 이벤트 타입
- **위치**: src/term2ai/signals/types.py
- **설명**: 시그널 이벤트의 ADT 정의
- **구현**:
  ```python
  from dataclasses import dataclass
  from datetime import datetime
  from signal import Signals
  from typing import Optional

  @dataclass(frozen=True)
  class SignalEvent:
      timestamp: datetime
      signal_number: int
      signal_name: str
      pid: int
      sender_pid: Optional[int]

  @dataclass(frozen=True)
  class SignalAction:
      action_type: Literal['ignore', 'handle', 'propagate', 'terminate']
      handler: Optional[Callable[[SignalEvent], IOEffect[None]]]
      propagate_to: tuple[int, ...]  # PIDs to propagate to

  # 시그널 카테고리
  @dataclass(frozen=True)
  class SignalCategory:
      name: str
      signals: tuple[Signals, ...]
      default_action: SignalAction

  SIGNAL_CATEGORIES = (
      SignalCategory('termination', (Signals.SIGTERM, Signals.SIGINT),
                    SignalAction('terminate', None, ())),
      SignalCategory('window', (Signals.SIGWINCH,),
                    SignalAction('handle', handle_window_resize, ())),
      SignalCategory('child', (Signals.SIGCHLD,),
                    SignalAction('handle', handle_child_exit, ())),
  )
  ```

### 2. 함수형 시그널 핸들러
- **위치**: src/term2ai/signals/handlers.py
- **설명**: 순수 함수 기반 시그널 처리 로직
- **구현**:
  ```python
  def decide_signal_action(
      signal_event: SignalEvent,
      current_state: TerminalState,
      config: SignalConfig
  ) -> SignalAction:
      """시그널에 대한 처리 방법 결정 (순수 함수)"""
      # 시그널 카테고리 찾기
      category = find_signal_category(signal_event.signal_number)

      # 사용자 정의 핸들러 확인
      custom_action = config.custom_handlers.get(signal_event.signal_name)
      if custom_action:
          return custom_action

      # 상태에 따른 동적 처리
      if current_state.is_shutting_down and category.name == 'termination':
          return SignalAction('ignore', None, ())

      return category.default_action

  def apply_signal_to_state(
      state: TerminalState,
      signal_event: SignalEvent
  ) -> TerminalState:
      """시그널 이벤트를 터미널 상태에 적용"""
      match signal_event.signal_name:
          case 'SIGWINCH':
              new_size = get_terminal_size()
              return replace(state, window_size=new_size)
          case 'SIGTERM' | 'SIGINT':
              return replace(state, is_shutting_down=True)
          case 'SIGCHLD':
              return update_child_processes(state)
          case _:
              return state
  ```

### 3. 시그널 스트림 처리
- **위치**: src/term2ai/signals/stream.py
- **설명**: 시그널을 이벤트 스트림으로 처리
- **구현**:
  ```python
  def create_signal_stream_effect() -> IOEffect[AsyncStream[SignalEvent]]:
      """시그널 이벤트 스트림 생성"""
      def setup_signal_handlers():
          signal_queue = asyncio.Queue()

          def signal_handler(signum, frame):
              event = SignalEvent(
                  timestamp=datetime.now(),
                  signal_number=signum,
                  signal_name=Signals(signum).name,
                  pid=os.getpid(),
                  sender_pid=None
              )
              asyncio.create_task(signal_queue.put(event))

          # 모든 관심 시그널에 핸들러 등록
          for sig in MONITORED_SIGNALS:
              signal.signal(sig, signal_handler)

          return AsyncStream(signal_queue)

      return IOEffect(setup_signal_handlers)

  def process_signal_stream(
      stream: AsyncStream[SignalEvent],
      state_ref: StateRef[TerminalState]
  ) -> AsyncStream[SignalEffect]:
      """시그널 스트림을 처리하여 Effect 스트림으로 변환"""
      return (
          stream
          .map(lambda event: (event, state_ref.get()))
          .map(lambda pair: decide_signal_action(pair[0], pair[1], config))
          .filter(lambda action: action.action_type != 'ignore')
          .map(create_signal_effect)
      )
  ```

### 4. 시그널 전파 시스템
- **위치**: src/term2ai/signals/propagation.py
- **설명**: 자식 프로세스로의 시그널 전파
- **구현**:
  ```python
  @dataclass(frozen=True)
  class PropagationRule:
      source_signal: Signals
      target_signal: Signals
      condition: Callable[[ProcessInfo], bool]

  def should_propagate_signal(
      signal_event: SignalEvent,
      process: ProcessInfo,
      rules: tuple[PropagationRule, ...]
  ) -> Optional[Signals]:
      """시그널 전파 여부 및 변환 결정"""
      for rule in rules:
          if (signal_event.signal_number == rule.source_signal and
              rule.condition(process)):
              return rule.target_signal
      return None

  def propagate_signal_effect(
      signal_event: SignalEvent,
      targets: tuple[ProcessInfo, ...]
  ) -> IOEffect[list[Result[None, str]]]:
      """여러 프로세스에 시그널 전파"""
      effects = [
          send_signal_to_process_effect(process.pid, target_signal)
          for process in targets
          if (target_signal := should_propagate_signal(signal_event, process, RULES))
      ]
      return sequence_effects(effects)
  ```

### 5. 시그널 안전성 보장
- **위치**: src/term2ai/signals/safety.py
- **설명**: 시그널 처리의 안전성 보장 메커니즘
- **구현**:
  ```python
  @dataclass(frozen=True)
  class SignalQueue:
      """불변 시그널 큐"""
      pending: tuple[SignalEvent, ...]
      processing: Optional[SignalEvent]
      processed: tuple[SignalEvent, ...]

      def enqueue(self, event: SignalEvent) -> 'SignalQueue':
          """시그널 추가 (중복 제거)"""
          if event not in self.pending:
              return replace(self, pending=self.pending + (event,))
          return self

      def dequeue(self) -> tuple[Optional[SignalEvent], 'SignalQueue']:
          """우선순위 기반 시그널 추출"""
          if not self.pending:
              return None, self

          sorted_pending = sort_by_priority(self.pending)
          next_event = sorted_pending[0]
          remaining = sorted_pending[1:]

          return next_event, replace(
              self,
              pending=remaining,
              processing=next_event
          )

  def with_signal_safety_effect[T](
      critical_effect: IOEffect[T]
  ) -> IOEffect[T]:
      """시그널 안전 구간에서 Effect 실행"""
      return (
          mask_signals_effect(CRITICAL_SIGNALS)
          .bind(lambda old_mask: critical_effect)
          .bind(lambda result: restore_signal_mask_effect(old_mask)
                               .map(lambda _: result))
      )
  ```

### 6. 시그널 테스트 스위트
- **위치**: tests/test_checkpoint_05_signals/
- **설명**: 시그널 처리의 함수형 테스트
- **파일**:
  - `test_signal_properties.py`: 시그널 이벤트 속성 테스트
  - `test_signal_handlers.py`: 핸들러 로직 테스트
  - `test_signal_stream.py`: 스트림 처리 테스트
  - `test_signal_propagation.py`: 전파 규칙 테스트
  - `test_signal_safety.py`: 안전성 메커니즘 테스트

## 함수형 구현 참고사항

### 시그널 처리 원칙
1. **순수 함수 우선**: 시그널 처리 로직을 순수 함수로 분리
2. **Effect 명시적 관리**: 실제 시그널 조작은 IOEffect로 캡슐화
3. **이벤트 소싱 통합**: 모든 시그널을 이벤트로 기록
4. **비동기 안전성**: 시그널 핸들러에서 비동기 작업 금지

### 플랫폼 고려사항
- **Unix 전용**: POSIX 시그널 API 사용
- **시그널 번호**: 플랫폼별 시그널 번호 차이 처리
- **실시간 시그널**: SIGRTMIN-SIGRTMAX 범위 지원
- **시그널 마스크**: 스레드별 시그널 마스크 관리

### 성능 최적화
- **배치 처리**: 짧은 시간 내 여러 시그널 배치 처리
- **우선순위 큐**: 중요 시그널 우선 처리
- **비동기 처리**: 시그널 핸들러는 최소 작업만 수행
- **메모리 풀**: SignalEvent 객체 재사용

## 함수형 승인 기준
- [ ] 모든 시그널이 불변 이벤트로 모델링됨
- [ ] 시그널 처리 로직이 순수 함수로 구현됨
- [ ] 시그널 스트림이 함수형으로 처리됨
- [ ] Property-based 테스트로 시그널 순서 보장 검증
- [ ] 시그널 전파 규칙이 일관성 있게 적용됨
- [ ] 재진입 안전성이 보장됨
- [ ] 크리티컬 섹션에서 시그널 마스킹 작동
- [ ] 동시 시그널 처리에서 데이터 일관성 유지
- [ ] 이벤트 소싱과 완벽히 통합됨

## 다음 체크포인트
함수형 시그널 처리가 구현되면 터미널의 모든 외부 이벤트가 함수형으로 처리되며, [체크포인트 6: 순수 함수 ANSI 파싱](06_pure_ansi_parsing.md)으로 진행할 수 있습니다.
