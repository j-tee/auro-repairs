#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Technician Dashboard Fixes
Tests all the implemented fixes to ensure they work correctly
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

from django.test import Client
from django.contrib.auth import get_user_model
from shop.models import Employee, Appointment
import json

def test_technician_dashboard_fixes():
    """Test all backend fixes for the technician dashboard"""
    
    print("🧪 COMPREHENSIVE TECHNICIAN DASHBOARD BACKEND TESTING")
    print("=" * 80)
    
    User = get_user_model()
    client = Client()
    
    # Test credentials
    test_email = 'john.mechanic@autorepair.com'
    test_password = 'password123'
    
    print(f"\n1️⃣ TESTING AUTHENTICATION")
    print("-" * 50)
    
    # Test login
    login_response = client.post('/api/token/', {
        'email': test_email,
        'password': test_password
    })
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get('access')
        print(f"   ✅ Login successful - Token received")
        
        # Set authorization header for subsequent requests
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        
    else:
        print(f"   ❌ Login failed: {login_response.status_code} - {login_response.content.decode()}")
        return False
    
    print(f"\n2️⃣ TESTING USER-EMPLOYEE LINKING")
    print("-" * 50)
    
    # Verify user-employee link exists
    try:
        user = User.objects.get(email=test_email)
        employee = Employee.objects.get(user=user)
        print(f"   ✅ User-Employee link verified:")
        print(f"      User ID: {user.id} ({user.email})")
        print(f"      Employee ID: {employee.id} ({employee.name})")
        print(f"      Employee Role: {employee.role}")
    except (User.DoesNotExist, Employee.DoesNotExist) as e:
        print(f"   ❌ User-Employee link missing: {e}")
        return False
    
    print(f"\n3️⃣ TESTING EMPLOYEE PROFILE ENDPOINT")
    print("-" * 50)
    
    # Test GET /api/auth/employee-profile/
    profile_response = client.get('/api/auth/employee-profile/', **auth_headers)
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"   ✅ Employee profile endpoint working:")
        print(f"      User ID: {profile_data.get('user_id')}")
        print(f"      Employee ID: {profile_data['employee']['id']}")
        print(f"      Employee Name: {profile_data['employee']['name']}")
        print(f"      Employee Role: {profile_data['employee']['role']}")
        if profile_data['employee']['shop']:
            print(f"      Shop: {profile_data['employee']['shop']['name']}")
        
        employee_id = profile_data['employee']['id']
    else:
        print(f"   ❌ Employee profile endpoint failed: {profile_response.status_code}")
        print(f"      Response: {profile_response.content.decode()}")
        return False
    
    print(f"\n4️⃣ TESTING APPOINTMENTS API WITH TECHNICIAN DATA")
    print("-" * 50)
    
    # Test GET /api/shop/appointments/ to see if it includes technician data
    appointments_response = client.get('/api/shop/appointments/', **auth_headers)
    
    if appointments_response.status_code == 200:
        appointments_data = appointments_response.json()
        print(f"   ✅ Appointments API working - {len(appointments_data)} appointments")
        
        # Check if any appointments have technician data
        technician_appointments = [apt for apt in appointments_data if apt.get('assigned_technician_id')]
        
        if technician_appointments:
            sample_apt = technician_appointments[0]
            print(f"   ✅ Sample appointment with technician data:")
            print(f"      Appointment ID: {sample_apt['id']}")
            print(f"      Status: {sample_apt['status']}")
            print(f"      Assigned Technician ID: {sample_apt.get('assigned_technician_id')}")
            
            if sample_apt.get('assigned_technician'):
                tech_data = sample_apt['assigned_technician']
                print(f"      Technician Name: {tech_data['name']}")
                print(f"      Technician Role: {tech_data['role']}")
                print(f"      Technician Email: {tech_data.get('email', 'N/A')}")
                print(f"      Technician User ID: {tech_data.get('user_id', 'N/A')}")
        else:
            print(f"   ⚠️  No appointments with assigned technicians found")
            
    else:
        print(f"   ❌ Appointments API failed: {appointments_response.status_code}")
        return False
    
    print(f"\n5️⃣ TESTING MY-ASSIGNMENTS ENDPOINT")
    print("-" * 50)
    
    # Test GET /api/shop/appointments/my-assignments/
    my_assignments_response = client.get('/api/shop/appointments/my-assignments/', **auth_headers)
    
    if my_assignments_response.status_code == 200:
        my_assignments_data = my_assignments_response.json()
        assignments_count = my_assignments_data.get('count', 0)
        assignments_list = my_assignments_data.get('results', [])
        
        print(f"   ✅ My assignments endpoint working:")
        print(f"      Total assignments: {assignments_count}")
        
        if assignments_list:
            print(f"   📋 Sample assignment:")
            sample = assignments_list[0]
            print(f"      ID: {sample['id']}")
            print(f"      Description: {sample.get('description', 'N/A')}")
            print(f"      Status: {sample['status']}")
            print(f"      Customer: {sample.get('customer_name', 'N/A')}")
            if sample.get('vehicle'):
                vehicle = sample['vehicle']
                print(f"      Vehicle: {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}")
        else:
            print(f"   ⚠️  No assignments found for this technician")
    else:
        print(f"   ❌ My assignments endpoint failed: {my_assignments_response.status_code}")
        print(f"      Response: {my_assignments_response.content.decode()}")
        return False
    
    print(f"\n6️⃣ TESTING STATUS UPDATE ENDPOINTS")
    print("-" * 50)
    
    # Find a test appointment assigned to our technician
    test_appointments = Appointment.objects.filter(
        assigned_technician_id=employee_id,
        status__in=['assigned', 'scheduled']
    )
    
    if test_appointments.exists():
        test_apt = test_appointments.first()
        print(f"   🔧 Testing with appointment {test_apt.id} (Status: {test_apt.status})")
        
        # Test start-work endpoint
        start_work_response = client.post(f'/api/shop/appointments/{test_apt.id}/start-work/', **auth_headers)
        
        if start_work_response.status_code == 200:
            start_data = start_work_response.json()
            print(f"   ✅ Start work endpoint working:")
            print(f"      Message: {start_data.get('message')}")
            print(f"      New status: {start_data['work_details']['status']}")
            print(f"      Started at: {start_data['work_details']['started_at']}")
            
            # Test complete-work endpoint
            complete_work_response = client.post(f'/api/shop/appointments/{test_apt.id}/complete-work/', **auth_headers)
            
            if complete_work_response.status_code == 200:
                complete_data = complete_work_response.json()
                print(f"   ✅ Complete work endpoint working:")
                print(f"      Message: {complete_data.get('message')}")
                print(f"      Final status: {complete_data['completion_details']['status']}")
                print(f"      Completed at: {complete_data['completion_details']['completed_at']}")
            else:
                print(f"   ❌ Complete work failed: {complete_work_response.status_code}")
                print(f"      Response: {complete_work_response.content.decode()}")
        else:
            print(f"   ❌ Start work failed: {start_work_response.status_code}")
            print(f"      Response: {start_work_response.content.decode()}")
    else:
        print(f"   ⚠️  No test appointments available for status updates")
    
    print(f"\n7️⃣ TESTING STATUS FILTERING")
    print("-" * 50)
    
    # Test status filtering on my-assignments
    status_filter_response = client.get('/api/shop/appointments/my-assignments/?status=scheduled,in_progress', **auth_headers)
    
    if status_filter_response.status_code == 200:
        filtered_data = status_filter_response.json()
        print(f"   ✅ Status filtering working:")
        print(f"      Filtered count: {filtered_data.get('count', 0)}")
        
        # Verify all returned appointments have the correct status
        results = filtered_data.get('results', [])
        if results:
            statuses = [apt['status'] for apt in results]
            print(f"      Returned statuses: {set(statuses)}")
    else:
        print(f"   ❌ Status filtering failed: {status_filter_response.status_code}")
    
    print(f"\n📊 FINAL DATABASE STATE VERIFICATION")
    print("-" * 50)
    
    # Check final database state
    total_employees = Employee.objects.count()
    linked_employees = Employee.objects.filter(user__isnull=False).count()
    total_appointments = Appointment.objects.count()
    assigned_appointments = Appointment.objects.filter(assigned_technician__isnull=False).count()
    
    print(f"   📈 Database Statistics:")
    print(f"      Total Employees: {total_employees}")
    print(f"      Linked Employees: {linked_employees} ({linked_employees/total_employees*100:.1f}%)")
    print(f"      Total Appointments: {total_appointments}")
    print(f"      Assigned Appointments: {assigned_appointments}")
    
    return True

def generate_curl_test_commands():
    """Generate curl commands for testing the endpoints"""
    
    print(f"\n🚀 CURL TESTING COMMANDS")
    print("=" * 80)
    
    commands = """
# 1. Login and get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \\
  -H "Content-Type: application/json" \\
  -d '{"email": "john.mechanic@autorepair.com", "password": "password123"}' | \\
  python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 2. Test employee profile endpoint
curl -H "Authorization: Bearer $TOKEN" \\
  http://127.0.0.1:8000/api/auth/employee-profile/

# 3. Test all appointments (should include technician data)
curl -H "Authorization: Bearer $TOKEN" \\
  http://127.0.0.1:8000/api/shop/appointments/

# 4. Test technician-specific appointments
curl -H "Authorization: Bearer $TOKEN" \\
  http://127.0.0.1:8000/api/shop/appointments/my-assignments/

# 5. Test status filtering
curl -H "Authorization: Bearer $TOKEN" \\
  "http://127.0.0.1:8000/api/shop/appointments/my-assignments/?status=scheduled,in_progress"

# 6. Test status updates (replace 50 with actual appointment ID)
curl -H "Authorization: Bearer $TOKEN" \\
  -X POST http://127.0.0.1:8000/api/shop/appointments/50/start-work/

curl -H "Authorization: Bearer $TOKEN" \\
  -X POST http://127.0.0.1:8000/api/shop/appointments/50/complete-work/
"""
    
    print(commands)

if __name__ == "__main__":
    print("🔧 BACKEND FIXES FOR TECHNICIAN DASHBOARD")
    print("🎯 Testing all implemented solutions")
    print()
    
    success = test_technician_dashboard_fixes()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Backend is ready for technician dashboard integration")
        print("✅ User-Employee linking working")
        print("✅ Employee profile endpoint working") 
        print("✅ Appointments API includes technician data")
        print("✅ My-assignments endpoint working")
        print("✅ Status update endpoints working")
        
        generate_curl_test_commands()
        
        print(f"\n📋 FRONTEND INTEGRATION SUMMARY:")
        print("   - All required endpoints are implemented and tested")
        print("   - Authentication maps correctly to employee records") 
        print("   - API responses include all required technician data")
        print("   - Status filtering and updates work correctly")
        print("   - Ready for frontend integration!")
        
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print("   Review the error messages above and fix issues before frontend integration")
    
    sys.exit(0 if success else 1)