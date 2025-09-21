from rest_framework import serializers
from .models import (
    Shop,
    Service,
    Part,
    Employee,
    Customer,
    Vehicle,
    VehicleProblem,
    Appointment,
    RepairOrder,
    RepairOrderService,
    RepairOrderPart,
)


# ------------------------
# PART
# ------------------------
class PartSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Part
        fields = "__all__"
        read_only_fields = ["total_cost", "created_at"]


# ------------------------
# SERVICE
# ------------------------
class ServiceSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = "__all__"


# ------------------------
# EMPLOYEE
# ------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    # 🎯 COMPUTED PROPERTIES - Include workload data for technicians
    workload_count = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    appointments_today_count = serializers.SerializerMethodField()
    is_technician = serializers.SerializerMethodField()
    
    # Detailed workload info (optional, included only for technicians)
    current_jobs = serializers.SerializerMethodField()
    
    def get_workload_count(self, obj):
        """Number of active appointments assigned to this employee"""
        return obj.workload_count if obj.is_technician else 0
    
    def get_is_available(self, obj):
        """Whether this technician is available for new assignments"""
        return obj.is_available if obj.is_technician else None
    
    def get_appointments_today_count(self, obj):
        """Number of appointments today for this technician"""
        return obj.appointments_today.count() if obj.is_technician else 0
    
    def get_is_technician(self, obj):
        """Whether this employee is a technician"""
        return obj.is_technician
    
    def get_current_jobs(self, obj):
        """Current active appointments (only for technicians)"""
        if not obj.is_technician:
            return []
        
        current_appointments = obj.current_appointments
        return [
            {
                'appointment_id': apt.id,
                'vehicle': f"{apt.vehicle.make} {apt.vehicle.model}",
                'customer': apt.vehicle.customer.name,
                'status': apt.status,
                'date': apt.date,
                'assigned_at': apt.assigned_at,
                'started_at': apt.started_at
            } for apt in current_appointments
        ]

    class Meta:
        model = Employee
        fields = [
            # Database fields
            "id", "name", "role", "phone_number", "email", "picture", "shop", "user",
            # Computed fields
            "workload_count", "is_available", "appointments_today_count", 
            "is_technician", "current_jobs"
        ]


# ------------------------
# CUSTOMER
# ------------------------
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


# Lightweight customer serializer for nested use
class CustomerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "email", "phone_number"]


# ------------------------
# VEHICLE
# ------------------------
class VehicleSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"

    def to_representation(self, instance):
        """Customize the output to include customer name at the top level"""
        representation = super().to_representation(instance)
        if instance.customer:
            representation["customer_name"] = instance.customer.name
            representation["customer_email"] = instance.customer.email
            representation["customer_phone"] = instance.customer.phone_number
        else:
            representation["customer_name"] = "Unknown Customer"
            representation["customer_email"] = None
            representation["customer_phone"] = None
        return representation


# Lightweight vehicle serializer for nested use
class VehicleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "make", "model", "year", "license_plate", "vin", "color"]


# ------------------------
# VEHICLE PROBLEM
# ------------------------
class VehicleProblemSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VehicleProblem
        fields = "__all__"
        read_only_fields = ["reported_date"]


# Lightweight vehicle problem serializer for nested use
class VehicleProblemSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleProblem
        fields = ["id", "description", "resolved", "reported_date"]


# ------------------------
# APPOINTMENT
# ------------------------
class AppointmentSerializer(serializers.ModelSerializer):
    # 🎯 CONSISTENT API FIELDS - Always provide both ID and object
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    vehicle = VehicleSummarySerializer(read_only=True)
    
    reported_problem_id = serializers.IntegerField(source='reported_problem.id', read_only=True, allow_null=True)
    reported_problem = VehicleProblemSummarySerializer(read_only=True, allow_null=True)
    
    # 🎯 TECHNICIAN ALLOCATION FIELDS
    assigned_technician_id = serializers.IntegerField(source='assigned_technician.id', read_only=True, allow_null=True)
    assigned_technician = serializers.SerializerMethodField()
    
    # Convenience fields
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    def get_assigned_technician(self, obj):
        """Get comprehensive technician data including user_id for frontend requirements"""
        if obj.assigned_technician:
            return {
                'id': obj.assigned_technician.id,
                'name': obj.assigned_technician.name,
                'role': obj.assigned_technician.role,
                'email': obj.assigned_technician.email,
                'user_id': obj.assigned_technician.user_id if obj.assigned_technician.user else None
            }
        return None

    class Meta:
        model = Appointment
        fields = [
            "id",
            "vehicle_id",           # ← Always integer ID for relationships/forms
            "vehicle",              # ← Always object data for display
            "reported_problem_id",  # ← Always integer ID (nullable)
            "reported_problem",     # ← Always object data (nullable)
            "assigned_technician_id",  # ← Technician ID for assignments
            "assigned_technician",     # ← Technician object data
            "customer_id",          # ← Convenience field
            "customer_name",        # ← Convenience field
            "description",
            "date", 
            "status",
            "assigned_at",          # ← When technician was assigned
            "started_at",           # ← When work began
            "completed_at"          # ← When work finished
        ]
        read_only_fields = [
            "id", "vehicle_id", "vehicle", "reported_problem_id", 
            "reported_problem", "assigned_technician_id", "assigned_technician",
            "customer_id", "customer_name", "assigned_at", "started_at", "completed_at"
        ]


# Enhanced appointment serializer with related data optimized for frontend
class AppointmentDetailSerializer(serializers.ModelSerializer):
    # Add customer info derived from vehicle relationship
    customer_id = serializers.IntegerField(source="vehicle.customer.id", read_only=True)
    customer = CustomerSummarySerializer(source="vehicle.customer", read_only=True)

    # Vehicle summary info
    vehicle = VehicleSummarySerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)

    # Reported problem summary
    reported_problem = VehicleProblemSummarySerializer(read_only=True)
    reported_problem_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "description",
            "date",
            "status",
            "customer_id",
            "customer",
            "vehicle_id",
            "vehicle",
            "reported_problem_id",
            "reported_problem",
        ]


# ------------------------
# REPAIR ORDER PART
# ------------------------
class RepairOrderPartSerializer(serializers.ModelSerializer):
    part = PartSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = RepairOrderPart
        fields = "__all__"
        read_only_fields = ["total_price"]


# ------------------------
# REPAIR ORDER SERVICE
# ------------------------
class RepairOrderServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = RepairOrderService
        fields = "__all__"


# ------------------------
# REPAIR ORDER
# ------------------------
class RepairOrderSerializer(serializers.ModelSerializer):
    # 🎯 CONSISTENT API FIELDS - Always provide both ID and object
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    vehicle = VehicleSummarySerializer(read_only=True)
    
    # Convenience fields for frontend (no additional API calls needed)
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)
    
    # Related data
    repair_order_parts = RepairOrderPartSerializer(many=True, read_only=True)
    repair_order_services = RepairOrderServiceSerializer(many=True, read_only=True)
    calculated_total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="calculate_total_cost"
    )
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        """Get status from the most recent appointment for this vehicle"""
        try:
            # Get the most recent appointment for this vehicle
            appointment = Appointment.objects.filter(
                vehicle=obj.vehicle
            ).order_by('-date').first()
            
            if appointment:
                return appointment.status
            else:
                return 'pending'  # Default status if no appointments found
        except Exception:
            return 'pending'

    class Meta:
        model = RepairOrder
        fields = [
            "id",
            "vehicle_id",      # ← Always integer ID for relationships/forms
            "vehicle",         # ← Always object data for display
            "customer_id",     # ← Convenience field
            "customer_name",   # ← Convenience field
            "status",          # ← Computed status
            "discount_amount",
            "discount_percent", 
            "tax_percent",
            "total_cost",
            "date_created",
            "notes",
            "repair_order_parts",
            "repair_order_services",
            "calculated_total_cost"
        ]
        read_only_fields = [
            "id", "vehicle_id", "vehicle", "customer_id", "customer_name", 
            "status", "total_cost", "calculated_total_cost", "date_created"
        ]


# Backward compatible creation serializer for repair orders
class CreateRepairOrderSerializer(serializers.ModelSerializer):
    # New preferred field name (clear and consistent)
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        source='vehicle',
        required=False,
        help_text="Preferred field name for vehicle ID"
    )
    
    # Legacy field name (deprecated but supported for backward compatibility)
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        required=False,
        help_text="DEPRECATED: Use vehicle_id instead. This field will be removed in a future version."
    )
    
    def validate(self, attrs):
        """Ensure exactly one vehicle identifier is provided"""
        # Check if both fields were provided in the original input data
        vehicle_id_provided = 'vehicle_id' in self.initial_data
        vehicle_provided = 'vehicle' in self.initial_data
        
        # Ensure exactly one is provided
        if vehicle_id_provided and vehicle_provided:
            raise serializers.ValidationError(
                "Provide either 'vehicle_id' or 'vehicle', not both. "
                "Please use 'vehicle_id' as 'vehicle' is deprecated."
            )
        
        if not vehicle_id_provided and not vehicle_provided:
            raise serializers.ValidationError(
                "Either 'vehicle_id' or 'vehicle' is required. "
                "Prefer using 'vehicle_id' as 'vehicle' is deprecated."
            )
        
        # The serializer field mapping handles the rest:
        # - vehicle_id field has source='vehicle', so it automatically maps to attrs['vehicle']
        # - vehicle field maps directly to attrs['vehicle'] 
        # Both end up setting the same field, which is what we want.
        
        return attrs

    class Meta:
        model = RepairOrder
        fields = ['vehicle_id', 'vehicle', 'notes', 'discount_amount']
        read_only_fields = ['total_cost', 'date_created']


# ------------------------
# SHOP
# ------------------------
class ShopSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    parts = PartSerializer(many=True, read_only=True)
    employees = EmployeeSerializer(many=True, read_only=True)
    customers = CustomerSerializer(many=True, read_only=True)
    appointments = AppointmentSerializer(many=True, read_only=True)
    repair_orders = RepairOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = "__all__"
        read_only_fields = ["created_at"]
        read_only_fields = [
            "created_at",
            "services",
            "parts",
            "employees",
            "customers",
            "appointments",
            "repair_orders",
        ]
