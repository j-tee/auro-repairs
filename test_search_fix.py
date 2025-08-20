#!/usr/bin/env python3
"""
Test script to verify the search fix
"""
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_repairs_backend.settings")
django.setup()


def test_search_endpoints():
    """Test individual search endpoints to verify the fix"""
    base_url = "http://localhost:8002/api"

    # Login to get token
    print("🔐 Getting authentication token...")
    login_data = {"username": "alice", "password": "password123"}

    try:
        login_response = requests.post(f"{base_url}/login/", json=login_data, timeout=5)

        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access")
            headers = {"Authorization": f"Bearer {access_token}"}
            print("✅ Authentication successful")

            # Test 1: Vehicle search endpoint
            print(
                "\n🚗 Testing Vehicle Search Endpoint: /api/shop/vehicles/?search=toyota"
            )
            vehicle_response = requests.get(
                f"{base_url}/shop/vehicles/?search=toyota", headers=headers, timeout=5
            )

            if vehicle_response.status_code == 200:
                vehicles = vehicle_response.json()
                print(f"Status: ✅ {vehicle_response.status_code}")
                print(f"Total vehicles found: {len(vehicles)}")

                toyota_count = 0
                non_toyota_count = 0

                for vehicle in vehicles:
                    make = vehicle.get("make", "").lower()
                    model = vehicle.get("model", "")
                    customer_name = vehicle.get("customer_name", "Unknown")

                    if "toyota" in make:
                        toyota_count += 1
                        print(
                            f"  ✅ CORRECT: {vehicle['make']} {model} - {customer_name}"
                        )
                    else:
                        non_toyota_count += 1
                        print(
                            f"  ❌ INCORRECT: {vehicle['make']} {model} - {customer_name}"
                        )

                print(f"\n📊 Vehicle Search Results:")
                print(f"  ✅ Toyota vehicles: {toyota_count}")
                print(f"  ❌ Non-Toyota vehicles: {non_toyota_count}")

                if non_toyota_count == 0:
                    print("  🎯 SUCCESS: Vehicle search is working correctly!")
                else:
                    print(
                        "  🚨 FAILURE: Vehicle search is still returning incorrect results!"
                    )

            else:
                print(
                    f"❌ Vehicle search failed: {vehicle_response.status_code} - {vehicle_response.text}"
                )

            # Test 2: Customer search endpoint
            print(
                "\n👤 Testing Customer Search Endpoint: /api/shop/customers/?search=toyota"
            )
            customer_response = requests.get(
                f"{base_url}/shop/customers/?search=toyota", headers=headers, timeout=5
            )

            if customer_response.status_code == 200:
                customers = customer_response.json()
                print(f"Status: ✅ {customer_response.status_code}")
                print(f"Total customers found: {len(customers)}")

                for customer in customers:
                    name = customer.get("name", "Unknown")
                    email = customer.get("email", "Unknown")
                    print(f"  Customer: {name} ({email})")

            else:
                print(
                    f"❌ Customer search failed: {customer_response.status_code} - {customer_response.text}"
                )

            # Test 3: Global search endpoint
            print("\n🌐 Testing Global Search Endpoint: /api/shop/search/?q=toyota")
            global_response = requests.get(
                f"{base_url}/shop/search/?q=toyota", headers=headers, timeout=5
            )

            if global_response.status_code == 200:
                results = global_response.json()
                print(f"Status: ✅ {global_response.status_code}")
                print(f"Total vehicles: {len(results.get('vehicles', []))}")
                print(f"Total customers: {len(results.get('customers', []))}")
                print(f"Total repair orders: {len(results.get('repair_orders', []))}")
                print(f"Grand total: {results.get('total_results', 0)}")

                # Check vehicles in global search
                vehicles = results.get("vehicles", [])
                toyota_count = 0
                non_toyota_count = 0

                for vehicle in vehicles:
                    make = vehicle.get("make", "").lower()
                    if "toyota" in make:
                        toyota_count += 1
                    else:
                        non_toyota_count += 1

                if non_toyota_count == 0:
                    print("  🎯 SUCCESS: Global search vehicles are correct!")
                else:
                    print("  🚨 WARNING: Global search still has non-Toyota vehicles!")

            else:
                print(
                    f"❌ Global search failed: {global_response.status_code} - {global_response.text}"
                )

        else:
            print(
                f"❌ Login failed: {login_response.status_code} - {login_response.text}"
            )

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to server. Make sure Django server is running on port 8002"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_search_endpoints()
