# Term2AI 사용자 가이드

## 소개

Term2AI는 함수형 프로그래밍 기반의 고급 터미널 래퍼로, 완전한 터미널 I/O 제어, 세션 관리, 실시간 필터링, 성능 분석 등의 기능을 제공합니다. 이 가이드는 Term2AI를 효과적으로 사용하는 방법을 설명합니다.

## 시작하기

### 설치

#### 기본 설치
```bash
# 기본 의존성만 설치
uv sync

# 최적 성능을 위한 설치 (Unix 전용, 권장)
uv sync --group performance

# 완전한 터미널 제어 기능 설치
uv sync --group hijacking

# 모든 기능 설치 (개발 환경 권장)
uv sync --all-groups
```

### 첫 실행

가장 간단한 사용법은 기본 터미널 세션을 시작하는 것입니다:

```bash
uv run term2ai start
```

이 명령은 기본 셸(보통 `/bin/bash`)로 투명한 터미널 세션을 시작합니다. 일반 터미널처럼 사용하면서 모든 I/O가 자동으로 기록됩니다.

### 기본 설정

처음 실행 시 기본 설정 파일이 `~/.term2ai/config.toml`에 생성됩니다:

```toml
[general]
shell = "/bin/bash"
default_profile = "default"

[hijacking]
level = "minimal"
keyboard = false
mouse = false

[logging]
enabled = true
path = "~/.term2ai/logs"
```

## 주요 기능

### 1. 터미널 세션 관리

#### 세션 시작
```bash
# 기본 세션
uv run term2ai start

# 특정 셸 사용
uv run term2ai start --shell /bin/zsh

# 커스텀 설정 파일 사용
uv run term2ai start --config ~/my-config.toml

# 상세 모드
uv run term2ai start --verbose
```

#### 하이재킹 레벨 이해하기

Term2AI는 세 가지 하이재킹 레벨을 제공합니다:

1. **minimal** (기본값): PTY만 사용
   - 가장 가벼운 모드
   - 기본적인 터미널 I/O 캡처
   ```bash
   uv run term2ai start --hijack-level minimal
   ```

2. **standard**: PTY + 키보드 캡처
   - 시스템 레벨 키보드 이벤트 캡처
   - 더 정확한 입력 분석
   ```bash
   uv run term2ai start --hijack-level standard
   ```

3. **complete**: PTY + 키보드 + 마우스 + blessed
   - 완전한 터미널 제어
   - 고급 터미널 기능 활용
   ```bash
   uv run term2ai start --hijack-level complete
   ```

### 2. 실시간 필터링

민감한 정보를 자동으로 필터링하거나 출력을 변환할 수 있습니다:

#### 비밀번호 필터링
```bash
# 비밀번호 자동 마스킹
uv run term2ai start --filter-passwords

# 예시 출력:
# $ mysql -u root -p
# Enter password: ********
```

#### 정규식 필터링
```bash
# 특정 패턴 필터링
uv run term2ai start --filter-regex "API_KEY=.*"

# 여러 패턴 필터링
uv run term2ai start --filter-regex "SECRET.*" --filter-regex "TOKEN.*"
```

#### 출력 변환
```bash
# 모든 출력을 대문자로
uv run term2ai start --transform uppercase

# 자동 색상화
uv run term2ai start --transform colorize
```

### 3. 세션 녹화 및 재생

#### 세션 녹화
```bash
# 기본 녹화 (JSON 형식)
uv run term2ai record --output session.json

# Asciinema 형식으로 녹화
uv run term2ai record --format asciinema --output session.cast

# 압축 및 타임스탬프 포함
uv run term2ai record --compress --timestamp --output session.json.gz
```

#### 세션 재생
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

### 4. 통계 및 분석

#### 세션 통계 확인
```bash
# 전체 통계
uv run term2ai stats

# 마지막 세션 통계
uv run term2ai stats --last

# 특정 메트릭만 표시
uv run term2ai stats --metric commands

# JSON 형식으로 출력
uv run term2ai stats --format json
```

#### 세션 분석
```bash
# Git 명령어 사용 패턴 분석
uv run term2ai analyze --pattern "git"

# 에러 패턴 분석
uv run term2ai analyze --pattern "error|failed|fatal"

# 지난 7일간 분석
uv run term2ai analyze --time-range 7d
```

### 5. 성능 측정

Term2AI의 성능을 측정하고 네이티브 터미널과 비교할 수 있습니다:

```bash
# 전체 벤치마크
uv run term2ai benchmark

# 처리량 측정
uv run term2ai benchmark --metric throughput --duration 60

# 네이티브 터미널과 비교
uv run term2ai benchmark --compare-with native

# 결과 저장
uv run term2ai benchmark --output results.json
```

예상 성능 (Unix 최적화):
- I/O 지연시간: <3ms
- 처리량: >300MB/s
- 메모리 사용량: <60MB
- CPU 사용률: <2%

### 6. 프로필 시스템

다양한 환경에 맞는 설정 프로필을 관리할 수 있습니다:

#### 프로필 생성
```bash
# 개발 환경 프로필 생성
uv run term2ai profile create development --base default

# 프로덕션 프로필 생성
uv run term2ai profile create production
```

#### 프로필 사용
```bash
# 특정 프로필로 시작
uv run term2ai start --profile development

# 프로필 내보내기
uv run term2ai profile export development > dev-profile.toml
```

### 7. 대화형 모드

대화형 CLI 인터페이스를 사용하면 더 편리하게 명령어를 실행할 수 있습니다:

```bash
# 대화형 모드 시작
uv run term2ai interactive

# 대화형 모드에서:
Term2AI> start --shell /bin/zsh
[세션 시작됨]

Term2AI> stats --last
마지막 세션: 5분 20초, 명령어 15개

Term2AI> help
[사용 가능한 명령어 목록]

Term2AI> exit
```

특징:
- 실시간 자동완성
- 명령어 히스토리 (화살표 키)
- 인라인 도움말
- 현재 상태 표시

### 8. 시스템 진단

문제가 발생했을 때 진단 도구를 사용할 수 있습니다:

```bash
# 기본 진단
uv run term2ai doctor

# 문제 자동 수정
uv run term2ai doctor --fix

# 상세 진단 보고서
uv run term2ai doctor --verbose --report diagnosis.txt
```

진단 항목:
- PTY 지원 확인
- 권한 설정 확인
- 의존성 설치 상태
- 터미널 기능 테스트

## 고급 기능

### 플러그인 시스템

```bash
# 플러그인 설치
uv run term2ai plugin install filter-secrets

# 플러그인 설정
uv run term2ai plugin configure filter-secrets --level high

# 플러그인 목록
uv run term2ai plugin list
```

### 보안 모드

민감한 작업을 수행할 때는 보안 모드를 사용하세요:

```bash
# 암호화된 세션
uv run term2ai start --secure

# 샌드박스 모드
uv run term2ai start --sandbox

# 감사 로깅 활성화
uv run term2ai start --audit
```

### 배치 실행

여러 명령어를 자동으로 실행할 수 있습니다:

```bash
# 명령어 파일 준비
cat > commands.txt << EOF
echo "시작"
ls -la
git status
echo "완료"
EOF

# 배치 실행
uv run term2ai batch commands.txt

# 병렬 실행
uv run term2ai batch commands.txt --parallel 4
```

## 문제 해결

### 일반적인 문제

#### 1. 권한 오류
```bash
# 진단 및 수정
uv run term2ai doctor --fix
```

#### 2. 성능 문제
```bash
# 성능 최적화 의존성 설치
uv sync --group performance

# 벤치마크 실행
uv run term2ai benchmark
```

#### 3. 하이재킹 실패
```bash
# 하이재킹 레벨 낮추기
uv run term2ai start --hijack-level minimal

# 또는 특정 기능만 활성화
uv run term2ai start --enable-keyboard --disable-mouse
```

### 디버깅

문제를 자세히 조사해야 할 때:

```bash
# 디버그 모드
uv run term2ai start --debug

# 모든 이벤트 추적
uv run term2ai start --trace --log-file trace.log

# 드라이런 (실제 실행 없이 검증)
uv run term2ai start --dry-run
```

## 모범 사례

### 1. 적절한 하이재킹 레벨 선택
- 일반 사용: `minimal`
- 입력 분석 필요: `standard`
- 완전한 제어 필요: `complete`

### 2. 민감 정보 보호
```bash
# 항상 비밀번호 필터링 활성화
uv run term2ai start --filter-passwords

# 민감한 작업은 보안 모드로
uv run term2ai start --secure --audit
```

### 3. 정기적인 세션 정리
```bash
# 30일 이상 된 세션 정리
uv run term2ai session clean --older-than 30d
```

### 4. 프로필 활용
개발, 테스트, 프로덕션 환경별로 프로필을 만들어 사용하세요.

## 설정 파일 예제

### 개발 환경 설정
```toml
# ~/.term2ai/profiles/development.toml
[general]
shell = "/bin/zsh"
verbose = true

[hijacking]
level = "complete"
keyboard = true
mouse = true

[logging]
enabled = true
level = "debug"

[filters]
passwords = true
regex = ["API_KEY=.*", "SECRET=.*"]
```

### 프로덕션 환경 설정
```toml
# ~/.term2ai/profiles/production.toml
[general]
shell = "/bin/bash"
verbose = false

[hijacking]
level = "minimal"

[security]
encryption = true
audit = true

[performance]
buffer_size = 16384
```

## 추가 리소스

- [CLI 레퍼런스](cli-reference.md): 모든 명령어의 상세 설명
- [아키텍처 문서](architecture.md): 시스템 구조 이해
- [API 문서](api-design.md): 프로그래밍 인터페이스
- [함수형 패턴](functional-patterns.md): 함수형 프로그래밍 가이드

## 도움 받기

문제가 있거나 기능 요청이 있으시면:
- GitHub Issues: https://github.com/yourusername/term2ai/issues
- 문서: https://term2ai.readthedocs.io
