#!/usr/bin/env python3
"""
Test Employee API Response Structure
Tests what fields are actually returned by the Employee API
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Employee
from shop.serializers import EmployeeSerializer
import json

def test_employee_api_response():
    """Test what fields are returned by EmployeeSerializer"""
    print("=" * 60)
    print("EMPLOYEE API RESPONSE STRUCTURE TEST")
    print("=" * 60)
    
    # Get a technician employee
    try:
        technician = Employee.objects.filter(role='technician').first()
        if not technician:
            # Get any employee
            technician = Employee.objects.first()
        
        if not technician:
            print("❌ No employees found in database")
            return
        
        print(f"Testing Employee: {technician.name} (ID: {technician.id})")
        print(f"Role: {technician.role}")
        print()
        
        # Test the serializer
        serializer = EmployeeSerializer(technician)
        response_data = serializer.data
        
        print("📋 API Response Fields:")
        print("-" * 40)
        for field, value in response_data.items():
            print(f"  {field}: {value} ({type(value).__name__})")
        
        print()
        print("🔍 Checking Computed Properties:")
        print("-" * 40)
        
        # Check if computed properties are included
        computed_props = [
            'current_appointments',
            'workload_count', 
            'is_available',
            'appointments_today',
            'is_technician'
        ]
        
        for prop in computed_props:
            if prop in response_data:
                print(f"  ✅ {prop}: {response_data[prop]}")
            else:
                print(f"  ❌ {prop}: NOT INCLUDED")
        
        print()
        print("📊 Response JSON Structure:")
        print("-" * 40)
        print(json.dumps(response_data, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error testing employee API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employee_api_response()