#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints documented in the frontend guides to ensure they work correctly
"""

import requests
import json
import sys
import os
from datetime import datetime

# Base URL for the Django server
BASE_URL = "http://localhost:8001"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"🧪 TESTING: {title}")
    print(f"{'='*60}{Colors.ENDC}")

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def test_endpoint(self, method, endpoint, data=None, expected_status=200, description=""):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers)
            elif method.upper() == 'POST':
                headers['Content-Type'] = 'application/json'
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                headers['Content-Type'] = 'application/json'
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'PATCH':
                headers['Content-Type'] = 'application/json'
                response = self.session.patch(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            else:
                print_error(f"Unsupported method: {method}")
                return False
                
            # Check status code
            if response.status_code == expected_status:
                try:
                    data = response.json() if response.content else {}
                    print_success(f"{method} {endpoint} - {description}")
                    print(f"    Status: {response.status_code}")
                    if data:
                        # Pretty print first few items for arrays
                        if isinstance(data, list) and len(data) > 0:
                            print(f"    Response: Array with {len(data)} items")
                            print(f"    First item: {json.dumps(data[0] if data else {}, indent=2)[:200]}...")
                        elif isinstance(data, dict):
                            print(f"    Response: {json.dumps(data, indent=2)[:300]}...")
                        else:
                            print(f"    Response: {str(data)[:200]}...")
                    return True, data
                except json.JSONDecodeError:
                    print_success(f"{method} {endpoint} - {description}")
                    print(f"    Status: {response.status_code} (No JSON content)")
                    return True, None
            else:
                print_error(f"{method} {endpoint} - {description}")
                print(f"    Expected: {expected_status}, Got: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"    Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"    Error: {response.text}")
                return False, None
                
        except requests.exceptions.ConnectionError:
            print_error(f"{method} {endpoint} - Connection failed")
            print("    Make sure Django server is running on the specified port")
            return False, None
        except Exception as e:
            print_error(f"{method} {endpoint} - Exception: {str(e)}")
            return False, None

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🚀 API ENDPOINT TESTING SUITE")
    print("Testing all documented endpoints from frontend guides")
    print(f"Server: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.ENDC}")
    
    tester = APITester(BASE_URL)
    
    # Track test results
    passed_tests = 0
    total_tests = 0
    
    # Test 1: Health Check
    print_section("HEALTH CHECK")
    success, _ = tester.test_endpoint('GET', '/api/health/', description="System health check")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 2: Employee/Technician Endpoints
    print_section("EMPLOYEE/TECHNICIAN MANAGEMENT")
    
    # Get all employees
    success, employees_data = tester.test_endpoint('GET', '/api/shop/employees/', description="Get all employees")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Filter technicians only
    success, technicians_data = tester.test_endpoint('GET', '/api/shop/employees/?role=technician', description="Get technicians only")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Get single employee (if we have employee data)
    if employees_data and len(employees_data) > 0:
        employee_id = employees_data[0]['id']
        success, _ = tester.test_endpoint('GET', f'/api/shop/employees/{employee_id}/', description=f"Get employee {employee_id}")
        if success:
            passed_tests += 1
        total_tests += 1
    
    # Test 3: Technician Workload
    print_section("TECHNICIAN WORKLOAD")
    
    success, workload_data = tester.test_endpoint('GET', '/api/shop/technicians/workload/', description="Get technician workload overview")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 4: Appointments
    print_section("APPOINTMENT MANAGEMENT")
    
    success, appointments_data = tester.test_endpoint('GET', '/api/shop/appointments/', description="Get all appointments")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Filter appointments by status
    success, _ = tester.test_endpoint('GET', '/api/shop/appointments/?status=pending', description="Get pending appointments")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Get single appointment (if we have appointment data)
    if appointments_data and len(appointments_data) > 0:
        appointment_id = appointments_data[0]['id']
        success, _ = tester.test_endpoint('GET', f'/api/shop/appointments/{appointment_id}/', description=f"Get appointment {appointment_id}")
        if success:
            passed_tests += 1
        total_tests += 1
    
    # Test 5: Vehicles
    print_section("VEHICLE MANAGEMENT")
    
    success, vehicles_data = tester.test_endpoint('GET', '/api/shop/vehicles/', description="Get all vehicles")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Get single vehicle (if we have vehicle data)
    if vehicles_data and len(vehicles_data) > 0:
        vehicle_id = vehicles_data[0]['id']
        success, _ = tester.test_endpoint('GET', f'/api/shop/vehicles/{vehicle_id}/', description=f"Get vehicle {vehicle_id}")
        if success:
            passed_tests += 1
        total_tests += 1
    
    # Test 6: Customers
    print_section("CUSTOMER MANAGEMENT")
    
    success, customers_data = tester.test_endpoint('GET', '/api/shop/customers/', description="Get all customers")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Get single customer (if we have customer data)
    if customers_data and len(customers_data) > 0:
        customer_id = customers_data[0]['id']
        success, _ = tester.test_endpoint('GET', f'/api/shop/customers/{customer_id}/', description=f"Get customer {customer_id}")
        if success:
            passed_tests += 1
        total_tests += 1
    
    # Test 7: Repair Orders
    print_section("REPAIR ORDER MANAGEMENT")
    
    success, repair_orders_data = tester.test_endpoint('GET', '/api/shop/repairorders/', description="Get all repair orders")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 8: Services
    print_section("SERVICE MANAGEMENT")
    
    success, services_data = tester.test_endpoint('GET', '/api/shop/services/', description="Get all services")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 9: Parts
    print_section("PARTS MANAGEMENT")
    
    success, parts_data = tester.test_endpoint('GET', '/api/shop/parts/', description="Get all parts")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 10: Shop Details
    print_section("SHOP MANAGEMENT")
    
    success, shops_data = tester.test_endpoint('GET', '/api/shop/shops/', description="Get all shops")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 11: Dashboard Stats
    print_section("DASHBOARD & ANALYTICS")
    
    success, _ = tester.test_endpoint('GET', '/api/shop/dashboard/stats/', description="Get dashboard statistics")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 12: Search Functionality
    print_section("SEARCH & FILTERING")
    
    success, _ = tester.test_endpoint('GET', '/api/shop/search/?q=test', description="Global search functionality")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test 13: Vehicle Problems
    print_section("VEHICLE PROBLEMS")
    
    success, _ = tester.test_endpoint('GET', '/api/shop/vehicleproblems/', description="Get vehicle problems")
    if success:
        passed_tests += 1
    total_tests += 1
    
    # Test endpoints that require specific data to exist
    print_section("CONDITIONAL TESTS (require existing data)")
    
    # Test assignment operations if we have appointments and technicians
    if appointments_data and len(appointments_data) > 0 and technicians_data and len(technicians_data) > 0:
        appointment_id = appointments_data[0]['id']
        technician_id = technicians_data[0]['id']
        
        # Test assignment endpoints (these might require specific appointment states)
        success, _ = tester.test_endpoint('POST', f'/api/shop/appointments/{appointment_id}/assign-technician/', 
                                        data={'technician_id': technician_id}, 
                                        expected_status=200, 
                                        description=f"Assign technician {technician_id} to appointment {appointment_id}")
        if success:
            passed_tests += 1
        total_tests += 1
    
    # Print final results
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}{Colors.ENDC}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{total_tests - passed_tests}{Colors.ENDC}")
    print(f"Success Rate: {Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED}{success_rate:.1f}%{Colors.ENDC}")
    
    if success_rate >= 80:
        print(f"\n{Colors.GREEN}🎉 Excellent! Most endpoints are working correctly.{Colors.ENDC}")
    elif success_rate >= 60:
        print(f"\n{Colors.YELLOW}⚠️  Good progress, but some endpoints need attention.{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}❌ Several endpoints are not working. Check server configuration.{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}💡 Note: Some failures may be expected if:")
    print("   - Endpoints require authentication")
    print("   - Database is empty (no test data)")
    print("   - Specific business logic prevents operations")
    print("   - Endpoints are not yet implemented{Colors.ENDC}")
    
    return success_rate >= 60

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Testing interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)