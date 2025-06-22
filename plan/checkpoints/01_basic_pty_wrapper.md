# 체크포인트 1: 기본 PTY 래퍼

## 개요
셸 프로세스를 생성하고 기본 입출력 작업을 처리할 수 있는 의사 터미널(PTY) 래퍼를 구현합니다. blessed 통합을 통해 고급 터미널 제어 기능도 포함하여 모든 터미널 래핑 기능의 기반이 됩니다.

## 상태
- **우선순위**: 높음
- **상태**: 대기
- **예상 시간**: 4시간
- **의존성**: 체크포인트 0 (프로젝트 설정)

## 기술 요구사항

### 1. PTY 프로세스 생성
- **설명**: 의사 터미널에서 프로세스를 생성하는 클래스 생성
- **승인 기준**:
  - ptyprocess를 사용하여 셸 프로세스 생성 가능
  - 사용자 정의 셸 명령 지원 (bash, zsh, fish 등)
  - 프로세스 라이프사이클 처리 (시작, 중지, 정리)
  - 프로세스 상태 정보 제공
  - PTY 파일 디스크립터 적절한 관리

### 2. 기본 I/O 작업
- **설명**: PTY에 대한 기본 읽기/쓰기 작업 구현
- **승인 기준**:
  - PTY에 데이터 쓰기 가능 (사용자 입력 시뮬레이션)
  - PTY에서 데이터 읽기 가능 (프로세스 출력 캡처)
  - 블로킹 및 논블로킹 I/O 처리
  - UTF-8 텍스트 적절한 인코딩/디코딩
  - 버퍼 크기 적절한 관리

### 3. 프로세스 관리
- **설명**: 프로세스 상태 및 라이프사이클 관리 처리
- **승인 기준**:
  - 프로세스 PID 및 상태 추적
  - 프로세스 종료 우아하게 처리
  - 프로세스 종료 감지
  - 종료 시 리소스 정리
  - 프로세스 재시작 지원

### 4. blessed 기반 터미널 제어 통합
- **설명**: blessed 라이브러리를 활용한 고급 터미널 제어 기능 통합
- **승인 기준**:
  - blessed Terminal 객체 초기화 및 관리
  - 터미널 기능 감지 (색상 깊이, 크기, 기능)
  - 전체 화면 모드 지원 (fullscreen context manager)
  - 고급 커서 제어 (정확한 위치 지정, 모양 변경)
  - 효율적인 ANSI 시퀀스 생성
  - 터미널별 호환성 처리

### 5. 오류 처리 및 리소스 관리
- **설명**: PTY 작업을 위한 견고한 오류 처리 및 자동 리소스 관리
- **승인 기준**:
  - PTY 생성 실패 처리
  - I/O 작업 오류 관리
  - 프로세스 생성 실패 우아하게 처리
  - blessed 터미널 제어 오류 처리
  - 적절한 예외 타입 및 메시지
  - 디버깅을 위한 로깅
  - Context manager를 통한 자동 리소스 정리
  - 예외 발생 시에도 보장되는 리소스 해제

## 테스트 케이스

### 단위 테스트

#### test_pty_wrapper_creation
- **설명**: PTYWrapper가 인스턴스화될 수 있는지 테스트
- **테스트 타입**: 단위
- **예상 동작**: PTYWrapper가 기본 설정으로 성공적으로 생성됨

#### test_spawn_shell_process
- **설명**: 셸 프로세스 생성 테스트
- **테스트 타입**: 단위
- **예상 동작**: 셸 프로세스가 생성되고 올바르게 추적됨

#### test_write_to_pty
- **설명**: PTY에 데이터 쓰기 테스트
- **테스트 타입**: 단위
- **예상 동작**: PTY에 데이터가 오류 없이 쓰여짐

#### test_read_from_pty
- **설명**: PTY에서 데이터 읽기 테스트
- **테스트 타입**: 단위
- **예상 동작**: PTY 출력에서 데이터를 읽을 수 있음

#### test_process_termination
- **설명**: 프로세스 종료 처리 테스트
- **테스트 타입**: 단위
- **예상 동작**: 프로세스 종료가 감지되고 처리됨

#### test_blessed_terminal_integration
- **설명**: blessed Terminal 객체 초기화 및 기능 테스트
- **테스트 타입**: 단위
- **예상 동작**: blessed Terminal이 올바르게 초기화되고 기본 기능 작동

#### test_terminal_capabilities_detection
- **설명**: 터미널 기능 감지 테스트
- **테스트 타입**: 단위
- **예상 동작**: 터미널 크기, 색상 깊이 등 기능이 올바르게 감지됨

#### test_cursor_control
- **설명**: blessed를 통한 커서 제어 테스트
- **테스트 타입**: 단위
- **예상 동작**: 커서 위치 이동 및 제어가 올바르게 작동함

### 통합 테스트

#### test_echo_command
- **설명**: 전체 echo 명령 실행 테스트
- **테스트 타입**: 통합
- **예상 동작**: echo 명령이 예상된 출력을 생성함

#### test_interactive_shell
- **설명**: 대화형 셸 명령 테스트
- **테스트 타입**: 통합
- **예상 동작**: 여러 명령이 순서대로 작동함

#### test_process_cleanup
- **설명**: 프로세스 종료 시 리소스 정리 테스트
- **테스트 타입**: 통합
- **예상 동작**: 모든 리소스가 적절히 정리됨

#### test_context_manager_usage
- **설명**: Context manager를 통한 자동 리소스 관리 테스트
- **테스트 타입**: 통합
- **예상 동작**: with 문 종료 시 자동으로 리소스 정리됨

#### test_blessed_fullscreen_mode
- **설명**: blessed 전체 화면 모드 통합 테스트
- **테스트 타입**: 통합
- **예상 동작**: 전체 화면 모드 진입/종료가 올바르게 작동함

#### test_pty_blessed_integration
- **설명**: PTY와 blessed 통합 작동 테스트
- **테스트 타입**: 통합
- **예상 동작**: PTY 출력과 blessed 터미널 제어가 함께 작동함

#### test_exception_safety
- **설명**: 예외 발생 시 리소스 정리 테스트
- **테스트 타입**: 통합
- **예상 동작**: 예외 발생해도 리소스가 누수되지 않음

### 엔드투엔드 테스트

#### test_basic_terminal_session
- **설명**: 완전한 터미널 세션 테스트
- **테스트 타입**: E2E
- **예상 동작**: 전체 터미널 세션이 예상대로 작동함

## 결과물

### 1. PTYWrapper 클래스
- **위치**: src/term2ai/core/pty_wrapper.py
- **설명**: blessed 통합 PTY 래퍼 구현
- **인터페이스**:
  ```python
  class PTYWrapper:
      def __init__(self, shell: str = "/bin/bash")
      def __enter__(self) -> 'PTYWrapper'
      def __exit__(self, exc_type, exc_val, exc_tb) -> None
      def spawn(self) -> None
      def write(self, data: str) -> int
      def read(self, size: int = 1024) -> str
      def is_alive(self) -> bool
      def terminate(self) -> None
      def get_exit_code(self) -> Optional[int]
      def _cleanup_resources(self) -> None
      
      # blessed 통합 메서드
      def get_terminal(self) -> Terminal
      def enter_fullscreen(self) -> BlessedTerminalControl
      def move_cursor(self, x: int, y: int) -> None
      def get_terminal_size(self) -> Tuple[int, int]
      def detect_capabilities(self) -> Dict[str, bool]
  ```

### 2. 프로세스 관리 유틸리티
- **위치**: src/term2ai/utils/process.py
- **설명**: 프로세스 관리를 위한 유틸리티 함수
- **함수**:
  - `find_shell()`: 사용 가능한 셸 자동 감지
  - `validate_shell()`: 셸 실행 파일 검증
  - `get_shell_info()`: 셸 버전 및 정보 획득

### 3. 테스트 스위트
- **위치**: tests/test_checkpoint_01_basic_pty/
- **설명**: PTY 래퍼를 위한 포괄적인 테스트
- **파일**:
  - `test_pty_wrapper.py`: PTYWrapper 단위 테스트
  - `test_process_management.py`: 프로세스 라이프사이클 테스트
  - `test_integration.py`: 통합 테스트
  - `conftest.py`: 테스트 픽스처 및 구성

### 4. blessed 터미널 제어 클래스
- **위치**: src/term2ai/core/blessed_control.py
- **설명**: blessed 기반 터미널 제어 구현
- **클래스**:
  - `BlessedTerminalControl`: 고급 터미널 제어
  - `TerminalCapabilities`: 터미널 기능 감지
  - `CursorController`: 커서 제어 및 관리

### 5. 타입 정의
- **위치**: src/term2ai/models/pty.py
- **설명**: PTY 작업을 위한 Pydantic 모델
- **모델**:
  - `PTYConfig`: PTY 래퍼 구성
  - `ProcessState`: 프로세스 상태 추적
  - `IOOperation`: 입출력 작업 레코드
  - `TerminalInfo`: blessed 터미널 정보
  - `TerminalCapabilities`: 터미널 기능 정의

## 구현 참고사항

### 핵심 의존성
- **ptyprocess**: Unix/Linux 전용 PTY 처리 라이브러리
- **blessed**: 고급 터미널 제어 및 기능 감지
- **pexpect**: Unix 계열 고급 PTY 작업 최적화
- **typing**: Unix 네이티브 성능을 위한 타입 힌트

### 주요 설계 결정
1. **블로킹 vs 논블로킹 I/O**: 두 모드 모두 지원
2. **버퍼 관리**: 구성 가능한 버퍼 크기
3. **오류 복구**: 오류 시 우아한 성능 저하
4. **리소스 정리**: Context manager를 통한 자동 정리
5. **RAII 패턴**: 리소스 획득과 동시에 해제 보장
6. **예외 안전성**: 예외 발생 시에도 리소스 누수 방지

### 테스트 전략
- 단위 테스트를 위한 PTY 작업 모킹
- 통합 테스트를 위한 실제 PTY 사용
- 다양한 셸에 대한 매개변수화된 테스트
- I/O 작업에 대한 성능 테스트
- Context manager 동작에 대한 테스트
- 예외 안전성 및 리소스 정리 테스트

## 승인 기준
- [ ] 모든 단위 테스트 통과 (100% 성공률)
- [ ] 실제 PTY로 통합 테스트 통과
- [ ] 핵심 기능에 대해 ≥90% 코드 커버리지
- [ ] mypy로 타입 검사 통과
- [ ] ruff로 린팅 통과
- [ ] 문서 완성 및 정확성
- [ ] Context manager 구현 및 테스트 완료
- [ ] 예외 안전성 테스트 통과
- [ ] 리소스 누수 방지 검증

## 다음 체크포인트
기본 PTY 래퍼가 구현되고 테스트되면 [체크포인트 2: I/O 처리](02_io_handling.md)로 진행합니다.