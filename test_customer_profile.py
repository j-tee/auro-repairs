#!/usr/bin/env python3
"""
Test Customer Profile Endpoint
Tests the customer profile endpoint with authenticated customer user
"""

import requests
import json

# Base URL
BASE_URL = 'http://127.0.0.1:8000'

def test_customer_profile():
    print('🧪 TESTING CUSTOMER PROFILE ENDPOINT')
    print('=' * 50)

    # Get JWT token for Alice Cooper
    login_data = {
        'email': 'alice.cooper@customer.com',
        'password': 'password123'
    }

    print('1. Getting JWT token for alice.cooper@customer.com...')
    try:
        response = requests.post(f'{BASE_URL}/api/token/', json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access']
            print('   ✅ Authentication successful')
            
            # Test customer profile endpoint
            print('\n2. Testing customer profile endpoint...')
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(f'{BASE_URL}/api/auth/customer-profile/', headers=headers)
            
            print(f'   Status Code: {profile_response.status_code}')
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print('   ✅ Customer profile retrieved successfully')
                print('   📋 Profile Data:')
                print(f'      User ID: {profile_data.get("user_id")}')
                customer = profile_data.get('customer', {})
                print(f'      Customer ID: {customer.get("id")}')
                print(f'      Name: {customer.get("name")}')
                print(f'      Email: {customer.get("email")}')
                print(f'      Phone: {customer.get("phone")}')
                print(f'      Address: {customer.get("address")}')
                print(f'      User Role: {profile_data.get("user_role")}')
                return True
            else:
                print(f'   ❌ Profile request failed: {profile_response.text}')
                return False
                
        else:
            print(f'   ❌ Authentication failed: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError:
        print('   ❌ Server not running. Please check server status.')
        return False
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')
        return False

if __name__ == '__main__':
    test_customer_profile()