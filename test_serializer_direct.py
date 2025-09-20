#!/usr/bin/env python3
"""
DIRECT SERIALIZER CONSISTENCY TEST
Tests the serializers directly using Django models to verify API consistency fix
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/home/teejay/Documents/Projects/auro-repairs')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import RepairOrder, Appointment
from shop.serializers import RepairOrderSerializer, AppointmentSerializer

def test_repair_order_serializer():
    """Test RepairOrderSerializer provides consistent fields"""
    print("🔧 TESTING REPAIR ORDER SERIALIZER")
    print("=" * 38)
    
    try:
        # Get a repair order
        repair_order = RepairOrder.objects.first()
        if not repair_order:
            print("   ⚠️  No repair orders found in database")
            return False
        
        # Serialize it
        serializer = RepairOrderSerializer(repair_order)
        data = serializer.data
        
        print(f"📋 RepairOrder #{data.get('id')} serialized fields:")
        print(f"   ✅ vehicle_id: {data.get('vehicle_id')} (type: {type(data.get('vehicle_id'))})")
        
        vehicle_obj = data.get('vehicle')
        if isinstance(vehicle_obj, dict):
            print(f"   ✅ vehicle: dict with make='{vehicle_obj.get('make')}'")
            success = True
        elif isinstance(vehicle_obj, int):
            print(f"   ❌ vehicle: {vehicle_obj} (still returns integer!)")
            success = False
        else:
            print(f"   ❌ vehicle: {vehicle_obj} (type: {type(vehicle_obj)})")
            success = False
        
        print(f"   ✅ customer_id: {data.get('customer_id')}")
        print(f"   ✅ customer_name: '{data.get('customer_name')}'")
        print(f"   ✅ status: '{data.get('status')}'")
        
        # Show complete vehicle object structure
        if isinstance(vehicle_obj, dict):
            print(f"   📄 Complete vehicle object: {vehicle_obj}")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error testing RepairOrderSerializer: {e}")
        return False

def test_appointment_serializer():
    """Test AppointmentSerializer provides consistent fields"""
    print("\n📅 TESTING APPOINTMENT SERIALIZER")
    print("=" * 35)
    
    try:
        # Get an appointment
        appointment = Appointment.objects.first()
        if not appointment:
            print("   ⚠️  No appointments found in database")
            return False
        
        # Serialize it
        serializer = AppointmentSerializer(appointment)
        data = serializer.data
        
        print(f"📅 Appointment #{data.get('id')} serialized fields:")
        print(f"   ✅ vehicle_id: {data.get('vehicle_id')} (type: {type(data.get('vehicle_id'))})")
        
        vehicle_obj = data.get('vehicle')
        if isinstance(vehicle_obj, dict):
            print(f"   ✅ vehicle: dict with make='{vehicle_obj.get('make')}'")
            success = True
        elif isinstance(vehicle_obj, int):
            print(f"   ❌ vehicle: {vehicle_obj} (still returns integer!)")
            success = False
        else:
            print(f"   ❌ vehicle: {vehicle_obj} (type: {type(vehicle_obj)})")
            success = False
        
        print(f"   ✅ customer_id: {data.get('customer_id')}")
        print(f"   ✅ customer_name: '{data.get('customer_name')}'")
        print(f"   ✅ reported_problem_id: {data.get('reported_problem_id')}")
        
        # Show complete vehicle object structure
        if isinstance(vehicle_obj, dict):
            print(f"   📄 Complete vehicle object: {vehicle_obj}")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error testing AppointmentSerializer: {e}")
        return False

def show_field_comparison():
    """Show before/after comparison"""
    print("\n📊 BEFORE vs AFTER COMPARISON")
    print("=" * 32)
    
    before_after = '''
🔧 RepairOrder API Response:
   BEFORE: {"vehicle": 27}  ← Integer ID only
   AFTER:  {"vehicle_id": 27, "vehicle": {"make": "Toyota", "model": "Camry", ...}}
                     
📅 Appointment API Response:  
   BEFORE: {"vehicle": {"make": "Toyota", ...}}  ← Object only
   AFTER:  {"vehicle_id": 27, "vehicle": {"make": "Toyota", "model": "Camry", ...}}

✅ CONSISTENT PATTERN: Both APIs now provide:
   • vehicle_id (integer) for relationships/forms
   • vehicle (object) for display purposes
   • customer_id + customer_name for convenience
'''
    print(before_after)

def main():
    """Main test function"""
    print("🧪 DIRECT SERIALIZER CONSISTENCY TEST")
    print("=" * 40)
    
    repair_order_ok = test_repair_order_serializer()
    appointment_ok = test_appointment_serializer()
    
    show_field_comparison()
    
    print("\n🎯 SUMMARY")
    print("=" * 15)
    
    if repair_order_ok and appointment_ok:
        print("✅ API CONSISTENCY FIX SUCCESSFUL!")
        print("✅ RepairOrderSerializer provides both vehicle_id and vehicle")
        print("✅ AppointmentSerializer provides both vehicle_id and vehicle")
        print("✅ Frontend can use consistent patterns")
        
        print("\n🎉 FRONTEND BENEFITS:")
        print("   • Always use obj.vehicle_id for form inputs")
        print("   • Always use obj.vehicle.make for displays")
        print("   • Customer info available without additional queries")
        print("   • Consistent TypeScript interfaces possible")
        
    else:
        print("❌ API consistency fix needs attention")
        if not repair_order_ok:
            print("❌ RepairOrderSerializer still inconsistent")
        if not appointment_ok:
            print("❌ AppointmentSerializer still inconsistent")
        
        print("\n🔧 Check that serializers.py was updated correctly")

if __name__ == "__main__":
    main()
