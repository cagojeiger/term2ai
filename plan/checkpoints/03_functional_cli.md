# 체크포인트 3: 함수형 CLI 인터페이스

## 개요
**함수형 프로그래밍 패러다임**을 사용하여 `term2ai` 명령어를 통한 사용자 인터페이스를 구현합니다. 모든 CLI 로직을 순수 함수로 구현하고, Effect 시스템을 통해 사용자 상호작용을 관리하여 실제로 사용 가능한 터미널 래퍼 도구를 완성합니다.

## 상태
- **우선순위**: 높음
- **상태**: 📋 대기
- **예상 시간**: 4시간 (함수형 CLI + Effect 통합)
- **의존성**: 체크포인트 2 (모나드 기반 I/O 시스템)

## 함수형 기술 요구사항

### 1. 순수 함수 기반 명령어 파싱
- **설명**: CLI 명령어와 옵션을 순수 함수로 파싱하고 검증
- **승인 기준**:
  - 순수 함수로 명령어 파싱 (`parse_cli_args`)
  - 순수 함수로 옵션 검증 (`validate_cli_options`)
  - Result 모나드로 파싱 에러 처리 (`parse_result`)
  - 명령어 도움말 생성 순수 함수 (`generate_help_text`)
  - 타입 안전한 CLI 설정 객체 (`CLIConfig`)

### 2. Effect 기반 명령어 실행
- **설명**: 모든 CLI 명령어를 IOEffect로 구현하여 부작용 명시적 관리
- **승인 기준**:
  - 터미널 세션 시작 Effect (`start_terminal_session_effect`)
  - 세션 통계 표시 Effect (`show_session_stats_effect`)
  - 설정 관리 Effect (`manage_config_effect`)
  - 시스템 진단 Effect (`run_diagnostics_effect`)
  - Effect 합성을 통한 복합 명령어 (`compose_command_effects`)

### 3. 함수형 설정 관리 시스템
- **설명**: 불변 설정 객체와 순수 함수를 통한 설정 관리
- **승인 기준**:
  - 불변 설정 데이터 구조 (`TerminalConfig`)
  - 순수 함수로 설정 병합 (`merge_configs`)
  - 설정 검증 순수 함수 (`validate_config`)
  - 임시 설정 오버라이드 함수 (`override_config`)
  - 설정 직렬화/역직렬화 순수 함수

### 4. 순수 함수 기반 출력 포맷팅
- **설명**: 모든 사용자 출력을 순수 함수로 포맷팅
- **승인 기준**:
  - 터미널 상태 표시 순수 함수 (`format_terminal_status`)
  - 에러 메시지 포맷팅 순수 함수 (`format_error_message`)
  - 진행률 표시 순수 함수 (`format_progress`)
  - 색상 및 스타일 적용 순수 함수 (`apply_terminal_style`)
  - 테이블 및 목록 포맷팅 순수 함수

### 5. 함수형 대화형 모드
- **설명**: 사용자 입력을 스트림으로 처리하는 대화형 인터페이스
- **승인 기준**:
  - 사용자 입력 스트림 처리 (`process_user_input_stream`)
  - 명령어 완성 순수 함수 (`generate_completions`)
  - 대화형 메뉴 상태 관리 (`manage_interactive_state`)
  - 실시간 터미널 모니터링 스트림
  - 함수형 프롬프트 시스템

## 함수형 테스트 케이스

### Property-Based CLI 테스트

#### test_cli_parsing_idempotent
- **설명**: CLI 파싱의 멱등성 속성 테스트
- **테스트 타입**: Property-based CLI
- **예상 동작**: `parse(format(parsed_args)) == parsed_args` 항상 성립

#### test_config_merge_properties
- **설명**: 설정 병합의 결합법칙 속성 테스트
- **테스트 타입**: Property-based 설정
- **예상 동작**: `merge(a, merge(b, c)) == merge(merge(a, b), c)` 성립

#### test_help_text_completeness
- **설명**: 도움말 텍스트가 모든 명령어를 포함하는지 속성 테스트
- **테스트 타입**: Property-based 문서
- **예상 동작**: 모든 유효한 명령어가 도움말에 포함됨

### Effect 시스템 CLI 테스트

#### test_command_effect_composition
- **설명**: CLI 명령어의 Effect 합성 테스트
- **테스트 타입**: Effect 통합
- **예상 동작**: 복합 명령어가 순수한 Effect 합성으로 실행됨

#### test_cli_error_handling
- **설명**: CLI 에러의 Result 모나드 처리 테스트
- **테스트 타입**: 에러 처리
- **예상 동작**: 모든 CLI 에러가 타입 안전하게 처리됨

#### test_interactive_mode_stream
- **설명**: 대화형 모드의 스트림 처리 테스트
- **테스트 타입**: 스트림 통합
- **예상 동작**: 사용자 입력 스트림이 함수형 변환으로 처리됨

### 사용성 테스트

#### test_cli_usability_scenarios
- **설명**: 실제 사용 시나리오의 엔드투엔드 테스트
- **테스트 타입**: E2E 사용성
- **예상 동작**: 모든 주요 CLI 워크플로우가 정상 작동

#### test_help_and_documentation
- **설명**: 도움말 및 문서의 정확성 테스트
- **테스트 타입**: 문서 검증
- **예상 동작**: 모든 도움말이 실제 기능과 일치

### 추가 테스트 케이스

#### test_hijacking_level_transitions
- **설명**: 하이재킹 레벨 전환의 안전성 테스트
- **테스트 타입**: 통합 테스트
- **예상 동작**: 레벨 변경 시 리소스 정리 및 재초기화 정상 작동

#### test_filter_pipeline_composition
- **설명**: 필터 파이프라인의 합성 테스트
- **테스트 타입**: Property-based 필터
- **예상 동작**: `filter1 ∘ filter2 = compose([filter1, filter2])` 성립

#### test_session_record_replay_fidelity
- **설명**: 세션 녹화/재생의 정확성 테스트
- **테스트 타입**: E2E 녹화
- **예상 동작**: 녹화된 세션 재생 시 원본과 동일한 출력

#### test_benchmark_accuracy
- **설명**: 벤치마크 측정의 정확성 테스트
- **테스트 타입**: 성능 테스트
- **예상 동작**: 측정된 메트릭이 실제 성능을 정확히 반영

#### test_profile_inheritance
- **설명**: 프로필 상속 메커니즘 테스트
- **테스트 타입**: 설정 테스트
- **예상 동작**: 자식 프로필이 부모 설정을 올바르게 상속

## 함수형 결과물

### 1. 함수형 CLI 엔트리포인트
- **위치**: src/term2ai/cli/main.py
- **설명**: 전체 CLI 애플리케이션의 함수형 엔트리포인트
- **구현**:
  ```python
  # 함수형 CLI 메인 함수
  def main() -> IOEffect[int]:
      return (
          parse_cli_args_effect()
          .bind(validate_args)
          .bind(execute_command)
          .bind(format_output)
          .map(lambda _: 0)
          .recover(handle_cli_error)
      )

  # Typer 통합
  app = typer.Typer()

  @app.command()
  def start(
      shell: str = "/bin/bash",
      config: Optional[str] = None,
      verbose: bool = False
  ) -> None:
      run_effect(start_terminal_session_effect(shell, config, verbose))
  ```

### 2. 순수 함수 명령어 시스템
- **위치**: src/term2ai/cli/commands.py
- **설명**: 모든 CLI 명령어의 순수 함수 구현
- **명령어들**:
  ```python
  # 핵심 명령어 Effect들
  def start_command_effect(config: CLIConfig) -> IOEffect[TerminalSession]
  def stats_command_effect(session_id: str) -> IOEffect[SessionStats]
  def config_command_effect(action: ConfigAction) -> IOEffect[Config]
  def doctor_command_effect() -> IOEffect[DiagnosticResult]

  # 명령어 조합 함수
  def compose_commands(
      commands: list[CommandEffect]
  ) -> IOEffect[list[CommandResult]]
  ```

### 3. 함수형 설정 시스템
- **위치**: src/term2ai/cli/config.py
- **설명**: 불변 설정 관리 시스템
- **구현**:
  ```python
  @dataclass(frozen=True)
  class CLIConfig:
      shell: str
      verbose: bool
      config_file: Optional[str]
      hijacking_level: HijackingLevel

  # 설정 관리 순수 함수들
  def load_config_from_file(path: str) -> Result[Config, ConfigError]
  def merge_configs(base: Config, override: Config) -> Config
  def validate_config(config: Config) -> Result[Config, ValidationError]
  def serialize_config(config: Config) -> str
  def deserialize_config(data: str) -> Result[Config, ParseError]
  ```

### 4. 순수 함수 출력 포맷터
- **위치**: src/term2ai/cli/formatters.py
- **설명**: 모든 CLI 출력을 위한 순수 함수들
- **포맷터들**:
  ```python
  # 출력 포맷팅 순수 함수들
  def format_session_status(session: TerminalSession) -> str
  def format_error_message(error: CLIError) -> str
  def format_statistics(stats: SessionStats) -> str
  def format_diagnostic_results(results: DiagnosticResult) -> str
  def format_help_text(command: CommandInfo) -> str

  # Rich 통합 포맷터
  def create_rich_table(data: TableData) -> Table
  def create_progress_bar(progress: ProgressInfo) -> Progress
  ```

### 5. 대화형 모드 시스템
- **위치**: src/term2ai/cli/interactive.py
- **설명**: 함수형 대화형 인터페이스
- **구현**:
  ```python
  # 대화형 모드 스트림 처리
  def create_interactive_session() -> IOEffect[AsyncStream[UserCommand]]

  def process_interactive_stream(
      input_stream: AsyncStream[UserInput]
  ) -> AsyncStream[CommandResult]:
      return (
          input_stream
          .map(parse_user_input)
          .filter(is_valid_command)
          .map(execute_command_effect)
          .map(format_command_result)
      )

  # 명령어 완성 시스템
  def generate_command_completions(partial: str) -> list[str]
  def suggest_next_actions(context: InteractiveContext) -> list[Suggestion]
  ```

### 6. CLI 테스트 스위트
- **위치**: tests/test_checkpoint_03_cli/
- **설명**: 함수형 CLI 시스템 테스트
- **파일**:
  - `test_cli_parsing.py`: CLI 파싱 순수 함수 테스트
  - `test_command_effects.py`: 명령어 Effect 테스트
  - `test_config_management.py`: 설정 관리 테스트
  - `test_interactive_mode.py`: 대화형 모드 테스트
  - `test_e2e_scenarios.py`: 엔드투엔드 시나리오 테스트

## CLI 명령어 구조

### 기본 명령어들
```bash
# 터미널 세션 시작
uv run term2ai start
uv run term2ai start --shell /bin/zsh
uv run term2ai start --config ~/.term2ai/config.toml
uv run term2ai start --verbose

# 하이재킹 레벨 제어
uv run term2ai start --hijack-level minimal    # PTY만
uv run term2ai start --hijack-level standard   # PTY + 키보드
uv run term2ai start --hijack-level complete   # PTY + 키보드 + 마우스 + blessed

# 실시간 필터링
uv run term2ai start --filter-passwords        # 비밀번호 자동 마스킹
uv run term2ai start --filter-regex "SECRET.*" # 정규식 필터링
uv run term2ai start --transform uppercase     # 출력 변환

# 통계 및 모니터링
uv run term2ai stats
uv run term2ai stats --session-id abc123
uv run term2ai stats --last
uv run term2ai stats --metric commands         # 특정 메트릭만

# 설정 관리
uv run term2ai config show
uv run term2ai config set shell /bin/fish
uv run term2ai config set hijacking.keyboard true
uv run term2ai config reset

# 시스템 진단
uv run term2ai doctor
uv run term2ai doctor --fix
uv run term2ai doctor --verbose --report diagnosis.txt

# 대화형 모드
uv run term2ai interactive
uv run term2ai shell  # 대화형 셸 모드
```

### 세션 관리 명령어들
```bash
# 세션 녹화
uv run term2ai record --output session.json
uv run term2ai record --format asciinema --output session.cast
uv run term2ai record --compress --timestamp

# 세션 재생
uv run term2ai replay session.json
uv run term2ai replay session.json --speed 2.0
uv run term2ai replay session.json --pause-on-output
uv run term2ai replay session.json --skip-idle 3

# 세션 관리
uv run term2ai session list
uv run term2ai session info abc123
uv run term2ai session export abc123 --format json
uv run term2ai session clean --older-than 30d
```

### 고급 명령어들
```bash
# 세션 분석
uv run term2ai analyze --pattern "git"
uv run term2ai analyze --session-id abc123 --pattern "error|failed"
uv run term2ai analyze --time-range 7d
uv run term2ai analyze --ai-model gpt-4       # AI 분석 (미래 기능)

# 성능 벤치마크
uv run term2ai benchmark
uv run term2ai benchmark --metric throughput --duration 60
uv run term2ai benchmark --compare-with native
uv run term2ai benchmark --output benchmark-results.json

# 프로필 관리
uv run term2ai profile list
uv run term2ai profile create development --base default
uv run term2ai profile edit development
uv run term2ai profile export development > dev-profile.toml
uv run term2ai start --profile production

# 플러그인 관리
uv run term2ai plugin list
uv run term2ai plugin install filter-secrets
uv run term2ai plugin configure filter-secrets --level high
uv run term2ai plugin disable filter-secrets

# 시각화 도구
uv run term2ai visualize --pipeline
uv run term2ai visualize --events --output svg > events.svg
uv run term2ai visualize --state-machine
```

### 디버깅 및 보안 명령어들
```bash
# 디버그 모드
uv run term2ai start --debug
uv run term2ai start --trace --log-file trace.log
uv run term2ai start --dry-run --verbose

# 보안 모드
uv run term2ai start --secure                  # 암호화된 세션
uv run term2ai start --sandbox                 # 샌드박스 모드
uv run term2ai start --audit                   # 감사 로깅

# 배치 실행
uv run term2ai batch commands.txt
uv run term2ai batch commands.txt --parallel 4
uv run term2ai batch commands.txt --on-error continue

# 테스트 실행
uv run term2ai test --scenario basic
uv run term2ai test --property-based
uv run term2ai test --coverage
```

## 함수형 구현 참고사항

### 함수형 CLI 의존성
- **typer**: CLI 프레임워크 (함수형 래핑)
- **rich**: 터미널 출력 포맷팅 (순수 함수 활용)
- **pydantic**: 설정 검증 (불변 모델)
- **toml**: 설정 파일 파싱

### 함수형 설계 결정
1. **명령어 Effect**: 모든 CLI 명령어를 IOEffect로 구현
2. **순수 파싱**: 모든 입력 파싱을 순수 함수로 처리
3. **불변 설정**: 모든 설정을 불변 객체로 관리
4. **스트림 처리**: 대화형 입력을 함수형 스트림으로 처리
5. **합성 가능성**: 작은 명령어들의 합성으로 복잡한 작업 구현

### 사용자 경험 고려사항
- **즉각적 피드백**: 명령어 실행 시 진행률 표시
- **명확한 에러 메시지**: 모든 에러를 사용자 친화적으로 포맷팅
- **일관된 인터페이스**: 모든 명령어가 동일한 패턴 따름
- **도움말 완성도**: 모든 기능에 대한 상세한 도움말 제공

## 함수형 승인 기준
- [ ] 모든 CLI 파싱이 순수 함수로 구현됨
- [ ] 모든 명령어가 IOEffect로 캡슐화됨
- [ ] Result 모나드로 모든 CLI 에러 타입 안전하게 처리
- [ ] 불변 설정 객체로 모든 설정 관리
- [ ] Property-based 테스트로 CLI 파싱 속성 검증
- [ ] 대화형 모드가 함수형 스트림으로 구현됨
- [ ] 모든 출력 포맷팅이 순수 함수로 구현됨
- [ ] CLI 도움말이 실제 기능과 100% 일치
- [ ] 엔드투엔드 시나리오 테스트 통과

## 다음 체크포인트
함수형 CLI 인터페이스가 구현되면 실제 사용 가능한 `term2ai` 도구가 완성되며, [체크포인트 4: 이벤트 소싱 터미널 상태](04_event_sourcing_state.md)로 진행할 수 있습니다.
