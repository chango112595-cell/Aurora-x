#!/bin/bash

echo "🔒 Testing Aurora-X Chat Security Fixes"
echo "========================================"

API_URL="http://localhost:5000/api/chat"

# Function to test a command
test_command() {
    local message="$1"
    local description="$2"
    
    echo ""
    echo "Testing: $description"
    echo "Input: \"$message\""
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Check if response contains an error
        if echo "$response" | grep -q '"error"'; then
            echo "❌ Error response received"
            echo "$response" | python3 -m json.tool 2>/dev/null | head -5
        else
            # Check if it's using fallback
            if echo "$response" | grep -q '"error_detail"'; then
                echo "⚠️  Fallback implementation used (Aurora-X synthesis failed)"
            else
                echo "✅ Success: Code generated"
            fi
            
            # Extract function name if present
            function_name=$(echo "$response" | grep -o '"function_name":"[^"]*"' | cut -d'"' -f4)
            if [ ! -z "$function_name" ]; then
                echo "   Function: $function_name"
            fi
        fi
    else
        echo "❌ Request failed"
    fi
}

echo ""
echo "📝 TESTING NORMAL COMMANDS (Should Work):"
echo "-----------------------------------------"

test_command "reverse a string" "String reversal"
test_command "calculate factorial" "Factorial calculation"
test_command "check if palindrome" "Palindrome checker"

echo ""
echo "🛡️ TESTING MALICIOUS INPUTS (Should Be Safely Handled):"
echo "-------------------------------------------------------"

test_command "; echo hacked" "Command injection with semicolon"
test_command "\$(rm -rf /)" "Command substitution injection"
test_command "\`cat /etc/passwd\`" "Backtick injection"
test_command "&& ls -la /" "Command chaining with &&"
test_command "|| whoami" "Command chaining with ||"

echo ""
echo "✨ Tests completed!"
echo "==================="
echo ""
echo "Review results to ensure:"
echo "1. Normal commands work (may use fallback if Aurora-X not fully configured)"
echo "2. Malicious inputs don't execute shell commands"
echo "3. Server doesn't crash on any input"