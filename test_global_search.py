#!/usr/bin/env python3
"""
Test script for global search functionality
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_repairs_backend.settings")
django.setup()


def test_global_search():
    """Test the global search API endpoint"""
    base_url = "http://localhost:8002/api"

    # Login to get token
    print("🔐 Logging in...")
    login_data = {"username": "alice", "password": "password123"}

    try:
        login_response = requests.post(f"{base_url}/login/", json=login_data, timeout=5)
        print(f"Login status: {login_response.status_code}")

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access")
            print("✅ Successfully logged in")

            # Test global search
            headers = {"Authorization": f"Bearer {access_token}"}

            # Test Toyota search
            print("\n🔍 Testing Toyota search...")
            search_response = requests.get(
                f"{base_url}/shop/search/?q=toyota", headers=headers, timeout=5
            )
            print(f"Search status: {search_response.status_code}")

            if search_response.status_code == 200:
                results = search_response.json()
                print(f"✅ Search successful!")
                print(f"Total results: {results.get('total_results', 0)}")
                print(f"Vehicles found: {len(results.get('vehicles', []))}")
                print(f"Customers found: {len(results.get('customers', []))}")
                print(f"Repair orders found: {len(results.get('repair_orders', []))}")

                # Show details
                vehicles = results.get("vehicles", [])
                if vehicles:
                    print("\n🚗 Vehicles found:")
                    for vehicle in vehicles:
                        print(
                            f"  - {vehicle.get('make')} {vehicle.get('model')} ({vehicle.get('year')}) - {vehicle.get('customer_name')}"
                        )

                customers = results.get("customers", [])
                if customers:
                    print("\n👤 Customers found:")
                    for customer in customers:
                        print(f"  - {customer.get('name')} ({customer.get('email')})")

                repair_orders = results.get("repair_orders", [])
                if repair_orders:
                    print("\n🔧 Repair orders found:")
                    for order in repair_orders:
                        print(f"  - Order #{order.get('id')} - {order.get('notes')}")

                # Check if this matches expected result
                expected_vehicles = 1  # Only Alice's Toyota Camry
                actual_vehicles = len(vehicles)
                if actual_vehicles == expected_vehicles:
                    print(
                        f"\n✅ CORRECT: Found {actual_vehicles} Toyota vehicle(s) as expected"
                    )
                else:
                    print(
                        f"\n❌ INCORRECT: Found {actual_vehicles} vehicles, expected {expected_vehicles}"
                    )
                    print(
                        "This indicates there might be an issue with the search logic!"
                    )

            else:
                print(f"❌ Search failed: {search_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to server. Make sure Django server is running on port 8000"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_global_search()
