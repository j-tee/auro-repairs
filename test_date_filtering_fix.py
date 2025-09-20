#!/usr/bin/env python
"""
Test script to verify appointment date filtering is working correctly
after the dateFrom/dateTo parameter fix.
"""

import os
import sys
import django
from datetime import date, datetime

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from shop.views import AppointmentViewSet
from shop.models import Appointment
from django.utils import timezone

User = get_user_model()

print("🔧 TESTING DATE FILTERING FIX")
print("=" * 50)

# Create a DRF API request factory
factory = APIRequestFactory()

# Get an owner user for testing
owner = User.objects.filter(role=User.OWNER).first()
if not owner:
    print("❌ No owner user found for testing!")
    sys.exit(1)

print(f"👤 Testing with owner user: {owner.email}")

# Check total appointments first
total_appointments = Appointment.objects.count()
print(f"📊 Total appointments in database: {total_appointments}")

# Test today's date (September 8, 2025)
today = "2025-09-08"
print(f"📅 Testing date filter for: {today}")

# Test 1: Frontend format (dateFrom/dateTo)
print("\n🧪 TEST 1: Frontend format (dateFrom/dateTo)")
request = factory.get(f'/api/shop/appointments/?dateFrom={today}&dateTo={today}')
force_authenticate(request, user=owner)

viewset = AppointmentViewSet()
viewset.request = request
viewset.format_kwarg = None
queryset = viewset.get_queryset()

print(f"✅ Query parameters: dateFrom={today}&dateTo={today}")
print(f"📈 Filtered result count: {queryset.count()}")

if queryset.count() > 0:
    print("📋 Filtered appointments:")
    for apt in queryset:
        print(f"   ID: {apt.id} | Date: {apt.date} | Status: {apt.status}")
else:
    print("⚠️  No appointments found for this date")

# Test 2: Backend format (date_from/date_to) - for backward compatibility
print("\n🧪 TEST 2: Backend format (date_from/date_to)")
request2 = factory.get(f'/api/shop/appointments/?date_from={today}&date_to={today}')
force_authenticate(request2, user=owner)

viewset2 = AppointmentViewSet()
viewset2.request = request2
viewset2.format_kwarg = None
queryset2 = viewset2.get_queryset()

print(f"✅ Query parameters: date_from={today}&date_to={today}")
print(f"📈 Filtered result count: {queryset2.count()}")

# Test 3: No date filters (should return all)
print("\n🧪 TEST 3: No date filters (should return all)")
request3 = factory.get('/api/shop/appointments/')
force_authenticate(request3, user=owner)

viewset3 = AppointmentViewSet()
viewset3.request = request3
viewset3.format_kwarg = None
queryset3 = viewset3.get_queryset()

print(f"✅ Query parameters: (none)")
print(f"📈 Filtered result count: {queryset3.count()}")

# Test 4: Date range filtering
print("\n🧪 TEST 4: Date range filtering (September 2025)")
request4 = factory.get('/api/shop/appointments/?dateFrom=2025-09-01&dateTo=2025-09-30')
force_authenticate(request4, user=owner)

viewset4 = AppointmentViewSet()
viewset4.request = request4
viewset4.format_kwarg = None
queryset4 = viewset4.get_queryset()

print(f"✅ Query parameters: dateFrom=2025-09-01&dateTo=2025-09-30")
print(f"📈 Filtered result count: {queryset4.count()}")

# Test 5: Invalid date format
print("\n🧪 TEST 5: Invalid date format handling")
request5 = factory.get('/api/shop/appointments/?dateFrom=invalid-date&dateTo=2025-09-08')
force_authenticate(request5, user=owner)

viewset5 = AppointmentViewSet()
viewset5.request = request5
viewset5.format_kwarg = None
queryset5 = viewset5.get_queryset()

print(f"✅ Query parameters: dateFrom=invalid-date&dateTo=2025-09-08")
print(f"📈 Filtered result count: {queryset5.count()}")

# Summary
print("\n🎯 CONCLUSION:")
print("-" * 30)
if queryset.count() == queryset2.count():
    print("✅ Both parameter formats return same results (good!)")
else:
    print("❌ Parameter formats return different results (problem!)")

if queryset3.count() == total_appointments:
    print("✅ No filters returns all appointments (good!)")
else:
    print("❌ No filters doesn't return all appointments (problem!)")

if queryset.count() < queryset3.count():
    print("✅ Date filtering is working (fewer results with filter)")
else:
    print("⚠️  Date filtering may not be working (same count as unfiltered)")

print(f"\n📊 Final Results:")
print(f"   Today only (frontend format): {queryset.count()}")
print(f"   Today only (backend format): {queryset2.count()}")
print(f"   September range: {queryset4.count()}")
print(f"   All appointments: {queryset3.count()}")
print(f"   Invalid date test: {queryset5.count()}")

# Check for today's appointment specifically
today_date = date(2025, 9, 8)
direct_query = Appointment.objects.filter(date__date=today_date)
print(f"   Direct DB query for {today_date}: {direct_query.count()}")

if queryset.count() == direct_query.count():
    print("🎉 SUCCESS: API filtering matches direct database query!")
else:
    print("❌ MISMATCH: API filtering doesn't match direct database query")

# Test with actual appointment data
print(f"\n📋 All appointments in database:")
all_appointments = Appointment.objects.all().order_by('-date')
for apt in all_appointments:
    is_today = apt.date.date() == today_date
    print(f"   ID: {apt.id:2d} | Date: {apt.date} | Today: {'✓' if is_today else '✗'} | Status: {apt.status}")
