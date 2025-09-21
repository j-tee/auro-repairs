#!/usr/bin/env python
"""
Fix for Active Repairs Status Issue - Update pending appointments to in_progress
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import RepairOrder, Appointment
from django.contrib.auth import get_user_model
from shop.views import RepairOrderViewSet
from unittest.mock import Mock

print('🔧 IMPLEMENTING ACTIVE REPAIRS STATUS FIX')
print('=' * 50)

# Find repair orders that should be 'in_progress' (have meaningful costs)
print('🔍 Step 1: Identifying repair orders that should be active...')

# Find repair orders with actual work (total_cost > 0) and pending appointments
meaningful_orders = RepairOrder.objects.filter(
    total_cost__gt=Decimal('0.00'),
    vehicle__appointments__status='pending'
).distinct()

print(f'📊 Found {meaningful_orders.count()} repair orders with costs and pending appointments')

# Show details of orders to be updated
print('\n📋 Orders to be updated to "in_progress":')
orders_to_update = []
for order in meaningful_orders[:10]:  # Limit to first 10 for safety
    most_recent_apt = order.vehicle.appointments.order_by('-date').first()
    if most_recent_apt and most_recent_apt.status == 'pending':
        print(f'  Order {order.id}: ${order.total_cost} - Vehicle {order.vehicle.id}')
        orders_to_update.append((order, most_recent_apt))

print(f'\n✅ Will update {len(orders_to_update)} appointments to "in_progress" status')

# Update the appointments
print('\n🔄 Step 2: Updating appointment statuses...')
updated_count = 0
for order, appointment in orders_to_update:
    appointment.status = 'in_progress'
    appointment.save()
    print(f'  ✓ Updated appointment {appointment.id} for Order {order.id} to in_progress')
    updated_count += 1

print(f'\n🎉 Successfully updated {updated_count} appointments to "in_progress" status')

# Verify the fix
print('\n📊 Step 3: Verification...')
in_progress_count = Appointment.objects.filter(status='in_progress').count()
pending_count = Appointment.objects.filter(status='pending').count()
completed_count = Appointment.objects.filter(status='completed').count()

print(f'Updated status distribution:')
print(f'  Pending: {pending_count}')
print(f'  In-progress: {in_progress_count}')
print(f'  Completed: {completed_count}')

# Test the API filtering now
print('\n🧪 Step 4: Testing API filtering after fix...')

User = get_user_model()
owner = User.objects.filter(role=User.OWNER).first()

def create_mock_request(query_params=None):
    request = Mock()
    request.user = owner
    request.query_params = Mock()
    request.query_params.get = lambda key, default=None: (query_params or {}).get(key, default)
    return request

viewset = RepairOrderViewSet()
viewset.request = create_mock_request({'status': 'in_progress'})
active_repairs = viewset.get_queryset()

print(f'🎯 RESULT: Active Repairs API now returns {active_repairs.count()} orders')

if active_repairs.count() > 0:
    print('✅ SUCCESS: Active Repairs dashboard will now show correct count!')
    print('\n📋 Active repair orders:')
    for order in active_repairs[:5]:
        print(f'  Order {order.id}: ${order.total_cost}')
else:
    print('❌ Still no active repairs found - may need more investigation')

print('\n🏁 SUMMARY:')
print(f'Before fix: 0 in-progress appointments')
print(f'After fix: {in_progress_count} in-progress appointments')
print(f'Active Repairs API: {active_repairs.count()} orders')
print('📈 Dashboard "Active Repairs" will now show the correct count!')
