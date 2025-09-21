#!/usr/bin/env python
import os
import sys
import django

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from auto_repairs_backend.models import User
from shop.models import Employee

def check_users():
    print("=== CHECKING USERS IN DATABASE ===")
    
    # Check all Django users
    print("\n1. All Django Users:")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Staff: {user.is_staff}")
        print(f"  Is Superuser: {user.is_superuser}")
        print("  ---")
    
    # Check specific user
    print(f"\n2. Checking for john.mechanic@autorepair.com:")
    try:
        user = User.objects.get(email="john.mechanic@autorepair.com")
        print(f"  Found user: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Password (hashed): {user.password[:50]}...")
        
        # Check if this user is an employee
        try:
            employee = Employee.objects.get(user=user)
            print(f"  Employee record exists:")
            print(f"    Name: {employee.name}")
            print(f"    Role: {employee.role}")
            print(f"    Email: {employee.email}")
            print(f"    Phone: {employee.phone_number}")
        except Employee.DoesNotExist:
            print("  No Employee record found for this user")
            
    except User.DoesNotExist:
        print("  User not found!")
    
    # Check all employees
    print(f"\n3. All Employees:")
    employees = Employee.objects.all()
    print(f"Total employees: {employees.count()}")
    
    for employee in employees:
        print(f"  Name: {employee.name}")
        print(f"  Email: {employee.email}")
        print(f"  Role: {employee.role}")
        print(f"  Phone: {employee.phone_number}")
        if employee.user:
            print(f"  Linked User: {employee.user.username} (Active: {employee.user.is_active})")
        else:
            print("  No linked Django user")
        print("  ---")

if __name__ == '__main__':
    check_users()