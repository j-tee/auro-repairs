#!/bin/bash
# Simple test script for customer profile endpoint

echo "🧪 TESTING CUSTOMER PROFILE ENDPOINT"
echo "=" > /tmp/line.txt && for i in {1..50}; do echo -n "=" >> /tmp/line.txt; done && cat /tmp/line.txt

echo "1. Getting JWT token for alice.cooper@customer.com..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alice.cooper@customer.com", "password": "password123"}')

# Extract access token using python
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "   ✅ Authentication successful"
    echo "   Token: ${TOKEN:0:30}..."
    
    echo ""
    echo "2. Testing customer profile endpoint..."
    PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/auth/customer-profile/)
    
    echo "   Response:"
    echo "$PROFILE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   Raw response: $PROFILE_RESPONSE"
else
    echo "   ❌ Authentication failed"
    echo "   Response: $RESPONSE"
fi