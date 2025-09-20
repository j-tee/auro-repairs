#!/usr/bin/env python
"""
Direct ViewSet QuerySet Test for appointment date filtering
"""

import os
import sys
import django
from datetime import date

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Appointment
from shop.views import AppointmentViewSet
from unittest.mock import Mock

User = get_user_model()

print("🔧 DIRECT VIEWSET QUERYSET TEST")
print("=" * 40)

# Get owner user
owner = User.objects.filter(role=User.OWNER).first()
if not owner:
    print("❌ No owner user found!")
    sys.exit(1)

print(f"👤 Testing with owner: {owner.email}")

# Database verification
total_appointments = Appointment.objects.count()
today_date = date(2025, 9, 8)
today_appointments = Appointment.objects.filter(date__date=today_date).count()

print(f"📊 Database has {total_appointments} total appointments")
print(f"📅 Database has {today_appointments} appointments for {today_date}")

# Function to create mock request
def create_mock_request(query_params=None):
    request = Mock()
    request.user = owner
    request.query_params = Mock()
    request.query_params.get = lambda key, default=None: (query_params or {}).get(key, default)
    return request

# Test 1: No date filters
print("\n🧪 TEST 1: No date filters")
viewset = AppointmentViewSet()
viewset.request = create_mock_request()
queryset = viewset.get_queryset()
no_filter_count = queryset.count()
print(f"✅ No filters: {no_filter_count} appointments")

# Test 2: Frontend format (dateFrom/dateTo)
print("\n🧪 TEST 2: Frontend format (dateFrom/dateTo)")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'dateFrom': '2025-09-08',
    'dateTo': '2025-09-08'
})
queryset = viewset.get_queryset()
frontend_count = queryset.count()
print(f"✅ Frontend format: {frontend_count} appointments")

if frontend_count > 0:
    print("📋 Today's appointments (frontend):")
    for apt in queryset:
        print(f"   ID: {apt.id} | Date: {apt.date} | Status: {apt.status}")

# Test 3: Backend format (date_from/date_to)
print("\n🧪 TEST 3: Backend format (date_from/date_to)")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'date_from': '2025-09-08',
    'date_to': '2025-09-08'
})
queryset = viewset.get_queryset()
backend_count = queryset.count()
print(f"✅ Backend format: {backend_count} appointments")

# Test 4: Date range (September 2025)
print("\n🧪 TEST 4: September 2025 range")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'dateFrom': '2025-09-01',
    'dateTo': '2025-09-30'
})
queryset = viewset.get_queryset()
september_count = queryset.count()
print(f"✅ September range: {september_count} appointments")

# Test 5: Only dateFrom (from today onwards)
print("\n🧪 TEST 5: Only dateFrom (from today onwards)")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'dateFrom': '2025-09-08'
})
queryset = viewset.get_queryset()
from_today_count = queryset.count()
print(f"✅ From today onwards: {from_today_count} appointments")

# Test 6: Only dateTo (up to today)
print("\n🧪 TEST 6: Only dateTo (up to today)")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'dateTo': '2025-09-08'
})
queryset = viewset.get_queryset()
up_to_today_count = queryset.count()
print(f"✅ Up to today: {up_to_today_count} appointments")

# Test 7: Invalid date format
print("\n🧪 TEST 7: Invalid date format")
viewset = AppointmentViewSet()
viewset.request = create_mock_request({
    'dateFrom': 'invalid-date',
    'dateTo': '2025-09-08'
})
queryset = viewset.get_queryset()
invalid_date_count = queryset.count()
print(f"✅ Invalid date handled: {invalid_date_count} appointments")

# Summary and validation
print("\n🎯 SUMMARY AND VALIDATION:")
print("-" * 40)
print(f"Database total: {total_appointments}")
print(f"Database today: {today_appointments}")
print(f"No filter: {no_filter_count}")
print(f"Today (frontend): {frontend_count}")
print(f"Today (backend): {backend_count}")
print(f"September: {september_count}")
print(f"From today: {from_today_count}")
print(f"Up to today: {up_to_today_count}")

# Validation logic
print("\n📊 VALIDATION RESULTS:")
validation_passed = True

# Check 1: No filter should return all
if no_filter_count != total_appointments:
    print("❌ FAIL: No filter doesn't return all appointments")
    validation_passed = False
else:
    print("✅ PASS: No filter returns all appointments")

# Check 2: Today filter should match database
if frontend_count != today_appointments:
    print("❌ FAIL: Frontend today filter doesn't match database")
    validation_passed = False
else:
    print("✅ PASS: Frontend today filter matches database")

# Check 3: Both formats should return same result
if frontend_count != backend_count:
    print("❌ FAIL: Frontend and backend formats return different results")
    validation_passed = False
else:
    print("✅ PASS: Both date formats return same results")

# Check 4: Date filtering should reduce count
if frontend_count >= no_filter_count:
    print("❌ FAIL: Date filtering doesn't reduce result count")
    validation_passed = False
else:
    print("✅ PASS: Date filtering reduces result count")

# Check 5: September should include today's appointment
if september_count < today_appointments:
    print("❌ FAIL: September range doesn't include today's appointment")
    validation_passed = False
else:
    print("✅ PASS: September range includes today's appointment")

# Check 6: From today should include today's appointment
if from_today_count < today_appointments:
    print("❌ FAIL: 'From today' doesn't include today's appointment")
    validation_passed = False
else:
    print("✅ PASS: 'From today' includes today's appointment")

# Check 7: Up to today should include today's appointment
if up_to_today_count < today_appointments:
    print("❌ FAIL: 'Up to today' doesn't include today's appointment")  
    validation_passed = False
else:
    print("✅ PASS: 'Up to today' includes today's appointment")

# Final result
if validation_passed:
    print("\n🎉 SUCCESS: All date filtering tests passed!")
    print("✅ The dateFrom/dateTo parameters are working correctly")
    print("✅ The backend is properly filtering appointments by date")
    print("✅ Both camelCase (frontend) and snake_case (backend) formats work")
    
    print(f"\n📋 Critical Test Result:")
    print(f"   Expected today's appointments: {today_appointments}")
    print(f"   API with dateFrom/dateTo filter: {frontend_count}")
    print(f"   Result: {'✅ MATCH - FILTERING WORKS!' if frontend_count == today_appointments else '❌ MISMATCH - FILTERING BROKEN!'}")
    
else:
    print("\n❌ FAILURE: Some date filtering tests failed")
    print("⚠️  The backend date filtering implementation needs investigation")

# Show the actual appointments for verification
print(f"\n📅 Database verification - appointments for {today_date}:")
direct_today = Appointment.objects.filter(date__date=today_date)
for apt in direct_today:
    print(f"   ID: {apt.id} | Date: {apt.date} | Status: {apt.status}")

print(f"\n📅 All appointments by date:")
for apt in Appointment.objects.all().order_by('-date')[:5]:
    is_today = apt.date.date() == today_date
    print(f"   ID: {apt.id} | Date: {apt.date.date()} | {'✓ TODAY' if is_today else '✗ other'}")
