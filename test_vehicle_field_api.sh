#!/bin/bash

# Vehicle Field Naming Consistency Test
# Tests the new vehicle_id field and backward compatibility with vehicle field

echo "🚀 Vehicle Field Naming Consistency Test"
echo "=" | tr " " "=" | head -c 50; echo
echo "Testing backward compatible vehicle → vehicle_id transition"
echo "=" | tr " " "=" | head -c 50; echo

# Configuration
BASE_URL="http://127.0.0.1:8000/api"
SHOP_URL="$BASE_URL/shop"

# Function to get auth token
get_auth_token() {
    echo "🔐 Getting authentication token..."
    
    # Try to get token for existing employee user
    RESPONSE=$(curl -s -X POST "$BASE_URL/token/" \
        -H "Content-Type: application/json" \
        -d '{"username": "john.mechanic@autorepair.com", "email": "john.mechanic@autorepair.com", "password": "testpass123"}')
    
    if echo "$RESPONSE" | grep -q "access"; then
        TOKEN=$(echo "$RESPONSE" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
        echo "   ✅ Token obtained successfully"
        echo "$TOKEN"
    else
        echo "   ❌ Failed to get token. Response: $RESPONSE"
        echo "   ℹ️  Make sure the Django server is running and user credentials are correct"
        exit 1
    fi
}

# Function to get a vehicle ID for testing
get_test_vehicle_id() {
    local token=$1
    echo "🚗 Getting test vehicle ID..."
    
    RESPONSE=$(curl -s -X GET "$SHOP_URL/vehicles/" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        VEHICLE_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   ✅ Found vehicle ID: $VEHICLE_ID"
        echo "$VEHICLE_ID"
    else
        echo "   ❌ No vehicles found. Response: $RESPONSE"
        echo "   ℹ️  Make sure you have test vehicles in the database"
        exit 1
    fi
}

# Function to test repair order creation with vehicle_id field
test_vehicle_id_field() {
    local token=$1
    local vehicle_id=$2
    
    echo "📝 Test 1: Creating repair order with vehicle_id (new preferred field)"
    
    RESPONSE=$(curl -s -X POST "$SHOP_URL/repair-orders/" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"vehicle_id\": $vehicle_id,
            \"notes\": \"Test repair order created with vehicle_id field\",
            \"discount_amount\": \"0.00\"
        }")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "   ✅ SUCCESS: Repair order created with vehicle_id"
        ORDER_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   📄 Created repair order ID: $ORDER_ID"
        echo "   📄 Response preview:"
        echo "$RESPONSE" | head -c 200
        echo "..."
        return 0
    else
        echo "   ❌ FAILED: Could not create repair order with vehicle_id"
        echo "   📄 Response: $RESPONSE"
        return 1
    fi
}

# Function to test repair order creation with legacy vehicle field
test_vehicle_field() {
    local token=$1
    local vehicle_id=$2
    
    echo "📝 Test 2: Creating repair order with vehicle (legacy deprecated field)"
    
    RESPONSE=$(curl -s -X POST "$SHOP_URL/repair-orders/" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"vehicle\": $vehicle_id,
            \"notes\": \"Test repair order created with legacy vehicle field\",
            \"discount_amount\": \"0.00\"
        }")
    
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "   ✅ SUCCESS: Repair order created with legacy vehicle field (backward compatibility)"
        ORDER_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   📄 Created repair order ID: $ORDER_ID"
        echo "   📄 Response preview:"
        echo "$RESPONSE" | head -c 200
        echo "..."
        return 0
    else
        echo "   ❌ FAILED: Could not create repair order with legacy vehicle field"
        echo "   📄 Response: $RESPONSE"
        return 1
    fi
}

# Function to test error when both fields provided
test_both_fields_error() {
    local token=$1
    local vehicle_id=$2
    
    echo "📝 Test 3: Error handling when both vehicle and vehicle_id provided"
    
    RESPONSE=$(curl -s -X POST "$SHOP_URL/repair-orders/" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"vehicle_id\": $vehicle_id,
            \"vehicle\": $vehicle_id,
            \"notes\": \"This should fail\",
            \"discount_amount\": \"0.00\"
        }")
    
    if echo "$RESPONSE" | grep -q "error\|Provide either"; then
        echo "   ✅ SUCCESS: Correctly rejected request with both fields"
        echo "   📄 Error message: $RESPONSE"
        return 0
    else
        echo "   ❌ FAILED: Should have returned an error"
        echo "   📄 Response: $RESPONSE"
        return 1
    fi
}

# Function to test error when no vehicle field provided
test_no_field_error() {
    local token=$1
    
    echo "📝 Test 4: Error handling when no vehicle field provided"
    
    RESPONSE=$(curl -s -X POST "$SHOP_URL/repair-orders/" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"notes\": \"This should fail - no vehicle specified\",
            \"discount_amount\": \"0.00\"
        }")
    
    if echo "$RESPONSE" | grep -q "error\|required"; then
        echo "   ✅ SUCCESS: Correctly rejected request with no vehicle field"
        echo "   📄 Error message: $RESPONSE"
        return 0
    else
        echo "   ❌ FAILED: Should have returned an error"
        echo "   📄 Response: $RESPONSE"
        return 1
    fi
}

# Function to test filtering consistency
test_filtering_consistency() {
    local token=$1
    local vehicle_id=$2
    
    echo "📝 Test 5: Testing vehicle_id filtering consistency"
    
    RESPONSE=$(curl -s -X GET "$SHOP_URL/repair-orders/?vehicle_id=$vehicle_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json")
    
    if echo "$RESPONSE" | grep -q '\['; then
        COUNT=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | wc -l)
        echo "   ✅ SUCCESS: Found $COUNT repair orders for vehicle_id=$vehicle_id"
        echo "   📄 Filter URL: GET $SHOP_URL/repair-orders/?vehicle_id=$vehicle_id"
        return 0
    else
        echo "   ❌ FAILED: Could not filter by vehicle_id"
        echo "   📄 Response: $RESPONSE"
        return 1
    fi
}

# Main test execution
main() {
    echo "🔄 Starting tests..."
    
    # Get authentication token
    TOKEN=$(get_auth_token)
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # Get test vehicle ID
    VEHICLE_ID=$(get_test_vehicle_id "$TOKEN")
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    echo
    echo "🧪 Running API Tests..."
    
    # Run all tests
    TESTS_PASSED=0
    TOTAL_TESTS=5
    
    # Test 1: vehicle_id field
    test_vehicle_id_field "$TOKEN" "$VEHICLE_ID"
    if [ $? -eq 0 ]; then ((TESTS_PASSED++)); fi
    echo
    
    # Test 2: legacy vehicle field
    test_vehicle_field "$TOKEN" "$VEHICLE_ID"
    if [ $? -eq 0 ]; then ((TESTS_PASSED++)); fi
    echo
    
    # Test 3: both fields error
    test_both_fields_error "$TOKEN" "$VEHICLE_ID"
    if [ $? -eq 0 ]; then ((TESTS_PASSED++)); fi
    echo
    
    # Test 4: no field error
    test_no_field_error "$TOKEN"
    if [ $? -eq 0 ]; then ((TESTS_PASSED++)); fi
    echo
    
    # Test 5: filtering consistency
    test_filtering_consistency "$TOKEN" "$VEHICLE_ID"
    if [ $? -eq 0 ]; then ((TESTS_PASSED++)); fi
    echo
    
    # Results summary
    echo "=" | tr " " "=" | head -c 50; echo
    echo "📊 Test Results: $TESTS_PASSED/$TOTAL_TESTS tests passed"
    
    if [ $TESTS_PASSED -eq $TOTAL_TESTS ]; then
        echo "🎉 ALL TESTS PASSED!"
        echo "✅ vehicle_id field works correctly (new preferred)"
        echo "✅ vehicle field works correctly (legacy/deprecated)"
        echo "✅ Error handling works for invalid combinations"
        echo "✅ API consistency maintained across endpoints"
        echo "🚀 Ready for frontend team integration!"
        echo "=" | tr " " "=" | head -c 50; echo
        exit 0
    else
        echo "❌ Some tests failed. Please check the implementation."
        echo "=" | tr " " "=" | head -c 50; echo
        exit 1
    fi
}

# Check if Django server is running
echo "🔍 Checking if Django server is running..."
if curl -s "$BASE_URL/token/" > /dev/null; then
    echo "   ✅ Django server is running"
else
    echo "   ❌ Django server is not running or not accessible"
    echo "   ℹ️  Please start the Django server with: python manage.py runserver"
    exit 1
fi

# Run the main test function
main
