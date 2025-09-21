#!/usr/bin/env python3
"""
IMMEDIATE FIX: Update RepairOrderSerializer to provide consistent vehicle_id
This fixes the immediate issue where frontend doesn't know whether to use 'vehicle' or 'vehicle_id'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

def test_current_serializer_output():
    """Test what the current serializer returns"""
    from shop.models import RepairOrder
    from shop.serializers import RepairOrderSerializer
    
    repair_order = RepairOrder.objects.first()
    if not repair_order:
        print("❌ No repair orders found in database")
        return
    
    serializer = RepairOrderSerializer(repair_order)
    data = serializer.data
    
    print("🔍 CURRENT SERIALIZER OUTPUT:")
    print(f"   vehicle field type: {type(data.get('vehicle'))}")
    print(f"   vehicle field value: {data.get('vehicle')}")
    print(f"   has vehicle_id field: {'vehicle_id' in data}")
    
    if isinstance(data.get('vehicle'), int):
        print("   ✅ Good: vehicle field contains ID")
        print("   ❌ Problem: Frontend needs vehicle object data too")
    elif isinstance(data.get('vehicle'), dict):
        print("   ❌ Problem: vehicle field contains object (frontend expects ID)")
        print("   ✅ Good: Vehicle object data is available")
    
    print(f"\n💡 SOLUTION: Provide both vehicle_id (integer) and vehicle (object)")

if __name__ == "__main__":
    test_current_serializer_output()
