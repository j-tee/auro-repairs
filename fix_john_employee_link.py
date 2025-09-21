#!/usr/bin/env python3
"""
Fix Employee-User linking for john.mechanic@autorepair.com
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autorepairs.settings')
django.setup()

from auto_repairs_backend.models import User
from shop.models import Employee

def fix_john_employee_link():
    try:
        # Find John's User record
        user = User.objects.get(email='john.mechanic@autorepair.com')
        print(f"✅ Found User: {user.email} (ID: {user.id})")
        
        # Find John's Employee record
        employee = Employee.objects.get(email='john.mechanic@autorepair.com')
        print(f"✅ Found Employee: {employee.name} (ID: {employee.id})")
        
        # Link them
        employee.user = user
        employee.save()
        print(f"✅ Successfully linked Employee {employee.name} to User {user.email}")
        
        # Verify the link
        employee.refresh_from_db()
        if employee.user == user:
            print("✅ Link verified successfully!")
        else:
            print("❌ Link verification failed")
            
    except User.DoesNotExist:
        print("❌ User john.mechanic@autorepair.com not found")
    except Employee.DoesNotExist:
        print("❌ Employee with email john.mechanic@autorepair.com not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_john_employee_link()