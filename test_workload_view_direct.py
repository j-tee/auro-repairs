#!/usr/bin/env python3
"""
Test Technician Workload View Function Directly
Tests the technician_workload view function without HTTP auth
"""

import os
import sys
import django
import json

# Set up Django environment
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Employee
from shop.serializers import EmployeeSerializer

def test_computed_properties_direct():
    """Test computed properties directly on Employee model"""
    print("=" * 60)
    print("EMPLOYEE COMPUTED PROPERTIES TEST")
    print("=" * 60)
    
    try:
        # Get a technician employee
        technician = Employee.objects.filter(role='technician').first()
        if not technician:
            technician = Employee.objects.first()
        
        if not technician:
            print("❌ No employees found in database")
            return
        
        print(f"Testing Employee: {technician.name} (ID: {technician.id})")
        print(f"Role: {technician.role}")
        print()
        
        print("� TESTING COMPUTED PROPERTIES DIRECTLY:")
        print("-" * 50)
        
        # Test each computed property
        computed_props = {
            'current_appointments': lambda: technician.current_appointments,
            'workload_count': lambda: technician.workload_count,
            'is_available': lambda: technician.is_available,
            'appointments_today': lambda: technician.appointments_today,
            'is_technician': lambda: technician.is_technician
        }
        
        for prop_name, prop_func in computed_props.items():
            try:
                value = prop_func()
                if hasattr(value, 'count'):  # QuerySet
                    count = value.count()
                    print(f"  ✅ {prop_name}: {count} items (QuerySet)")
                    if count > 0:
                        print(f"      First item: {list(value)[0] if count > 0 else 'None'}")
                else:
                    print(f"  ✅ {prop_name}: {value} ({type(value).__name__})")
            except Exception as e:
                print(f"  ❌ {prop_name}: ERROR - {e}")
        
        print()
        print("📋 REGULAR EMPLOYEE SERIALIZER OUTPUT:")
        print("-" * 50)
        
        # Test regular serializer
        serializer = EmployeeSerializer(technician)
        response_data = serializer.data
        print(json.dumps(response_data, indent=2, default=str))
        
        print()
        print("🎯 WORKLOAD DATA STRUCTURE (Manual):")
        print("-" * 50)
        
        # Build workload structure like the specialized endpoint does
        workload_structure = {
            'technician': {
                'id': technician.id,
                'name': technician.name,
                'role': technician.role,
            },
            'workload': {
                'current_appointments': technician.workload_count,
                'is_available': technician.is_available,
                'appointments_today': technician.appointments_today.count(),
                'max_capacity': 3
            }
        }
        
        print(json.dumps(workload_structure, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error testing computed properties: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_computed_properties_direct()