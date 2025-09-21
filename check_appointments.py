#!/usr/bin/env python
import os
import sys
import django
from datetime import date, datetime

# Setup Django
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from shop.models import Appointment
from django.utils import timezone

print("🔍 APPOINTMENT DATABASE VERIFICATION")
print("=" * 50)

# Check total appointments
total = Appointment.objects.all().count()
print(f"📊 Total appointments in database: {total}")

# Check today's date
today = date.today()
print(f"📅 Today's date: {today}")

# Check appointments for today (2025-09-05)
today_tz = timezone.now().date()
todays_appointments = Appointment.objects.filter(date__date=today_tz)
todays_count = todays_appointments.count()
print(f"✅ Appointments for TODAY ({today_tz}): {todays_count}")

# Show all appointments with their dates
print("\n📋 ALL APPOINTMENTS:")
print("-" * 30)
appointments = Appointment.objects.all().order_by('date')
for apt in appointments:
    print(f"ID: {apt.id:2d} | Date: {apt.date} | Status: {apt.status}")

print(f"\n🎯 CONCLUSION:")
print(f"Database shows {todays_count} appointments for today ({today_tz})")
print(f"Frontend shows 17 appointments")
if todays_count != 17:
    print("⚠️  MISMATCH DETECTED! Frontend and database don't match.")
    print("Frontend is likely counting all appointments instead of just today's.")
else:
    print("✅ Frontend and database match!")
