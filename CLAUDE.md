# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Term2AI is a **함수형 프로그래밍 기반** Python 터미널 래퍼로, **순수 함수**, **모나드 시스템**, **Effect 캡슐화**를 통해 **완전한 I/O 제어**, **이벤트 스트림 처리**, **AI 통합**, **고급 터미널 에뮬레이션** 기능을 제공합니다. 모든 부작용을 명시적으로 관리하고, 불변 데이터 구조를 통해 동시성 안전성을 보장하며, Property-Based Testing으로 견고한 소프트웨어를 구축합니다.

**Project Status**: 함수형 재설계 단계 (Checkpoint 0 완료). 함수형 아키텍처 문서화와 모나드 시스템 설계가 완료되었으며, 순수 함수 기반 PTY 처리 구현을 진행 중입니다. 프로젝트는 `uv` 패키지 매니저를 사용하고 Property-Based TDD 방법론을 따릅니다.

### 함수형 핵심 기능
- **순수 함수 레이어**: 모든 비즈니스 로직을 부작용 없는 순수 함수로 구현
- **Effect 시스템**: IOEffect 모나드를 통한 모든 I/O 작업 캡슐화 (PTY, 파일, 네트워크)
- **이벤트 스트림**: 키보드, 마우스, PTY 이벤트를 함수형 스트림으로 처리
- **모나드 기반 에러 처리**: Result와 Maybe 모나드로 타입 안전한 에러 및 null 처리
- **이벤트 소싱**: 모든 상태 변경을 불변 이벤트로 기록하여 완벽한 추적성 제공
- **함수 합성**: 작은 순수 함수들의 합성으로 복잡한 터미널 기능 구현

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

### 함수형 Testing
```bash
# Property-based testing으로 순수 함수 검증
uv run pytest --cov=src/term2ai --cov-report=term-missing

# 순수 함수 테스트 (Property-based)
uv run pytest -m "pure_function"

# 모나드 법칙 테스트
uv run pytest -m "monad_laws"

# Effect 시스템 테스트 (모킹)
uv run pytest -m "effect_test"

# 이벤트 소싱 일관성 테스트
uv run pytest -m "event_sourcing"

# 함수 합성 테스트
uv run pytest -m "composition"

# 속성 기반 테스트만 실행
uv run pytest -k "test_property"

# 순수 함수 역변환 속성 테스트
uv run pytest -k "test_inverse"

# Hypothesis를 이용한 경계값 테스트
uv run pytest --hypothesis-show-statistics

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

## 함수형 아키텍처 개요

### 함수형 설계 원칙

1. **순수성 (Purity)**: 모든 비즈니스 로직은 순수 함수로 구현하여 참조 투명성과 예측 가능성을 보장합니다. 동일한 입력에 대해 항상 동일한 출력을 생성하고 부작용이 없습니다.

2. **Property-Based TDD**: 기존 TDD에서 Property-Based Testing으로 발전하여, 함수의 수학적 속성을 검증합니다. 모나드 법칙, 함수 합성 법칙, 역변환 속성 등을 자동으로 검증합니다.

3. **모나드 타입 안전성**: Result, Maybe, IOEffect 모나드를 통해 에러, null, 부작용을 타입 시스템에서 명시적으로 관리합니다. 모든 위험한 연산이 타입에 표현됩니다.

4. **함수형 스트림 아키텍처**: 계층화된 함수 합성 시스템:
   - **순수 함수 레이어**: 모든 도메인 로직 (ANSI 파싱, 데이터 변환, 검증)
   - **Effect 레이어**: IOEffect 모나드로 모든 부작용 캡슐화
   - **스트림 레이어**: 비동기 이벤트 스트림의 함수형 변환
   - **이벤트 소싱 레이어**: 불변 이벤트 저장소와 상태 재구성
   - **합성 레이어**: 함수 파이프라인과 모나드 체인
   - **애플리케이션 레이어**: 최종 사용자 기능의 Effect 합성

### 함수형 핵심 구성요소 (계획된 아키텍처)

**순수 함수 모듈들** (planned: `src/term2ai/pure/`):
- 모든 비즈니스 로직을 순수 함수로 구현
- `parse_ansi_sequence: str -> ANSISequence`
- `validate_terminal_state: TerminalState -> Result[TerminalState, Error]`
- `transform_keyboard_event: RawInput -> KeyboardEvent`
- `analyze_input_patterns: [Event] -> PatternAnalysis`

**모나드 시스템** (planned: `src/term2ai/monads/`):
- `IOEffect[T]`: 모든 I/O 작업을 캡슐화하는 Effect 모나드
- `Result[T, E]`: 타입 안전한 에러 처리 모나드
- `Maybe[T]`: null 안전성을 위한 모나드
- `State[S, A]`: 함수형 상태 관리 모나드

**이벤트 스트림 처리** (planned: `src/term2ai/streams/`):
- `create_keyboard_stream_effect() -> IOEffect[AsyncStream[KeyboardEvent]]`
- `create_pty_stream_effect(handle) -> IOEffect[AsyncStream[PTYEvent]]`
- `merge_streams([stream]) -> AsyncStream[Event]`
- `filter_stream(stream, predicate) -> AsyncStream[Event]`

**이벤트 소싱 시스템** (planned: `src/term2ai/events/`):
- 불변 이벤트 저장소: `EventStore`
- 상태 재구성: `fold_events: [Event] -> ApplicationState`
- 이벤트 추가: `append_event: EventStore -> Event -> EventStore`
- 시간 여행 디버깅 지원

**함수 합성 파이프라인** (planned: `src/term2ai/pipelines/`):
- `pty_processing_pipeline: PTYHandle -> IOEffect[ProcessedData]`
- `terminal_rendering_pipeline: TerminalState -> IOEffect[Unit]`
- `event_analysis_pipeline: [Event] -> IOEffect[Analysis]`
- 모든 복잡한 기능을 순수 함수의 합성으로 구현

**함수형 구현 현재 상태**:
- 함수형 아키텍처 문서화 완료 (`docs/functional-architecture.md`)
- 기존 OOP 문서들을 함수형 관점으로 전면 재작성 완료
- Property-Based Testing 인프라 설계 완료 (hypothesis 기반)
- 모나드 시스템 타입 설계 완료 (IOEffect, Result, Maybe)
- 이벤트 소싱 아키텍처 설계 완료
- 다음 단계: 순수 함수 기반 PTY 처리 구현 시작

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

**Development Philosophy** (from `plan/roadmap.md`):
- **테스트 주도 개발**: Tests written first, implementation follows
- **점진적 개발**: Incremental feature building through checkpoints
- **타입 안전성**: Pydantic models with comprehensive type hints
- **문서 주도**: Documentation maintained alongside code

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
- **PTY Library**: Using `ptyprocess` instead of `subprocess` for true terminal emulation
- **Architecture**: Hybrid sync/async approach for progressive complexity
- **Platform**: Unix-only (Linux/macOS) for optimal performance
- **Context Managers**: RAII pattern for all resource management
- **Hijacking Libraries**: `keyboard` + `pynput` + `blessed` for complete terminal control

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
