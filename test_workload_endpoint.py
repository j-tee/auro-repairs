#!/usr/bin/env python3
"""
Test Technician Workload API Endpoint
Tests the specialized /api/shop/technicians/workload/ endpoint
"""

import os
import sys
import django
import requests
import json

# Set up Django environment
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

def test_workload_endpoint():
    """Test the technician workload API endpoint"""
    print("=" * 60)
    print("TECHNICIAN WORKLOAD API ENDPOINT TEST")
    print("=" * 60)
    
    try:
        # Make a request to the workload endpoint
        url = "http://127.0.0.1:8000/api/shop/technicians/workload/"
        response = requests.get(url)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("📋 WORKLOAD API RESPONSE:")
            print("-" * 40)
            print(json.dumps(data, indent=2, default=str))
            
            # Analyze the response structure
            if 'summary' in data and 'technicians' in data:
                print()
                print("🔍 RESPONSE ANALYSIS:")
                print("-" * 40)
                summary = data.get('summary', {})
                technicians = data.get('technicians', [])
                
                print(f"Total technicians: {summary.get('total_technicians', 0)}")
                print(f"Available technicians: {summary.get('available_technicians', 0)}")
                
                if technicians:
                    first_tech = technicians[0]
                    workload = first_tech.get('workload', {})
                    
                    print()
                    print("✅ COMPUTED PROPERTIES FOUND:")
                    for prop in ['current_appointments', 'is_available', 'appointments_today']:
                        if prop in workload:
                            print(f"  {prop}: {workload[prop]}")
                        else:
                            print(f"  ❌ Missing: {prop}")
                else:
                    print("No technicians found in response")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server")
        print("   Make sure Django development server is running:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Error testing workload endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workload_endpoint()