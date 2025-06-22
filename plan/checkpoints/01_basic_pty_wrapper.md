# 체크포인트 1: 순수 함수 기반 PTY 처리

## 개요
**함수형 프로그래밍 패러다임**을 사용하여 셸 프로세스를 생성하고 기본 입출력 작업을 처리할 수 있는 순수 함수 기반 의사 터미널(PTY) 시스템을 구현합니다. 모든 PTY 작업을 순수 함수와 IOEffect 모나드로 구현하여 테스트 가능하고 예측 가능한 터미널 기능의 기반을 구축합니다.

## 상태
- **우선순위**: 높음
- **상태**: 🎯 다음 단계
- **예상 시간**: 5시간 (순수 함수 + Effect 시스템)
- **의존성**: 체크포인트 0 (함수형 프로젝트 설정)

## 함수형 기술 요구사항

### 1. 순수 함수 기반 PTY 설정
- **설명**: PTY 프로세스 설정을 생성하는 순수 함수들 구현
- **승인 기준**:
  - 순수 함수로 PTY 설정 생성 (`create_pty_config`)
  - 순수 함수로 PTY 설정 검증 (`validate_pty_config`)
  - 셸 명령 검증을 위한 순수 함수 (`validate_shell_command`)
  - 모든 설정이 불변 데이터 구조로 표현
  - 사용자 정의 셸 명령 지원 (bash, zsh, fish 등)

### 2. IOEffect 모나드 기반 I/O 시스템
- **설명**: 모든 PTY I/O 작업을 IOEffect 모나드로 캡슐화
- **승인 기준**:
  - `read_pty_effect: PTYHandle -> IOEffect[Result[bytes, IOError]]`
  - `write_pty_effect: PTYHandle -> str -> IOEffect[Result[int, IOError]]`
  - 순수 함수로 데이터 변환 (`decode_pty_data`, `encode_pty_data`)
  - Result 모나드로 타입 안전한 에러 처리
  - Effect 합성을 통한 복합 I/O 작업

### 3. 함수형 프로세스 상태 관리
- **설명**: 프로세스 상태를 순수 함수와 이벤트 소싱으로 관리
- **승인 기준**:
  - 순수 함수로 프로세스 상태 변환 (`update_process_state`)
  - 불변 이벤트로 상태 변경 기록 (`ProcessEvent`)
  - 이벤트 폴드를 통한 현재 상태 재구성 (`fold_process_events`)
  - 순수 함수로 프로세스 검증 (`validate_process_state`)
  - IOEffect로 프로세스 라이프사이클 관리

### 4. 함수형 터미널 제어 시스템
- **설명**: blessed 기능을 순수 함수와 Effect로 래핑
- **승인 기준**:
  - 순수 함수로 터미널 기능 분석 (`analyze_terminal_capabilities`)
  - IOEffect로 터미널 초기화 (`init_terminal_effect`)
  - 순수 함수로 ANSI 시퀀스 생성 (`generate_ansi_sequence`)
  - 순수 함수로 커서 제어 명령 생성 (`create_cursor_commands`)
  - Effect로 터미널 상태 변경 (`apply_terminal_changes_effect`)

### 5. 함수형 에러 처리 시스템
- **설명**: Result 모나드와 Maybe 모나드를 통한 타입 안전 에러 처리
- **승인 기준**:
  - Result 모나드로 모든 실패 가능 작업 래핑
  - Maybe 모나드로 null 안전성 보장
  - 순수 함수로 에러 변환 및 복구 (`recover_from_error`)
  - Effect 체인에서 에러 전파 (`bind`, `map_err`)
  - 컴파일 타임 에러 감지를 위한 타입 힌트

## 함수형 테스트 케이스

### Property-Based 단위 테스트

#### test_pty_config_creation_properties
- **설명**: PTY 설정 생성 순수 함수의 속성 테스트
- **테스트 타입**: Property-based 단위
- **예상 동작**: 모든 유효한 입력에 대해 일관된 설정 생성

#### test_pty_config_validation_properties
- **설명**: PTY 설정 검증 함수의 속성 테스트
- **테스트 타입**: Property-based 단위
- **예상 동작**: 검증 함수가 일관되고 예측 가능한 결과 제공

#### test_data_encoding_decoding_inverse
- **설명**: 데이터 인코딩/디코딩의 역함수 속성 테스트
- **테스트 타입**: Property-based 단위
- **예상 동작**: `decode(encode(x)) == x` 항상 성립

#### test_process_state_transitions
- **설명**: 프로세스 상태 전이 순수 함수의 속성 테스트
- **테스트 타입**: Property-based 단위
- **예상 동작**: 상태 전이가 항상 유효한 상태로 이어짐

#### test_ansi_sequence_generation
- **설명**: ANSI 시퀀스 생성 순수 함수 테스트
- **테스트 타입**: Property-based 단위
- **예상 동작**: 생성된 시퀀스가 항상 유효한 ANSI 형식

### 모나드 법칙 테스트

#### test_result_monad_laws
- **설명**: Result 모나드가 모나드 법칙을 만족하는지 테스트
- **테스트 타입**: 모나드 법칙
- **예상 동작**: Left Identity, Right Identity, Associativity 법칙 통과

#### test_maybe_monad_laws
- **설명**: Maybe 모나드가 모나드 법칙을 만족하는지 테스트
- **테스트 타입**: 모나드 법칙
- **예상 동작**: 모든 모나드 법칙 통과

#### test_ioeffect_monad_laws
- **설명**: IOEffect 모나드가 모나드 법칙을 만족하는지 테스트
- **테스트 타입**: 모나드 법칙
- **예상 동작**: Effect 합성에서 모나드 법칙 준수

### Effect 시스템 통합 테스트

#### test_effect_composition_pipeline
- **설명**: Effect 합성을 통한 전체 PTY 파이프라인 테스트
- **테스트 타입**: Effect 통합
- **예상 동작**: Effect 체인이 예상대로 작동하고 에러 전파됨

#### test_pty_effect_with_mocking
- **설명**: IOEffect 모킹을 통한 PTY 작업 테스트
- **테스트 타입**: Effect 통합
- **예상 동작**: 실제 I/O 없이 Effect 로직 검증

#### test_error_handling_in_effect_chain
- **설명**: Effect 체인에서 에러 처리 테스트
- **테스트 타입**: Effect 통합
- **예상 동작**: 에러가 Result 모나드로 안전하게 전파됨

#### test_state_reconstruction_from_events
- **설명**: 이벤트 소싱을 통한 프로세스 상태 재구성 테스트
- **테스트 타입**: 이벤트 소싱 통합
- **예상 동작**: 이벤트 스트림에서 정확한 상태 재구성

#### test_functional_terminal_control
- **설명**: 함수형 터미널 제어 시스템 통합 테스트
- **테스트 타입**: 터미널 제어 통합
- **예상 동작**: 순수 함수로 생성된 명령이 올바르게 실행됨

#### test_immutability_preservation
- **설명**: 모든 데이터 구조의 불변성 보장 테스트
- **테스트 타입**: 불변성 통합
- **예상 동작**: 모든 작업에서 원본 데이터 변경되지 않음

### 함수형 엔드투엔드 테스트

#### test_functional_terminal_session_pipeline
- **설명**: 완전한 함수형 터미널 세션 파이프라인 테스트
- **테스트 타입**: 함수형 E2E
- **예상 동작**: 순수 함수와 Effect 합성으로 전체 세션 작동

#### test_event_sourcing_session_replay
- **설명**: 이벤트 소싱을 통한 세션 재생 테스트
- **테스트 타입**: 이벤트 소싱 E2E
- **예상 동작**: 기록된 이벤트로 정확한 세션 상태 재현

## 결과물

### Phase 1 결과물 (✅ 완료)

#### 1. OOP 기반 PTY 래퍼
- **위치**: src/term2ai/pty_wrapper.py
- **설명**: 기본 PTY 기능을 제공하는 클래스
- **구현 상태**: ✅ 완료

### Phase 2 결과물 (🎯 현재 작업 중)

#### 2. 순수 함수 모듈
- **위치**: src/term2ai/pure_functions.py (계획)
- **설명**: 핵심 로직을 추출한 순수 함수들
- **계획 함수**:
  ```python
  # 설정 생성 및 검증
  def create_pty_config(shell: str, env: dict) -> dict
  def validate_input(data: str) -> Result[str, str]

  # 데이터 변환
  def transform_data(input: str) -> str
  def parse_command(cmd: str) -> dict
  ```

### 2. IOEffect 시스템
- **위치**: src/term2ai/effects/pty_effects.py
- **설명**: PTY 작업을 위한 Effect 정의
- **Effects**:
  ```python
  # Effect 정의들
  def spawn_pty_effect(config: PTYConfig) -> IOEffect[Result[PTYHandle, PTYError]]
  def read_pty_effect(handle: PTYHandle, size: int) -> IOEffect[Result[bytes, IOError]]
  def write_pty_effect(handle: PTYHandle, data: str) -> IOEffect[Result[int, IOError]]
  def terminate_pty_effect(handle: PTYHandle) -> IOEffect[Result[Unit, TerminationError]]
  def init_terminal_effect(config: TerminalConfig) -> IOEffect[Result[Terminal, TerminalError]]
  ```

### 3. 이벤트 소싱 시스템
- **위치**: src/term2ai/events/pty_events.py
- **설명**: PTY 관련 이벤트 정의 및 폴드 함수
- **구성요소**:
  ```python
  # 이벤트 타입들
  @dataclass(frozen=True)
  class ProcessSpawned(ProcessEvent): ...
  class ProcessTerminated(ProcessEvent): ...
  class DataReceived(ProcessEvent): ...

  # 상태 재구성 함수
  def fold_process_events(events: tuple[ProcessEvent, ...]) -> ProcessState
  ```

### 4. Property-Based 테스트 스위트
- **위치**: tests/test_checkpoint_01_functional_pty/
- **설명**: 함수형 PTY 시스템을 위한 포괄적인 테스트
- **파일**:
  - `test_pure_functions.py`: 순수 함수 Property-based 테스트
  - `test_monad_laws.py`: 모나드 법칙 검증 테스트
  - `test_effect_composition.py`: Effect 합성 테스트
  - `test_event_sourcing.py`: 이벤트 소싱 테스트
  - `conftest.py`: 함수형 테스트 픽스처

### 5. 불변 타입 정의
- **위치**: src/term2ai/models/functional_pty.py
- **설명**: PTY 작업을 위한 불변 Pydantic 모델
- **모델**:
  ```python
  @dataclass(frozen=True)
  class PTYConfig: ...
  class ProcessState: ...
  class TerminalCapabilities: ...
  class ProcessEvent: ...
  ```

## 함수형 구현 참고사항

### 함수형 핵심 의존성
- **ptyprocess**: Unix/Linux 전용 PTY 처리 (IOEffect로 래핑)
- **blessed**: 터미널 제어 (순수 함수로 래핑)
- **hypothesis**: Property-based testing 프레임워크
- **typing**: 모나드 타입 힌트 지원
- **pydantic**: 불변 데이터 모델 (`frozen=True`)

### 함수형 설계 결정
1. **순수성 우선**: 모든 비즈니스 로직을 순수 함수로 구현
2. **Effect 캡슐화**: 모든 I/O 작업을 IOEffect 모나드로 래핑
3. **불변성**: 모든 데이터 구조를 `frozen=True`로 설정
4. **타입 안전성**: Result/Maybe 모나드로 에러/null 처리
5. **이벤트 소싱**: 상태 변경을 불변 이벤트로 기록
6. **합성성**: 작은 함수들의 합성으로 복잡한 로직 구현

### 함수형 테스트 전략
- **Property-based testing**: hypothesis로 순수 함수의 속성 검증
- **모나드 법칙 테스트**: 수학적 모나드 법칙 준수 확인
- **Effect 모킹**: IOEffect를 모킹하여 부작용 없이 테스트
- **이벤트 재생**: 이벤트 소싱으로 상태 일관성 검증
- **불변성 검증**: 모든 작업에서 원본 데이터 보존 확인
- **합성 테스트**: 함수 합성의 결합법칙 및 항등원 테스트

## 함수형 승인 기준
- [ ] 모든 순수 함수에 Property-based testing 적용 (≥95% 속성 커버리지)
- [ ] 모나드 법칙 테스트 통과 (Left Identity, Right Identity, Associativity)
- [ ] Effect 시스템 모킹 테스트 완료
- [ ] 이벤트 소싱 일관성 테스트 통과
- [ ] 모든 비즈니스 로직이 순수 함수로 구현
- [ ] 부작용이 IOEffect로 완전히 캡슐화
- [ ] 불변 데이터 구조만 사용 (frozen=True 검증)
- [ ] Result/Maybe 모나드로 에러/null 처리
- [ ] mypy 타입 검사 통과 (모나드 타입 포함)

## 다음 체크포인트
순수 함수 기반 PTY 처리가 구현되고 테스트되면 [체크포인트 2: 모나드 기반 I/O 시스템](02_io_handling.md)로 진행합니다.
