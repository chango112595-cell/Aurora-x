#!/bin/bash
# Run tests from all Aurora-X spec compilation runs

echo "🧪 Aurora-X Test Runner"
echo "========================"

TOTAL_RUNS=0
TOTAL_TESTS=0
FAILED_RUNS=0

# Find all run directories
for RUN_DIR in runs/run-*/; do
    if [[ -d "$RUN_DIR" && -d "${RUN_DIR}tests" ]]; then
        RUN_NAME=$(basename "$RUN_DIR")
        echo ""
        echo "📁 Testing: $RUN_NAME"
        echo "------------------------"
        
        # Run tests with PYTHONPATH set
        cd "$RUN_DIR"
        if PYTHONPATH=$PWD python -m unittest discover -s tests 2>&1; then
            echo "✅ Tests passed for $RUN_NAME"
            # Count tests
            TEST_COUNT=$(python -m unittest discover -s tests 2>&1 | grep -oE "Ran [0-9]+ test" | grep -oE "[0-9]+")
            if [[ -n "$TEST_COUNT" ]]; then
                TOTAL_TESTS=$((TOTAL_TESTS + TEST_COUNT))
            fi
        else
            echo "❌ Tests failed for $RUN_NAME"
            FAILED_RUNS=$((FAILED_RUNS + 1))
        fi
        
        TOTAL_RUNS=$((TOTAL_RUNS + 1))
        cd - > /dev/null
    fi
done

echo ""
echo "========================"
echo "📊 Summary:"
echo "  Total runs tested: $TOTAL_RUNS"
echo "  Total tests executed: $TOTAL_TESTS"
if [[ $FAILED_RUNS -eq 0 ]]; then
    echo "  ✅ All runs passed!"
else
    echo "  ❌ Failed runs: $FAILED_RUNS"
    exit 1
fi