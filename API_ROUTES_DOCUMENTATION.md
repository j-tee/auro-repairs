# Complete API Routes Documentation

## Overview

This document provides a comprehensive list of all available API routes in the auto repair shop management system, organized by functionality and access level.

## Base URL
```
http://127.0.0.1:8000/api/
```

## Authentication Endpoints

### Public Endpoints (No Authentication Required)
```
POST /api/token/                    # Obtain JWT access & refresh tokens
POST /api/token/refresh/            # Refresh JWT access token
POST /api/auth/register/            # Register new customer account
```

### Authenticated Endpoints
```
GET  /api/auth/user/                # Get current user profile
PUT  /api/auth/user/update/         # Update current user profile
POST /api/auth/verify-email/        # Verify email address
POST /api/auth/resend-verification/ # Resend verification email
```

## Admin Endpoints (Owner Only)

```
GET  /api/admin/users/              # List all users in system
PUT  /api/admin/users/{id}/role/    # Update user role (owner/employee/customer)
```

## Shop Management Endpoints

### Shop Operations (Owner Only)
```
GET    /api/shop/shops/             # List all shops
POST   /api/shop/shops/             # Create new shop
GET    /api/shop/shops/{id}/        # Get specific shop details
PUT    /api/shop/shops/{id}/        # Update shop details
DELETE /api/shop/shops/{id}/        # Delete shop
GET    /api/shop/shops/{id}/employees/     # Get employees for specific shop
GET    /api/shop/shops/{id}/services/      # Get services for specific shop
```

### Inventory Management (Owner + Employee)

#### Services
```
GET    /api/shop/services/          # List services (filtered by user role)
POST   /api/shop/services/          # Create new service
GET    /api/shop/services/{id}/     # Get specific service
PUT    /api/shop/services/{id}/     # Update service
DELETE /api/shop/services/{id}/     # Delete service
```

#### Parts
```
GET    /api/shop/parts/             # List parts (filtered by user role)
POST   /api/shop/parts/             # Create new part
GET    /api/shop/parts/{id}/        # Get specific part
PUT    /api/shop/parts/{id}/        # Update part
DELETE /api/shop/parts/{id}/        # Delete part
GET    /api/shop/parts/low_stock/   # Get parts with low stock (< 10 items)
```

### Employee Management (Owner Only)
```
GET    /api/shop/employees/         # List employees
POST   /api/shop/employees/         # Create new employee
GET    /api/shop/employees/{id}/    # Get specific employee
PUT    /api/shop/employees/{id}/    # Update employee
DELETE /api/shop/employees/{id}/    # Delete employee
```

## Customer Management

### Customer Data (Role-Based Access)
```
GET    /api/shop/customers/         # List customers (all for owner/employee, own for customer)
POST   /api/shop/customers/         # Create new customer
GET    /api/shop/customers/{id}/    # Get specific customer
PUT    /api/shop/customers/{id}/    # Update customer (own data only for customers)
DELETE /api/shop/customers/{id}/    # Delete customer (owner/employee only)
```

### Vehicle Management
```
GET    /api/shop/vehicles/          # List vehicles (filtered by user role)
POST   /api/shop/vehicles/          # Create new vehicle
GET    /api/shop/vehicles/{id}/     # Get specific vehicle
PUT    /api/shop/vehicles/{id}/     # Update vehicle (own vehicles for customers)
DELETE /api/shop/vehicles/{id}/     # Delete vehicle (owner/employee only)
```

### Vehicle Problems
```
GET    /api/shop/vehicle-problems/  # List vehicle problems (filtered by user role)
POST   /api/shop/vehicle-problems/  # Report new vehicle problem
GET    /api/shop/vehicle-problems/{id}/  # Get specific problem
PUT    /api/shop/vehicle-problems/{id}/  # Update problem (own problems for customers)
DELETE /api/shop/vehicle-problems/{id}/  # Delete problem (owner/employee only)
GET    /api/shop/vehicle-problems/unresolved/  # Get unresolved problems
```

## Appointment Management

```
GET    /api/shop/appointments/      # List appointments (filtered by user role)
POST   /api/shop/appointments/      # Create new appointment (all authenticated users)
GET    /api/shop/appointments/{id}/ # Get specific appointment
PUT    /api/shop/appointments/{id}/ # Update appointment (owner/employee only)
DELETE /api/shop/appointments/{id}/ # Delete appointment (owner/employee only)
GET    /api/shop/appointments/upcoming/  # Get upcoming appointments
```

## Repair Order Management

### Repair Orders (Owner + Employee for full access, Customer for own orders)
```
GET    /api/shop/repair-orders/     # List repair orders (filtered by user role)
POST   /api/shop/repair-orders/     # Create new repair order (owner/employee only)
GET    /api/shop/repair-orders/{id}/ # Get specific repair order
PUT    /api/shop/repair-orders/{id}/ # Update repair order (owner/employee only)
DELETE /api/shop/repair-orders/{id}/ # Delete repair order (owner/employee only)
GET    /api/shop/repair-orders/financial_summary/  # Financial summary (owner only)
```

### Repair Order Parts (Owner + Employee)
```
GET    /api/shop/repair-order-parts/     # List repair order parts (filtered by user role)
POST   /api/shop/repair-order-parts/     # Add part to repair order
GET    /api/shop/repair-order-parts/{id}/ # Get specific repair order part
PUT    /api/shop/repair-order-parts/{id}/ # Update repair order part
DELETE /api/shop/repair-order-parts/{id}/ # Remove part from repair order
```

### Repair Order Services (Owner + Employee)
```
GET    /api/shop/repair-order-services/     # List repair order services (filtered by user role)
POST   /api/shop/repair-order-services/     # Add service to repair order
GET    /api/shop/repair-order-services/{id}/ # Get specific repair order service
PUT    /api/shop/repair-order-services/{id}/ # Update repair order service
DELETE /api/shop/repair-order-services/{id}/ # Remove service from repair order
```

## Django Admin Interface

```
GET /admin/                         # Django admin login page
```

## Access Control Summary

### Owner (Full Access)
- ✅ All endpoints
- ✅ User management
- ✅ Financial data
- ✅ Shop management
- ✅ All CRUD operations

### Employee (Limited Management Access)
- ✅ Inventory management (parts/services)
- ✅ Repair order creation and management
- ✅ Customer data access
- ✅ Vehicle and problem management
- ✅ Appointment management
- ❌ Shop creation/deletion
- ❌ Employee management
- ❌ Financial data access
- ❌ User role management

### Customer (Personal Data Only)
- ✅ Own profile management
- ✅ Own vehicle management
- ✅ Own problem reporting
- ✅ Appointment creation
- ✅ View own repair orders
- ❌ All management functions
- ❌ Other customers' data
- ❌ Shop operations

## HTTP Methods

Each endpoint supports standard REST operations:
- `GET`: Retrieve data
- `POST`: Create new resource
- `PUT`: Update entire resource
- `PATCH`: Partial update (supported on all endpoints)
- `DELETE`: Remove resource

## Query Parameters

### Filtering (Available on list endpoints)
```
?field_name=value                   # Filter by exact field value
?field_name__icontains=value        # Case-insensitive contains
?field_name__gte=value              # Greater than or equal
?field_name__lte=value              # Less than or equal
```

### Searching (Available on list endpoints)
```
?search=query                       # Search across defined search fields
```

### Ordering (Available on list endpoints)
```
?ordering=field_name                # Ascending order
?ordering=-field_name               # Descending order
?ordering=field1,-field2            # Multiple fields
```

### Pagination (Automatic on list endpoints)
```
?page=1                             # Page number
?page_size=20                       # Items per page
```

## Authentication Headers

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

## Response Formats

### Success Response (200/201)
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  "created_at": "2025-08-19T10:00:00Z"
}
```

### List Response (200)
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/shop/vehicles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "field1": "value1"
    }
  ]
}
```

### Error Response (400/401/403/404)
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Testing the API

### Using curl
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@autorepairshop.com", "password": "owner123"}'

# Use token
curl -X GET http://127.0.0.1:8000/api/shop/shops/ \
  -H "Authorization: Bearer <access_token>"
```

### Using Python requests
```python
import requests

# Login
response = requests.post('http://127.0.0.1:8000/api/token/', 
                        json={'email': 'owner@autorepairshop.com', 'password': 'owner123'})
tokens = response.json()

# Make authenticated request
headers = {'Authorization': f'Bearer {tokens["access"]}'}
shops = requests.get('http://127.0.0.1:8000/api/shop/shops/', headers=headers)
```

## Sample Test Accounts

```
Owner:    owner@autorepairshop.com     / owner123
Employee: john.mechanic@autorepair.com / password123
Customer: alice.cooper@customer.com    / password123
```

This completes the comprehensive API documentation for the auto repair shop management system.
