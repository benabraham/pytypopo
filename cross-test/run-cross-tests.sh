#!/bin/bash
#
# Run upstream typopo JS tests against pytypopo Python port
#
# This script:
# 1. Starts the Python HTTP bridge server
# 2. Runs the JS test suite (which calls Python via HTTP)
# 3. Reports results and cleans up
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  pytypopo Cross-Test Suite                 ║${NC}"
echo -e "${YELLOW}║  Testing Python port against JS tests      ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check dependencies
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv not found. Please install uv first.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm not found. Please install Node.js first.${NC}"
    exit 1
fi

# Install JS dependencies if needed
if [ ! -d "js-adapter/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing JS dependencies...${NC}"
    cd js-adapter
    npm install
    cd ..
fi

# Start Python bridge in background
echo -e "${YELLOW}🐍 Starting Python bridge server...${NC}"
cd "$PROJECT_ROOT"
uv run python cross-test/python_bridge.py 9876 &
PYTHON_PID=$!
cd "$SCRIPT_DIR"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if kill -0 $PYTHON_PID 2>/dev/null; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Wait for server to be ready
echo -e "${YELLOW}⏳ Waiting for Python bridge to start...${NC}"
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:9876 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Python bridge is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Python bridge failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Run JS tests
echo -e "\n${YELLOW}🧪 Running upstream typopo tests against pytypopo...${NC}"
echo ""

cd js-adapter
if npm test; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ All cross-tests passed!                 ║${NC}"
    echo -e "${GREEN}║  Python port matches JS behavior           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ Some tests failed                       ║${NC}"
    echo -e "${RED}║  Check output above for details            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
    exit 1
fi
