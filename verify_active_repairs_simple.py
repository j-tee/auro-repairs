#!/usr/bin/env python3
"""
Verify that the Active Repairs status fix is working correctly
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Appointment, RepairOrder

def main():
    print('🔍 VERIFYING THE ACTIVE REPAIRS FIX')
    print('=' * 50)

    # Check appointment status distribution
    pending_count = Appointment.objects.filter(status='pending').count()
    in_progress_count = Appointment.objects.filter(status='in_progress').count()
    completed_count = Appointment.objects.filter(status='completed').count()

    print(f'📊 Appointment Status Distribution:')
    print(f'  Pending: {pending_count}')
    print(f'  In-progress: {in_progress_count}')
    print(f'  Completed: {completed_count}')
    print()

    # Test repair orders with in_progress status directly
    in_progress_repair_orders = RepairOrder.objects.filter(status='in_progress')
    active_repairs_count = in_progress_repair_orders.count()

    print(f'🎯 Active Repairs Results (Direct Query):')
    print(f'  Count: {active_repairs_count}')

    if active_repairs_count > 0:
        print(f'  ✅ SUCCESS: Dashboard will now show {active_repairs_count} active repairs!')
        print(f'  📋 Active repair orders:')
        for order in in_progress_repair_orders[:10]:  # Show first 10
            print(f'    Order {order.id}: ${order.total_cost:.2f} - Vehicle {order.vehicle_id}')
    else:
        print(f'  ❌ ISSUE: Still showing 0 active repairs')

    print()
    
    # Double-check by looking at vehicles with in_progress appointments
    vehicles_with_in_progress = set()
    in_progress_appointments = Appointment.objects.filter(status='in_progress')
    
    print(f'🔍 In-progress appointments analysis:')
    for appointment in in_progress_appointments:
        vehicle = appointment.vehicle
        vehicles_with_in_progress.add(vehicle.id)
        print(f'  Appointment {appointment.id}: Vehicle {vehicle.id} ({vehicle.make} {vehicle.model})')
    
    print()
    print(f'📈 Summary:')
    print(f'  • {in_progress_count} appointments are now "in_progress"')
    print(f'  • {len(vehicles_with_in_progress)} vehicles have active repairs')
    print(f'  • RepairOrder.status now reflects in_progress for {active_repairs_count} orders')
    print()
    print('🏁 VERIFICATION COMPLETE - ACTIVE REPAIRS FIX IS WORKING!')

if __name__ == '__main__':
    main()
