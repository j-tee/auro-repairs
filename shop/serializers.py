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
    class Meta:
        model = Employee
        fields = "__all__"


# ------------------------
# CUSTOMER
# ------------------------
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


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


# ------------------------
# APPOINTMENT
# ------------------------
class AppointmentSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    reported_problem = VehicleProblemSerializer(read_only=True)
    reported_problem_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = "__all__"


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
    repair_order_parts = RepairOrderPartSerializer(many=True, read_only=True)
    repair_order_services = RepairOrderServiceSerializer(many=True, read_only=True)
    calculated_total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="calculate_total_cost"
    )

    class Meta:
        model = RepairOrder
        fields = "__all__"
        read_only_fields = ["total_cost", "calculated_total_cost", "date_created"]


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
