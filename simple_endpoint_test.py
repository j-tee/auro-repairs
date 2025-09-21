#!/usr/bin/env python3
"""
Simple API Test Script
Test the documented endpoints with correct URL patterns
"""

import requests
import json
import time

# Base URL for the Django server
BASE_URL = "http://localhost:8001"

def test_endpoint(url, description):
    """Test a single endpoint and return result"""
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ {description}")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   Response: Array with {len(data)} items")
                    if len(data) > 0:
                        print(f"   Sample: {str(data[0])[:100]}...")
                elif isinstance(data, dict):
                    print(f"   Response: {str(data)[:100]}...")
                else:
                    print(f"   Response: {str(data)[:100]}...")
            except json.JSONDecodeError:
                print(f"   Response: Non-JSON content")
        else:
            print(f"   Error: {response.text[:200]}...")
            
        print()
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}")
        print(f"   URL: {url}")
        print(f"   Error: Connection refused - Server not running")
        print()
        return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   URL: {url}")  
        print(f"   Error: {str(e)}")
        print()
        return False

def main():
    print("🧪 TESTING DOCUMENTED API ENDPOINTS")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    endpoints_to_test = [
        # Core endpoints from documentation
        (f"{BASE_URL}/api/shop/employees/", "Get all employees"),
        (f"{BASE_URL}/api/shop/employees/?role=technician", "Get technicians only"),
        (f"{BASE_URL}/api/shop/technicians/workload/", "Get technician workload"),
        (f"{BASE_URL}/api/shop/appointments/", "Get all appointments"),
        (f"{BASE_URL}/api/shop/vehicles/", "Get all vehicles"),
        (f"{BASE_URL}/api/shop/customers/", "Get all customers"),
        (f"{BASE_URL}/api/shop/repair-orders/", "Get repair orders"),
        (f"{BASE_URL}/api/shop/services/", "Get services"),
        (f"{BASE_URL}/api/shop/parts/", "Get parts"),
        (f"{BASE_URL}/api/shop/shops/", "Get shops"),
        (f"{BASE_URL}/api/shop/vehicle-problems/", "Get vehicle problems"),
        (f"{BASE_URL}/api/shop/search/?q=test", "Global search"),
        (f"{BASE_URL}/api/shop/shops/stats/", "Shop statistics"),
        (f"{BASE_URL}/api/shop/technicians/available/", "Available technicians"),
        
        # Authentication endpoints (might need authentication)
        (f"{BASE_URL}/api/auth/user/", "Get user profile"),
        (f"{BASE_URL}/api/admin/users/stats/", "Admin user stats"),
    ]
    
    passed = 0
    total = len(endpoints_to_test)
    
    for url, description in endpoints_to_test:
        if test_endpoint(url, description):
            passed += 1
    
    print("=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed >= total * 0.8:
        print("🎉 Excellent! Most endpoints are working.")
    elif passed >= total * 0.5:
        print("⚠️  Good progress, some issues to address.")
    else:
        print("❌ Many endpoints not working. Check server and database.")

if __name__ == "__main__":
    main()