#!/usr/bin/env python3
"""
Test script for the Role-Based Access Control (RBAC) system
"""

import requests
import json
import sys


def test_user_login(email, password, role_name):
    """Test user login and profile access"""
    print(f"\n=== TESTING {role_name.upper()} ACCOUNT ===")

    # Login
    login_data = {"email": email, "password": password}
    response = requests.post("http://127.0.0.1:8000/api/token/", json=login_data)

    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

    tokens = response.json()
    access_token = tokens["access"]
    print(f"✅ Login successful for {email}")

    # Test profile access
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(
        "http://127.0.0.1:8000/api/auth/user/", headers=headers
    )

    if profile_response.status_code != 200:
        print(f"❌ Profile access failed: {profile_response.status_code}")
        return None

    profile = profile_response.json()
    print(f"✅ Profile access successful!")
    print(f"   Email: {profile.get('email')}")
    print(f"   Role: {profile.get('role')}")
    print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")

    # Show permissions
    permissions = profile.get("permissions", {})
    print(f"\n   {role_name} Permissions:")
    for perm, value in permissions.items():
        status = "✅" if value else "❌"
        print(f"   {status} {perm}: {value}")

    return access_token


def test_owner_endpoints(access_token):
    """Test owner-specific endpoints"""
    print(f"\n=== TESTING OWNER-SPECIFIC ENDPOINTS ===")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test 1: List all users (owner only)
    print("\n1. Testing /api/admin/users/ (Owner Only):")
    users_response = requests.get(
        "http://127.0.0.1:8000/api/admin/users/", headers=headers
    )
    if users_response.status_code == 200:
        users = users_response.json()
        print(f"✅ Success! Found {len(users)} users")
        for user in users[:3]:  # Show first 3
            print(f"   - {user.get('email')} ({user.get('role')})")
        if len(users) > 3:
            print(f"   ... and {len(users)-3} more users")
    else:
        print(f"❌ Failed: {users_response.status_code}")
        print(f"   Error: {users_response.text[:200]}")

    # Test 2: View shops (shop management)
    print("\n2. Testing /api/shop/shops/ (Shop Management):")
    shops_response = requests.get(
        "http://127.0.0.1:8000/api/shop/shops/", headers=headers
    )
    if shops_response.status_code == 200:
        shops = shops_response.json()
        print(f"✅ Success! Owner can access shop management")
        if isinstance(shops, list):
            print(f"   Shop count: {len(shops)}")
            for shop in shops[:2]:
                print(f"   - {shop.get('name')}: {shop.get('address')}")
        else:
            print(f"   Response type: {type(shops)}")
    else:
        print(f"❌ Failed: {shops_response.status_code}")
        print(f"   Error: {shops_response.text[:200]}")

    # Test 3: Employee management
    print("\n3. Testing /api/shop/employees/ (Employee Management):")
    employees_response = requests.get(
        "http://127.0.0.1:8000/api/shop/employees/", headers=headers
    )
    if employees_response.status_code == 200:
        employees = employees_response.json()
        print(f"✅ Success! Owner can manage employees")
        if isinstance(employees, list):
            print(f"   Employee count: {len(employees)}")
        else:
            print(f"   Response type: {type(employees)}")
    else:
        print(f"❌ Failed: {employees_response.status_code}")
        print(f"   Error: {employees_response.text[:200]}")

    # Test 4: Financial data access
    print("\n4. Testing /api/shop/repair-orders/financial_summary/ (Financial Data):")
    financial_response = requests.get(
        "http://127.0.0.1:8000/api/shop/repair-orders/financial_summary/",
        headers=headers,
    )
    if financial_response.status_code == 200:
        financial_data = financial_response.json()
        print(f"✅ Success! Owner can access financial data")
        print(f"   Total Orders: {financial_data.get('total_orders', 'N/A')}")
        print(f"   Total Revenue: ${financial_data.get('total_revenue', 0):.2f}")
    else:
        print(f"❌ Failed: {financial_response.status_code}")
        print(f"   Error: {financial_response.text[:200]}")

    # Test 5: Vehicle management
    print("\n5. Testing /api/shop/vehicles/ (Vehicle Management):")
    vehicles_response = requests.get(
        "http://127.0.0.1:8000/api/shop/vehicles/", headers=headers
    )
    if vehicles_response.status_code == 200:
        vehicles = vehicles_response.json()
        print(f"✅ Success! Owner can access vehicle data")
        if isinstance(vehicles, list):
            print(f"   Vehicle count: {len(vehicles)}")
            for vehicle in vehicles[:2]:
                print(
                    f"   - {vehicle.get('make')} {vehicle.get('model')} ({vehicle.get('year')})"
                )
        else:
            print(f"   Response type: {type(vehicles)}")
    else:
        print(f"❌ Failed: {vehicles_response.status_code}")
        print(f"   Error: {vehicles_response.text[:200]}")

    # Test 6: Vehicle problems
    print("\n6. Testing /api/shop/vehicle-problems/ (Vehicle Problems):")
    problems_response = requests.get(
        "http://127.0.0.1:8000/api/shop/vehicle-problems/", headers=headers
    )
    if problems_response.status_code == 200:
        problems = problems_response.json()
        print(f"✅ Success! Owner can access vehicle problems")
        if isinstance(problems, list):
            print(f"   Problem count: {len(problems)}")
        else:
            print(f"   Response type: {type(problems)}")
    else:
        print(f"❌ Failed: {problems_response.status_code}")
        print(f"   Error: {problems_response.text[:200]}")


def test_employee_access(email="john.mechanic@autorepair.com", password="password123"):
    """Test employee access restrictions"""
    print(f"\n=== TESTING EMPLOYEE RESTRICTIONS ===")

    # Login as employee
    login_data = {"email": email, "password": password}
    response = requests.post("http://127.0.0.1:8000/api/token/", json=login_data)

    if response.status_code != 200:
        print(f"❌ Employee login failed")
        return

    tokens = response.json()
    headers = {"Authorization": f'Bearer {tokens["access"]}'}

    # Test restricted endpoint (should fail)
    print("\n1. Testing employee access to /api/admin/users/ (Should fail):")
    users_response = requests.get(
        "http://127.0.0.1:8000/api/admin/users/", headers=headers
    )
    if users_response.status_code == 403:
        print("✅ Correctly blocked! Employee cannot access admin endpoints")
    elif users_response.status_code == 200:
        print("❌ Security issue! Employee should not access admin endpoints")
    else:
        print(f"❓ Unexpected response: {users_response.status_code}")


def test_customer_access(email="alice.cooper@customer.com", password="password123"):
    """Test customer access restrictions"""
    print(f"\n=== TESTING CUSTOMER RESTRICTIONS ===")

    # Login as customer
    login_data = {"email": email, "password": password}
    response = requests.post("http://127.0.0.1:8000/api/token/", json=login_data)

    if response.status_code != 200:
        print(f"❌ Customer login failed")
        return

    tokens = response.json()
    headers = {"Authorization": f'Bearer {tokens["access"]}'}

    # Test actual shop management endpoints (should fail)
    print("\n1. Testing customer access to /api/shop/shops/ (Should fail):")
    shops_response = requests.get(
        "http://127.0.0.1:8000/api/shop/shops/", headers=headers
    )
    print(f"   Status Code: {shops_response.status_code}")
    if shops_response.status_code == 403:
        print("✅ Correctly blocked! Customer cannot access shop management")
    elif shops_response.status_code == 200:
        print("❌ Security issue! Customer should not access shop endpoints")
        print(f"   Response: {shops_response.text[:200]}")
    else:
        print(f"❓ Unexpected response: {shops_response.status_code}")

    # Test admin endpoints (should fail)
    print("\n2. Testing customer access to /api/admin/users/ (Should fail):")
    users_response = requests.get(
        "http://127.0.0.1:8000/api/admin/users/", headers=headers
    )
    if users_response.status_code == 403:
        print("✅ Correctly blocked! Customer cannot access admin endpoints")
    else:
        print(f"❓ Status: {users_response.status_code} - {users_response.text[:100]}")

    # Test employee management (should fail)
    print("\n3. Testing customer access to /api/shop/employees/ (Should fail):")
    employees_response = requests.get(
        "http://127.0.0.1:8000/api/shop/employees/", headers=headers
    )
    if employees_response.status_code == 403:
        print("✅ Correctly blocked! Customer cannot access employee management")
    else:
        print(
            f"❓ Status: {employees_response.status_code} - {employees_response.text[:100]}"
        )

    # Test customer access to their own data (should succeed)
    print(
        "\n4. Testing customer access to /api/shop/customers/ (Should succeed for own data):"
    )
    customers_response = requests.get(
        "http://127.0.0.1:8000/api/shop/customers/", headers=headers
    )
    if customers_response.status_code == 200:
        customers = customers_response.json()
        print(f"✅ Success! Customer can access customer data")
        print(
            f"   Found {len(customers) if isinstance(customers, list) else 'some'} customer records"
        )
    else:
        print(
            f"❓ Status: {customers_response.status_code} - {customers_response.text[:100]}"
        )

    # Test appointment access (should succeed for own appointments)
    print(
        "\n5. Testing customer access to /api/shop/appointments/ (Should succeed for own data):"
    )
    appointments_response = requests.get(
        "http://127.0.0.1:8000/api/shop/appointments/", headers=headers
    )
    if appointments_response.status_code == 200:
        appointments = appointments_response.json()
        print(f"✅ Success! Customer can access appointment data")
        print(
            f"   Found {len(appointments) if isinstance(appointments, list) else 'some'} appointment records"
        )
    else:
        print(
            f"❓ Status: {appointments_response.status_code} - {appointments_response.text[:100]}"
        )


def main():
    """Main test function"""
    print("🔐 ROLE-BASED ACCESS CONTROL (RBAC) SYSTEM TEST")
    print("=" * 50)

    try:
        # Test Owner Account
        owner_token = test_user_login("owner@autorepairshop.com", "owner123", "Owner")

        if owner_token:
            test_owner_endpoints(owner_token)

        # Test Employee Account
        test_user_login("john.mechanic@autorepair.com", "password123", "Employee")

        # Test Customer Account
        test_user_login("alice.cooper@customer.com", "password123", "Customer")

        # Test access restrictions
        test_employee_access()
        test_customer_access()

        print(f"\n🎉 RBAC TESTING COMPLETE!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Django server")
        print("   Make sure the server is running on http://127.0.0.1:8000/")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
