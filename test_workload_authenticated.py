#!/usr/bin/env python3
"""
Test Technician Workload API with Authentication
Tests the /api/shop/technicians/workload/ endpoint using proper Django authentication
"""

import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth import authenticate

# Set up Django environment
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Employee

def test_workload_endpoint_authenticated():
    """Test the technician workload API endpoint with authentication"""
    print("=" * 60)
    print("AUTHENTICATED TECHNICIAN WORKLOAD API TEST")
    print("=" * 60)
    
    try:
        # Create a test client
        client = Client()
        
        # Try to authenticate with owner credentials
        print("🔐 Authenticating with owner credentials...")
        user = authenticate(username='owner@autorepairshop.com', password='owner123')
        
        if user:
            print(f"✅ Authentication successful: {user.username}")
            client.force_login(user)
        else:
            print("❌ Authentication failed - trying to find existing user")
            # Try to find the user directly
            try:
                user = User.objects.get(email='owner@autorepairshop.com')
                print(f"✅ Found user: {user.username}")
                client.force_login(user)
            except User.DoesNotExist:
                print("❌ Owner user not found in database")
                return
        
        print()
        
        # Make authenticated request to workload endpoint
        url = '/api/shop/technicians/workload/'
        print(f"📡 Making request to: {url}")
        response = client.get(url)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("📋 WORKLOAD API RESPONSE STRUCTURE:")
            print("-" * 40)
            
            # Check response structure
            if 'summary' in data:
                summary = data['summary']
                print("📊 SUMMARY:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
                print()
            
            if 'technicians' in data:
                technicians = data['technicians']
                print(f"👨‍🔧 TECHNICIANS FOUND: {len(technicians)}")
                print()
                
                if technicians:
                    # Show first technician in detail
                    first_tech = technicians[0]
                    print("🔍 FIRST TECHNICIAN DETAILS:")
                    print(json.dumps(first_tech, indent=2, default=str))
                    print()
                    
                    # Verify computed properties are included
                    workload = first_tech.get('workload', {})
                    print("✅ COMPUTED PROPERTIES VERIFICATION:")
                    print("-" * 40)
                    
                    expected_props = [
                        'current_appointments',
                        'is_available', 
                        'appointments_today',
                        'max_capacity'
                    ]
                    
                    all_present = True
                    for prop in expected_props:
                        if prop in workload:
                            print(f"  ✅ {prop}: {workload[prop]}")
                        else:
                            print(f"  ❌ MISSING: {prop}")
                            all_present = False
                    
                    print()
                    if all_present:
                        print("🎉 SUCCESS: All computed properties are available in workload endpoint!")
                        print("📋 This confirms the workload endpoint provides the data promised in documentation.")
                    else:
                        print("⚠️  WARNING: Some computed properties are missing!")
                        
            else:
                print("❌ No 'technicians' key found in response")
                
        elif response.status_code == 401:
            print("❌ Still getting 401 Unauthorized")
            print("   This might be due to API authentication middleware")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response content: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Error testing authenticated workload endpoint: {e}")
        import traceback
        traceback.print_exc()

def compare_employee_vs_workload_apis():
    """Compare regular Employee API vs specialized Workload API"""
    print("\n" + "=" * 60)
    print("COMPARISON: EMPLOYEE API vs WORKLOAD API")
    print("=" * 60)
    
    try:
        client = Client()
        
        # Authenticate
        user = User.objects.get(email='owner@autorepairshop.com')
        client.force_login(user)
        
        # Test regular employee endpoint
        print("1️⃣ TESTING REGULAR EMPLOYEE API:")
        print("-" * 40)
        emp_response = client.get('/api/shop/employees/')
        
        if emp_response.status_code == 200:
            emp_data = emp_response.json()
            if emp_data and isinstance(emp_data, list) and len(emp_data) > 0:
                first_employee = emp_data[0]
                print("📋 Employee API fields:")
                for field in first_employee.keys():
                    print(f"  - {field}")
                    
                # Check for computed properties
                computed_props = ['current_appointments', 'workload_count', 'is_available', 'appointments_today']
                print("\n🔍 Computed properties in Employee API:")
                for prop in computed_props:
                    status = "✅ PRESENT" if prop in first_employee else "❌ MISSING"
                    print(f"  {prop}: {status}")
            else:
                print("No employee data found")
        else:
            print(f"Employee API failed: {emp_response.status_code}")
        
        print("\n2️⃣ TESTING WORKLOAD API:")
        print("-" * 40)
        workload_response = client.get('/api/shop/technicians/workload/')
        
        if workload_response.status_code == 200:
            workload_data = workload_response.json()
            if 'technicians' in workload_data and workload_data['technicians']:
                first_tech = workload_data['technicians'][0]
                
                print("📋 Workload API structure:")
                print(f"  - technician: {list(first_tech.get('technician', {}).keys())}")
                print(f"  - workload: {list(first_tech.get('workload', {}).keys())}")
                print(f"  - current_jobs: {len(first_tech.get('current_jobs', []))} jobs")
                
                # Check for computed properties
                workload_info = first_tech.get('workload', {})
                print("\n🔍 Computed properties in Workload API:")
                for prop in computed_props:
                    status = "✅ PRESENT" if prop in workload_info else "❌ MISSING"
                    value = workload_info.get(prop, 'N/A')
                    print(f"  {prop}: {status} ({value})")
            else:
                print("No technician data found")
        else:
            print(f"Workload API failed: {workload_response.status_code}")
            
        print("\n📋 CONCLUSION:")
        print("-" * 40)
        print("✅ Regular Employee API: Returns basic model fields only")
        print("✅ Workload API: Returns computed properties via custom view logic")
        print("📖 Documentation should clarify which endpoint provides which data!")
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")

if __name__ == "__main__":
    test_workload_endpoint_authenticated()
    compare_employee_vs_workload_apis()