#!/usr/bin/env python3
"""
Verify that the Active Repairs status fix is working correctly
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Appointment, RepairOrder
from shop.views import RepairOrderViewSet
from django.test import RequestFactory
from rest_framework.request import Request

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

    # Test the actual Active Repairs API endpoint
    factory = RequestFactory()
    request = factory.get('/api/repair-orders/?status=in_progress')
    request = Request(request)

    viewset = RepairOrderViewSet()
    viewset.setup(request)
    queryset = viewset.get_queryset().filter(status='in_progress')
    active_repairs_count = queryset.count()

    print(f'🎯 Active Repairs API Results:')
    print(f'  Count: {active_repairs_count}')

    if active_repairs_count > 0:
        print(f'  ✅ SUCCESS: Dashboard will now show {active_repairs_count} active repairs!')
        print(f'  📋 Active repair orders:')
        for order in queryset[:5]:  # Show first 5
            print(f'    Order {order.id}: ${order.total_cost:.2f} - Vehicle {order.vehicle_id}')
    else:
        print(f'  ❌ ISSUE: Still showing 0 active repairs')

    print()
    print('🏁 VERIFICATION COMPLETE')

if __name__ == '__main__':
    main()
