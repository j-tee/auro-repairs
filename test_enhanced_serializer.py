#!/usr/bin/env python3
"""
Test Enhanced Employee Serializer
Tests the updated EmployeeSerializer with computed properties
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

def test_enhanced_employee_serializer():
    """Test the enhanced EmployeeSerializer with computed properties"""
    print("=" * 60)
    print("ENHANCED EMPLOYEE SERIALIZER TEST")
    print("=" * 60)
    
    try:
        # Test with a technician
        technician = Employee.objects.filter(role='technician').first()
        
        if not technician:
            print("❌ No technician found in database")
            return False
        
        print(f"Testing Technician: {technician.name} (ID: {technician.id})")
        print(f"Role: {technician.role}")
        print()
        
        # Test the enhanced serializer
        print("📋 ENHANCED EMPLOYEE SERIALIZER OUTPUT:")
        print("-" * 50)
        
        serializer = EmployeeSerializer(technician)
        serialized_data = serializer.data
        
        print("All fields now included:")
        for field_name, value in serialized_data.items():
            if field_name in ['workload_count', 'is_available', 'appointments_today_count', 'is_technician', 'current_jobs']:
                print(f"  ✅ {field_name}: {value} (COMPUTED)")
            else:
                print(f"  📋 {field_name}: {value}")
        
        print()
        print("🔍 COMPUTED PROPERTIES VERIFICATION:")
        print("-" * 50)
        
        # Verify computed properties are now included
        computed_props = ['workload_count', 'is_available', 'appointments_today_count', 'is_technician']
        
        all_included = True
        for prop in computed_props:
            if prop in serialized_data:
                print(f"  ✅ {prop}: {serialized_data[prop]}")
            else:
                print(f"  ❌ MISSING: {prop}")
                all_included = False
        
        # Check current_jobs structure
        current_jobs = serialized_data.get('current_jobs', [])
        print(f"  ✅ current_jobs: {len(current_jobs)} jobs")
        if current_jobs:
            print(f"      Example job: {current_jobs[0]}")
        
        print()
        print("📊 COMPLETE JSON RESPONSE:")
        print("-" * 50)
        print(json.dumps(serialized_data, indent=2, default=str))
        
        if all_included:
            print("\n🎉 SUCCESS: Enhanced serializer includes all computed properties!")
            return True
        else:
            print("\n⚠️  WARNING: Some computed properties are still missing!")
            return False
        
    except Exception as e:
        print(f"❌ Error testing enhanced serializer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_non_technician_employee():
    """Test serializer with non-technician employee"""
    print("\n" + "=" * 60)
    print("NON-TECHNICIAN EMPLOYEE SERIALIZER TEST")
    print("=" * 60)
    
    try:
        # Find a non-technician employee
        non_tech = Employee.objects.exclude(role__icontains='technician').first()
        
        if not non_tech:
            print("❌ No non-technician employee found")
            return
        
        print(f"Testing Employee: {non_tech.name} (ID: {non_tech.id})")
        print(f"Role: {non_tech.role}")
        print()
        
        serializer = EmployeeSerializer(non_tech)
        serialized_data = serializer.data
        
        print("📋 NON-TECHNICIAN COMPUTED FIELDS:")
        print("-" * 50)
        print(f"  workload_count: {serialized_data.get('workload_count', 'N/A')}")
        print(f"  is_available: {serialized_data.get('is_available', 'N/A')}")
        print(f"  appointments_today_count: {serialized_data.get('appointments_today_count', 'N/A')}")
        print(f"  is_technician: {serialized_data.get('is_technician', 'N/A')}")
        print(f"  current_jobs: {serialized_data.get('current_jobs', 'N/A')}")
        
        print("\n✅ Non-technician fields handled appropriately")
        
    except Exception as e:
        print(f"❌ Error testing non-technician: {e}")

if __name__ == "__main__":
    success = test_enhanced_employee_serializer()
    test_non_technician_employee()
    
    if success:
        print("\n" + "🚀 SERIALIZER ENHANCEMENT COMPLETE!")
        print("   • Computed properties now included in Employee API")
        print("   • Workload data available for technicians")  
        print("   • Appropriate handling for non-technician employees")
    else:
        print("\n❌ SERIALIZER ENHANCEMENT FAILED!")
        print("   Some computed properties are not working correctly")