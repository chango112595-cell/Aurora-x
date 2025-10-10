#!/bin/bash

echo "🔒 Testing Specific Injection Vulnerabilities"
echo "============================================="

API_URL="http://localhost:5000/api/chat"

# Function to test a command
test_injection() {
    local message="$1"
    local description="$2"
    
    echo ""
    echo "Testing: $description"
    echo "Input: \"$message\""
    
    # Send the request
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}" 2>/dev/null)
    
    # Check if the command executed by looking for specific patterns
    if echo "$response" | grep -q "root:x:0:0"; then
        echo "❌ VULNERABILITY DETECTED: /etc/passwd content exposed!"
        return 1
    elif echo "$response" | grep -q "bin/bash"; then
        echo "❌ VULNERABILITY DETECTED: Shell execution detected!"
        return 1
    elif echo "$response" | grep -q "runner"; then
        echo "❌ VULNERABILITY DETECTED: Username exposed!"
        return 1
    elif echo "$response" | grep -q "hacked"; then
        echo "❌ VULNERABILITY DETECTED: Command injection succeeded!"
        return 1
    else
        echo "✅ SAFE: Input sanitized, no injection detected"
        
        # Check if it generated code or used fallback
        if echo "$response" | grep -q '"error_detail"'; then
            echo "   Used fallback implementation"
        elif echo "$response" | grep -q '"code"'; then
            echo "   Generated code successfully"
        fi
    fi
}

echo ""
echo "🛡️ Testing Critical Injection Attempts:"
echo "----------------------------------------"

test_injection "\`cat /etc/passwd\`" "Backtick command substitution"
test_injection "\$(cat /etc/passwd)" "Dollar command substitution"
test_injection "; cat /etc/passwd" "Semicolon command injection"
test_injection "&& cat /etc/passwd" "AND command chaining"
test_injection "|| cat /etc/passwd" "OR command chaining"
test_injection "| cat /etc/passwd" "Pipe command"
test_injection "\$(whoami)" "Whoami command substitution"
test_injection "\`whoami\`" "Whoami backtick substitution"
test_injection "; echo 'hacked' > /tmp/pwned.txt" "File write attempt"
test_injection "\$PATH" "Environment variable access"

echo ""
echo "📝 Testing Normal Commands Still Work:"
echo "--------------------------------------"

# Test a normal command to ensure functionality isn't broken
response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d '{"message": "reverse a string"}' 2>/dev/null)

if echo "$response" | grep -q '"code"'; then
    echo "✅ Normal command works: reverse a string"
else
    echo "❌ Normal command failed"
fi

echo ""
echo "✨ Security test completed!"
echo "==========================="
echo ""
echo "Summary:"
echo "- All injection attempts should show SAFE"
echo "- Normal commands should still work"