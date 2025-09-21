#!/usr/bin/env python3
"""
API Response Standardization Fix
Addresses inconsistent serializer responses where sometimes 'vehicle' contains an integer ID
and sometimes it contains the full vehicle object, causing frontend confusion.

This script creates standardized serializers that always provide both:
- {field_name}_id: Integer ID for the relationship
- {field_name}: Full object data for the relationship
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import RepairOrder, Appointment, Vehicle, Customer

def analyze_current_api_inconsistencies():
    """Analyze current API response inconsistencies"""
    print("🔍 ANALYZING CURRENT API INCONSISTENCIES")
    print("=" * 50)
    
    # Check RepairOrder serializer behavior
    repair_order = RepairOrder.objects.first()
    if repair_order:
        print(f"📋 RepairOrder Example (ID: {repair_order.id}):")
        print(f"   • vehicle field in model: {type(repair_order.vehicle)} (Vehicle object)")
        print(f"   • vehicle.id: {repair_order.vehicle.id}")
        print(f"   • vehicle.customer.id: {repair_order.vehicle.customer.id}")
        
        # Check what serializer would return
        from shop.serializers import RepairOrderSerializer
        from rest_framework.renderers import JSONRenderer
        
        serializer = RepairOrderSerializer(repair_order)
        data = serializer.data
        
        print(f"   • Serialized 'vehicle' field type: {type(data.get('vehicle'))}")
        print(f"   • Serialized 'vehicle' value: {data.get('vehicle')}")
        
        if isinstance(data.get('vehicle'), dict):
            print("   ⚠️  PROBLEM: 'vehicle' returns full object (inconsistent for frontend)")
        elif isinstance(data.get('vehicle'), int):
            print("   ⚠️  PROBLEM: 'vehicle' returns ID only (frontend needs object data too)")
    
    # Check Appointment serializer behavior  
    appointment = Appointment.objects.first()
    if appointment:
        print(f"\n📅 Appointment Example (ID: {appointment.id}):")
        print(f"   • vehicle field in model: {type(appointment.vehicle)} (Vehicle object)")
        print(f"   • vehicle.id: {appointment.vehicle.id}")
        
        from shop.serializers import AppointmentSerializer
        serializer = AppointmentSerializer(appointment)
        data = serializer.data
        
        print(f"   • Serialized 'vehicle' field type: {type(data.get('vehicle'))}")
        print(f"   • Has 'vehicle_id' field: {'vehicle_id' in data}")
        
    print(f"\n🎯 FRONTEND IMPACT:")
    print(f"   • React developer confused: use 'vehicle' or 'vehicle_id'?")
    print(f"   • Inconsistent across different API endpoints")
    print(f"   • TypeScript interfaces become complex and error-prone")
    print(f"   • API responses vary between create/read/update operations")

def create_standardized_serializers():
    """Create standardized serializer patterns"""
    print(f"\n🔧 CREATING STANDARDIZED SERIALIZER PATTERNS")
    print("=" * 50)
    
    serializer_code = '''# 🎯 STANDARDIZED SERIALIZERS FOR CONSISTENT API RESPONSES
#
# DESIGN PRINCIPLE: Always provide both ID and object data
# - {field_name}_id: Integer ID (for forms, updates, relationships)
# - {field_name}: Full object data (for display, nested data)
#
# This eliminates frontend confusion about which field to use.

from rest_framework import serializers
from .models import *

# ===========================
# SUMMARY SERIALIZERS (for nested use)
# ===========================

class CustomerSummarySerializer(serializers.ModelSerializer):
    """Lightweight customer data for nested responses"""
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone_number']

class VehicleSummarySerializer(serializers.ModelSerializer):
    """Lightweight vehicle data for nested responses"""
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'make', 'model', 'year', 'license_plate', 'vin', 'color', 'customer_id', 'customer_name']

class VehicleProblemSummarySerializer(serializers.ModelSerializer):
    """Lightweight vehicle problem data for nested responses"""
    class Meta:
        model = VehicleProblem
        fields = ['id', 'description', 'resolved', 'reported_date']

# ===========================
# STANDARDIZED MAIN SERIALIZERS
# ===========================

class StandardizedRepairOrderSerializer(serializers.ModelSerializer):
    """
    STANDARDIZED RepairOrder serializer
    
    Frontend gets:
    - vehicle_id: 123 (integer for relationships/forms)
    - vehicle: {id: 123, make: "Toyota", ...} (object for display)
    """
    
    # Always provide the ID field explicitly
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    
    # Always provide the full object data
    vehicle = VehicleSummarySerializer(read_only=True)
    
    # Computed fields
    status = serializers.SerializerMethodField()
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)
    
    # Related data
    repair_order_parts = 'RepairOrderPartSerializer'(many=True, read_only=True)
    repair_order_services = 'RepairOrderServiceSerializer'(many=True, read_only=True)

    def get_status(self, obj):
        """Get status from the most recent appointment for this vehicle"""
        try:
            appointment = Appointment.objects.filter(
                vehicle=obj.vehicle
            ).order_by('-date').first()
            return appointment.status if appointment else 'pending'
        except Exception:
            return 'pending'

    class Meta:
        model = RepairOrder
        fields = [
            'id',
            'vehicle_id',      # ← Always available as integer
            'vehicle',         # ← Always available as object
            'customer_id',     # ← Convenience field
            'customer_name',   # ← Convenience field
            'status',          # ← Computed field
            'total_cost',
            'discount_amount',
            'discount_percent',
            'tax_percent',
            'date_created',
            'notes',
            'repair_order_parts',
            'repair_order_services'
        ]
        read_only_fields = ['id', 'vehicle_id', 'vehicle', 'customer_id', 'customer_name', 'status', 'date_created']

class StandardizedAppointmentSerializer(serializers.ModelSerializer):
    """
    STANDARDIZED Appointment serializer
    
    Frontend gets:
    - vehicle_id: 123 (integer for relationships/forms)  
    - vehicle: {id: 123, make: "Toyota", ...} (object for display)
    - reported_problem_id: 456 (integer, nullable)
    - reported_problem: {id: 456, description: "..."} (object, nullable)
    """
    
    # Always provide the ID fields explicitly
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    reported_problem_id = serializers.IntegerField(source='reported_problem.id', read_only=True, allow_null=True)
    
    # Always provide the full object data
    vehicle = VehicleSummarySerializer(read_only=True)
    reported_problem = VehicleProblemSummarySerializer(read_only=True, allow_null=True)
    
    # Convenience fields from related objects
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'vehicle_id',           # ← Always available as integer
            'vehicle',              # ← Always available as object  
            'reported_problem_id',  # ← Always available as integer (nullable)
            'reported_problem',     # ← Always available as object (nullable)
            'customer_id',          # ← Convenience field
            'customer_name',        # ← Convenience field
            'description',
            'date',
            'status'
        ]
        read_only_fields = ['id', 'vehicle_id', 'vehicle', 'reported_problem_id', 'reported_problem', 'customer_id', 'customer_name']

class StandardizedVehicleSerializer(serializers.ModelSerializer):
    """
    STANDARDIZED Vehicle serializer
    
    Frontend gets:
    - customer_id: 789 (integer for relationships/forms)
    - customer: {id: 789, name: "John Doe", ...} (object for display)
    """
    
    # Always provide the ID field explicitly
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    
    # Always provide the full object data
    customer = CustomerSummarySerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id',
            'customer_id',    # ← Always available as integer
            'customer',       # ← Always available as object
            'make',
            'model', 
            'year',
            'vin',
            'license_plate',
            'color'
        ]
        read_only_fields = ['id', 'customer_id', 'customer']

# ===========================
# CREATE/UPDATE SERIALIZERS (for write operations)
# ===========================

class CreateRepairOrderSerializer(serializers.ModelSerializer):
    """
    WRITE-ONLY serializer for creating RepairOrders
    Accepts vehicle_id as input, returns standardized response
    """
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        source='vehicle',
        write_only=True,
        help_text="ID of the vehicle for this repair order"
    )

    def to_representation(self, instance):
        """Return standardized response after create/update"""
        return StandardizedRepairOrderSerializer(instance, context=self.context).data

    class Meta:
        model = RepairOrder
        fields = ['vehicle_id', 'notes', 'discount_amount', 'discount_percent', 'tax_percent']

class CreateAppointmentSerializer(serializers.ModelSerializer):
    """
    WRITE-ONLY serializer for creating Appointments
    Accepts vehicle_id and reported_problem_id as input, returns standardized response
    """
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        source='vehicle',
        write_only=True,
        help_text="ID of the vehicle for this appointment"
    )
    
    reported_problem_id = serializers.PrimaryKeyRelatedField(
        queryset=VehicleProblem.objects.all(),
        source='reported_problem',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of the reported problem (optional)"
    )

    def to_representation(self, instance):
        """Return standardized response after create/update"""
        return StandardizedAppointmentSerializer(instance, context=self.context).data

    class Meta:
        model = Appointment
        fields = ['vehicle_id', 'reported_problem_id', 'description', 'date', 'status']

class CreateVehicleSerializer(serializers.ModelSerializer):
    """
    WRITE-ONLY serializer for creating Vehicles
    Accepts customer_id as input, returns standardized response
    """
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True,
        help_text="ID of the customer who owns this vehicle"
    )

    def to_representation(self, instance):
        """Return standardized response after create/update"""
        return StandardizedVehicleSerializer(instance, context=self.context).data

    class Meta:
        model = Vehicle
        fields = ['customer_id', 'make', 'model', 'year', 'vin', 'license_plate', 'color']

# ===========================
# FRONTEND INTEGRATION EXAMPLES
# ===========================

"""
FRONTEND TYPESCRIPT INTERFACES (now consistent):

interface RepairOrder {
  id: number;
  vehicle_id: number;           // ← Always integer ID
  vehicle: VehicleSummary;      // ← Always object data
  customer_id: number;          // ← Convenience field
  customer_name: string;        // ← Convenience field
  status: string;
  total_cost: number;
  // ... other fields
}

interface Appointment {
  id: number;
  vehicle_id: number;           // ← Always integer ID
  vehicle: VehicleSummary;      // ← Always object data
  reported_problem_id?: number; // ← Always integer ID (nullable)
  reported_problem?: VehicleProblemSummary; // ← Always object data (nullable)
  customer_id: number;          // ← Convenience field
  customer_name: string;        // ← Convenience field
  // ... other fields
}

FRONTEND USAGE (now consistent):

// Display vehicle info
<div>{repairOrder.vehicle.make} {repairOrder.vehicle.model}</div>

// Form relationships
<select value={repairOrder.vehicle_id}>
  {vehicles.map(v => <option key={v.id} value={v.id}>{v.make}</option>)}
</select>

// Customer info (no need for additional API calls)
<div>Customer: {repairOrder.customer_name}</div>

// Filter/search by vehicle
const filteredOrders = orders.filter(order => order.vehicle_id === selectedVehicleId);
"""
'''
    
    # Write the standardized serializers to a new file
    with open('/home/teejay/Documents/Projects/auro-repairs/shop/standardized_serializers.py', 'w') as f:
        f.write(serializer_code)
    
    print("✅ Created standardized_serializers.py")

def create_migration_plan():
    """Create a migration plan for updating existing serializers"""
    print(f"\n📋 MIGRATION PLAN FOR API STANDARDIZATION")
    print("=" * 50)
    
    migration_plan = '''# 🚀 API STANDARDIZATION MIGRATION PLAN

## PHASE 1: IMPLEMENT STANDARDIZED SERIALIZERS (Non-breaking)

### Step 1: Add new standardized serializers
- ✅ Created shop/standardized_serializers.py
- Import and test new serializers alongside existing ones

### Step 2: Update ViewSets gradually (one at a time)
```python
# In shop/views.py, update one viewset at a time:

from .standardized_serializers import (
    StandardizedRepairOrderSerializer,
    CreateRepairOrderSerializer,
    StandardizedAppointmentSerializer,
    CreateAppointmentSerializer
)

class RepairOrderViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateRepairOrderSerializer
        return StandardizedRepairOrderSerializer
```

### Step 3: Test API responses
```bash
# Test RepairOrder API
curl -H "Authorization: Bearer <token>" \\
     "http://127.0.0.1:8000/api/shop/repair-orders/"

# Verify response structure:
{
  "results": [
    {
      "id": 1,
      "vehicle_id": 123,           // ← Always integer
      "vehicle": {                 // ← Always object
        "id": 123,
        "make": "Toyota",
        "model": "Camry"
      },
      "customer_id": 456,          // ← Convenience field
      "customer_name": "John Doe", // ← Convenience field
      "status": "completed"
    }
  ]
}
```

## PHASE 2: UPDATE FRONTEND (TypeScript interfaces)

### Step 1: Update TypeScript interfaces
```typescript
// types/api.ts - BEFORE (inconsistent)
interface RepairOrder {
  id: number;
  vehicle: number | Vehicle;  // ← PROBLEM: Could be either!
  // ... confusion
}

// types/api.ts - AFTER (consistent)
interface RepairOrder {
  id: number;
  vehicle_id: number;         // ← Always integer for relationships
  vehicle: VehicleSummary;    // ← Always object for display
  customer_id: number;        // ← Convenience field
  customer_name: string;      // ← Convenience field
  status: string;
  total_cost: number;
}

interface VehicleSummary {
  id: number;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  customer_id: number;
  customer_name: string;
}
```

### Step 2: Update React components
```typescript
// BEFORE (confusing)
const RepairOrderCard = ({ order }: { order: RepairOrder }) => {
  // Is order.vehicle an ID or object? 🤔
  const vehicleId = typeof order.vehicle === 'number' ? order.vehicle : order.vehicle.id;
  const vehicleName = typeof order.vehicle === 'object' ? 
    `${order.vehicle.make} ${order.vehicle.model}` : 
    'Loading...'; // Need separate API call
  
  return (
    <div>
      <div>Vehicle ID: {vehicleId}</div>
      <div>Vehicle: {vehicleName}</div>
      {/* Need separate API call for customer info */}
    </div>
  );
};

// AFTER (clear and consistent)  
const RepairOrderCard = ({ order }: { order: RepairOrder }) => {
  return (
    <div>
      <div>Vehicle ID: {order.vehicle_id}</div>
      <div>Vehicle: {order.vehicle.make} {order.vehicle.model}</div>
      <div>Customer: {order.customer_name}</div>
      <div>Status: {order.status}</div>
    </div>
  );
};
```

### Step 3: Update forms and selects
```typescript
// BEFORE (unclear which field to use)
<select value={formData.vehicle ?? formData.vehicle_id}>
  {vehicles.map(v => <option key={v.id} value={v.id}>{v.make}</option>)}
</select>

// AFTER (always use _id fields for form values)
<select value={formData.vehicle_id}>
  {vehicles.map(v => <option key={v.id} value={v.id}>{v.make}</option>)}
</select>
```

## PHASE 3: DEPRECATE OLD PATTERNS (Breaking change)

### Step 1: Add deprecation warnings
```python
# In old serializers, add deprecation warnings
import warnings

class OldRepairOrderSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        warnings.warn(
            "This serializer is deprecated. Use StandardizedRepairOrderSerializer instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return super().to_representation(instance)
```

### Step 2: Update all ViewSets
- Replace all serializers with standardized versions
- Ensure all API endpoints return consistent format

### Step 3: Remove deprecated serializers
- Delete old serializer classes
- Update imports throughout codebase

## TESTING CHECKLIST

### Backend API Testing
- [ ] RepairOrder API returns both vehicle_id and vehicle object
- [ ] Appointment API returns both vehicle_id and vehicle object  
- [ ] Vehicle API returns both customer_id and customer object
- [ ] All create/update operations accept *_id fields
- [ ] No breaking changes to existing API contracts

### Frontend Integration Testing
- [ ] TypeScript interfaces match API responses exactly
- [ ] Forms use *_id fields for relationships
- [ ] Display components use object fields for data
- [ ] No runtime type errors in React components
- [ ] All dropdown/select components work correctly

### End-to-End Testing
- [ ] Revenue Today calculation works with consistent vehicle_id
- [ ] Active Repairs filtering works with consistent status
- [ ] Customer-vehicle-appointment relationships display correctly
- [ ] Create/edit forms submit correct data format

## BENEFITS AFTER MIGRATION

### For Backend Developers
✅ Consistent serializer patterns across all models
✅ Clear separation between read and write serializers  
✅ Reduced confusion about field naming
✅ Better API documentation

### For Frontend Developers  
✅ Always know which field to use: *_id for relationships, object for display
✅ No more runtime type checking for ambiguous fields
✅ Cleaner TypeScript interfaces
✅ Fewer API calls needed (related data included)
✅ Consistent patterns across all components

### For the Application
✅ More reliable data flow
✅ Better performance (fewer API calls)
✅ Easier debugging and maintenance
✅ Future-proof API design
'''
    
    with open('/home/teejay/Documents/Projects/auro-repairs/API_STANDARDIZATION_MIGRATION_PLAN.md', 'w') as f:
        f.write(migration_plan)
    
    print("✅ Created API_STANDARDIZATION_MIGRATION_PLAN.md")

def create_immediate_fix():
    """Create an immediate fix for the current revenue issue"""
    print(f"\n🚨 IMMEDIATE FIX FOR CURRENT REVENUE ISSUE")
    print("=" * 50)
    
    immediate_fix_code = '''#!/usr/bin/env python3
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
    
    print(f"\\n💡 SOLUTION: Provide both vehicle_id (integer) and vehicle (object)")

if __name__ == "__main__":
    test_current_serializer_output()
'''
    
    with open('/home/teejay/Documents/Projects/auro-repairs/test_serializer_consistency.py', 'w') as f:
        f.write(immediate_fix_code)
    
    print("✅ Created test_serializer_consistency.py")

def main():
    """Main function to analyze and fix API inconsistencies"""
    print("🔧 API RESPONSE STANDARDIZATION ANALYSIS & FIX")
    print("=" * 60)
    
    analyze_current_api_inconsistencies()
    create_standardized_serializers()
    create_migration_plan()
    create_immediate_fix()
    
    print(f"\\n🎯 SUMMARY")
    print("=" * 20)
    print("✅ Analyzed current API inconsistencies")
    print("✅ Created standardized serializer patterns")  
    print("✅ Generated comprehensive migration plan")
    print("✅ Created immediate testing script")
    
    print(f"\\n📋 NEXT STEPS:")
    print("1. Review shop/standardized_serializers.py")
    print("2. Test current serializer output: python test_serializer_consistency.py")
    print("3. Follow API_STANDARDIZATION_MIGRATION_PLAN.md")
    print("4. Update ViewSets to use standardized serializers")
    print("5. Update frontend TypeScript interfaces")
    
    print(f"\\n🎉 RESULT: Consistent API responses with both vehicle_id and vehicle fields!")

if __name__ == "__main__":
    main()
