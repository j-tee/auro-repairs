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

def create_test_user():
    print("=== CREATING TEST USER ===")
    
    # Create or get a test user for technician testing
    email = "test.mechanic@autorepair.com"
    password = "testpass123"
    
    # Check if user already exists
    try:
        user = User.objects.get(email=email)
        print(f"User {email} already exists")
        # Update password to ensure it's correct
        user.set_password(password)
        user.is_active = True
        user.role = User.EMPLOYEE
        user.save()
        print(f"Updated user {email} with new password and activated account")
    except User.DoesNotExist:
        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role=User.EMPLOYEE,
            is_active=True
        )
        print(f"Created new user: {email}")
    
    # Test login immediately
    print(f"\nTesting login for {email}...")
    if user.check_password(password):
        print("✅ Password check successful")
    else:
        print("❌ Password check failed")
    
    print(f"User details:")
    print(f"  ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is Active: {user.is_active}")
    print(f"  Role: {user.role}")
    
    return user

def test_existing_user():
    print("\n=== TESTING EXISTING USER ===")
    
    email = "john.mechanic@autorepair.com"
    password = "password123"
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.email}")
        
        # Test the password
        if user.check_password(password):
            print("✅ Password is correct!")
        else:
            print("❌ Password is incorrect")
            # Try setting the password again
            user.set_password(password)
            user.save()
            print("Reset password and trying again...")
            if user.check_password(password):
                print("✅ Password now works after reset")
            else:
                print("❌ Password still doesn't work")
                
        print(f"User status: Active={user.is_active}, Role={user.role}")
        
    except User.DoesNotExist:
        print(f"User {email} not found")

if __name__ == '__main__':
    test_existing_user()
    create_test_user()