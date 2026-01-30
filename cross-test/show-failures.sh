#!/usr/bin/env bash
#
# Show only failed cross-tests for debugging
#
# Usage:
#   ./show-failures.sh                    # All failures
#   ./show-failures.sh dash               # Only dash.test.js failures
#   ./show-failures.sh --json             # Output as JSON
#

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start bridge if not running
if ! curl -s http://127.0.0.1:9876 > /dev/null 2>&1; then
    echo "Starting Python bridge..."
    uv run python python_bridge.py 9876 &
    BRIDGE_PID=$!
    trap "kill $BRIDGE_PID 2>/dev/null" EXIT
    sleep 2
fi

cd js-adapter

if [[ "$1" == "--json" ]]; then
    # JSON output
    PYTHON_BRIDGE_URL=http://127.0.0.1:9876 npx vitest run --reporter=json 2>/dev/null | \
        jq '[.testResults[].assertionResults[] | select(.status == "failed") | {name: .fullName, expected: .failureMessages[0]}]'
elif [[ -n "$1" ]]; then
    # Filter by test file pattern
    PYTHON_BRIDGE_URL=http://127.0.0.1:9876 npx vitest run "../typopo/tests/**/*$1*.test.js" 2>&1 | \
        grep -E "FAIL|Expected:|Received:" | head -100
else
    # All failures, summarized
    echo "=== Failed Tests Summary ==="
    echo ""
    PYTHON_BRIDGE_URL=http://127.0.0.1:9876 npx vitest run 2>&1 | \
        grep -E "^ (FAIL|✗)" | \
        sed 's/^ //' | \
        sort | uniq -c | sort -rn | head -50
fi
