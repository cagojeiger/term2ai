# Term2AI CLI 레퍼런스

## 개요
Term2AI는 실용적이고 사용하기 쉬운 터미널 래퍼입니다. 이 문서는 계획된 CLI 명령어의 사용법을 설명합니다. (주의: CLI는 아직 구현되지 않았으며, 이는 향후 구현될 인터페이스입니다)

## 기본 사용법
```bash
uv run term2ai [COMMAND] [OPTIONS]
```

## 핵심 명령어

### `start` - 터미널 세션 시작
투명한 터미널 래핑을 시작합니다. 사용자는 일반 터미널처럼 사용하면서 모든 I/O가 기록됩니다.

```bash
uv run term2ai start [OPTIONS]
```

**옵션:**
- `--shell PATH`: 사용할 셸 경로 (기본값: `/bin/bash`)
- `--config PATH`: 설정 파일 경로
- `--verbose`: 상세 출력 모드
- `--log-file PATH`: 세션 로그 파일 경로

**실시간 필터링 옵션:**
- `--filter-passwords`: 비밀번호 자동 마스킹
- `--filter-regex PATTERN`: 정규식 기반 필터링
- `--transform FUNCTION`: 출력 변환
  - `uppercase`: 모든 출력 대문자로
  - `lowercase`: 모든 출력 소문자로
  - `colorize`: 자동 색상화
- `--mask-sensitive`: 민감 정보 자동 감지 및 마스킹

**예제:**
```bash
# 기본 사용
uv run term2ai start

# zsh 셸로 시작
uv run term2ai start --shell /bin/zsh

# 상세 모드로 시작
uv run term2ai start --verbose

# 세션 로깅과 함께 시작
uv run term2ai start --log-file session.log

# 커스텀 설정 파일 사용
uv run term2ai start --config ~/.term2ai/config.toml
```

### `stats` - 세션 통계 확인
터미널 사용 통계를 표시합니다.

```bash
uv run term2ai stats [OPTIONS]
```

**옵션:**
- `--session-id ID`: 특정 세션의 통계
- `--last`: 마지막 세션 통계
- `--format FORMAT`: 출력 형식 (`table`, `json`, `csv`)
- `--metric METRIC`: 특정 메트릭만 표시
  - `commands`: 명령어 사용 통계
  - `io`: 입출력 통계
  - `time`: 시간 관련 통계
  - `patterns`: 사용 패턴 분석

**예제:**
```bash
# 전체 통계
uv run term2ai stats

# 마지막 세션 통계
uv run term2ai stats --last

# JSON 형식으로 출력
uv run term2ai stats --format json

# 명령어 사용 통계만
uv run term2ai stats --metric commands
```

### `config` - 설정 관리
Term2AI 설정을 관리합니다.

```bash
uv run term2ai config [SUBCOMMAND] [OPTIONS]
```

**서브커맨드:**
- `show`: 현재 설정 표시
- `set KEY VALUE`: 설정 값 변경
- `reset`: 기본값으로 초기화
- `validate`: 설정 파일 검증

**주요 설정 키:**
- `shell`: 기본 셸 경로
- `hijacking.keyboard`: 키보드 캡처 활성화
- `hijacking.mouse`: 마우스 캡처 활성화
- `hijacking.blessed`: blessed 터미널 제어
- `logging.enabled`: 로깅 활성화
- `logging.path`: 로그 파일 경로
- `filters.passwords`: 비밀번호 필터링
- `performance.buffer_size`: 버퍼 크기

**예제:**
```bash
# 현재 설정 확인
uv run term2ai config show

# 기본 셸 변경
uv run term2ai config set shell /bin/fish

# 키보드 캡처 활성화
uv run term2ai config set hijacking.keyboard true

# 설정 초기화
uv run term2ai config reset

# 설정 검증
uv run term2ai config validate
```

### `doctor` - 시스템 진단
시스템 호환성과 설정을 진단합니다.

```bash
uv run term2ai doctor [OPTIONS]
```

**옵션:**
- `--fix`: 발견된 문제 자동 수정
- `--verbose`: 상세 진단 정보
- `--report PATH`: 진단 보고서 저장
- `--check COMPONENT`: 특정 컴포넌트만 검사
  - `pty`: PTY 지원
  - `permissions`: 권한 설정
  - `dependencies`: 의존성 설치
  - `terminal`: 터미널 기능

**예제:**
```bash
# 기본 진단
uv run term2ai doctor

# 문제 자동 수정
uv run term2ai doctor --fix

# 상세 진단 및 보고서 생성
uv run term2ai doctor --verbose --report diagnosis.txt

# PTY 지원만 검사
uv run term2ai doctor --check pty
```

### `interactive` - 대화형 모드
대화형 CLI 인터페이스를 시작합니다.

```bash
uv run term2ai interactive [OPTIONS]
```

**기능:**
- 실시간 명령어 자동완성
- 인라인 도움말
- 명령어 히스토리
- 실시간 통계 표시
- 함수형 스트림 기반 입력 처리

**예제:**
```bash
# 대화형 모드 시작
uv run term2ai interactive

# 대화형 모드 명령어:
Term2AI> start --shell /bin/zsh
Term2AI> stats --last
Term2AI> help
Term2AI> exit
```

## 세션 관리 명령어

### `record` - 세션 녹화
터미널 세션을 녹화합니다.

```bash
uv run term2ai record [OPTIONS]
```

**옵션:**
- `--output PATH`: 출력 파일 경로
- `--format FORMAT`: 녹화 형식
  - `json`: Term2AI 네이티브 형식 (기본값)
  - `asciinema`: Asciinema 형식
  - `typescript`: Script 형식
- `--compress`: 압축 활성화
- `--timestamp`: 타임스탬프 포함

**예제:**
```bash
# 기본 녹화
uv run term2ai record --output session.json

# Asciinema 형식으로 녹화
uv run term2ai record --format asciinema --output session.cast

# 압축된 타임스탬프 포함 녹화
uv run term2ai record --compress --timestamp
```

### `replay` - 세션 재생
녹화된 세션을 재생합니다.

```bash
uv run term2ai replay PATH [OPTIONS]
```

**옵션:**
- `--speed FLOAT`: 재생 속도 (기본값: 1.0)
- `--pause-on-output`: 출력 시 일시정지
- `--skip-idle TIME`: 유휴 시간 건너뛰기
- `--max-wait TIME`: 최대 대기 시간
- `--loop`: 반복 재생

**예제:**
```bash
# 기본 재생
uv run term2ai replay session.json

# 2배속 재생
uv run term2ai replay session.json --speed 2.0

# 출력마다 일시정지
uv run term2ai replay session.json --pause-on-output

# 3초 이상 유휴 시간 건너뛰기
uv run term2ai replay session.json --skip-idle 3
```

### `session` - 세션 관리
활성 세션을 관리합니다.

```bash
uv run term2ai session [SUBCOMMAND] [OPTIONS]
```

**서브커맨드:**
- `list`: 세션 목록 표시
- `info ID`: 세션 상세 정보
- `export ID`: 세션 내보내기
- `import PATH`: 세션 가져오기
- `clean`: 오래된 세션 정리

**예제:**
```bash
# 세션 목록
uv run term2ai session list

# 세션 정보
uv run term2ai session info abc123

# 세션 내보내기
uv run term2ai session export abc123 --format json

# 30일 이상 된 세션 정리
uv run term2ai session clean --older-than 30d
```

## 분석 및 성능 명령어

### `analyze` - 세션 분석
세션 데이터를 분석합니다.

```bash
uv run term2ai analyze [OPTIONS]
```

**옵션:**
- `--pattern PATTERN`: 분석할 패턴
- `--session-id ID`: 특정 세션 분석
- `--time-range RANGE`: 시간 범위 지정
- `--output-format FORMAT`: 결과 형식
- `--ai-model MODEL`: AI 모델 사용 (미래 기능)

**예제:**
```bash
# Git 명령어 패턴 분석
uv run term2ai analyze --pattern "git"

# 특정 세션의 에러 패턴 분석
uv run term2ai analyze --session-id abc123 --pattern "error|failed"

# 지난 7일간 분석
uv run term2ai analyze --time-range 7d
```

### `benchmark` - 성능 측정
Term2AI의 성능을 측정합니다.

```bash
uv run term2ai benchmark [OPTIONS]
```

**옵션:**
- `--metric METRIC`: 측정할 메트릭
  - `throughput`: 처리량 (MB/s)
  - `latency`: 지연시간 (ms)
  - `memory`: 메모리 사용량
  - `cpu`: CPU 사용률
- `--duration SECONDS`: 테스트 시간
- `--compare-with BASELINE`: 기준선과 비교
- `--output PATH`: 결과 저장

**예제:**
```bash
# 전체 벤치마크
uv run term2ai benchmark

# 처리량 측정 (60초)
uv run term2ai benchmark --metric throughput --duration 60

# 네이티브 터미널과 비교
uv run term2ai benchmark --compare-with native

# 결과 저장
uv run term2ai benchmark --output benchmark-results.json
```

## 고급 기능

### `profile` - 프로필 관리
설정 프로필을 관리합니다.

```bash
uv run term2ai profile [SUBCOMMAND] [OPTIONS]
```

**서브커맨드:**
- `list`: 프로필 목록
- `create NAME`: 새 프로필 생성
- `edit NAME`: 프로필 편집
- `delete NAME`: 프로필 삭제
- `export NAME`: 프로필 내보내기
- `import PATH`: 프로필 가져오기

**예제:**
```bash
# 프로필 목록
uv run term2ai profile list

# 개발 환경 프로필 생성
uv run term2ai profile create development --base default

# 프로필로 시작
uv run term2ai start --profile development

# 프로필 내보내기
uv run term2ai profile export development > dev-profile.toml
```

### `plugin` - 플러그인 관리
플러그인을 관리합니다.

```bash
uv run term2ai plugin [SUBCOMMAND] [OPTIONS]
```

**서브커맨드:**
- `list`: 설치된 플러그인
- `install NAME`: 플러그인 설치
- `uninstall NAME`: 플러그인 제거
- `enable NAME`: 플러그인 활성화
- `disable NAME`: 플러그인 비활성화
- `configure NAME`: 플러그인 설정

**예제:**
```bash
# 플러그인 목록
uv run term2ai plugin list

# 플러그인 설치
uv run term2ai plugin install filter-secrets

# 플러그인 설정
uv run term2ai plugin configure filter-secrets --level high
```

### `visualize` - 시각화 도구
Term2AI의 내부 동작을 시각화합니다.

```bash
uv run term2ai visualize [OPTIONS]
```

**옵션:**
- `--pipeline`: Effect 파이프라인 구조
- `--events`: 이벤트 플로우
- `--state-machine`: 상태 머신
- `--dependencies`: 의존성 그래프
- `--output FORMAT`: 출력 형식 (`text`, `dot`, `svg`)

**예제:**
```bash
# 파이프라인 시각화
uv run term2ai visualize --pipeline

# 이벤트 플로우 SVG 생성
uv run term2ai visualize --events --output svg > events.svg

# 상태 머신 텍스트 출력
uv run term2ai visualize --state-machine
```

## 디버깅 및 테스트

### `debug` - 디버그 모드
디버그 정보를 표시합니다.

```bash
uv run term2ai start --debug [OPTIONS]
```

**디버그 옵션:**
- `--debug`: 상세 로깅 활성화
- `--trace`: 모든 이벤트 추적
- `--dry-run`: 실제 실행 없이 검증
- `--log-level LEVEL`: 로그 레벨 설정
- `--log-file PATH`: 로그 파일 경로

**예제:**
```bash
# 디버그 모드로 시작
uv run term2ai start --debug

# 추적 모드
uv run term2ai start --trace --log-file trace.log

# 드라이런
uv run term2ai start --dry-run --verbose
```

### `test` - 테스트 실행
통합 테스트를 실행합니다.

```bash
uv run term2ai test [OPTIONS]
```

**옵션:**
- `--scenario NAME`: 특정 시나리오 테스트
- `--property-based`: Property-Based 테스트
- `--coverage`: 커버리지 측정
- `--benchmark`: 성능 테스트 포함

**예제:**
```bash
# 기본 시나리오 테스트
uv run term2ai test --scenario basic

# Property-Based 테스트
uv run term2ai test --property-based

# 커버리지 측정
uv run term2ai test --coverage
```

## 보안 기능

### 보안 모드 옵션
```bash
# 암호화된 세션
uv run term2ai start --secure

# 샌드박스 모드
uv run term2ai start --sandbox

# 감사 로깅
uv run term2ai start --audit

# 모든 보안 기능 활성화
uv run term2ai start --secure --sandbox --audit
```

## 배치 작업

### `batch` - 배치 실행
여러 명령어를 배치로 실행합니다.

```bash
uv run term2ai batch PATH [OPTIONS]
```

**옵션:**
- `--parallel N`: 병렬 실행 수
- `--on-error ACTION`: 에러 처리 (`stop`, `continue`, `retry`)
- `--timeout SECONDS`: 명령어 타임아웃
- `--output-dir PATH`: 결과 저장 디렉토리

**예제:**
```bash
# 순차 실행
uv run term2ai batch commands.txt

# 4개 병렬 실행
uv run term2ai batch commands.txt --parallel 4

# 에러 시 계속
uv run term2ai batch commands.txt --on-error continue
```

## 환경 변수

Term2AI는 다음 환경 변수를 지원합니다:

- `TERM2AI_CONFIG`: 기본 설정 파일 경로
- `TERM2AI_SHELL`: 기본 셸 경로
- `TERM2AI_LOG_LEVEL`: 로그 레벨
- `TERM2AI_HIJACK_LEVEL`: 기본 하이재킹 레벨
- `TERM2AI_PLUGIN_PATH`: 플러그인 검색 경로

## 설정 파일 형식

Term2AI는 TOML 형식의 설정 파일을 사용합니다:

```toml
# ~/.term2ai/config.toml
[general]
shell = "/bin/zsh"
default_profile = "development"

[hijacking]
keyboard = true
mouse = false
blessed = true
level = "standard"

[logging]
enabled = true
path = "~/.term2ai/logs"
level = "info"
rotation = "daily"

[filters]
passwords = true
regex = ["SECRET.*", "TOKEN.*"]

[performance]
buffer_size = 8192
use_uvloop = true
async_io = true

[security]
encryption = false
audit = false
sandbox = false
```

## 설계 원칙

Term2AI CLI는 다음 원칙을 따릅니다:

1. **직관적 인터페이스**: 복잡한 옵션보다 간단한 명령어
2. **명확한 에러 메시지**: 사용자가 이해할 수 있는 메시지
3. **점진적 기능 추가**: 기본 기능부터 시작
4. **표준 관례 준수**: Unix CLI 관례 따르기
5. **실용적 접근**: 필요한 기능만 구현

## 성능 목표

Unix 시스템에서 최적화된 성능:
- I/O 지연시간: <3ms
- 처리량: >300MB/s
- 메모리 사용량: <60MB
- CPU 사용률: <2%

## 문제 해결

일반적인 문제와 해결 방법:

1. **권한 오류**: `uv run term2ai doctor --fix`
2. **의존성 누락**: `uv sync --all-groups`
3. **성능 문제**: `uv sync --group performance`
4. **하이재킹 실패**: 하이재킹 레벨 조정

자세한 문제 해결은 사용자 가이드를 참조하세요.

## 구현 상태 (2025-06-22)

**⚠️ 주의**: 이 CLI 레퍼런스는 계획된 인터페이스를 설명합니다. 실제 CLI는 아직 구현되지 않았습니다.

### 현재 구현된 기능
- ✅ 기본 PTY 래퍼 (`src/term2ai/pty_wrapper.py`)
- ✅ Python API로 PTY 제어 가능

### 계획된 기능 (미구현)
- ❌ CLI 인터페이스 (`term2ai` 명령어)
- ❌ 세션 관리 및 통계
- ❌ 설정 파일 시스템
- ❌ 플러그인 시스템
- ❌ 고급 필터링 및 변환

### 다음 단계
1. 기본 CLI 구현 (Checkpoint 3)
2. 간단한 `start` 명령어부터 시작
3. 실제 사용 피드백 기반 기능 추가
