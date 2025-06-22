#!/bin/bash
# Safe test runner that avoids hanging tests

echo "Running safe tests (excluding potentially hanging PTY tests)..."

# Run all tests except PTY wrapper tests
uv run pytest \
    --timeout=10 \
    --timeout-method=thread \
    -v \
    --tb=short \
    --cov=src/term2ai \
    --cov-report=term-missing \
    --ignore=tests/test_pty_wrapper.py \
    "$@"

echo ""
echo "Note: PTY tests were skipped to avoid hanging."
echo "To run PTY tests separately with timeout:"
echo "  uv run pytest tests/test_pty_wrapper.py --timeout=5 -v"
