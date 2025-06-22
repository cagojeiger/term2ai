# term2ai

**완전한 I/O 제어**, **전역 입력 하이재킹**, **AI 통합**, **고급 터미널 에뮬레이션** 기능을 제공하는 Python 기반 터미널 래퍼입니다.

## 주요 기능

- 🖥️ **완전한 터미널 제어**: PTY 기반 터미널 세션 완벽 관리
- ⌨️ **전역 입력 하이재킹**: 시스템 레벨 키보드/마우스 이벤트 캡처
- 🎨 **고급 터미널 UI**: blessed 기반 전체 화면 터미널 제어
- 🤖 **AI 통합**: 터미널 향상을 위한 내장 AI 기능
- 🚀 **고성능**: uvloop를 활용한 Unix 최적화로 최대 처리량 달성
- 🔌 **플러그인 시스템**: 사용자 정의 기능을 위한 확장 가능한 아키텍처

## 요구사항

- Python 3.11 이상
- Unix 기반 시스템 (Linux/macOS)
- uv 패키지 매니저

## 설치 방법

### 1. uv 설치 (아직 설치하지 않은 경우)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 저장소 클론

```bash
git clone https://github.com/yourusername/term2ai.git
cd term2ai
```

### 3. 의존성 설치

```bash
# 핵심 의존성만 설치
uv sync

# 개발 도구를 포함한 모든 의존성 설치 (권장)
uv sync --all-groups

# 또는 특정 그룹만 설치:
uv sync --group dev          # 개발 도구 (pytest, mypy 등)
uv sync --group performance  # Unix 성능 최적화
uv sync --group hijacking    # 터미널 하이재킹 기능
```

## 개발

### 테스트 실행

```bash
# 기본 테스트 실행 (빠름)
./scripts/test.sh basic

# 모든 테스트 실행
./scripts/test.sh all

# 커버리지 리포트와 함께 테스트 실행
./scripts/test.sh coverage

# 또는 pytest 직접 실행
uv run pytest --cov=src/term2ai --cov-report=term-missing

# 특정 테스트 파일 실행
uv run pytest tests/test_specific_file.py

# 특정 마커로 테스트 실행
uv run pytest -m "unit"
uv run pytest -m "not slow"
```

### 코드 품질 관리

```bash
# 모든 pre-commit 훅 실행
uv run pre-commit run --all-files

# 또는 개별 도구 실행:

# 타입 체크
uv run mypy src/term2ai

# 린팅
uv run ruff check src/ tests/

# 린팅 문제 자동 수정
uv run ruff check src/ tests/ --fix

# 코드 포맷팅
uv run black src/ tests/

# 포맷팅 확인만 (변경 없음)
uv run black --check src/ tests/
```

### Pre-commit 설정

코드 품질을 자동으로 검사하는 pre-commit 훅이 설정되어 있습니다:

```bash
# pre-commit 훅 설치
uv run pre-commit install

# 수동으로 훅 실행
uv run pre-commit run --all-files
```

## 사용법 (개발 중)

CLI 인터페이스는 현재 개발 중입니다. 완성되면 다음과 같이 사용할 수 있습니다:

```bash
# 터미널 세션 시작
term2ai start

# 전체 하이재킹 모드로 시작
term2ai start --hijack all

# 세션 통계 보기
term2ai stats --last

# 설정 표시
term2ai config show
```

## 프로젝트 구조

```
term2ai/
├── src/term2ai/          # 소스 코드
│   ├── core/             # 핵심 기능
│   ├── models/           # 데이터 모델
│   └── utils/            # 유틸리티 함수
├── tests/                # 테스트 모음
├── plan/                 # 개발 계획
│   ├── checkpoints/      # 개발 마일스톤
│   └── models/           # 계획 모델
├── docs/                 # 기술 문서
└── scripts/              # 유틸리티 스크립트
```

## 개발 현황

이 프로젝트는 초기 개발 단계입니다. 현재 상태:

- ✅ **체크포인트 0**: 프로젝트 설정 (완료)
- ✅ **체크포인트 1**: 기본 PTY 래퍼 (완료)
- 📋 **체크포인트 1.5**: 전역 하이재킹 시스템 (대기)
- 📋 **체크포인트 2**: I/O 처리 (대기)
- 📋 **체크포인트 2.5**: CLI 인터페이스 (대기)
- 📋 **체크포인트 3**: 터미널 상태 관리 (대기)
- 📋 **체크포인트 4**: 시그널 처리 (대기)
- 📋 **체크포인트 5**: ANSI 파싱 (대기)
- 📋 **체크포인트 6**: 세션 관리 (대기)
- 📋 **체크포인트 7**: 고급 기능 (대기)

## 기여하기

1. 테스트 주도 개발(TDD) 접근법을 따라주세요
2. 모든 테스트가 90% 이상의 커버리지로 통과하는지 확인하세요
3. 커밋 전에 pre-commit 훅을 실행하세요
4. 필요에 따라 문서를 업데이트하세요

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 성능 목표

- **I/O 지연시간**: < 3ms
- **처리량**: > 300MB/s
- **메모리 사용량**: < 60MB
- **CPU 사용률**: < 2%

## 문제 해결

### 일반적인 문제

1. **Import 오류**: `uv sync --all-groups`로 모든 의존성을 설치했는지 확인하세요
2. **테스트 실패**: 일부 PTY 테스트는 플랫폼에 따라 타이밍 문제로 실패할 수 있습니다 - 이는 정상입니다
3. **커버리지 경고**: 올바른 설정을 사용하려면 `--cov-config=.coveragerc`를 사용하세요

### 도움 받기

- [문서](docs/)를 확인하세요
- 구현 세부사항은 [체크포인트](plan/checkpoints/)를 검토하세요
- GitHub에 이슈를 열어주세요
