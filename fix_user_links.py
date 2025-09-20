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

def fix_user_employee_links():
    print("=== FIXING USER-EMPLOYEE LINKS ===")
    
    # Link users to employees based on matching emails
    employees_without_users = Employee.objects.filter(user__isnull=True)
    print(f"Found {employees_without_users.count()} employees without linked users")
    
    fixed_count = 0
    
    for employee in employees_without_users:
        try:
            # Find matching user by email
            user = User.objects.get(email=employee.email)
            
            # Link the user to the employee
            employee.user = user
            
            # Set the user role based on employee role
            if employee.role in ['mechanic', 'technician']:
                user.role = User.EMPLOYEE  # Both mechanics and technicians are employees
            elif employee.role == 'manager':
                user.role = User.OWNER  # Managers get owner privileges
            elif employee.role == 'receptionist':
                user.role = User.EMPLOYEE
            else:
                user.role = User.EMPLOYEE  # Default to employee
                
            # Save both records
            user.save()
            employee.save()
            
            print(f"✅ Linked {employee.name} ({employee.email}) to user {user.username}")
            print(f"   Employee role: {employee.role} -> User role: {user.role}")
            fixed_count += 1
            
        except User.DoesNotExist:
            print(f"❌ No user found for employee {employee.name} ({employee.email})")
        except Exception as e:
            print(f"❌ Error linking {employee.name}: {str(e)}")
    
    print(f"\n✅ Successfully linked {fixed_count} employees to users")
    
    # Verify the john.mechanic user specifically
    print(f"\n=== VERIFYING john.mechanic@autorepair.com ===")
    try:
        user = User.objects.get(email="john.mechanic@autorepair.com")
        employee = Employee.objects.get(email="john.mechanic@autorepair.com")
        
        print(f"User ID: {user.id}")
        print(f"User role: {user.role}")
        print(f"User active: {user.is_active}")
        print(f"Employee name: {employee.name}")
        print(f"Employee role: {employee.role}")
        print(f"Employee linked user: {employee.user.id if employee.user else 'None'}")
        
        if employee.user == user:
            print("✅ User and Employee are properly linked!")
        else:
            print("❌ User and Employee are NOT linked")
            
    except Exception as e:
        print(f"❌ Error checking john.mechanic: {str(e)}")

if __name__ == '__main__':
    fix_user_employee_links()