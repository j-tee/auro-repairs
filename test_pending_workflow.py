#!/usr/bin/env python3
"""
Test script to verify the pending → assigned → in_progress → completed workflow
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Appointment, Employee


def test_appointment_workflow():
    """Test the complete appointment workflow"""
    print("🔧 Testing Appointment Workflow with PENDING Status")
    print("=" * 60)
    
    # Find a pending appointment
    pending_appointment = Appointment.objects.filter(status='pending').first()
    if not pending_appointment:
        print("❌ No pending appointments found")
        return
    
    print(f"📋 Testing with Appointment #{pending_appointment.id}")
    print(f"   Initial status: {pending_appointment.status}")
    
    # Find a technician
    technician = Employee.objects.filter(role__icontains='technician').first()
    if not technician:
        print("❌ No technician found")
        return
    
    print(f"👤 Using technician: {technician.name}")
    
    # Test 1: Assignment (pending → assigned)
    print("\n1️⃣ Testing: PENDING → ASSIGNED")
    try:
        pending_appointment.assign_technician(technician)
        print(f"   ✅ Status: {pending_appointment.status}")
        print(f"   ✅ Assigned to: {pending_appointment.assigned_technician.name}")
        print(f"   ✅ Assigned at: {pending_appointment.assigned_at}")
    except Exception as e:
        print(f"   ❌ Assignment failed: {e}")
        return
    
    # Test 2: Start work (assigned → in_progress)
    print("\n2️⃣ Testing: ASSIGNED → IN_PROGRESS")
    try:
        pending_appointment.start_work()
        print(f"   ✅ Status: {pending_appointment.status}")
        print(f"   ✅ Started at: {pending_appointment.started_at}")
    except Exception as e:
        print(f"   ❌ Start work failed: {e}")
        return
    
    # Test 3: Complete work (in_progress → completed)
    print("\n3️⃣ Testing: IN_PROGRESS → COMPLETED")
    try:
        pending_appointment.complete_work()
        print(f"   ✅ Status: {pending_appointment.status}")
        print(f"   ✅ Completed at: {pending_appointment.completed_at}")
    except Exception as e:
        print(f"   ❌ Complete work failed: {e}")
        return
    
    print("\n🎉 All workflow tests passed!")
    print("\n📊 Final appointment state:")
    print(f"   ID: {pending_appointment.id}")
    print(f"   Status: {pending_appointment.status}")
    print(f"   Technician: {pending_appointment.assigned_technician.name}")
    print(f"   Assigned: {pending_appointment.assigned_at}")
    print(f"   Started: {pending_appointment.started_at}")
    print(f"   Completed: {pending_appointment.completed_at}")


def test_status_distribution():
    """Show current status distribution"""
    print("\n📈 Current Appointment Status Distribution:")
    print("-" * 50)
    
    statuses = Appointment.objects.values_list('status', flat=True).distinct()
    total = Appointment.objects.count()
    
    for status in statuses:
        count = Appointment.objects.filter(status=status).count()
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {status.upper():<12}: {count:2d} appointments ({percentage:.1f}%)")
    
    print(f"   {'TOTAL':<12}: {total:2d} appointments")


if __name__ == "__main__":
    test_status_distribution()
    test_appointment_workflow()
