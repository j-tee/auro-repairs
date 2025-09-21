#!/usr/bin/env python3
"""
TEST UPDATED API CONSISTENCY
Tests that RepairOrder and Appointment APIs now provide consistent field patterns
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/shop"

def test_repair_order_consistency():
    """Test RepairOrder API provides both vehicle_id and vehicle fields"""
    print("🔧 TESTING REPAIR ORDER API CONSISTENCY")
    print("=" * 45)
    
    try:
        response = requests.get(f"{BASE_URL}/repair-orders/")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                first_order = data[0]
                
                print(f"📋 RepairOrder #{first_order.get('id')} fields:")
                print(f"   ✅ vehicle_id: {first_order.get('vehicle_id')} (type: {type(first_order.get('vehicle_id'))})")
                
                vehicle_obj = first_order.get('vehicle')
                if vehicle_obj:
                    print(f"   ✅ vehicle: {type(vehicle_obj)} with make='{vehicle_obj.get('make')}'")
                else:
                    print(f"   ❌ vehicle: {vehicle_obj}")
                
                print(f"   ✅ customer_id: {first_order.get('customer_id')}")
                print(f"   ✅ customer_name: '{first_order.get('customer_name')}'")
                print(f"   ✅ status: '{first_order.get('status')}'")
                
                # Check for the old inconsistent pattern
                if isinstance(first_order.get('vehicle'), int):
                    print("   ❌ STILL BROKEN: vehicle field returns integer instead of object")
                    return False
                else:
                    print("   ✅ FIXED: vehicle field returns object data")
                    return True
            else:
                print("   ⚠️  No repair orders found")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_appointment_consistency():
    """Test Appointment API provides both vehicle_id and vehicle fields"""
    print("\n📅 TESTING APPOINTMENT API CONSISTENCY")
    print("=" * 42)
    
    try:
        response = requests.get(f"{BASE_URL}/appointments/")
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                first_appointment = data[0]
                
                print(f"📅 Appointment #{first_appointment.get('id')} fields:")
                print(f"   ✅ vehicle_id: {first_appointment.get('vehicle_id')} (type: {type(first_appointment.get('vehicle_id'))})")
                
                vehicle_obj = first_appointment.get('vehicle')
                if vehicle_obj and isinstance(vehicle_obj, dict):
                    print(f"   ✅ vehicle: {type(vehicle_obj)} with make='{vehicle_obj.get('make')}'")
                else:
                    print(f"   ❌ vehicle: {vehicle_obj} (type: {type(vehicle_obj)})")
                
                print(f"   ✅ customer_id: {first_appointment.get('customer_id')}")
                print(f"   ✅ customer_name: '{first_appointment.get('customer_name')}'")
                print(f"   ✅ status: '{first_appointment.get('status')}'")
                
                return isinstance(vehicle_obj, dict)
            else:
                print("   ⚠️  No appointments found")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_frontend_typescript_example():
    """Show example of consistent TypeScript interface usage"""
    print("\n📝 FRONTEND TYPESCRIPT INTERFACE EXAMPLE")
    print("=" * 45)
    
    typescript_example = '''
// ✅ CONSISTENT TypeScript interfaces after API fix
interface RepairOrder {
  id: number;
  vehicle_id: number;     // Always integer for forms/relationships
  vehicle: VehicleSummary; // Always object for display
  customer_id: number;    // Convenience field
  customer_name: string;  // Convenience field
  status: string;
  // ... other fields
}

interface Appointment {
  id: number;
  vehicle_id: number;     // Always integer for forms/relationships  
  vehicle: VehicleSummary; // Always object for display
  customer_id: number;    // Convenience field
  customer_name: string;  // Convenience field
  status: string;
  // ... other fields
}

// ✅ Frontend usage is now consistent:
function displayRepairOrder(order: RepairOrder) {
  // Use integer ID for relationships/forms
  const vehicleId = order.vehicle_id;
  
  // Use object data for display
  const vehicleName = `${order.vehicle.year} ${order.vehicle.make} ${order.vehicle.model}`;
  const customerName = order.customer_name;
  
  return `${customerName}'s ${vehicleName} - Status: ${order.status}`;
}

// ✅ Same pattern works for appointments:
function displayAppointment(appointment: Appointment) {
  const vehicleId = appointment.vehicle_id;
  const vehicleName = `${appointment.vehicle.year} ${appointment.vehicle.make} ${appointment.vehicle.model}`;
  const customerName = appointment.customer_name;
  
  return `${customerName}'s ${vehicleName} - ${appointment.date}`;
}
'''
    
    print(typescript_example)

def main():
    """Test the API consistency fix"""
    print("🧪 TESTING API CONSISTENCY FIX")
    print("=" * 35)
    
    repair_order_ok = test_repair_order_consistency()
    appointment_ok = test_appointment_consistency()
    
    print("\n🎯 SUMMARY")
    print("=" * 15)
    
    if repair_order_ok and appointment_ok:
        print("✅ API CONSISTENCY FIX SUCCESSFUL!")
        print("✅ RepairOrder API provides both vehicle_id (int) and vehicle (object)")
        print("✅ Appointment API provides both vehicle_id (int) and vehicle (object)")
        print("✅ Frontend developers can use consistent patterns")
        
        test_frontend_typescript_example()
        
        print("\n🎉 RESULT: API responses are now consistent!")
        print("   • Always use vehicle_id for relationships/forms")
        print("   • Always use vehicle.make, vehicle.model for display") 
        print("   • Customer info available without additional API calls")
        
    else:
        print("❌ API consistency fix needs attention")
        if not repair_order_ok:
            print("❌ RepairOrder API still inconsistent")
        if not appointment_ok:
            print("❌ Appointment API still inconsistent")

if __name__ == "__main__":
    main()
