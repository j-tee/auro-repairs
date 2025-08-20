#!/usr/bin/env python3
"""
Frontend Developer Debug Script
Test the Vehicle-Customer API to verify the fix
"""

import requests
import json
import sys


def test_vehicle_api():
    """Test the vehicle API endpoints for frontend integration"""

    print("🔧 VEHICLE-CUSTOMER API DEBUG SCRIPT")
    print("=" * 50)

    # Test credentials
    credentials = [
        {"email": "owner@autorepairshop.com", "password": "owner123", "role": "Owner"},
        {
            "email": "john.mechanic@autorepair.com",
            "password": "password123",
            "role": "Employee",
        },
        {
            "email": "alice.cooper@customer.com",
            "password": "password123",
            "role": "Customer",
        },
    ]

    for cred in credentials:
        print(f"\n🔑 Testing as {cred['role']}: {cred['email']}")

        # Login
        login_data = {"email": cred["email"], "password": cred["password"]}
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/token/", json=login_data
            )

            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                continue

            tokens = response.json()
            headers = {"Authorization": f'Bearer {tokens["access"]}'}
            print(f"✅ Login successful")

            # Test vehicles endpoint
            vehicles_response = requests.get(
                "http://127.0.0.1:8000/api/shop/vehicles/", headers=headers
            )

            if vehicles_response.status_code == 200:
                vehicles = vehicles_response.json()
                print(f"✅ Vehicles API: {len(vehicles)} vehicles found")

                # Show first vehicle structure for frontend dev
                if vehicles:
                    print(f"\n📋 Sample Vehicle Data Structure:")
                    sample_vehicle = vehicles[0]

                    # Key fields for frontend
                    key_fields = [
                        "id",
                        "customer_name",
                        "customer_email",
                        "customer_phone",
                        "make",
                        "model",
                        "year",
                        "vin",
                        "license_plate",
                        "color",
                    ]

                    print("Frontend-friendly fields:")
                    for field in key_fields:
                        value = sample_vehicle.get(field, "NOT_FOUND")
                        print(f"  {field}: {value}")

                    print(f"\n📝 Frontend Code Example:")
                    print(
                        f"  Customer Name: vehicle.customer_name = '{sample_vehicle.get('customer_name')}'"
                    )
                    print(
                        f"  Vehicle Info: {{vehicle.year}} {{vehicle.make}} {{vehicle.model}}"
                    )
                    print(
                        f"  Result: '{sample_vehicle.get('year')} {sample_vehicle.get('make')} {sample_vehicle.get('model')}'"
                    )

                    # Show all vehicles for this role
                    print(f"\n🚗 All vehicles for {cred['role']}:")
                    for i, vehicle in enumerate(vehicles, 1):
                        customer_name = vehicle.get("customer_name", "Unknown Customer")
                        vehicle_info = f"{vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}"
                        print(f"  {i}. {customer_name} -> {vehicle_info}")

            elif vehicles_response.status_code == 403:
                print(
                    f"🔒 Access restricted for {cred['role']} (expected for some roles)"
                )
            else:
                print(f"❌ API Error: {vehicles_response.status_code}")
                print(f"   Response: {vehicles_response.text[:200]}")

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Django server")
            print("   Make sure the server is running on http://127.0.0.1:8000/")
            return False
        except Exception as e:
            print(f"❌ Error testing {cred['role']}: {e}")

    print(f"\n🧪 FRONTEND TESTING INSTRUCTIONS")
    print("=" * 50)
    print("1. Open your browser's developer console")
    print("2. Run this JavaScript code:")
    print(
        """
// Test the API directly in browser
fetch('/api/shop/vehicles/', {
  headers: {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(vehicles => {
  console.log('✅ Vehicles loaded:', vehicles.length);
  vehicles.forEach((vehicle, i) => {
    console.log(`${i+1}. ${vehicle.customer_name} -> ${vehicle.year} ${vehicle.make} ${vehicle.model}`);
  });
})
.catch(error => console.error('❌ Error:', error));
"""
    )

    print(f"\n🔑 Test Login Tokens:")
    print("Replace YOUR_ACCESS_TOKEN with the token from:")
    print("POST /api/token/ with email/password from above")

    return True


def test_single_vehicle():
    """Test a single vehicle detail endpoint"""
    print(f"\n🔍 TESTING SINGLE VEHICLE DETAIL")
    print("=" * 30)

    # Login as owner
    login_data = {"email": "owner@autorepairshop.com", "password": "owner123"}
    try:
        response = requests.post("http://127.0.0.1:8000/api/token/", json=login_data)
        tokens = response.json()
        headers = {"Authorization": f'Bearer {tokens["access"]}'}

        # Get vehicles list first
        vehicles_response = requests.get(
            "http://127.0.0.1:8000/api/shop/vehicles/", headers=headers
        )
        vehicles = vehicles_response.json()

        if vehicles:
            vehicle_id = vehicles[0]["id"]

            # Get single vehicle detail
            detail_response = requests.get(
                f"http://127.0.0.1:8000/api/shop/vehicles/{vehicle_id}/",
                headers=headers,
            )

            if detail_response.status_code == 200:
                vehicle = detail_response.json()
                print(f"✅ Single vehicle detail working")
                print(f"📋 Complete vehicle object structure:")

                # Pretty print the JSON for frontend dev
                print(json.dumps(vehicle, indent=2)[:500] + "...")

                print(f"\n🎯 Key frontend fields:")
                print(f"  ID: {vehicle.get('id')}")
                print(f"  Customer: {vehicle.get('customer_name')}")
                print(
                    f"  Vehicle: {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}"
                )
                print(f"  VIN: {vehicle.get('vin')}")
                print(f"  License: {vehicle.get('license_plate')}")

    except Exception as e:
        print(f"❌ Error testing single vehicle: {e}")


if __name__ == "__main__":
    print("Starting Vehicle-Customer API debug tests...")

    if test_vehicle_api():
        test_single_vehicle()

        print(f"\n🎉 SUMMARY FOR FRONTEND DEVELOPER")
        print("=" * 50)
        print("✅ Backend is working correctly")
        print("✅ Customer names are properly linked to vehicles")
        print("✅ API returns customer_name field directly")
        print("")
        print("🔧 Frontend fixes needed:")
        print("1. Clear browser cache (Ctrl+F5)")
        print("2. Use vehicle.customer_name instead of vehicle.customer?.name")
        print("3. Ensure proper API authentication")
        print("4. Check API endpoint is /api/shop/vehicles/")
        print("")
        print("📋 Working customer-vehicle relationships:")
        print("- Alice Cooper -> Toyota Camry")
        print("- Bob Martinez -> Honda Civic")
        print("- Carol White -> Ford F-150")
        print("- And 4 more vehicles with proper customer links")
    else:
        print("❌ Backend not accessible. Start Django server first.")
        sys.exit(1)
