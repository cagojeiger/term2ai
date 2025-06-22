# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Term2AI is a **실용적 Python 터미널 래퍼**로, 안정적인 **PTY 제어**, **터미널 I/O 처리**, **세션 관리** 기능을 제공합니다. 필요한 부분에만 함수형 프로그래밍 개념을 적용하여 복잡도를 낮추고 유지보수성을 높입니다. Python의 관용적 패턴을 존중하면서 점진적으로 개선 가능한 구조를 제공합니다.

**Project Status**: 실용적 재설계 단계 (Checkpoint 1 완료). 기본 PTY 래퍼가 구현되었으며, 과도한 함수형 설계를 실용적 접근으로 전환 중입니다. 프로젝트는 `uv` 패키지 매니저를 사용하고 점진적 개선 방법론을 따릅니다.

### 핵심 기능
- **기본 PTY 래퍼**: ptyprocess 기반 안정적인 터미널 제어
- **간단한 API**: Python 개발자에게 친숙한 직관적 인터페이스
- **점진적 개선**: 기본 기능부터 시작, 필요시 고급 기능 추가
- **실용적 에러 처리**: 명확한 에러 메시지와 복구 가능한 설계
- **선택적 고급 기능**: blessed, keyboard hooks 등은 필요시만 사용
- **Unix 최적화**: Linux/macOS에서 최적 성능 (uvloop 선택적 사용)

## Development Commands

### Package Management
```bash
# Install core dependencies only
uv sync

# Add new dependency
uv add <package-name>

# Add development dependency
uv add --group dev <package-name>

# Install Unix performance optimizations (uvloop, aiosignal)
uv sync --group performance

# Install complete terminal hijacking features (keyboard, pynput, blessed)
uv sync --group hijacking

# Install all optional dependencies (recommended for full development)
uv sync --all-groups
```

### Code Quality
```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Run type checking
uv run mypy src/term2ai

# Run linting
uv run ruff check src/ tests/

# Format code
uv run black src/ tests/

# Auto-fix linting issues
uv run ruff check src/ tests/ --fix

# Fix type annotations to Python 3.10+ style
uv run ruff check --fix --unsafe-fixes .

# Run all quality checks
uv run ruff check src/ tests/ && uv run mypy src/term2ai && uv run black --check src/ tests/
```

### Testing
```bash
# 기본 테스트 실행
uv run pytest --cov=src/term2ai --cov-report=term-missing

# 단위 테스트만 실행
uv run pytest -m "unit"

# 통합 테스트 실행
uv run pytest -m "integration"

# PTY 관련 테스트 실행
uv run pytest tests/test_pty_wrapper.py

# 빠른 테스트 (느린 테스트 제외)
uv run pytest -m "not slow"

# 특정 테스트 함수 실행
uv run pytest -k "test_pty_basic_io"

# 테스트 타임아웃 설정 (PTY 테스트가 멈출 때)
uv run pytest --timeout=10

# 디버그 모드로 실행
uv run pytest -vv -s

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### CLI Application
```bash
# Current basic functionality (Checkpoint 0)
uv run python -c "from term2ai import hello; print(hello())"

# CLI interface (Checkpoint 2.5 - planned)
uv run term2ai --help                    # Show help
uv run term2ai start                     # Start transparent terminal session
uv run term2ai start --hijack all        # Full hijacking mode
uv run term2ai stats --last             # Show last session stats
uv run term2ai config show              # Show current configuration

# Advanced CLI usage (post Checkpoint 2.5)
uv run term2ai session list             # List active sessions
uv run term2ai monitor --dashboard      # Real-time monitoring dashboard
uv run term2ai doctor                   # System diagnostics
```

## 실용적 아키텍처 개요

### 설계 원칙

1. **실용성 우선**: 작동하는 코드부터 시작하여 점진적으로 개선합니다. 과도한 추상화를 피하고 필요한 기능에 집중합니다.

2. **점진적 개선**: 기본 기능이 안정적으로 동작한 후, 필요에 따라 고급 기능을 추가합니다. 모든 것을 한 번에 구현하려 하지 않습니다.

3. **명확한 에러 처리**: 기본 Python Exception을 활용하되, 사용자가 이해할 수 있는 명확한 에러 메시지를 제공합니다.

4. **표준 패턴 활용**: Python의 관용적 패턴을 존중하고, 표준 라이브러리와 잘 통합되는 API를 제공합니다.

### 현재 구현 상태

**Phase 1 - 기본 PTY 래퍼 (✅ 완료)**:
- `src/term2ai/pty_wrapper.py`: 기본 PTY 기능 제공
- ptyprocess 기반 안정적인 터미널 제어
- Context manager 패턴으로 리소스 관리
- 간단하고 직관적인 API

**Phase 2 - 핵심 유틸리티 (🎯 계획)**:
- 필요시 순수 함수로 데이터 변환 로직 추출
- ANSI 시퀀스 파싱 (실제 필요 발생시)
- 입력 검증 및 인코딩 함수
- 점진적으로 기능 추가

**Phase 3 - 고급 기능 (📋 선택적)**:
- blessed 터미널 제어 (풀스크린 앱 필요시)
- keyboard hooks (전역 단축키 필요시)
- 비동기 I/O (성능 이슈 발생시)
- Event sourcing (감사 추적 필요시)

### 실용적 개선 로드맵

1. **MVP 완성**: 기본 터미널 기능이 안정적으로 동작
2. **사용자 피드백**: 실제 사용 사례에서 필요한 기능 파악
3. **점진적 리팩토링**: 반복되는 패턴을 함수로 추출
4. **선택적 최적화**: 실제 병목 지점만 개선

### Development Workflow

The project follows a checkpoint-based development approach with detailed specifications in `plan/checkpoints/`. **Current project status: Checkpoint 1 is complete with basic PTY wrapper functionality implemented.**

**Implementation Status:**
- **Checkpoint 0**: Project setup (✅ Complete)
- **Checkpoint 1**: Basic PTY wrapper + blessed integration (✅ Complete)
- **Checkpoint 1.5**: Global hijacking system (keyboard + pynput + blessed) (📋 Pending - Next priority)
- **Checkpoint 2**: I/O handling + global input integration (📋 Pending)
- **Checkpoint 3**: CLI interface (`term2ai` command) (📋 Pending)
- **Checkpoint 4**: Terminal state management (📋 Pending)
- **Checkpoint 5**: Signal handling (📋 Pending)
- **Checkpoint 6**: ANSI parsing (📋 Pending)
- **Checkpoint 7**: Session management (📋 Pending)
- **Checkpoint 8**: Advanced features (📋 Pending)

**Development Philosophy** (updated):
- **실용적 개발**: Working code first, refine later
- **점진적 개선**: Start simple, add complexity only when needed
- **명확한 인터페이스**: Clear APIs over clever abstractions
- **사용자 중심**: Real user needs drive feature development

Each checkpoint has specific acceptance criteria including:
- All tests passing (≥95% success rate)
- ≥90% code coverage for core functionality
- Type checking with mypy
- Linting with ruff
- Context manager implementation and testing
- Resource leak prevention verification

### Critical Implementation Requirements

1. **Context Manager Implementation**: All resource-managing classes MUST implement appropriate context manager protocols to prevent resource leaks.

2. **Exception Safety**: Resource cleanup must be guaranteed even when exceptions occur.

3. **Async Resource Management**: Async operations must use async context managers (`async with`) for proper cleanup.

4. **RAII Pattern**: Resource Acquisition Is Initialization - resources are acquired in `__init__` or `__enter__` and automatically released in `__exit__`.

### Testing Strategy

- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: Component interaction testing
- **E2E Tests**: Full workflow testing with real terminals
- **Performance Tests**: Latency and throughput verification
- **Resource Safety Tests**: Context manager and exception safety verification

Use pytest markers to categorize tests: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`, `@pytest.mark.slow`.

### Documentation

The project maintains comprehensive documentation in `docs/` and `plan/`:
- `docs/api-design.md`: API interfaces and usage patterns with context manager examples
- `docs/architecture.md`: System architecture and design principles including RAII pattern
- `docs/technical-decisions.md`: Technical choices and rationale, including Context Manager vs manual resource management
- `plan/checkpoints/`: Detailed checkpoint specifications with acceptance criteria
- `plan/roadmap.md`: Overall development strategy and milestone tracking

**Documentation Requirements**:
- Always update relevant documentation when implementing features
- Include context manager interfaces and resource management patterns
- Maintain Korean language sections for development philosophy
- Update checkpoint status and acceptance criteria as features are completed
- Update this CLAUDE.md file's "Current Implementation Status" sections as work progresses

### Key Technical Decisions

From `docs/technical-decisions.md`:
- **PTY Library**: Using `ptyprocess` for stable terminal emulation
- **Architecture**: Start with sync, add async only when needed
- **Platform**: Unix-only (Linux/macOS) for simplicity
- **Resource Management**: Context managers for clean resource handling
- **Optional Libraries**: `blessed`, `keyboard`, `pynput` only when required

### Project Dependencies

**Core Dependencies**:
- `pexpect>=4.9.0`: Terminal automation and interaction
- `ptyprocess>=0.7.0`: Pseudo-terminal process management
- `pydantic>=2.11.7`: Data validation and serialization
- `rich>=14.0.0`: Terminal output formatting and styling
- `typer>=0.16.0`: CLI application framework
- `aiofiles>=23.2.0`: Asynchronous file I/O operations

**Performance Dependencies (Unix-only)**:
- `uvloop>=0.19.0`: High-performance event loop for asyncio
- `aiosignal>=1.3.1`: Asynchronous signal handling

**Hijacking Dependencies (Complete Terminal Control)**:
- `keyboard>=0.13.5`: Global keyboard event capture and system-level hooks
- `pynput>=1.7.6`: Cross-platform mouse and advanced input control
- `blessed>=1.20.0`: Advanced terminal control and fullscreen capabilities

**Development Dependencies**:
- `pytest>=8.4.1` with `pytest-asyncio>=1.0.0`: Testing framework
- `mypy>=1.16.1`: Static type checking
- `ruff>=0.12.0`: Fast Python linter
- `black>=25.1.0`: Code formatter
- `pytest-cov>=6.2.1`: Coverage reporting
- `pytest-timeout>=2.4.0`: Test timeout management
- `pre-commit>=4.2.0`: Git hook framework

The project requires Python 3.11+ and is designed exclusively for Unix systems (Linux/macOS). Windows is not supported to ensure optimal performance and simplicity.

### Project Scripts Entry Point

From `pyproject.toml`:
```toml
[project.scripts]
term2ai = "term2ai.cli:app"  # Note: CLI module not yet implemented
```

### Performance Goals (Unix-only)

From `plan/roadmap.md`:
- **I/O Latency**: < 3ms (with uvloop + epoll/kqueue optimization)
- **Throughput**: > 300MB/s (3-5x improvement over basic asyncio)
- **Memory Usage**: < 60MB (Unix memory management optimization)
- **CPU Usage**: < 2% (native Unix I/O performance)

### Common Issues and Solutions

1. **PTY tests hanging**: Use `--timeout=10` flag or skip with `--ignore=tests/test_pty_wrapper.py`
2. **Coverage data files**: Configure `.coveragerc` to prevent multiple coverage files
3. **Type annotation errors**: Use `uv run ruff check --fix --unsafe-fixes` to auto-fix
4. **Pre-commit failures**: Run `uv run pre-commit run --all-files` to fix before committing

## 실용적 개선 가이드 (2025-06-22 업데이트)

### 현재 상태 요약
- **완료**: 기본 PTY 래퍼 구현 (Checkpoint 1)
- **진행중**: 과도한 함수형 설계를 실용적 접근으로 전환
- **다음**: CLI 인터페이스 구현, 실제 사용 사례 테스트

### 권장 개발 접근법
1. **기본 기능 우선**: PTY I/O, 세션 관리 등 핵심 기능 완성
2. **사용자 피드백 기반**: 실제 필요한 기능만 추가
3. **점진적 리팩토링**: 동작하는 코드를 유지하며 개선
4. **실용적 테스트**: 단위 테스트 우선, Property-based는 선택적

### 피해야 할 것들
- ❌ 모든 것을 모나드로 래핑
- ❌ 과도한 타입 추상화
- ❌ 불필요한 함수형 라이브러리 도입
- ❌ 3중 하이재킹 시스템 (PTY + keyboard + pynput + blessed)
- ❌ 100% 함수형 순수성 추구

### 집중해야 할 것들
- ✅ 안정적인 PTY 처리
- ✅ 명확한 에러 메시지
- ✅ 간단한 CLI 인터페이스
- ✅ 실용적인 테스트
- ✅ 점진적 개선
