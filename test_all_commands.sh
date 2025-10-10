#!/bin/bash

echo "🔧 Testing All Supported Aurora-X Commands"
echo "=========================================="

API_URL="http://localhost:5000/api/chat"
SUCCESS_COUNT=0
TOTAL_COUNT=0

# Function to test a command
test_command() {
    local message="$1"
    local expected_func="$2"
    
    TOTAL_COUNT=$((TOTAL_COUNT + 1))
    echo ""
    echo "[$TOTAL_COUNT] Testing: \"$message\""
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # Check if response contains code
        if echo "$response" | grep -q '"code"'; then
            # Extract function name
            function_name=$(echo "$response" | grep -o '"function_name":"[^"]*"' | cut -d'"' -f4)
            
            # Check if it's using fallback
            if echo "$response" | grep -q '"error_detail"'; then
                echo "   ⚠️  Fallback used (Aurora-X synthesis failed)"
                echo "   Expected: $expected_func"
            else
                echo "   ✅ Success! Generated: $function_name"
                if [ ! -z "$expected_func" ] && [ "$function_name" != "$expected_func" ]; then
                    echo "   Note: Expected '$expected_func' but got '$function_name'"
                fi
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            fi
        else
            echo "   ❌ Failed - No code generated"
            echo "$response" | python3 -m json.tool 2>/dev/null | head -3
        fi
    else
        echo "   ❌ Request failed"
    fi
}

echo ""
echo "📝 Testing Core Commands:"
echo "-------------------------"

# Test basic string operations
test_command "reverse a string" "reverse_string"
test_command "reverse the text hello" "reverse_string"

# Test math operations
test_command "calculate factorial" "factorial"
test_command "factorial of 5" "factorial"
test_command "add two numbers" "add_two_numbers"
test_command "sum of two integers" "add_two_numbers"
test_command "find the greatest common divisor" "gcd"
test_command "calculate fibonacci" "fibonacci"
test_command "sum of squares" "sum_of_squares"

# Test string analysis
test_command "check if palindrome" "is_palindrome"
test_command "check palindrome" "check_palindrome"
test_command "count vowels in a string" "count_vowels"

# Test list operations
test_command "find maximum in list" "max_in_list"
test_command "largest number in array" "find_largest"
test_command "sort a list" "sort_list"
test_command "sort array of numbers" "sort_list"

# Test number checks
test_command "check if prime" "is_prime"
test_command "is 17 a prime number" "is_prime"

echo ""
echo "📊 Testing Complex Requests:"
echo "-----------------------------"

# Test more natural language requests
test_command "I need a function to reverse text" "reverse_string"
test_command "write code to calculate the factorial of a number" "factorial"
test_command "can you create a palindrome checker" "check_palindrome"
test_command "generate a function that adds two numbers together" "add_two_numbers"
test_command "make a program to find the largest element" "find_largest"

echo ""
echo "🔍 Testing Edge Cases:"
echo "----------------------"

# Test ambiguous or unusual requests
test_command "string backwards" "reverse_string"
test_command "flip text" "reverse_string"
test_command "math factorial" "factorial"
test_command "prime checker" "is_prime"

echo ""
echo "=========================================="
echo "✨ Test Results:"
echo "=========================================="
echo "Successful generations: $SUCCESS_COUNT / $TOTAL_COUNT"
echo ""

if [ $SUCCESS_COUNT -lt 10 ]; then
    echo "⚠️  WARNING: Less than 10 commands worked successfully!"
    echo "This might indicate that functionality is broken."
else
    echo "✅ SUCCESS: At least 10+ commands are working!"
fi

echo ""
echo "Note: Some commands may use fallback implementations"
echo "if Aurora-X synthesis engine is not fully configured."