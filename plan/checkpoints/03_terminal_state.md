# 체크포인트 3: 터미널 상태 관리

## 개요
터미널 모드, 크기, 커서 위치, 터미널 기능을 포함한 포괄적인 터미널 상태 관리를 구현합니다. 이 체크포인트는 고급 터미널 에뮬레이션 및 제어를 위한 기반을 제공합니다.

## 상태
- **우선순위**: 높음
- **상태**: 대기
- **예상 시간**: 5시간
- **의존성**: 체크포인트 2 (I/O 처리)

## 기술 요구사항

### 1. 터미널 모드 관리
- **설명**: 다양한 터미널 모드 처리 (raw, cbreak, cooked)
- **승인 기준**:
  - canonical 및 non-canonical 모드 간 전환
  - 문자 에코 및 라인 버퍼링 제어
  - 특수 문자 처리 (Ctrl+C, Ctrl+Z)
  - 터미널 속성 저장 및 복원
  - 터미널 기능 쿼리 지원

### 2. 창 크기 및 차원
- **설명**: 터미널 창 크기 추적 및 관리
- **승인 기준**:
  - 창 크기 변경 모니터링 (SIGWINCH)
  - 자식 프로세스로 크기 변경 전파
  - 사용자 정의 터미널 크기 지원
  - 크기 제약 및 한계 처리
  - 터미널 기능 쿼리 및 캐싱

### 3. 커서 위치 및 화면 상태
- **설명**: 커서 위치 및 화면 버퍼 상태 추적
- **승인 기준**:
  - 커서 위치 좌표 유지
  - 화면 버퍼 내용 추적
  - 스크롤링 및 화면 지우기 처리
  - 대체 화면 버퍼 지원
  - 커서 저장/복원 작업 구현

### 4. 터미널 기능
- **설명**: 터미널 기능 쿼리 및 관리 (terminfo)
- **승인 기준**:
  - 터미널 타입 및 기능 쿼리
  - 색상 깊이 감지 지원
  - 다양한 터미널 에뮬레이터 특성 처리
  - 기능 대체 구현
  - 기능 정보 캐싱

## 테스트 케이스

### 단위 테스트

#### test_terminal_mode_switching
- **설명**: 터미널 모드 전환 테스트
- **테스트 타입**: 단위
- **예상 동작**: 터미널 모드가 오류 없이 올바르게 전환됨

#### test_window_size_tracking
- **설명**: 창 크기 변경 감지 테스트
- **테스트 타입**: 단위
- **예상 동작**: 창 크기 변경이 감지되고 처리됨

#### test_cursor_position_tracking
- **설명**: 커서 위치 관리 테스트
- **테스트 타입**: 단위
- **예상 동작**: 커서 위치가 정확하게 추적됨

#### test_screen_buffer_management
- **설명**: 화면 버퍼 작업 테스트
- **테스트 타입**: 단위
- **예상 동작**: 화면 버퍼가 올바른 상태 유지

#### test_terminal_capabilities
- **설명**: 터미널 기능 감지 테스트
- **테스트 타입**: 단위
- **예상 동작**: 터미널 기능이 올바르게 감지됨

### 통합 테스트

#### test_sigwinch_handling
- **설명**: SIGWINCH 시그널 처리 테스트
- **테스트 타입**: 통합
- **예상 동작**: 창 크기 변경 시그널이 적절히 처리됨

#### test_mode_persistence
- **설명**: 작업 간 터미널 모드 지속성 테스트
- **테스트 타입**: 통합
- **예상 동작**: 터미널 모드가 올바르게 지속됨

#### test_screen_coordination
- **설명**: 커서와 화면 상태 간 조정 테스트
- **테스트 타입**: 통합
- **예상 동작**: 커서와 화면 상태가 동기화 상태 유지

### 엔드투엔드 테스트

#### test_terminal_emulation
- **설명**: 완전한 터미널 에뮬레이션 테스트
- **테스트 타입**: E2E
- **예상 동작**: 터미널이 실제 터미널처럼 동작함

#### test_application_compatibility
- **설명**: 터미널 애플리케이션과의 호환성 테스트
- **테스트 타입**: E2E
- **예상 동작**: 표준 터미널 앱이 올바르게 작동함

## 결과물

### 1. 터미널 상태 관리자
- **위치**: src/term2ai/core/terminal_state.py
- **설명**: 핵심 터미널 상태 관리
- **인터페이스**:
  ```python
  class TerminalState:
      def __init__(self, fd: int)
      def set_mode(self, mode: TerminalMode) -> None
      def get_mode(self) -> TerminalMode
      def set_size(self, rows: int, cols: int) -> None
      def get_size(self) -> Tuple[int, int]
      def get_cursor_position(self) -> Tuple[int, int]
      def set_cursor_position(self, row: int, col: int) -> None
  ```

### 2. 창 크기 관리자
- **위치**: src/term2ai/core/window_size.py
- **설명**: 창 크기 변경 및 시그널 처리
- **클래스**:
  - `WindowSizeManager`: 창 크기 변경 추적
  - `SigwinchHandler`: SIGWINCH 시그널 처리
  - `DimensionValidator`: 터미널 크기 검증

### 3. 화면 버퍼
- **위치**: src/term2ai/core/screen_buffer.py
- **설명**: 터미널 화면 버퍼 상태 관리
- **클래스**:
  - `ScreenBuffer`: 주 화면 버퍼 구현
  - `AlternateBuffer`: 대체 화면 버퍼 지원
  - `ScrollBuffer`: 스크롤백 버퍼 관리

### 4. 터미널 기능
- **위치**: src/term2ai/core/capabilities.py
- **설명**: 터미널 기능 감지 및 관리
- **클래스**:
  - `TerminalCapabilities`: 기능 감지 및 캐싱
  - `TermInfoParser`: terminfo 데이터베이스 파싱
  - `CapabilityCache`: 기능 정보 캐싱

### 5. 향상된 터미널 모델
- **위치**: src/term2ai/models/terminal.py
- **설명**: 터미널 상태를 위한 Pydantic 모델
- **모델**:
  - `TerminalMode`: 터미널 모드 열거형
  - `TerminalSize`: 창 크기
  - `CursorPosition`: 커서 좌표
  - `TerminalCapabilities`: 기능 정보
  - `ScreenState`: 완전한 화면 상태

### 6. 테스트 스위트
- **위치**: tests/test_checkpoint_03_terminal_state/
- **설명**: 포괄적인 터미널 상태 테스트
- **파일**:
  - `test_terminal_state.py`: 터미널 상태 관리 테스트
  - `test_window_size.py`: 창 크기 처리 테스트
  - `test_screen_buffer.py`: 화면 버퍼 테스트
  - `test_capabilities.py`: 터미널 기능 테스트
  - `test_integration.py`: 통합 테스트

## 구현 참고사항

### 터미널 모드
- POSIX 터미널 제어를 위해 `termios` 모듈 사용
- 적절한 모드 저장/복원 구현
- 모드 전환을 안전하게 처리
- 블로킹 및 논블로킹 모드 모두 지원

### 시그널 처리 (Unix 전용)
- Unix 전용 SIGWINCH 최적화 처리를 위해 `signal` 모듈 사용
- Unix 네이티브 시그널 안전 작업 구현
- epoll/kqueue를 통한 시그널 핸들러와 메인 스레드 간 최적 조정
- Unix 계열 시그널 전달 최적화

### 화면 버퍼 관리
- 효율적인 화면 버퍼 데이터 구조 구현
- 버퍼 스냅샷을 위한 copy-on-write 사용
- 유니코드 문자 적절한 처리
- 업데이트를 위한 효율적인 diff 알고리즘 구현

### 기능 감지
- terminfo 데이터베이스 파싱 또는 내장 기능 사용
- 알려지지 않은 터미널을 위한 대체 기능 구현
- 성능을 위한 기능 캐싱
- 기능 변형 우아하게 처리

## 테스트 전략

### 단위 테스트
- 터미널 파일 디스크립터 모킹
- 상태 전환을 독립적으로 테스트
- 다양한 터미널에 대한 매개변수화된 테스트
- 오류 조건 및 엣지 케이스 테스트

### 통합 테스트
- 실제 터미널 파일 디스크립터 사용
- 다양한 터미널 에뮬레이터로 테스트
- 시그널 처리가 올바르게 작동하는지 확인
- 작업 간 상태 지속성 테스트

### 호환성 테스트
- 다양한 터미널 애플리케이션으로 테스트
- ANSI 준수 확인
- 다양한 터미널 타입으로 테스트
- screen/tmux와의 호환성 확인

## 성능 고려사항
- 상태 쿼리를 위한 시스템 콜 최소화
- 자주 접근하는 상태 정보 캐싱
- 화면 버퍼를 위한 효율적인 데이터 구조 사용
- 가능한 경우 업데이트 일괄 처리

## 승인 기준
- [ ] 터미널 모드가 올바르고 안전하게 전환됨
- [ ] 창 크기 변경이 자동으로 처리됨
- [ ] 커서 위치 추적이 정확함
- [ ] 화면 버퍼가 올바른 상태 유지
- [ ] 터미널 기능이 적절히 감지됨
- [ ] SIGWINCH 시그널이 올바르게 처리됨
- [ ] 표준 터미널 애플리케이션과 호환됨
- [ ] 모든 테스트가 ≥95% 커버리지로 통과함
- [ ] 성능 요구사항 충족
- [ ] 코드가 타입 검사 및 린팅 통과함

## 다음 체크포인트
터미널 상태 관리가 완료되고 테스트되면 [체크포인트 4: 시그널 처리](04_signal_handling.md)로 진행합니다.