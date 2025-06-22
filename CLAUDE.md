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
```

### Code Quality
```bash
# Run type checking
uv run mypy src/term2ai

# Run linting
uv run ruff check src/ tests/

# Format code
uv run black src/ tests/

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
# Run the main CLI
uv run term2ai

# Run with specific options
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

### Key Components

**PTYWrapper Class** (`src/term2ai/core/pty_wrapper.py`):
- Core terminal wrapper with context manager support
- Must implement `__enter__`/`__exit__` for automatic resource cleanup
- Handles process lifecycle, basic I/O, and error handling

**AsyncIOManager Class** (`src/term2ai/core/async_io.py`):
- Asynchronous I/O operations with async context manager support  
- Must implement `__aenter__`/`__aexit__` for async resource management
- Handles non-blocking I/O, multiplexing, and timeouts

**SessionManager & SessionContext**:
- Session lifecycle management through context managers
- Automatic session cleanup and persistence handling

**ConfigManager & TempConfigContext**:
- Configuration management with temporary override support
- Context manager for temporary config changes that auto-restore

### Development Workflow

The project follows a checkpoint-based development approach:

- **Checkpoint 0**: Project setup (✅ Complete)
- **Checkpoint 1**: Basic PTY wrapper (🎯 Next)
- **Checkpoint 2**: I/O handling  
- **Checkpoint 3**: Terminal state management
- **Checkpoint 4**: Signal handling
- **Checkpoint 5**: ANSI parsing
- **Checkpoint 6**: Session management  
- **Checkpoint 7**: Advanced features

Each checkpoint has specific acceptance criteria including:
- All tests passing (≥95% success rate)
- ≥90% code coverage for core functionality
- Type checking with mypy
- Linting with ruff
- Context manager implementation and testing

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
- `docs/api-design.md`: API interfaces and usage patterns
- `docs/architecture.md`: System architecture and design principles  
- `docs/technical-decisions.md`: Technical choices and rationale
- `plan/checkpoints/`: Detailed checkpoint specifications and requirements

Always update relevant documentation when implementing features, especially for context manager interfaces and resource management patterns.