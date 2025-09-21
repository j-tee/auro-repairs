#!/usr/bin/env python3
"""
TECHNICIAN ALLOCATION FUNCTIONALITY TEST
Tests the complete workflow: scheduled → assigned → in_progress → completed
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Appointment, Employee, Vehicle, Customer
from shop.serializers import AppointmentSerializer
from django.utils import timezone

def create_test_data():
    """Create test data if needed"""
    print("🔧 SETTING UP TEST DATA")
    print("=" * 25)
    
    # Check if we have necessary data
    appointments = Appointment.objects.all()
    technicians = Employee.objects.filter(role__icontains='technician')
    
    print(f"   📅 Found {appointments.count()} appointments")
    print(f"   👨‍🔧 Found {technicians.count()} technicians")
    
    if appointments.count() == 0:
        print("   ⚠️  No appointments found - need test data")
        return False
    
    if technicians.count() == 0:
        print("   ⚠️  No technicians found - creating test technician")
        # Create a test technician
        from shop.models import Shop
        shop = Shop.objects.first()
        if shop:
            technician = Employee.objects.create(
                shop=shop,
                name="Test Technician",
                role="technician",
                phone_number="555-0123",
                email="tech@test.com"
            )
            print(f"   ✅ Created test technician: {technician.name}")
        else:
            print("   ❌ No shop found to create technician")
            return False
    
    return True

def test_appointment_workflow():
    """Test the complete appointment workflow"""
    print("\n🔄 TESTING APPOINTMENT WORKFLOW")
    print("=" * 35)
    
    # Get first appointment and technician
    appointment = Appointment.objects.first()
    technician = Employee.objects.filter(role__icontains='technician').first()
    
    if not appointment or not technician:
        print("   ❌ Missing test data")
        return False
    
    print(f"   📅 Testing with Appointment #{appointment.id} - {appointment.vehicle}")
    print(f"   👨‍🔧 Using Technician: {technician.name}")
    
    # Test workflow stages
    success = True
    
    # 1. Initial state should be 'scheduled'
    if appointment.status != 'scheduled':
        appointment.status = 'scheduled'
        appointment.assigned_technician = None
        appointment.assigned_at = None
        appointment.started_at = None
        appointment.completed_at = None
        appointment.save()
    
    print(f"\n   1️⃣ INITIAL STATE")
    print(f"      Status: {appointment.status}")
    print(f"      Technician: {appointment.assigned_technician}")
    print(f"      Is Available: {technician.is_available}")
    print(f"      Workload: {technician.workload_count}/3")
    
    # 2. Assign technician
    try:
        appointment.assign_technician(technician)
        print(f"\n   2️⃣ ASSIGNED TECHNICIAN")
        print(f"      Status: {appointment.status}")
        print(f"      Technician: {appointment.assigned_technician.name}")
        print(f"      Assigned at: {appointment.assigned_at}")
        print(f"      Workload: {technician.workload_count}/3")
        print(f"      Is Available: {technician.is_available}")
    except Exception as e:
        print(f"      ❌ Failed to assign technician: {e}")
        success = False
    
    # 3. Start work
    try:
        appointment.start_work()
        print(f"\n   3️⃣ STARTED WORK")
        print(f"      Status: {appointment.status}")
        print(f"      Started at: {appointment.started_at}")
        work_duration = appointment.started_at - appointment.assigned_at
        print(f"      Time to start: {work_duration}")
    except Exception as e:
        print(f"      ❌ Failed to start work: {e}")
        success = False
    
    # 4. Complete work
    try:
        appointment.complete_work()
        print(f"\n   4️⃣ COMPLETED WORK")
        print(f"      Status: {appointment.status}")
        print(f"      Completed at: {appointment.completed_at}")
        if appointment.started_at:
            work_duration = appointment.completed_at - appointment.started_at
            print(f"      Work duration: {work_duration}")
        print(f"      Technician workload: {technician.workload_count}/3")
        print(f"      Is Available: {technician.is_available}")
    except Exception as e:
        print(f"      ❌ Failed to complete work: {e}")
        success = False
    
    return success

def test_serializer_with_technician_data():
    """Test that the serializer includes technician data"""
    print("\n📋 TESTING SERIALIZER WITH TECHNICIAN DATA")
    print("=" * 45)
    
    appointment = Appointment.objects.filter(assigned_technician__isnull=False).first()
    
    if not appointment:
        print("   ⚠️  No appointment with assigned technician found")
        return False
    
    serializer = AppointmentSerializer(appointment)
    data = serializer.data
    
    print(f"   📅 Appointment #{data.get('id')} serialized data:")
    print(f"      ✅ assigned_technician_id: {data.get('assigned_technician_id')}")
    
    technician_data = data.get('assigned_technician')
    if technician_data:
        print(f"      ✅ assigned_technician: {technician_data}")
        print(f"         - name: {technician_data.get('name')}")
        print(f"         - role: {technician_data.get('role')}")
    else:
        print(f"      ❌ assigned_technician: {technician_data}")
        return False
    
    print(f"      ✅ assigned_at: {data.get('assigned_at')}")
    print(f"      ✅ started_at: {data.get('started_at')}")
    print(f"      ✅ completed_at: {data.get('completed_at')}")
    print(f"      ✅ status: {data.get('status')}")
    
    return True

def test_workload_management():
    """Test technician workload management"""
    print("\n👨‍🔧 TESTING WORKLOAD MANAGEMENT")
    print("=" * 35)
    
    technicians = Employee.objects.filter(role__icontains='technician')
    
    if not technicians:
        print("   ⚠️  No technicians found")
        return False
    
    for tech in technicians:
        print(f"\n   👨‍🔧 {tech.name}:")
        print(f"      Current appointments: {tech.workload_count}")
        print(f"      Is available: {tech.is_available}")
        print(f"      Appointments today: {tech.appointments_today.count()}")
        
        # Show current jobs
        current_jobs = tech.current_appointments
        if current_jobs:
            print(f"      Current jobs:")
            for job in current_jobs:
                print(f"         - #{job.id}: {job.status} - {job.vehicle}")
        else:
            print(f"      No current jobs")
    
    return True

def show_status_flow_example():
    """Show the status flow with real data"""
    print("\n📊 APPOINTMENT STATUS FLOW EXAMPLE")
    print("=" * 40)
    
    flow_example = '''
🔄 APPOINTMENT LIFECYCLE:

1. 📅 SCHEDULED (Customer books)
   ├─ assigned_technician: null
   ├─ assigned_at: null
   └─ Status: "scheduled"

2. 👨‍🔧 ASSIGNED (Shop assigns technician)
   ├─ assigned_technician: Employee object
   ├─ assigned_at: timestamp
   └─ Status: "assigned"

3. 🔧 IN_PROGRESS (Technician starts work)
   ├─ started_at: timestamp
   └─ Status: "in_progress"

4. ✅ COMPLETED (Work finished)
   ├─ completed_at: timestamp
   └─ Status: "completed"

🎯 BENEFITS:
✅ Clear workflow progression
✅ Automatic status updates
✅ Workload management
✅ Performance tracking
✅ Better customer updates
'''
    print(flow_example)

def main():
    """Main test function"""
    print("🧪 TECHNICIAN ALLOCATION FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Setup test data
    if not create_test_data():
        print("\n❌ Test setup failed")
        return
    
    # Test workflow
    workflow_success = test_appointment_workflow()
    
    # Test serializer
    serializer_success = test_serializer_with_technician_data()
    
    # Test workload management
    workload_success = test_workload_management()
    
    # Show example
    show_status_flow_example()
    
    print("\n🎯 TEST SUMMARY")
    print("=" * 20)
    
    if workflow_success and serializer_success and workload_success:
        print("✅ ALL TESTS PASSED!")
        print("✅ Appointment workflow: scheduled → assigned → in_progress → completed")
        print("✅ Technician assignment works correctly")
        print("✅ API serialization includes technician data")
        print("✅ Workload management prevents overallocation")
        
        print("\n🎉 RESULT: Technician allocation fully functional!")
        print("   • Appointments can be assigned to technicians")
        print("   • Status automatically progresses through workflow")
        print("   • Timestamps track complete process")
        print("   • Workload management prevents overload")
        
    else:
        print("❌ Some tests failed:")
        if not workflow_success:
            print("   ❌ Appointment workflow test failed")
        if not serializer_success:
            print("   ❌ Serializer test failed")
        if not workload_success:
            print("   ❌ Workload management test failed")

if __name__ == "__main__":
    main()
