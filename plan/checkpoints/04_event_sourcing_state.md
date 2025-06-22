# 체크포인트 4: 이벤트 소싱 터미널 상태

## 개요
**이벤트 소싱 패턴**을 사용하여 터미널 상태를 불변 이벤트의 스트림으로 관리합니다. 모든 상태 변경을 이벤트로 기록하고, 이벤트들을 fold하여 현재 상태를 재구성합니다. 이를 통해 완벽한 감사 추적, 시간 여행 디버깅, 상태 재생이 가능한 터미널 상태 관리 시스템을 구축합니다.

## 상태
- **우선순위**: 높음
- **상태**: 📋 대기
- **예상 시간**: 6시간 (이벤트 소싱 + 함수형 상태)
- **의존성**: 체크포인트 2 (모나드 기반 I/O 시스템)

## 함수형 기술 요구사항

### 1. 불변 이벤트 모델링
- **설명**: 터미널에서 발생하는 모든 이벤트를 불변 데이터로 표현
- **승인 기준**:
  - 불변 이벤트 타입 정의 (`TerminalEvent` ADT)
  - 이벤트 타임스탬프 및 메타데이터 포함
  - 이벤트 직렬화/역직렬화 순수 함수
  - 이벤트 검증 순수 함수 (`validate_event`)
  - 이벤트 순서 보장 메커니즘

### 2. 이벤트 저장소 구현
- **설명**: 이벤트들을 저장하고 조회하는 불변 저장소
- **승인 기준**:
  - 불변 EventStore 데이터 구조 (`EventStore`)
  - 이벤트 추가 순수 함수 (`append_event`)
  - 이벤트 조회 순수 함수 (`get_events_since`)
  - 이벤트 필터링 순수 함수 (`filter_events_by_type`)
  - 이벤트 스냅샷 지원 (`create_snapshot`)

### 3. 상태 재구성 함수
- **설명**: 이벤트 스트림을 fold하여 터미널 상태 재구성
- **승인 기준**:
  - 초기 상태 정의 (`initial_terminal_state`)
  - 이벤트 적용 순수 함수 (`apply_event`)
  - 상태 재구성 함수 (`fold_events`)
  - 부분 상태 재구성 (`replay_from_snapshot`)
  - 상태 검증 순수 함수 (`validate_state`)

### 4. 시간 여행 디버깅
- **설명**: 과거 시점의 상태로 돌아가고 재생하는 기능
- **승인 기준**:
  - 특정 시점 상태 재구성 (`reconstruct_at_time`)
  - 이벤트 재생 파이프라인 (`replay_events_pipeline`)
  - 상태 차이 계산 (`diff_states`)
  - 디버그 정보 생성 (`generate_debug_info`)
  - 이벤트 타임라인 시각화 데이터 생성

### 5. 이벤트 소싱 Effect 통합
- **설명**: IOEffect와 이벤트 소싱의 함수형 통합
- **승인 기준**:
  - 이벤트 발생 Effect (`emit_event_effect`)
  - 이벤트 저장 Effect (`persist_event_effect`)
  - 상태 조회 Effect (`get_current_state_effect`)
  - 이벤트 스트림 Effect (`create_event_stream_effect`)
  - 트랜잭션 보장 Effect (`transactional_update_effect`)

## 함수형 테스트 케이스

### Property-Based 이벤트 소싱 테스트

#### test_event_ordering_property
- **설명**: 이벤트 순서가 유지되는지 속성 테스트
- **테스트 타입**: Property-based 이벤트
- **예상 동작**: 이벤트 추가 순서와 조회 순서가 항상 일치

#### test_state_reconstruction_deterministic
- **설명**: 동일한 이벤트로 항상 동일한 상태가 재구성되는지 테스트
- **테스트 타입**: Property-based 상태
- **예상 동작**: `fold_events(events)` 결과가 결정적

#### test_event_idempotency
- **설명**: 이벤트 중복 적용 시 멱등성 테스트
- **테스트 타입**: Property-based 멱등성
- **예상 동작**: 특정 이벤트 타입은 중복 적용해도 동일한 결과

### 이벤트 저장소 테스트

#### test_event_store_immutability
- **설명**: EventStore의 불변성 테스트
- **테스트 타입**: 불변성 테스트
- **예상 동작**: 이벤트 추가 시 새로운 EventStore 인스턴스 생성

#### test_snapshot_consistency
- **설명**: 스냅샷과 전체 재구성의 일관성 테스트
- **테스트 타입**: 일관성 테스트
- **예상 동작**: 스냅샷 기반 재구성과 전체 재구성 결과 동일

#### test_concurrent_event_handling
- **설명**: 동시 이벤트 처리의 안전성 테스트
- **테스트 타입**: 동시성 테스트
- **예상 동작**: 동시 이벤트 발생 시 순서 보장 및 데이터 일관성

### 시간 여행 테스트

#### test_time_travel_accuracy
- **설명**: 특정 시점 상태 재구성의 정확성 테스트
- **테스트 타입**: 시간 여행 테스트
- **예상 동작**: 과거 시점 상태가 당시 실제 상태와 일치

#### test_replay_performance
- **설명**: 대량 이벤트 재생의 성능 테스트
- **테스트 타입**: 성능 테스트
- **예상 동작**: 이벤트 수에 대해 선형 시간 복잡도

## 함수형 결과물

### 1. 이벤트 타입 시스템
- **위치**: src/term2ai/events/types.py
- **설명**: 터미널 이벤트의 ADT(Algebraic Data Type) 정의
- **구현**:
  ```python
  from dataclasses import dataclass
  from datetime import datetime
  from typing import Union

  @dataclass(frozen=True)
  class KeyPressEvent:
      timestamp: datetime
      key: str
      modifiers: tuple[str, ...]

  @dataclass(frozen=True)
  class OutputEvent:
      timestamp: datetime
      data: str
      source: str  # 'stdout' | 'stderr'

  @dataclass(frozen=True)
  class StateChangeEvent:
      timestamp: datetime
      field: str
      old_value: Any
      new_value: Any

  # Union type for all events
  TerminalEvent = Union[
      KeyPressEvent,
      OutputEvent,
      StateChangeEvent,
      WindowResizeEvent,
      CursorMoveEvent,
      CommandExecuteEvent
  ]
  ```

### 2. 이벤트 저장소
- **위치**: src/term2ai/events/store.py
- **설명**: 불변 이벤트 저장소 구현
- **구현**:
  ```python
  @dataclass(frozen=True)
  class EventStore:
      events: tuple[TerminalEvent, ...]
      snapshots: tuple[StateSnapshot, ...]

      def append(self, event: TerminalEvent) -> 'EventStore':
          """이벤트 추가 (새 인스턴스 반환)"""
          return EventStore(
              events=self.events + (event,),
              snapshots=self.snapshots
          )

      def create_snapshot(self, state: TerminalState) -> 'EventStore':
          """현재 상태의 스냅샷 생성"""
          snapshot = StateSnapshot(
              timestamp=datetime.now(),
              state=state,
              event_index=len(self.events)
          )
          return replace(self, snapshots=self.snapshots + (snapshot,))
  ```

### 3. 상태 재구성 시스템
- **위치**: src/term2ai/events/reconstruction.py
- **설명**: 이벤트로부터 상태를 재구성하는 순수 함수들
- **구현**:
  ```python
  def apply_event(state: TerminalState, event: TerminalEvent) -> TerminalState:
      """단일 이벤트를 상태에 적용"""
      match event:
          case KeyPressEvent(_, key, modifiers):
              return handle_key_press(state, key, modifiers)
          case OutputEvent(_, data, source):
              return handle_output(state, data, source)
          case StateChangeEvent(_, field, _, new_value):
              return update_field(state, field, new_value)
          case _:
              return state

  def fold_events(
      events: Sequence[TerminalEvent],
      initial: TerminalState = INITIAL_STATE
  ) -> TerminalState:
      """이벤트 시퀀스를 fold하여 최종 상태 생성"""
      return reduce(apply_event, events, initial)

  def reconstruct_at_time(
      store: EventStore,
      target_time: datetime
  ) -> TerminalState:
      """특정 시점의 상태 재구성"""
      # 가장 가까운 스냅샷 찾기
      snapshot = find_nearest_snapshot(store.snapshots, target_time)

      # 스냅샷 이후 이벤트만 적용
      events_since = filter(
          lambda e: snapshot.timestamp <= e.timestamp <= target_time,
          store.events[snapshot.event_index:]
      )

      return fold_events(list(events_since), snapshot.state)
  ```

### 4. 시간 여행 디버거
- **위치**: src/term2ai/events/time_travel.py
- **설명**: 시간 여행 디버깅 기능
- **구현**:
  ```python
  @dataclass(frozen=True)
  class TimelinePoint:
      timestamp: datetime
      state: TerminalState
      event: Optional[TerminalEvent]

  def generate_timeline(
      store: EventStore,
      start_time: datetime,
      end_time: datetime,
      resolution: timedelta
  ) -> list[TimelinePoint]:
      """시간 범위의 상태 타임라인 생성"""
      points = []
      current_time = start_time

      while current_time <= end_time:
          state = reconstruct_at_time(store, current_time)
          event = find_event_at(store.events, current_time)
          points.append(TimelinePoint(current_time, state, event))
          current_time += resolution

      return points
  ```

### 5. 이벤트 소싱 Effect 통합
- **위치**: src/term2ai/events/effects.py
- **설명**: IOEffect와 이벤트 소싱의 통합
- **구현**:
  ```python
  def emit_event_effect(event: TerminalEvent) -> IOEffect[None]:
      """이벤트를 발생시키는 Effect"""
      return IOEffect(lambda: event_bus.emit(event))

  def create_event_sourced_terminal() -> IOEffect[EventSourcedTerminal]:
      """이벤트 소싱 기반 터미널 생성"""
      return (
          IOEffect.pure(EventStore.empty())
          .bind(lambda store: create_event_stream_effect())
          .bind(lambda stream:
              IOEffect.pure(EventSourcedTerminal(store, stream))
          )
      )
  ```

### 6. 이벤트 소싱 테스트 스위트
- **위치**: tests/test_checkpoint_04_event_sourcing/
- **설명**: 이벤트 소싱 시스템의 속성 기반 테스트
- **파일**:
  - `test_event_properties.py`: 이벤트 속성 테스트
  - `test_store_immutability.py`: 저장소 불변성 테스트
  - `test_state_reconstruction.py`: 상태 재구성 테스트
  - `test_time_travel.py`: 시간 여행 기능 테스트
  - `test_concurrent_events.py`: 동시성 테스트

## 함수형 구현 참고사항

### 이벤트 소싱 핵심 원칙
1. **이벤트는 불변**: 한번 기록된 이벤트는 절대 변경되지 않음
2. **이벤트는 사실의 기록**: 의도가 아닌 실제 발생한 일을 기록
3. **상태는 파생물**: 현재 상태는 항상 이벤트로부터 재구성 가능
4. **이벤트 순서 중요**: 이벤트 적용 순서가 최종 상태를 결정

### 성능 최적화
- **스냅샷 전략**: 주기적으로 스냅샷을 생성하여 재구성 시간 단축
- **이벤트 압축**: 오래된 이벤트들을 압축하여 저장 공간 절약
- **지연 평가**: 필요할 때만 상태 재구성 수행
- **메모이제이션**: 자주 조회되는 상태는 캐싱

### 이벤트 설계 가이드라인
- **세밀한 이벤트**: 큰 변경보다는 작은 원자적 이벤트 선호
- **도메인 이벤트**: 기술적 이벤트보다 비즈니스 의미 있는 이벤트
- **버전 관리**: 이벤트 스키마 변경을 위한 버전 필드 포함
- **메타데이터**: 디버깅을 위한 충분한 컨텍스트 정보 포함

## 함수형 승인 기준
- [ ] 모든 이벤트 타입이 불변 데이터 구조로 정의됨
- [ ] EventStore가 순수한 불변 데이터 구조로 구현됨
- [ ] 상태 재구성이 순수 함수로만 이루어짐
- [ ] Property-based 테스트로 이벤트 순서 보장 검증
- [ ] 시간 여행 디버깅이 부작용 없이 작동
- [ ] 동시 이벤트 처리에서 데이터 일관성 보장
- [ ] 스냅샷과 전체 재구성 결과가 항상 일치
- [ ] 대량 이벤트 재생이 효율적으로 처리됨
- [ ] 이벤트 스트림과 IOEffect의 원활한 통합

## 다음 체크포인트
이벤트 소싱 터미널 상태가 구현되면 상태 관리가 완전히 함수형으로 전환되며, [체크포인트 5: 함수형 시그널 처리](05_functional_signals.md)로 진행할 수 있습니다.
