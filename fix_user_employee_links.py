#!/usr/bin/env python3
"""
Fix User-Employee Database Links
Links existing User records to Employee records by matching email addresses
"""

import os
import sys
import django
from django.conf import settings

# Add project root to Python path
sys.path.append('/home/teejay/Documents/Projects/auro-repairs')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from shop.models import Employee
from django.db import transaction

def fix_user_employee_links():
    """Link existing User records to Employee records by email matching"""
    
    print("🔗 Fixing User-Employee Database Links")
    print("=" * 60)
    
    User = get_user_model()
    
    # Get all users and employees
    users = User.objects.all()
    employees = Employee.objects.all()
    
    print(f"📊 Current Database State:")
    print(f"   - Total Users: {users.count()}")
    print(f"   - Total Employees: {employees.count()}")
    print(f"   - Employees with user_id: {employees.exclude(user=None).count()}")
    print(f"   - Employees without user_id: {employees.filter(user=None).count()}")
    
    # Show current state of key accounts
    print(f"\n🔍 Current User-Employee Links:")
    for user in users:
        try:
            employee = Employee.objects.get(user=user)
            print(f"   ✅ User {user.id} ({user.email}) → Employee {employee.id} ({employee.name})")
        except Employee.DoesNotExist:
            print(f"   ❌ User {user.id} ({user.email}) → No Employee linked")
    
    print(f"\n🔍 Unlinked Employees:")
    unlinked_employees = Employee.objects.filter(user=None)
    for employee in unlinked_employees:
        print(f"   📋 Employee {employee.id} ({employee.name}) - Email: {employee.email}")
    
    # Perform the linking
    print(f"\n🔧 Performing Email-Based Linking...")
    linked_count = 0
    
    with transaction.atomic():
        for employee in unlinked_employees:
            if employee.email:
                try:
                    # Find user with matching email
                    user = User.objects.get(email__iexact=employee.email)
                    employee.user = user
                    employee.save()
                    linked_count += 1
                    print(f"   ✅ Linked Employee {employee.id} ({employee.name}) to User {user.id} ({user.email})")
                except User.DoesNotExist:
                    print(f"   ⚠️  No User found for Employee {employee.name} ({employee.email})")
                except User.MultipleObjectsReturned:
                    print(f"   ⚠️  Multiple Users found for email {employee.email}")
            else:
                print(f"   ⚠️  Employee {employee.name} has no email address")
    
    print(f"\n📈 Linking Results:")
    print(f"   - Successfully linked: {linked_count} Employee(s)")
    print(f"   - Remaining unlinked: {Employee.objects.filter(user=None).count()}")
    
    # Verify specific test account
    print(f"\n🧪 Test Account Verification:")
    try:
        test_user = User.objects.get(email='john.mechanic@autorepair.com')
        print(f"   ✅ Found User: {test_user.id} ({test_user.email})")
        
        try:
            test_employee = Employee.objects.get(user=test_user)
            print(f"   ✅ Linked Employee: {test_employee.id} ({test_employee.name}) - Role: {test_employee.role}")
        except Employee.DoesNotExist:
            print(f"   ❌ No Employee linked to this user")
            
    except User.DoesNotExist:
        print(f"   ❌ Test user john.mechanic@autorepair.com not found")
    
    # Show final state
    print(f"\n📊 Final Database State:")
    print(f"   - Total Employees with user_id: {Employee.objects.exclude(user=None).count()}")
    print(f"   - Total Employees without user_id: {Employee.objects.filter(user=None).count()}")
    
    print(f"\n✅ User-Employee linking completed!")
    return linked_count

if __name__ == "__main__":
    linked_count = fix_user_employee_links()
    
    if linked_count > 0:
        print(f"\n🎉 SUCCESS: {linked_count} Employee(s) successfully linked!")
    else:
        print(f"\n⚠️  No new links created - check data manually")
    
    sys.exit(0)