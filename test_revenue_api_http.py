#!/usr/bin/env python3
"""
Revenue Today API HTTP Testing Script
Direct HTTP testing for frontend integration verification
"""
import requests
import json
from datetime import date

class HTTPRevenueTest:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.today = "2025-09-08"
        self.token = None
        
    def get_auth_token(self):
        """Get authentication token"""
        print("🔐 Getting authentication token...")
        
        # Try to get token with test credentials
        login_data = {
            "email": "admin@example.com",  # Adjust as needed
            "password": "admin123"         # Adjust as needed
        }
        
        try:
            response = requests.post(f'{self.base_url}/api/token/', json=login_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('access')
                print(f"✅ Authentication successful: {self.token[:20] if self.token else 'No token'}...")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try alternative endpoints
                print("🔄 Trying alternative login endpoint...")
                response = requests.post(f'{self.base_url}/api/auth/login/', json=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    self.token = token_data.get('access') or token_data.get('token')
                    print(f"✅ Alternative auth successful: {self.token[:20] if self.token else 'No token'}...")
                    return True
                    
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is the Django server running?")
            print("   Please run: python manage.py runserver")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_revenue_endpoint(self):
        """Test the revenue endpoint that frontend uses"""
        print(f"\n🧪 Testing Revenue Today endpoint for {self.today}...")
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        # Test the exact endpoint frontend uses
        url = f'{self.base_url}/api/shop/repair-orders/'
        params = {
            'status': 'completed',
            'completed_date_after': self.today,
            'completed_date_before': self.today,
            'limit': 100
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            print(f"📡 Request: GET {url}")
            print(f"📋 Params: {params}")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Request successful")
                print(f"📦 Response structure: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                
                # Parse response (handle different formats)
                orders = []
                if isinstance(data, list):
                    orders = data
                elif 'results' in data:
                    orders = data['results']
                elif 'repair_orders' in data:
                    orders = data['repair_orders']
                
                print(f"📦 Found {len(orders)} completed orders for today")
                
                # Calculate revenue
                total_revenue = 0
                for order in orders:
                    order_total = order.get('total_cost', 0) or order.get('total', 0)
                    total_revenue += float(order_total) if order_total else 0
                    print(f"   Order {order.get('id')}: ${order_total}")
                
                print(f"💰 Total Revenue Today: ${total_revenue:.2f}")
                return total_revenue, orders
                
            elif response.status_code == 401:
                print(f"❌ Authentication required")
                print(f"   Response: {response.text}")
                return None, None
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None, None
    
    def test_all_orders_endpoint(self):
        """Test getting all repair orders"""
        print(f"\n🔍 Testing all repair orders endpoint...")
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        url = f'{self.base_url}/api/shop/repair-orders/'
        params = {'limit': 10}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                orders = []
                if isinstance(data, list):
                    orders = data
                elif 'results' in data:
                    orders = data['results']
                
                print(f"📦 Found {len(orders)} total orders")
                
                # Show sample orders
                for order in orders[:3]:
                    print(f"   Order {order.get('id')}: ${order.get('total_cost', 0)} - Status: {order.get('status', 'N/A')}")
                
                return orders
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def test_without_auth(self):
        """Test endpoints without authentication to see error response"""
        print(f"\n🔓 Testing endpoints without authentication...")
        
        url = f'{self.base_url}/api/shop/repair-orders/'
        
        try:
            response = requests.get(url)
            print(f"📊 Status (no auth): {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
            if response.status_code == 401:
                print("✅ Authentication is properly required")
            elif response.status_code == 200:
                print("⚠️  Warning: Endpoint accessible without authentication")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_http_tests(self):
        """Run all HTTP tests"""
        print("🌐 Starting HTTP Revenue Today API Tests")
        print("=" * 50)
        
        # Test without auth first
        self.test_without_auth()
        
        # Try to get auth token
        auth_success = self.get_auth_token()
        
        # Test revenue endpoint
        revenue, orders = self.test_revenue_endpoint()
        
        # Test all orders
        all_orders = self.test_all_orders_endpoint()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 HTTP TEST RESULTS SUMMARY")
        print("=" * 50)
        
        print(f"🔐 Authentication: {'✅ Success' if auth_success else '❌ Failed'}")
        print(f"🧪 Revenue endpoint: {'✅ Working' if revenue is not None else '❌ Failed'}")
        print(f"📊 All orders endpoint: {'✅ Working' if all_orders else '❌ Failed'}")
        
        if revenue is not None:
            print(f"💰 Revenue Today: ${revenue:.2f}")
            if revenue > 0:
                print("✅ Frontend should display actual revenue amount")
            else:
                print("🟡 Frontend should display $0.00 (correct if no completed orders today)")
        else:
            print("❌ Revenue calculation failed - check authentication or API implementation")
        
        print(f"\n🎯 FRONTEND INTEGRATION STATUS:")
        if auth_success and revenue is not None:
            print("✅ API is accessible and working")
            print("✅ Frontend can integrate successfully")
            print(f"✅ Expected frontend display: Revenue Today: ${revenue:.2f}")
        else:
            print("❌ API integration issues found")
            print("🔧 Backend fixes required before frontend integration")

if __name__ == "__main__":
    test = HTTPRevenueTest()
    test.run_http_tests()
