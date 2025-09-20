#!/usr/bin/env python3
"""
Direct API Test - Test endpoints using Django management command approach
"""

import os
import sys
import django
from django.conf import settings

# Add the project path
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')

# Setup Django
django.setup()

# Now import Django models and test the views directly
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
import json

def test_django_endpoints():
    """Test endpoints using Django test client"""
    print("🧪 TESTING DJANGO API ENDPOINTS")
    print("=" * 50)
    
    client = Client()
    
    endpoints_to_test = [
        # Shop endpoints that should work without authentication
        ('/api/shop/employees/', 'GET', 'Get all employees'),
        ('/api/shop/technicians/workload/', 'GET', 'Get technician workload'),
        ('/api/shop/appointments/', 'GET', 'Get all appointments'),
        ('/api/shop/vehicles/', 'GET', 'Get all vehicles'),
        ('/api/shop/customers/', 'GET', 'Get all customers'),
        ('/api/shop/repair-orders/', 'GET', 'Get repair orders'),
        ('/api/shop/services/', 'GET', 'Get services'),
        ('/api/shop/parts/', 'GET', 'Get parts'),
        ('/api/shop/shops/', 'GET', 'Get shops'),
        ('/api/shop/vehicle-problems/', 'GET', 'Get vehicle problems'),
        ('/api/shop/search/?q=test', 'GET', 'Global search'),
        ('/api/shop/technicians/available/', 'GET', 'Available technicians'),
    ]
    
    passed = 0
    total = len(endpoints_to_test)
    
    for url, method, description in endpoints_to_test:
        try:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, content_type='application/json')
            else:
                continue
                
            print(f"✅ {description}")
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Response: Array with {len(data)} items")
                        if len(data) > 0:
                            print(f"   Sample: {str(data[0])[:150]}...")
                    elif isinstance(data, dict):
                        keys = list(data.keys())[:5]  # First 5 keys
                        print(f"   Response: Dict with keys: {keys}")
                        print(f"   Sample: {str(data)[:150]}...")
                    else:
                        print(f"   Response: {str(data)[:100]}...")
                except Exception as e:
                    print(f"   Response: {response.content[:100]}...")
                passed += 1
            else:
                print(f"   Error: {response.content[:200]}...")
                
        except Exception as e:
            print(f"❌ {description}")
            print(f"   URL: {url}")
            print(f"   Error: {str(e)}")
            
        print()
    
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
    
    return passed, total

def check_database_content():
    """Check if database has test data"""
    print("\n🔍 CHECKING DATABASE CONTENT")
    print("=" * 50)
    
    try:
        from shop.models import Employee, Appointment, Vehicle, Customer, Shop
        
        print(f"Shops: {Shop.objects.count()}")
        print(f"Employees: {Employee.objects.count()}")
        print(f"Customers: {Customer.objects.count()}")
        print(f"Vehicles: {Vehicle.objects.count()}")
        print(f"Appointments: {Appointment.objects.count()}")
        
        # Show technicians specifically
        technicians = Employee.objects.filter(role='technician')
        print(f"Technicians: {technicians.count()}")
        
        if technicians.count() > 0:
            print("\nTechnician Details:")
            for tech in technicians[:3]:  # First 3 technicians
                print(f"  - {tech.name} (ID: {tech.id})")
                print(f"    Workload: {tech.workload_count}")
                print(f"    Available: {tech.is_available}")
                
    except Exception as e:
        print(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    check_database_content()
    passed, total = test_django_endpoints()
    
    print(f"\n📝 DOCUMENTATION VERIFICATION")
    print("=" * 50)
    
    if passed >= total * 0.8:
        print("✅ Documentation appears accurate - most endpoints working")
    elif passed >= total * 0.5:
        print("⚠️  Documentation mostly accurate - some endpoints need fixes")
    else:
        print("❌ Documentation may need updates - several endpoints not working")