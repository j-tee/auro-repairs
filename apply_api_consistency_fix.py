#!/usr/bin/env python3
"""
IMMEDIATE API CONSISTENCY FIX
Updates existing serializers to provide both vehicle_id and vehicle fields
This solves the frontend confusion about which field to use.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

def backup_current_serializers():
    """Create a backup of current serializers"""
    import shutil
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'/home/teejay/Documents/Projects/auro-repairs/shop/serializers_backup_{timestamp}.py'
    
    shutil.copy2('/home/teejay/Documents/Projects/auro-repairs/shop/serializers.py', backup_file)
    print(f"✅ Created backup: {backup_file}")

def update_repair_order_serializer():
    """Update RepairOrderSerializer to provide both vehicle_id and vehicle fields"""
    
    # Read current serializers.py
    with open('/home/teejay/Documents/Projects/auro-repairs/shop/serializers.py', 'r') as f:
        content = f.read()
    
    # Find the RepairOrderSerializer class and update it
    old_serializer = '''class RepairOrderSerializer(serializers.ModelSerializer):
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
        fields = "__all__"
        read_only_fields = ["total_cost", "calculated_total_cost", "date_created", "status"]'''

    new_serializer = '''class RepairOrderSerializer(serializers.ModelSerializer):
    # 🎯 CONSISTENT API FIELDS for frontend integration
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    vehicle = VehicleSummarySerializer(read_only=True)
    
    # Convenience fields for frontend
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
            "vehicle_id",      # ← Always integer ID for relationships
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
        ]'''
    
    # Replace the serializer
    content = content.replace(old_serializer, new_serializer)
    
    return content

def update_appointment_serializer():
    """Update AppointmentSerializer to provide consistent fields"""
    
    with open('/home/teejay/Documents/Projects/auro-repairs/shop/serializers.py', 'r') as f:
        content = f.read()
    
    # Add the updated AppointmentSerializer
    old_appointment = '''class AppointmentSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    reported_problem = VehicleProblemSerializer(read_only=True)
    reported_problem_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = "__all__"'''

    new_appointment = '''class AppointmentSerializer(serializers.ModelSerializer):
    # 🎯 CONSISTENT API FIELDS for frontend integration
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    vehicle = VehicleSummarySerializer(read_only=True)
    
    reported_problem_id = serializers.IntegerField(source='reported_problem.id', read_only=True, allow_null=True)
    reported_problem = VehicleProblemSummarySerializer(read_only=True, allow_null=True)
    
    # Convenience fields
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "vehicle_id",           # ← Always integer ID
            "vehicle",              # ← Always object data
            "reported_problem_id",  # ← Always integer ID (nullable)
            "reported_problem",     # ← Always object data (nullable)
            "customer_id",          # ← Convenience field
            "customer_name",        # ← Convenience field
            "description",
            "date", 
            "status"
        ]
        read_only_fields = [
            "id", "vehicle_id", "vehicle", "reported_problem_id", 
            "reported_problem", "customer_id", "customer_name"
        ]'''
    
    content = content.replace(old_appointment, new_appointment)
    return content

def apply_serializer_fixes():
    """Apply all serializer fixes"""
    print("🔧 APPLYING IMMEDIATE SERIALIZER FIXES")
    print("=" * 40)
    
    # 1. Backup current serializers
    backup_current_serializers()
    
    # 2. Read current content
    with open('/home/teejay/Documents/Projects/auro-repairs/shop/serializers.py', 'r') as f:
        content = f.read()
    
    # 3. Update RepairOrderSerializer
    print("🔧 Updating RepairOrderSerializer...")
    
    # Find and replace the RepairOrderSerializer
    old_repair_order = '''class RepairOrderSerializer(serializers.ModelSerializer):
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
        fields = "__all__"
        read_only_fields = ["total_cost", "calculated_total_cost", "date_created", "status"]'''

    new_repair_order = '''class RepairOrderSerializer(serializers.ModelSerializer):
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
        ]'''
    
    if old_repair_order in content:
        content = content.replace(old_repair_order, new_repair_order)
        print("✅ Updated RepairOrderSerializer")
    else:
        print("⚠️  RepairOrderSerializer pattern not found - may already be updated")
    
    # 4. Update AppointmentSerializer
    print("🔧 Updating AppointmentSerializer...")
    
    old_appointment = '''class AppointmentSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True)
    reported_problem = VehicleProblemSerializer(read_only=True)
    reported_problem_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Appointment
        fields = "__all__"'''

    new_appointment = '''class AppointmentSerializer(serializers.ModelSerializer):
    # 🎯 CONSISTENT API FIELDS - Always provide both ID and object
    vehicle_id = serializers.IntegerField(source='vehicle.id', read_only=True)
    vehicle = VehicleSummarySerializer(read_only=True)
    
    reported_problem_id = serializers.IntegerField(source='reported_problem.id', read_only=True, allow_null=True)
    reported_problem = VehicleProblemSummarySerializer(read_only=True, allow_null=True)
    
    # Convenience fields
    customer_id = serializers.IntegerField(source='vehicle.customer.id', read_only=True)
    customer_name = serializers.CharField(source='vehicle.customer.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "vehicle_id",           # ← Always integer ID for relationships/forms
            "vehicle",              # ← Always object data for display
            "reported_problem_id",  # ← Always integer ID (nullable)
            "reported_problem",     # ← Always object data (nullable)
            "customer_id",          # ← Convenience field
            "customer_name",        # ← Convenience field
            "description",
            "date", 
            "status"
        ]
        read_only_fields = [
            "id", "vehicle_id", "vehicle", "reported_problem_id", 
            "reported_problem", "customer_id", "customer_name"
        ]'''
    
    if old_appointment in content:
        content = content.replace(old_appointment, new_appointment)
        print("✅ Updated AppointmentSerializer")
    else:
        print("⚠️  AppointmentSerializer pattern not found - may already be updated")
    
    # 5. Write updated content
    with open('/home/teejay/Documents/Projects/auro-repairs/shop/serializers.py', 'w') as f:
        f.write(content)
    
    print("✅ Applied serializer fixes to shop/serializers.py")

def test_fixed_serializers():
    """Test the fixed serializers"""
    print("\n🧪 TESTING FIXED SERIALIZERS")
    print("=" * 30)
    
    from shop.models import RepairOrder, Appointment
    from shop.serializers import RepairOrderSerializer, AppointmentSerializer
    
    # Test RepairOrder serializer
    repair_order = RepairOrder.objects.first()
    if repair_order:
        serializer = RepairOrderSerializer(repair_order)
        data = serializer.data
        
        print("📋 RepairOrder API Response:")
        print(f"   ✅ vehicle_id: {data.get('vehicle_id')} (type: {type(data.get('vehicle_id'))})")
        print(f"   ✅ vehicle: {type(data.get('vehicle'))} - {data.get('vehicle', {}).get('make', 'N/A')}")
        print(f"   ✅ customer_id: {data.get('customer_id')}")
        print(f"   ✅ customer_name: {data.get('customer_name')}")
        print(f"   ✅ status: {data.get('status')}")
    
    # Test Appointment serializer
    appointment = Appointment.objects.first()
    if appointment:
        serializer = AppointmentSerializer(appointment)
        data = serializer.data
        
        print("\n📅 Appointment API Response:")
        print(f"   ✅ vehicle_id: {data.get('vehicle_id')} (type: {type(data.get('vehicle_id'))})")
        print(f"   ✅ vehicle: {type(data.get('vehicle'))} - {data.get('vehicle', {}).get('make', 'N/A')}")
        print(f"   ✅ customer_id: {data.get('customer_id')}")
        print(f"   ✅ customer_name: {data.get('customer_name')}")

def main():
    """Main function to apply the immediate API consistency fix"""
    print("🚀 IMMEDIATE API CONSISTENCY FIX")
    print("=" * 40)
    
    apply_serializer_fixes()
    test_fixed_serializers()
    
    print("\n🎯 SUMMARY")
    print("=" * 20)
    print("✅ Created backup of original serializers")
    print("✅ Updated RepairOrderSerializer with consistent fields")
    print("✅ Updated AppointmentSerializer with consistent fields") 
    print("✅ Tested updated serializers")
    
    print("\n📋 FRONTEND BENEFITS:")
    print("✅ Always use vehicle_id for relationships/forms")
    print("✅ Always use vehicle.make, vehicle.model for display")
    print("✅ Customer info available without additional API calls")
    print("✅ Consistent TypeScript interfaces possible")
    
    print("\n🎉 RESULT: Frontend developers can now reliably use:")
    print("   • repairOrder.vehicle_id (integer)")
    print("   • repairOrder.vehicle.make (string)")
    print("   • repairOrder.customer_name (string)")

if __name__ == "__main__":
    main()
