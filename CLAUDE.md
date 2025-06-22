# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Term2AI is a Python-based terminal wrapper providing complete I/O control, AI integration, and advanced terminal emulation capabilities. The project follows a test-driven development (TDD) approach with 8 planned checkpoints for incremental feature development.

## Development Commands

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package-name>

# Add development dependency  
uv add --group dev <package-name>

# Install Unix performance optimizations (uvloop, aiosignal)
uv sync --group performance

# Install all optional dependencies
uv sync --all-groups
```

### Code Quality
```bash
# Run type checking
uv run mypy src/term2ai

# Run linting
uv run ruff check src/ tests/

# Format code
uv run black src/ tests/

# Auto-fix linting issues
uv run ruff check src/ tests/ --fix

# Run all quality checks
uv run ruff check src/ tests/ && uv run mypy src/term2ai && uv run black --check src/ tests/
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_specific_file.py

# Run tests with specific marker
uv run pytest -m "unit"
uv run pytest -m "integration" 
uv run pytest -m "e2e"

# Run tests excluding slow ones
uv run pytest -m "not slow"

# Generate coverage report
uv run pytest --cov-report=html
```

### CLI Application
```bash
# Run the main CLI (currently returns hello message - project in early development)
uv run python -c "from term2ai import hello; print(hello())"

# Future CLI interface (when implemented)
uv run term2ai --help
```

## Architecture Overview

### Core Design Principles

1. **Context Manager Pattern (RAII)**: All resource management uses Python's context manager protocol (`__enter__`/`__exit__` and `__aenter__`/`__aexit__`) to ensure automatic cleanup and prevent resource leaks.

2. **Test-Driven Development**: Features are implemented following strict TDD - tests are written first, then implementation follows to pass the tests.

3. **Type Safety**: Comprehensive type hints throughout with Pydantic models for data validation and mypy for static type checking.

4. **Modular Architecture**: Layered system with clear separation of concerns:
   - PTY Wrapper Core (lowest level)
   - I/O Management & Terminal State
   - Processing Layer (ANSI parsing, signal handling, filtering)
   - Feature Layer (sessions, AI integration, networking)
   - Plugin System
   - User Interface Layer

### Key Components (Planned Architecture)

**PTYWrapper Class** (planned: `src/term2ai/core/pty_wrapper.py`):
- Core terminal wrapper with context manager support
- Must implement `__enter__`/`__exit__` for automatic resource cleanup
- Handles process lifecycle, basic I/O, and error handling

**AsyncIOManager Class** (planned: `src/term2ai/core/async_io.py`):
- Asynchronous I/O operations with async context manager support  
- Must implement `__aenter__`/`__aexit__` for async resource management
- Handles non-blocking I/O, multiplexing, and timeouts

**SessionManager & SessionContext** (planned):
- Session lifecycle management through context managers
- Automatic session cleanup and persistence handling

**ConfigManager & TempConfigContext** (planned):
- Configuration management with temporary override support
- Context manager for temporary config changes that auto-restore

**Current Implementation Status**: Only basic module structure exists in `src/term2ai/`. Core classes are not yet implemented.

### Development Workflow

The project follows a checkpoint-based development approach with detailed specifications in `plan/checkpoints/`. **Current project status: Early development phase with only basic project structure in place.**

**Implementation Status:**
- **Checkpoint 0**: Project setup (✅ Complete)
- **Checkpoint 1**: Basic PTY wrapper (📋 Pending - Next priority)
- **Checkpoint 2**: I/O handling (📋 Pending)
- **Checkpoint 3**: Terminal state management (📋 Pending)
- **Checkpoint 4**: Signal handling (📋 Pending)
- **Checkpoint 5**: ANSI parsing (📋 Pending)
- **Checkpoint 6**: Session management (📋 Pending)
- **Checkpoint 7**: Advanced features (📋 Pending)

**Important**: Most core functionality described in this document represents planned architecture, not implemented features. Always check the actual source code in `src/term2ai/` before assuming functionality exists.

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

**Development Dependencies**:
- `pytest>=8.4.1` with `pytest-asyncio>=1.0.0`: Testing framework
- `mypy>=1.16.1`: Static type checking
- `ruff>=0.12.0`: Fast Python linter
- `black>=25.1.0`: Code formatter
- `pytest-cov>=6.2.1`: Coverage reporting

The project requires Python 3.11+ and is designed exclusively for Unix systems (Linux/macOS). Windows is not supported to ensure optimal performance and simplicity.