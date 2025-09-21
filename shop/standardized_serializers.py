# 🎯 STANDARDIZED SERIALIZERS FOR CONSISTENT API RESPONSES
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
