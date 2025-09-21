#!/usr/bin/env python
"""
Direct API test to verify appointment date filtering using HTTP calls
"""

import os
import sys
import django
import json
import requests
from datetime import date

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Appointment

User = get_user_model()

print("🔧 TESTING DATE FILTERING VIA API")
print("=" * 50)

# API base URL - adjust if different
BASE_URL = "http://127.0.0.1:8001"

# Get owner user for login
owner = User.objects.filter(role=User.OWNER).first()
if not owner:
    print("❌ No owner user found for testing!")
    sys.exit(1)

print(f"👤 Testing with owner: {owner.email}")

# Step 1: Login to get token
print("\n🔐 Step 1: Authenticating...")
login_data = {
    "email": owner.email,
    "password": "password123"  # Default password from seed data
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        print("✅ Authentication successful")
    else:
        print(f"❌ Authentication failed: {response.status_code} - {response.text}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to API server. Is it running on port 8000?")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 2: Test the appointments endpoint
print("\n📊 Step 2: Database verification...")
total_appointments = Appointment.objects.count()
print(f"Total appointments in database: {total_appointments}")

today_date = date(2025, 9, 8)
today_appointments = Appointment.objects.filter(date__date=today_date)
print(f"Appointments for {today_date}: {today_appointments.count()}")

# Step 3: Test API without filters
print("\n🧪 Step 3: Testing API without filters...")
try:
    response = requests.get(f"{BASE_URL}/api/shop/appointments/", headers=headers)
    if response.status_code == 200:
        all_appointments = response.json()
        print(f"✅ API returned {len(all_appointments)} appointments (no filter)")
    else:
        print(f"❌ API call failed: {response.status_code} - {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ API request error: {e}")
    sys.exit(1)

# Step 4: Test API with date filters (frontend format)
print("\n🧪 Step 4: Testing dateFrom/dateTo filters...")
try:
    params = {
        "dateFrom": "2025-09-08",
        "dateTo": "2025-09-08"
    }
    response = requests.get(f"{BASE_URL}/api/shop/appointments/", headers=headers, params=params)
    if response.status_code == 200:
        filtered_appointments = response.json()
        print(f"✅ API with dateFrom/dateTo returned {len(filtered_appointments)} appointments")
        
        if len(filtered_appointments) > 0:
            print("📋 Filtered appointments:")
            for apt in filtered_appointments[:5]:  # Show first 5
                print(f"   ID: {apt['id']} | Date: {apt['date']} | Status: {apt['status']}")
        else:
            print("⚠️  No appointments found for today")
    else:
        print(f"❌ Filtered API call failed: {response.status_code} - {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Filtered API request error: {e}")
    sys.exit(1)

# Step 5: Test API with date range
print("\n🧪 Step 5: Testing date range (September 2025)...")
try:
    params = {
        "dateFrom": "2025-09-01",
        "dateTo": "2025-09-30"
    }
    response = requests.get(f"{BASE_URL}/api/shop/appointments/", headers=headers, params=params)
    if response.status_code == 200:
        september_appointments = response.json()
        print(f"✅ September range returned {len(september_appointments)} appointments")
    else:
        print(f"❌ September range API call failed: {response.status_code}")
except Exception as e:
    print(f"❌ September range API request error: {e}")

# Step 6: Test invalid date format
print("\n🧪 Step 6: Testing invalid date format...")
try:
    params = {
        "dateFrom": "invalid-date",
        "dateTo": "2025-09-08"
    }
    response = requests.get(f"{BASE_URL}/api/shop/appointments/", headers=headers, params=params)
    if response.status_code == 200:
        invalid_date_appointments = response.json()
        print(f"✅ Invalid date handled gracefully, returned {len(invalid_date_appointments)} appointments")
    else:
        print(f"❌ Invalid date API call failed: {response.status_code}")
except Exception as e:
    print(f"❌ Invalid date API request error: {e}")

# Summary
print("\n🎯 CONCLUSION:")
print("-" * 40)
print(f"Database total: {total_appointments}")
print(f"Database today: {today_appointments.count()}")
print(f"API no filter: {len(all_appointments)}")
print(f"API today filter: {len(filtered_appointments)}")
print(f"API September: {len(september_appointments)}")

if len(all_appointments) == total_appointments:
    print("✅ API without filters matches database")
else:
    print("❌ API without filters doesn't match database")

if len(filtered_appointments) == today_appointments.count():
    print("✅ Date filtering is working correctly!")
else:
    print("❌ Date filtering is not working correctly")

if len(filtered_appointments) < len(all_appointments):
    print("✅ Filtering reduces result count (good)")
else:
    print("❌ Filtering doesn't reduce result count (bad)")

# Show actual appointment dates
print(f"\n📅 Appointment dates in database:")
for apt in Appointment.objects.all().order_by('-date')[:10]:
    is_today = apt.date.date() == today_date
    print(f"   ID: {apt.id:2d} | Date: {apt.date.date()} | Today: {'✓' if is_today else '✗'}")
