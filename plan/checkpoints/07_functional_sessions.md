# 체크포인트 7: 함수형 세션 관리

## 개요
터미널 세션을 **이벤트 스트림**으로 표현하고 관리합니다. 모든 세션 데이터는 불변 이벤트로 기록되며, 순수 함수를 통해 세션 분석, 재생, 변환이 가능합니다. 이벤트 재적용을 통해 과거 세션을 완벽하게 재현할 수 있는 함수형 세션 관리 시스템을 구축합니다.

## 상태
- **우선순위**: 중간
- **상태**: 📋 대기
- **예상 시간**: 6시간 (이벤트 기반 세션)
- **의존성**: 체크포인트 4 (이벤트 소싱), 체크포인트 6 (ANSI 파싱)

## 함수형 기술 요구사항

### 1. 세션 이벤트 모델
- **설명**: 세션의 모든 활동을 이벤트로 표현
- **승인 기준**:
  - 세션 이벤트 타입 정의 (`SessionEvent` ADT)
  - 세션 메타데이터 타입 (`SessionMetadata`)
  - 세션 ID 생성 순수 함수 (`generate_session_id`)
  - 이벤트 타임스탬핑 함수 (`timestamp_event`)
  - 이벤트 직렬화/역직렬화 (`serialize_session_event`)

### 2. 세션 라이프사이클 관리
- **설명**: 세션의 생성, 활성화, 종료를 순수 함수로 관리
- **승인 기준**:
  - 세션 상태 타입 (`SessionState`)
  - 세션 생성 순수 함수 (`create_session`)
  - 세션 상태 전이 함수 (`transition_session_state`)
  - 세션 검증 순수 함수 (`validate_session`)
  - 세션 종료 처리 함수 (`finalize_session`)

### 3. 세션 기록 및 재생
- **설명**: 세션을 기록하고 나중에 재생하는 기능
- **승인 기준**:
  - 세션 레코딩 타입 (`SessionRecording`)
  - 이벤트 기록 순수 함수 (`record_event`)
  - 세션 재생 함수 (`replay_session`)
  - 재생 속도 제어 함수 (`control_playback_speed`)
  - 포맷 변환 함수 (`convert_recording_format`)

### 4. 세션 분석 및 통계
- **설명**: 세션 데이터를 분석하는 순수 함수들
- **승인 기준**:
  - 세션 통계 타입 (`SessionStatistics`)
  - 명령어 분석 함수 (`analyze_commands`)
  - 시간 분석 함수 (`analyze_timing`)
  - 패턴 검출 함수 (`detect_patterns`)
  - 세션 비교 함수 (`compare_sessions`)

### 5. 다중 세션 관리
- **설명**: 여러 세션을 동시에 관리하는 함수형 시스템
- **승인 기준**:
  - 세션 풀 타입 (`SessionPool`)
  - 세션 검색 순수 함수 (`find_sessions`)
  - 세션 필터링 함수 (`filter_sessions`)
  - 세션 집계 함수 (`aggregate_session_data`)
  - 세션 병합 함수 (`merge_sessions`)

## 함수형 테스트 케이스

### Property-Based 세션 테스트

#### test_session_event_ordering
- **설명**: 세션 이벤트의 시간 순서 보장 테스트
- **테스트 타입**: Property-based 순서
- **예상 동작**: 이벤트 타임스탬프가 항상 증가

#### test_session_replay_fidelity
- **설명**: 세션 재생의 정확성 테스트
- **테스트 타입**: Property-based 재생
- **예상 동작**: 재생된 세션이 원본과 동일한 상태 생성

#### test_session_serialization_inverse
- **설명**: 세션 직렬화의 역함수 속성 테스트
- **테스트 타입**: Property-based 직렬화
- **예상 동작**: `deserialize(serialize(session)) == session`

### 세션 라이프사이클 테스트

#### test_session_state_transitions
- **설명**: 세션 상태 전이의 유효성 테스트
- **테스트 타입**: 상태 전이
- **예상 동작**: 모든 상태 전이가 유효한 경로 따름

#### test_concurrent_session_isolation
- **설명**: 동시 세션의 격리성 테스트
- **테스트 타입**: 격리성
- **예상 동작**: 세션 간 데이터 누출 없음

#### test_session_cleanup
- **설명**: 세션 종료 시 리소스 정리 테스트
- **테스트 타입**: 정리 테스트
- **예상 동작**: 모든 세션 리소스가 적절히 해제됨

### 세션 분석 테스트

#### test_statistics_accuracy
- **설명**: 세션 통계 계산의 정확성 테스트
- **테스트 타입**: 통계 정확성
- **예상 동작**: 계산된 통계가 실제 데이터와 일치

#### test_pattern_detection_consistency
- **설명**: 패턴 검출의 일관성 테스트
- **테스트 타입**: 패턴 검출
- **예상 동작**: 동일한 패턴이 일관되게 검출됨

## 함수형 결과물

### 1. 세션 이벤트 타입
- **위치**: src/term2ai/sessions/events.py
- **설명**: 세션 관련 이벤트의 ADT 정의
- **구현**:
  ```python
  from dataclasses import dataclass
  from datetime import datetime
  from typing import Union, Optional

  @dataclass(frozen=True)
  class SessionStartEvent:
      session_id: str
      timestamp: datetime
      shell: str
      environment: tuple[tuple[str, str], ...]
      working_directory: str

  @dataclass(frozen=True)
  class CommandExecuteEvent:
      session_id: str
      timestamp: datetime
      command: str
      working_directory: str
      exit_code: Optional[int]

  @dataclass(frozen=True)
  class OutputCaptureEvent:
      session_id: str
      timestamp: datetime
      output_type: Literal['stdout', 'stderr']
      data: str

  @dataclass(frozen=True)
  class SessionEndEvent:
      session_id: str
      timestamp: datetime
      exit_reason: str
      final_state: dict[str, Any]

  SessionEvent = Union[
      SessionStartEvent,
      CommandExecuteEvent,
      OutputCaptureEvent,
      InputEvent,
      WindowResizeEvent,
      SessionEndEvent
  ]

  @dataclass(frozen=True)
  class SessionMetadata:
      """세션의 불변 메타데이터"""
      session_id: str
      created_at: datetime
      user: str
      host: str
      terminal_type: str
      tags: tuple[str, ...]
  ```

### 2. 세션 상태 관리
- **위치**: src/term2ai/sessions/state.py
- **설명**: 세션 상태와 전이 관리
- **구현**:
  ```python
  from enum import Enum

  class SessionStatus(Enum):
      CREATED = "created"
      ACTIVE = "active"
      SUSPENDED = "suspended"
      ENDED = "ended"

  @dataclass(frozen=True)
  class SessionState:
      metadata: SessionMetadata
      status: SessionStatus
      events: tuple[SessionEvent, ...]
      current_directory: str
      environment: tuple[tuple[str, str], ...]
      command_history: tuple[str, ...]

  def create_session(
      shell: str,
      environment: dict[str, str],
      working_dir: str
  ) -> SessionState:
      """새 세션 생성 (순수 함수)"""
      session_id = generate_session_id()
      metadata = SessionMetadata(
          session_id=session_id,
          created_at=datetime.now(),
          user=environment.get('USER', 'unknown'),
          host=environment.get('HOSTNAME', 'unknown'),
          terminal_type=environment.get('TERM', 'xterm'),
          tags=()
      )

      start_event = SessionStartEvent(
          session_id=session_id,
          timestamp=datetime.now(),
          shell=shell,
          environment=tuple(environment.items()),
          working_directory=working_dir
      )

      return SessionState(
          metadata=metadata,
          status=SessionStatus.ACTIVE,
          events=(start_event,),
          current_directory=working_dir,
          environment=tuple(environment.items()),
          command_history=()
      )

  def transition_session_state(
      state: SessionState,
      event: SessionEvent
  ) -> Result[SessionState, str]:
      """세션 상태 전이 (순수 함수)"""
      # 상태 전이 검증
      if not is_valid_transition(state.status, event):
          return Err(f"Invalid transition from {state.status} with {type(event)}")

      # 이벤트 적용
      new_state = apply_session_event(state, event)

      # 상태 업데이트
      new_status = determine_new_status(state.status, event)

      return Ok(replace(
          new_state,
          status=new_status,
          events=state.events + (event,)
      ))
  ```

### 3. 세션 기록 및 재생
- **위치**: src/term2ai/sessions/recording.py
- **설명**: 세션 기록과 재생 시스템
- **구현**:
  ```python
  @dataclass(frozen=True)
  class SessionRecording:
      """불변 세션 레코딩"""
      metadata: SessionMetadata
      events: tuple[TimestampedEvent, ...]
      format_version: str
      compression: Optional[str]

  @dataclass(frozen=True)
  class TimestampedEvent:
      """타임스탬프가 포함된 이벤트"""
      relative_time: float  # 세션 시작부터의 경과 시간
      event: SessionEvent

  def record_session_events(
      events: AsyncStream[SessionEvent],
      start_time: datetime
  ) -> AsyncStream[TimestampedEvent]:
      """세션 이벤트를 타임스탬프와 함께 기록"""
      return events.map(lambda event: TimestampedEvent(
          relative_time=(event.timestamp - start_time).total_seconds(),
          event=event
      ))

  def replay_session(
      recording: SessionRecording,
      speed: float = 1.0
  ) -> IOEffect[AsyncStream[SessionEvent]]:
      """세션 재생 스트림 생성"""
      def create_replay_stream():
          async def replay_generator():
              last_time = 0.0
              for timestamped in recording.events:
                  # 시간 간격 계산
                  delay = (timestamped.relative_time - last_time) / speed
                  if delay > 0:
                      await asyncio.sleep(delay)

                  yield timestamped.event
                  last_time = timestamped.relative_time

          return AsyncStream(replay_generator())

      return IOEffect(create_replay_stream)

  # 포맷 변환
  def to_asciinema_format(recording: SessionRecording) -> str:
      """Asciinema 포맷으로 변환"""
      header = {
          "version": 2,
          "width": 80,
          "height": 24,
          "timestamp": recording.metadata.created_at.timestamp()
      }

      events = []
      for timestamped in recording.events:
          if isinstance(timestamped.event, OutputCaptureEvent):
              events.append([
                  timestamped.relative_time,
                  "o",
                  timestamped.event.data
              ])

      return json.dumps({"header": header, "events": events})
  ```

### 4. 세션 분석 시스템
- **위치**: src/term2ai/sessions/analysis.py
- **설명**: 세션 데이터 분석 순수 함수들
- **구현**:
  ```python
  @dataclass(frozen=True)
  class SessionStatistics:
      total_duration: timedelta
      command_count: int
      output_bytes: int
      error_count: int
      average_command_time: timedelta
      most_used_commands: tuple[tuple[str, int], ...]

  def analyze_session(state: SessionState) -> SessionStatistics:
      """세션 통계 분석 (순수 함수)"""
      events = state.events

      # 시간 분석
      start_time = events[0].timestamp if events else datetime.now()
      end_time = events[-1].timestamp if events else start_time
      duration = end_time - start_time

      # 명령어 분석
      commands = [e for e in events if isinstance(e, CommandExecuteEvent)]
      command_freq = count_frequency([c.command for c in commands])

      # 출력 분석
      outputs = [e for e in events if isinstance(e, OutputCaptureEvent)]
      output_bytes = sum(len(o.data) for o in outputs)

      # 에러 분석
      errors = [c for c in commands if c.exit_code != 0]

      return SessionStatistics(
          total_duration=duration,
          command_count=len(commands),
          output_bytes=output_bytes,
          error_count=len(errors),
          average_command_time=calculate_avg_time(commands),
          most_used_commands=tuple(command_freq.most_common(10))
      )

  def detect_command_patterns(
      events: list[CommandExecuteEvent],
      min_support: float = 0.1
  ) -> list[CommandPattern]:
      """명령어 패턴 검출 (순수 함수)"""
      # 순차 패턴 마이닝
      sequences = extract_command_sequences(events)
      frequent_patterns = find_frequent_patterns(sequences, min_support)

      return [
          CommandPattern(
              pattern=pattern,
              frequency=freq,
              average_interval=calc_avg_interval(pattern, events)
          )
          for pattern, freq in frequent_patterns
      ]
  ```

### 5. 다중 세션 관리
- **위치**: src/term2ai/sessions/pool.py
- **설명**: 여러 세션을 관리하는 불변 구조
- **구현**:
  ```python
  @dataclass(frozen=True)
  class SessionPool:
      """불변 세션 풀"""
      sessions: tuple[SessionState, ...]
      index: dict[str, int]  # session_id -> index mapping

      def add_session(self, session: SessionState) -> 'SessionPool':
          """세션 추가 (새 풀 반환)"""
          new_sessions = self.sessions + (session,)
          new_index = {**self.index, session.metadata.session_id: len(self.sessions)}
          return SessionPool(new_sessions, new_index)

      def update_session(self, session_id: str, event: SessionEvent) -> Result['SessionPool', str]:
          """세션 업데이트 (새 풀 반환)"""
          if session_id not in self.index:
              return Err(f"Session {session_id} not found")

          idx = self.index[session_id]
          old_session = self.sessions[idx]

          # 세션 상태 전이
          result = transition_session_state(old_session, event)
          if isinstance(result, Err):
              return result

          # 새 세션 목록 생성
          new_sessions = list(self.sessions)
          new_sessions[idx] = result.value

          return Ok(SessionPool(tuple(new_sessions), self.index))

  def find_active_sessions(pool: SessionPool) -> list[SessionState]:
      """활성 세션 검색 (순수 함수)"""
      return [
          session for session in pool.sessions
          if session.status == SessionStatus.ACTIVE
      ]

  def merge_session_recordings(
      recordings: list[SessionRecording]
  ) -> SessionRecording:
      """여러 세션 레코딩 병합"""
      # 모든 이벤트를 시간순으로 정렬
      all_events = []
      for recording in recordings:
          all_events.extend(recording.events)

      sorted_events = sorted(all_events, key=lambda e: e.relative_time)

      # 메타데이터 병합
      merged_metadata = SessionMetadata(
          session_id=generate_session_id(),
          created_at=min(r.metadata.created_at for r in recordings),
          user="merged",
          host="multiple",
          terminal_type="mixed",
          tags=tuple(set(sum((r.metadata.tags for r in recordings), ())))
      )

      return SessionRecording(
          metadata=merged_metadata,
          events=tuple(sorted_events),
          format_version="1.0",
          compression=None
      )
  ```

### 6. 세션 테스트 스위트
- **위치**: tests/test_checkpoint_07_sessions/
- **설명**: 세션 관리의 함수형 테스트
- **파일**:
  - `test_session_events.py`: 세션 이벤트 속성 테스트
  - `test_session_lifecycle.py`: 라이프사이클 테스트
  - `test_session_recording.py`: 기록/재생 테스트
  - `test_session_analysis.py`: 분석 기능 테스트
  - `test_session_pool.py`: 다중 세션 관리 테스트

## 함수형 구현 참고사항

### 세션 설계 원칙
1. **이벤트 기반**: 모든 세션 활동은 이벤트로 표현
2. **불변성**: 세션 상태는 항상 불변
3. **재현성**: 이벤트 재적용으로 동일 상태 재현
4. **격리성**: 세션 간 완전한 격리 보장

### 세션 포맷 지원
- **Native JSON**: 기본 세션 기록 포맷
- **Asciinema**: 터미널 레코딩 표준 포맷
- **Script/Typescript**: 전통적인 script 명령 호환
- **Custom Binary**: 압축된 바이너리 포맷

### 성능 최적화
- **이벤트 배칭**: 작은 이벤트들을 배치로 처리
- **압축**: 대용량 세션 데이터 압축 저장
- **인덱싱**: 빠른 이벤트 검색을 위한 인덱스
- **스트리밍**: 대용량 세션도 스트리밍 처리

## 함수형 승인 기준
- [ ] 모든 세션 데이터가 불변 이벤트로 표현됨
- [ ] 세션 상태 전이가 순수 함수로 구현됨
- [ ] 세션 재생이 원본과 동일한 결과 생성
- [ ] Property-based 테스트로 세션 속성 검증
- [ ] 다중 세션이 서로 격리되어 관리됨
- [ ] 세션 분석이 정확한 통계 생성
- [ ] 다양한 세션 포맷 간 변환 가능
- [ ] 대용량 세션도 효율적으로 처리됨
- [ ] 이벤트 소싱과 완벽히 통합됨

## 다음 체크포인트
함수형 세션 관리가 구현되면 터미널 세션을 완벽하게 기록, 분석, 재생할 수 있으며, [체크포인트 8: 함수형 고급 기능](08_advanced_features.md)으로 진행할 수 있습니다.
