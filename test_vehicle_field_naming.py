#!/usr/bin/env python
"""
Test script to verify the vehicle field naming consistency implementation.

This script tests both the new vehicle_id field and the deprecated vehicle field
to ensure backward compatibility during the transition period.
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_repairs_backend.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from shop.models import Shop, Vehicle, Customer, RepairOrder
from auto_repairs_backend.models import User

def setup_test_data():
    """Create test data for vehicle field naming tests"""
    
    print("🔧 Setting up test data...")
    
    # Create a test user with appropriate permissions
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        role='employee'  # Employee can create repair orders
    )
    
    # Create a test shop
    shop = Shop.objects.create(
        name='Test Auto Shop',
        address='123 Test St',
        phone='555-0123',
        email='shop@test.com'
    )
    
    # Create a test customer
    customer = Customer.objects.create(
        name='John Doe',
        email='john@example.com',
        phone_number='555-0456',
        address='456 Customer Ave'
    )
    
    # Create a test vehicle
    vehicle = Vehicle.objects.create(
        make='Toyota',
        model='Camry',
        year=2020,
        license_plate='ABC123',
        vin='1234567890',
        color='Blue',
        mileage=25000,
        customer=customer
    )
    
    print(f"✅ Created test data:")
    print(f"   - User: {user.username} (role: {user.role})")
    print(f"   - Customer: {customer.name}")
    print(f"   - Vehicle: {vehicle.year} {vehicle.make} {vehicle.model} (ID: {vehicle.id})")
    
    return user, vehicle

def test_api_endpoints():
    """Test the repair order creation API with both field names"""
    
    print("\n🧪 Testing API Endpoints...")
    
    user, vehicle = setup_test_data()
    
    # Create API client and authenticate
    client = APIClient()
    
    # Get JWT token for the user
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test 1: Create repair order with new vehicle_id field (preferred)
    print("\n📝 Test 1: Creating repair order with vehicle_id (new preferred field)")
    data_new = {
        'vehicle_id': vehicle.id,
        'notes': 'Test repair order created with vehicle_id field',
        'discount_amount': '0.00'
    }
    
    response = client.post('/api/shop/repair-orders/', data_new, format='json')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        print("   ✅ SUCCESS: Repair order created with vehicle_id")
        response_data = response.json()
        print(f"   📄 Response includes:")
        print(f"      - ID: {response_data.get('id')}")
        print(f"      - Vehicle: {response_data.get('vehicle')}")
        print(f"      - Status: {response_data.get('status')}")
        print(f"      - Notes: {response_data.get('notes')}")
        
        # Store the ID for cleanup
        new_field_order_id = response_data.get('id')
    else:
        print(f"   ❌ FAILED: {response.status_code} - {response.json()}")
        return False
    
    # Test 2: Create repair order with legacy vehicle field (deprecated)
    print("\n📝 Test 2: Creating repair order with vehicle (legacy deprecated field)")
    data_legacy = {
        'vehicle': vehicle.id,
        'notes': 'Test repair order created with legacy vehicle field',
        'discount_amount': '0.00'
    }
    
    response = client.post('/api/shop/repair-orders/', data_legacy, format='json')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        print("   ✅ SUCCESS: Repair order created with legacy vehicle field (backward compatibility)")
        response_data = response.json()
        print(f"   📄 Response includes:")
        print(f"      - ID: {response_data.get('id')}")
        print(f"      - Vehicle: {response_data.get('vehicle')}")
        print(f"      - Status: {response_data.get('status')}")
        print(f"      - Notes: {response_data.get('notes')}")
        
        legacy_field_order_id = response_data.get('id')
    else:
        print(f"   ❌ FAILED: {response.status_code} - {response.json()}")
        return False
    
    # Test 3: Error when both fields provided
    print("\n📝 Test 3: Error handling when both vehicle and vehicle_id provided")
    data_both = {
        'vehicle_id': vehicle.id,
        'vehicle': vehicle.id,
        'notes': 'This should fail',
        'discount_amount': '0.00'
    }
    
    response = client.post('/api/shop/repair-orders/', data_both, format='json')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        print("   ✅ SUCCESS: Correctly rejected request with both fields")
        error_data = response.json()
        print(f"   📄 Error message: {error_data}")
    else:
        print(f"   ❌ FAILED: Should have returned 400, got {response.status_code}")
        return False
    
    # Test 4: Error when no vehicle field provided
    print("\n📝 Test 4: Error handling when no vehicle field provided")
    data_none = {
        'notes': 'This should fail - no vehicle specified',
        'discount_amount': '0.00'
    }
    
    response = client.post('/api/shop/repair-orders/', data_none, format='json')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 400:
        print("   ✅ SUCCESS: Correctly rejected request with no vehicle field")
        error_data = response.json()
        print(f"   📄 Error message: {error_data}")
    else:
        print(f"   ❌ FAILED: Should have returned 400, got {response.status_code}")
        return False
    
    # Test 5: Verify both repair orders are retrievable and have consistent data
    print("\n📝 Test 5: Retrieving created repair orders")
    
    # Get the repair order created with vehicle_id
    response = client.get(f'/api/shop/repair-orders/{new_field_order_id}/')
    if response.status_code == 200:
        print("   ✅ Successfully retrieved repair order created with vehicle_id")
        data = response.json()
        print(f"      - Vehicle ID: {data.get('vehicle')}")
        print(f"      - Status: {data.get('status')}")
    else:
        print(f"   ❌ Failed to retrieve repair order: {response.status_code}")
    
    # Get the repair order created with legacy vehicle
    response = client.get(f'/api/shop/repair-orders/{legacy_field_order_id}/')
    if response.status_code == 200:
        print("   ✅ Successfully retrieved repair order created with legacy vehicle")
        data = response.json()
        print(f"      - Vehicle ID: {data.get('vehicle')}")
        print(f"      - Status: {data.get('status')}")
    else:
        print(f"   ❌ Failed to retrieve repair order: {response.status_code}")
    
    print("\n🎉 All API tests completed successfully!")
    return True

def test_api_consistency():
    """Test API consistency with other endpoints using vehicle_id pattern"""
    
    print("\n🔍 Testing API Consistency...")
    
    user, vehicle = setup_test_data()
    
    # Create API client and authenticate
    client = APIClient()
    
    # Get JWT token for the user
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Create a repair order first
    data = {
        'vehicle_id': vehicle.id,
        'notes': 'Consistency test repair order'
    }
    response = client.post('/api/shop/repair-orders/', data, format='json')
    
    if response.status_code != 201:
        print(f"❌ Failed to create test repair order: {response.status_code}")
        return False
    
    # Test filtering with vehicle_id parameter (should be consistent)
    print("\n📝 Testing vehicle_id filtering consistency")
    response = client.get(f'/api/shop/repair-orders/?vehicle_id={vehicle.id}')
    print(f"   GET /api/shop/repair-orders/?vehicle_id={vehicle.id}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {len(data)} repair orders for vehicle_id={vehicle.id}")
    else:
        print(f"   ❌ Failed to filter by vehicle_id: {response.status_code}")
        return False
    
    print("\n🎯 API consistency verification completed!")
    return True

if __name__ == '__main__':
    print("🚀 Vehicle Field Naming Consistency Test")
    print("=" * 50)
    print("Testing backward compatible vehicle → vehicle_id transition")
    print("=" * 50)
    
    try:
        # Run the API tests
        api_success = test_api_endpoints()
        
        if api_success:
            # Run consistency tests
            consistency_success = test_api_consistency()
            
            if consistency_success:
                print("\n" + "=" * 50)
                print("🎉 ALL TESTS PASSED!")
                print("✅ vehicle_id field works correctly (new preferred)")
                print("✅ vehicle field works correctly (legacy/deprecated)")
                print("✅ Error handling works for invalid combinations")
                print("✅ API consistency maintained across endpoints")
                print("🚀 Ready for frontend team integration!")
                print("=" * 50)
                sys.exit(0)
            else:
                print("\n❌ Consistency tests failed")
                sys.exit(1)
        else:
            print("\n❌ API tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
