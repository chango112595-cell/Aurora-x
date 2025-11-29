#!/bin/bash
# Aurora-X Test Runner Script
# Runs comprehensive test suite with coverage reporting

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Aurora-X Test Suite${NC}"
echo "======================================"

# Parse arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-true}"

# ============================================
# Python Tests
# ============================================

if [ "$TEST_TYPE" == "all" ] || [ "$TEST_TYPE" == "python" ]; then
    echo -e "\n${BLUE}Running Python Tests...${NC}"
    
    # Check if pytest is installed
    if ! python3 -m pytest --version > /dev/null 2>&1; then
        echo -e "${RED}❌ pytest not installed. Installing test requirements...${NC}"
        pip install -r requirements-test.txt
    fi
    
    # Run pytest with coverage
    if [ "$COVERAGE" == "true" ]; then
        echo -e "${YELLOW}Running with coverage analysis...${NC}"
        python3 -m pytest tests/ -v --cov --cov-report=html --cov-report=term
    else
        echo -e "${YELLOW}Running without coverage...${NC}"
        python3 -m pytest tests/ -v
    fi
    
    PYTHON_EXIT_CODE=$?
    
    if [ $PYTHON_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Python tests passed!${NC}"
    else
        echo -e "${RED}❌ Python tests failed!${NC}"
    fi
fi

# ============================================
# Unit Tests Only
# ============================================

if [ "$TEST_TYPE" == "unit" ]; then
    echo -e "\n${BLUE}Running Unit Tests Only...${NC}"
    python3 -m pytest tests/unit/ -v -m unit
fi

# ============================================
# Integration Tests Only
# ============================================

if [ "$TEST_TYPE" == "integration" ]; then
    echo -e "\n${BLUE}Running Integration Tests...${NC}"
    python3 -m pytest tests/integration/ -v -m integration
fi

# ============================================
# Smoke Tests
# ============================================

if [ "$TEST_TYPE" == "smoke" ]; then
    echo -e "\n${BLUE}Running Smoke Tests...${NC}"
    python3 -m pytest tests/ -v -m smoke --maxfail=1
fi

# ============================================
# Coverage Report
# ============================================

if [ "$COVERAGE" == "true" ] && [ "$TEST_TYPE" != "smoke" ]; then
    echo -e "\n${BLUE}📊 Coverage Report${NC}"
    echo "======================================"
    
    if [ -f "coverage.json" ]; then
        echo -e "${GREEN}Coverage report generated:${NC}"
        echo "  - HTML: htmlcov/index.html"
        echo "  - JSON: coverage.json"
        echo "  - XML: coverage.xml"
        echo ""
        echo -e "${YELLOW}To view HTML report:${NC}"
        echo "  python3 -m http.server -d htmlcov 8080"
        echo "  Then open: http://localhost:8080"
    fi
fi

# ============================================
# Summary
# ============================================

echo ""
echo "======================================"
echo -e "${BLUE}Test Summary${NC}"
echo "======================================"

if [ "$TEST_TYPE" == "all" ]; then
    echo "Test type: All tests"
elif [ "$TEST_TYPE" == "python" ]; then
    echo "Test type: Python tests only"
elif [ "$TEST_TYPE" == "unit" ]; then
    echo "Test type: Unit tests only"
elif [ "$TEST_TYPE" == "integration" ]; then
    echo "Test type: Integration tests"
elif [ "$TEST_TYPE" == "smoke" ]; then
    echo "Test type: Smoke tests"
fi

echo "Coverage: $COVERAGE"
echo ""

# Exit with test result
if [ -n "$PYTHON_EXIT_CODE" ]; then
    exit $PYTHON_EXIT_CODE
fi
