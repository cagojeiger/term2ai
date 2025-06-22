#!/bin/bash
# Simple test runner script

echo "Running term2ai tests..."

# Default to running basic tests
TEST_SCOPE="${1:-basic}"

case $TEST_SCOPE in
    basic)
        echo "Running basic tests..."
        uv run pytest tests/test_project_structure.py tests/test_dependencies.py tests/test_pydantic_models.py -v
        ;;
    all)
        echo "Running all tests..."
        uv run pytest --cov=src/term2ai --cov-report=term-missing
        ;;
    coverage)
        echo "Running tests with coverage report..."
        uv run pytest --cov=src/term2ai --cov-report=term-missing --cov-report=html
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    *)
        echo "Usage: $0 [basic|all|coverage]"
        exit 1
        ;;
esac
