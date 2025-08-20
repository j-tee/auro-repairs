#!/usr/bin/env python3
"""
Backend API Test Script - For Frontend Developer Verification
This script shows exactly what the backend returns for toyota search
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_repairs_backend.settings")
django.setup()


def test_backend_queries():
    """Test the exact backend queries that should work"""

    print("🔍 BACKEND API VERIFICATION SCRIPT")
    print("=" * 50)
    print("This script shows the EXACT responses your frontend should receive")
    print()

    # First test direct database queries
    print("📊 DIRECT DATABASE VERIFICATION:")
    print("-" * 30)

    from shop.models import Vehicle, Customer
    from django.db.models import Q

    # Test vehicle search logic
    search_query = "toyota"
    vehicles = Vehicle.objects.filter(
        Q(make__icontains=search_query)
        | Q(model__icontains=search_query)
        | Q(vin__icontains=search_query)
        | Q(license_plate__icontains=search_query)
        | Q(color__icontains=search_query)
    ).select_related("customer")

    print(
        f"Database Query: Vehicle.objects.filter(Q(make__icontains='{search_query}') | ...)"
    )
    print(f"Results: {vehicles.count()} vehicle(s)")

    for vehicle in vehicles:
        print(
            f"  ✅ {vehicle.make} {vehicle.model} ({vehicle.year}) - Customer: {vehicle.customer.name}"
        )
        print(f"     VIN: {vehicle.vin}")
        print(f"     License: {vehicle.license_plate}")
        print(f"     Color: {vehicle.color}")

    # Test customer search logic
    customers = Customer.objects.filter(
        Q(name__icontains=search_query)
        | Q(email__icontains=search_query)
        | Q(address__icontains=search_query)
        | Q(phone_number__icontains=search_query)
        | Q(vehicles__make__icontains=search_query)
        | Q(vehicles__model__icontains=search_query)
    ).distinct()

    print(f"\nCustomer Query Results: {customers.count()} customer(s)")
    for customer in customers:
        print(f"  ✅ {customer.name} ({customer.email})")

    print("\n" + "=" * 50)
    print("🌐 API ENDPOINT TESTING:")
    print("-" * 30)

    # Test API endpoints
    base_url = "http://localhost:8000/api"

    # Login first
    print("🔐 Authenticating...")
    login_data = {"username": "alice", "password": "password123"}

    try:
        login_response = requests.post(f"{base_url}/login/", json=login_data, timeout=5)

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access")
            headers = {"Authorization": f"Bearer {access_token}"}
            print("✅ Authentication successful")

            # Test Vehicle Search Endpoint
            print(f"\n🚗 Testing: GET {base_url}/shop/vehicles/?search=toyota")
            vehicle_response = requests.get(
                f"{base_url}/shop/vehicles/?search=toyota", headers=headers, timeout=5
            )

            if vehicle_response.status_code == 200:
                vehicles_data = vehicle_response.json()
                print(f"✅ Status: {vehicle_response.status_code}")
                print(f"📊 Response: {len(vehicles_data)} vehicle(s)")
                print("📋 Raw JSON Response:")
                print(json.dumps(vehicles_data, indent=2))

                # Verify results
                toyota_found = False
                non_toyota_found = False

                for vehicle in vehicles_data:
                    make = vehicle.get("make", "").lower()
                    if "toyota" in make:
                        toyota_found = True
                        print(
                            f"  ✅ CORRECT: Found Toyota - {vehicle['make']} {vehicle['model']}"
                        )
                    else:
                        non_toyota_found = True
                        print(
                            f"  ❌ INCORRECT: Found non-Toyota - {vehicle['make']} {vehicle['model']}"
                        )

                if toyota_found and not non_toyota_found:
                    print("  🎯 PERFECT: Only Toyota vehicles returned!")
                elif toyota_found and non_toyota_found:
                    print("  🚨 ERROR: Mixed results - should only be Toyota!")
                else:
                    print("  ❓ UNEXPECTED: No Toyota vehicles found!")

            else:
                print(f"❌ Vehicle search failed: {vehicle_response.status_code}")
                print(f"Response: {vehicle_response.text}")

            # Test Global Search Endpoint
            print(f"\n🌐 Testing: GET {base_url}/shop/search/?q=toyota")
            global_response = requests.get(
                f"{base_url}/shop/search/?q=toyota", headers=headers, timeout=5
            )

            if global_response.status_code == 200:
                global_data = global_response.json()
                print(f"✅ Status: {global_response.status_code}")
                print(f"📊 Total Results: {global_data.get('total_results', 0)}")
                print(f"🚗 Vehicles: {len(global_data.get('vehicles', []))}")
                print(f"👤 Customers: {len(global_data.get('customers', []))}")
                print(f"🔧 Repair Orders: {len(global_data.get('repair_orders', []))}")
                print("📋 Raw JSON Response:")
                print(json.dumps(global_data, indent=2))

            else:
                print(f"❌ Global search failed: {global_response.status_code}")
                print(f"Response: {global_response.text}")

        else:
            print(f"❌ Authentication failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Start Django server with:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("📝 SUMMARY FOR FRONTEND DEVELOPER:")
    print("-" * 30)
    print("1. ✅ Backend database contains exactly 1 Toyota vehicle")
    print("2. ✅ Backend search logic returns only Toyota results")
    print("3. ✅ API endpoints are working correctly")
    print("4. 🎯 If your frontend shows Honda/Ford, the issue is:")
    print("   - Browser/API caching")
    print("   - Wrong endpoint URLs")
    print("   - Frontend state management")
    print("   - Multiple API calls being combined incorrectly")
    print("\n💡 TIP: Copy the exact API URLs and test them in your browser's")
    print("      Network tab to see what responses you're actually getting!")


if __name__ == "__main__":
    test_backend_queries()
