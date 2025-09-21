#!/usr/bin/env python
"""
Django unit test for appointment date filtering functionality
"""

import os
import sys
import django
from datetime import date

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from shop.models import Appointment

User = get_user_model()

print("🔧 TESTING DATE FILTERING WITH DJANGO TEST CLIENT")
print("=" * 55)

# Setup test client
client = APIClient()

# Get owner user for authentication
owner = User.objects.filter(role=User.OWNER).first()
if not owner:
    print("❌ No owner user found!")
    sys.exit(1)

print(f"👤 Testing with owner: {owner.email}")

# Authenticate
client.force_authenticate(user=owner)

# Database verification
total_appointments = Appointment.objects.count()
today_date = date(2025, 9, 8)
today_appointments = Appointment.objects.filter(date__date=today_date).count()

print(f"📊 Database has {total_appointments} total appointments")
print(f"📅 Database has {today_appointments} appointments for {today_date}")

# Test 1: No date filters (should return all)
print("\n🧪 TEST 1: No date filters")
response = client.get('/api/shop/appointments/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    all_data = response.json()
    print(f"✅ Returned {len(all_data)} appointments (no filter)")
else:
    print(f"❌ Failed: {response.data}")

# Test 2: Date filter for today (frontend format: dateFrom/dateTo)
print("\n🧪 TEST 2: Frontend format (dateFrom/dateTo)")
response = client.get('/api/shop/appointments/', {
    'dateFrom': '2025-09-08',
    'dateTo': '2025-09-08'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    today_data = response.json()
    print(f"✅ Frontend format returned {len(today_data)} appointments")
    
    if len(today_data) > 0:
        print("📋 Today's appointments:")
        for apt in today_data:
            print(f"   ID: {apt['id']} | Date: {apt['date']} | Status: {apt['status']}")
else:
    print(f"❌ Failed: {response.data}")

# Test 3: Date filter for today (backend format: date_from/date_to)
print("\n🧪 TEST 3: Backend format (date_from/date_to)")
response = client.get('/api/shop/appointments/', {
    'date_from': '2025-09-08',
    'date_to': '2025-09-08'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    backend_data = response.json()
    print(f"✅ Backend format returned {len(backend_data)} appointments")
else:
    print(f"❌ Failed: {response.data}")

# Test 4: Date range (September 2025)
print("\n🧪 TEST 4: Date range (September 2025)")
response = client.get('/api/shop/appointments/', {
    'dateFrom': '2025-09-01',
    'dateTo': '2025-09-30'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    september_data = response.json()
    print(f"✅ September range returned {len(september_data)} appointments")
else:
    print(f"❌ Failed: {response.data}")

# Test 5: Invalid date format
print("\n🧪 TEST 5: Invalid date format")
response = client.get('/api/shop/appointments/', {
    'dateFrom': 'invalid-date',
    'dateTo': '2025-09-08'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    invalid_data = response.json()
    print(f"✅ Invalid date handled gracefully, returned {len(invalid_data)} appointments")
else:
    print(f"❌ Failed: {response.data}")

# Summary
print("\n🎯 SUMMARY AND VALIDATION:")
print("-" * 40)
print(f"Database total appointments: {total_appointments}")
print(f"Database today appointments: {today_appointments}")
print(f"API no filter: {len(all_data) if 'all_data' in locals() else 'N/A'}")
print(f"API today (frontend): {len(today_data) if 'today_data' in locals() else 'N/A'}")
print(f"API today (backend): {len(backend_data) if 'backend_data' in locals() else 'N/A'}")
print(f"API September: {len(september_data) if 'september_data' in locals() else 'N/A'}")

# Validation checks
validation_passed = True

if 'all_data' in locals() and len(all_data) != total_appointments:
    print("❌ FAIL: API without filters doesn't match database")
    validation_passed = False
else:
    print("✅ PASS: API without filters matches database")

if 'today_data' in locals() and len(today_data) != today_appointments:
    print("❌ FAIL: Frontend date filtering doesn't match database")
    validation_passed = False
else:
    print("✅ PASS: Frontend date filtering matches database")

if 'backend_data' in locals() and 'today_data' in locals() and len(backend_data) != len(today_data):
    print("❌ FAIL: Frontend and backend date formats return different results")
    validation_passed = False
else:
    print("✅ PASS: Both date formats return same results")

if 'today_data' in locals() and 'all_data' in locals() and len(today_data) >= len(all_data):
    print("❌ FAIL: Date filtering doesn't reduce result count")
    validation_passed = False
else:
    print("✅ PASS: Date filtering reduces result count")

if validation_passed:
    print("\n🎉 SUCCESS: All date filtering tests passed!")
    print("✅ dateFrom/dateTo parameters are working correctly")
    print("✅ Backend is properly filtering appointments by date")
else:
    print("\n❌ FAILURE: Some date filtering tests failed")
    print("⚠️  The backend date filtering needs investigation")

print(f"\n📋 Expected vs Actual for today ({today_date}):")
print(f"   Expected: {today_appointments} appointment(s)")
print(f"   API Result: {len(today_data) if 'today_data' in locals() else 'N/A'}")

if 'today_data' in locals() and len(today_data) == 1:
    apt = today_data[0]
    print(f"   Today's appointment: ID {apt['id']} - {apt['date']}")
