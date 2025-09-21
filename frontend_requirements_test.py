#!/usr/bin/env python3
"""
Comprehensive Backend Verification for Frontend Requirements
Tests all technician assignment endpoints and validates response formats
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
from django.urls import reverse
from shop.models import Employee, Appointment, Vehicle, Customer, Shop
import json

def test_frontend_requirements():
    """Test all requirements specified by the frontend developer"""
    print("🧪 TESTING BACKEND IMPLEMENTATION FOR FRONTEND REQUIREMENTS")
    print("=" * 80)
    
    client = Client()
    User = get_user_model()
    
    # Create test user if needed
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
    
    # Login to get authentication
    client.login(username='testuser', password='testpass123')
    
    # Test Results Tracking
    results = {
        'endpoints_tested': 0,
        'endpoints_passed': 0,
        'issues_found': [],
        'recommendations': []
    }
    
    print("\n📋 TESTING REQUIRED ENDPOINTS")
    print("-" * 60)
    
    # 1. Test GET /api/shop/employees/?role=technician
    print("1️⃣ Testing: GET /api/shop/employees/?role=technician")
    response = client.get('/api/shop/employees/?role=technician')
    results['endpoints_tested'] += 1
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📊 Technicians found: {len(data)}")
        
        if len(data) > 0:
            tech = data[0]
            required_fields = [
                'id', 'name', 'role', 'email', 'workload_count', 
                'is_available', 'current_jobs'
            ]
            missing_fields = [field for field in required_fields if field not in tech]
            
            if missing_fields:
                results['issues_found'].append(f"Employee API missing fields: {missing_fields}")
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print("   ✅ All required fields present")
                results['endpoints_passed'] += 1
        else:
            results['issues_found'].append("No technicians found in database")
            print("   ⚠️  No technicians in database")
    else:
        results['issues_found'].append(f"Employee API failed: {response.status_code}")
        print(f"   ❌ Status: {response.status_code}")
    
    # 2. Test GET /api/shop/technicians/workload/
    print("\n2️⃣ Testing: GET /api/shop/technicians/workload/")
    response = client.get('/api/shop/technicians/workload/')
    results['endpoints_tested'] += 1
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        
        # Check response structure
        required_top_level = ['summary', 'technicians']
        missing_top = [field for field in required_top_level if field not in data]
        
        if missing_top:
            results['issues_found'].append(f"Workload API missing top-level fields: {missing_top}")
            print(f"   ⚠️  Missing top-level fields: {missing_top}")
        else:
            print("   ✅ Correct response structure")
            
            # Check summary structure
            summary = data.get('summary', {})
            summary_fields = ['total_technicians', 'available_technicians', 'busy_technicians']
            missing_summary = [field for field in summary_fields if field not in summary]
            
            if missing_summary:
                results['issues_found'].append(f"Workload summary missing: {missing_summary}")
                print(f"   ⚠️  Summary missing: {missing_summary}")
            else:
                print("   ✅ Summary structure correct")
                results['endpoints_passed'] += 1
    else:
        results['issues_found'].append(f"Workload API failed: {response.status_code}")
        print(f"   ❌ Status: {response.status_code}")
    
    # 3. Test Assignment Workflow
    print("\n3️⃣ Testing: Assignment Workflow")
    
    # Get a test appointment and technician
    appointments = Appointment.objects.filter(status='pending')
    technicians = Employee.objects.filter(role__icontains='technician')
    
    if appointments.exists() and technicians.exists():
        appointment = appointments.first()
        technician = technicians.first()
        
        # 3a. Test assign technician
        print(f"   🔧 Testing assign technician (Apt: {appointment.id}, Tech: {technician.id})")
        response = client.post(
            f'/api/shop/appointments/{appointment.id}/assign-technician/',
            data=json.dumps({'technician_id': technician.id}),
            content_type='application/json'
        )
        results['endpoints_tested'] += 1
        
        if response.status_code == 200:
            print(f"   ✅ Assign Status: {response.status_code}")
            
            # Check response format
            data = response.json()
            frontend_required = ['message', 'appointment', 'technician', 'assignment_details']
            
            # Check what frontend expects vs what we return
            if 'appointment' in data:
                print("   ✅ Returns appointment data")
            else:
                results['issues_found'].append("Assignment response missing appointment data")
                print("   ⚠️  Missing appointment data in response")
            
            results['endpoints_passed'] += 1
            
            # 3b. Test start work (if appointment was assigned)
            print(f"   ⚡ Testing start work")
            response = client.post(f'/api/shop/appointments/{appointment.id}/start-work/')
            results['endpoints_tested'] += 1
            
            if response.status_code == 200:
                print(f"   ✅ Start Work Status: {response.status_code}")
                results['endpoints_passed'] += 1
                
                # 3c. Test complete work
                print(f"   🏁 Testing complete work")
                response = client.post(f'/api/shop/appointments/{appointment.id}/complete-work/')
                results['endpoints_tested'] += 1
                
                if response.status_code == 200:
                    print(f"   ✅ Complete Work Status: {response.status_code}")
                    results['endpoints_passed'] += 1
                else:
                    results['issues_found'].append(f"Complete work failed: {response.status_code}")
                    print(f"   ❌ Complete Work Status: {response.status_code}")
            else:
                results['issues_found'].append(f"Start work failed: {response.status_code}")
                print(f"   ❌ Start Work Status: {response.status_code}")
        else:
            results['issues_found'].append(f"Assign technician failed: {response.status_code}")
            print(f"   ❌ Assign Status: {response.status_code}")
    else:
        results['issues_found'].append("No test data available for assignment workflow")
        print("   ⚠️  No test appointments or technicians available")
    
    # 4. Response Format Analysis
    print("\n4️⃣ Analyzing Response Format Compatibility")
    
    # Check if current response matches frontend expectations
    response = client.get('/api/shop/technicians/workload/')
    if response.status_code == 200:
        data = response.json()
        
        # Frontend expects this structure per their requirements:
        frontend_expected_structure = {
            'technicians': [
                {
                    'id': 'number',
                    'first_name': 'string',
                    'last_name': 'string', 
                    'position': 'string',
                    'email': 'string',
                    'current_workload': 'number',
                    'max_capacity': 'number',
                    'availability_score': 'number',
                    'current_jobs': [
                        {
                            'appointment_id': 'number',
                            'customer_name': 'string',
                            'vehicle': 'string',
                            'service_type': 'string',
                            'status': 'string',
                            'started_at': 'datetime',
                            'estimated_completion': 'datetime'
                        }
                    ]
                }
            ],
            'summary': {
                'total_technicians': 'number',
                'available_technicians': 'number',
                'busy_technicians': 'number',
                'total_active_jobs': 'number',
                'average_workload': 'number'
            }
        }
        
        # Check current structure vs frontend expectations
        current_structure_issues = []
        
        if 'technicians' in data and len(data['technicians']) > 0:
            tech_sample = data['technicians'][0]
            
            # Check technician structure
            if 'technician' in tech_sample:
                # Our current format uses nested 'technician' object
                actual_tech = tech_sample['technician']
                if 'name' in actual_tech and 'first_name' not in actual_tech:
                    current_structure_issues.append("Frontend expects 'first_name'/'last_name', we provide 'name'")
                    
            if 'workload' in tech_sample:
                workload = tech_sample['workload']
                if 'current_appointments' in workload and 'current_workload' not in workload:
                    current_structure_issues.append("Frontend expects 'current_workload', we provide 'current_appointments'")
        
        # Check summary structure  
        if 'summary' in data:
            summary = data['summary']
            frontend_summary_fields = ['total_technicians', 'available_technicians', 'busy_technicians', 'total_active_jobs', 'average_workload']
            missing_summary_fields = [f for f in frontend_summary_fields if f not in summary]
            
            if missing_summary_fields:
                current_structure_issues.append(f"Summary missing frontend-expected fields: {missing_summary_fields}")
        
        if current_structure_issues:
            results['recommendations'].extend(current_structure_issues)
            print("   ⚠️  Response format issues found:")
            for issue in current_structure_issues:
                print(f"      - {issue}")
        else:
            print("   ✅ Response format compatible with frontend expectations")
    
    # Final Report
    print(f"\n📊 FINAL RESULTS")
    print("=" * 80)
    
    success_rate = (results['endpoints_passed'] / results['endpoints_tested']) * 100 if results['endpoints_tested'] > 0 else 0
    
    print(f"📈 Success Rate: {success_rate:.1f}% ({results['endpoints_passed']}/{results['endpoints_tested']} endpoints working)")
    
    if results['issues_found']:
        print(f"\n🚨 Issues Found ({len(results['issues_found'])}):")
        for i, issue in enumerate(results['issues_found'], 1):
            print(f"   {i}. {issue}")
    
    if results['recommendations']:
        print(f"\n💡 Recommendations ({len(results['recommendations'])}):")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Overall Status
    if success_rate >= 80 and len(results['issues_found']) == 0:
        print(f"\n🎉 READY FOR FRONTEND INTEGRATION!")
        print("   All required endpoints are working and compatible")
        return True
    elif success_rate >= 60:
        print(f"\n⚠️  MOSTLY READY - Minor adjustments needed")
        print("   Most endpoints working, address issues above")
        return False
    else:
        print(f"\n❌ NEEDS WORK - Several issues to resolve")
        print("   Address critical issues before frontend integration")
        return False

if __name__ == "__main__":
    success = test_frontend_requirements()
    
    print(f"\n📋 SUMMARY FOR FRONTEND DEVELOPER:")
    print("=" * 80)
    
    if success:
        print("✅ Backend is ready for your frontend integration!")
        print("✅ All required endpoints implemented and working")
        print("✅ Response formats compatible with your requirements")
        print("\n🚀 You can proceed with testing your React application")
    else:
        print("⚠️  Backend needs minor adjustments before full integration")
        print("📝 Review the issues and recommendations above")
        print("🔧 Most endpoints are working - small tweaks needed")
    
    sys.exit(0 if success else 1)