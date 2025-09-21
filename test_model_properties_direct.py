#!/usr/bin/env python3
"""
Direct Model Property Test
Tests the Employee model properties without HTTP/auth complications
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Employee, Appointment
from shop.serializers import EmployeeSerializer
import json

def test_employee_model_properties():
    """Test Employee model computed properties directly"""
    print("=" * 60)
    print("EMPLOYEE MODEL COMPUTED PROPERTIES TEST")
    print("=" * 60)
    
    try:
        # Get a technician employee
        technician = Employee.objects.filter(role='technician').first()
        
        if not technician:
            print("❌ No technician found in database")
            return
        
        print(f"Testing Technician: {technician.name} (ID: {technician.id})")
        print(f"Role: {technician.role}")
        print()
        
        # Test computed properties directly on model instance
        print("🔍 COMPUTED PROPERTIES ON MODEL INSTANCE:")
        print("-" * 50)
        
        try:
            current_appointments = technician.current_appointments
            print(f"✅ current_appointments: {current_appointments} (QuerySet with {current_appointments.count()} items)")
        except Exception as e:
            print(f"❌ current_appointments failed: {e}")
        
        try:
            workload_count = technician.workload_count
            print(f"✅ workload_count: {workload_count}")
        except Exception as e:
            print(f"❌ workload_count failed: {e}")
        
        try:
            is_available = technician.is_available
            print(f"✅ is_available: {is_available}")
        except Exception as e:
            print(f"❌ is_available failed: {e}")
        
        try:
            appointments_today = technician.appointments_today
            print(f"✅ appointments_today: {appointments_today} (QuerySet with {appointments_today.count()} items)")
        except Exception as e:
            print(f"❌ appointments_today failed: {e}")
        
        try:
            is_technician = technician.is_technician
            print(f"✅ is_technician: {is_technician}")
        except Exception as e:
            print(f"❌ is_technician failed: {e}")
        
        print()
        
        # Test what EmployeeSerializer includes
        print("📋 EMPLOYEE SERIALIZER OUTPUT:")
        print("-" * 50)
        
        serializer = EmployeeSerializer(technician)
        serialized_data = serializer.data
        
        print("Fields included in serializer:")
        for field_name, value in serialized_data.items():
            print(f"  {field_name}: {value}")
        
        print()
        
        # Check if computed properties are in serializer output
        print("🔍 COMPUTED PROPERTIES IN SERIALIZER:")
        print("-" * 50)
        
        computed_props = ['current_appointments', 'workload_count', 'is_available', 'appointments_today', 'is_technician']
        
        for prop in computed_props:
            if prop in serialized_data:
                print(f"  ✅ {prop}: INCLUDED ({serialized_data[prop]})")
            else:
                print(f"  ❌ {prop}: NOT INCLUDED")
        
        print()
        print("📊 ANALYSIS:")
        print("-" * 50)
        print("✅ Model has computed properties (@property methods)")
        print("❌ Serializer excludes computed properties (DRF limitation)")
        print("💡 Workload endpoint manually includes them via custom view logic")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing employee properties: {e}")
        import traceback
        traceback.print_exc()
        return False

def explain_api_discrepancy():
    """Explain the discrepancy between documentation and actual API"""
    print("\n" + "=" * 60)
    print("DOCUMENTATION vs REALITY ANALYSIS")
    print("=" * 60)
    
    print("""
🎯 THE ISSUE IDENTIFIED:

1. EMPLOYEE MODEL ✅
   - Has @property methods for computed fields
   - Properties work correctly on model instances
   - current_appointments, workload_count, is_available, etc.

2. EMPLOYEE API (EmployeeSerializer) ❌ 
   - Uses fields = "__all__" 
   - DRF ModelSerializer ONLY includes database fields
   - @property methods are NOT automatically included
   - Missing: current_appointments, workload_count, is_available

3. WORKLOAD API (Custom View) ✅
   - Manually calls the @property methods
   - tech.workload_count, tech.is_available, etc.
   - Constructs custom response with computed data
   - Available at: /api/shop/technicians/workload/

📋 DOCUMENTATION PROBLEM:
The frontend documentation suggests computed properties are available 
in regular Employee API responses, but they're only available via 
the specialized workload endpoint.

🔧 SOLUTIONS:
A) Update documentation to clarify which endpoint provides which data
B) Enhance EmployeeSerializer to include computed properties
C) Create separate TechnicianSerializer for technician-specific needs
    """)

if __name__ == "__main__":
    success = test_employee_model_properties()
    explain_api_discrepancy()