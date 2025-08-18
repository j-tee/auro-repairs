from rest_framework import serializers
from .models import (
    Shop, Service, Part, Employee, Customer,
    Appointment, RepairOrder, RepairOrderService, RepairOrderPart
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
        fields = '__all__'
        read_only_fields = ['total_cost', 'created_at']


# ------------------------
# SERVICE
# ------------------------
class ServiceSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = '__all__'


# ------------------------
# EMPLOYEE
# ------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


# ------------------------
# CUSTOMER
# ------------------------
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


# ------------------------
# APPOINTMENT
# ------------------------
class AppointmentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


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
        fields = '__all__'
        read_only_fields = ['total_price']


# ------------------------
# REPAIR ORDER SERVICE
# ------------------------
class RepairOrderServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = RepairOrderService
        fields = '__all__'


# ------------------------
# REPAIR ORDER
# ------------------------
class RepairOrderSerializer(serializers.ModelSerializer):
    repair_order_parts = RepairOrderPartSerializer(many=True, read_only=True)
    repair_order_services = RepairOrderServiceSerializer(many=True, read_only=True)
    calculated_total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source='calculate_total_cost'
    )

    class Meta:
        model = RepairOrder
        fields = '__all__'
        read_only_fields = ['total_cost', 'calculated_total_cost', 'date_created']


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
        fields = '__all__'
        read_only_fields = ['created_at']
        read_only_fields = ['created_at', 'services', 'parts', 'employees', 'customers', 'appointments', 'repair_orders']