# Complete API Reference
## Auto Repair Shop Management System

> **🎯 COMPREHENSIVE**: Complete reference for all available API endpoints with verified responses

---

## Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication
All endpoints require JWT Bearer token authentication unless specified otherwise.

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## Authentication Endpoints

### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response 200**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "role": "owner"
  }
}
```

### Token Refresh
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Employee Management

### List All Employees
```http
GET /api/shop/employees/
```

**✅ Verified Response 200**:
```json
[
  {
    "id": 27,
    "name": "Test Technician",
    "role": "technician",
    "phone_number": "555-0123",
    "email": "tech@test.com",
    "picture": null,
    "shop": 18,
    "user": null,
    "workload_count": 1,
    "is_available": true,
    "appointments_today_count": 0,
    "is_technician": true,
    "current_jobs": [
      {
        "appointment_id": 34,
        "vehicle": "Toyota Camry",
        "customer": "Alice Cooper",
        "status": "assigned",
        "date": "2025-08-22T10:30:00Z",
        "assigned_at": "2025-09-13T10:17:49.359466Z",
        "started_at": null
      }
    ]
  }
]
```

### Get Single Employee
```http
GET /api/shop/employees/{id}/
```

**Response 200**: Single employee object (same structure as above)

### Create Employee
```http
POST /api/shop/employees/
Content-Type: application/json

{
  "name": "John Smith",
  "role": "technician",
  "phone_number": "555-0456",
  "email": "john@example.com",
  "shop": 18
}
```

### Update Employee
```http
PUT /api/shop/employees/{id}/
PATCH /api/shop/employees/{id}/
```

### Delete Employee
```http
DELETE /api/shop/employees/{id}/
```

---

## Technician Workload

### Get Workload Overview
```http
GET /api/shop/technicians/workload/
```

**✅ Verified Response 200**:
```json
{
  "summary": {
    "total_technicians": 3,
    "available_technicians": 2,
    "busy_technicians": 1
  },
  "technicians": [
    {
      "technician": {
        "id": 27,
        "name": "Test Technician",
        "role": "technician",
        "shop": "Main Shop"
      },
      "workload": {
        "current_appointments": 1,
        "is_available": true,
        "appointments_today": 0,
        "max_capacity": 3
      },
      "current_jobs": [
        {
          "appointment_id": 34,
          "vehicle": "Toyota Camry",
          "customer": "Alice Cooper",
          "status": "assigned",
          "assigned_at": "2025-09-13T10:17:49.359466Z",
          "started_at": null
        }
      ]
    }
  ]
}
```

---

## Appointment Management

### List All Appointments
```http
GET /api/shop/appointments/
```

**✅ Verified Response 200**:
```json
[
  {
    "id": 34,
    "vehicle_id": 12,
    "vehicle": {
      "id": 12,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "license_plate": "ABC-5189",
      "vin": "1HGBH41JXMN109186",
      "color": "Blue"
    },
    "reported_problem_id": null,
    "reported_problem": null,
    "assigned_technician_id": 27,
    "assigned_technician": {
      "id": 27,
      "name": "Test Technician",
      "role": "technician"
    },
    "customer_id": 15,
    "customer_name": "Alice Cooper",
    "description": "Engine noise inspection",
    "date": "2025-08-22T10:30:00Z",
    "status": "assigned",
    "assigned_at": "2025-09-13T10:17:49.359466Z",
    "started_at": null,
    "completed_at": null
  }
]
```

### Get Single Appointment
```http
GET /api/shop/appointments/{id}/
```

### Create Appointment
```http
POST /api/shop/appointments/
Content-Type: application/json

{
  "vehicle_id": 12,
  "description": "Engine noise inspection",
  "date": "2025-08-22T10:30:00Z",
  "reported_problem_id": null
}
```

### Update Appointment
```http
PUT /api/shop/appointments/{id}/
PATCH /api/shop/appointments/{id}/
```

### Assign Technician
```http
POST /api/shop/appointments/{id}/assign-technician/
Content-Type: application/json

{
  "technician_id": 27
}
```

**Response 200**: Updated appointment with `assigned_technician` and `assigned_at`

### Start Work
```http
POST /api/shop/appointments/{id}/start-work/
```

**Response 200**: Updated appointment with `status: "in_progress"` and `started_at`

### Complete Work
```http
POST /api/shop/appointments/{id}/complete-work/
```

**Response 200**: Updated appointment with `status: "completed"` and `completed_at`

### Unassign Technician
```http
POST /api/shop/appointments/{id}/unassign-technician/
```

---

## Vehicle Management

### List All Vehicles
```http
GET /api/shop/vehicles/
```

**✅ Verified Response 200**:
```json
[
  {
    "id": 12,
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "license_plate": "ABC-5189",
    "vin": "1HGBH41JXMN109186",
    "color": "Blue",
    "customer_id": 15,
    "customer": {
      "id": 15,
      "name": "Alice Cooper",
      "email": "alice@example.com",
      "phone_number": "555-0199"
    },
    "customer_name": "Alice Cooper",
    "customer_email": "alice@example.com",
    "customer_phone": "555-0199"
  }
]
```

### Get Single Vehicle
```http
GET /api/shop/vehicles/{id}/
```

### Create Vehicle
```http
POST /api/shop/vehicles/
Content-Type: application/json

{
  "make": "Honda",
  "model": "Civic",
  "year": 2022,
  "license_plate": "XYZ-789",
  "vin": "2HGFC2F59MH123456",
  "color": "Red",
  "customer_id": 15
}
```

### Update Vehicle
```http
PUT /api/shop/vehicles/{id}/
PATCH /api/shop/vehicles/{id}/
```

---

## Customer Management

### List All Customers
```http
GET /api/shop/customers/
```

**Response 200**:
```json
[
  {
    "id": 15,
    "name": "Alice Cooper",
    "phone_number": "555-0199",
    "email": "alice@example.com",
    "address": "123 Main St",
    "user": null
  }
]
```

### Get Single Customer
```http
GET /api/shop/customers/{id}/
```

### Create Customer
```http
POST /api/shop/customers/
Content-Type: application/json

{
  "name": "Bob Johnson",
  "phone_number": "555-0777",
  "email": "bob@example.com",
  "address": "456 Oak Ave"
}
```

### Update Customer
```http
PUT /api/shop/customers/{id}/
PATCH /api/shop/customers/{id}/
```

---

## Vehicle Problems

### List Vehicle Problems
```http
GET /api/shop/vehicleproblems/
```

**Response 200**:
```json
[
  {
    "id": 1,
    "description": "Engine making unusual noise",
    "reported_date": "2025-09-10T14:30:00Z",
    "resolved": false,
    "vehicle_id": 12,
    "vehicle": {
      "id": 12,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "license_plate": "ABC-5189"
    }
  }
]
```

### Create Vehicle Problem
```http
POST /api/shop/vehicleproblems/
Content-Type: application/json

{
  "description": "Brake squealing when stopping",
  "vehicle_id": 12
}
```

---

## Repair Orders

### List Repair Orders
```http
GET /api/shop/repairorders/
```

**✅ Verified Response 200**:
```json
[
  {
    "id": 1,
    "vehicle_id": 12,
    "vehicle": {
      "id": 12,
      "make": "Toyota",
      "model": "Camry",
      "year": 2020,
      "license_plate": "ABC-5189",
      "vin": "1HGBH41JXMN109186",
      "color": "Blue"
    },
    "customer_id": 15,
    "customer_name": "Alice Cooper",
    "status": "assigned",
    "discount_amount": "0.00",
    "discount_percent": "0.00",
    "tax_percent": "8.25",
    "total_cost": "350.00",
    "date_created": "2025-09-13T10:00:00Z",
    "notes": "Standard inspection and oil change",
    "repair_order_parts": [],
    "repair_order_services": [],
    "calculated_total_cost": "350.00"
  }
]
```

### Create Repair Order
```http
POST /api/shop/repairorders/
Content-Type: application/json

{
  "vehicle_id": 12,
  "notes": "Customer complaint about engine noise",
  "discount_amount": "0.00"
}
```

---

## Services

### List Services
```http
GET /api/shop/services/
```

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "Oil Change",
    "description": "Full synthetic oil change with filter",
    "labor_cost": "45.00",
    "taxable": true,
    "warranty_months": 6,
    "shop": 18,
    "parts": []
  }
]
```

### Create Service
```http
POST /api/shop/services/
Content-Type: application/json

{
  "name": "Brake Inspection",
  "description": "Complete brake system inspection",
  "labor_cost": "85.00",
  "taxable": true,
  "warranty_months": 12,
  "shop": 18
}
```

---

## Parts

### List Parts
```http
GET /api/shop/parts/
```

**Response 200**:
```json
[
  {
    "id": 1,
    "name": "Oil Filter",
    "category": "Filter",
    "part_number": "OF-12345",
    "description": "High-quality oil filter",
    "manufacturer": "AutoParts Co",
    "unit_price": "12.99",
    "taxable": true,
    "warranty_months": 12,
    "stock_quantity": 50,
    "created_at": "2025-09-01T10:00:00Z",
    "shop": 18,
    "total_cost": "649.50"
  }
]
```

### Create Part
```http
POST /api/shop/parts/
Content-Type: application/json

{
  "name": "Brake Pad Set",
  "category": "Brake",
  "part_number": "BP-67890",
  "description": "Premium ceramic brake pads",
  "manufacturer": "BrakeTech",
  "unit_price": "89.99",
  "taxable": true,
  "warranty_months": 24,
  "stock_quantity": 20,
  "shop": 18
}
```

---

## Shop Management

### Get Shop Details
```http
GET /api/shop/shops/
GET /api/shop/shops/{id}/
```

**Response 200**:
```json
{
  "id": 18,
  "name": "Main Auto Repair Shop",
  "address": "123 Workshop Lane",
  "phone": "555-0100",
  "email": "info@autorepair.com",
  "bay_count": 4,
  "is_active": true,
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-09-13T15:30:00Z",
  "services": [],
  "parts": [],
  "employees": [],
  "customers": [],
  "appointments": [],
  "repair_orders": []
}
```

---

## Search & Filtering

### Global Search
```http
GET /api/shop/search/?q={query}
```

**Query Parameters**:
- `q`: Search term
- `type`: Filter by entity type (`customers`, `vehicles`, `appointments`)

### Filter Appointments
```http
GET /api/shop/appointments/?status={status}&date_from={date}&date_to={date}
```

**Query Parameters**:
- `status`: `pending`, `assigned`, `in_progress`, `completed`, `cancelled`
- `date_from`: ISO date format (e.g., `2025-09-13`)
- `date_to`: ISO date format
- `assigned_technician`: Technician ID

### Filter by Date Range
```http
GET /api/shop/appointments/?date_from=2025-09-01&date_to=2025-09-30
```

---

## Dashboard & Analytics

### Dashboard Stats
```http
GET /api/shop/dashboard/stats/
```

**Response 200**:
```json
{
  "active_repairs": 19,
  "revenue_today": "691.00",
  "pending_appointments": 12,
  "completed_today": 3,
  "available_technicians": 2,
  "total_customers": 45
}
```

### Revenue Analytics
```http
GET /api/shop/analytics/revenue/?period={period}
```

**Query Parameters**:
- `period`: `today`, `week`, `month`, `year`

---

## Status Codes & Error Handling

### Success Responses
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Resource deleted successfully

### Error Responses
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "authentication_failed"
}
```

### Validation Error Format
```json
{
  "email": ["This field is required."],
  "phone_number": ["Ensure this field has at least 10 characters."]
}
```

---

## Rate Limiting

- **Rate Limit**: 100 requests per minute per user
- **Headers**:
  ```http
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1694678400
  ```

---

## API Versioning

Current version: `v1` (default)

Future versions will be accessible via:
```http
GET /api/v2/shop/employees/
```

Or via header:
```http
Accept: application/json; version=2
```

---

## Webhook Support (Future)

Planned webhook events:
- `appointment.assigned`
- `appointment.completed`
- `workload.updated`

---

## Testing Endpoints

### Health Check
```http
GET /api/health/
```

**Response 200**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## Notes for Frontend Developers

### 🎯 Key Implementation Points

1. **All Employee data includes computed properties** - no need for separate workload API calls
2. **Consistent field patterns** - APIs return both `{field}_id` and `{field}` object
3. **Real-time updates** - Consider polling workload endpoint every 30 seconds
4. **Optimistic updates** - Update UI immediately, rollback on error
5. **Error handling** - Implement retry logic for failed requests
6. **Caching** - Cache employee/customer data, refresh appointments frequently

### 🔄 Recommended Update Frequencies

- **Appointments**: Every 15-30 seconds (high priority)
- **Workload data**: Every 30-60 seconds
- **Employees/Customers**: On demand or every 5 minutes
- **Static data** (services, parts): On demand only

This API reference reflects the actual, verified backend implementation with accurate response examples.